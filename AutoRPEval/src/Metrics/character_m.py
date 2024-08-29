import glob
import json
import os

import numpy as np
import tqdm
from config import MetricModels, t_TestModel
from scipy import stats

def calculate_role_character(role_file):
    with open(role_file, 'r', encoding='utf-8') as file:
        role_data = json.load(file)
    
    character_scores_accuracy = []
    character_score_recall = []
    character_score_precision = []
    
    label = role_data['character'].replace(",", "，").split("，")
    character_candidates = role_data['character'].replace(",", "，").split("，")
    for chat_role, chat in role_data['chats'].items():
        pred = chat['character_eval']
        TP = sum(1 for c in character_candidates if c in label and c in pred)
        TN = sum(1 for c in character_candidates if c not in label and c not in pred)
        FP = sum(1 for c in character_candidates if c not in label and c in pred)
        FN = sum(1 for c in character_candidates if c in label and c not in pred)
        
        accuracy = (TP + TN) / (TP + TN + FP + FN)
        recall = TP / (TP + FN) if TP + FN != 0 else 0
        precision = TP / (TP + FP) if TP + FP != 0 else 0
        character_scores_accuracy.append(accuracy)
        character_score_recall.append(recall)
        character_score_precision.append(precision)
    return character_scores_accuracy, character_score_recall, character_score_precision

def process_base_dirs(base_dirs, t_test=False):
    calculate_models = MetricModels
    character_metrics = {}
    t_test_array = []
    for model in calculate_models:
        test_roles = []
        for base_dir in base_dirs:
            model_dir = os.path.join(base_dir, model)
            test_roles.extend(glob.glob(f"{model_dir}/*.json"))
        model_character_acc = []
        model_character_recall = []
        model_character_precision = []
        for role_file in test_roles:
            character_accuracy, character_recall, character_percision = calculate_role_character(role_file)
            model_character_acc.extend(character_accuracy)
            model_character_recall.extend(character_recall)
            model_character_precision.extend(character_percision)
        if model in t_TestModel:
            t_test_array.append(np.array(model_character_recall))
        mean_acc = np.mean(model_character_acc)
        mean_precision = np.mean(model_character_precision)
        mean_recall = np.mean(model_character_recall)
        sem_acc = np.std(model_character_acc, ddof=1) / np.sqrt(len(model_character_acc))
        sem_precision = np.std(model_character_precision, ddof=1) / np.sqrt(len(model_character_precision))
        sem_recall = np.std(model_character_recall, ddof=1) / np.sqrt(len(model_character_recall))
        
        # print(f"Model {model} character accuracy: {round(mean_acc * 100, 2)} ± {round(sem_acc * 100, 2)} character precision: {round(mean_precision * 100, 2)} ± {round(sem_precision * 100, 2)} character recall: {round(mean_recall * 100, 2)} ± {round(sem_recall * 100, 2)}")
        character_metrics[model] = (mean_recall, sem_recall)
    if t_test and len(t_test_array) == 2:
        t_stat, p_value = stats.ttest_ind(t_test_array[0], t_test_array[1])
        print("*" * 20 + "T-Test-Character" + "*" * 20)
        print(f"Models: {t_TestModel}")
        print(f"t-statistic: {t_stat} p-value: {p_value}")
        print("*" * 20 + "T-Test-Character" + "*" * 20)
    return character_metrics
        
def character_m():
    # print("==================CN==================")
    base_dirs = ['../chat_dialogues']
    character_metrics_cn = process_base_dirs(base_dirs)
    # print("==================EN==================")
    base_dirs = ['../chat_dialogues_en']
    character_metrics_en = process_base_dirs(base_dirs)
    # print("==================CN & EN==================")
    base_dirs = ['../chat_dialogues', '../chat_dialogues_en']
    character_metrics = process_base_dirs(base_dirs, t_test=True)
    return character_metrics_cn, character_metrics_en, character_metrics
        

# python -m Metrics.character_m
if __name__ == '__main__':
    character_m()
