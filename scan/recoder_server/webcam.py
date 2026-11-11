import os
import subprocess
import time

# 大华摄像头实时流 RTSP 地址
DAHUA_RTSP_URL = os.environ.get("CAMERA_RTSP_URL", "")

# 输出路径
output_dir = 'D:/camera_test/hls_output/'
playlist_file = f'{output_dir}playlist.m3u8'

# ffmpeg 命令
cmd = [
    'ffmpeg',
    '-rtsp_transport', 'tcp',
    '-i', DAHUA_RTSP_URL,
    '-c:v', 'copy',
    '-c:a', 'copy',
    '-f', 'hls',
    '-hls_time', '10',
    '-hls_list_size', '0',
    '-hls_segment_filename', f'{output_dir}segment_%03d.ts',
    playlist_file
]

# 执行
subprocess.run(cmd)
