import bpy, random
import os
import sys
import pdb
import math
from mathutils import Vector

def gc():
    for i in range(10): bpy.ops.outliner.orphans_purge()

def clear():
    [bpy.data.objects.remove(bpy.data.objects[x]) for x in list(bpy.data.objects.keys())]
    gc()

def importVrm(importVrmPath):
    old_objs = set(bpy.context.scene.objects)
    result = bpy.ops.import_scene.vrm(filepath=importVrmPath)
    return [x for x in set(bpy.context.scene.objects)-old_objs if x.type=="ARMATURE"][0]

def getVrm():
    return [x for x in set(bpy.context.scene.objects) if x.type=="ARMATURE"][0]

def importFbx(importFbxPath):
    old_objs = set(bpy.context.scene.objects)
    result = bpy.ops.import_scene.fbx(filepath=importFbxPath)
    return list(set(bpy.context.scene.objects)-old_objs)[0]

def get_keyframes(obj_list):
    keyframes = []
    for obj in obj_list:
        anim = obj.animation_data
        if anim is not None and anim.action is not None:
            for fcu in anim.action.fcurves:
                for keyframe in fcu.keyframe_points:
                    x, y = keyframe.co
                    if x not in keyframes:
                        keyframes.append(int(x))
    return keyframes

def retarget(source_armature,target_armature):
    bpy.context.view_layer.objects.active = source_armature
    bpy.context.scene.source_rig=source_armature.name
    bpy.context.scene.target_rig=target_armature.name
    bpy.ops.arp.build_bones_list()
    bpy.ops.arp.import_config(filepath=os.path.abspath("remap_mixamo.bmap"))
    bpy.ops.arp.auto_scale()
    keyframes=get_keyframes([source_armature])
    
    bpy.ops.arp.retarget(frame_end=int(max(keyframes)))

def look_at(obj_camera, point):
    direction = point - obj_camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    obj_camera.rotation_euler = rot_quat.to_euler()


def calc_camera_position():
    base_camera_position = (0, -2.5, 0.5)
    radius = 2.5
    num_cameras = 21  # 相机数量
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


def render_views(folder, origin = (0, 0, 0)):
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.resolution_x = 1024
    bpy.context.scene.render.resolution_y = 1024

    # bpy.context.scene.render.engine = 'CYCLES'

    # # Enable CUDA
    # bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
    # bpy.context.preferences.addons['cycles'].preferences.devices[0].use = True

    # # Enable all CPU and GPU devices
    # for device in bpy.context.preferences.addons['cycles'].preferences.get_devices():
    #     device.use = True
    
    # camera_positions = {
    #     '0': (0.0, -2.5, 0.5),
    #     '40': (1.61, -1.92, 0.5),
    #     '80': (2.46, -0.43, 0.5),
    #     '120': (2.17, 1.25, 0.5),
    #     '160': (0.86, 2.35, 0.5),
    #     '200': (-0.86, 2.35, 0.5),
    #     '240': (-2.17, 1.25, 0.5),
    #     '280': (-2.46, -0.43, 0.5),
    #     '320': (-1.61, -1.92, 0.5),
    # }

    camera_positions = calc_camera_position()

    camera_data = bpy.data.cameras.new(name='MyCamera')
    camera_data.angle = math.radians(40)
    camera_object = bpy.data.objects.new('MyCamera', camera_data)

    bpy.context.collection.objects.link(camera_object)
    bpy.context.scene.camera = camera_object

    camera = bpy.data.objects['MyCamera']
    for index, position in enumerate(camera_positions):
        camera.location = Vector(position) + Vector(origin)
        look_at(camera, Vector(origin))
        
        frame_name = '{:03d}'.format(index)
        bpy.context.scene.render.filepath = f'{folder}/{frame_name}.png'
        bpy.ops.render.render(write_still=True)
    print("render views done")

