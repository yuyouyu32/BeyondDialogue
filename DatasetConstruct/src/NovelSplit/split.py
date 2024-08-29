import re
import tiktoken
from typing import List, Tuple
enc = tiktoken.get_encoding("cl100k_base")


def _divide_str(s, sep=['\n', '.', '。']):
    mid_len = len(s) // 2
    best_sep_pos = len(s) + 1
    best_sep = None
    for curr_sep in sep:
        sep_pos = s.rfind(curr_sep, 0, mid_len)
        if sep_pos > 0 and abs(sep_pos - mid_len) < abs(best_sep_pos -
                                                        mid_len):
            best_sep_pos = sep_pos
            best_sep = curr_sep
    if not best_sep:
        return s, ''
    return s[:best_sep_pos + 1], s[best_sep_pos + 1:]


def _strong_divide(s):
    left, right = _divide_str(s)

    if right != '':
        return left, right

    whole_sep = ['\n', '.', '，', ',', ';', ',', '；',\
                 '：', '！', '？', '(', ')', '”', '“', \
                 '’', '‘', '[', ']', '{', '}', '<', '>', \
                 '/', '\'', '|', '-', '=', '+', '*', '%', \
               '$', '#', '@', '&', '^', '_', '`', '~',\
                 '·', '…']
    left, right = _divide_str(s, sep=whole_sep)

    if right != '':
        return left, right

    mid_len = len(s) // 2
    return s[:mid_len], s[mid_len:]


def chapter_split(raw_text: str) -> List[str]:
    '''
    Split the raw text into chapters
    
    Parameters:
        raw_text: the raw text of the novel
    Returns:
        chapters: a list of strings, each string is a chapter of the novel
    '''
    chapters = []
    chapter_contents = []
    splitters = {"章", "节", "回", "卷", "部", "篇", "集", "幕", "折", "场", "段", "曲", "文"}
    splitter_pattern = f"第[0-9一二三四五六七八九十百千万]+[{'' .join(splitters)}]"
    min_chapter_length = 500

    for line in raw_text.split('\n'):
        match = re.search(splitter_pattern, line)
        if match:
            if len('\n'.join(chapter_contents)) < min_chapter_length and chapters:
                chapters[-1] += '\n' + '\n'.join(chapter_contents) + '\n' + line
                chapter_contents = []
            else:
                if chapter_contents:
                    chapters.append('\n'.join(chapter_contents))
                chapter_contents = [line]
        else:
            chapter_contents.append(line)

    if chapter_contents:
        chapters.append('\n'.join(chapter_contents))
        
    return chapters

def _remove_superset_elements(names: List[str]) -> Tuple[str]:
    '''
    Remove the superset elements in the list of names to avoid double counting of occurrences.

    Parameters:
        names: a list of strings, each string is a name of a character
    Returns:
        final_set: a set of strings, each string is a name of a character
    '''
    sorted_elements = sorted(names, key=len, reverse=True)
    to_remove = set()
    for i in range(len(sorted_elements)):
        for j in range(i + 1, len(sorted_elements)):
            if sorted_elements[j] in sorted_elements[i]:
                to_remove.add(sorted_elements[i])
                break
    final_set = set(sorted_elements) - to_remove
    return final_set

def split_chunks(chapters: List[str], names: List[str] = [], min_appear_times:int = 3, max_token_len: int = 1500) -> List[Tuple[int, str]]:
    '''
    Split the chapters into chunks of text with a maximum token length and a minimum number of appearances of the names of the characters.
    
    Parameters:
        chapters: a list of strings, each string is a chapter of the novel
        names: a list of strings, each string is a name of a character
        min_appear_times: the minimum number of appearances of the names of the characters
        max_token_len: the maximum token length of the chunks
    Returns:
        chunk_texts: a list of tuples, each tuple contains a chapter id and a chunk of text with a maximum token length and a minimum number of appearances of the names of the characters
    '''
    names = _remove_superset_elements(names)
    chunk_texts = []
    for chapter_id, chapter in enumerate(chapters):
        lines = chapter.split('\n')
        split_texts = []
        def split_and_append(text, max_len):
            # Recursively split the text into smaller parts, keep the order of the text
            if len(enc.encode(text)) <= max_len:
                split_texts.append(text)
                return
            left, right = _strong_divide(text)
            split_and_append(left, max_len)
            split_and_append(right, max_len)
            
        max_token_len_adjusted = max_token_len - 15
        for line in lines:
            if len(enc.encode(line)) <= max_token_len - 5:
                split_texts.append(line)
            else:
                split_and_append(line, max_token_len_adjusted)
                
        curr_len = 0
        curr_chunk = ''
        for line in split_texts:
            line = line.strip()
            line_len = len(enc.encode(line))

            if line_len > max_token_len:
                print('warning line_len = ', line_len)

            if curr_len + line_len <= max_token_len:
                curr_chunk += line
                curr_chunk += '\n'
                curr_len += line_len
                curr_len += 1
            else:
                if sum(curr_chunk.count(item) for item in names) >= min_appear_times:
                    curr_chunk = re.sub(r'\n+', '\n', curr_chunk)
                    curr_chunk = curr_chunk.strip()
                    chunk_texts.append((chapter_id, curr_chunk))
                curr_chunk = line
                curr_chunk += '\n'
                curr_len = line_len
        if curr_chunk.replace('\n', ''):
            if sum(curr_chunk.count(item) for item in names) >= min_appear_times:
                curr_chunk = re.sub(r'\n+', '\n', curr_chunk)
                curr_chunk = curr_chunk.strip()
                chunk_texts.append((chapter_id, curr_chunk))
    return chunk_texts


