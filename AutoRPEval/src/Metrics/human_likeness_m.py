import glob
import json
import os

import numpy as np
from config import MetricModels, t_TestModel
from scipy import stats

def calculate_human_likeness(role_file):
    role_data = json.load(open(role_file, 'r'))
    true_count = 0
    for chat_role, chat in role_data['chats'].items():
        if chat['human_likeness_eval'] == 1:
            true_count += 1
    return true_count / len(role_data['chats'])
            

def process_base_dirs(base_dirs, t_test=False):
    calculate_models = MetricModels
    human_likeness_metric = {}
    t_test_array = []
    for model in calculate_models:
        test_roles = []
        for base_dir in base_dirs:
            model_dir = os.path.join(base_dir, model)
            test_roles.extend(glob.glob(f"{model_dir}/*.json"))
        model_human_likeness_scores = []
        for role_file in test_roles:
            human_likeness_score = calculate_human_likeness(role_file)
            model_human_likeness_scores.append(human_likeness_score)
        
        mean_human_likeness_score = np.mean(model_human_likeness_scores)
        sem_human_likeness_score = np.std(model_human_likeness_scores, ddof=1) / np.sqrt(len(model_human_likeness_scores))
        if model in t_TestModel:
            t_test_array.append(np.array(model_human_likeness_scores))
        # print(f"Model {model} Human likeness: {round(mean_human_likeness_score * 100, 2)} ± {round(sem_human_likeness_score * 100, 2)}")
        human_likeness_metric[model] = (mean_human_likeness_score, sem_human_likeness_score)
    if t_test and len(t_test_array) == 2:
        t_stat, p_value = stats.ttest_ind(t_test_array[0], t_test_array[1])
        print("*" * 20 + "T-Test-Human-likeness" + "*" * 20)
        print(f"Models: {t_TestModel}")
        print(f"t-statistic: {t_stat} p-value: {p_value}")
        print("*" * 20 + "T-Test-Human-likeness" + "*" * 20)
    return human_likeness_metric

def human_likeness_m():
    # print("==================CN==================")
    base_dir = '../chat_dialogues'
    human_likeness_metric_cn = process_base_dirs([base_dir])
    # print("==================EN==================")
    base_dir = '../chat_dialogues_en'
    human_likeness_metric_en = process_base_dirs([base_dir])
    # print("==================CN & EN==================")
    human_likeness_metric = process_base_dirs(['../chat_dialogues', '../chat_dialogues_en'], t_test=True)
    return human_likeness_metric_cn, human_likeness_metric_en, human_likeness_metric

# python -m Metrics.human_likeness_m
if __name__ == '__main__':
    human_likeness_m()
