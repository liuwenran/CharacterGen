import bpy, random
import os
import sys
import pdb
import math
from mathutils import Vector

RADIUS = 5
HEIGHT = -0.5
LIGHT_ENERGY = 1000

def gc():
    for i in range(10): bpy.ops.outliner.orphans_purge()

def clear():
    [bpy.data.objects.remove(bpy.data.objects[x]) for x in list(bpy.data.objects.keys())]
    gc()

def getMesh():
    # 打印所有对象以调试
    print("Objects in scene:")
    for obj in bpy.context.scene.objects:
        print(f" - {obj.name}: {obj.type}")
    
    # 查找 MESH 对象
    meshes = [x for x in set(bpy.context.scene.objects) if x.type == "MESH"]
    if not meshes:
        raise ValueError("No MESH found in the scene. Please ensure the .blend file contains a MESH object.")
    return meshes[0]

def importFbx(importFbxPath):
    old_objs = set(bpy.context.scene.objects)
    result = bpy.ops.import_scene.fbx(filepath=importFbxPath)
    return list(set(bpy.context.scene.objects) - old_objs)[0]

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

def look_at(obj_camera, point):
    direction = point - obj_camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    obj_camera.rotation_euler = rot_quat.to_euler()

def calc_camera_position(center, model_width, model_height, num_cameras=21):
    """
    Calculate camera positions around the center of the model at eye level.
    
    Args:
        center (Vector): Center position of the model.
        model_width (float): Width of the model to adjust camera radius.
        num_cameras (int): Number of camera positions.
    
    Returns:
        list: List of camera positions.
    """
    # Set radius to bring camera closer and maintain proportion
    # radius = model_width * 1  # Adjust distance based on model width
    radius = RADIUS  # Adjust distance based on model width
    height = HEIGHT  # Fix camera height at ground level for eye-level view
    print(f"Camera radius: {radius}, Height: {height}")

    camera_positions = []
    for i in range(num_cameras):
        angle = -math.pi / 2 + 2 * math.pi * i / num_cameras
        x = round(radius * math.cos(angle), 2)
        y = round(radius * math.sin(angle), 2)
        camera_positions.append(Vector((x, y, height)) + center)
    return camera_positions

def setup_lighting(camera):
    """
    Add a point light that follows the camera to illuminate the model.
    
    Args:
        camera: The camera object to parent the light to.
    
    Returns:
        bpy.types.Object: The created light object.
    """
    # Create a point light
    light_data = bpy.data.lights.new(name="PointLight", type='POINT')
    light_data.energy = LIGHT_ENERGY  # Increase light intensity
    light_data.color = (1.0, 1.0, 1.0)  # White light
    
    light_object = bpy.data.objects.new(name="PointLight", object_data=light_data)
    bpy.context.collection.objects.link(light_object)
    
    # Position the light near the camera
    light_object.location = camera.location
    light_object.parent = camera  # Parent the light to the camera so it moves with it
    
    return light_object

def render_views(folder, center=Vector((0, 0, 0)), model_height=1.0, model_width=1.0):
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.resolution_x = 1024
    bpy.context.scene.render.resolution_y = 1024

    # Create camera
    camera_data = bpy.data.cameras.new(name='MyCamera')
    camera_data.angle = math.radians(40)
    camera_object = bpy.data.objects.new('MyCamera', camera_data)
    bpy.context.collection.objects.link(camera_object)
    bpy.context.scene.camera = camera_object

    # Setup lighting
    light_object = setup_lighting(camera_object)

    # Calculate camera positions based on model center and dimensions
    camera_positions = calc_camera_position(center, model_width, model_height)

    camera = bpy.data.objects['MyCamera']
    center = center + Vector((0, 0, HEIGHT))
    for index, position in enumerate(camera_positions):
        print(f"Camera position {index}: {position}")
        camera.location = position
        look_at(camera, center)
        

        frame_name = '{:03d}'.format(index)
        # frame_name = '{:03d}'.format((index - 1) % len(camera_positions))
        bpy.context.scene.render.filepath = os.path.join(folder, f'{frame_name}.png')
        bpy.ops.render.render(write_still=True)
    print("render views done")

def move_origin_to_center(obj):
    """
    Move the object's origin to its geometric center and translate to world origin (0, 0, 0).
    
    Args:
        obj: The Blender object to adjust (MESH).
    
    Returns:
        tuple: (center, height, width) - The original center position, model height, and width.
    """
    # Ensure the object is a MESH
    if obj.type != "MESH":
        raise ValueError(f"Expected MESH object, got {obj.type}")

    # Deselect all objects manually
    for o in bpy.context.scene.objects:
        o.select_set(False)

    # Calculate the local bounding box center
    local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
    global_bbox_center = obj.matrix_world @ local_bbox_center

    # Calculate model dimensions
    bbox = [Vector(b) for b in obj.bound_box]
    model_height = max(v.z for v in bbox) - min(v.z for v in bbox)
    model_width = max(v.x for v in bbox) - min(v.x for v in bbox)

    # Move the object to the world origin
    obj.location -= global_bbox_center

    # Update the scene to reflect changes
    bpy.context.view_layer.update()

    return global_bbox_center, model_height, model_width

def export(obj, apose=False, origin=None, model_height=1.0, model_width=1.0, save_dir='apose', data_root_path='./'):
    if apose:
        save_dir = os.path.join(data_root_path, save_dir)
        os.makedirs(save_dir, exist_ok=True)
        render_views(save_dir, origin or Vector((0, 0, 0)), model_height, model_width)
    else:
        os.makedirs(os.path.join(save_dir, "pose"), exist_ok=True)
        bpy.ops.wm.obj_export(filepath=os.path.join(save_dir, "pose.obj"), export_animation=False, start_frame=0, end_frame=0,
                            export_selected_objects=True, export_materials=False, export_colors=False, export_uv=False, export_normals=False)
        render_views(os.path.join(save_dir, "pose"), origin, model_height, model_width)

def exportAnimatedMesh(importFbxPath, folder, apose, data_root_path='./'):
    # Get the mesh from the scene (already loaded in the .blend file)
    mesh_obj = getMesh()
    if apose:
        center, model_height, model_width = move_origin_to_center(mesh_obj)
        print(f"Model center: {center}, Height: {model_height}, Width: {model_width}")
        export(mesh_obj, True, center, model_height, model_width, save_dir=folder, data_root_path=data_root_path)
    else:
        anim = importFbx(importFbxPath)
        # Skip retarget since no ARMATURE is present
        center, model_height, model_width = move_origin_to_center(mesh_obj)
        print(f"Model center: {center}, Height: {model_height}, Width: {model_width}")
        export(mesh_obj, False, center, model_height, model_width, save_dir=folder, data_root_path=data_root_path)
    if 'anim' in locals():
        bpy.data.objects.remove(anim, do_unlink=True)
    gc()
    bpy.data.objects.remove(mesh_obj, do_unlink=True)
    gc()

if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
        importFbxPath, folder, apose = argv
    else:
        raise Exception("no args")
    print("importFbxPath:", importFbxPath)
    data_root_path = "/home/PJLAB/liuwenran/bigdisk"
    exportAnimatedMesh(importFbxPath, folder, int(apose), data_root_path=data_root_path)