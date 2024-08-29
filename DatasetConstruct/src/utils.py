import glob
import json
import os
import time
from typing import List, Dict
import pandas as pd

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

def collect_novels(novel_root_path: str) -> List[str]:
    """
    Collect the paths of all the novels in the given directory.

    Parameters:
        novel_root_path: a string, the path of the directory containing the novels.
    Return:
        a list of strings, the paths of the novels chunks.
    """
    if not os.path.exists(novel_root_path):
        return []
    return glob.glob(os.path.join(novel_root_path, '**', '*.jsonl'), recursive=True)    


def collect_roles(role_root_path: str) -> List[str]:
    """
    Collect the paths of all the roles in the given directory.
    
    Parameters:
        role_root_path: a string, the path of the directory containing the roles.
        
    Return:
        a list of strings, the paths of the roles.
    """
    if not os.path.exists(role_root_path):
        return []
    return glob.glob(os.path.join(role_root_path, '**', '*.json'), recursive=True)

def get_novel_chunks_dict(novel_files_path):
    """
    Get the dictionary of novel chunks.
    
    Parameters:
        novel_files_path: a string, the path of the directory containing the novel chunks.
    
    Return:
        a dictionary, the dictionary of novel chunks.
        {
            novel_name: {
                chunk_id: {
                    'id': chunk_id,
                    'chap_id': chapter_id,
                    'chunk': chunk_text,
                    'scene': scene_text
                },
                ...
            },
            ...
        }
    """
    novel_files = collect_novels(novel_files_path)
    novel_chunks = {}
    for file in novel_files:
        novel_name = file.split('/')[-1].split('.')[0].split('_')[0]
        novel_chunks[novel_name] = {}
        for  line in open(file):
            chunk = json.loads(line)
            novel_chunks[novel_name][chunk['id']] = chunk
    return novel_chunks


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

def construct_emotion(emotion_scale_scores: Dict[str, int]):
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

def construct_emotion_en(emotion_scale_scores: Dict[str, int]):
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

def get_charcater_candidates(df: pd.DataFrame):
    """
    Get the character candidates from the given data path.
    
    Parameters:
        data_path: a string, the path of the data.
        
    Return:
        a set of strings, the character candidates.
    """
    df['character'] = df['character'].str.replace(',', '，')
    df['character'] = df['character'].str.replace('、', '，')
    # Create a new total set
    total_set_corrected = set()
    df['character'].apply(lambda x: total_set_corrected.update(x.split('，')))

    return total_set_corrected


def get_style_candidates(df: pd.DataFrame):
    """
    Get the style candidates from the given data path.
    
    Parameters:
        data_path: a string, the path of the data.
        
    Return:
        a set of strings, the style candidates.
    """
    df['style'] = df['style'].str.replace(',', '，')
    df['style'] = df['style'].str.replace('、', '，')
    # Create a new total set
    total_set_corrected = set()
    df['style'].apply(lambda x: total_set_corrected.update(x.split('，')))
    
    return total_set_corrected 

def get_candidates_c_s(data_path: str):
    df = pd.read_excel(data_path)
    return get_charcater_candidates(df), get_style_candidates(df)
    
def construct_str_dialogue(dialogues):
    return '\n'.join([f"{d['role']}: {d['dialogue']}" for d in dialogues])    

def unit_test():
    data_path = "../../DialogueGenerate/data/Roles Info.xlsx"
    c, s = get_candidates_c_s(data_path)
    print(c)
    print('\n')
    print(s)

# python -m utils
if __name__ == '__main__':
    unit_test()
    print('Done!') # 'Done!
        