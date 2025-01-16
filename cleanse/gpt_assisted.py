import json
import os
import openai
import shutil
import re
import numpy as np

# 定义文件路径和API
models_path = r"D:\store\ToBeCleaned\cjy\0_299"  # 包含 .glb 和 .obj 文件的文件夹路径
json_path = r"D:\store\ToBeCleaned\cjy\existing_models.jsonl"  # 包含模型信息的 JSON或JSONL 文件路径
cleaned_json_path = r"D:\store\ToBeCleaned\cjy\cjy_cleaned_models.json"  # 清洗后的json文件保存路径
deleted_models_path = r"D:\store\ToBeCleaned\cjy\deleted_models"  # 被删除模型的保存路径
deleted_json_path = r"D:\store\ToBeCleaned\cjy\cjy_deleted_models.json"  # 被删除模型信息的 JSON 文件路径
openai.api_key = "sk-fTYanC4HhsI1rXeFe5uH3nZfYvITQFziyogfNsTthufRuGMe" #你的api-key
openai.api_base = "https://api.chatanywhere.com.cn/v1" #不用改


# 读取JSONL文件

def read_jsonl(file_path):
    models = []
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # 使用正则表达式分割多个 JSON 对象
        json_objects = re.findall(r'\{.*?\}', content, re.DOTALL)
        for glb in json_objects:
            try:
                models.append(json.loads(glb))
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}\nObject: {glb}")
    return models

# 读取JSON文件

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            data = None
    return data

# 根据文件类型读取文件

def read_models(file_path):
    _, file_extension = os.path.splitext(file_path)
    if file_extension == '.jsonl':
        return read_jsonl(file_path)
    elif file_extension == '.json':
        return read_json(file_path)
    else:
        print(f"Unsupported file extension: {file_extension}")
        return None

# 读取模型信息
models = read_models(json_path)

# 根据 UID 查找对应的模型信息

def get_model_info(uid):
    for model in models:
        if model['uid'] == uid:
            return model
    return None

# 将合格的模型条目追加到新的 JSON 文件

def append_to_json(valid_model_entry):
    try:
        if os.path.exists(cleaned_json_path):
            with open(cleaned_json_path, 'r+') as f:
                try:
                    current_data = json.load(f)
                except json.JSONDecodeError:
                    print(
                        "JSON file is empty or corrupt, initializing with an empty list.")
                    current_data = []

                current_data.append(valid_model_entry)
                f.seek(0)
                json.dump(current_data, f, indent=4)
                f.truncate()
            print(f"Appended entry to {cleaned_json_path}")
        else:
            print(f"File {cleaned_json_path} does not exist.")
    except Exception as e:
        print(f"Error appending to JSON file: {e}")

# 使用 GPT API 筛选模型
# openai.api_key = "sk-fTYanC4HhsI1rXeFe5uH3nZfYvITQFziyogfNsTthufRuGMe"
# openai.api_base = "https://api.chatanywhere.com.cn/v1"
# 定义分类函数，每次处理 5 个模型

def categorize_relics(descriptions, object_names):
    batch_request = ""
    for i in range(len(descriptions)):
        batch_request += f"Model {i+1}: description '{descriptions[i]}' and object name '{object_names[i]}'.\n"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"According to the following descriptions and object names, categorize each as: human bone or its model, decorative items, artworks, sculptures, cultural relics or antiques(1), real plants(2), real animals or animal skeletons(3), buildings or architectural models(4), or none of them(5). For example, masks, badges and stones should be categorized as 1. Any ancient items or those from museums should also be categorized as 1, souvenirs should be categorized as 1. Objects made of bronze, stone or clay should be categorized as 1. Clothes, caps, chairs should be categorized as 5: \n{batch_request}\n. Please provide the category index for each model in the form like Model 2: 1."
                }
            ],
            max_tokens=2000,
            temperature=0.2
        )

        # 输出分类结果
        category_indices = response.choices[0].message['content'].strip().split(
            "\n")
        print(f"Category indices: {category_indices}")
        return category_indices

    except Exception as e:
        print(f"Error: {e}")
        return None

# 删除模型文件及其信息，并保存到指定文件夹和 JSON 文件中

def delete_model(model_path, uid, deleted_models_info):
    try:
        if not os.path.exists(deleted_models_path):
            os.makedirs(deleted_models_path)

        # 移动文件
        shutil.move(model_path, os.path.join(
            deleted_models_path, os.path.basename(model_path)))

        # 添加到被删除模型的信息
        for model in models:
            if model['uid'] == uid:
                deleted_models_info.append(model)  # 保存被删除的模型信息
                models.remove(model)
                print(f"Deleted entry with UID: {uid} from JSON.")
                return
        print(f"UID: {uid} not found in JSON.")
    except Exception as e:
        print(f"Error deleting entry from JSON: {e}")

# 保存被删除模型信息的 JSON 文件

def save_deleted_models(deleted_models_info):
    try:
        with open(deleted_json_path, 'w') as f:
            json.dump(deleted_models_info, f, indent=4)
        print(f"Deleted models information saved to {deleted_json_path}")
    except Exception as e:
        print(f"Error saving deleted models information: {e}")

# 主程序
model_files = sorted([file for file in os.listdir(models_path)
                      if file.endswith('.glb') or file.endswith('.obj')])
total_files = len(model_files)
processed_files = 0
remaining_files = total_files
batch_size = 5
deleted_models_info = []  # 用于保存被删除模型的信息

for i in range(0, len(model_files), batch_size):
    batch_files = model_files[i:i + batch_size]
    descriptions = []
    object_names = []
    uids = []

    for model_file in batch_files:
        # 获取 UID（假设 UID 是文件名的一部分）
        uid = os.path.splitext(model_file)[0]
        model_info = get_model_info(uid)

        if model_info:
            descriptions.append(model_info.get('description', ''))
            object_names.append(model_info.get('model name', ''))
            uids.append(uid)
        else:
            print(f"Model with UID {uid} not found in JSON.")

    if descriptions:
        category_indices = categorize_relics(descriptions, object_names)

        if category_indices:
            for j in range(len(category_indices)):
                model_file = batch_files[j]
                model_info = get_model_info(uids[j])

                category_index = category_indices[j].split(':')[-1].strip()
                print("index=", category_index)

                # 根据类别更新状态数组
                if category_index == "1":
                    append_to_json(model_info)
                else:
                    model_path = os.path.join(models_path, model_file)
                    delete_model(model_path, uids[j], deleted_models_info)
                    print(f"模型名称: {object_names[j]} 被删除，因其不属于文物类别。")
                    remaining_files -= 1

                processed_files += 1

        print(f"Processing files {processed_files}/{total_files}")

# 保存被删除的模型信息到 JSON 文件
save_deleted_models(deleted_models_info)

print(
    f"\nProcessing complete. Remaining files: {remaining_files}/{total_files}")
