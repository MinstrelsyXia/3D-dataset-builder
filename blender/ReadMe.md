# 环境配置
## windows 系统
安装[blenderproc的github仓](https://github.com/DLR-RM/BlenderProc)
```shell
（打开某个anaconda环境 eg.conda activate 3d 建议3.11版本）
pip install blenderproc # 安装pip包
(
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc
)
blenderproc quickstart
 # 跑一个示例以真正安装blender软件
```
第三行代码等同于blenderproc run quickstart.py 可以按github仓链接里的quickstart.py跑一下，这样最后的output会在同目录下，不然不知道在哪里。

## linux 系统
```shell
# Download Blender for Linux
wget https://mirrors.ocf.berkeley.edu/blender/release/Blender3.6/blender-3.6.5-linux-x64.tar.xz
# Extract the downloaded Blender archive to /opt/
tar -xvf blender-3.6.5-linux-x64.tar.xz -C /opt/
# Install BlenderProc
pip install blenderproc==2.6.1
# Install required dependencies
apt update && apt install -y libsm6 libglfw3-dev
```

# 代码解析：
`render_final.py` ：
1. 支持渲染断掉重连，并行渲染。
2. `gt-depth.png` 数值范围为（0，65535）,`gt-depth-mm.png` 是未缩放的现实距离（以mm为单位）
3. **运行方式**
```shell
conda activate 3d
blenderproc run render_final.py
```
注意修改`render_final/main`函数中 `filename`, `model_dir`, `save_dir` 的路径。

`render_12345.py`:
1. 基于 one-2345官方代码，增加了depth输出。`depth_{idx}` 以m为单位。
2. `launch_render_eval.py`是blenderproc的环境运行程序，其调用渲染主程序`single_render_eval.py`
3. **运行方式**：
   ```shell
   python launch_render_eval.py --DATA_DIR ./examples/objaverse/
   ```

