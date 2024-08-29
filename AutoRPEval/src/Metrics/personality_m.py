import glob
import json
import os

import numpy as np
from config import MetricModels, t_TestModel
from scipy import stats

opposites = {
        "I": "E",
        "E": "I",
        "N": "S",
        "S": "N",
        "T": "F",
        "F": "T",
        "J": "P",
        "P": "J"
    }

def vote_personlaity(role_data):
    label = role_data['personality']
    vote_result = {
        "I": 0,
        "E": 0,
        "N": 0,
        "S": 0,
        "T": 0,
        "F": 0,
        "J": 0,
        "P": 0
    }
    for chat_role, chat in role_data['chats'].items():
        if chat['personality_eval'] is None:
            raise ValueError(f"Chat {chat['chat_id']} has no personality evaluation.")
        for index, c in enumerate(chat['personality_eval']):
            vote_result[c] += 1
    correct = 0
    pred_personality = []
    for trait in label:
        if vote_result[trait] >= vote_result[opposites[trait]]:
            correct += 1
            pred_personality.append(trait)
        else:
            pred_personality.append(opposites[trait])
    return pred_personality, correct / len(label)

def cal_chat_personality(role_data):
    label = role_data['personality']
    role_personality_scores = []
    for chat_role, chat in role_data['chats'].items():
        if chat['personality_eval'] is None:
            raise ValueError(f"Chat {chat['chat_id']} has no personality evaluation.")
        correct = 0
        for l, p in zip(label, chat['personality_eval']):
            if l == p:
                correct += 1
        role_personality_scores.append(correct / len(label))
    return np.mean(role_personality_scores)
            
            

def calculate_role_personality(role_file):
    role_data = json.load(open(role_file, 'r'))
    # pred_personality, personality_score = vote_personlaity(role_data)
    personality_score = cal_chat_personality(role_data)
    return personality_score

def process_base_dirs(base_dirs, t_test=False):
    calculate_models = MetricModels
    personality_metric = {}
    t_test_array = []
    for model in calculate_models:
        test_roles = []
        for base_dir in base_dirs:
            model_dir = os.path.join(base_dir, model)
            test_roles.extend(glob.glob(f"{model_dir}/*.json"))
        model_personality_scores = []
        for role_file in test_roles:
            personality_score = calculate_role_personality(role_file)
            model_personality_scores.append(personality_score)
        
        mean_personality_score = np.mean(model_personality_scores)
        sem_personality_score = np.std(model_personality_scores, ddof=1) / np.sqrt(len(model_personality_scores))
        if model in t_TestModel:
            t_test_array.append(np.array(model_personality_scores))
        # print(f"Model {model} personality score: {round(mean_personality_score * 100, 2)} ± {round(sem_personality_score * 100, 2)}")
        personality_metric[model] = (mean_personality_score, sem_personality_score)
    if t_test and len(t_test_array) == 2:
        t_stat, p_value = stats.ttest_ind(t_test_array[0], t_test_array[1])
        print("*" * 20 + "T-Test-Personality" + "*" * 20)
        print(f"Models: {t_TestModel}")
        print(f"t-statistic: {t_stat} p-value: {p_value}")
        print("*" * 20 + "T-Test-Personality" + "*" * 20)
    return personality_metric

def personality_m():
    # print("==================CN==================")
    base_dir = '../chat_dialogues'
    personality_metric_cn = process_base_dirs([base_dir])
    # print("==================EN==================")
    base_dir = '../chat_dialogues_en'
    personality_metric_en = process_base_dirs([base_dir])
    # print("==================CN & EN==================")
    personality_metric = process_base_dirs(['../chat_dialogues', '../chat_dialogues_en'], t_test=True)
    return personality_metric_cn, personality_metric_en, personality_metric

# python -m Metrics.personality_m
if __name__ == "__main__":
    personality_m()