import ast
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

from config import TestModels, language
if language == 'cn':
    from AutoTest.prompts import EmotionScalePrompt
elif language == 'en':
    from AutoTest.prompts_en import EmotionScalePrompt
else:
    raise ValueError(f"Invalid language {language}")
from LLMClients import Cost, OpenAIClient
from tqdm import tqdm
from utils import generate_MBTI_str, construct_str_dialogue, generate_MBTI_str_en

import glob
import os

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
    if language == 'cn':
        valid_keys = ['快乐', '悲伤', '厌恶', '恐惧', '惊讶', '愤怒']
    elif language == 'en':
        valid_keys = ['happiness', 'sadness', 'disgust', 'fear', 'surprise', 'anger']
    for key in json_rsp.keys():
        if key in valid_keys:
            try:
                emotions_scale_scores[key] = int(json_rsp[key])
            except:
                raise ValueError("Invalid response format in int(json_rsp[key])")
    if len(emotions_scale_scores) != 6:
        raise ValueError("Invalid response format in len(emotions_scale_scores) != 6")
    return emotions_scale_scores

def eval_chat_emotion(chat, role_name, character, MBTI, style, client, model, index):
    global AllCost
    scene = chat['scene']
    dialogues = construct_str_dialogue(chat['dialogues'])
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": EmotionScalePrompt.format(role_name=role_name, character=character, dialogues=dialogues, scene=scene, MBTI=MBTI, style=style)}
    ]
    rsps, cost = client.call(messages=messages, model=model, n=1, temperature=0)
    AllCost += cost
    rsp = rsps[0]
    try:
        emotion_eval = extrct_emotions(rsp)
    except Exception as e:
        print(f"Error: {e}")
        emotion_eval = None
    chat['emotion_eval'] = emotion_eval
    chat['emotion_analysis_eval'] = rsp
    return index, chat
  
def eval_role_emotion(role_file):
    with open(role_file, 'r') as file:
        role_data = json.load(file)

    role_name = role_data['name']
    character = role_data['character']
    style = role_data['style']
    if language == 'cn':
        MBTI = generate_MBTI_str(role_data['personality'])
    elif language == 'en':
        MBTI = generate_MBTI_str_en(role_data['personality'])
        character = character.lower().replace(",", ", ")
        style = style.lower().replace(",", ", ")
    client = OpenAIClient(client_type='openAI')
    model  = 'gpt-4o'
    chats_with_eval = [None] * len(role_data['chats'])
    with ThreadPoolExecutor(max_workers=MaxWorkers) as executor:
        futures = [
        executor.submit(eval_chat_emotion, chat, role_name, character, MBTI, style, client, model, index) 
        for index, chat in enumerate(role_data['chats'].values())
    ]
        for future in as_completed(futures):
            index, result = future.result()
            chats_with_eval[index] = result
            if result['emotion_eval'] is None:
                print(f"Warning: {role_file} with emotion_eval is none.")
    role_data['chats'] = {chat['chat_role']: chat for chat in chats_with_eval}
    with open(role_file, 'w') as f:
        json.dump(role_data, f, ensure_ascii=False, indent=4)

        
def main():
    if language == 'cn':
        base_dir = '../chat_dialogues'
    elif language == 'en':
        base_dir = '../chat_dialogues_en'
    test_models = TestModels
    for model in test_models:
        model_dir = os.path.join(base_dir, model)
        test_roles = glob.glob(f"{model_dir}/*.json")
        for role_file in tqdm(test_roles, desc=f"Processing {model} Dialogues Files emotion Scale"):
            eval_role_emotion(role_file)
    global AllCost
    print(f"AllCost: {AllCost}")
    
# python -m AutoTest.emotion
# nohup python -u -m AutoTest.emotion > ../logs/emotion_eval.log 2>&1 &
if __name__ == '__main__':
    main()
