import ast
import glob
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

from config import TestModels, language

if language == 'cn':
    from AutoTest.prompts import RelationshipScalePrompt
elif language == 'en':
    from AutoTest.prompts_en import RelationshipScalePrompt
else:
    raise ValueError(f"Invalid language {language}")

from LLMClients import Cost, OpenAIClient
from tqdm import tqdm
from utils import construct_str_dialogue, generate_MBTI_str, generate_MBTI_str_en

MaxWorkers = 10
AllCost = Cost()

def extrct_relationship(rsp: str) -> Dict[str, int]:
    matches = re.findall(r"{[^}]*}", rsp, re.DOTALL)
    if not matches:
        raise ValueError("Invalid response format in re.findall")
    rsp = matches[-1]
    try:
        json_rsp = ast.literal_eval(rsp)
    except:
        raise ValueError("Invalid response format in ast.literal_eval")
    if 'relationship' not in json_rsp:
        raise ValueError("Invalid response format in 'relationship' not in json_rsp")
    else:
        try:
            return float(json_rsp['relationship'])
        except:
            raise ValueError("Invalid response format in int(json_rsp['relationship'])")


def eval_chat_relationship(chat, role_name, character, MBTI, style, client, model, index):
    global AllCost
    scene = chat['scene']
    chat_role = chat['chat_role']
    dialogues = construct_str_dialogue(chat['dialogues'])
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": RelationshipScalePrompt.format(role_name=role_name, character=character, dialogues=dialogues, scene=scene, MBTI=MBTI, style=style, chat_role=chat_role)}
    ]
    rsps, cost = client.call(messages=messages, model=model, n=1, temperature=0)
    AllCost += cost
    rsp = rsps[0]
    try:
        relationship_eval = extrct_relationship(rsp)
    except Exception as e:
        print(f"Error: {e}")
        relationship_eval = None
    chat['relationship_eval'] = relationship_eval
    chat['relationship_analysis_eval'] = rsp
    return index, chat
  
def eval_role_relationship(role_file):
    with open(role_file, 'r') as file:
        role_data = json.load(file)

    role_name = role_data['name']
    character = role_data['character']
    style = role_data['style']
    if language == 'cn':
        MBTI = generate_MBTI_str(role_data['personality'])
    elif language == 'en':
        MBTI = generate_MBTI_str_en(role_data['personality'])
        character = character.lower().replace(',', ', ')
        style = style.lower().replace(',', ', ')

    client = OpenAIClient(client_type='openAI')
    model  = 'gpt-4o'
    chats_with_eval = [None] * len(role_data['chats'])
    with ThreadPoolExecutor(max_workers=MaxWorkers) as executor:
        futures = [
        executor.submit(eval_chat_relationship, chat, role_name, character, MBTI, style, client, model, index) 
        for index, chat in enumerate(role_data['chats'].values())
    ]
        for future in as_completed(futures):
            index, result = future.result()
            chats_with_eval[index] = result
            if result['relationship_eval'] is None:
                print(f"Warning: {role_file} with relationship_eval is none.")
    role_data['chats'] = {chat['chat_role']: chat for chat in chats_with_eval}
    with open(role_file, 'w') as f:
        json.dump(role_data, f, ensure_ascii=False, indent=4)

        
def main():
    if language == 'cn':
        base_dir = '../chat_dialogues'
    elif language == 'en':
        base_dir = '../chat_dialogues_en'
    test_models = TestModels
    for model in test_models:
        model_dir = os.path.join(base_dir, model)
        test_roles = glob.glob(f"{model_dir}/*.json")
        for role_file in tqdm(test_roles, desc=f"Processing {model} Dialogues Files relationship Scale"):
            eval_role_relationship(role_file)
    global AllCost
    print(f"AllCost: {AllCost}")
    
# python -m AutoTest.relationship
# nohup python -u -m AutoTest.relationship > ../logs/relationship_eval.log 2>&1 &
if __name__ == '__main__':
    main()
