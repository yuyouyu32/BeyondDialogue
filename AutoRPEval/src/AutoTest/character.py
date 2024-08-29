import ast
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional


from LLMClients import Cost, OpenAIClient
from tqdm import tqdm
from utils import construct_str_dialogue
from config import TestModels, language
if language == 'cn':
    from AutoTest.prompts import CharacterClsPrompt
elif language == 'en':
    from AutoTest.prompts_en import CharacterClsPrompt
import glob
import os

MaxWorkers = 10
AllCost = Cost()

def extrct_characters(rsp: str, character_candidates: List[str]) -> Dict[str, int]:
    matches = re.findall(r"{[^}]*}", rsp, re.DOTALL)
    if not matches:
        raise ValueError("Invalid response format in re.findall")
    try:
        json_rsp = ast.literal_eval(matches[-1])
    except:
        raise ValueError("Invalid response format in ast.literal_eval")
    if 'character' not in json_rsp:
        raise ValueError("Invalid response format in 'character' not in json_rsp")
    if type(json_rsp['character']) != str:
        raise ValueError("Invalid response format in type(json_rsp['character']) != str")
    if language == 'cn':
        characters = json_rsp['character'].replace(',', '，').split("，")
    elif language == 'en':
        characters = json_rsp['character'].lower().replace('，', ',').split(",")
    character_result = []
    for character in characters:
        character = character.strip()
        if character not in character_candidates:
            continue
            raise ValueError(f"Invalid {character} ({characters}) in {character_candidates}".replace("'", "\""))
        else:
            character_result.append(character)
    return character_result
    
def eval_chat_character(chat, role_name, character_candidates, client, model, index):
    global AllCost
    scene = chat['scene']
    dialogues = construct_str_dialogue(chat['dialogues'])
    if language == 'cn':
        query = CharacterClsPrompt.format(role_name=role_name, dialogues=dialogues, scene=scene, character_candidates="，".join(character_candidates))
    else:
        query = CharacterClsPrompt.format(role_name=role_name, dialogues=dialogues, scene=scene, character_candidates=", ".join(character_candidates))
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": query}
    ]
    rsps, cost = client.call(messages=messages, model=model, n=1, temperature=0)
    AllCost += cost
    rsp = rsps[0]
    try:
        character_eval = extrct_characters(rsp, character_candidates)
    except Exception as e:
        print(f"Error: {role_name} {chat['chat_role']} {e}")
        character_eval = None
    chat['character_eval'] = character_eval
    chat['character_analysis_eval'] = rsp
    return index, chat
  
def eval_role_character(role_file):
    with open(role_file, 'r') as file:
        role_data = json.load(file)
    client = OpenAIClient(client_type='openAI')
    model  = 'gpt-4o'
    role_name = role_data['name']
    if language == 'cn':
        character_candidates = role_data['character'].replace(",", "，").split("，")
    elif language == 'en':
        character_candidates = role_data['character'].lower().replace("，", ",").split(",")
    chats_with_eval = [None] * len(role_data['chats'])
    with ThreadPoolExecutor(max_workers=MaxWorkers) as executor:
        futures = [
        executor.submit(eval_chat_character, chat, role_name, character_candidates, client, model, index) 
        for index, chat in enumerate(role_data['chats'].values())
    ]
        for future in as_completed(futures):
            index, result = future.result()
            chats_with_eval[index] = result
            if result['character_eval'] is None:
                print(f"{role_file} with character_eval is none.")
    role_data['chats'] = {chat['chat_role']: chat for chat in chats_with_eval}
    with open(role_file, 'w') as f:
        json.dump(role_data, f, ensure_ascii=False, indent=4)

        
def main():
    if language == 'cn':
        base_dir = '../chat_dialogues'
    elif language == 'en':
        base_dir = '../chat_dialogues_en'
    test_models = TestModels
    for index, model in enumerate(test_models):
        model_dir = os.path.join(base_dir, model)
        test_roles = glob.glob(f"{model_dir}/*.json")
        for role_file in tqdm(test_roles, desc=f"Processing {model} Dialogues Files character Scale"):
            eval_role_character(role_file)
    global AllCost
    print(f"AllCost: {AllCost}")
    
# python -m AutoTest.character
# nohup python -u -m AutoTest.character > ../logs/character_eval.log 2>&1 &
if __name__ == '__main__':
    main()
