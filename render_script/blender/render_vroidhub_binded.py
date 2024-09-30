import bpy
import random
import numpy as np
import math
import os
import argparse
import sys
from mathutils import Vector
import datetime


def constraint():
    # 获取场景中的相机和骨架对象
    camera = bpy.data.objects.get('Camera')
    armature = bpy.data.objects.get('Body')

    # 确保需要的对象都存在
    if camera and armature:
        # 切换到相机的对象模式（确保不在编辑模式或其他模式中）
        bpy.context.view_layer.objects.active = camera
        bpy.ops.object.mode_set(mode='OBJECT')

        # 为相机添加Track To约束
        constraint = camera.constraints.new('TRACK_TO')
        constraint.target = armature
        constraint.subtarget = 'root.x'
        constraint.track_axis = 'TRACK_NEGATIVE_Z'  # 相机的Z轴指向目标
        constraint.up_axis = 'UP_Y'  # 相机的Y轴向上

        print("Constraint added successfully.")

    else:
        print("Required objects not found, or 'mixamorig8:Head' bone missing.")

def look_at(obj_camera, point):
    direction = point - obj_camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    obj_camera.rotation_euler = rot_quat.to_euler()


def calc_camera_position(base_camera_position=(0, -2.5, 0.5), radius=2.5, num_cameras=21):
    camera_positions = []

    for i in range(num_cameras):
        angle = 0 - math.pi / 2 + 2 * math.pi * i / num_cameras  # 计算每个相机的角度
        x = round(radius * math.cos(angle), 2)# 计算x坐标
        y = round(radius * math.sin(angle), 2)  # 计算y坐标
        camera_positions.append((x, y, base_camera_position[2]))  # z坐标保持不变

    # 打印相机位置
    # for idx, pos in enumerate(camera_positions):
    #     print(f"{idx * 40}: {pos}")

    return camera_positions


