import ast
import glob
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

from tqdm import tqdm

from ChunkEval.prompts import *
from LLMClients import OpenAIClient
from utils import collect_roles


def extrct_score(raw_texts: List[str]) -> Optional[int]:
    scores = []
    for rsp in raw_texts:
        try:
            rsp = re.findall(r'\{.*?\}', rsp)[0]
            json_rsp = ast.literal_eval(rsp)
            scores.append(int(json_rsp['score']))
        except:
            continue
    if scores:
        return sum(scores) / len(scores)
    else:
        return None

def process_chunk(chunk, role_name, character, client):
    chunk_text = chunk['chunk']
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": prompt_cn.format(role_name=role_name, character=character, chunk=chunk_text)}
    ]
    rsps, cost = client.call(messages=messages, model='Qwen1.5-110B-Chat', n=5)
    score = extrct_score(rsps)
    chunk['score'] = score
    return chunk
  
def process_role_json(role_path):
    try:
        with open(role_path, 'r') as file:
            role_data = json.load(file)

        role_name = role_data['姓名']
        character = role_data['性格']
        client = OpenAIClient(base_url='http://127.0.0.1:8080/v1', api_key='EMPTY')

        if role_data['chunks'][-1].get('score') is not None:
            print(f"Already processed {role_path}")
            return

        new_chunks = []
        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = [
                executor.submit(process_chunk, chunk, role_name, character, client)
                for chunk in role_data['chunks']
            ]
            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing Chunks"):
                new_chunks.append(future.result())
                
        new_chunks = sorted(new_chunks, key=lambda x: x['id'])
        role_data['chunks'] = new_chunks
        with open(role_path, 'w') as f:
            json.dump(role_data, f, ensure_ascii=False, indent=4)
        print(f"Processed {role_path}")
    except Exception as e:
        print(f"Failed to process {role_path}: {e}")
        
def main():
    role_root_path = '../../NovelData/roles'
    role_files = collect_roles(role_root_path)
    for role_file in tqdm(role_files, desc="Processing Roles"):
        process_role_json(role_file)
    
# python -m ChunkEval.chunk_eval  
if __name__ == '__main__':
    main()
