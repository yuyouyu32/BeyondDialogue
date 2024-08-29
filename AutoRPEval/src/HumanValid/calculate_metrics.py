import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine

def cosine_similarity(row_A, row_B):
    return 1 - cosine(row_A, row_B)

def calculate_global_cosine_similarity(A: np.ndarray, B: np.ndarray):
    if A.ndim == 1:
        A = A.reshape(1, -1)
    if B.ndim == 1:
        B = B.reshape(1, -1)
    if A.shape != B.shape:
        raise ValueError("The matrices must have the same shape.")
    similarity_scores = []
    
    for row_A, row_B in zip(A, B):
        similarity = cosine_similarity(row_A, row_B)
        similarity_scores.append(similarity)
    
    global_cosine_similarity = np.mean(similarity_scores)
    sem = np.std(similarity_scores) / np.sqrt(len(similarity_scores))
    
    return global_cosine_similarity, sem

def converts_emb_c_s(label, pred):
    if not all(p in label for p in pred):
        print('、'.join(label), '、'.join(pred))
        raise ValueError("All words in 'pred' must be present in 'label'.")
    
    emb = [0] * len(label)
    for index, l in enumerate(label):
        if l in pred:
            emb[index] = 1
    return emb

def converts_emb_p(p):
    if len(p) != 4 or p[0] not in 'EI' or p[1] not in 'SN' or p[2] not in 'TF' or p[3] not in 'JP':
        raise ValueError("Input string does not match expected MBTI format.")
    
    return [1 if p[i] in 'ESFP' else 0 for i in range(4)]

def converts_emb_e(e):
    if not all(e in ['快乐', '悲伤', '厌恶', '恐惧', '惊讶', '愤怒'] for e in e.keys()):
        raise ValueError("Input dictionary does not match expected emotion format.")
    
    return [e['快乐'], e['悲伤'], e['厌恶'], e['恐惧'], e['惊讶'], e['愤怒']]

def converts_emb_rc(rc):
    if rc not in ['A', 'B', 'C', 'D']:
        raise ValueError("Input string does not match expected rolechoice format.")
    
    return [1 if rc == r else 0 for r in ['A', 'B', 'C', 'D']]


def pad_matrix_with_zeros(matrix):
    max_len = max(len(row) for row in matrix)
    padded_matrix = np.array([np.pad(row, (0, max_len - len(row)), 'constant', constant_values=0) for row in matrix])
    return padded_matrix

def read_human_valid_data(data_path):
    data = pd.read_csv(data_path)
    # Check "_valid" columns are binary
    for col in data.columns:
        if col.endswith("_valid"):
            assert data[col].isin([0, 1]).all()
    # Check "rolechoice_human_eval" is in ["A", "B", "C", "D"]
    assert data["rolechoice_human_eval"].isin(["A", "B", "C", "D"]).all()
    # Check if ‘emotion_human_eval’ can all be turned into dict and then {‘happy’: 3, ‘sad’: 0, ‘disgust’: 8, ‘fear’: 5, ‘surprise’: 3, ‘anger’: 7} key is not one of these 6 and value is not 0-10
    assert data["emotion_human_eval"].apply(eval).apply(lambda x: set(x.keys()) == {"快乐", "悲伤", "厌恶", "恐惧", "惊讶", "愤怒"} and all(0 <= v <= 10 for v in x.values())).all()
    data["emotion_eval"] = data["emotion_eval"].apply(eval)
    data["emotion_human_eval"] = data["emotion_human_eval"].apply(eval)
    # Check if relationship_human_eval is 0-10.
    assert data["relationship_human_eval"].between(0, 10).all()
    # Check if personality_human_eval is MBTI 4 characters
    assert data["personality_human_eval"].apply(len).eq(4).all()
    # Check if personality_human_eval is in ["EI", "SN", "TF", "JP"]
    MBTI_legal_chars = [["E", "I"], ["S", "N"], ["T", "F"], ["J", "P"]]
    for i in range(4):
        assert data["personality_human_eval"].str[i].isin(MBTI_legal_chars[i]).all()
    # Check if human_likeness_human_eval is 0 or 1
    assert data["human_likeness_human_eval"].isin([0, 1]).all()
    # Check if coherence_human_eval is 0 or 1
    assert data["coherence_human_eval"].isin([0, 1]).all()
    # Take ‘data[’character‘]’ and cut it up into lists, where it's, like, all of it.
    data["character"] = data["character"].apply(lambda x: x.replace(",", "，").split("，"))
    data["character_human_eval"] = data["character_human_eval"].apply(lambda x: x.replace(",", "，").split("，"))
    data["character_eval"] = data["character_eval"].apply(eval)
    # Take ‘data[’style‘]’ and cut it up into lists
    data["style"] = data["style"].apply(lambda x: x.split("、"))
    data["style_human_eval"] = data["style_human_eval"].apply(lambda x: x.split("、"))
    data["style_eval"] = data["style_eval"].apply(eval)
    return data


