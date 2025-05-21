#!/bin/bash

# 脚本名称：render_vroidhub_views.sh
# 功能：运行 Blender 命令，循环渲染 21 个视图（view_number 从 0 到 20）

# 定义路径和参数
BLENDER_PATH="/home/PJLAB/liuwenran/Downloads/blender-3.6.9-linux-x64/blender"
BLEND_FILE="/home/PJLAB/liuwenran/bigdisk/vroidhub_binded_blend/1_19_Idle.blend"
PYTHON_SCRIPT="render_vroidhub_binded_export_camera_params.py"
HDR_PATH="1"
SAVE_PATH_BASE="vroidhub_binded_mp4_view2_temp/1_19_Idle"

# 循环从 0 到 20
for VIEW_NUMBER in {0..20}
do
    echo "Rendering view_number: $VIEW_NUMBER at $(date +'%T')"
    sudo "$BLENDER_PATH" "$BLEND_FILE" -b --python "$PYTHON_SCRIPT" -- --hdr_path "$HDR_PATH" --save_path "$SAVE_PATH_BASE" --view_number "$VIEW_NUMBER"
    if [ $? -eq 0 ]; then
        echo "View $VIEW_NUMBER rendered successfully."
    else
        echo "Error rendering view $VIEW_NUMBER. Check logs or output."
    fi
done

echo "All rendering tasks completed at $(date +'%T')."