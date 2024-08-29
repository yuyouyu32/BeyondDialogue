import asyncio
import json
import os
import time
from typing import Dict, List, Optional

import websockets
from config import model_config, TestModels

from LLMClients import Cost, OpenAIClient
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from CESRPExp.parse_uitls import ExtractFuncs


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
        
        
def get_eval_result(test_data, model_name: str, client: Optional[OpenAIClient]):
    messages = test_data["Q"]
    Q_type = test_data["type"]
    language = test_data["language"]
    answer = test_data["A"]
    extract_result = None
    rsp = None
    if model_name not in model_config.keys():
        rsps, cost = client.call(messages=messages, model=model_name, n=1)
        rsp = rsps[0]
        try_times = 0
        while try_times < 5:
            try:
                if Q_type in {"character", "style"}:
                    extract_result = ExtractFuncs[Q_type](rsp, answer)
                else:
                    extract_result = ExtractFuncs[Q_type](rsp, language)
                global ALL_Cost
                ALL_Cost += cost
                break
            except:
                try_times += 1
                rsps, cost = client.call(messages=messages, model=model_name, n=1)
                rsp = rsps[0]

    else:
        ip = model_config[model_name]['ip']
        port = model_config[model_name]['port']
        rsp = asyncio.run(get_rsp_from_ip(ip, port, messages=messages))
        try_times = 0
        while try_times < 5:
            try:
                if Q_type in {"character", "style"}:
                    extract_result = ExtractFuncs[Q_type](rsp, answer)
                else:
                    extract_result = ExtractFuncs[Q_type](rsp, language)
                break
            except:
                try_times += 1
                rsp = asyncio.run(get_rsp_from_ip(ip, port, messages=messages))
    result = test_data.copy()
    result["eval_result"] =  extract_result if extract_result else ""
    result["rsp"] = rsp
    return result


def process_model(model_name, all_test_data, client, save_dir):
    results = []
    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(get_eval_result, test_data, model_name, client) for test_data in all_test_data]
        for future in tqdm(futures, desc=model_name):
            results.append(future.result())

    save_path = os.path.join(save_dir, f"{model_name}_CESRP_test.json")
    with open(save_path, 'w', encoding='utf-8') as f:
        json_string = "[" + ",\n".join(json.dumps(item, ensure_ascii=False) for item in results) + "]"
        f.write(json_string)
        
def main():
    data_path = "../data/CESRP_test.json"
    save_dir = "../data/CESRP_results/"
    all_test_data = json.load(open(data_path, "r"))
    test_models = TestModels
    client = OpenAIClient()
    global ALL_Cost
    ALL_Cost = Cost()
    with ThreadPoolExecutor(max_workers=len(test_models)) as executor:
        futures = [executor.submit(process_model, model_name, all_test_data, client, save_dir) for model_name in test_models]
        for future in futures:
            future.result()
        
# python -m CESRPExp.auto_test
if __name__ == "__main__":
    main()