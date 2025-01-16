import selenium
import requests
import os
import time
import threading
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException,NoSuchElementException,ElementNotVisibleException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import uuid
import shutil
import regex
import re

# 0、准备工作
download_dictionary = './models'
os.makedirs(download_dictionary,exist_ok=True)
models_data = []
# 生成模型对应uid
def generate_uid(input_str):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, input_str))

# 1、用户输入
museum = input('请输入想要查询的模型的来源博物馆:')
topic = input('请输入想要查询的模型类别:')
# eg:museum=National+Museum+of+American+History, topic=Coins

# 2、构造网址
url = f'https://3d.si.edu/explore?edan_q=*:*&edan_fq[]=data_source:"{museum}"&edan_fq[]=topic:"{topic}"'

# 3、打开浏览器
chrome_options = Options()
# 3.1、设置浏览器的偏好设置
prefs = {
    "download.prompt_for_download":False, #下载时不弹出提示框，直接下载
    "download.default_directory":".\models", #下载文件的指定目录 "D:\BaiduSyncdisk\selenium_learning\models"
    "profile.default_content_settings.popups":0 #禁止弹出窗口
}
chrome_options.add_experimental_option('prefs',prefs)
# chrome_options.add_argument('--headless')  #增加无头，防止被网站识别
chrome_options.page_load_strategy = 'eager' #增加界面加载速度，在DOM内容加载完成后立即返回，不必等所有资源（eg：图像）加载完成
chrome_options.add_argument('--disable-gpu') #禁止GPU加速，提高稳定性
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-blink-features=AutomationControlled") #防止网站检测到selenium
chrome_options.add_experimental_option('excludeSwitches',['enable-automation']) #关闭在浏览器中显示自动化控制的标识，防止网站检测

browser = webdriver.Chrome(options=chrome_options)

# 4、加载需要查找的模型页面
browser.get(url)
wait = WebDriverWait(browser,180)
wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div/div[2]/div/div/div[2]/div[1]/ul/li")))  

# 4.1、点击show more按钮，加载完整页面
try:
    page_list = WebDriverWait(browser,3).until(EC.presence_of_all_elements_located((By.XPATH,"//div[@class='item-list']/ul/li")))
    page_num_to_load = len(page_list)-3
    for i in range(page_num_to_load):
        button = WebDriverWait(browser, 10).until(  
                EC.element_to_be_clickable((By.XPATH, "//div[@class='item-list']/ul/li[@class='pager-next']/a"))  
            )  
        button.click()  
    print("Page loaded")
except TimeoutException as error:
    print("Page loaded")

# 4.2、加载该类别的全部模型页面
models = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='search-explore3d']/ul/li")))  
num = len(models)
print(f"Successfully find {num} models of topic {topic} in catagory {museum}\n")

# 5、遍历待查找的所有模型，依次访问每个模型的下载页面，将模型下载到指定文件夹
for model in models:
    time.sleep(5)
    # 获取模型名和url
    model_url = model.find_element(By.XPATH,"./div/a").get_attribute('href')
    model_name = model.find_element(By.XPATH,"./div/a/span[2]/span").text
    model_uid = generate_uid(model_url)
    # 加载模型界面
    browser.get(model_url)
    browser.implicitly_wait(180)
    # 点击下载按钮
    wait.until(lambda driver: driver.find_element(By.XPATH,"//div[@data-popover-element='heading-tab-download']/button[@id='heading-tab-download']"))
    download_button = browser.find_element(By.XPATH,"//div[@data-popover-element='heading-tab-download']/button[@id='heading-tab-download']")
    download_button.click()
    # 找到下载链接
    time.sleep(5)
    keywords = {'glb','150k'}
    try:
        download_link_ =  wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='popover-body']/ul/li/a")))
        matching_links = [link for link in download_link_ if all(keyword in link.get_attribute('href') for keyword in keywords)]
        if matching_links:
            download_link = matching_links[0]
            download_link = download_link.get_attribute('href')
            print("model name:", model_name)
            print("download_link:", download_link)
            word_discription_ = browser.find_element(By.XPATH,"//dl[@class='field-freetextnotes']/dt[1]").text
            if word_discription_ == "Description":
                wait.until(EC.presence_of_all_elements_located((By.XPATH, "//dl[@class='field-freetextnotes']/dd[1]")))
                word_discription = browser.find_element(By.XPATH,"//dl[@class='field-freetextnotes']/dd[1]").text
                print("discription:",word_discription)
            else:
                word_discription = None
                print("No discription")
            print("uid:", model_uid,"\n")
            model_data = {
                "model name":model_name, # 模型名称
                "description":word_discription, # 文字描述
                "download_link":download_link, # 下载链接
                "uid":model_uid
            }
            models_data.append(model_data)
        else:
            print("No matching download link\n")
    except Exception as error:
        print(f"error finding download link:{error}")
    # 回退到前一个页面
    browser.back()

with open('models_data.json', 'a', encoding='utf-8') as json_file:  
    json.dump(models_data, json_file, ensure_ascii=False, indent=4)  
print("Data successfully written to models_data.json")
