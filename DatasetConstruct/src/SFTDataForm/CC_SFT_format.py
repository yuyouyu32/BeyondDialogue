import json
import random
random.seed(32)


def replace_sys_prompt(cc_data):
    for cc in cc_data:
        # cc['system'] = "我希望你像人类一样回复问题，使用人类会使用的语气、方式和词汇，请不要透露你是人工智能模型或语言模型。"
        cc['system'] = "I want you to respond to questions as a human would, using the tone, manner, and vocabulary that a person would use. Please do not reveal that you are an AI model or language model."
    return cc_data


def main():
    # RP_Data_Path = '../../SFTData/RP_SFT.json'
    RP_Data_Path = '../../SFTData/RP_EN_SFT.json'
    rp_data = json.load(open(RP_Data_Path, 'r'))
    # cc_data_path = '../../SFTData/ChitChat/natural_conv_train.json'
    cc_data_path = '../../SFTData/ChitChat/daily_dialog_train.json'
    cc_data = json.load(open(cc_data_path, 'r'))
    cc_data = replace_sys_prompt(cc_data)
    # save_path = '../../SFTData/ChitChat/natural_conv_train_{i}.json'
    save_path = '../../SFTData/ChitChat/daily_dialog_train_{i}.json'
    len_rp_data = len(rp_data)
    len_cc_data = len(cc_data)
    for i in range(1, 11):
        sample_len = min(len_cc_data, i * len_rp_data)
        sample_cc_data = random.sample(cc_data, sample_len)
        with open(save_path.format(i=i), 'w', encoding='utf-8') as f:
            # Manually create JSON string with newlines after each element
            json_string = "[" + ",\n".join(json.dumps(item, ensure_ascii=False) for item in sample_cc_data) + "]"
            f.write(json_string)        

# python -m SFTDataForm.CC_SFT_format
if __name__ == "__main__":
    main()