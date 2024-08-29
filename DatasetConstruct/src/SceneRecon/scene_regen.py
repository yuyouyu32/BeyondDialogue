import glob
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

from tqdm import tqdm
import re

from LLMClients import OpenAIClient, Cost
from SceneRecon.prompts import regen_prompt_cn as regen_prompt
from utils import collect_roles

MaxWorkers = 16
ALL_Cost = Cost()

def get_csv_str_dialogues(dialogues: List[Dict]) -> str:
    if len(dialogues) > 0:
        result = ['role|dialogue']
        for dialogue in dialogues:
            role = dialogue.get('role', '')
            text = dialogue.get('dialogue', '')
            result.append(f'{role}|{text}')
        return '\n'.join(result)
    else:
        return ''

def parse_rsp(rsp: str):
    try:
        rsp = re.findall(r'{[^}]*}', rsp, re.DOTALL)[-1]
        json_rsp = json.loads(rsp)
        if 'scene' not in json_rsp or 'coherence' not in json_rsp:
            raise ValueError(f'Invalid response: {json_rsp}')
        return json_rsp
    except:
        return {'scene': rsp, 'coherence': -1}

def process_dialogue(chunk, client):
    global ALL_Cost
    if "scene" not in chunk or "dialogues" not in chunk:
        raise ValueError(f"Invalid chunk: {chunk}")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": regen_prompt.format(scene=chunk['scene'], dialogue=get_csv_str_dialogues(chunk['dialogues']))}
    ]
    rsps, cost = client.call(messages=messages, model='gpt-4o', n=1)
    # rsp = re.sub(r'\[[^\]]*场景[^\]]*\]', '', rsps[0]).replace('\n', '')
    rsp = re.sub(r'\[[^\]]*Scene[^\]]*\]', '', rsps[0]).replace('\n', '')
    rsp = parse_rsp(rsp)
    ALL_Cost += cost
    chunk['sub_scene'] = rsp['scene']
    chunk['coherence'] = rsp['coherence']
    return chunk

def proces_dialogue_json(file):
    with open(file, 'r') as f:
        role_data = json.load(f)
    new_chunks_with_dialogues = []
    client = OpenAIClient(client_type='openAI')
    # if len(role_data['chunks_with_dialogues']) == 0 or 'sub_scene' in role_data['chunks_with_dialogues'][-1]:
    #     print(f"Skip {file} with sub_scene already processed.")
    #     return
    with ThreadPoolExecutor(max_workers=MaxWorkers) as executor:
        futures = [
            executor.submit(process_dialogue, chunk, client)
            for chunk in role_data['chunks_with_dialogues']
        ]
        for future in as_completed(futures):
            new_chunks_with_dialogues.append(future.result())
    new_chunks_with_dialogues = sorted(new_chunks_with_dialogues, key=lambda x: x['id'])
    for i, chunk in enumerate(new_chunks_with_dialogues):
        if chunk['coherence'] == -1:
            print(f"Failed to process {file} chunk {i}, please check this file manually.")
    role_data['chunks_with_dialogues'] = new_chunks_with_dialogues
    with open(file, 'w') as f:
        f.write(json.dumps(role_data, ensure_ascii=False, indent=4))
    # print(f"Processed {file}")

def main():
    # dialogue_root_path = '../../NovelData/AB_dialogues'
    dialogue_root_path = '../../NovelData/AB_dialogues_EN'
    dialogue_files = collect_roles(dialogue_root_path)
    for file in tqdm(dialogue_files, desc="Processing Novels"):
        proces_dialogue_json(file)
    print(ALL_Cost)
    
# python -m SceneRecon.scene_regen
# nohup python -u -m SceneExt.scene_regen > scene_regen.log 2>&1 &
if __name__ == '__main__':
    main()