import glob
import json
import os

import numpy as np
from config import MetricModels, t_TestModel
from scipy import stats


def calculate_role_emotion(role_file):
    role_data = json.load(open(role_file, 'r'))
    emotion_scores = []
    for chat_role, chat in role_data['chats'].items():
        label = chat['emotions']
        pred = chat['emotion_eval']
        mape_norm_record = []
        for key in label.keys():
            mape_norm = abs(label[key] - pred[key]) / 10
            mape_norm_record.append(mape_norm)
        emotion_scores.append(np.mean(mape_norm_record))
    return emotion_scores

def process_base_dirs(base_dirs, t_test=False):
    calculate_models = MetricModels
    emotion_metric = {}
    t_test_array = []
    for model in calculate_models:
        test_roles = []
        for base_dir in base_dirs:
            model_dir = os.path.join(base_dir, model)
            test_roles.extend(glob.glob(f"{model_dir}/*.json"))
        model_emotion_scores = []
        for role_file in test_roles:
            emotion_score = calculate_role_emotion(role_file)
            model_emotion_scores.extend(emotion_score)
        
        mean_emotion_score = np.mean(model_emotion_scores)
        sem_emotion_score = np.std(model_emotion_scores, ddof=1) / np.sqrt(len(model_emotion_scores))
        if model in t_TestModel:
            t_test_array.append(np.array(model_emotion_scores))
        # print(f"Model {model} emotion score: {round(mean_emotion_score * 100, 2)} ± {round(sem_emotion_score * 100, 2)}")
        emotion_metric[model] = (1 - mean_emotion_score, sem_emotion_score)
    if t_test and len(t_test_array) == 2:
        t_stat, p_value = stats.ttest_ind(t_test_array[0], t_test_array[1])
        print("*" * 20 + "T-Test-Emotion" + "*" * 20)
        print(f"Models: {t_TestModel}")
        print(f"t-statistic: {t_stat} p-value: {p_value}")
        print("*" * 20 + "T-Test-Emotion" + "*" * 20)
    return emotion_metric

def emotion_m():
    # print("==================CN==================")
    base_dir = '../chat_dialogues'
    emotion_metric_cn = process_base_dirs([base_dir])
    # print("==================EN==================")
    base_dir = '../chat_dialogues_en'
    emotion_metric_en = process_base_dirs([base_dir])
    # print("==================CN & EN==================")
    emotion_metric = process_base_dirs(['../chat_dialogues', '../chat_dialogues_en'], t_test=True)
    return emotion_metric_cn, emotion_metric_en, emotion_metric

# python -m Metrics.emotion_m
if __name__ == '__main__':
    emotion_m()
