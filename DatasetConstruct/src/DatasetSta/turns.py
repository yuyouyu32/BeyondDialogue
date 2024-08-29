import glob
import json
import os
import matplotlib.pyplot as plt
from kor.extraction.parser import KorParser
from kor.nodes import Object
from kor.encoders import initialize_encoder
import pandas as pd
import seaborn as sns

schema_parse = Object(
    id="script",
    attributes=[]
)
encoder = initialize_encoder("csv", schema_parse)
OutputParser=KorParser(encoder=encoder, validator=None, schema_=schema_parse)


def process_dialogues(dialogues):
    if len(dialogues) > 0:
        result = ['role|dialogue']
        for dialogue in dialogues:
            role = dialogue.get('role', '')
            text = dialogue.get('dialogue', '')
            result.append(f'{role}|{text}')
        return '\n'.join(result)
    else:
        return ''

def novel_chunks_statis():
    novel_chunks_path = '../novel_chunks'
    files = glob.glob(os.path.join(novel_chunks_path, '*.jsonl'))
    statis = {'all_novel_chunk_nums': 0}
    for file in files:
        novel_name = os.path.basename(file).split('_')[0]
        chunk_nums = len(open(file, 'r').readlines())
        statis[novel_name] = {'novel_chunk_num': chunk_nums}
        statis['all_novel_chunk_nums'] += chunk_nums
    with open(os.path.join('./novel_statis.json'), 'w') as f:
        json.dump(statis, f, indent=4, ensure_ascii=False)

def role_chunks_statis():
    role_chunks_path = '../roles'
    files = glob.glob(os.path.join(role_chunks_path, '*/*.json'))
    statis = {'all_role_chunk_nums': 0}
    for file in files:
        role_name = os.path.basename(file).split('.')[0]
        novel_name = file.split('/')[-2]
        chunk_nums = json.load(open(file, 'r'))['chunk_nums']
        if novel_name not in statis:
            statis[novel_name] = {}
        temp = statis[novel_name].get(role_name, 0)
        temp += chunk_nums
        statis[novel_name][role_name] = temp
        statis['all_role_chunk_nums'] += chunk_nums
    novels_num, roles_num = 0,0
    error_role = {}
    for novel, statis in statis.items():
        if novel in {'all_role_chunk_nums', 'all_novel_chunk_nums'}: continue
        novels_num += 1
        for role in statis:
            if role == 'novel_chunk_num': continue
            roles_num += 1
            if statis[role] < 10:
                if novel not in error_role:
                    error_role[novel] = {}
                error_role[novel][role] = statis[role]
    statis['novels_num'] = novels_num
    statis['roles_num'] = roles_num
    statis['error_role'] = error_role
    with open(os.path.join('./statis.json'), 'w') as f:
        json.dump(statis, f, indent=4, ensure_ascii=False)

def process_dialog_names(role_name: str, names, dialogs):
    if type(dialogs) == str:
        return dialogs
    for dialog in dialogs:
        if dialog["role"] in names:
            dialog["role"] = role_name
    return dialogs

def process_trush(dialogues_string):
    rows = dialogues_string.split('\n')
    modify_rows = []
    for row in rows:
        if row.count('|') == 1:
            modify_rows.append(row)
        else:
            # 删除第二个以后的|
            parts = row.split('|')
            new_row = parts[0] + '|' + ''.join(parts[1:]).replace('|', '')
            modify_rows.append(new_row)
    dialogues_string = '\n'.join(modify_rows)
    parse_result = OutputParser.parse(dialogues_string)
    if not parse_result['errors']:
        return parse_result['data']['script']
    else:
        return dialogues_string
         
def draw_turns_count(turns_count, name):
    plt.figure(figsize=(14, 10))
    
    # Sort turns_count by key
    turns_count = dict(sorted(turns_count.items(), key=lambda x: x[0]))
    
    # Modify turns_count to group values exceeding 20 into "20+"
    turns_count_modified = {}
    for key, value in turns_count.items():
        if key <= 20:
            turns_count_modified[key] = value
        else:
            turns_count_modified["20+"] = turns_count_modified.get("20+", 0) + value
    
    turns_count_modified_str_keys = {str(k): v for k, v in turns_count_modified.items()}
    
    sns.barplot(
        x=list(turns_count_modified_str_keys.keys()), 
        y=list(turns_count_modified_str_keys.values()), 
        hue=list(turns_count_modified_str_keys.keys()), 
        dodge=False, 
        palette="viridis"
    )
    
    plt.xlabel('Dialogue Turns', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)
    # plt.title('Distribution of Dialogue Turns', fontsize=18)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.legend([],[], frameon=False)  # Remove the legend created by hue
    plt.tight_layout()  # Adjust layout to make room for the rotated x-axis labels
    plt.savefig(f'./{name}_Distribution of Dialogue Turns.pdf', dpi=500)
    plt.show()

