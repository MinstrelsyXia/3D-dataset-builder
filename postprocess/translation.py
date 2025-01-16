import openai
import requests
import json
import re
from langdetect import detect
import os
import rarfile
from zipfile import ZipFile

# 设置API密钥
openai.api_key = '***'
openai.api_base = "https://api.chatanywhere.com.cn/v1"
deepl_api_key = '***'

# 从文件加载JSON数据
def read_models(file_path):
    models = []
    with open(file_path, 'r', encoding='utf-8') as file:
        # import pdb
        # pdb.set_trace()
        content = file.read()
        # 使用正则表达式分割多个 JSON 对象
        json_objects = re.findall(r'\{.*?\}', content, re.DOTALL)
        for obj in json_objects:
            try:
                models.append(json.loads(obj))
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}\nObject: {obj}")
    return models

def is_english(text):
    try:
        # 检测语言
        language = detect(text)
        return language == 'en'
    except:
        # 捕获检测失败的情况
        return False

# 使用DeepL API翻译为英文
def translate_to_english(text):
    print("in")
    url = "https://api-free.deepl.com/v2/translate"
    data = {
        "auth_key": deepl_api_key,
        "text": text,
        "target_lang": "EN"
    }
    response = requests.post(url, data=data)
    result = response.json()
    print("out")
    return result["translations"][0]["text"]

def get_folder_names(path):
    folder_names = []
    #print(path)
    if path.endswith('.zip'):
        with ZipFile(path, 'r') as z:
            # 获取所有文件夹路径并提取最后一层文件夹名字
            folder_paths = [name for name in z.namelist() if name.endswith('/')]
            folder_names = [os.path.basename(os.path.normpath(folder)) for folder in folder_paths]
            print(folder_names[0],len(folder_names))
    elif path.endswith('.rar'):
        print('rar')
        with rarfile.RarFile(path, 'r') as r:
            print('open')
            # 获取所有文件夹路径并提取最后一层文件夹名字
            folder_paths = [name for name in r.namelist() if name.endswith('/')]
            folder_names = [os.path.basename(os.path.normpath(folder)) for folder in folder_paths]
            print(folder_names[0],len(folder_names))
    else:
        # 处理普通文件夹
        folder_names = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
        print(folder_names[0],len(folder_names))

    return folder_names

def append_to_json_file(model, file_path='translated_models.json'):
    with open(file_path, 'a', encoding='utf-8') as file:
        # 每次写入一个模型时，确保是正确的JSON格式
        file.write(json.dumps(model, ensure_ascii=False, indent=4) + ",\n")

def save_processed_uids(uids, file_path='processed_uids.json'):
    with open(file_path, 'a', encoding='utf-8') as f:
        json.dump(list(uids), f, ensure_ascii=False, indent=4)

def read_uuids(file_path):
    uuids = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 去除每行的前后空白字符（包括换行符）
            uuid = line.strip().strip('"').strip('",')
            if uuid:  # 确保不添加空字符串
                uuids.append(uuid)
    return uuids

json_files = [f for f in os.listdir('E:\机器学习数据集\json') if f.endswith('.jsonl') or ('.json')]
# import pdb
# pdb.set_trace()
processed_uids = read_uuids('processed_uids.json')
# import pdb
# pdb.set_trace()
root_path = r"E:\机器学习数据集\渲染结果"

def find(folder_name, item_path):
    # import pdb
    # pdb.set_trace()
    for json_file in json_files:
        # import pdb
        # pdb.set_trace()
        file_path = os.path.join('E:\机器学习数据集\json', json_file)
        models = read_models(file_path)
        # import pdb
        # pdb.set_trace()
        for model in models:
            #print(model)
            uid = model['uid']
            #print("for model in models")
            if uid == folder_name:
                # import pdb
                # pdb.set_trace()
                if uid not in processed_uids:
                    print("json_path:", file_path)
                    description = model.get('description', '')
                    print("descrption:", description)
                    if description:
                        result = is_english(description)
                        print("result:", result)
                        if not result:
                            translated_description = translate_to_english(description)
                            model['description'] = translated_description
                            print(f"Translated description for model: {model['description']}")
                    model['pic_path'] = item_path
                    append_to_json_file(model)
                    append_to_json_file(uid,'processed_uids.json')
                return
            
if __name__ == "__main__":
    print("loop")

    for item in os.listdir(root_path):
        item_path = os.path.join(root_path, item)
        # import pdb
        # pdb.set_trace()
        print(item_path)
        folder_names = get_folder_names(item_path)
        # import pdb
        # pdb.set_trace()
        print(folder_names)
        for folder_name in folder_names:
            print("folder_name:", folder_name)
            find(folder_name, item_path)
        import pdb
        pdb.set_trace()

    print("Translation process completed.")

