import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

from tqdm import tqdm

from LLMClients import OpenAIClient, Cost
from SFTDataForm.prompts import SystemPromptFormat, SystemTemp

ALL_Cost = Cost()

def process_row_system_prompt_format(row: pd.Series, client: OpenAIClient, index):
    global ALL_Cost
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": SystemPromptFormat.format(role_name= row['姓名'], character=row['new_character'], MBTI=row['人格'], style=row['说话风格'], world=row['world'], example=SystemTemp)}
    ]
    rsps, cost = client.call(messages=messages, model='gpt-4o', n=1)
    rsp = rsps[0].strip('"')
    ALL_Cost += cost
    row['sys_prompt'] = rsp
    return index, row

def main():
    role_info = pd.read_excel("../../DialogueGenerate/data/Roles Info.xlsx")
    client = OpenAIClient()
    # 多线程，带进度条apply process_row_system_prompt_format
    new_df = [None] * len(role_info)
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(process_row_system_prompt_format, row, client, index) for index, row in role_info.iterrows()]
        for future in tqdm(as_completed(futures), total=len(futures)):
            index, row = future.result()
            new_df[index] = row
    print(ALL_Cost)
    new_df = pd.DataFrame(new_df)
    new_df.to_excel("../../DialogueGenerate/data/Roles Info.xlsx", index=False)

# nohup python -u -m SFTDataForm.system_prompt_format > ../logs/system_prompt_format.log 2>&1 &
if __name__ == '__main__':
    main()