import glob
import json
import os

import numpy as np
from config import MetricModels, t_TestModel
from scipy import stats

def calculate_coherence(role_file):
    role_data = json.load(open(role_file, 'r'))
    true_count = 0
    for chat_role, chat in role_data['chats'].items():
        if chat['coherence_eval'] == 1:
            true_count += 1
    return true_count / len(role_data['chats'])
            

def process_base_dirs(base_dirs, t_test=False):
    calculate_models = MetricModels
    coherence_metric = {}
    t_test_array = []
    for model in calculate_models:
        test_roles = []
        for base_dir in base_dirs:
            model_dir = os.path.join(base_dir, model)
            test_roles.extend(glob.glob(f"{model_dir}/*.json"))
        model_coherence_scores = []
        for role_file in test_roles:
            coherence_score = calculate_coherence(role_file)
            model_coherence_scores.append(coherence_score)
        
        mean_coherence_score = np.mean(model_coherence_scores)
        sem_coherence_score = np.std(model_coherence_scores, ddof=1) / np.sqrt(len(model_coherence_scores))
        if model in t_TestModel:
            t_test_array.append(np.array(model_coherence_scores))
        # print(f"Model {model} Coherence: {round(mean_coherence_score * 100, 2)} ± {round(sem_coherence_score * 100, 2)}")
        coherence_metric[model] = (mean_coherence_score, sem_coherence_score)
    if t_test and len(t_test_array) == 2:
        t_stat, p_value = stats.ttest_ind(t_test_array[0], t_test_array[1])
        print("*" * 20 + "T-Test-Coherence" + "*" * 20)
        print(f"Models: {t_TestModel}")
        print(f"t-statistic: {t_stat} p-value: {p_value}")
        print("*" * 20 + "T-Test-Coherence" + "*" * 20)
    return coherence_metric

def coherence_m():
    # print("==================CN==================")
    base_dir = '../chat_dialogues'
    coherence_metric_cn = process_base_dirs([base_dir])
    # print("==================EN==================")
    base_dir = '../chat_dialogues_en'
    coherence_metric_en = process_base_dirs([base_dir])
    # print("==================CN & EN==================")
    coherence_metric = process_base_dirs(['../chat_dialogues', '../chat_dialogues_en'], t_test=True)
    return coherence_metric_cn, coherence_metric_en, coherence_metric

# python -m Metrics.coherence_m
if __name__ == '__main__':
    coherence_m()
