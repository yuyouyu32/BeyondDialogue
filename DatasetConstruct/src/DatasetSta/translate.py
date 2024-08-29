import os
from tqdm import tqdm
import json
from concurrent.futures import ThreadPoolExecutor
from LLMClients import OpenAIClient


TranslateMapPath = "../data/Dict.json"
TranslatePrompt = """Please translate the following Chinese character or speaking style into Chinese, preferably using only one word, there are several examples below:
Input:活泼
Output: brisk
Input:冷漠
Output: indifferent

Now please translate the following Chinese character or speaking style into English, preferably using only one word:
{text}"""

if os.path.exists(TranslateMapPath):
    Dictionary = json.load(open(TranslateMapPath, 'r'))
else:
    Dictionary = {}

Client = OpenAIClient()


def translate_text(text):
    if text in Dictionary:
        return Dictionary[text]
    else:
        messages =  [{
            "role": "user",
            "content": TranslatePrompt.format(text=text)
        }
        ]
        model = 'gpt-4o-mini'
        response, cost = Client.call(messages=messages, model=model, n=1)
        en_text = response[0].lower().strip().replace('output', '').replace(':', '').strip()
        Dictionary[text] = en_text
    return en_text

def translate_words(cn_texts):
    client = OpenAIClient()
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(tqdm(executor.map(translate_text, cn_texts), total=len(cn_texts), desc='Translating'))
    return results