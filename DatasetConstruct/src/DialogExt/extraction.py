import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Tuple, Union, Set

from kor.encoders import initialize_encoder
from kor.extraction import create_extraction_chain
from kor.extraction.parser import KorParser
from kor.nodes import Object
from langchain.chains import LLMChain
from langchain_community.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI
from tqdm import tqdm
from utils import collect_roles, get_novel_chunks_dict

from LLMClients import Cost, OpenAIClient

schema_parse = Object(
    id="script",
    attributes=[]
)
encoder = initialize_encoder('csv', schema_parse)
OutputParser=KorParser(encoder=encoder, validator=None, schema_=schema_parse)


NovelRootPath = '../../NovelData/novel_chunks'
RoleRootPath = '../../NovelData/roles'
DialogExtPath = '../../NovelData/dialogues'
MaxWorkers = 8

def prompt_extraction(prompt: str, llm: Union[OpenAIClient], model: str) -> Tuple[Union[str, List[Dict]], Cost]:
    """
    Extract the script from the chunk of text using the LLM.

    Parameters:
        prompt: a string, the prompt for the extraction
        llm: a GZClient, OpenAIClient, or AsyncOpenAIClient, the LLM to use for the extraction
    Returns:
        response: List of Dict or String. Success: List of Dict, Error: String. The extracted script or raw response from LLM.
        cost: an int, the cost of the extraction
    """
    # rsp, cost = llm.call([{"role": "system", "content": "You are a helpful assistant"}, {"role": "user", "content": prompt}], model=model, n=1)
    rsp, cost = llm.call([{"role": "user", "content": prompt}], model=model, n=1)
    rsp = rsp[0].replace('Output:', '')
    rsp = '\n'.join([line for line in rsp.split('\n') if '|' in line])
    rsp = OutputParser.parse(rsp)
    response = rsp['data']
    errors = rsp['errors']
    if not errors: 
        return response['script'], cost
    else:
        return rsp['raw'], cost  


def kor_extraction(chunk: str, chain: LLMChain) -> Tuple[Union[str, List[Dict]], float]:
    """
    Extract the script from the chunk of text using the LLMChain.

    Parameters:
        chunk: a string, the chunk of text
        chain: an LLMChain, the LLMChain to use for the extraction
    Returns:
        response: List of Dict or String. Success: List of Dict, Error: String. The extracted script or raw response from LLM.
        cost: an int, the cost of the extraction
    """
    with get_openai_callback() as cb:
        rsp = chain.invoke( f"{chunk}" )
        response = rsp['text']['data']
        errors = rsp['text']['errors']
        cost = cb.total_cost
    if not errors: 
        return response['script'], cost
    else:
        return rsp['text']['raw'], cost


def _parse_config(config: Dict[str, str]) -> Tuple[Union[OpenAIClient, LLMChain], Union[str, None]]:
    """
    Parse the configuration for the extraction method.
    """
    if config['method'] == 'prompt':
        if config['language'] == 'cn':
            from DialogExt.prompts import prompt_cn as prompt_template
        else:
            from DialogExt.prompts import prompt_en as prompt_template

        if config['model'] == 'deepseek-chat':
            llm = OpenAIClient(client_type='deepseek')
        elif config['model'] == 'yi-large-preview':
            llm = OpenAIClient(client_type='01-AI')
        else:
            llm = OpenAIClient(client_type='openAI')
        return llm, prompt_template
    elif config['method'] == 'kor':
        if config['language'] == 'cn':
            from DialogExt.KorSchema import schema_cn as schema
        else:
            from DialogExt.KorSchema import schema_en as schema
        if config['model'] == 'deepseek-chat':
            llm = ChatOpenAI(
                model_name = config['model'],
                base_url='https://api.deepseek.com',
                api_key='sk-6ff66dcc5a424a18bd5b06c7d1930583'
            )
        else:
            llm = ChatOpenAI(
                model_name = config['model'],
                base_url = 'http://api-skynetyu.woa.com/v1/chat/completions',
                api_key = 'shediaoNpc#2023@LSTC',
                )
        chain = create_extraction_chain(llm, schema)
        return chain, None

def process_chunk(chunk: str, config: Dict[str, str], llm, prompt_template):
    if config['method'] == 'prompt':
        task_prompt = prompt_template.format(user_input=chunk)
        response, cost = prompt_extraction(task_prompt, llm, config['model'])
        return response, cost, chunk, task_prompt
    elif config['method'] == 'kor':
        response, cost = kor_extraction(chunk, llm)
        return response, cost, chunk, llm.prompt.format_prompt(text=chunk).to_string()
    else:
        raise ValueError(f"Invalid method: {config['method']}")

