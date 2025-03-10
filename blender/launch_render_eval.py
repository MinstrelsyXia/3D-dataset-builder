# Batch render all meshes in the folder DATA_DIR: ["examples/objaverse/", "examples/ours/"]
import os
import subprocess
import argparse

# Create an argument parser to accept the DATA_DIR as a command-line argument
parser = argparse.ArgumentParser()
parser.add_argument('--DATA_DIR', type=str, default='examples/objaverse/', help='Path to the folder containing meshes to render')
args = parser.parse_args()

# The directory containing the extracted Blender
BLD_DIR = "/opt/blender-3.6.5-linux-x64/"
DATA_DIR = args.DATA_DIR
OUT_DIR = "output/"
SCRIPT = "single_render_eval.py"
RESOLUTION = "512"

## modified
# conda_env_name = "blender_env"
# conda_base = subprocess.check_output("conda info --base", shell=True).decode("utf-8").strip()
# activate_conda_env = os.path.join(conda_base, "bin", "activate")
# os.system(f"source {activate_conda_env} {conda_env_name}")

# # 设置PYTHONPATH
# python_path = os.path.join(conda_base, "envs", conda_env_name, "lib", "python3.9", "site-packages")
# os.environ["PYTHONPATH"] = python_path

# Command to run
blenderproc_command = [
    "/home/charlotte/miniconda3/envs/blender_env/bin/blenderproc",
    "run",
    "--custom-blender-path="+BLD_DIR,
    "--blender-install-path="+BLD_DIR,
    SCRIPT,
    "--object_path",
    "",
    "--output_dir",
    OUT_DIR,
    "--engine",
    "CYCLES",
    "--camera_dist",
    "1.3",
    "--resolution",
    RESOLUTION
]

for shape in os.listdir(DATA_DIR):
    print(f"Rendering {shape} ...")
    object_path = f"{DATA_DIR}/{shape}"
    render_path = os.path.join(OUT_DIR, shape.split('.')[0], f"render_{RESOLUTION}")
    blenderproc_command[6] = object_path
    blenderproc_command[8] = render_path
    subprocess.run(blenderproc_command)