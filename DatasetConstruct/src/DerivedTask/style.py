import ast
import glob
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict

# from DerivedTask.prompts import StyleClsPrompt
from DerivedTask.prompts_en import StyleClsPrompt
from tqdm import tqdm
from utils import collect_roles, retry_on_failure, generate_MBTI_str, construct_str_dialogue, generate_MBTI_str_en

from LLMClients import OpenAIClient, Cost

MaxWorkers = 10
AllCost = Cost()

def extrct_styles(rsp: str, style_candidates) -> Dict[str, int]:
    matches = re.findall(r"{[^}]*}", rsp, re.DOTALL)
    if not matches:
        raise ValueError("Invalid response format in re.findall")
    try:
        json_rsp = ast.literal_eval(matches[-1])
    except:
        raise ValueError("Invalid response format in ast.literal_eval")
    if 'style' not in json_rsp:
        raise ValueError("Invalid response format in 'style' not in json_rsp")
    if type(json_rsp['style']) != str:
        raise ValueError("Invalid response format in type(json_rsp['style']) != str")
    styles = json_rsp['style'].replace(',', '，').split("，")
    styles_result = []
    for style in styles:
        style = style.strip().lower()
        if style not in style_candidates:
            continue
        else:
            styles_result.append(style)
    return styles_result



def process_dialogue(chunk_with_dialogues, role_name, character, MBTI, style, client, model):
    global AllCost
    scene = chunk_with_dialogues['sub_scene']
    dialogues = construct_str_dialogue(chunk_with_dialogues['dialogues'])
    # style_candidates = style.split("、")
    style_candidates = style.lower().split(",")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": StyleClsPrompt.format(role_name=role_name, character=character, dialogues=dialogues, scene=scene, MBTI=MBTI, style_candidates=", ".join(style_candidates))}
    ]
    rsps, cost = client.call(messages=messages, model=model, n=1)
    AllCost += cost
    rsp = rsps[0]
    style
    try:
        style_eval = extrct_styles(rsp, style_candidates)
    except Exception as e:
        print(f"Warning: {e}")
        style_eval = None
    chunk_with_dialogues['style_eval'] = style_eval
    chunk_with_dialogues['style_analysis'] = rsp
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
            if result['style_eval'] is None:
                print(f"Error: {dialogues_file} id: {result['id']} with style_eval is none.")
            if result['style_eval'] == []:
                print(f"Waring: {dialogues_file} id: {result['id']} with style_eval is empty.")
    new_dialogues = sorted(new_dialogues, key=lambda x: x['id'])
    role_data['chunks_with_dialogues'] = new_dialogues
    with open(dialogues_file, 'w') as f:
        json.dump(role_data, f, ensure_ascii=False, indent=4)
    # print(f"Processed {dialogues_file}")

        
def main():
    # role_root_path = '../../NovelData/AB_dialogues_top10len'
    role_root_path = '../../NovelData/AB_dialogues_EN'
    dialogues_files = collect_roles(role_root_path)
    for dialogues_file in tqdm(dialogues_files, desc="Processing Dialogues Files style Scale"):
        process_dialogues_json(dialogues_file)
    global AllCost
    print(f"AllCost: {AllCost}")
    
# python -m DerivedTask.style
# nohup python -u -m DerivedTask.style > ../logs/style_eval.log 2>&1 &
if __name__ == '__main__':
    main()