def novel_extractor(chunks: List[str], config: Dict[str, str]) -> List[Tuple[List[Dict[str, str]], Union[float, Cost], str, str, int]]:
    """
    Extract the script from the chunks of text using the LLM.

    Parameters:
        chunks: a list of strings, the chunks of text
        config: a dictionary, the configuration for the extraction method.
            config['method']: a string, the method for the extraction. 'prompt' or 'kor' or 'cw'
            config['language']: a string, the language for the extraction. 'cn' or 'en'
            config['model']: a string, the model for the `prompt` and `kor` method. `gpt-4-turbo` or `gpt-3.5-turbo` or `main`

    Return:
        Tuple of the response (List of Dict or String) and the cost (float). The extracted script or raw response from LLM, and the extraction cost.
    """
    llm, prompt_template = _parse_config(config)
    
    results = []

    def process_chunk_with_index(chunk, index):
        result = process_chunk(chunk, config, llm, prompt_template)
        return result + (index,)

    with ThreadPoolExecutor(max_workers=MaxWorkers) as executor:
        futures = [executor.submit(process_chunk_with_index, chunk, idx) for idx, chunk in enumerate(chunks)]

        for future in tqdm(futures, total=len(chunks), desc=f"Processing chunks with {config['model']} {config['method']}"):
            results.append(future.result())

    return results

def pre_process_roles():
    """
    Preprocess the roles for the extraction of dialogues.
    """
    novel_chunks = get_novel_chunks_dict(NovelRootPath)
    role_files = collect_roles(RoleRootPath)
    for role_file in tqdm(role_files, desc='Preprocess chunks for Dialogues Extraction'):
        with open(role_file, 'r') as f:
            role = json.load(f)
        # Remove specified keys
        role.pop('chunk_nums', None)
        role.pop('min_appear_times', None)
        role.pop('max_token_len', None)
        names = set()  
        names.update(role['姓名'].split("、"))
        names.update(role['别称'].split("、"))
        names.update(role['搜索名称'].split("、"))
        if '' in names: names.remove('') 
        if '-' in names: names.remove('-')
        role['names'] = list(names)
        novel_name = role['文件路径'].split('/')[-1].split('.')[0]
        chunks = role.pop('chunks', None)
        
        # Sort the chunks by score
        if chunks:
            chunks = sorted(chunks, key=lambda x: x['score'], reverse=True)
        ext_chunks = {}
        # Extract the chunks
        for index, chunk in enumerate(chunks):
            id = chunk['id']
            # last_id, next_id = max(0, id-1), id+1
            # last_chunk, next_chunk = novel_chunks[novel_name].get(last_id, None), novel_chunks[novel_name].get(next_id, None)
            chunk = novel_chunks[novel_name][id]
            # if last_chunk:
            #     ext_chunks[last_id] = last_chunk
            ext_chunks[id] = chunk
            # if next_chunk:
            #     ext_chunks[next_id] = next_chunk
            if index >= 30:
                break
        # Save the file to be extracted
        ext_chunks = [ext_chunks[key] for key in sorted(ext_chunks.keys())]
        role['chunks_with_dialogues'] = ext_chunks
        novel_save_path = os.path.join(DialogExtPath, novel_name)
        if not os.path.exists(novel_save_path):
            os.makedirs(novel_save_path)     
        with open(os.path.join(novel_save_path, f"{role['姓名']}.json"), 'w') as f:
            f.write(json.dumps(role, ensure_ascii=False, indent=4))


def process_dialog_names(role_name: str, names: Set[str], dialogs: Union[List[Dict], str]) -> Union[List[Dict], str]:
    if type(dialogs) == str:
        return dialogs
    for dialog in dialogs:
        if dialog['role'] in names:
            dialog['role'] = role_name
    return dialogs
    
def main():
    role_files = collect_roles(DialogExtPath)
    all_cost = Cost()
    for role_file in tqdm(role_files, desc="Extract Roles' Dialogues from Chunks"):
        with open(role_file, 'r') as f:
            role = json.load(f)
            
        if len(role['chunks_with_dialogues']) == 0:
            print(f"Skip {role_file} with no dialogues")
            continue
        
        if 'dialogues' in role['chunks_with_dialogues'][-1]:
            print(f"Skip {role_file} with dialogues extracted")
            continue 
        
        chunks = [chunk['chunk'] for chunk in role['chunks_with_dialogues']]
        config = {
            'method': 'prompt',
            'language': 'cn',
            'model': 'gpt-4-turbo'
        }
        results = novel_extractor(chunks, config)
        role_cost = Cost()
        all_dialogues = []
        for dialogs, cost, chunk, prompt, index  in results:
            curr_dialogue = role['chunks_with_dialogues'][index]
            curr_dialogue['dialogues'] = process_dialog_names(role['姓名'], role['names'], dialogs)
            curr_dialogue['cost'] = dict(cost)
            curr_dialogue['model'] = config['model']
            all_dialogues.append(curr_dialogue)
            role_cost += cost
        role['chunks_with_dialogues'] = all_dialogues
        print(f"Cost for {role['姓名']}: {role_cost}")
        with open(role_file, 'w') as f:
            f.write(json.dumps(role, ensure_ascii=False, indent=4))
        print(f"Processed {role_file}")
        all_cost += role_cost
    print(f"Total Cost: {all_cost}")


# python -m DialogExt.extraction
# nohup python -m DialogExt.extraction > ../logs/extraction.log 2>&1 &
if __name__ == '__main__':
    main()