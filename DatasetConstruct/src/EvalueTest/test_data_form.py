import json
import random
from typing import Dict, List

from DerivedTask.prompts import (CharacterClsPrompt, EmotionPrompt,
                                 PersonalityClsPrompt, RelationshipPrompt,
                                 StyleClsPrompt)
from DerivedTask.prompts_en import CharacterClsPrompt as CharacterClsPrompt_en
from DerivedTask.prompts_en import EmotionPrompt as EmotionPrompt_en
from DerivedTask.prompts_en import \
    PersonalityClsPrompt as PersonalityClsPrompt_en
from DerivedTask.prompts_en import RelationshipPrompt as RelationshipPrompt_en
from DerivedTask.prompts_en import StyleClsPrompt as StyleClsPrompt_en
from tqdm import tqdm
from utils import (collect_roles, construct_str_dialogue, generate_MBTI_str,
                   generate_MBTI_str_en)

random.seed(21)


def get_derived_task_data(role_files, language: str = 'cn'):
    C_Test, S_Test, E_Test, R_Test, P_Test = [], [], [], [], []
    for file in tqdm(role_files):
        with open(file, 'r') as f:
            role_data = json.load(f)
        name = role_data['name']
        character_candidates = role_data['character'].lower().replace(",", "，").split("，")
        style_candidates = role_data['style'].lower().replace("、", "，").replace(",", "，").split("，")
        for chat_role, chat_data in role_data["chats"].items():
            character_A = chat_data["character_eval"]
            style_A = chat_data["style_eval"]
            emotion_A = chat_data["emotion_eval"]
            relationship_A = chat_data["relationship_eval"]
            personality_A = chat_data["personality_eval"]
            dialogues = construct_str_dialogue(chat_data["dialogues"])
            scene = chat_data["scene"]
            style = role_data['style']
            if language == 'cn':
                MBTI = generate_MBTI_str(role_data['personality'])
                character_Q = CharacterClsPrompt.format(role_name=name, style=style, dialogues=dialogues, scene=scene, MBTI=MBTI, character_candidates=", ".join(character_candidates))
                style_Q = StyleClsPrompt.format(role_name=name, style=style, dialogues=dialogues, scene=scene, MBTI=MBTI, style_candidates=", ".join(style_candidates))
                emotion_Q = EmotionPrompt.format(role_name=name, character=character_A, MBTI=MBTI, style=style_A, scene=scene, dialogues=dialogues)
                relationship_Q = RelationshipPrompt.format(role_name=name, character=character_A, MBTI=MBTI, style=style_A, scene=scene, dialogues=dialogues, target_name=chat_role)
                personality_Q = PersonalityClsPrompt.format(role_name=name, character=character_A, MBTI=MBTI, style=style_A, scene=scene, dialogues=dialogues)
            elif language == 'en':
                MBTI = generate_MBTI_str_en(role_data['personality'])
                character_Q = CharacterClsPrompt_en.format(role_name=name, style=style, dialogues=dialogues, scene=scene, MBTI=MBTI, character_candidates=", ".join(character_candidates))
                style_Q = StyleClsPrompt_en.format(role_name=name, style=style, dialogues=dialogues, scene=scene, MBTI=MBTI, style_candidates=", ".join(style_candidates))
                emotion_Q = EmotionPrompt_en.format(role_name=name, character=character_A, MBTI=MBTI, style=style_A, scene=scene, dialogues=dialogues)
                relationship_Q = RelationshipPrompt_en.format(role_name=name, character=character_A, MBTI=MBTI, style=style_A, scene=scene, dialogues=dialogues, target_name=chat_role)
                personality_Q = PersonalityClsPrompt_en.format(role_name=name, character=character_A, MBTI=MBTI, style=style_A, scene=scene, dialogues=dialogues)
            C_Test.append({"Q": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": character_Q}
            ], 
            "A": character_A,
            "type": "character",
            "language": language})
            S_Test.append({"Q": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": style_Q}], 
            "A": style_A,
            "type": "style",
            "language": language})
            E_Test.append({"Q": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": emotion_Q}
            ], "A": emotion_A,
                           "type": "emotion",
                           "language": language})
            R_Test.append({"Q": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": relationship_Q}
            ], "A": relationship_A,
                           "type": "relationship",
                           "language": language})
            P_Test.append({"Q": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": personality_Q}
            ], "A": personality_A,
                           "type": "personality",
                           "language": language})
    return C_Test, S_Test, E_Test, R_Test, P_Test
                 
def main():
    chat_root_path = '../../AutoRPTest/chat_dialogues'
    chat_en_root_path = "../../AutoRPTest/chat_dialogues_en"
    save_path = '../data/CESRP_test.json'
    role_files = collect_roles(chat_root_path)
    role_files_en = collect_roles(chat_en_root_path)
    C_Test, S_Test, E_Test, R_Test, P_Test = get_derived_task_data(role_files, language='cn')
    C_Test_en, S_Test_en, E_Test_en, R_Test_en, P_Test_en = get_derived_task_data(role_files_en, language='en')
    print(len(C_Test), len(S_Test), len(E_Test), len(R_Test), len(P_Test))
    print(len(C_Test_en), len(S_Test_en), len(E_Test_en), len(R_Test_en), len(P_Test_en))
    # random sample 75 indexs from 0 to len(C_Test)
    indexs = random.sample(range(len(C_Test)), 75)
    # random sample 25 indexs from 0 to len(C_Test_en)
    indexs_en = random.sample(range(len(C_Test_en)), 25)
    # sample data from C_Test, S_Test, E_Test, R_Test, P_Test
    C_Test_sample = [C_Test[i] for i in indexs]
    S_Test_sample = [S_Test[i] for i in indexs]
    E_Test_sample = [E_Test[i] for i in indexs]
    R_Test_sample = [R_Test[i] for i in indexs]
    P_Test_sample = [P_Test[i] for i in indexs]
    # sample data from C_Test_en, S_Test_en, E_Test_en, R_Test_en, P_Test_en
    C_Test_en_sample = [C_Test_en[i] for i in indexs_en]
    S_Test_en_sample = [S_Test_en[i] for i in indexs_en]
    E_Test_en_sample = [E_Test_en[i] for i in indexs_en]
    R_Test_en_sample = [R_Test_en[i] for i in indexs_en]
    P_Test_en_sample = [P_Test_en[i] for i in indexs_en]
    # merge all samples in one list
    C_Test_sample.extend(C_Test_en_sample)
    S_Test_sample.extend(S_Test_en_sample)
    E_Test_sample.extend(E_Test_en_sample)
    R_Test_sample.extend(R_Test_en_sample)
    P_Test_sample.extend(P_Test_en_sample)
    all_samples = C_Test_sample + S_Test_sample + E_Test_sample + R_Test_sample + P_Test_sample
    
    with open(save_path, 'w', encoding='utf-8') as f:
        # Manually create JSON string with newlines after each element
        json_string = "[" + ",\n".join(json.dumps(item, ensure_ascii=False) for item in all_samples) + "]"
        f.write(json_string)
        

# python -m EvalueTest.test_data_form
if __name__ == "__main__":
    main()