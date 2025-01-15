import blenderproc as bproc
from numpy.linalg import norm
import bpy
import bpy.ops as ops
import sys
from math import pi,sin,cos,tan
import mathutils
import os
import io
from contextlib import contextmanager
import json
import numpy as np
#from multiprocessing import Pool
#from functools import partial
# bug:zoom out
import math
from mathutils import Vector
import time
from concurrent.futures import ThreadPoolExecutor

stdout = io.StringIO()

Objects=bpy.data.objects
Scene=bpy.data.scenes["Scene"]
bpy.data.worlds['World'].node_tree.nodes['Background'].inputs[0].default_value=[1,1,1,1]
Engines=['BLENDER_WORKBENCH' ,'BLENDER_EEVEE', 'CYCLES']

Scene.view_layers["ViewLayer"].use_pass_z=True

@contextmanager
def stdout_redirected(to=os.devnull):#disable print
    '''
    import os

    with stdout_redirected(to=filename):
        print("from Python")
        os.system("echo non-Python applications are also supported")
    '''
    fd = sys.stdout.fileno()

    ##### assert that Python and C stdio write using the same file descriptor
    ####assert libc.fileno(ctypes.c_void_p.in_dll(libc, "stdout")) == fd == 1

    def _redirect_stdout(to):
        sys.stdout.close() # + implicit flush()
        os.dup2(to.fileno(), fd) # fd writes to 'to' file
        sys.stdout = os.fdopen(fd, 'w') # Python writes to fd

    with os.fdopen(os.dup(fd), 'w') as old_stdout:
        with open(to, 'w') as file:
            _redirect_stdout(to=file)
        try:
            yield # allow code to be run with the redirected stdout
        finally:
            _redirect_stdout(to=old_stdout) # restore stdout.
                                            # buffering and flags such as
                                            # CLOEXEC may be different

# @contextmanager
# def stdout_redirected(file_path="render/output/render_output.txt"):
#     # 提取目录名称并创建目录（如果不存在）
#     dir_name = os.path.dirname(file_path)
#     if dir_name and not os.path.exists(dir_name):
#         os.makedirs(dir_name)

#     # 保存原始 stdout
#     original_stdout = sys.stdout
#     # 打开文件以写入
#     with open(file_path, 'w') as f:
#         sys.stdout = f  # 重定向 stdout 到文件
#         try:
#             yield  # 在上下文中执行的代码
#         finally:
#             # 恢复原始 stdout
#             sys.stdout = original_stdout

def deleteAllObjects():
    """
    Deletes all objects in the current scene
    
    deleteListObjects = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'POINTCLOUD', 'VOLUME', 'GPENCIL',
                         'ARMATURE', 'LATTICE', 'EMPTY', 'LIGHT', 'LIGHT_PROBE', 'CAMERA', 'SPEAKER']
    """
    deleteListObjects = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'POINTCLOUD', 'VOLUME', 'GPENCIL',
                         'ARMATURE', 'LATTICE', 'EMPTY',  'CAMERA', 'SPEAKER']
    
    # Select all objects in the scene to be deleted:

    for o in Objects:
        if o.type in deleteListObjects:
            o.select_set(True)
    bpy.ops.object.delete() # Deletes all selected objects in the scene

def auto_dist(target):
    viewAngle=0.691112
    xs=[ p[0] for p in target.bound_box]
    ys=[ p[1] for p in target.bound_box]
    zs=[ p[2] for p in target.bound_box]
    longest=norm([max(xs)-min(xs),max(ys)-min(ys),max(zs)-min(zs)])
    dist=longest/2/tan(viewAngle/2)/cos(viewAngle/2)
    return dist
