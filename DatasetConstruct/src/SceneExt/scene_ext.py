import glob
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from tqdm import tqdm

from LLMClients import OpenAIClient
from SceneExt.prompts import *
from utils import collect_novels


def process_chunk(chunk, client):
    chunk_text = chunk['chunk']
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": prompt_cn.format(chunk=chunk_text)}
    ]
    rsps, cost = client.call(messages=messages, model='Qwen1.5-110B-Chat', n=1)
    rsp = rsps[0].replace('[场景]', '').replace('\n', '')
    chunk['scene'] = rsp
    return chunk

def process_novel_jsonl(novel_chunk_path):
    try:
        with open(novel_chunk_path, 'r') as f:
            original_chunks = [json.loads(line) for line in f]
        
        if original_chunks[-1].get('scene') is not None:
            print(f"Already processed {novel_chunk_path}")
            return
        
        new_chunks = []
        client = OpenAIClient(base_url='http://127.0.0.1:8080/v1', api_key='EMPTY')
        
        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = [
                executor.submit(process_chunk, chunk, client)
                for chunk in original_chunks
            ]
            for future in tqdm(as_completed(futures), total=len(futures), desc=f"Processing {novel_chunk_path}"):
                new_chunks.append(future.result())
                
        new_chunks = sorted(new_chunks, key=lambda x: x['id'])
        
        with open(novel_chunk_path, 'w') as f:
            for chunk in new_chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
        
        print(f"Processed {novel_chunk_path}")
    
    except Exception as e:
        print(f"Failed to process {novel_chunk_path}: {e}")

def main():
    novel_root_path = '../../NovelData/novel_chunks'
    novel_files = collect_novels(novel_root_path)
    for novel_file in tqdm(novel_files, desc="Processing Novels"):
        process_novel_jsonl(novel_file)

# python -m SceneExt.scene_ext
# nohup python -u -m SceneExt.scene_ext > ./logs/scene.log 2>&1 &
if __name__ == '__main__':
    main()