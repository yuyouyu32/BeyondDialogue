
import asyncio
import concurrent.futures
import json
import os
import time
from typing import Dict, List, Optional
import copy

import requests
import websockets
from config import model_config, DialogueModels, language
if language == 'cn':
    from AutoDialog.prompts import ChatRoleSysPrompt
elif language == 'en':
    from AutoDialog.prompts import ChatRoleSysPromptEN as ChatRoleSysPrompt
else:
    raise ValueError("Invalid language")
from LLMClients import Cost, OpenAIClient
from tqdm import tqdm
from utils import collect_roles, construct_emotion, construct_emotion_en

ALL_Cost = Cost()
MaxWorkers = 1
MaxTrun = 10

async def get_rsp_from_ip(ip: str, port: int, messages: List[Dict[str, str]], do_sample: bool = True, temperature: float = 0.7, session_meta: Optional[Dict] = None):
    url = f"ws://{ip}:{port}"
    async with websockets.connect(url, timeout=60) as websocket:
        await websocket.send(json.dumps({"messages": messages, "do_sample": do_sample, "temperature": temperature, "session_meta": session_meta if session_meta else ""}))
        try:
            response = await asyncio.wait_for(websocket.recv(), 60)
            response_data = json.loads(response)
            return response_data["response"]
        except Exception as e:
            print(f"Error: {e}, ip: {ip}, port: {port}, return empty string")
            return ""
    
def get_baichuanNPC_rsp(model_name, messages: List[Dict[str, str]], character_profile, temperature: float = 0.8):
    url = "https://api.baichuan-ai.com/v1/chat/completions"
    api_key = "sk-xxxx"
    data = {
        "model": model_name,
        "character_profile": character_profile,
        "messages": messages,
        "temperature": temperature,
        "top_k":10,
        "max_tokens": 512,
        "stream": False
    }

    json_data = json.dumps(data)

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key
    }

    response = requests.post(url, data=json_data, headers=headers, timeout=60)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]['content']
    else:
        print("请求失败，状态码:", response.status_code)
        print("请求失败，body:", response.text)
        print("请求失败，X-BC-Request-Id:", response.headers.get("X-BC-Request-Id"))
        raise ValueError("Request failed")

def chat_role_speak(system_prompt: str, instruction: str, history: List[List[str]], client: OpenAIClient):
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    for user_content, assistant_content in history:
        messages.append({"role": "user", "content": user_content})
        messages.append({"role": "assistant", "content": assistant_content})
    messages.append({"role": "user", "content": instruction})
    rsps, cost = client.call(messages=messages, model="gpt-4o", n=1)
    global ALL_Cost
    ALL_Cost += cost
    rsp = rsps[0]
    return rsp

def role_speak(system_prompt: str, instruction: str, history: List[List[str]], model_name: str, client: Optional[OpenAIClient], character_profile: Optional[Dict] = None):
    messages = [
            {"role": "system", "content": system_prompt}
        ]
    for user_content, assistant_content in history:
        messages.append({"role": "user", "content": user_content})
        messages.append({"role": "assistant", "content": assistant_content})
    messages.append({"role": "user", "content": instruction})
    if model_name == "Baichuan-NPC-Turbo":
        rsp = get_baichuanNPC_rsp(model_name, messages, character_profile)
    elif model_name not in model_config.keys():
        rsps, cost = client.call(messages=messages, model=model_name, n=1, temperature=0)
        global ALL_Cost
        ALL_Cost += cost
        rsp = rsps[0]
    else:
        ip = model_config[model_name]['ip']
        port = model_config[model_name]['port']
        if model_name == "CharacterGLM":
            session_meta = {
                'user_info': character_profile["user_info"], 
                'user_name': character_profile["user_name"],
                'bot_info': system_prompt, 
                'bot_name': character_profile["character_name"]
            }
        else:
            session_meta = None
        rsp = asyncio.run(get_rsp_from_ip(ip, port, messages, do_sample=True, session_meta=session_meta))
    return rsp