def setCameraAngle(c2w:list,target=None):
    '''
    angle: radius
    '''
    camera=None
     
    for o in bpy.data.objects:
        if target is None and o.type=='MESH':
            target=o
        elif o.type=='CAMERA':
            camera=o
    if target is None:
        raise ValueError('No mesh')
    if camera is None:
        raise ValueError('No camera')
    
    c2w=np.array(c2w)
    camera.location = c2w[:3, 3]
    rotation = mathutils.Matrix(c2w[:3, :3])  # 获取 3x3 旋转部分
    camera.rotation_euler = rotation.to_euler()
    dist=norm([camera.location,[0,0,0]])
    height=10
    camera.data.lens = 28
    print("camera dist",dist,",auto dist:",auto_dist(target=target),',lens:',camera.data.lens)
def presetCompositor():

    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    # clear default nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

    # create input view node
    input_node = tree.nodes.new(type='CompositorNodeRLayers')
    input_node.location = 0,0

    # create output node
    #convert_space=tree.nodes.new('CompositorNodeConvertColorSpace')
    #convert_space.from_color_space='sRGB'
    #convert_space.to_color_space='Linear'
    #convert_space.name='convert_space'
    
    #multi_ply3=tree.nodes.new('CompositorNodeMath')
    #multi_ply3.operation='MULTIPLY'
    #multi_ply3.name='multiply3'
    
    comp_node = tree.nodes.new('CompositorNodeComposite') 
    comp_node.name=  'CompositorNodeComposite'
    comp_node.location = 400,0
    
    # create middle node 
    normalize=tree.nodes.new('CompositorNodeNormalize')
    map_range=tree.nodes.new('CompositorNodeMapRange')
    map_range.use_clamp=True
    map_range.inputs[1].default_value=0
    map_range.inputs[2].default_value=2000
    map_range.inputs[3].default_value=0
    map_range.inputs[4].default_value=2000
    
    less_than1=tree.nodes.new('CompositorNodeMath')
    less_than1.operation='LESS_THAN'
    less_than1.name='less_than1'
    less_than1.inputs[1].default_value=0.99999
    
    less_than2=tree.nodes.new('CompositorNodeMath')
    less_than2.operation='LESS_THAN'
    less_than2.name='less_than2'
    less_than2.inputs[1].default_value=2000
    
    multi_ply1=tree.nodes.new('CompositorNodeMath')
    multi_ply1.operation='MULTIPLY'
    multi_ply1.name='multiply1'
    multi_ply2=tree.nodes.new('CompositorNodeMath')
    multi_ply2.operation='MULTIPLY'
    multi_ply2.name='multiply2'
    
    divide=tree.nodes.new('CompositorNodeMath')
    divide.operation='DIVIDE'
    divide.inputs[1].default_value=65.535
    
    

    # inner link nodes
    
    
    links = tree.links
    
    links.new(input_node.outputs[2],normalize.inputs[0])
    links.new(normalize.outputs[0], less_than1.inputs[0])
    links.new(normalize.outputs[0], multi_ply1.inputs[0])
    links.new(less_than1.outputs[0], multi_ply1.inputs[1])
    
    
    links.new(input_node.outputs[2],map_range.inputs[0])
    links.new(map_range.outputs[0], less_than2.inputs[0])
    links.new(map_range.outputs[0], divide.inputs[0])
    links.new(divide.outputs[0], multi_ply2.inputs[0])
    links.new(less_than2.outputs[0], multi_ply2.inputs[1])
    
    
    #links.new(convert_space.outputs[0],multi_ply3.inputs[0])
    #links.new(multi_ply3.outputs[0],comp_node.inputs[0])
    
    #links.new(convert_space.outputs[0],comp_node.inputs[0])
    
    
    bpy.context.scene.use_nodes = False
