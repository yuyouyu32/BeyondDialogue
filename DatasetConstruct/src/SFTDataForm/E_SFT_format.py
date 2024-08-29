import json
from typing import Dict, List

from tqdm import tqdm
from utils import collect_roles, construct_str_dialogue, generate_MBTI_str, generate_MBTI_str_en
# from DerivedTask.prompts import EmotionPrompt
from DerivedTask.prompts_en import EmotionPrompt


def construct_E_SFT_Data(name: str, scene: str, character, MBTI, style, dialogues: List[Dict[str, str]], emotion_analysis: str):
    system_prompt = "You are a helpful assistant."
    character = character.lower().replace('，', ',').replace(",", ", ")
    style = style.lower().replace('，', ',').replace(",", ", ")
    instruction = EmotionPrompt.format(role_name=name, scene=scene, dialogues=construct_str_dialogue(dialogues), character=character, MBTI=MBTI, style=style)
    output = emotion_analysis.replace('```json', '').replace('```', '')
    json_data = {
        "instruction": instruction,
        "input": "",
        "output": output,
        "system": system_prompt,
        "history": []
    }
    return json_data
            
                
def main():
    # role_root_path = '../../NovelData/AB_dialogues_top10len'
    # save_path = '../../SFTData/Emotion_SFT.json'
    role_root_path = '../../NovelData/AB_dialogues_EN'
    save_path = '../../SFTData/Emotion_EN_SFT.json'
    dialogues_files = collect_roles(role_root_path)
    E_SFT_data = []
    for file in tqdm(dialogues_files):
        with open(file, 'r') as f:
            role_data = json.load(f)
        name = role_data['name']
        for chunk_with_dialogues in role_data['chunks_with_dialogues']:
            dialogues = chunk_with_dialogues['dialogues']
            scene = chunk_with_dialogues['sub_scene']
            emotion_analysis = chunk_with_dialogues['emotion_analysis']
            character = role_data['character']
            # MBTI = generate_MBTI_str(role_data['personality'])
            MBTI = generate_MBTI_str_en(role_data['personality'])
            style = role_data['style']
            emotion_scale_scores_sum = sum(chunk_with_dialogues['emotion_scale_scores'].values())
            train_data = construct_E_SFT_Data(name, scene, character, MBTI, style, dialogues, emotion_analysis)
            E_SFT_data.append((emotion_scale_scores_sum, train_data))
    E_SFT_data.sort(key=lambda x: x[0])
    with open(save_path, 'w', encoding='utf-8') as f:
        # Manually create JSON string with newlines after each element
        json_string = "[" + ",\n".join(json.dumps(item[1], ensure_ascii=False) for item in E_SFT_data) + "]"
        f.write(json_string)

# python -m SFTDataForm.E_SFT_format
if __name__ == "__main__":
    main()