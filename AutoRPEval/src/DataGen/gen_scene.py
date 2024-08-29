language = "en"
MaxWorkerNum = 10
import ast
import json
import re
from typing import Dict

import tqdm
if language == "cn":
    from DataGen.prompts import ScenePrompt
elif language == "en":
    from DataGen.prompts_en import ScenePrompt
else:
    raise ValueError("Invalid language")

from LLMClients import Cost, OpenAIClient
from utils import collect_roles, generate_MBTI_str, retry_on_failure, generate_MBTI_str_en
from concurrent.futures import ThreadPoolExecutor, as_completed
ALL_Cost = Cost()

@retry_on_failure(retries=5)
def get_chat_scene(client: OpenAIClient, role_name: str, character: str, MBTI: str, style: str, world: str, chat_role: str, role_des: str):
    global ALL_Cost
    if language == "cn":
        MBTI = generate_MBTI_str(MBTI)
    elif language == "en":
        MBTI = generate_MBTI_str_en(MBTI)
        character = character.lower().replace(",", ", ")
        style = style.lower().replace(",", ", ")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": ScenePrompt.format(role_name=role_name, character=character, MBTI=MBTI, style=style, world=world, chat_role=chat_role, role_des=role_des)}
    ]
    rsps, cost = client.call(messages=messages, model="gpt-4o", n=1)
    matches = re.findall(r"{[^}]*}", rsps[0], re.DOTALL)
    if not matches:
        raise ValueError("Invalid response format")
    rsp = matches[-1]
    json_rsp = ast.literal_eval(rsp)
    ALL_Cost += cost
    if "scene" in json_rsp:
        return json_rsp["scene"].strip()
    raise ValueError("Invalid response format")



def process_role(role, role_data):
    client = OpenAIClient()
    if "chats" not in role_data:
        raise ValueError(f"Role {role} does not have chat roles, please generate chat roles first...")
    for chat_role, chat_role_data in tqdm.tqdm(role_data["chats"].items(), desc=f"Generating scene for {role}"):
        scene = get_chat_scene(client, role, role_data["character"], role_data["personality"], role_data["style"], role_data["world"], chat_role, chat_role_data["role_des"])
        role_data["chats"][chat_role]["scene"] = scene
    if language == "cn":
        json.dump(role_data, open(f'../data/roles/{role}.json', 'w'), ensure_ascii=False, indent=4)
    elif language == "en":
        json.dump(role_data, open(f'../data/roles_en/{role}.json', 'w'), ensure_ascii=False, indent=4)
    return role

def main():
    if language == "cn":
        roles = collect_roles('../data/roles')
    else:
        roles = collect_roles('../data/roles_en')
    with ThreadPoolExecutor(max_workers=MaxWorkerNum) as executor:
        futures = {executor.submit(process_role, role, role_data): role for role, role_data in roles.items()}
        for future in as_completed(futures):
            role = futures[future]
            # try:
            future.result()
            # except Exception as exc:
            #     print(f'Role {role} generated an exception: {exc}')
    global ALL_Cost
    print(f"Total cost: {ALL_Cost}")
    
# nohup python -u -m DataGen.gen_scene > ../logs/generate_scene.log 2>&1 &
if __name__ == '__main__':
    main()