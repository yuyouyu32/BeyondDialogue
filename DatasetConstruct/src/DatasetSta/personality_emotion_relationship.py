import json

from pyecharts import options as opts
from pyecharts.charts import Pie
from pyecharts.globals import ThemeType
from utils import collect_roles

EmotionMap = {
    "快乐": "happiness",
    "悲伤": "sadness",
    "厌恶": "disgust",
    "恐惧": "fear",
    "惊讶": "surprise",
    "愤怒": "anger"
}


def draw_pie_chart(data, title):
    # Convert to the format required by pyecharts
    data_pair = [(k, v) for k, v in data.items()]
    # sort by v
    data_pair = sorted(data_pair, key=lambda x: x[1], reverse=True)
    # Create a pie chart with pyecharts
    print(data_pair)
    pie = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.MACARONS))
        .add(
            "",
            data_pair,
            radius=["30%", "70%"], 
            center=["60%", "50%"],  # Adjust center to move the pie chart
            rosetype="radius",  # Use rosetype to create a rose chart
        )
        .set_global_opts(
            # title_opts=opts.TitleOpts(title=title, title_textstyle_opts=opts.TextStyleOpts(font_weight="bold")),
            legend_opts=opts.LegendOpts(
                orient="vertical", 
                pos_top="15%", 
                pos_left="2%",
                textstyle_opts=opts.TextStyleOpts(font_weight="bold")  # Set legend text to bold
            )
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(
                formatter="{b}: {d}%",
                position="outside",
                font_size=10,
                is_show=True,
                color="#000",
                distance=20,  # Adjust the distance from label to pie chart
                font_weight="bold"  # Set label text to bold
            )
        )
    )
    pie.render(f'../figures/{title}.html')


def e_r_p_count(role_files):
    emotions_count = {"happiness": 0,
                "sadness": 0,
                "disgust": 0,
                "fear": 0,
                "surprise": 0,
                "anger": 0}
    relationship_count = {}
    personality_count = {}
    for role_file in role_files:
        role_data = json.load(open(role_file, 'r'))
        personality = role_data["personality"]
        if personality in personality_count:
            personality_count[personality] += 1
        else:
            personality_count[personality] = 1
        for chat in role_data["chunks_with_dialogues"]:
            emotion = chat["emotion_scale_scores"]
            # key is max value key in emotion
            key = max(emotion, key=emotion.get)
            if key in EmotionMap.keys():
                emotions_count[EmotionMap[key]] += 1
            else:
                emotions_count[key] += 1
            relationship = int(chat["relationship"])
            if relationship in relationship_count:
                relationship_count[relationship] += 1
            else:
                relationship_count[relationship] = 1
    return emotions_count, relationship_count, personality_count
            
def main():
    EN_Path = "../../NovelData/AB_dialogues_EN"
    CN_Path = "../../NovelData/AB_dialogues_top10len"
    role_files_en = collect_roles(EN_Path)
    role_files_cn = collect_roles(CN_Path)
    all_files = role_files_en + role_files_cn
    emotions_count, relationship_count, personality_count = e_r_p_count(all_files)
    # upper emotion_count keys first letter
    emotions_count = dict((k.capitalize(), v) for k, v in emotions_count.items())
    draw_pie_chart(emotions_count, "Emotions")
    draw_pie_chart(relationship_count, "Relationship")
    draw_pie_chart(personality_count, "Personality")
    
# python -m DatasetSta.personality_emotion_relationship
if __name__ == "__main__":
    main()