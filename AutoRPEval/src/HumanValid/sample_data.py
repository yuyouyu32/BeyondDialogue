import json
import glob
import os
import random
import pandas as pd

from utils import collect_roles, construct_str_dialogue, converts_emb_c_s, converts_emb_p



def main():
    base_dir = '../chat_dialogues/gpt-4o'
    all_role_data = collect_roles(base_dir)
    sample_df = []
    
    for role_name, role_data in all_role_data.items():
        row_data = role_data.copy()
        chats = row_data.pop('chats')
        row_data.pop("style_candidates")
        row_data.pop("character_candidates")
        
        # 从chats中sample 5个随机chat, chats是一个dict
        sample_chats = random.sample(list(chats.values()), 5)
        
        # sample_chats中是5个dict，将每一个dict的key update到row_data中，然后row_data插入到sample_df中
        for chat in sample_chats:
            chat['dialogues'] = construct_str_dialogue(chat['dialogues'])
            chat_data = row_data.copy()
            chat_data.update(chat)
            sample_df.append(chat_data)
    
    sample_df = pd.DataFrame(sample_df)
    # 你可以选择将DataFrame保存到文件或进一步处理
    sample_df.to_excel('../data/sample_chats.xlsx', index=False)

                    
        

# python -m HumanValid.sample_data
if __name__ == '__main__':
    main()