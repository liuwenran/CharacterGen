# 读取文件内容，去除重复行
with open('/home/PJLAB/liuwenran/bigdisk/vroidhub_14k_info/failed_id_all.txt', 'r') as f:
    lines = f.readlines()
    unique_lines = set(lines)

# 将去除重复行后的内容写回文件
with open('/home/PJLAB/liuwenran/bigdisk/vroidhub_14k_info/failed_id_all_done.txt', 'w') as f:
    for line in unique_lines:
        f.write(line)