from flask import Flask, jsonify, request, render_template, url_for
import os
import json
import shutil

app = Flask(__name__)

# 读取 .glb 文件
def get_glb_files():
    directory = os.path.join(os.path.dirname(__file__), 'static/1500_1799')  # 使用绝对路径
    return [f for f in os.listdir(directory) if f.endswith('.glb')]

# 路由：主页
@app.route('/')
def index():
    return render_template('index.html')

# 路由：保存用户反馈
@app.route('/save_feedback', methods=['POST'])
def save_feedback():
    data = request.json
    model_name = data['model']
    response = data['response']
    print(f'用户对模型 {model_name} 的反馈是：{response}')
    # 保存到 JSON 文件
    with open('D:\脚痛大学/basics\大三上\机器学习\web_show_css\static/1500_1799\jsons/feedback.jsonl', 'a', encoding='utf-8') as f:
        json.dump({'model': model_name, 'response': response}, f, ensure_ascii=False)
        f.write('\n')  # 每个反馈一行

    return jsonify({'status': 'success'})

# 路由：获取下一个模型
models = get_glb_files()
cnt = 0
@app.route('/next-model', methods=['GET'])
def next_model():
    global cnt
    if cnt < len(models):
        next_model = models[cnt]
        cnt += 1
        return jsonify({'src': url_for('static', filename='1500_1799/' + next_model), 'description': '下一个模型描述'})
    else:
        cnt = len(models)  # 添加这行代码
        # classify_models()  # 调用分类模型文件的函数
        return jsonify({'error': '没有更多模型了'}), 404

# 函数：分类模型文件
# def classify_models():
#     feedback_file = 'feedback.json'
#     antique_file = os.path.join(os.path.dirname(__file__), 'static/models_copy/json/antique.json')
#     cleaned_json_path = r"D:\store\ToBeCleaned\cjy\cjy_cleaned_models.json"
#     deleted_json_path = r"D:\store\ToBeCleaned\cjy\cjy_deleted_models.json"
#     unknown_json_path = r"D:\store\ToBeCleaned\cjy\unknown_models.json"
#     cleaned_models_path = r"D:\store\ToBeCleaned\cjy\cleaned_models"
#     deleted_models_path = r"D:\store\ToBeCleaned\cjy\deleted_models"
#     unknown_models_path = r"D:\store\ToBeCleaned\cjy\unknown_models"

#     # 创建目标文件夹
#     os.makedirs(cleaned_models_path, exist_ok=True)
#     os.makedirs(deleted_models_path, exist_ok=True)
#     os.makedirs(unknown_models_path, exist_ok=True)

#     # 读取反馈文件
#     with open(feedback_file, 'r', encoding='utf-8') as f:
#         feedback_data = [json.loads(line) for line in f]

#     # 读取antique.json文件
#     with open(antique_file, 'r', encoding='utf-8') as f:
#         antique_data = json.load(f)

#     cleaned_data = []
#     deleted_data = []
#     unknown_data = []

#     for item in feedback_data:
#         model_name = item['model']
#         response = item['response']
#         src_path = os.path.join(os.path.dirname(__file__), 'static/models_copy', model_name)

#         if response == 'yes':
#             dst_path = os.path.join(cleaned_models_path, model_name)
#             shutil.move(src_path, dst_path)
#             cleaned_data.append(item)
#         elif response == 'no':
#             dst_path = os.path.join(deleted_models_path, model_name)
#             shutil.move(src_path, dst_path)
#             deleted_data.append(item)
#         else:
#             dst_path = os.path.join(unknown_models_path, model_name)
#             shutil.move(src_path, dst_path)
#             unknown_data.append(item)

#     # 保存分类后的数据
#     with open(cleaned_json_path, 'w', encoding='utf-8') as f:
#         json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

#     with open(deleted_json_path, 'w', encoding='utf-8') as f:
#         json.dump(deleted_data, f, ensure_ascii=False, indent=2)

#     with open(unknown_json_path, 'w', encoding='utf-8') as f:
#         json.dump(unknown_data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
