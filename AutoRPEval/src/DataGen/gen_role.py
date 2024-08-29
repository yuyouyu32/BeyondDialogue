language = "en"
MaxWorkerNum = 10
import ast
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict

import tqdm
from config import MaxGenRoleNum
if language == "cn":
    from DataGen.prompts import RolePrompt, RoleReference
elif language == "en":
    from DataGen.prompts_en import RolePrompt, RoleReference
else:
    raise ValueError("Invalid language")
from LLMClients import Cost, OpenAIClient
from utils import (collect_roles, generate_MBTI_str, generate_MBTI_str_en,
                   retry_on_failure)

ALL_Cost = Cost()

@retry_on_failure(retries=5)
def get_chat_roles(client, role_name, character, MBTI, style, world, role_reference=None):
    global ALL_Cost
    if language == "cn":
        MBTI = generate_MBTI_str(MBTI)
    elif language == "en":
        MBTI = generate_MBTI_str_en(MBTI)
        character = character.lower().replace(",", ", ")
        style = style.lower().replace(",", ", ")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": RolePrompt.format(role_name=role_name, character=character, MBTI=MBTI, style=style, world=world, role_reference=role_reference)}
    ]
    rsps, cost = client.call(messages=messages, model="gpt-4o", n=1)
    matches = re.findall(r"{[^}]*}", rsps[0], re.DOTALL)
    if not matches:
        raise ValueError("No valid JSON found in the response")
    
    rsp = matches[-1]
    json_rsp = ast.literal_eval(rsp)
    ALL_Cost += cost
    
    if "chat_role" in json_rsp and "role_des" in json_rsp:
        return json_rsp["chat_role"], json_rsp["role_des"]
    else:
        raise ValueError("Invalid response format")

def construct_role_reference(chat_roles: Dict[str, Dict[str, str]]):
    reference = ""
    for chat_role, role_data in chat_roles.items():
        reference += f"{chat_role}: {role_data['role_des']}\n"
    return RoleReference.format(reference=reference)


def process_role(role, role_data):
    chat_roles = {}
    client = OpenAIClient()
    for i in tqdm.tqdm(range(MaxGenRoleNum), desc=f"Generating chat roles for {role}", total=MaxGenRoleNum):
        if i == 0:
            chat_role, role_des = get_chat_roles(client, role, role_data["character"], role_data["personality"], role_data["style"], role_data["world"])
            chat_roles[chat_role] = {"chat_role": chat_role, "role_des": role_des.strip()}
        else:
            role_reference = RoleReference.format(reference=construct_role_reference(chat_roles))
            chat_role, role_des = get_chat_roles(client, role, role_data["character"], role_data["personality"], role_data["style"], role_data["world"], role_reference)
            chat_roles[chat_role] = {"chat_role": chat_role, "role_des": role_des}
    role_data["chats"] = chat_roles
    if language == 'cn':
        json.dump(role_data, open(f'../data/roles/{role}.json', 'w'), ensure_ascii=False, indent=4)
    elif language == 'en':
        json.dump(role_data, open(f'../data/roles_en/{role}.json', 'w'), ensure_ascii=False, indent=4)
    return role

def main():
    if language == 'cn':
        roles = collect_roles('../data/roles')
    elif language == 'en':
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
    
# nohup python -u -m DataGen.gen_role > ../logs/generate_role.log 2>&1 &  
if __name__ == '__main__':
    main()