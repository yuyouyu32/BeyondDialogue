import json
import jieba.posseg as pseg

from tqdm import tqdm

import nltk
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.wsd import lesk

# 下载需要的 NLTK 数据包
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('stopwords')


def get_verb_noun_pairs_en(text):
    text = text.lower()
    tokens = word_tokenize(text)
    tagged_tokens = pos_tag(tokens)
    verb_noun_pairs = []
    for i, (word, tag) in enumerate(tagged_tokens):
        if tag.startswith('VB'):
            noun = None
            for j in range(i+1, len(tagged_tokens)):
                if tagged_tokens[j][1] == 'NN':
                    noun = tagged_tokens[j][0]
                    break
            if noun:
                verb_noun_pairs.append((word, noun))
    return verb_noun_pairs


def get_verb_noun_pairs_zh(text):
    words = pseg.cut(text)
    word_list = list(words)

    verb_noun_pairs = []

    for i, (word, flag) in enumerate(word_list):
        if 'v' in flag:  # 识别动词
            for j in range(i + 1, len(word_list)):
                noun, noun_flag = word_list[j]
                if 'n' in noun_flag:  # 识别名词
                    verb_noun_pairs.append((word, noun))
                    break  # 配对成功后跳出当前循环，继续寻找下一个动词

    return verb_noun_pairs

def get_verb_noun_count(datas, language='en'):
    verb_noun_pairs = {}
    for data in tqdm(datas, desc=f"Extracting verb-noun pairs in {language}"):
        # print(data)
        if data["history"] != []:
            instructions = [h[0] for h in data["history"]]
        else:
            instructions = []
        instructions.append(data["instruction"])
        for instruction in instructions:
            if language == 'en':
                pairs = get_verb_noun_pairs_en(instruction)
            elif language == 'zh':
                pairs = get_verb_noun_pairs_zh(instruction)
            for pair in pairs:
                if pair[0] not in verb_noun_pairs:
                    verb_noun_pairs[pair[0]] = {
                        pair[1]: 1
                    }
                else:
                    if pair[1] not in verb_noun_pairs[pair[0]]:
                        verb_noun_pairs[pair[0]][pair[1]] = 1
                    else:
                        verb_noun_pairs[pair[0]][pair[1]] += 1
    return verb_noun_pairs

def del_n(data):
    for verb in list(data.keys()):
        for noun in list(data[verb].keys()):
            if len(noun) < 3 or noun in {"harry", "voldemort", "sirius", "hermione", "dumbledore", "ron", "hagrid"}:
                del data[verb][noun]
            elif data[verb][noun] == 1:
                del data[verb][noun]
        if not data[verb] or len(verb) <= 3:
            del data[verb]
    sorted_data = {}
    for verb, noun_data in sorted(data.items(), key=lambda x: sum(x[1].values()), reverse=True):
        sorted_noun = {}
        for noun, noun_cout in sorted(noun_data.items(), key=lambda x: x[1], reverse=True):
            sorted_noun[noun] = noun_cout
            if len(sorted_noun) >=4:
                break
        if len(sorted_noun) >1:
            sorted_data[verb] = sorted_noun
    return sorted_data
     
def main():
    SFTDataPath_EN = "../../SFTData/RPA_EN_SFT.json"
    SFTDataPath_CN = "../../SFTData/RPA_SFT.json"
    cn_data = json.load(open(SFTDataPath_CN))
    en_data = json.load(open(SFTDataPath_EN))
    # cn_result = get_verb_noun_count(cn_data, language='zh')
    en_result = get_verb_noun_count(en_data, language='en')
    # cn_result = del_n(cn_result)
    en_result = del_n(en_result)
    # with open('../data/verb_noun_pairs_cn.json', 'w') as f:
    #     json.dump(cn_result, f, ensure_ascii=False, indent=4)
    
    with open('../data/verb_noun_pairs_en.json', 'w') as f:
        json.dump(en_result, f, ensure_ascii=False, indent=4)
    
    
if __name__ == '__main__':
    main()