import math

# 0号相机的位置
base_camera_position = (0, -2.5, 0.5)
radius = 2.5  # 半径
num_cameras = 9  # 相机数量
camera_positions = []

for i in range(num_cameras):
    angle = 0 - math.pi / 2 + 2 * math.pi * i / num_cameras  # 计算每个相机的角度
    x = round(radius * math.cos(angle), 2)# 计算x坐标
    y = round(radius * math.sin(angle), 2)  # 计算y坐标
    camera_positions.append((x, y, base_camera_position[2]))  # z坐标保持不变

# 打印相机位置
for idx, pos in enumerate(camera_positions):
    print(f"{idx * 40}: {pos}")