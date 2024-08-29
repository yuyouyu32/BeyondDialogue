import json
import os
from utils import collect_roles

from wordcloud import WordCloud
import matplotlib.pyplot as plt
from DatasetSta.translate import *

def generate_wordcloud_from_frequencies(frequencies, file_name):

    wordcloud = WordCloud(width=1600, height=800, background_color='white').generate_from_frequencies(frequencies)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')  # 关闭坐标轴
    plt.savefig(f'../figures/{file_name}.pdf', dpi=500)
    plt.close()


def word_count(role_files, key, translate=False):
    words_count = {}
    for role_file in role_files:
        role_data = json.load(open(role_file))
        characters = role_data[key].lower().replace('、', ',').replace('，', ',').replace(' ', '').split(',')
        for character in characters:
            if character and character not in words_count:
                words_count[character] = 1
            else:
                words_count[character] += 1
    if translate:
        all_characters = list(words_count.keys())
        try:
            en_characters = translate_words(all_characters)
        except:
            print("Translate Error")
            with open(TranslateMapPath, 'w') as f:
                json.dump(Dictionary, f, indent=4, ensure_ascii=False)
                return None
        en_words_count = {en_c: words_count[cn_c] for cn_c, en_c in zip(all_characters,  en_characters)}
        words_count = en_words_count
        with open(TranslateMapPath, 'w') as f:
            json.dump(Dictionary, f, indent=4, ensure_ascii=False)
    return words_count


def character_word_count(role_files, translate=False):
    return word_count(role_files, 'character', translate)


def style_word_count(role_files, translate=False):
    return word_count(role_files, 'style', translate)

# python -m DatasetSta.character_style
def main():
    EN_Path = "../../NovelData/AB_dialogues_EN"
    CN_Path = "../../NovelData/AB_dialogues_top10len"
    role_files_en = collect_roles(EN_Path)
    role_files_cn = collect_roles(CN_Path)
    ### Character ###
    character_en = character_word_count(role_files_en, translate=False)
    character_cn = character_word_count(role_files_cn, translate=True)
    # combine en and cn
    all_character_count = {}
    for character, count in character_en.items():
        all_character_count[character] = count
    for character, count in character_cn.items():
        if character in all_character_count:
            all_character_count[character] += count
        else:
            all_character_count[character] = count
    generate_wordcloud_from_frequencies(all_character_count, 'character_wordcloud')
    
    ### Style ###
    style_en = style_word_count(role_files_en, translate=False)
    style_cn = style_word_count(role_files_cn, translate=True)
    # combine en and cn
    all_style_count = {}
    for style, count in style_en.items():
        all_style_count[style] = count
    for style, count in style_cn.items():
        if style in all_style_count:
            all_style_count[style] += count
        else:
            all_style_count[style] = count
    generate_wordcloud_from_frequencies(all_style_count, 'style_wordcloud')

# python -m DatasetSta.character_style
if __name__ == '__main__':
    main()
    