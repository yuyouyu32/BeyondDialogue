import json
from typing import Dict, List

from tqdm import tqdm
from utils import collect_roles, construct_str_dialogue, generate_MBTI_str, generate_MBTI_str_en
# from DerivedTask.prompts import RelationshipPrompt
from DerivedTask.prompts_en import RelationshipPrompt


def construct_R_SFT_Data(name: str, scene: str, character, MBTI, style, dialogues: List[Dict[str, str]], relationship_analysis: str):
    system_prompt = "You are a helpful assistant."
    chat_role = dialogues[0]['role']
    character = character.lower().replace('，', ',').replace(",", ", ")
    style = style.lower().replace('，', ',').replace(",", ", ")
    instruction = RelationshipPrompt.format(role_name=name, scene=scene, dialogues=construct_str_dialogue(dialogues), character=character, MBTI=MBTI, style=style, target_name=chat_role)
    output = relationship_analysis.replace('```json', '').replace('```', '')
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
    # save_path = '../../SFTData/Relationship_SFT.json'
    role_root_path = '../../NovelData/AB_dialogues_EN'
    save_path = '../../SFTData/Relationship_EN_SFT.json'
    dialogues_files = collect_roles(role_root_path)
    R_SFT_data = []
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
            relationship = chunk_with_dialogues['relationship']
            relationship_analysis = chunk_with_dialogues['relationship_analysis']
            train_data = construct_R_SFT_Data(name, scene, character, MBTI, style, dialogues, relationship_analysis)
            R_SFT_data.append((relationship, train_data))
    R_SFT_data.sort(key=lambda x: x[0])
    with open(save_path, 'w', encoding='utf-8') as f:
        # Manually create JSON string with newlines after each element
        json_string = "[" + ",\n".join(json.dumps(item[1], ensure_ascii=False) for item in R_SFT_data) + "]"
        f.write(json_string)
        

# python -m SFTDataForm.R_SFT_format
if __name__ == "__main__":
    main()