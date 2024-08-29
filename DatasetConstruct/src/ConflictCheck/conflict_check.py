import glob
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

from tqdm import tqdm
import re

from LLMClients import OpenAIClient, Cost
from ConflictCheck.prompts import prompt_cn_conflict_check
from utils import collect_roles, generate_MBTI_str, generate_MBTI_str_en

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
        if "conflict" not in json_rsp:
            raise ValueError(f"Invalid response: {json_rsp}")
        if json_rsp["conflict"] not in [0, 1]:
            raise ValueError(f"Invalid conflict value: {json_rsp['conflict']}")
        return json_rsp
    except:
        return {"conflict": -1}

def process_dialogue(chunk, client, role_des):
    global ALL_Cost
    if "scene" not in chunk or "dialogues" not in chunk:
        raise ValueError(f"Invalid chunk: {chunk}")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt_cn_conflict_check.format(scene=chunk['scene'], dialogue=get_csv_str_dialogues(chunk['dialogues']), role_des=role_des)}
    ]
    rsps, cost = client.call(messages=messages, model='gpt-4o', n=1)
    rsp = rsps[0]
    rsp = parse_rsp(rsp)
    ALL_Cost += cost
    chunk['conflict'] = rsp['conflict']
    return chunk

def proces_dialogue_json(file):
    with open(file, 'r') as f:
        role_data = json.load(f)
    new_chunks_with_dialogues = []
    client = OpenAIClient(client_type='openAI')
    role_name = role_data['name']
    character = role_data['character']
    # MBTI = generate_MBTI_str(role_data['personality'])
    MBTI = generate_MBTI_str_en(role_data['personality'])
    style = role_data['style']
    role_des = "{role_name}的性格是{character}，MBTI人格类型是{MBTI}，说话风格是{style}。".format(role_name=role_name, character=character, MBTI=MBTI, style=style)
    with ThreadPoolExecutor(max_workers=MaxWorkers) as executor:
        futures = [
            executor.submit(process_dialogue, chunk, client, role_des)
            for chunk in role_data['chunks_with_dialogues']
        ]
        for future in as_completed(futures):
            new_chunks_with_dialogues.append(future.result())
    new_chunks_with_dialogues = sorted(new_chunks_with_dialogues, key=lambda x: x['id'])
    for i, chunk in enumerate(new_chunks_with_dialogues):
        if chunk['conflict'] == -1:
            print(f"Error in {file} chunk {i}: {chunk}")
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
    
# python -m ConflictCheck.conflict_check
# nohup python -u -m ConflictCheck.conflict_check > conflict_check.log 2>&1 &
if __name__ == '__main__':
    main()