def dialogue_statis():
    dir_name = 'AB_dialogues_EN'
    dialogue_path = '../../NovelData/AB_dialogues_EN'
    files = glob.glob(os.path.join(dialogue_path, '*/*.json'))
    statis = {'all_dialogue_nums': 0, 'all_dialogue_turns': 0, 'ave_dialogue_turns': 0}
    turns_count = {}
    trunsh_record = {}
    for file in files:
        role_data = json.load(open(file, 'r'))
        dialogue_nums = len(role_data['chunks_with_dialogues'])
        sum_dialogues_turn = 0
        name = role_data['姓名'] if '姓名' in role_data else role_data['name']
        
        names = role_data['names'] if 'names' in role_data else [name]
        for index, dialogue in enumerate(role_data['chunks_with_dialogues']):
            if type(dialogue.get('dialogues', [])) == str:
                result = process_trush(dialogue['dialogues'])
                if type(result) == str:
                    trunsh_record[file] = dialogue
                    dialogue_len = len(result.split('\n'))
                else:
                    print('file:', file, 'index:', index, 'dialogue:', dialogue['dialogues'])
                    result = process_dialog_names(name, names, result)
                    role_data['chunks_with_dialogues'][index]['dialogues'] = result
                    dialogue_len = len(result)
                    with open(file, 'w') as f:
                        json.dump(role_data, f, indent=4, ensure_ascii=False)
            else:
                dialogue_len = len(dialogue.get('dialogues', []))
            sum_dialogues_turn += dialogue_len // 2
            turns_count[dialogue_len // 2] = turns_count.get(dialogue_len // 2, 0) + 1
        statis[file] = {
            'sum_dialogue_turns': sum_dialogues_turn,
            'ave_dialogue_turns': round(sum_dialogues_turn / dialogue_nums, 2) if dialogue_nums > 0 else 0
        }
        statis['all_dialogue_turns'] += sum_dialogues_turn
        statis['all_dialogue_nums'] += dialogue_nums
    statis['ave_dialogue_turns'] = round(statis['all_dialogue_turns'] / statis['all_dialogue_nums'], 2)
    
    with open(os.path.join(f'./{dir_name}.json'), 'w') as f:
        json.dump(statis, f, indent=4, ensure_ascii=False)
    if trunsh_record:
        with open(os.path.join(f'./{dir_name}_trush.json'), 'w') as f:
            json.dump(trunsh_record, f, indent=4, ensure_ascii=False)
    draw_turns_count(turns_count, f'{dir_name}')

def coherence_statis():
    dialogue_path = '../../NovelData/AB_dialogues'
    files = glob.glob(os.path.join(dialogue_path, '*/*.json'))
    statis = {'all_dialogue_nums': 0, 'all_dialogue_turns': 0, 'ave_dialogue_turns': 0}
    turns_count = {}
    trunsh_data = []
    for file in files:
        role_data = json.load(open(file, 'r'))
        dialogue_nums = 0
        sum_dialogues_turn = 0
        for index, dialogue in enumerate(role_data['chunks_with_dialogues']):
            if dialogue['coherence'] == 0:
                trunsh_data.append({'sub_scene': dialogue['sub_scene'], 'dialogues': process_dialogues(dialogue['dialogues']), 'coherence': dialogue['coherence']})
                continue
            if dialogue['coherence'] not in {0, 1}:
                raise ValueError('coherence is -1 in file:', file, 'index:', index)
            dialogue_len = len(dialogue.get('dialogues', []))
            dialogue_nums += 1
            sum_dialogues_turn += dialogue_len // 2
            turns_count[dialogue_len // 2] = turns_count.get(dialogue_len // 2, 0) + 1
        statis[file] = {
            'sum_dialogue_turns': sum_dialogues_turn,
            'ave_dialogue_turns': round(sum_dialogues_turn / dialogue_nums, 2) if dialogue_nums > 0 else 0
        }
        statis['all_dialogue_turns'] += sum_dialogues_turn
        statis['all_dialogue_nums'] += dialogue_nums
    statis['ave_dialogue_turns'] = round(statis['all_dialogue_turns'] / statis['all_dialogue_nums'], 2)

    with open(os.path.join('./AB_coherence_1_dialogue_statis.json'), 'w') as f:
        json.dump(statis, f, indent=4, ensure_ascii=False)
    
    draw_turns_count(turns_count, 'AB_coherence_1_dialogue_statis')


if __name__ == '__main__':
    dialogue_statis()