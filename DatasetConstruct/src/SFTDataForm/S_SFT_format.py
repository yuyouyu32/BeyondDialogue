import json
from typing import Dict, List

from tqdm import tqdm
from utils import collect_roles, construct_str_dialogue, generate_MBTI_str, generate_MBTI_str_en
# from DerivedTask.prompts import StyleClsPrompt
from DerivedTask.prompts_en import StyleClsPrompt


def construct_S_SFT_data(name: str, scene: str, character, MBTI, style, dialogues: List[Dict[str, str]], style_analysis: str):
    system_prompt = "You are a helpful assistant."
    dialogues = construct_str_dialogue(dialogues)
    # style_candidates = style.split("、")
    character = character.lower().replace('，', ',').replace(",", ", ")
    style = style.lower().replace('，', ',').replace(",", ", ")
    instruction = StyleClsPrompt.format(role_name=name, character=character, dialogues=dialogues, scene=scene, MBTI=MBTI, style_candidates=style)
    output = style_analysis.replace('```json', '').replace('```', '')
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
    # save_path = '../../SFTData/Style_SFT.json'
    role_root_path = '../../NovelData/AB_dialogues_EN'
    save_path = '../../SFTData/Style_EN_SFT.json'
    dialogues_files = collect_roles(role_root_path)
    P_SFT_data = []
    for file in tqdm(dialogues_files):
        with open(file, 'r') as f:
            role_data = json.load(f)
        name = role_data['name']
        for chunk_with_dialogues in role_data['chunks_with_dialogues']:
            dialogues = chunk_with_dialogues['dialogues']
            scene = chunk_with_dialogues['sub_scene']
            character = role_data['character']
            # MBTI = generate_MBTI_str(role_data['personality'])
            MBTI = generate_MBTI_str_en(role_data['personality'])
            style = role_data['style']
            style_eval = chunk_with_dialogues['style_eval']
            style_analysis = chunk_with_dialogues['style_analysis']
            train_data = construct_S_SFT_data(name, scene, character, MBTI, style, dialogues, style_analysis)
            P_SFT_data.append(train_data)
    with open(save_path, 'w', encoding='utf-8') as f:
        # Manually create JSON string with newlines after each element
        json_string = "[" + ",\n".join(json.dumps(item, ensure_ascii=False) for item in P_SFT_data) + "]"
        f.write(json_string)
        

# python -m SFTDataForm.S_SFT_format
if __name__ == "__main__":
    main()