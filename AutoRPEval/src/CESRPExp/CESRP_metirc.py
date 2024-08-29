import glob
import os
import json
import numpy as np
import pandas as pd

def calculate_C_S(pred, label):
    if pred == "": return 0
    TP = sum(1 for c in label if c in label and c in pred)
    TN = sum(1 for c in label if c not in label and c not in pred)
    FP = sum(1 for c in label if c not in label and c in pred)
    FN = sum(1 for c in label if c in label and c not in pred)
        
    accuracy = (TP + TN) / (TP + TN + FP + FN)
    recall = TP / (TP + FN) if TP + FN != 0 else 0
    precision = TP / (TP + FP) if TP + FP != 0 else 0
        
    return recall

def calculate_E(pred, label):
    if pred == "": return 1
    mape_norm_record = []
    for key in label.keys():
        mape_norm = abs(label[key] - pred[key]) / 10
        mape_norm_record.append(mape_norm)
    return np.mean(mape_norm_record)

def calculate_R(pred, label):
    if pred == "": return 1
    return abs(pred - label) / 10

def calculate_P(pred, label):
    if pred == "": return 0
    correct = 0
    for l, p in zip(label, pred):
        if l == p:
            correct += 1
    return correct / len(label)

def main():
    type_dict = {
    "character": calculate_C_S,
    "emotion": calculate_E,
    "style": calculate_C_S,
    "relationship": calculate_R,
    "personality": calculate_P
    }
    result_path = "../data/CESRP_results"
    all_files = glob.glob(os.path.join(result_path, "*.json"))
    model_results = {}
    for file in all_files:
        print(file)
        model_name = file.split("/")[-1].split("_CESRP_test.")[0]
        result = json.load(open(file, 'r'))
        model_results[model_name] = {}
        for index, test_data in enumerate(result):
            score = type_dict[test_data['type']](test_data["eval_result"], test_data['A'])
            if test_data['type'] not in model_results[model_name]:
                model_results[model_name][test_data['type']] = []
            model_results[model_name][test_data['type']].append(score)
    # calculate the average score and sem score
    save_results = {}
    for model_name in model_results:
        for type_name in model_results[model_name]:
            if model_name not in save_results:
                save_results[model_name] = {}
            mean_score = np.mean(model_results[model_name][type_name])
            sem_score = np.std(model_results[model_name][type_name], ddof=1) / np.sqrt(len(model_results[model_name][type_name]))
            # print(f"Model {model} personality score: {round(mean_personality_score * 100, 2)} ± {round(sem_personality_score * 100, 2)}")
            print(f"Model {model_name} {type_name} score: {round(mean_score * 100, 2)} ± {round(sem_score * 100, 2)}")
            save_results[model_name][type_name] = f"{round(mean_score * 100, 2)} ± {round(sem_score * 100, 2)}"
    # 最终计算每一个模型的5个维度的average，注意Emotion和Relation计算时要用100减去，同时计算sem
    for model_name in save_results:
        average_score = 0
        sem_score = 0
        for type_name in save_results[model_name]:
            if type_name == "emotion" or type_name == "relationship":
                average_score += 100 - float(save_results[model_name][type_name].split(" ± ")[0])
                sem_score += float(save_results[model_name][type_name].split(" ± ")[1])
            else:
                average_score += float(save_results[model_name][type_name].split(" ± ")[0])
                sem_score += float(save_results[model_name][type_name].split(" ± ")[1])
        average_score /= 5
        sem_score /= 5
        print(f"Model {model_name} average score: {round(average_score, 2)} ± {round(sem_score, 2)}")
        save_results[model_name]["average"] = f"{round(average_score, 2)} ± {round(sem_score, 2)}"
    # save to excel

    df = pd.DataFrame(save_results)
    df.T.to_excel("../CESRP_results/CESRP_test_result.xlsx")
    
            
            
    
# python -m CESRPExp.CESRP_metirc
if __name__ == "__main__":
    main()