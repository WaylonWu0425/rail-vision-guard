import subprocess
from datetime import datetime
import os

# 确保保存目录存在
save_dir = 'D:/camera_test/recordings'
os.makedirs(save_dir, exist_ok=True)

# 获取当前时间戳，作为文件名
now = datetime.now()
timestamp_str = now.strftime('%Y_%m_%d_%H_%M_%S')

# 实时流 RTSP 地址
RTSP_URL = os.environ.get("CAMERA_RTSP_URL", "")

# 输出文件路径
output_file = os.path.join(save_dir, f'recording_{timestamp_str}.mp4')

# ffmpeg 命令
cmd = [
    'ffmpeg',
    '-rtsp_transport', 'tcp',  # 使用 TCP 传输
    '-i', RTSP_URL,            # 输入 RTSP 流
    '-c:v', 'libx264',          # 使用 x264 编码
    '-preset', 'fast',          # 编码速度设置
    '-crf', '23',               # 设置质量
    '-t', '600',                # 录制 10 分钟
    output_file
]

# 执行
try:
    print(f"开始实时录制，保存到 {output_file} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    if result.returncode == 0:
        print("录制完成！")
    else:
        print("录制失败，请检查错误信息。")
except Exception as e:
    print("录制过程中出错：", e)
