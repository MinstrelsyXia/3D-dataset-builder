# 3D-dataset-builder
Utils for building a dataset for 3D reconstruction, including spidering on sketchfab, poly and 3d.si; data cleasing based on gpt, web for visualizing 3d model, code for translating labels and collecting dirty data, blender for generating rgb and depth images of different angle

# Overview on Dataset Format
Our goal is to generate dataset for one-23-45, which as the following dataset requirement：
```
One2345
├── One2345_training_pose.json
├── lvis_split_cc_by.json
└── zero12345_narrow
    ├── 000-000
    ├── 000-001
    ├── 000-002
    ...
    └── 000-159
        ├──uid
        └──uid
            └── 120个png图片

└── 000-159
        ├──uid
        └──uid
            └── render 256
                 └── 120个png图片 

lvis_split_cc_by.json
├── "train": List [{"folder name": Str, "uid": Str}] 文件夹名称和样本的唯一标识符
└── "val": List [{"folder name": Str, "uid": Str}] 

One2345_training_pose.json
├── "intrinsics": 3*3 相机的内参矩阵
|                  [[fx,0,u0],
|                   [0,fy,v0],
|                   [0, 0, 1]]
|                   fx：x轴方向焦距的长度（单位：像素）
|                   fy：y轴方向焦距的长度（单位：像素）
|                   u0,v0：主点的实际位置（单位：像素）
├── "near_far": List len=2 相机的近平面和远平面的深度范围
|                           （即相机的可见深度范围）
|               [近平面深度，远平面深度] （猜测单位为米）
└── "c2ws" 
    ├── "view_0" 
    ├── "view_1"
    ...
    └── "view_7_3_10" 4*4 相机到世界坐标系的变换矩阵
    前8个view_0~view_7是第一阶段生成的角度；（在球面上均匀采样得到的8个相机姿态）
    后面view_0_0_10~view_0_3_10，view_1_0_10~view_1_3_10，是根据前8个view再生成的*4视角（前8个view每个分别对应4个邻近视角，相差10°，共计32个视角）
```

We record every model's basic information:
- model name: raw model name after spidering from the Internet
- description: raw description after spidering from the Internet, used for judging whether it is an antique, all trnaslated into English
- download_link: link to download the model
- uid: a unique label for every 3d-model, generated by sha256 of the raw model name after spidering
- pic_path: auxilliary information for backtracing possible problems

An example is as follows:
```json
{
    "model name": "NMB&H, Iron Age pottery",
    "description": "“Early Iron Age Ceramic bowl, decorated with grooves on the inner side. Height 19.5 cm. From the site of Donja Dolina near Bosanska Gradiška (northern Bosnia) - settlement and cemetery, plot of M. Petrović, Grave 46. 6th c. BCE. Artifact in the National Museum of Bosnia and Herzegovina. Processed in Reality Capture from 310 images. GDH ID No. 22398",
    "download_link": "https://sketchfab.com/3d-models/nmbh-iron-age-pottery-a675e7290af84af4b849b3908ac8abf8#download",
    "uid": "159ee6cd-947c-5342-b731-b60c7748c6d0",
    "pic_path": "E:\\机器学习数据集\\渲染结果\\1684b48f-a6a6-51d7-9f5d-9ac3ee77e951.zip"
},

```

# Pipeline
1. First see `spider/` to crawl down raw 3d models as `*.glb` format from sketchfab, 3d.si, polycam
2. Then either use a gpt-based method from `cleanse/gpt_assisted.py` or create a web and manually kick out the dirty models from `web_show_css`
3. After that see `blender/` for rendering and generating rgb and depth images of different angle
4. At last, use `postprocess/translation.py` to translate some captions in French or other languages into English

# dataset
See our final dataset of 7000+ high-quality antiques at [SJTU-clouddrive](https://pan.sjtu.edu.cn/web/share/464683ef88a5cac71f4c1392ca4a8111), , 提取码: bdmi, if you are an SJTU student
