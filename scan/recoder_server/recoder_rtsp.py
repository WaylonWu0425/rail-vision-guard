import os
import subprocess
from datetime import datetime, timedelta

# 设定回放起止时间（当前时间往前推30分钟）
end_time = datetime.now()
start_time = end_time - timedelta(minutes=30)

# 转成摄像头需要的字符串格式
start_str = start_time.strftime('%Y_%m_%d_%H_%M_%S')
end_str = end_time.strftime('%Y_%m_%d_%H_%M_%S')

# 拼接 RTSP 回放 URL（动态时间）
PLAYBACK_RTSP_URL = f'rtsp://CAMERA_USER:CAMERA_PASSWORD@127.0.0.1/cam/playback?channel=1&subtype=0&starttime={start_str}&endtime={end_str}'

# 输出文件路径
output_file = f'D:/camera/recordings/playback_{start_str}_{end_str}.mp4'

# ffmpeg 命令
cmd = [
    'ffmpeg',
    '-rtsp_transport', 'tcp',
    '-i', PLAYBACK_RTSP_URL,
    '-c', 'copy',
    '-movflags', '+faststart',
    output_file
]

# 执行
try:
    print(f"开始录制回放 {start_str} 到 {end_str} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    print("回放录制完成！")
except Exception as e:
    print("录制过程中出错：", e)