def process_chat_role(model_name, role_name, role_data, chat_role, chat, role_client: OpenAIClient, chat_role_client:OpenAIClient):
    role_name = role_data['name']
    world = role_data['world']
    sys_prompt_temp = role_data['sys_prompt']
    style = role_data['style']
    if language == "cn":
        chat_role_style = "古风" if "古风" in style else "白话文"
    else:
        chat_role_style = ""
    chat_role_des = chat['role_des']
    if language == "cn":
        emotion_scale_scores = construct_emotion(chat['emotions'])
    elif language == "en":
        emotion_scale_scores = construct_emotion_en(chat['emotions'])
    relationship = chat['relationship_score']
    scene = chat['scene']
    
    role_sys_prompt = sys_prompt_temp.format(chat_role=chat_role, emotion=emotion_scale_scores, relationship=relationship, scene=scene)
    chat_role_sys_prompt = ChatRoleSysPrompt.format(chat_role=chat_role, role_name=role_name, role_des=chat_role_des, scene=scene, relationship=relationship, world=world, chat_role_style=chat_role_style)
    role_history = []
    chat_role_history = []
    
    role_instruction = ""
    chat_role_instruction = ""
    
    dialogues = []
    character_profile = {
        "character_name": role_name,
        "character_info": role_sys_prompt,
        "user_name": chat_role,
        "user_info": chat_role_sys_prompt
    }
    for turn in range(MaxTrun):
        if turn % 2 == 0:
            rsp = chat_role_speak(system_prompt=chat_role_sys_prompt, instruction=chat_role_instruction, history=chat_role_history, client=chat_role_client)
            rsp =  rsp.strip().split("\n")[0]
            chat_role_history.append([chat_role_instruction, rsp])
            role_instruction = rsp
            dialogues.append({"role": chat_role, "dialogue": rsp})
        else:
            rsp = role_speak(system_prompt=role_sys_prompt, instruction=role_instruction, history=role_history, model_name=model_name, client=role_client, character_profile=character_profile)
            rsp = rsp.strip().split("\n")[0]
            role_history.append([role_instruction, rsp])
            chat_role_instruction = rsp
            dialogues.append({"role": role_name, "dialogue": rsp})
    return (chat_role, dialogues)

def main():
    test_models = DialogueModels
    if language == 'cn':
        roles = collect_roles("../data/roles")
        base_save_dir = "../chat_dialogues/"
    elif language == 'en':
        roles = collect_roles("../data/roles_en")
        base_save_dir = "../chat_dialogues_en/"
    if not os.path.exists(base_save_dir):
        os.makedirs(base_save_dir)
    chat_role_client = OpenAIClient()
    role_client = OpenAIClient() # baichuan, 01-AI, deepseek
    def process_model(model_name):
        save_dir_path = os.path.join(base_save_dir, model_name)
        if not os.path.exists(save_dir_path):
            os.makedirs(save_dir_path)
        for role_name, role_data in tqdm(roles.items(), desc=f"Model: {model_name}"):
            with concurrent.futures.ThreadPoolExecutor(max_workers=MaxWorkers) as executor:
                futures = {executor.submit(process_chat_role, model_name, role_name, role_data, chat_role, chat, role_client, chat_role_client): chat_role for chat_role, chat in role_data['chats'].items()}
                save_results = copy.deepcopy(role_data)
                for future in concurrent.futures.as_completed(futures):
                    chat_role = futures[future]
                    chat_role, dialogues = future.result()
                    save_results['chats'][chat_role]['dialogues'] = dialogues
            role_save_path = os.path.join(save_dir_path, f"{role_name}.json")
            with open(role_save_path, 'w') as f:
                json.dump(save_results, f, indent=4, ensure_ascii=False)
            # print(f"Processed {role_name} chat roles and saved in {role_save_path}.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as model_executor:
        model_futures = {model_executor.submit(process_model, model_name): model_name for model_name in test_models}
        for future in concurrent.futures.as_completed(model_futures):
            model_name = model_futures[future]
            future.result()

    global ALL_Cost
    print(f"Total Cost: {ALL_Cost}")
           
# python -m AutoDialog.auto_dialogues
# nohup python -u -m AutoDialog.auto_dialogues > ../logs/auto_dialogues.log 2>&1 &
if __name__ == "__main__":
    main()