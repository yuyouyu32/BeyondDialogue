import ast
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
from config import TestModels, language
if language == 'cn':
    from AutoTest.prompts import HumanLikenessPrompt
elif language == 'en':
    from AutoTest.prompts_en import HumanLikenessPrompt
else:
    raise ValueError(f"Invalid language {language}")
from LLMClients import Cost, OpenAIClient
from tqdm import tqdm
from utils import generate_MBTI_str, construct_str_dialogue, generate_MBTI_str_en

import glob
import os

MaxWorkers = 10
AllCost = Cost()

def extrct_human_likeness(rsp: str) -> Dict[str, int]:
    matches = re.findall(r"{[^}]*}", rsp, re.DOTALL)
    if not matches:
        raise ValueError("Invalid response format in re.findall")
    rsp = matches[-1]
    try:
        json_rsp = ast.literal_eval(rsp)
    except:
        raise ValueError("Invalid response format in ast.literal_eval")
    if 'is_real_dialogue' not in json_rsp:
        raise ValueError("Invalid response format in 'is_real_dialogue' not in json_rsp")
    else:
        if json_rsp['is_real_dialogue'] == 'true':
            return 1
        elif json_rsp['is_real_dialogue'] == 'false':
            return 0
        else:
            raise ValueError(f"Invalid response format in 'is_real_dialogue' value {json_rsp['is_real_dialogue']}")


def eval_chat_human_likeness(chat, role_name, character, MBTI, style, client, model, index):
    global AllCost
    scene = chat['scene']
    chat_role = chat['chat_role']
    relationship = chat['relationship_score']
    dialogues = construct_str_dialogue(chat['dialogues'])
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": HumanLikenessPrompt.format(role_name=role_name, character=character, dialogues=dialogues, scene=scene, MBTI=MBTI, style=style, chat_role=chat_role, relationship=relationship)}
    ]
    rsps, cost = client.call(messages=messages, model=model, n=1, temperature=0)
    AllCost += cost
    rsp = rsps[0]
    try:
        human_likeness_eval = extrct_human_likeness(rsp)
    except Exception as e:
        print(f"Error: {e}")
        human_likeness_eval = None
    chat['human_likeness_eval'] = human_likeness_eval
    chat['human_likeness_analysis_eval'] = rsp
    return index, chat
  
def eval_role_human_likeness(role_file):
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
        executor.submit(eval_chat_human_likeness, chat, role_name, character, MBTI, style, client, model, index) 
        for index, chat in enumerate(role_data['chats'].values())
    ]
        for future in as_completed(futures):
            index, result = future.result()
            chats_with_eval[index] = result
            if result['human_likeness_eval'] is None:
                print(f"Warning: {role_file} with human_likeness_eval is none.")
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
        for role_file in tqdm(test_roles, desc=f"Processing {model} Dialogues Files human-likeness Scale"):
            eval_role_human_likeness(role_file)
    global AllCost
    print(f"AllCost: {AllCost}")
    
# python -m AutoTest.human_likeness
# nohup python -u -m AutoTest.human_likeness > ../logs/human_likeness_eval.log 2>&1 &
if __name__ == '__main__':
    main()