def CameraMove():
    # 获取当前场景

    track_lists = [
        "track1",
        "track2",
        "track3",
        "track4",
        "track5",
        "track6",
        "track7",
        "track8"
    ]

    camera_track = random.choice(track_lists)

    curve_data = bpy.data.curves.new(name="LineCurve", type='CURVE')
    curve_data.dimensions = '3D'
    polyline = curve_data.splines.new('POLY')
    polyline.points.add(1)

    # create 8 camera track
    if camera_track == "track1":
        x1 = random.uniform(-0.5, 0.5)
        y1 = random.uniform(-5, -4)

        x2 = random.uniform(0.5, 1)
        y2 = random.uniform(-4, -3)

        z1 = random.uniform(0.4, 1.6)
        z2 = random.uniform(0.4, 1.6)

    elif camera_track == "track2":
        x2 = random.uniform(-0.5, 0.5)
        y2 = random.uniform(-5, -4)

        x1 = random.uniform(0.5, 1)
        y1 = random.uniform(-4, -3)

        z1 = random.uniform(0.4, 1.6)
        z2 = random.uniform(0.4, 1.6)

    elif camera_track == "track3":
        x1 = random.uniform(-1, 1)
        y1 = random.uniform(-5, -4)

        x2 = random.uniform(-2, -1)
        y2 = random.uniform(-4, -3)

        z1 = random.uniform(0.4, 1.6)
        z2 = random.uniform(0.4, 1.6)

    elif camera_track == "track4":
        x2 = random.uniform(-1, 1)
        y2 = random.uniform(-5, -4)

        x1 = random.uniform(-2, -1)
        y1 = random.uniform(-4, -3)

        z1 = random.uniform(0.4, 1.6)
        z2 = random.uniform(0.4, 1.6)

    elif camera_track == "track5":
        x1 = random.uniform(-1, -0.5)
        y1 = random.uniform(-5, -4)

        x2 = random.uniform(0.5, 1)
        y2 = random.uniform(-5, -4)

        z1 = random.uniform(0.4, 1.6)
        z2 = random.uniform(0.4, 1.6)

    elif camera_track == "track6":
        x2 = random.uniform(-1, -0.5)
        y1 = random.uniform(-5, -4)

        x1 = random.uniform(0.5, 1)
        y2 = random.uniform(-5, -4)

        z1 = random.uniform(0.4, 1.6)
        z2 = random.uniform(0.4, 1.6)

    elif camera_track == "track7":
        x1 = random.uniform(-1, 1)
        y1 = random.uniform(-5, -4)

        x2 = random.uniform(-1, 1)
        y2 = random.uniform(-4, -3)

        z1 = random.uniform(0.4, 1.6)
        z2 = random.uniform(0.4, 1.6)

    else:
        x1 = random.uniform(-1, 1)
        y2 = random.uniform(-5, -4)

        x2 = random.uniform(-1, 1)
        y1 = random.uniform(-4, -3)

        z1 = random.uniform(0.4, 1.6)
        z2 = random.uniform(0.4, 1.6)


    polyline.points[0].co = (x1, y1, z1, 1)
    polyline.points[1].co = (x2, y2, z2, 1)

    # 创建曲线对象
    curve_obj = bpy.data.objects.new(name="LineCurveObject", object_data=curve_data)
    bpy.context.collection.objects.link(curve_obj)

    # 获取当前场景
    scene = bpy.context.scene

    # 获取场景中的所有相机对象
    cameras = [obj for obj in scene.objects if obj.type == 'CAMERA']

    # 遍历每个相机对象,并删除它们
    for camera in cameras:
        scene.collection.objects.unlink(camera)
        bpy.data.objects.remove(camera, do_unlink=True)

    # 更新场景以应用更改
    bpy.context.view_layer.update()

    # 创建一个新的摄像机对象
    camera_data = bpy.data.cameras.new("Camera")
    camera_object = bpy.data.objects.new("Camera", camera_data)

    # 将摄像机对象添加到场景中
    scene = bpy.context.scene
    scene.collection.objects.link(camera_object)

    camera_positions = calc_camera_position(base_camera_position=(0.0, -3.5, 0.7), radius=3.5, num_cameras=21)

    # camera_object.location = (0, 0, 0)  # 设置摄像机位置
    # camera_object.location = (0.0, -3.5, 0.7)  # 设置摄像机位置
    camera_object.location = camera_positions[1]  # 设置摄像机位置

    origin = (0, 0, 0.7)
    look_at(camera_object, Vector(origin))

    # 将场景的活动摄像机设置为新创建的摄像机
    scene.camera = camera_object
    bpy.context.view_layer.update()

    # # 添加路径约束
    # constraint = camera_object.constraints.new(type='FOLLOW_PATH')
    # constraint.target = curve_obj
    # constraint.use_curve_follow = True

    # # 将相机沿路径动画化
    # bpy.context.view_layer.update()
    # bpy.context.view_layer.objects.active = camera_object
    # bpy.ops.constraint.followpath_path_animate(constraint="跟随路径", owner='OBJECT')

    return camera_track


def print_camera(camera_track, image_path):
    # 获取场景
    scene = bpy.context.scene

    # 获取动画的起始和结束帧
    start_frame = bpy.context.scene.frame_start
    end_frame = bpy.context.scene.frame_end

    # 获取相机对象，假设你的相机名为'Camera'
    camera = bpy.data.objects['Camera']

    # 获取当前打开的.blend文件的路径
    current_blend_file_path = bpy.data.filepath

    blend_name = current_blend_file_path.split(".blend")[0]
    image_name = image_path.split("/")[-1].split("_4k")[0]

    txt_path = blend_name + "_" + camera_track + "_" + image_name + ".txt"

    # 打印相机信息
    with open(f'{txt_path}', 'w') as file:
        for frame in range(start_frame, end_frame + 1):
            scene.frame_set(frame)
            # 使用 matrix_world 获取有约束影响的位置和旋转
            camera_world_location = camera.matrix_world.to_translation()
            camera_world_rotation = camera.matrix_world.to_euler()

            # 打印相机的世界位置和旋转
            # print(f"{frame}: {camera_world_location},  {camera_world_rotation}")
            line = f"{frame}: {camera_world_location},  {camera_world_rotation}\n"
            file.write(line)


