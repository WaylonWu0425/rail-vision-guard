import subprocess
import time
import os
import glob
import threading
import json
from datetime import datetime
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

# 大华摄像头实时流 RTSP 地址
DAHUA_RTSP_URL = os.environ.get("CAMERA_RTSP_URL", "")

# 输出路径
output_dir = 'D:/camera_test/hls_output/'
playlist_file = f'{output_dir}playlist.m3u8'

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 视频文件访问路由
@app.route('/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory(output_dir, filename)

# API端点，列出所有HLS视频文件
@app.route('/api/list-hls-videos')
def list_hls_videos():
    directory = request.args.get('directory', output_dir)
    video_files = []
    
    # 查找所有.m3u8文件
    m3u8_files = glob.glob(os.path.join(directory, '*.m3u8'))
    
    for file_path in m3u8_files:
        filename = os.path.basename(file_path)
        
        # 跳过主播放列表文件
        if filename == 'playlist.m3u8':
            continue
            
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        file_time = file_stats.st_mtime
        
        # 从文件名提取日期时间（如果有）
        date_str = None
        try:
            # 尝试从文件名中提取日期时间
            if '_' in filename:
                date_parts = filename.split('_')
                if len(date_parts) >= 3 and len(date_parts[1]) == 8 and len(date_parts[2]) >= 6:
                    date_str = f"{date_parts[1]}_{date_parts[2][:6]}"
        except Exception as e:
            print(f"解析文件名日期出错: {e}")
        
        # 如果未能从文件名提取日期，使用文件修改时间
        if not date_str:
            dt = datetime.fromtimestamp(file_time)
            date_str = dt.strftime("%Y%m%d_%H%M%S")
        
        # 构建视频信息对象
        video_info = {
            "filename": filename,
            "path": os.path.join(directory, filename),
            "size": f"{file_size / 1024:.1f} KB",
            "date": date_str,
            "duration": "未知"  # 可以使用ffprobe获取实际时长，这里简化处理
        }
        
        video_files.append(video_info)
    
    # 按日期降序排序
    video_files.sort(key=lambda x: x['date'], reverse=True)
    
    return jsonify({"videos": video_files})

# FFMPEG转码函数，在单独线程中运行
def run_ffmpeg():
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
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"FFMPEG运行出错: {e}")

# 定期生成新的HLS文件（用于测试）
def generate_test_files():
    counter = 0
    while True:
        try:
            # 每5分钟生成一个新文件
            now = datetime.now()
            date_str = now.strftime("%Y%m%d_%H%M%S")
            filename = f"video_{date_str}.m3u8"
            test_file_path = os.path.join(output_dir, filename)
            
            # 创建简单的测试m3u8文件
            with open(test_file_path, 'w') as f:
                f.write("#EXTM3U\n")
                f.write("#EXT-X-VERSION:3\n")
                f.write("#EXT-X-TARGETDURATION:10\n")
                f.write("#EXT-X-MEDIA-SEQUENCE:0\n")
                f.write(f"#EXTINF:10.0,\n")
                f.write(f"segment_test_{counter:03d}.ts\n")
                f.write("#EXT-X-ENDLIST\n")
            
            # 创建简单的测试ts文件
            test_ts_path = os.path.join(output_dir, f"segment_test_{counter:03d}.ts")
            with open(test_ts_path, 'wb') as f:
                # 写入一些随机数据
                f.write(os.urandom(1024 * 10))  # 10KB的随机数据
            
            counter += 1
            time.sleep(300)  # 暂停5分钟
        except Exception as e:
            print(f"生成测试文件出错: {e}")
            time.sleep(60)  # 出错后等待1分钟再试

if __name__ == "__main__":
    # 检查输出目录
    if not os.path.exists(output_dir):
        print(f"创建输出目录: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
    
    print("启动服务器...")
    
    # 启动FFMPEG录制线程
    print("启动RTSP转HLS录制...")
    ffmpeg_thread = threading.Thread(target=run_ffmpeg)
    ffmpeg_thread.daemon = True
    ffmpeg_thread.start()
    
    # 是否生成测试文件（测试用途，只在没有真实视频文件时使用）
    # 如果启用了FFMPEG录制，可以注释掉这个测试生成器
    # test_files_thread = threading.Thread(target=generate_test_files)
    # test_files_thread.daemon = True
    # test_files_thread.start()
    
    # 启动Flask服务器
    print("启动Web服务器在 http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