def changeApose(armature):
    bones = armature.pose.bones
    if "J_Bip_L_UpperArm" in bones:
        L_arm_name = "J_Bip_L_UpperArm" 
        R_arm_name = "J_Bip_R_UpperArm"
        L_leg_name = "J_Bip_L_UpperLeg"
        R_leg_name = "J_Bip_R_UpperLeg"
    elif "腕上_L.002" in bones:
        L_arm_name = "腕上_L.002"
        R_arm_name = "腕上_R.002"
        L_leg_name = "太もも_L.001"
        R_leg_name = "太もも_R.001"
    elif "Left arm" in bones:
        L_arm_name = "Left arm"
        R_arm_name = "Right arm"
        L_leg_name = "Left leg"
        R_leg_name = "Right leg"
    elif "upper_arm.L" in bones:
        L_arm_name = "upper_arm.L"
        R_arm_name = "upper_arm.R"
        L_leg_name = "upper_leg.L"
        R_leg_name = "upper_leg.R"
    elif "LeftArm" in bones:
        L_arm_name = "LeftArm"
        R_arm_name = "RightArm"
        L_leg_name = "LeftUpLeg"
        R_leg_name = "RightUpLeg"
    elif "Arm_L" in bones:
        L_arm_name = "Arm_L"
        R_arm_name = "Arm_R"
        L_leg_name = "UpLeg_L"
        R_leg_name = "UpLeg_R"
    elif "mixamorig:LeftArm" in bones:
        L_arm_name = "mixamorig:LeftArm"
        R_arm_name = "mixamorig:RightArm"
        L_leg_name = "mixamorig:LeftUpLeg"
        R_leg_name = "mixamorig:RightUpLeg"
    elif "UpperArm_L" in bones:
        L_arm_name = "UpperArm_L"
        R_arm_name = "UpperArm_R"
        L_leg_name = "UpperLeg_L"
        R_leg_name = "UpperLeg_R"
    else:
        print('limb names not found')
        L_arm_name = "L_arm_found"
        R_arm_name = "R_arm_found"
        L_leg_name = "L_leg_found"
        R_leg_name = "R_leg_found"
        exit()

    if L_arm_name in bones:
        bones[L_arm_name].rotation_mode = "XYZ"
        bones[L_arm_name].rotation_euler = (-math.pi / 4, 0.0, 0.0)
        bones[L_arm_name].keyframe_insert(data_path="rotation_euler",frame=0)

    if R_arm_name in bones:
        bones[R_arm_name].rotation_mode = "XYZ"
        bones[R_arm_name].rotation_euler = (-math.pi / 4, 0.0, 0.0)
        bones[R_arm_name].keyframe_insert(data_path="rotation_euler",frame=0)

    if L_leg_name in bones:
        bones[L_leg_name].rotation_mode = "XYZ"
        bones[L_leg_name].rotation_euler = (-math.pi / 30, 0.0, 0.0)
        bones[L_leg_name].keyframe_insert(data_path="rotation_euler",frame=0)

    if R_leg_name in bones:
        bones[R_leg_name].rotation_mode = "XYZ"
        bones[R_leg_name].rotation_euler = (-math.pi / 30, 0.0, 0.0)
        bones[R_leg_name].keyframe_insert(data_path="rotation_euler",frame=0)


def move_origin_to_center(obj):
    local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
    scale_factor = max(obj.dimensions)
    return local_bbox_center
    #print(local_bbox_center)
   #local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
    #global_bbox_center = obj.matrix_world @ local_bbox_center
  
    # for cur_obj in bpy.context.scene.objects:
    #     if cur_obj.type != "MESH":
    #         continue
    #     print(cur_obj.name, cur_obj.type)
    #     import pdb; pdb.set_trace()
    #     global_bbox_center = local_bbox_center @ cur_obj.matrix_world 
    #     cur_obj.location -= global_bbox_center
        #cur_obj.scale /= scale_factor
        #obj.scale /= max(obj.dimensions)

   #  # bpy.ops.object.select_all(action='DESELECT') 
   #  # cur_obj.select_set(True) 
   #  # bpy.context.view_layer.objects.active = cur_obj
   #  # bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
   
def export(armature, apose=False, origin=None, save_dir='apose', data_root_path='./'):
    bpy.ops.object.select_all(action='DESELECT')
    [x.select_set(True) for x in armature.children if(x.type=="MESH")]
    if apose:
        changeApose(armature)
        save_dir = os.path.join(data_root_path, save_dir)
        os.makedirs(save_dir,exist_ok=True)
        # bpy.ops.wm.obj_export(filepath=folder + "/apose.obj",export_animation=True,start_frame=0,end_frame=0,
        #                     export_selected_objects=True,export_materials=False,export_colors=False,export_uv=False,export_normals=False)
        render_views(save_dir, origin)
    else:
        keyframes = get_keyframes([armature])
        #rand_frame = int(random.choice(keyframes))
        os.makedirs(folder + "/pose",exist_ok=True)
        bpy.ops.wm.obj_export(filepath=folder + "/pose.obj",export_animation=True,start_frame=0,end_frame=0,
                            export_selected_objects=True,export_materials=False,export_colors=False,export_uv=False,export_normals=False)
        render_views(folder + "/pose", origin)

def exportAnimatedMesh(importVrmPath,importFbxPath,folder,apose, data_root_path='./'):
    # clear()
    # human=importVrm(importVrmPath)
    human = getVrm()
    # resize human
    if apose:
        origin = move_origin_to_center(human)
        export(human, True, origin, save_dir=folder, data_root_path=data_root_path)
    else:
        anim = importFbx(importFbxPath)
        retarget(anim, human)
        origin = move_origin_to_center(human)
        export(human, folder, False, origin)
   #bpy.data.objects.remove(anim)
   #gc()
   #bpy.data.objects.remove(human)
   #gc()

if(__name__=="__main__"):
    argv = sys.argv
    if("--" in argv):
        argv = argv[argv.index("--") + 1:]
        importVrmPath, importFbxPath, folder, apose=argv
    else:
        raise Exception("no args")
    print("importVrmPath:", importVrmPath)
    data_root_path = "/home/PJLAB/liuwenran/bigdisk"
    exportAnimatedMesh(importVrmPath, importFbxPath, folder, int(apose), data_root_path=data_root_path)