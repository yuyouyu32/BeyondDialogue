import ast
import glob
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict

# from DerivedTask.prompts import CharacterClsPrompt
from DerivedTask.prompts_en import CharacterClsPrompt
from tqdm import tqdm
from utils import collect_roles, generate_MBTI_str, construct_str_dialogue, generate_MBTI_str_en

from LLMClients import OpenAIClient, Cost

MaxWorkers = 10
AllCost = Cost()

def extrct_characters(rsp: str, character_candidates) -> Dict[str, int]:
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
    characters = json_rsp['character'].replace(',', '，').split("，")
    character_result = []
    for character in characters:
        # character = character.strip()
        character = character.strip().lower()
        if character not in character_candidates:
            continue
        else:
            character_result.append(character)
    return character_result



def process_dialogue(chunk_with_dialogues, role_name, character, MBTI, style, client, model):
    global AllCost
    scene = chunk_with_dialogues['sub_scene']
    dialogues = construct_str_dialogue(chunk_with_dialogues['dialogues'])
    # character_candidates = character.replace(",", "，").split("，")
    character_candidates = character.lower().replace(",", "，").split("，")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": CharacterClsPrompt.format(role_name=role_name, style=style, dialogues=dialogues, scene=scene, MBTI=MBTI, character_candidates=", ".join(character_candidates))}
    ]
    rsps, cost = client.call(messages=messages, model=model, n=1)
    AllCost += cost
    rsp = rsps[0]
    character
    try:
        character_eval = extrct_characters(rsp, character_candidates)
    except Exception as e:
        print(f"Warning: {e}")
        character_eval = None
    chunk_with_dialogues['character_eval'] = character_eval
    chunk_with_dialogues['character_analysis'] = rsp
    return chunk_with_dialogues
  
def process_dialogues_json(dialogues_file):
    with open(dialogues_file, 'r') as file:
        role_data = json.load(file)

    role_name = role_data['name']
    character = role_data['character']
    # MBTI = generate_MBTI_str(role_data['personality'])
    MBTI = generate_MBTI_str_en(role_data['personality'])
    style = role_data['style']
    client = OpenAIClient(client_type='openAI')
    model  = 'gpt-4o'
    new_dialogues = []
    with ThreadPoolExecutor(max_workers=MaxWorkers) as executor:
        futures = [
        executor.submit(process_dialogue, chunk_with_dialogues, role_name, character, MBTI, style, client, model) 
        for chunk_with_dialogues in role_data['chunks_with_dialogues']
    ]
        for future in as_completed(futures):
            result = future.result()
            new_dialogues.append(result)
            if result['character_eval'] is None:
                print(f"Error: {dialogues_file} id: {result['id']} with character_eval is none.")
            if result['character_eval'] == []:
                print(f"Warning: {dialogues_file} id: {result['id']} with character_eval is empty.")
    new_dialogues = sorted(new_dialogues, key=lambda x: x['id'])
    role_data['chunks_with_dialogues'] = new_dialogues
    with open(dialogues_file, 'w') as f:
        json.dump(role_data, f, ensure_ascii=False, indent=4)
    # print(f"Processed {dialogues_file}")

        
def main():
    # role_root_path = '../../NovelData/AB_dialogues_top10len'
    role_root_path = '../../NovelData/AB_dialogues_EN'
    dialogues_files = collect_roles(role_root_path)
    for dialogues_file in tqdm(dialogues_files, desc="Processing Dialogues Files character Scale"):
        process_dialogues_json(dialogues_file)
    global AllCost
    print(f"AllCost: {AllCost}")
    
# python -m DerivedTask.character
# nohup python -u -m DerivedTask.character > ../logs/character_eval.log 2>&1 &
if __name__ == '__main__':
    main()
