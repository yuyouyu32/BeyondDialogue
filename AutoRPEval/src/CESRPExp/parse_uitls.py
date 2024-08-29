import re
import ast
from typing import List, Dict
from utils import MBTIMAP

def extrct_characters(rsp: str, character_candidates: List[str]) -> Dict[str, int]:
    matches = re.findall(r"{[^}]*}", rsp, re.DOTALL)
    if not matches:
        raise ValueError("Invalid response format in re.findall")
    try:
        json_rsp = ast.literal_eval(matches[-1])
    except:
        raise ValueError("Invalid response format in ast.literal_eval")
    if 'character' not in json_rsp:
        raise ValueError("Invalid response format in 'character' not in json_rsp")
    if type(json_rsp['character']) != str:
        raise ValueError("Invalid response format in type(json_rsp['character']) != str")

    characters = json_rsp['character'].lower().replace('，', ',').split(",")
    character_result = []
    for character in characters:
        character = character.strip()
        if character not in character_candidates:
            continue
            # raise ValueError(f"Invalid {character} ({characters}) in {character_candidates}".replace("'", "\""))
        else:
            character_result.append(character)
    return character_result

def extrct_styles(rsp: str, style_candidates) -> Dict[str, int]:
    matches = re.findall(r"{[^}]*}", rsp, re.DOTALL)
    if not matches:
        raise ValueError("Invalid response format in re.findall")
    try:
        json_rsp = ast.literal_eval(matches[-1])
    except:
        raise ValueError("Invalid response format in ast.literal_eval")
    if 'style' not in json_rsp:
        raise ValueError("Invalid response format in 'style' not in json_rsp")
    if type(json_rsp['style']) != str:
        raise ValueError("Invalid response format in type(json_rsp['style']) != str")

    styles = json_rsp['style'].lower().replace('，', ',').split(",")
    styles_result = []
    for style in styles:
        style = style.strip()
        if style not in style_candidates:
            continue
            # raise ValueError(f"Invalid {style} ({styles}) in {style_candidates}".replace("'", "\""))
        else:
            styles_result.append(style)
    return styles_result

def extrct_emotions(rsp: str, language) -> Dict[str, int]:
    matches = re.findall(r"{[^}]*}", rsp, re.DOTALL)
    if not matches:
        raise ValueError("Invalid response format in re.findall")
    try:
        json_rsp = ast.literal_eval(matches[-1])
    except:
        raise ValueError("Invalid response format in ast.literal_eval")
    emotions_scale_scores = {}
    if language == 'cn':
        valid_keys = ['快乐', '悲伤', '厌恶', '恐惧', '惊讶', '愤怒']
    elif language == 'en':
        valid_keys = ['happiness', 'sadness', 'disgust', 'fear', 'surprise', 'anger']
    for key in json_rsp.keys():
        if key in valid_keys:
            try:
                emotions_scale_scores[key] = int(json_rsp[key])
            except:
                raise ValueError("Invalid response format in int(json_rsp[key])")
    if len(emotions_scale_scores) != 6:
        raise ValueError("Invalid response format in len(emotions_scale_scores) != 6")
    return emotions_scale_scores

def extrct_relationship(rsp: str, language) -> Dict[str, int]:
    matches = re.findall(r"{[^}]*}", rsp, re.DOTALL)
    if not matches:
        raise ValueError("Invalid response format in re.findall")
    rsp = matches[-1]
    try:
        json_rsp = ast.literal_eval(rsp)
    except:
        raise ValueError("Invalid response format in ast.literal_eval")
    if 'relationship' not in json_rsp:
        raise ValueError("Invalid response format in 'relationship' not in json_rsp")
    else:
        try:
            return float(json_rsp['relationship'])
        except:
            raise ValueError("Invalid response format in int(json_rsp['relationship'])")

def extrct_personalitys(rsp: str, language) -> Dict[str, int]:
    matches = re.findall(r"{[^}]*}", rsp, re.DOTALL)
    if not matches:
        raise ValueError("Invalid response format in re.findall")
    try:
        json_rsp = ast.literal_eval(matches[-1])
    except:
        raise ValueError("Invalid response format in ast.literal_eval")
    if 'personality' not in json_rsp:
        raise ValueError("Invalid response format in 'personality' not in json_rsp")
    if type(json_rsp['personality']) != str:
        raise ValueError("Invalid response format in type(json_rsp['personality']) != str")
    json_rsp['personality'] = json_rsp['personality'].strip()
    for index, c in enumerate(json_rsp['personality']):
        if c not in list(MBTIMAP.keys())[index * 2: index * 2 + 2]:
            raise ValueError(f"Invalid response format in {c} not in MBTI_MAP")
    return json_rsp['personality']


ExtractFuncs = {
    "character": extrct_characters,
    "style": extrct_styles,
    "emotion": extrct_emotions,
    "relationship": extrct_relationship,
    "personality": extrct_personalitys
}