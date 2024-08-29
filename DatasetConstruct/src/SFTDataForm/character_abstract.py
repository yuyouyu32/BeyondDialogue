import ast
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict

import pandas as pd
from LLMClients import Cost, OpenAIClient
from tqdm import tqdm

from SFTDataForm.prompts import CAPrompt

AllCost = Cost()
MaxWorkers = 16

def extrct_characters(rsp: str) -> Dict[str, str]:
    try:
        rsp = re.findall(r'{[^}]*}', rsp, re.DOTALL)[-1]
        json_rsp = ast.literal_eval(rsp)
        if 'character' in json_rsp:
            return json_rsp['character']
        else:
            return None
    except Exception as e:
        print(e)
        return None


def process_role(index:int, raw: pd.Series, client: OpenAIClient, model: str):
    global AllCost
    role_name = raw['姓名']
    character = raw['性格']
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": CAPrompt.format(role_name=role_name, character=character)}
    ]
    rsps, cost = client.call(messages=messages, model=model, n=1)
    AllCost += cost
    rsp = rsps[0]
    new_character = extrct_characters(rsp)
    raw['new_character'] = new_character
    raw['character_analysis'] = rsp
    return index, raw


def main():
    # Load the roles info from the Excel file
    role_info = pd.read_excel('../../DialogueGenerate/data/Roles Info.xlsx')
    client = OpenAIClient(client_type='openAI')
    model = 'gpt-4o'
    new_role_info = [None] * len(role_info)

    # Create a ThreadPoolExecutor and process the roles with a progress bar
    with ThreadPoolExecutor(max_workers=MaxWorkers) as executor:
        futures = [executor.submit(process_role, index, raw, client, model) for index, raw in role_info.iterrows()]
        
        # Use tqdm to create a progress bar
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing roles"):
            index, raw = future.result()
            new_role_info[index] = raw

    # Convert the list to a DataFrame and save to Excel
    new_role_info = pd.DataFrame(new_role_info)
    new_role_info.to_excel('../../DialogueGenerate/data/Roles Info Processed.xlsx', index=False)
    global AllCost
    print(f"Total cost: {AllCost}")
    
# python -m PromptsFormat.character_abstract
# nohup python -m PromptsFormat.character_abstract > ../logs/character_abstract.log 2>&1 &
if __name__ == '__main__':
    main()
            
            
            
            
    