def converts_emb(data: pd.DataFrame):
    data["emotion_human_eval_emb"] = data["emotion_human_eval"].apply(converts_emb_e)
    data["emotion_eval_emb"] = data["emotion_eval"].apply(converts_emb_e)
    data["character_eval_emb"] = data.apply(lambda x: converts_emb_c_s(x["character"], x["character_eval"]), axis=1)
    data["character_human_eval_emb"] = data.apply(lambda x: converts_emb_c_s(x["character"], x["character_human_eval"]), axis=1)
    data["style_eval_emb"] = data.apply(lambda x: converts_emb_c_s(x["style"], x["style_eval"]), axis=1)
    data["style_human_eval_emb"] = data.apply(lambda x: converts_emb_c_s(x["style"], x["style_human_eval"]), axis=1)
    data["personality_eval_emb"] = data["personality_eval"].apply(converts_emb_p)
    data["personality_human_eval_emb"] = data["personality_human_eval"].apply(converts_emb_p)
    data["rolechoice_eval_emb"] = data["rolechoice_eval"].apply(converts_emb_rc)
    data["rolechoice_human_eval_emb"] = data["rolechoice_human_eval"].apply(converts_emb_rc)
    
    return data
    

def calculate_cosine_similarity(data: pd.DataFrame):
    character_eval = pad_matrix_with_zeros(data["character_eval_emb"].to_numpy())
    character_human_eval = pad_matrix_with_zeros(data["character_human_eval_emb"].to_numpy())
    character_similarity, character_similarity_sem = calculate_global_cosine_similarity(character_eval, character_human_eval)
    print(f"character_similarity: {round(character_similarity, 2)} ± {round(character_similarity_sem, 2)}")
    
    style_eval = pad_matrix_with_zeros(data["style_eval_emb"].to_numpy())
    style_human_eval = pad_matrix_with_zeros(data["style_human_eval_emb"].to_numpy())
    style_similarity, style_similarity_sem = calculate_global_cosine_similarity(style_eval, style_human_eval)
    print(f"style_similarity: {round(style_similarity, 2)} ± {round(style_similarity_sem, 2)}")
    
    emotion_eval = pad_matrix_with_zeros(data["emotion_eval_emb"].to_numpy())
    emotion_human_eval = pad_matrix_with_zeros(data["emotion_human_eval_emb"].to_numpy())
    emotion_similarity, emotion_similarity_sem = calculate_global_cosine_similarity(emotion_eval, emotion_human_eval)
    print(f"emotion_similarity: {round(emotion_similarity, 2)} ± {round(emotion_similarity_sem, 2)}")
    
    relationship_eval = data["relationship_eval"].to_numpy().reshape(1, -1)
    relationship_human_eval = data["relationship_human_eval"].to_numpy().reshape(1, -1)
    relationship_similarity, relationship_similarity_sem = calculate_global_cosine_similarity(relationship_eval, relationship_human_eval)
    print(f"relationship_similarity: {round(relationship_similarity, 2)} ± {round(relationship_similarity_sem, 2)}")
    
    personality_eval = pad_matrix_with_zeros(data["personality_eval_emb"].to_numpy())
    personality_human_eval = pad_matrix_with_zeros(data["personality_human_eval_emb"].to_numpy())
    personality_similarity, personality_similarity_sem = calculate_global_cosine_similarity(personality_eval, personality_human_eval)
    print(f"personality_similarity: {round(personality_similarity, 2)} ± {round(personality_similarity_sem, 2)}")
    
    human_likeness_eval = data["human_likeness_eval"].to_numpy().reshape(1, -1)
    human_likeness_human_eval = data["human_likeness_human_eval"].to_numpy().reshape(1, -1)
    human_likeness_similarity, human_likeness_similarity_sem = calculate_global_cosine_similarity(human_likeness_eval, human_likeness_human_eval)
    print(f"human_likeness_similarity: {round(human_likeness_similarity, 2)} ± {round(human_likeness_similarity_sem, 2)}")
    
    rolechoice_eval = pad_matrix_with_zeros(data["rolechoice_eval_emb"].to_numpy())
    rolechoice_human_eval = pad_matrix_with_zeros(data["rolechoice_human_eval_emb"].to_numpy())
    rolechoice_similarity, rolechoice_similarity_sem = calculate_global_cosine_similarity(rolechoice_eval, rolechoice_human_eval)
    print(f"rolechoice_similarity: {round(rolechoice_similarity, 2)} ± {round(rolechoice_similarity_sem, 2)}")
    
    coherence_eval = data["coherence_eval"].to_numpy().reshape(1, -1)
    coherence_human_eval = data["coherence_human_eval"].to_numpy().reshape(1, -1)
    coherence_similarity, coherence_similarity_sem = calculate_global_cosine_similarity(coherence_eval, coherence_human_eval)
    print(f"coherence_similarity: {round(coherence_similarity, 2)} ± {round(coherence_similarity_sem, 2)}")
    

