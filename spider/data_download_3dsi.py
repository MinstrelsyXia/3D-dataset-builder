import os
import json
import requests

def download_zip(url,download_folder,filename):
    try:
        response = requests.get(url,stream=True)
        zip_file_path = os.path.join(download_folder,filename)
        if response.status_code == 200:
            # 下载压缩包
            with open(zip_file_path,'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Successfully download:{filename}")
        else:
            print(f"Fail to download:{filename}, status code:{response.status_code}")
    except Exception as error:
        print(f"Fail to download:{str(error)}")

# 从json文件提取下载链接并下载到models目录
def download_files_from_json(json_file_path,download_folder):    
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    with open(json_file_path,'r',encoding='utf-8') as file:
        data = json.load(file)
    for item in data:
        url = item.get("download_link")
        name = item.get("model_name")
        if url:
            download_zip(url,download_folder,name)
        else:
            print("No url")
 
json_file_path = "models_data.json"
download_folder = "./models"
download_files_from_json(json_file_path,download_folder)