def novel_split(raw_text: str, names: List[str], min_appear_times:int = 3, max_token_len: int = 1500) -> List[str]: 
    '''
    Split the raw text of the novel into chunks of text with a maximum token length and a minimum number of appearances of the names of the characters.
    
    Parameters:
        raw_text: the raw text of the novel
        names: a list of strings, each string is a name of a character
        min_appear_times: the minimum number of appearances of the names of the characters
        max_token_len: the maximum token length of the chunks
    Returns:
        chunk_texts: a list of strings, each string is a chunk of text with a maximum token length and a minimum number of appearances of the names of the characters
    '''
    chapters = chapter_split(raw_text)
    names = _remove_superset_elements(names)
    return split_chunks(chapters, names, min_appear_times, max_token_len)

def novel_split_sort_with_appear_times(raw_text: str, names: List[str], min_appear_times: int = 3, max_token_len: int = 1500) -> List[Tuple[str, int]]:
    '''
    Split the raw text of the novel into chunks of text with a maximum token length and a minimum number of appearances of the names of the characters, and return the chunks with the number of appearances of the names of the characters.
    
    Parameters:
        raw_text: the raw text of the novel
        names: a list of strings, each string is a name of a character
        min_appear_times: the minimum number of appearances of the names of the characters
        max_token_len: the maximum token length of the chunks
    Returns:
        chunk_texts: a list of tuples, each tuple contains a chunk of text and the number of appearances of the names of the characters
    '''
    chapters = chapter_split(raw_text)
    names = _remove_superset_elements(names)
    chunk_texts = split_chunks(chapters, names, min_appear_times, max_token_len)
    chunk_texts_with_appear_times = [(chunk, sum(chunk.count(item) for item in names)) for chunk in chunk_texts]
    # sort the chunks by the number of appearances of the names of the characters
    chunk_texts_with_appear_times.sort(key=lambda x: x[1], reverse=True)
    # only return chunks
    chunk_texts = [item[0] for item in chunk_texts_with_appear_times]
    return chunk_texts
    
# python -m NovelSplit.split
def main():
    import pandas as pd
    import os
    from tqdm import tqdm
    import json
    role_data = pd.read_excel('../data/Roles Info.xlsx')
    role_data.fillna('-', inplace=True)
    novel_path = '../../NovelData/novels'
    role_save_path = '../../NovelData/roles'
    if not os.path.exists(role_save_path):
        os.makedirs(role_save_path)
    novel_chunks_path = '../../NovelData/novel_chunks'
    if not os.path.exists(novel_chunks_path):
        os.makedirs(novel_chunks_path)
    min_appear_times = 6
    max_token_len = 2000
    for index, row in tqdm(role_data.iterrows(), total=role_data.shape[0]):
        novel_file = row['文件路径']
        novel_name = novel_file.split('/')[-1].strip('.txt')
        novel_file_path = os.path.join(novel_path, novel_file)
        if os.path.exists(novel_file_path):
            with open(novel_file_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            if len(raw_text) < max_token_len:
                print(f"role: {row['所属作品']} {row['姓名']} novel file {novel_file_path} too short, droped")
                continue
            names = set()
            names.update(row['姓名'].split("、"))
            if not pd.isna(row['别称']):
                names.update(row['别称'].split("、"))
            if not pd.isna(row['搜索名称']):
                names.update(row['搜索名称'].split("、"))
            if '' in names:
                names.remove('') 
            if '-' in names:
                names.remove('-')
            names = _remove_superset_elements(list(names))
            novel_chunks = []
            novel_chunks_file_pth = os.path.join(novel_chunks_path, f'{novel_name}_chunks.jsonl')
            if not os.path.exists(novel_chunks_file_pth):
                novel_chunks = novel_split(raw_text, names=list(names), min_appear_times=-1, max_token_len=max_token_len)
                with open(novel_chunks_file_pth, 'w', encoding='utf-8') as f:
                    for index, chunk in enumerate(novel_chunks):
                        f.write(json.dumps({'id': index, 'chap_id': chunk[0],'chunk': chunk[1]}, ensure_ascii=False) + '\n')
            else:
                with open(novel_chunks_file_pth, 'r') as f:
                    novel_chunks = [(json.loads(line.strip())['chap_id'], json.loads(line.strip())['chunk']) for line in f]
            # chunk_texts = novel_split(raw_text, names=list(names), min_appear_times=min_appear_times, max_token_len=max_token_len)
            chunks = []
            for index, chunk in enumerate(novel_chunks):
                if sum(chunk[1].count(item) for item in names) >= min_appear_times:
                    chunks.append({
                        'id': index,
                        'chap_id': chunk[0],
                        'chunk': chunk[1]
                    })
            role_dict = row.to_dict()
            role_dict['min_appear_times'] = min_appear_times
            role_dict['max_token_len'] = max_token_len
            role_dict['chunks'] = chunks
            role_dict['chunk_nums'] = len(chunks)
            role_file_name = f'{row["姓名"]}.json'
            if not os.path.exists(os.path.join(role_save_path, novel_name)):
                os.makedirs(os.path.join(role_save_path, novel_name))
            role_file_path = os.path.join(role_save_path, novel_name, role_file_name)
            with open(role_file_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(role_dict, ensure_ascii=False, indent=4))
        else:
            if novel_name != '-':
                print(f"role: {row['所属作品']} {row['姓名']} novel file {novel_file_path} not exists")
# python -m NovelSplit.split
if __name__ == '__main__':
    main()