def create_world_with_environment_texture(image_path):
    # 创建一个新的世界数据块
    new_world = bpy.data.worlds.new("EnvironmentWorld")
    bpy.context.scene.world = new_world

    # 启用节点并清除默认节点
    new_world.use_nodes = True
    nodes = new_world.node_tree.nodes
    nodes.clear()

    # 添加环境纹理节点
    env_texture_node = nodes.new('ShaderNodeTexEnvironment')
    env_texture_node.location = (-300, 0)
    # 加载并设置环境纹理图像
    try:
        env_texture_node.image = bpy.data.images.load(image_path)
    except:
        print("Failed to load image at:", image_path)
        return

    # 添加背景节点
    background_node = nodes.new('ShaderNodeBackground')
    background_node.location = (0, 0)

    # 添加世界输出节点
    world_output_node = nodes.new('ShaderNodeOutputWorld')
    world_output_node.location = (300, 0)

    # 连接节点
    links = new_world.node_tree.links
    try:
        links.new(env_texture_node.outputs['Color'], background_node.inputs['Color'])
        links.new(background_node.outputs['Background'], world_output_node.inputs['Surface'])
    except KeyError as e:
        print("Failed to connect nodes:", e)

def split_str(s, num):
    count = 0
    for i, char in enumerate(s):
        if char == "/":
            count += 1
            if count == num:
                return s[i+1:]
    return ""


def blender_mp4(camera_track, image_path, save_dir, view_name='view0'):
    # 获取当前打开的.blend文件的路径
    current_blend_file_path = bpy.data.filepath   

    blend_name = current_blend_file_path.split('/')[-1].split(".blend")[0]
    image_name = image_path.split("/")[-1].split("_4k")[0]

    time_str = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    # mp4_path = blend_name + "_" + camera_track + "_" + image_name + "_" + time_str + ".mp4"
    mp4_path = os.path.join(save_dir, blend_name + "_" + view_name + ".mp4")

    # 设置输出格式为 FFmpeg 视频
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'

    # 设置容器为 MPEG-4
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'

    # 设置视频编码器为 H.264
    bpy.context.scene.render.ffmpeg.codec = 'H264'

    # 设置渲染分辨率
    bpy.context.scene.render.resolution_x = 1024
    bpy.context.scene.render.resolution_y = 1024

    bpy.context.scene.frame_end = 60

    bpy.context.scene.render.filepath = mp4_path

    # 执行渲染
    bpy.ops.render.render(animation=True, write_still=True)


def select_background():
    image_paths = [
        # '/Users/fangyouqing/Project/vroid_dataset/0619_scale/0628_hdr_images/small_rural_road_02_4k.hdr',
        # '/Users/fangyouqing/Project/vroid_dataset/0619_scale/0628_hdr_images/old_outdoor_theater_4k.hdr',
    ]

    image_path = random.choice(image_paths)

    return image_path



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hdr_path", type=str, help="背景环境图片")
    parser.add_argument("--save_path", type=str, help="保存路径")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])  # 分割blender参数和自定义py文件参数

    camera_track = CameraMove()
    # constraint()

    # 用您自己的图像路径替换这里的路径
    # image_path = select_background()
    image_path = args.hdr_path
    # create_world_with_environment_texture(image_path)
    bpy.context.scene.render.film_transparent = True

    # 获取当前 Blender 文件的路径
    save_path = args.save_path
    current_file = bpy.data.filepath  

    print("image_path:", image_path)
    root_path = '/home/PJLAB/liuwenran/bigdisk'
    view_name = 'view5'
    save_dir = os.path.join(root_path, save_path)
    os.makedirs(save_dir, exist_ok=True)
    blender_mp4(camera_track, image_path, save_dir, view_name=view_name)
    # print_camera(camera_track, image_path )
    # 保存当前 Blender 文件
    # save_path_split = current_file.split('/')
    # save_path_split[-1] = '1_without_fbx.blend'
    # save_path = '/'.join(save_path_split)
    # bpy.ops.wm.save_mainfile(filepath=save_path)
    # print(f"Blender file saved at: {current_file}")

# /Applications/Blender.app/Contents/MacOS/Blender /Users/fangyouqing/Documents/GitHub/Render4HA-appendix/1.blend --python /Users/fangyouqing/Documents/GitHub/Render4HA-appendix/0628_render_videos.py -b -- --hdr_path /Users/fangyouqing/Documents/GitHub/Render4HA-appendix/autumn_park_4k.hdr