def change_compositor(mode:int=0):
    
    '''
    0:render
    1:normalized depth 
    2:millimeter depth
    '''
    if mode!=0 and mode!=1 and mode!=2:
        '''No Change'''
        return
    if mode==0:
        bpy.context.scene.use_nodes = False
        Scene.render.image_settings.color_mode='RGBA'
        Scene.render.image_settings.color_depth='8'
        
        Scene.render.image_settings.view_settings.view_transform='Standard'
        
    elif mode==1:
        bpy.context.scene.use_nodes = True
        nodes = bpy.context.scene.node_tree.nodes
        links = bpy.context.scene.node_tree.links
        
        links.new(nodes['multiply1'].outputs[0],nodes['CompositorNodeComposite'].inputs[0])
        #links.new(nodes['less_than1'].outputs[0],nodes['multiply3'].inputs[1])
        
        Scene.render.image_settings.color_mode='BW'
        Scene.render.image_settings.color_depth='16'
        
        
        
        Scene.render.image_settings.view_settings.view_transform='Raw'
        
    
    elif mode==2:
        bpy.context.scene.use_nodes = True
        nodes = bpy.context.scene.node_tree.nodes
        links = bpy.context.scene.node_tree.links
        links.new(nodes['multiply2'].outputs[0],nodes['CompositorNodeComposite'].inputs[0])
        #links.new(nodes['less_than2'].outputs[0],nodes['multiply3'].inputs[1])
        
        Scene.render.image_settings.color_mode='BW'
        Scene.render.image_settings.color_depth='16'
        
        
        
        Scene.render.image_settings.view_settings.view_transform='Raw'

##
def scene_root_objects():
    for obj in bpy.context.scene.objects.values():
        if not obj.parent:
            yield obj

def scene_meshes():
    for obj in bpy.context.scene.objects.values():
        if isinstance(obj.data, (bpy.types.Mesh)):
            yield obj

def scene_bbox(single_obj=None, ignore_matrix=False):
    bbox_min = (math.inf,) * 3
    bbox_max = (-math.inf,) * 3
    found = False
    for obj in scene_meshes() if single_obj is None else [single_obj]:
        found = True
        for coord in obj.bound_box:
            coord = Vector(coord)
            if not ignore_matrix:
                coord = obj.matrix_world @ coord
            bbox_min = tuple(min(x, y) for x, y in zip(bbox_min, coord))
            bbox_max = tuple(max(x, y) for x, y in zip(bbox_max, coord))
    if not found:
        raise RuntimeError("no objects in scene to compute bounding box for")
    return Vector(bbox_min), Vector(bbox_max)

def normalize_scene(format="glb"):
    bbox_min, bbox_max = scene_bbox()
    scale = 1 / max(bbox_max - bbox_min)
    for obj in scene_root_objects():
        obj.scale = obj.scale * scale * 0.8
    # Apply scale to matrix_world.
    bpy.context.view_layer.update()
    bbox_min, bbox_max = scene_bbox()
    offset = -(bbox_min + bbox_max) / 2
    for obj in scene_root_objects():
        obj.matrix_world.translation += offset
    bpy.ops.object.select_all(action="DESELECT")

