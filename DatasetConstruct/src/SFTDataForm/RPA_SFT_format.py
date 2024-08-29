import json
from typing import Dict, List

from tqdm import tqdm
from utils import collect_roles, construct_emotion, generate_MBTI_str, construct_emotion_en, generate_MBTI_str_en
from SFTDataForm.prompts import SystemPromptTemplate
from SFTDataForm.prompts import SystemPromptTemplateEN


def construct_SFT_Data(name: str, sys_prompt: str, dialogues: List[Dict[str, str]]):
    train_data = []
    history = []
    for d in dialogues:
        if d['role'] != name:
                instruction = d['dialogue']
        else:
            json_data = {
                "instruction": instruction,
                "input": "",
                "output": d['dialogue'],
                "system": sys_prompt,
                "history": history.copy()
            }
            history.append([instruction, d['dialogue']])
            train_data.append(json_data)
    return train_data[-1]
                
def main():
    # role_root_path = '../../NovelData/AB_dialogues_top10len'
    # save_path = '../../SFTData/RPA_SFT.json'
    # notA_save_path = '../../SFTData/RP_SFT.json'
    role_root_path = '../../NovelData/AB_dialogues_EN'
    save_path = '../../SFTData/RPA_EN_SFT.json'
    notA_save_path = '../../SFTData/RP_EN_SFT.json'
    dialogues_files = collect_roles(role_root_path)
    all_align_train_data = []
    all_train_data = []
    for file in tqdm(dialogues_files):
        with open(file, 'r') as f:
            role_data = json.load(f)
        name = role_data['name']
        world = role_data['world']
        # original_character = role_data['character']
        # original_style = role_data['style']
        # original_personality = generate_MBTI_str(role_data['personality'])
        original_character = role_data['character'].lower().replace(",", ", ")
        original_style = role_data['style'].lower().replace(",", ", ")
        original_personality = generate_MBTI_str_en(role_data['personality'])
        for chunk_with_dialogues in role_data['chunks_with_dialogues']:
            emotion_scale_scores = chunk_with_dialogues['emotion_scale_scores']
            relationship = chunk_with_dialogues['relationship']
            dialogues = chunk_with_dialogues['dialogues']
            scene = chunk_with_dialogues['sub_scene']
            # character = '，'.join(chunk_with_dialogues['character_eval'])
            # style = '，'.join(chunk_with_dialogues['style_eval'])
            # personality = generate_MBTI_str(chunk_with_dialogues['personality_eval'])
            character = ', '.join(chunk_with_dialogues['character_eval']).lower()
            style = ', '.join(chunk_with_dialogues['style_eval']).lower()
            personality = generate_MBTI_str_en(chunk_with_dialogues['personality_eval']).upper()
            chat_role = dialogues[0]['role']
            # sys_prompt_align = SystemPromptTemplate.format(role_name=name, character=character, personality=personality, style=style, world=world, scene=scene, emotion=construct_emotion(emotion_scale_scores), chat_role=chat_role, relationship=relationship)
            # system_prompt_not_align = SystemPromptTemplate.format(role_name=name, character=original_character, personality=original_personality, style=original_style, world=world, scene=scene, emotion=construct_emotion(emotion_scale_scores), chat_role=chat_role, relationship=relationship)
            sys_prompt_align = SystemPromptTemplateEN.format(role_name=name, character=character, personality=personality, style=style, world=world, scene=scene, emotion=construct_emotion_en(emotion_scale_scores), chat_role=chat_role, relationship=relationship)
            system_prompt_not_align = SystemPromptTemplateEN.format(role_name=name, character=original_character, personality=original_personality, style=original_style, world=world, scene=scene, emotion=construct_emotion_en(emotion_scale_scores), chat_role=chat_role, relationship=relationship)
            train_data = construct_SFT_Data(name, sys_prompt_align, dialogues)
            train_data_not_align = construct_SFT_Data(name, system_prompt_not_align, dialogues)
            all_align_train_data.append(train_data)
            all_train_data.append(train_data_not_align)
    with open(save_path, 'w', encoding='utf-8') as f:
            # Manually create JSON string with newlines after each element
            json_string = "[" + ",\n".join(json.dumps(item, ensure_ascii=False) for item in all_align_train_data) + "]"
            f.write(json_string)
    with open(notA_save_path, 'w', encoding='utf-8') as f:
            # Manually create JSON string with newlines after each element
            json_string = "[" + ",\n".join(json.dumps(item, ensure_ascii=False) for item in all_train_data) + "]"
            f.write(json_string)
        

# python -m SFTDataForm.RPA_SFT_format
if __name__ == "__main__":
    main()