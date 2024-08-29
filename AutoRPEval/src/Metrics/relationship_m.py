import glob
import json
import os

import numpy as np
import tqdm
from config import MetricModels, t_TestModel
from scipy import stats

def calculate_role_relationship(role_file):
    role_data = json.load(open(role_file, 'r'))
    relationship_scores = []
    for chat_role, chat in role_data['chats'].items():
        label = chat['relationship_score']
        pred = chat['relationship_eval']
        relationship_score = abs(label - pred) / 10
        relationship_scores.append(relationship_score)
    return relationship_scores
        
def process_base_dirs(base_dirs, t_test=False):
    calculate_models = MetricModels
    relationship_metric = {}
    t_test_array = []
    for model in calculate_models:
        test_roles = []
        for base_dir in base_dirs:
            model_dir = os.path.join(base_dir, model)
            test_roles.extend(glob.glob(f"{model_dir}/*.json"))
        model_relationship_scores = []
        for role_file in test_roles:
            relationship_score = calculate_role_relationship(role_file)
            model_relationship_scores.extend(relationship_score)
        
        mean_relationship_score = np.mean(model_relationship_scores)
        sem_relationship_score = np.std(model_relationship_scores, ddof=1) / np.sqrt(len(model_relationship_scores))
        if model in t_TestModel:
            t_test_array.append(np.array(model_relationship_scores))
        # print(f"Model {model} relationship score: {round(mean_relationship_score * 100, 2)} ± {round(sem_relationship_score * 100, 2)}")
        relationship_metric[model] = (1 - mean_relationship_score, sem_relationship_score)
    if t_test and len(t_test_array) == 2:
        t_stat, p_value = stats.ttest_ind(t_test_array[0], t_test_array[1])
        print("*" * 20 + "T-Test-Relationship" + "*" * 20)
        print(f"Models: {t_TestModel}")
        print(f"t-statistic: {t_stat} p-value: {p_value}")
        print("*" * 20 + "T-Test-Relationship" + "*" * 20)
    return relationship_metric

def relationship_m():
    # print("==================CN==================")
    base_dir = '../chat_dialogues'
    relationship_metric_cn = process_base_dirs([base_dir])
    # print("==================EN==================")
    base_dir = '../chat_dialogues_en'
    relationship_metric_en = process_base_dirs([base_dir])
    # print("==================CN & EN==================")
    relationship_metric = process_base_dirs(['../chat_dialogues', '../chat_dialogues_en'], t_test=True)
    return relationship_metric_cn, relationship_metric_en, relationship_metric

# python -m Metrics.relationship_m
if __name__ == '__main__':
    relationship_m()