def calculate_validity(data: pd.DataFrame):
    role_valid = data["role_valid"].mean()
    role_valid_sem = data["role_valid"].std() / np.sqrt(len(data))
    print(f"role_valid: {round(role_valid, 2)} ± {round(role_valid_sem, 2)}")

    scene_valid = data["scene_valid"].mean()
    scene_valid_sem = data["scene_valid"].std() / np.sqrt(len(data))
    print(f"scene_valid: {round(scene_valid, 2)} ± {round(scene_valid_sem, 2)}")

    emotion_valid = data["emotions_valid"].mean()
    emotion_valid_sem = data["emotions_valid"].std() / np.sqrt(len(data))
    print(f"emotion_valid: {round(emotion_valid, 2)} ± {round(emotion_valid_sem, 2)}")

    relationship_valid = data["relationship_valid"].mean()
    relationship_valid_sem = data["relationship_valid"].std() / np.sqrt(len(data))
    print(f"relationship_valid: {round(relationship_valid, 2)} ± {round(relationship_valid_sem, 2)}")

    dialogues_valid = data["dialogues_valid"].mean()
    dialogues_valid_sem = data["dialogues_valid"].std() / np.sqrt(len(data))
    print(f"dialogues_valid: {round(dialogues_valid, 2)} ± {round(dialogues_valid_sem, 2)}")

    charcater_a_valid = data["charcater_a_valid"].mean()
    charcater_a_valid_sem = data["charcater_a_valid"].std() / np.sqrt(len(data))
    print(f"charcater_a_valid: {round(charcater_a_valid, 2)} ± {round(charcater_a_valid_sem, 2)}")

    style_a_valid = data["style_a_valid"].mean()
    style_a_valid_sem = data["style_a_valid"].std() / np.sqrt(len(data))
    print(f"style_a_valid: {round(style_a_valid, 2)} ± {round(style_a_valid_sem, 2)}")

    emotion_a_valid = data["emotion_a_valid"].mean()
    emotion_a_valid_sem = data["emotion_a_valid"].std() / np.sqrt(len(data))
    print(f"emotion_a_valid: {round(emotion_a_valid, 2)} ± {round(emotion_a_valid_sem, 2)}")

    relationship_a_valid = data["relationship_a_valid"].mean()
    relationship_a_valid_sem = data["relationship_a_valid"].std() / np.sqrt(len(data))
    print(f"relationship_a_valid: {round(relationship_a_valid, 2)} ± {round(relationship_a_valid_sem, 2)}")

    personality_a_valid = data["personality_a_valid"].mean()
    personality_a_valid_sem = data["personality_a_valid"].std() / np.sqrt(len(data))
    print(f"personality_a_valid: {round(personality_a_valid, 2)} ± {round(personality_a_valid_sem, 2)}")

    human_likeness_a_valid = data["human_likeness_a_valid"].mean()
    human_likeness_a_valid_sem = data["human_likeness_a_valid"].std() / np.sqrt(len(data))
    print(f"human_likeness_a_valid: {round(human_likeness_a_valid, 2)} ± {round(human_likeness_a_valid_sem, 2)}")

    rolechoice_a_valid = data["rolechoice_a_valid"].mean()
    rolechoice_a_valid_sem = data["rolechoice_a_valid"].std() / np.sqrt(len(data))
    print(f"rolechoice_a_valid: {round(rolechoice_a_valid, 2)} ± {round(rolechoice_a_valid_sem, 2)}")

    coherence_a_valid = data["coherence_a_valid"].mean()
    coherence_a_valid_sem = data["coherence_a_valid"].std() / np.sqrt(len(data))
    print(f"coherence_a_valid: {round(coherence_a_valid, 2)} ± {round(coherence_a_valid_sem, 2)}")
    
# python -m HumanValid.calculate_metrics
if __name__ == "__main__":
    data = read_human_valid_data("../data/human_valid/Human_Valid.csv")
    data = converts_emb(data)
    print("===================Validity===================")
    calculate_validity(data)
    print("===================Cosine Similarity===================")
    calculate_cosine_similarity(data)
