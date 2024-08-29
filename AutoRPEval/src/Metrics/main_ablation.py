from config import MetricModels
from Metrics.character_m import character_m
from Metrics.emotion_m import emotion_m
from Metrics.personality_m import personality_m
from Metrics.relationship_m import relationship_m
from Metrics.style_m import style_m
import pandas as pd

def main():
    all_result = {}
    cn_result = {}
    en_result = {}
    print("Metrics Models: ", MetricModels)
    print("================Running Metrics.character================")
    cn_result["character"], en_result["character"], all_result["character"] = character_m()
    print("================Running Metrics.style================")
    cn_result["style"], en_result["style"], all_result["style"] = style_m()
    print("================Running Metrics.emotion================")
    cn_result["emotion"], en_result["emotion"], all_result["emotion"] = emotion_m()
    print("================Running Metrics.relationship================")
    cn_result["relationship"], en_result["relationship"], all_result["relationship"] = relationship_m()
    print("================Running Metrics.personality================")
    cn_result["personality"], en_result["personality"], all_result["personality"] = personality_m()
    return cn_result, en_result, all_result

# python -m Metrics.main_ablation
if __name__ == '__main__':
    cn_result, en_result, all_result = main()
    for language, result in zip(["cn", "en", "all"], [cn_result, en_result, all_result]):
        print("================Calculate Average Scores================")
        average_scores = {}
        average_sems = {}
        # 计算character, style, emotion, relationship, personality的ave
        include_metrics = ['character',  'emotion', 'style', 'relationship', 'personality']
        for category, scores in result.items():
            if category not in include_metrics:
                continue
            for model, (score, sem) in scores.items():
                if model not in average_scores:
                    average_scores[model] = []
                    average_sems[model] = []
                average_scores[model].append(score)
                average_sems[model].append(sem)

        for model in average_scores:
            average_scores[model] = sum(average_scores[model]) / len(average_scores[model])
            average_sems[model] = sum(average_sems[model]) / len(average_sems[model])

        # 在result把emotion 和relationship tuple 第一个元素变成 1 - 第一个元素
        for category, scores in result.items():
            if category not in ["emotion", "relationship"]:
                continue
            for model, (score, sem) in scores.items():
                result[category][model] = (1 - score, sem)
        # 打印每个模型的平均分和平均标准误差
        for model in average_scores:
            print(f"{model}: average = {average_scores[model] * 100:.2f} ± {average_sems[model] * 100:.2f}")
        # 保存average_score 和 average_sem到result新的一个key中，并且是tuple的格式
        result["average_score"] = {model: (average_scores[model], average_sems[model]) for model in average_scores}
        # 保存result到xlsx文件中
        df = pd.DataFrame(result)
        # 把每一个(0.835, 0.04935105182049795)这样的tuple都变成 83.5 ± 4.94这样的字符串
        for col in df.columns:
            df[col] = df[col].apply(lambda x: f"{x[0] * 100:.2f} ± {x[1] * 100:.2f}")

        df = df[["character", "style", "emotion", "relationship", "personality", "average_score"]]

        df.to_excel(f"../ablation_results/Metrics_ablation_{language}_result.xlsx")
        