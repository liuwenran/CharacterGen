import os
import subprocess
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument("--thread", type=int)
parser.add_argument("--all", action='store_true', default=False)
args = parser.parse_args()

MARGIN = 4000

all_blend_id_file = '/home/PJLAB/liuwenran/bigdisk/vroidhub_binded_info/blend_0623_random_motion_id.txt'
remote_blend_file_dir = 's3://lol/240704_VRoidDataset/blend_0623_random_motion/'
temp_dir = '/home/PJLAB/liuwenran/bigdisk/vroidhub_binded_temp'

if not args.all:
    finished_id_file = f'/home/PJLAB/liuwenran/bigdisk/vroidhub_binded_info/finished_id_{args.thread}.txt'
else:
    finished_id_file = f'/home/PJLAB/liuwenran/bigdisk/vroidhub_binded_info/finished_id_all.txt'

if os.path.exists(finished_id_file):
    finished_id_file_handle = open(finished_id_file, 'r')
    finished_file_lines = finished_id_file_handle.read().splitlines()
    finished_id_set = set(finished_file_lines)
    finished_id_file_handle.close()
else:
    finished_id_set = set()
finished_id_file_handle = open(finished_id_file, 'a+')


if not args.all:
    failed_id_file = f'/home/PJLAB/liuwenran/bigdisk/vroidhub_binded_info/failed_id_{args.thread}.txt'
else:
    failed_id_file = f'/home/PJLAB/liuwenran/bigdisk/vroidhub_binded_info/failed_id_all.txt'

if os.path.exists(failed_id_file):
    failed_id_file_handle = open(failed_id_file, 'r')
    failed_file_lines = failed_id_file_handle.read().splitlines()
    failed_id_set = set(failed_file_lines)
    failed_id_file_handle.close()
else:
    failed_id_set = set()
failed_id_file_handle = open(failed_id_file, 'a+')



all_blend_id_lines = open(all_blend_id_file, 'r').read().splitlines()


for ind, line in enumerate(all_blend_id_lines):
    if not args.all:
        if ind >= args.thread * MARGIN and ind < (args.thread + 1) * MARGIN:
            print(f"Processing {ind} file {line}")
        else:
            continue
    time_begin = time.time()
    blend_id = line.split('.')[0]
    blend_name = blend_id + '.blend'
    if blend_id in finished_id_set:
        print(f"File {blend_name} already rendered")
        continue
    if blend_id in failed_id_set:
        print(f"File {blend_name} failed before")
        continue

    blend_remote_path = os.path.join(remote_blend_file_dir, blend_name)
    blend_local_path = os.path.join(temp_dir, blend_name)
    result = subprocess.run(['aws','s3','cp', '--profile', 'default', '--endpoint-url', 'http://10.140.2.254', blend_remote_path, blend_local_path], text=True, stdout=subprocess.DEVNULL)

    if not os.path.exists(blend_local_path):
        print(f"File {blend_name} download failed")
        failed_id_file.write(f"{blend_id}\n")
        continue
    
    imgs_output_subdir = 'vroidhub_binded_mp4/' + blend_id 
    result = subprocess.run(['sudo', '/home/PJLAB/liuwenran/Downloads/blender-3.6.9-linux-x64/blender', blend_local_path, '-b', '--python', 'render_vroidhub_binded.py', '--', '--hdr_path', '1', '--save_path', imgs_output_subdir], text=True, stdout=subprocess.DEVNULL)

    time_end = time.time()
    print(f"time cost: {time_end - time_begin}")
    check_mp4 = os.path.join("/home/PJLAB/liuwenran/bigdisk", imgs_output_subdir, blend_id + '_view0.mp4')
    if os.path.exists(check_mp4):
        finished_id_file_handle.write(f"{blend_id}\n")
        print('finished:', blend_id)
        result = subprocess.run(['rm', blend_local_path], text=True, stdout=subprocess.DEVNULL)
    else:
        failed_id_file.write(f"{blend_id}\n")
        print('failed:', blend_id)