def list_render(c2w_dict:dict,savedir:str,filepath:str):
    start_time = time.time()
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File does not exist: {filepath}")
    deleteAllObjects()
    
    with stdout_redirected():
        ops.import_scene.gltf(filepath=filepath)
        
    fileID=os.path.split(filepath)[1].split('.')[0]
    ops.object.select_all(action='DESELECT')
    countMesh=0
    for o in Objects:
        if o.type=='MESH':
            countMesh+=1
            o.select_set(True)
            bpy.context.view_layer.objects.active=o
    if countMesh>1:
        ops.object.join()

    ##缩放
    normalize_scene()
    ##缩放

    ops.object.origin_set(type='GEOMETRY_ORIGIN')
    ops.object.select_all(action='DESELECT')
    
    target=None
    for o in Objects:
        if o.type=='MESH':
            target=o
            break
    ops.object.camera_add(location=[auto_dist(target),0,0],rotation=[0.5*pi,0,0.5*pi])
    camera_object = bpy.context.view_layer.objects.active
    # 设置场景中的相机
    bpy.context.scene.camera = camera_object
    ##Format
    Scene.render.resolution_x = 256            
    Scene.render.resolution_y = 256
    # Scene.camera = Objects['Camera'] 
    Scene.render.image_settings.file_format = 'PNG'
    Scene.render.image_settings.compression = 0
    Scene.render.image_settings.color_management='OVERRIDE'
    Scene.render.engine = Engines[2]
    bpy.context.scene.cycles.device = "CPU" ##
    bpy.context.scene.cycles.samples = 128 ##
    bpy.context.scene.cycles.threads = 16
    for view_name,c2w in c2w_dict.items():
        setCameraAngle(target=target,c2w=c2w)
        
        #Render main view
        Scene.render.film_transparent = True
        change_compositor(0)
        Scene.render.filepath=os.path.join(savedir,fileID,view_name+'_gt.png')
        with stdout_redirected():
            bpy.ops.render.render( write_still=True )
        
        
        
        change_compositor(1)
        Scene.render.filepath=os.path.join(savedir,fileID,view_name+'_gt_depth.png')
        
        with stdout_redirected():
            bpy.ops.render.render( write_still=True )
        
        

        change_compositor(2)
        Scene.render.filepath=os.path.join(savedir,fileID,view_name+'_gt_depth_mm.png')
        with stdout_redirected():
            bpy.ops.render.render( write_still=True )
    execute_time=time.time()-start_time
    return {'execute_time':execute_time, 'filepath': filepath}
        
            
def renderAll(model_dir:str,save_dir:str,c2w_dict:dict,multiprocess=False,start_from=None):
    glb_names=[name for name in os.listdir(model_dir) if name.endswith('.glb')]
    if len(glb_names)==0:
        raise Exception('No \'.glb\' file is found')
    if start_from is not None:
        start_index=glb_names.index(start_from)
    else:
        start_index=0
    dir_count = sum([1 for entry in os.listdir(save_dir) if os.path.isdir(os.path.join(save_dir, entry))])
    # Set start_index based on the number of directories found, instead of glb_names
    start_index = dir_count-1
    print('start from:',start_index)
    num_names=len(glb_names)
    if not multiprocess:
        for Index in range(start_index,num_names):
            start_time = time.time()
            list_render(c2w_dict=c2w_dict,
                    filepath=os.path.join(model_dir,glb_names[Index]),
                    savedir=save_dir)
            end_time = time.time()
            print(Index+1,'/',num_names,'  name :',glb_names[Index])
            duration=end_time-start_time
            print(f"renderlist 函数运行时长: {duration:.2f} 秒")
    else:
        with ThreadPoolExecutor(max_workers=os.cpu_count()-2) as executor:
            # 使用非阻塞方式提交任务
            print('cpu count:',os.cpu_count())
            results=[]
            for index in range(start_index, num_names):
                filepath = os.path.join(model_dir, glb_names[index])
                # print(f"Trying to render: {filepath}")  # 打印生成的文件路径
                future = executor.submit(list_render, c2w_dict.copy(), save_dir, filepath)
                # futures[future] = glb_names[index]  # 关联 Future 对象与文件名
                results.append(future.result())
            for result in results:
                print(result)


# '''
# conda activate 3d
# cd C:\Users\lenovo\Desktop\3d_generate\One-2-3-45-master
# blenderproc run render_final.py
# '''

if __name__=='__main__':
    presetCompositor()
    filename = r'C:\Users\lenovo\Desktop\3d_generate\One-2-3-45-master\render\One2345_training_pose.json'
    
    with open(filename, 'r') as file:
        jsondata = json.load(file)
        
    c2w_dict = jsondata.get('c2ws', None)
    intrinsics = jsondata.get('intrinsics', None)

    # 调用 renderAll 函数
    renderAll(model_dir=r'C:\Users\lenovo\Desktop\3d_generate\One-2-3-45-master\render\examples\remain2',
               save_dir=r'C:\Users\lenovo\Desktop\3d_generate\One-2-3-45-master\render\output\remain2',
               c2w_dict=c2w_dict,
               multiprocess=False)
