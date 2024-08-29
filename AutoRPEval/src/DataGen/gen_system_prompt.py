language = "en"
import json

import tqdm

if language == "cn":
    from DataGen.prompts import SystemPromptTemplate
elif language == "en":
    from DataGen.prompts_en import SystemPromptTemplate
else:
    raise ValueError("Invalid language")
from utils import (collect_roles, construct_emotion, construct_emotion_en,
                   generate_MBTI_str, generate_MBTI_str_en)


def system_prompt_formater(role_name, character, MBTI, style, world):
    if language == 'cn':
        MBTI = generate_MBTI_str(MBTI)
    elif language == 'en':
        MBTI = generate_MBTI_str_en(MBTI)
        character = character.lower().replace(",", ", ")
        style = style.lower().replace(",", ", ")
    system_prompt = SystemPromptTemplate.format(role_name=role_name, character=character, personality=MBTI, style=style, world=world)
    return system_prompt
    
def main():
    if language == "cn":
        roles = collect_roles('../data/roles')
    else:
        roles = collect_roles('../data/roles_en')
    for role, role_data in tqdm.tqdm(roles.items(), desc="Generating system prompts"):
        system_prompt = system_prompt_formater(role, role_data["character"], role_data["personality"], role_data["style"], role_data["world"])
        role_data["sys_prompt"] = system_prompt
        if 'chats' in role_data:
            chats = role_data.pop('chats')
            role_data['chats'] = chats
        if language == "cn":
            json.dump(role_data, open(f'../data/roles/{role}.json', 'w'), ensure_ascii=False, indent=4)
        elif language == "en":
            json.dump(role_data, open(f'../data/roles_en/{role}.json', 'w'), ensure_ascii=False, indent=4)

# python -m DataGen.gen_system_prompt
if __name__ == "__main__":
    main()
            