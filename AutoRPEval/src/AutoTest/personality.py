import ast
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
from config import TestModels, language
if language == 'cn':
    from AutoTest.prompts import PersonalityClsPrompt
elif language == 'en':
    from AutoTest.prompts_en import PersonalityClsPrompt
else:
    raise ValueError(f"Invalid language {language}")
from LLMClients import Cost, OpenAIClient
from tqdm import tqdm
from utils import construct_str_dialogue, MBTIMAP, generate_MBTI_str, generate_MBTI_str_en

import glob
import os

MaxWorkers = 10
AllCost = Cost()

def extrct_personalitys(rsp: str) -> Dict[str, int]:
    matches = re.findall(r"{[^}]*}", rsp, re.DOTALL)
    if not matches:
        raise ValueError("Invalid response format in re.findall")
    try:
        json_rsp = ast.literal_eval(matches[-1])
    except:
        raise ValueError("Invalid response format in ast.literal_eval")
    if 'personality' not in json_rsp:
        raise ValueError("Invalid response format in 'personality' not in json_rsp")
    if type(json_rsp['personality']) != str:
        raise ValueError("Invalid response format in type(json_rsp['personality']) != str")
    json_rsp['personality'] = json_rsp['personality'].strip()
    for index, c in enumerate(json_rsp['personality']):
        if c not in list(MBTIMAP.keys())[index * 2: index * 2 + 2]:
            raise ValueError(f"Invalid response format in {c} not in MBTI_MAP")
    return json_rsp['personality']


def eval_chat_personality(chat, role_name, character, style, MBTI, client, model, index):
    global AllCost
    scene = chat['scene']
    dialogues = construct_str_dialogue(chat['dialogues'])
    # dialogues = construct_masked_dialogue(chat['dialogues'])
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": PersonalityClsPrompt.format(role_name=role_name, character=character, dialogues=dialogues, scene=scene, style=style)}
        # {"role": "user", "content": PersonalityClsPrompt.format(role_name="B", character=character, dialogues=dialogues, scene=scene, style=style)}
    ]
    rsps, cost = client.call(messages=messages, model=model, n=1, temperature=0)
    AllCost += cost
    rsp = rsps[0]
    try:
        personality_eval = extrct_personalitys(rsp)
    except Exception as e:
        print(f"Error: {e}")
        personality_eval = None
    chat['personality_eval'] = personality_eval
    chat['personality_analysis_eval'] = rsp
    return index, chat
  
def eval_role_personality(role_file):
    with open(role_file, 'r') as file:
        role_data = json.load(file)

    role_name = role_data['name']
    character = role_data['character']
    style = role_data['style']
    personality = role_data['personality']
    if language == 'en':
        character = character.lower().replace(',', ', ')
        style = style.lower().replace(',', ', ')
    client = OpenAIClient(client_type='openAI')
    model  = 'gpt-4o'
    chats_with_eval = [None] * len(role_data['chats'])
    if language == 'cn':
        MBTI = generate_MBTI_str(personality)
    elif language == 'en':
        MBTI = generate_MBTI_str_en(personality)
    with ThreadPoolExecutor(max_workers=MaxWorkers) as executor:
        futures = [
        executor.submit(eval_chat_personality, chat, role_name, character, style, MBTI, client, model, index) 
        for index, chat in enumerate(role_data['chats'].values())
    ]
        for future in as_completed(futures):
            index, result = future.result()
            chats_with_eval[index] = result
            if result['personality_eval'] is None:
                print(f"Warning: {role_file} with personality_eval is none.")
    role_data['chats'] = {chat['chat_role']: chat for chat in chats_with_eval}
    with open(role_file, 'w') as f:
        json.dump(role_data, f, ensure_ascii=False, indent=4)

        
def main():
    if language == 'cn':
        base_dir = '../chat_dialogues'
    elif language == 'en':
        base_dir = '../chat_dialogues_en'
    for model in TestModels:
        model_dir = os.path.join(base_dir, model)
        test_roles = glob.glob(f"{model_dir}/*.json")
        for role_file in tqdm(test_roles, desc=f"Processing {model} Dialogues Files personality Scale"):
            eval_role_personality(role_file)
    global AllCost
    print(f"AllCost: {AllCost}")
    
# python -m AutoTest.personality
# nohup python -u -m AutoTest.personality > ../logs/personality_eval.log 2>&1 &
if __name__ == '__main__':
    main()
