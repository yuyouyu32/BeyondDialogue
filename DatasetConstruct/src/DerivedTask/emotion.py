import ast
import glob
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict

# from DerivedTask.prompts import EmotionPrompt
from DerivedTask.prompts_en import EmotionPrompt
from tqdm import tqdm
from utils import collect_roles, retry_on_failure, generate_MBTI_str, construct_str_dialogue, generate_MBTI_str_en

from LLMClients import OpenAIClient, Cost

MaxWorkers = 10
AllCost = Cost()

def extrct_emotions(rsp: str) -> Dict[str, int]:
    matches = re.findall(r"{[^}]*}", rsp, re.DOTALL)
    if not matches:
        raise ValueError("Invalid response format in re.findall")
    try:
        json_rsp = ast.literal_eval(matches[-1])
    except:
        raise ValueError("Invalid response format in ast.literal_eval")
    emotions_scale_scores = {}
    for key in json_rsp.keys():
        # if key in ['快乐', '悲伤', '厌恶', '恐惧', '惊讶', '愤怒']:
        if key in ['happiness', 'sadness', 'disgust', 'fear', 'surprise', 'anger']:
            try:
                emotions_scale_scores[key] = int(json_rsp[key])
            except:
                raise ValueError("Invalid response format in int(json_rsp[key])")
    if len(emotions_scale_scores) != 6:
        raise ValueError("Invalid response format in len(emotions_scale_scores) != 6")
    return emotions_scale_scores

@retry_on_failure(retries=5)
def process_dialogue(chunk_with_dialogues, role_name, character, MBTI, style, client, model):
    global AllCost
    scene = chunk_with_dialogues['sub_scene']
    dialogues = construct_str_dialogue(chunk_with_dialogues['dialogues'])
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": EmotionPrompt.format(role_name=role_name, character=character, dialogues=dialogues, scene=scene, MBTI=MBTI, style=style)}
    ]
    rsps, cost = client.call(messages=messages, model=model, n=1)
    AllCost += cost
    rsp = rsps[0]
    emotion_scale_scores = extrct_emotions(rsp)
    chunk_with_dialogues['emotion_scale_scores'] = emotion_scale_scores
    chunk_with_dialogues['emotion_analysis'] = rsp
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
    # if 'emotion_scale_scores' in role_data['chunks_with_dialogues'][-1]:
    #     print(f"Skip {dialogues_file} with emotion_scale_scores already processed.")
    #     return 
    with ThreadPoolExecutor(max_workers=MaxWorkers) as executor:
        futures = [
        executor.submit(process_dialogue, chunk_with_dialogues, role_name, character, MBTI, style, client, model) 
        for chunk_with_dialogues in role_data['chunks_with_dialogues']
    ]
        for future in tqdm(as_completed(futures), total=len(futures), fdesc=f"Processing Dialogues {dialogues_file} Emotions"):
            result = future.result()
            new_dialogues.append(result)
            if result['emotion_scale_scores'] is None:
                print(f"Error: {dialogues_file} id: {result['id']} with emotion_scale_scores is none.")
    new_dialogues = sorted(new_dialogues, key=lambda x: x['id'])
    role_data['chunks_with_dialogues'] = new_dialogues
    with open(dialogues_file, 'w') as f:
        json.dump(role_data, f, ensure_ascii=False, indent=4)
    # print(f"Processed {dialogues_file}")

        
def main():
    # role_root_path = '../../NovelData/AB_dialogues_top10len'
    role_root_path = '../../NovelData/AB_dialogues_EN'
    dialogues_files = collect_roles(role_root_path)
    for dialogues_file in tqdm(dialogues_files, desc="Processing Dialogues Files Emotion Scale"):
        process_dialogues_json(dialogues_file)
    global AllCost
    print(f"AllCost: {AllCost}")
    
# python -m DerivedTask.emotion
if __name__ == '__main__':
    main()
