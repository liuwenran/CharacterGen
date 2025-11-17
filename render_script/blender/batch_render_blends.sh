#!/bin/bash

# 配置路径
BLENDER_PATH="/home/PJLAB/liuwenran/Downloads/blender-3.6.9-linux-x64/blender"
SCRIPT_PATH="/home/PJLAB/liuwenran/Downloads/CharacterGen/render_script/blender/render_vroidhub_multiview_imgs_iclr26.py"
# INPUT_DIR="/home/PJLAB/liuwenran/Downloads/Human_blend"
# OUTPUT_DIR="/home/PJLAB/liuwenran/Downloads/human_blend_rendered"
INPUT_DIR="/home/PJLAB/liuwenran/Downloads/Human_blend_v2"
OUTPUT_DIR="/home/PJLAB/liuwenran/Downloads/human_blend_v2_rendered_bigsize"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 统计信息
total=0
success=0
failed=0

# 记录失败的文件
failed_files=()

echo "=========================================="
echo "开始批量渲染 .blend 文件"
echo "输入目录: $INPUT_DIR"
echo "输出目录: $OUTPUT_DIR"
echo "=========================================="
echo ""

# 遍历所有 .blend 文件
for blend_file in "$INPUT_DIR"/*.blend; do
    # 检查文件是否存在
    if [ ! -f "$blend_file" ]; then
        echo "未找到 .blend 文件，跳过..."
        continue
    fi
    
    # 获取文件名（不含路径和扩展名）
    filename=$(basename "$blend_file" .blend)
    
    # 设置输出文件夹路径
    output_folder="$OUTPUT_DIR/$filename"
    
    # 计数
    total=$((total + 1))
    
    echo "----------------------------------------"
    echo "[$total] 正在处理: $filename"
    echo "输入文件: $blend_file"
    echo "输出文件夹: $output_folder"
    echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # 执行渲染命令
    "$BLENDER_PATH" "$blend_file" --background --python "$SCRIPT_PATH" -- dummy "$output_folder" 1
    
    # 检查执行结果
    if [ $? -eq 0 ]; then
        echo "✓ 渲染成功: $filename"
        success=$((success + 1))
    else
        echo "✗ 渲染失败: $filename"
        failed=$((failed + 1))
        failed_files+=("$filename")
    fi
    
    echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
done

# 输出统计信息
echo "=========================================="
echo "批量渲染完成"
echo "=========================================="
echo "总计文件数: $total"
echo "成功: $success"
echo "失败: $failed"
echo ""

# 如果有失败的文件，列出来
if [ ${#failed_files[@]} -gt 0 ]; then
    echo "失败的文件列表:"
    for failed_file in "${failed_files[@]}"; do
        echo "  - $failed_file"
    done
    echo ""
fi

echo "所有输出保存在: $OUTPUT_DIR"
echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"

