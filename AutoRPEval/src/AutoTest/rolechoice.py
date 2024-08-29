import ast
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
from config import TestModels, language
if language == 'cn':
    from AutoTest.prompts import RoleChoicePrompt
elif language == 'en':
    from AutoTest.prompts_en import RoleChoicePrompt
else:
    raise ValueError(f"Invalid language {language}")
from LLMClients import Cost, OpenAIClient
from tqdm import tqdm
from utils import construct_masked_dialogue, construct_masked_scene, construct_masked_dialogue_en, construct_masked_scene_en

import glob
import os

MaxWorkers = 10
AllCost = Cost()

def extrct_rolechoice(rsp: str) -> Dict[str, int]:
    matches = re.findall(r"{[^}]*}", rsp, re.DOTALL)
    if not matches:
        raise ValueError("Invalid response format in re.findall")
    rsp = matches[-1]
    try:
        json_rsp = ast.literal_eval(rsp)
    except:
        raise ValueError("Invalid response format in ast.literal_eval")
    if 'answer' not in json_rsp:
        raise ValueError("Invalid response format in 'answer' not in json_rsp")
    else:
        if len(json_rsp['answer']) != 1:
            raise ValueError(f"Invalid response format {json_rsp['answer']} in len(json_rsp['answer']) != 1")
        return json_rsp['answer'].upper()


def eval_chat_rolechoice(chat, role_name, role_candidates, client, model, index):
    global AllCost
    if language == 'cn':
        scene = construct_masked_scene(chat['scene'], role_name)
        dialogues = construct_masked_dialogue(chat['dialogues'])
    elif language == 'en':
        scene = construct_masked_scene_en(chat['scene'], role_name)
        dialogues = construct_masked_dialogue_en(chat['dialogues'])
    chat_role = chat['chat_role']
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": RoleChoicePrompt.format(role_name=role_name, dialogues=dialogues, role_candidates=role_candidates, scene=scene, chat_role=chat_role)}
    ]
    rsps, cost = client.call(messages=messages, model=model, n=1, temperature=0)
    AllCost += cost
    rsp = rsps[0]
    try:
        rolechoice_eval = extrct_rolechoice(rsp)
    except Exception as e:
        print(f"Error: {e}")
        rolechoice_eval = None
    chat['rolechoice_eval'] = rolechoice_eval
    chat['rolechoice_analysis_eval'] = rsp
    return index, chat
  
def eval_rolechoice(role_file):
    with open(role_file, 'r') as file:
        role_data = json.load(file)

    role_name = role_data['name']
    role_candidates = role_data['role_candidates']
    client = OpenAIClient(client_type='openAI')
    model  = 'gpt-4o'
    chats_with_eval = [None] * len(role_data['chats'])
    with ThreadPoolExecutor(max_workers=MaxWorkers) as executor:
        futures = [
        executor.submit(eval_chat_rolechoice, chat, role_name, role_candidates, client, model, index) 
        for index, chat in enumerate(role_data['chats'].values())
    ]
        for future in as_completed(futures):
            index, result = future.result()
            chats_with_eval[index] = result
            if result['rolechoice_eval'] is None:
                print(f"Warning: {role_file} with rolechoice_eval is none.")
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
        for role_file in tqdm(test_roles, desc=f"Processing {model} Dialogues Files role choice Scale"):
            eval_rolechoice(role_file)
    global AllCost
    print(f"AllCost: {AllCost}")
    
# python -m AutoTest.rolechoice
# nohup python -u -m AutoTest.rolechoice > ../logs/rolechoice_eval.log 2>&1 &
if __name__ == '__main__':
    main()
