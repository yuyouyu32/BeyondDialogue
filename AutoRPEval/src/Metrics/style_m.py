import glob
import json
import os

import numpy as np
from config import MetricModels, t_TestModel
from scipy import stats

def calculate_role_style(role_file):
    with open(role_file, 'r', encoding='utf-8') as file:
        role_data = json.load(file)
    
    style_scores_accuracy = []
    style_score_recall = []
    style_score_precision = []
    style_candidates = role_data['style'].replace("、", ",").split(",")
    label = role_data['style'].replace("、", ",").split(",")
    for chat_role, chat in role_data['chats'].items():
        pred = chat.get('style_eval', [])
        TP = sum(1 for c in style_candidates if c in label and c in pred)
        TN = sum(1 for c in style_candidates if c not in label and c not in pred)
        FP = sum(1 for c in style_candidates if c not in label and c in pred)
        FN = sum(1 for c in style_candidates if c in label and c not in pred)
        
        accuracy = (TP + TN) / (TP + TN + FP + FN)
        recall = TP / (TP + FN) if TP + FN != 0 else 0
        precision = TP / (TP + FP) if TP + FP != 0 else 0
        style_scores_accuracy.append(accuracy)
        style_score_recall.append(recall)
        style_score_precision.append(precision)
    
    return style_scores_accuracy, style_score_recall, style_score_precision
        
def process_base_dirs(base_dirs, t_test=False):
    calculate_models = MetricModels
    style_metrics = {}
    t_test_array = []
    for model in calculate_models:
        test_roles = []
        for base_dir in base_dirs:
            model_dir = os.path.join(base_dir, model)
            test_roles.extend(glob.glob(f"{model_dir}/*.json"))
        model_style_acc = []
        model_style_recall = []
        model_style_precision = []
        for role_file in test_roles:
            style_accuracy, style_recall, style_precision = calculate_role_style(role_file)
            model_style_acc.extend(style_accuracy)
            model_style_recall.extend(style_recall)
            model_style_precision.extend(style_precision)
        
        mean_acc = np.mean(model_style_acc)
        mean_precision = np.mean(model_style_precision)
        mean_recall = np.mean(model_style_recall)
        
        sem_acc = np.std(model_style_acc, ddof=1) / np.sqrt(len(model_style_acc))
        sem_precision = np.std(model_style_precision, ddof=1) / np.sqrt(len(model_style_precision))
        sem_recall = np.std(model_style_recall, ddof=1) / np.sqrt(len(model_style_recall))
        if model in t_TestModel:
            t_test_array.append(np.array(model_style_recall))
        # print(f"Model {model} style accuracy: {round(mean_acc * 100, 2)} ± {round(sem_acc * 100, 2)} style precision: {round(mean_precision * 100, 2)} ± {round(sem_precision * 100, 2)} style recall: {round(mean_recall * 100, 2)} ± {round(sem_recall * 100, 2)}")
        style_metrics[model] = (mean_recall, sem_recall)
        
    if t_test and len(t_test_array) == 2:
        t_stat, p_value = stats.ttest_ind(t_test_array[0], t_test_array[1])
        print("*" * 20 + "T-Test-Style" + "*" * 20)
        print(f"Models: {t_TestModel}")
        print(f"t-statistic: {t_stat} p-value: {p_value}")
        print("*" * 20 + "T-Test-Style" + "*" * 20)
    return style_metrics        

def style_m():
    # print("==================CN==================")
    base_dir = '../chat_dialogues'
    style_metric_cn = process_base_dirs([base_dir])
    # print("==================EN==================")
    base_dir = '../chat_dialogues_en'
    style_metric_en = process_base_dirs([base_dir])
    # print("==================CN & EN==================")
    style_metric = process_base_dirs(['../chat_dialogues', '../chat_dialogues_en'], t_test=True)
    return style_metric_cn, style_metric_en, style_metric

# python -m Metrics.style_m
if __name__ == '__main__':
    style_m()
