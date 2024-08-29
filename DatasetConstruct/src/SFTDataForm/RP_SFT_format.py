import json
from typing import Dict, List

from tqdm import tqdm
from utils import collect_roles, construct_emotion


def construct_SFT_Data(name: str, sys_prompt: str, scene: str, emotion_scale_scores: Dict[str, int], relationship: int, dialogues: List[Dict[str, str]]):
    chat_role = dialogues[0]['role']
    system_prompt = sys_prompt.format(role_name=name, scene=scene, emotion=construct_emotion(emotion_scale_scores), chat_role=chat_role, relationship=relationship)
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
                "system": system_prompt,
                "history": history.copy()
            }
            history.append([instruction, d['dialogue']])
            train_data.append(json_data)
    return train_data[-1]
                
def main():
    role_root_path = '../../NovelData/AB_dialogues_top10len'
    save_path = '../../SFTData/RP_SFT.json'
    dialogues_files = collect_roles(role_root_path)
    all_train_data = []
    for file in tqdm(dialogues_files):
        with open(file, 'r') as f:
            role_data = json.load(f)
        name = role_data['name']
        sys_prompt = role_data['sys_prompt']
        for chunk_with_dialogues in role_data['chunks_with_dialogues']:
            emotion_scale_scores = chunk_with_dialogues['emotion_scale_scores']
            relationship = chunk_with_dialogues['relationship']
            dialogues = chunk_with_dialogues['dialogues']
            scene = chunk_with_dialogues['sub_scene']
            train_data = construct_SFT_Data(name, sys_prompt, scene, emotion_scale_scores, relationship, dialogues)
            all_train_data.append(train_data)
    with open(save_path, 'w', encoding='utf-8') as f:
            # Manually create JSON string with newlines after each element
            json_string = "[" + ",\n".join(json.dumps(item, ensure_ascii=False) for item in all_train_data) + "]"
            f.write(json_string)
        

# python -m SFTDataForm.RP_SFT_format
if __name__ == "__main__":
    main()