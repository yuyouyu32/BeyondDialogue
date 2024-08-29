import ast
import glob
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict

# from DerivedTask.prompts import RelationshipPrompt
from DerivedTask.prompts_en import RelationshipPrompt
from tqdm import tqdm
from utils import collect_roles, retry_on_failure, generate_MBTI_str, construct_str_dialogue, generate_MBTI_str_en

from LLMClients import OpenAIClient, Cost

MaxWorkers = 10
AllCost = Cost()

def extrct_relationship(rsp: str) -> Dict[str, int]:
    matches = re.findall(r"{[^}]*}", rsp, re.DOTALL)
    if not matches:
        raise ValueError("Invalid response format in re.findall")
    rsp = matches[-1]
    try:
        json_rsp = ast.literal_eval(rsp)
    except:
        raise ValueError("Invalid response format in ast.literal_eval")
    if 'relationship' not in json_rsp:
        raise ValueError("Invalid response format in 'relationship' not in json_rsp")
    else:
        try:
            return int(json_rsp['relationship'])
        except:
            raise ValueError("Invalid response format in int(json_rsp['relationship'])")

@retry_on_failure(retries=5)
def process_dialogue(chunk_with_dialogues, role_name, character, MBTI, style, client, model):
    global AllCost
    scene = chunk_with_dialogues['sub_scene']
    dialogues = construct_str_dialogue(chunk_with_dialogues['dialogues'])
    target_name = chunk_with_dialogues['dialogues'][0]['role']
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": RelationshipPrompt.format(role_name=role_name, character=character, dialogues=dialogues, scene=scene, target_name=target_name, MBTI=MBTI, style=style)}
    ]
    rsps, cost = client.call(messages=messages, model=model, n=1)
    AllCost += cost
    rsp = rsps[0]
    relationship_score = extrct_relationship(rsp)
    chunk_with_dialogues['relationship'] = relationship_score
    chunk_with_dialogues['relationship_analysis'] = rsp
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
    # if 'relationship' in role_data['chunks_with_dialogues'][-1]:
    #     print(f"Skip {dialogues_file} with relationship already processed.")
    #     return 
    with ThreadPoolExecutor(max_workers=MaxWorkers) as executor:
        futures = [
        executor.submit(process_dialogue, chunk_with_dialogues, role_name, character, MBTI, style, client, model) 
        for chunk_with_dialogues in role_data['chunks_with_dialogues']
    ]
        for future in tqdm(as_completed(futures), total=len(futures), desc=f"Processing Dialogues {dialogues_file} Relationship"):
            result = future.result()
            new_dialogues.append(result)
            if result['relationship'] is None:
                print(f"Error: {dialogues_file} id: {result['id']} with relationship is none.")
    new_dialogues = sorted(new_dialogues, key=lambda x: x['id'])
    role_data['chunks_with_dialogues'] = new_dialogues
    with open(dialogues_file, 'w') as f:
        json.dump(role_data, f, ensure_ascii=False, indent=4)
    # print(f"Processed {dialogues_file}")

        
def main():
    # role_root_path = '../../NovelData/AB_dialogues_top10len'
    role_root_path = '../../NovelData/AB_dialogues_EN'
    dialogues_files = collect_roles(role_root_path)
    for dialogues_file in tqdm(dialogues_files, desc="Processing Dialogues Files Relationship Scale"):
        process_dialogues_json(dialogues_file)
    global AllCost
    print(f"AllCost: {AllCost}")
    
# python -m DerivedTask.relationship
if __name__ == '__main__':
    main()
