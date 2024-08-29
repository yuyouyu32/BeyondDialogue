import glob
import json
import os

import numpy as np
from config import MetricModels, t_TestModel
from scipy import stats

def calculate_role_choice(role_file):
    role_data = json.load(open(role_file, 'r'))
    label = role_data['role_answer']
    correct_count = 0
    for chat_role, chat in role_data['chats'].items():
        pred = chat['rolechoice_eval']
        if pred not in {'A', 'B', 'C', 'D'}:
            raise ValueError(f"Invalid role choice {pred} in {role_file}")
        if pred == label:
            correct_count += 1
    return correct_count / len(role_data['chats'])
            
def process_base_dirs(base_dirs, t_test=False):
    calculate_models = MetricModels
    rolechoice_metric = {}
    t_test_array = []
    for model in calculate_models:
        test_roles = []
        for base_dir in base_dirs:
            model_dir = os.path.join(base_dir, model)
            test_roles.extend(glob.glob(f"{model_dir}/*.json"))
        model_choice_scores = []
        for role_file in test_roles:
            choice_score = calculate_role_choice(role_file)
            model_choice_scores.append(choice_score)
        
        mean_choice_score = np.mean(model_choice_scores)
        sem_choice_score = np.std(model_choice_scores, ddof=1) / np.sqrt(len(model_choice_scores))
        if model in t_TestModel:
            t_test_array.append(np.array(model_choice_scores))
        # print(f"Model {model} choice score: {round(mean_choice_score * 100, 2)} ± {round(sem_choice_score * 100, 2)}")
        rolechoice_metric[model] = (mean_choice_score, sem_choice_score)
    if t_test and len(t_test_array) == 2:
        t_stat, p_value = stats.ttest_ind(t_test_array[0], t_test_array[1])
        print("*" * 20 + "T-Test-RoleChoice" + "*" * 20)
        print(f"Models: {t_TestModel}")
        print(f"t-statistic: {t_stat} p-value: {p_value}")
        print("*" * 20 + "T-Test-RoleChoice" + "*" * 20)
    return rolechoice_metric

def rolechoice_m():
    # print("==================CN==================")
    base_dir = '../chat_dialogues'
    rolechoice_metric_cn = process_base_dirs([base_dir])
    # print("==================EN==================")
    base_dir = '../chat_dialogues_en'
    rolechoice_metric_en = process_base_dirs([base_dir])
    # print("==================CN & EN==================")
    rolechoice_metric = process_base_dirs(['../chat_dialogues', '../chat_dialogues_en'], t_test=True)
    return rolechoice_metric_cn, rolechoice_metric_en, rolechoice_metric

# python -m Metrics.rolechoice_m
if __name__ == '__main__':
    rolechoice_m()
