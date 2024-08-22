import os
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--thread", type=int)
args = parser.parse_args()

MARGIN = 2000

all_blend_id_file = '/home/PJLAB/liuwenran/bigdisk/vroidhub_14k_info/blend_oss_id.txt'
remote_blend_file_dir = 's3://lol/240628_VRoidData/'
temp_dir = '/home/PJLAB/liuwenran/bigdisk/vroidhub_14k_blend_temp'
finished_id_file = f'/home/PJLAB/liuwenran/bigdisk/vroidhub_14k_info/finished_id_{args.thread}.txt'

if os.path.exists(finished_id_file):
    finished_id_file_handle = open(finished_id_file, 'r')
    finished_file_lines = finished_id_file_handle.read().splitlines()
    finished_id_set = set(finished_file_lines)
    finished_id_file_handle.close()

    pre_finished_id_file_handle = open('/home/PJLAB/liuwenran/bigdisk/vroidhub_14k_info/finished_id.txt', 'r')
    pre_finished_file_lines = pre_finished_id_file_handle.read().splitlines()
    pre_finished_id_set = set(pre_finished_file_lines)
    pre_finished_id_file_handle.close()

    finished_id_set = finished_id_set.union(pre_finished_id_set)
else:
    finished_id_set = set()
finished_id_file_handle = open(finished_id_file, 'a+')


all_blend_id_lines = open(all_blend_id_file, 'r').read().splitlines()
failed_id_file = open(f'/home/PJLAB/liuwenran/bigdisk/vroidhub_14k_info/failed_id_{args.thread}.txt', 'w+')


for ind, line in enumerate(all_blend_id_lines):
    if ind >= args.thread * MARGIN and ind < (args.thread + 1) * MARGIN:
        print(f"Processing {ind} file")
    else:
        continue
    blend_id = line.split('.')[0]
    blend_name = blend_id + '.blend'
    if blend_id in finished_id_set:
        print(f"File {blend_name} already rendered")
        continue

    blend_remote_path = os.path.join(remote_blend_file_dir, blend_name)
    blend_local_path = os.path.join(temp_dir, blend_name)
    result = subprocess.run(['aws','s3','cp', '--profile', 'default', '--endpoint-url', 'http://10.140.2.254', blend_remote_path, blend_local_path], text=True, stdout=subprocess.DEVNULL)

    if not os.path.exists(blend_local_path):
        print(f"File {blend_name} download failed")
        failed_id_file.write(f"{blend_id}\n")
        continue
    
    imgs_output_subdir = 'vroidhub_14k_21views/' + blend_id 
    result = subprocess.run(['sudo', '/home/PJLAB/liuwenran/Downloads/blender-3.6.9-linux-x64/blender', blend_local_path, '-b', '--python', 'render_vroidhub_multiview_imgs.py', '--', 'a', 'a', imgs_output_subdir, '1'], text=True, stdout=subprocess.DEVNULL)

    check_21views_png = os.path.join("/home/PJLAB/liuwenran/bigdisk", imgs_output_subdir, '020.png')
    if os.path.exists(check_21views_png):
        finished_id_file_handle.write(f"{blend_id}\n")
        print('finished:', blend_id)
        result = subprocess.run(['rm', blend_local_path], text=True, stdout=subprocess.DEVNULL)
    else:
        failed_id_file.write(f"{blend_id}\n")
        print('failed:', blend_id)