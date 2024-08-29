import glob
import json
import os
import time

MBTIMAP = {
    "I": "内向型（I）",
    "E": "外向型（E）",
    "N": "直觉型（N）",
    "S": "实感型（S）",
    "T": "思维型（T）",
    "F": "情感型（F）",
    "J": "判断型（J）",
    "P": "感知型（P）"
}

MBTIMAP_EN = {
    "I": "Introverted (I)",
    "E": "Extraverted (E)",
    "N": "Intuitive (N)",
    "S": "Sensing (S)",
    "T": "Thinking (T)",
    "F": "Feeling (F)",
    "J": "Judging (J)",
    "P": "Perceiving (P)"
}

def collect_roles(base_path):
    roles = {}
    for file in glob.glob(os.path.join(base_path, "*.json")):
        with open(file, "r") as f:
            data = json.load(f)
            roles[data['name']] = data
    return roles

def retry_on_failure(retries):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except ValueError as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    attempt += 1
                    time.sleep(3)
            raise ValueError("Max retries exceeded")
        return wrapper
    return decorator

def generate_MBTI_str(MBTI):
    assert len(MBTI) == 4
    MBTIs = []
    for i in range(4):
        MBTIs.append(MBTIMAP[MBTI[i]])
    return '、'.join(MBTIs)

def generate_MBTI_str_en(MBTI):
    """
    Generate the MBTI string from the MBTI list.
    
    Parameters:
        MBTI: a list of 4 characters, the MBTI list.
        "INTJ"
    Return:
        a string, the MBTI string.
    """
    assert len(MBTI) == 4
    MBTIs = []
    for i in range(4):
        MBTIs.append(MBTIMAP_EN[MBTI[i]])
    return ', '.join(MBTIs)


def construct_emotion(emotion_scale_scores):
    """
    Construct the emotion from the emotion scale scores.
    
    Parameters:
        emotion_scale_scores: a dictionary, the emotion scale scores.
        "emotion_scale_scores": {
                "快乐": 0,
                "悲伤": 1,
                "厌恶": 6,
                "恐惧": 2,
                "惊讶": 1,
                "愤怒": 8
            }
    Return:
        a string, the emotion constructed from the emotion scale scores.
    """
    return f"""快乐: {emotion_scale_scores['快乐']}, 悲伤: {emotion_scale_scores['悲伤']}, 厌恶: {emotion_scale_scores['厌恶']}, 恐惧: {emotion_scale_scores['恐惧']}, 惊讶: {emotion_scale_scores['惊讶']}, 愤怒: {emotion_scale_scores['愤怒']}"""

def construct_emotion_en(emotion_scale_scores):
    """
    Construct the emotion from the emotion scale scores.
    
    Parameters:
        emotion_scale_scores: a dictionary, the emotion scale scores.
        "emotion_scale_scores": {
                "happiness": 3,
                "sadness": 5,
                "disgust": 4,
                "fear": 6,
                "surprise": 2,
                "anger": 5
            },
    Return:
        a string, the emotion constructed from the emotion scale scores.
    """
    return f"""happiness: {emotion_scale_scores['happiness']}, sadness: {emotion_scale_scores['sadness']}, disgust: {emotion_scale_scores['disgust']}, fear: {emotion_scale_scores['fear']}, surprise: {emotion_scale_scores['surprise']}, anger: {emotion_scale_scores['anger']}"""

def construct_str_dialogue(dialogues):
    return '\n'.join([f"{d['role']}: {d['dialogue']}" for d in dialogues])

def construct_masked_dialogue(dialogues):
    masked_dialogues = []
    role_name = dialogues[1]['role']
    chat_role_name = dialogues[0]['role']
    for index, d in enumerate(dialogues):
        dialogue = d['dialogue']
        masked_dialogue = dialogue.replace(role_name, '[角色]')
        if len(role_name) > 2:
            masked_dialogue = masked_dialogue.replace(role_name[-2:], '[角色]')
        if index % 2 == 0:
            masked_dialogues.append(f"{chat_role_name}: {masked_dialogue}")
        else:
            masked_dialogues.append(f"[角色]: {masked_dialogue}")
    return '\n'.join(masked_dialogues)


def construct_masked_dialogue_en(dialogues):
    masked_dialogues = []
    role_name = dialogues[1]['role']
    chat_role_name = dialogues[0]['role']
    split_names = role_name.split(' ')
    for index, d in enumerate(dialogues):
        dialogue = d['dialogue']
        masked_dialogue = dialogue.replace(role_name, '[Role]]')
        if len(split_names) > 2:
            masked_dialogue = masked_dialogue.replace(split_names[1], '[Role]')
        if index % 2 == 0:
            masked_dialogues.append(f"{chat_role_name}: {masked_dialogue}")
        else:
            masked_dialogues.append(f"[Role]: {masked_dialogue}")
    return '\n'.join(masked_dialogues)

def construct_masked_scene(scene, role_name):
    masked_scene = scene.replace(role_name, '[角色]')
    if len(role_name) > 2:
        masked_scene = masked_scene.replace(role_name[-2:], '[角色]')
    return masked_scene

def construct_masked_scene_en(scene, role_name):
    masked_scene = scene.replace(role_name, '[Role]')
    split_names = role_name.split(' ')
    if len(split_names) > 2:
        masked_scene = masked_scene.replace(split_names[1], '[Role]')
    return masked_scene