import selenium
import requests
import os
import time
import json
import random
import uuid
import shutil
import regex
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException,ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

def scroll_page():
    body = browser.find_element(By.TAG_NAME, 'body')
    body.send_keys(Keys.PAGE_DOWN)
    # 随机等待时间，模拟人类行为
    time.sleep(random.uniform(1.5, 3.0))

def generate_uid(input_str):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, input_str))

def find_file_move(model_name: str, uid: str, destination_folder='models', download_address="C:/Users/cyd/Downloads", max_attempts=50, delay=3):

    destination_path = os.path.join(destination_folder, f"{uid}.glb")

    for attempt in range(max_attempts):
        try:
            while True:
                file_names = os.listdir(download_address)
                if file_names:
                    break
                time.sleep(delay)

            source_path = os.path.join(download_address, file_names[0])
            shutil.move(source_path, destination_path)
            print(f"Moved to {destination_path}")
            time.sleep(10)
            for file_name in os.listdir(download_address):
                file_path = os.path.join(download_address, file_name)
                if os.path.isfile(file_path):
                    os.unlink(file_path)

            return True

        except PermissionError:
            print(f"Attempt {attempt + 1}: File is still in use. Retrying in {delay} seconds...")
            time.sleep(delay)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

        print(f"Failed to move file after {max_attempts} attempts.")
    return False

# 0、准备工作

# 1、用户输入
catagory = input('请输入想要查询的类别(art):')
item = input('请输入想要查询的具体物品(ceramics):')

# 2、构造网址
url = f'https://poly.cam/explore?tags={catagory}&feed=top&search={item}'
# ceramics / bronze / dynasty / ancient / antique / culture

# 3、打开浏览器
chrome_options = Options()
# 3.1、设置浏览器的偏好设置
chrome_options.page_load_strategy = 'eager' #增加界面加载速度，在DOM内容加载完成后立即返回，不必等所有资源（eg：图像）加载完成
chrome_options.add_argument('--disable-gpu') #禁止GPU加速，提高稳定性
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-blink-features=AutomationControlled") #防止网站检测到selenium
chrome_options.add_experimental_option('excludeSwitches',['enable-automation']) #关闭在浏览器中显示自动化控制的标识，防止网站检测
browser = webdriver.Chrome(options=chrome_options)

# 4、加载需要查找的模型页面
browser.get(url)
wait = WebDriverWait(browser,180)
wait.until(EC.presence_of_all_elements_located((By.XPATH, "/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div")))
browser.maximize_window()
time.sleep(5)

# 4.1、log in
button_log_in = WebDriverWait(browser,10).until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[1]/div[2]/nav/div/div/div[7]/div/div/button[1]")))
button_log_in.click()
time.sleep(5)
button_email = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[3]/div/div/div/div[2]/div[2]/div/div[3]/div/button[1]")))
button_email.click()
time.sleep(5)
input1 = WebDriverWait(browser,10).until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[3]/div/div/div/div[4]/div/div[1]/form/div[1]/div[1]/div/div/input")))
input1.send_keys('your email address')
input2 = WebDriverWait(browser,10).until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[3]/div/div/div/div[4]/div/div[1]/form/div[1]/div[2]/div/div/div/div/input")))
input2.send_keys('your password')
button = browser.find_element(By.XPATH,"/html/body/div[3]/div/div/div/div[4]/div/div[1]/form/div[2]/button")
button.click()
wait.until(EC.presence_of_all_elements_located((By.XPATH,"/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div")))
time.sleep(30)

