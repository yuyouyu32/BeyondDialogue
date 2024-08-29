import ast
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

from config import TestModels, language

if language == 'cn':
    from AutoTest.prompts import StyleClsPrompt
elif language == 'en':
    from AutoTest.prompts_en import StyleClsPrompt
else:
    raise ValueError(f"Invalid language {language}")
import glob
import os

from LLMClients import Cost, OpenAIClient
from tqdm import tqdm
from utils import construct_str_dialogue

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
    if language == 'cn':
        styles = json_rsp['style'].replace(',', '，').split("，")
    else:
        styles = json_rsp['style'].lower().replace('，', ',').split(",")
    styles_result = []
    for style in styles:
        style = style.strip()
        if style not in style_candidates:
            continue
            raise ValueError(f"Invalid {style} ({styles}) in {style_candidates}".replace("'", "\""))
        else:
            styles_result.append(style)
    return styles_result
    

def eval_chat_style(chat, role_name, style_candidates, client, model, index):
    global AllCost
    scene = chat['scene']
    dialogues = construct_str_dialogue(chat['dialogues'])
    if language == 'cn':
        query = StyleClsPrompt.format(role_name=role_name, dialogues=dialogues, scene=scene, style_candidates="，".join(style_candidates))
    elif language == 'en':
        query = StyleClsPrompt.format(role_name=role_name, dialogues=dialogues, scene=scene, style_candidates=", ".join(style_candidates))
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": query}
    ]
    rsps, cost = client.call(messages=messages, model=model, n=1, temperature=0)
    AllCost += cost
    rsp = rsps[0]
    try:
        style_eval = extrct_styles(rsp, style_candidates)
    except Exception as e:
        print(f"Error: {role_name} {chat['chat_role']} {e}")
        style_eval = None
    chat['style_eval'] = style_eval
    chat['style_analysis_eval'] = rsp
    return index, chat
  
def eval_role_style(role_file):
    with open(role_file, 'r') as file:
        role_data = json.load(file)
    client = OpenAIClient(client_type='openAI')
    model  = 'gpt-4o'
    role_name = role_data['name']
    if language == 'cn':
        style_candidates = role_data['style'].split("、")
    elif language == 'en':
        style_candidates = role_data['style'].lower().split(",")
    chats_with_eval = [None] * len(role_data['chats'])
    with ThreadPoolExecutor(max_workers=MaxWorkers) as executor:
        futures = [
        executor.submit(eval_chat_style, chat, role_name, style_candidates, client, model, index) 
        for index, chat in enumerate(role_data['chats'].values())
    ]
        for future in as_completed(futures):
            index, result = future.result()
            chats_with_eval[index] = result
            if result['style_eval'] is None:
                print(f"{role_file} with style_eval is none.")
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
        for role_file in tqdm(test_roles, desc=f"Processing {model} Dialogues Files style Scale"):
            eval_role_style(role_file)
    global AllCost
    print(f"AllCost: {AllCost}")
    
# python -m AutoTest.style
# nohup python -u -m AutoTest.style > ../logs/style_eval.log 2>&1 &
if __name__ == '__main__':
    main()