# 5、对于每一个模型，爬取模型名并下载
model_download = 0
iter_num = 0
while(True): 
    time.sleep(10)                                                                              
    models = WebDriverWait(browser,60).until(EC.presence_of_all_elements_located((By.XPATH,"/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div")))
    new_model = 0
    print(len(models))
    if len(models) <= 16:
        start = 0
    else:
        start = len(models) - 16
    for i in range(start,len(models)):
        time.sleep(2)
        print(i)
        xpath_name = f"/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div[{i+1}]/div/div[1]/div/a/div/img"
        model_name_ = WebDriverWait(browser,30).until(EC.presence_of_element_located((By.XPATH,xpath_name)))
        model_name = model_name_.get_attribute('alt')
        print("model_name:",model_name)
        xpath_url = f"/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div[{i+1}]/div/div[1]/div/a"
        model_url = WebDriverWait(browser,30).until(EC.presence_of_element_located((By.XPATH,xpath_url))).get_attribute('href')
        print("model_url:",model_url)
        model_uid = generate_uid(model_url)
        print("model_uid:",model_uid)
        xpath_decription = f"/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div[{i+1}]/div/div[2]/div[2]/button"
        button_description = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.XPATH,xpath_decription)))
        button_description.click()
        try:
            description = WebDriverWait(browser,30).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[3]/div/div/div/div[4]/div/div/span[1]"))).text
            print("description:",description)
        except TimeoutException:
            description = None
            print("no description")
        button_quit2 = WebDriverWait(browser,10).until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[3]/div/div/div/div[1]/div[3]/button")))
        button_quit2.click()
        time.sleep(2)
        xpath_save = f"/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div[{i+1}]/div/div[2]/div[2]/div[1]/button"
        buttons = WebDriverWait(browser,60).until(EC.presence_of_all_elements_located((By.XPATH,f"/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div[{i+1}]/div/div[2]/div[2]/div")))
        button_num = len(buttons)
        if button_num == 1:
            print(model_name," no download link\n")
            continue    
        button_save_capture = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.XPATH,xpath_save)))
        button_save_capture.click()
        time.sleep(2)
        xpath_check = f"/html/body/div[3]/div/div/div/div[5]/div/div/label/div/input"
        try:
            button_check = WebDriverWait(browser,10).until(EC.element_to_be_clickable((By.XPATH,xpath_check)))
        except TimeoutException:
            button_quit1 = WebDriverWait(browser,60).until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[3]/div/div/div/div[1]/div[3]/button")))
            button_quit1.click()
            time.sleep(1)
            print(model_name," already saved\n")
            continue
        button_check.click()
        time.sleep(2)
        new_model += 1
        xpath_download = f"/html/body/div[3]/div/div/div/div[5]/div/button/span"
        button_save_and_download = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.XPATH,xpath_download)))
        button_save_and_download.click()
        time.sleep(5)
        xpath_choices = f"/html/body/div[3]/div/div/div/div[4]/div[3]/div/div[1]/button/div[2]/span[1]"
        try:
            choices = WebDriverWait(browser,360).until(EC.presence_of_all_elements_located((By.XPATH,xpath_choices)))
        except TimeoutException:
            print(model_name," no download links\n")
            continue
        my_buttons = [choice for choice in choices if choice.text == 'GLTF']  
        if my_buttons:
            my_buttons[0].click()
            time.sleep(2)
            xpath_download_real = f"/html/body/div[3]/div/div/div/div[4]/div[4]/div/button"
            download_button_real = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.XPATH,xpath_download_real)))
            download_button_real.click()
            wait.until(EC.element_to_be_clickable((By.XPATH,xpath_download_real)))
            model_data = {
                    "model name":model_name,
                    "description":description,
                    "download_link":model_url,
                    "uid":model_uid
                }
            model_download += 1
            time.sleep(2)
            is_moved=find_file_move(model_name=model_name,uid=model_uid)
            if is_moved:
                with open('models.json','a',encoding='utf-8') as json_flie:
                    json.dump(model_data,json_flie,ensure_ascii=False,indent=4)
                    json_flie.write('\n')
            else:
                print("Fail to write to json")
        else:
            print(model_name, "no glb download link\n")

        time.sleep(2)
        xpath_quit = f"/html/body/div[3]/div/div/div/div[1]/div[1]/button"
        button_quit = WebDriverWait(browser,10).until(EC.element_to_be_clickable((By.XPATH,xpath_quit)))
        button_quit.click()
        time.sleep(2)
    time.sleep(5)
    if new_model == 0:
        break
    iter_num += 1

print(model_download)
