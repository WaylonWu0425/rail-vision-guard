import subprocess
import threading
import time
import os
import glob
import json
import signal
import datetime
import shutil
from datetime import datetime
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

# 大华摄像头实时流 RTSP 地址
DAHUA_RTSP_URL = os.environ.get("CAMERA_RTSP_URL", "")

# 输出路径
output_dir = 'D:/camera_test/hls_output/'
playlist_file = f'{output_dir}playlist.m3u8'

# 直播片段存放子目录
live_dir = f'{output_dir}live/'

# 每个录像的时长（秒）
SEGMENT_DURATION = 300  # 5分钟

# 当前的ffmpeg进程
current_ffmpeg_process = None
live_ffmpeg_process = None

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)
os.makedirs(live_dir, exist_ok=True)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 视频文件访问路由
@app.route('/videos/<path:filename>')
def serve_video(filename):
    # 先检查主目录
    if os.path.exists(os.path.join(output_dir, filename)):
        return send_from_directory(output_dir, filename)
    # 再检查直播子目录
    elif os.path.exists(os.path.join(live_dir, filename)):
        return send_from_directory(live_dir, filename)
    else:
        return "文件不存在", 404

# API端点，列出所有HLS视频文件
@app.route('/api/list-hls-videos')
def list_hls_videos():
    directory = request.args.get('directory', output_dir)
    video_files = []
    
    try:
        # 查找所有.m3u8文件
        m3u8_files = glob.glob(os.path.join(directory, "*.m3u8"))
        
        for file_path in m3u8_files:
            filename = os.path.basename(file_path)
            
            # 跳过主播放列表文件和临时文件
            if filename == 'playlist.m3u8' or filename.endswith('.tmp'):
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
            
            # 计算视频时长（简化处理，使用固定值）
            duration = "05:00"  # 5分钟
            
            # 构建视频信息对象
            video_info = {
                "filename": filename,
                "path": os.path.join(directory, filename),
                "size": f"{file_size / 1024:.1f} KB",
                "date": date_str,
                "duration": duration
            }
            
            video_files.append(video_info)
        
        # 按日期降序排序
        video_files.sort(key=lambda x: x['date'], reverse=True)
    except Exception as e:
        print(f"获取视频列表时出错: {e}")
    
    return jsonify({"videos": video_files})

# 添加一个API端点，返回主播放列表的信息
@app.route('/api/live-stream')
def get_live_stream():
    # 获取playlist.m3u8的文件名
    playlist_filename = os.path.basename(playlist_file)
    
    # 确保文件存在
    if not os.path.exists(playlist_file):
        return jsonify({"error": "直播流文件未找到"}), 404
    
    # 如果文件存在但小于10字节，可能还未正确写入
    if os.path.getsize(playlist_file) < 10:
        return jsonify({"error": "直播流文件正在准备中，请稍后再试"}), 503
    
    live_stream_info = {
        "filename": playlist_filename,
        "path": f"/videos/{playlist_filename}",
        "url": f"http://localhost:5000/videos/{playlist_filename}",
        "title": "实时监控",
        "is_live": True
    }
    
    # 添加日志记录
    print(f"正在提供直播流: {playlist_filename}")
    
    return jsonify(live_stream_info)

# 添加状态API，便于前端检查服务器状态
@app.route('/api/status')
def get_status():
    try:
        # 获取当前正在录制的视频信息
        recording_info = None
        if current_ffmpeg_process and current_ffmpeg_process.poll() is None:
            recording_info = {"status": "recording"}
        else:
            recording_info = {"status": "idle"}
            
        # 获取直播状态
        live_status = None
        if live_ffmpeg_process and live_ffmpeg_process.poll() is None:
            live_status = {"status": "streaming"}
        else:
            live_status = {"status": "stopped"}
            
        # 获取系统信息
        disk_space = shutil.disk_usage(output_dir)
        disk_info = {
            "total": f"{disk_space.total / (1024**3):.2f} GB",
            "used": f"{disk_space.used / (1024**3):.2f} GB",
            "free": f"{disk_space.free / (1024**3):.2f} GB",
            "percent_used": f"{disk_space.used / disk_space.total * 100:.1f}%"
        }
        
        # 获取视频文件数量
        videos_count = len(glob.glob(os.path.join(output_dir, "video_*.m3u8")))
        
        return jsonify({
            "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "recording": recording_info,
            "live_stream": live_status,
            "disk_space": disk_info,
            "videos_count": videos_count,
            "version": "1.0.1"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 清理旧的直播TS文件
def clean_live_ts_files():
    try:
        # 获取直播目录中的所有ts文件
        ts_files = glob.glob(os.path.join(live_dir, "*.ts"))
        
        # 按修改时间排序
        ts_files.sort(key=os.path.getmtime)
        
        # 如果超过10个文件，删除最旧的几个
        if len(ts_files) > 10:
            for old_file in ts_files[:-10]:  # 保留最新的10个文件
                try:
                    if os.path.exists(old_file):
                        os.remove(old_file)
                        print(f"已删除旧的TS文件: {os.path.basename(old_file)}")
                except Exception as e:
                    print(f"删除文件出错: {os.path.basename(old_file)} - {e}")
    except Exception as e:
        print(f"清理TS文件出错: {e}")

# 生成新的视频文件名
def generate_video_filename():
    now = datetime.now()
    date_str = now.strftime("%Y%m%d_%H%M%S")
    return f"video_{date_str}"

# 使用FFMPEG录制指定时长的视频
def record_segment():
    global current_ffmpeg_process
    
    try:
        # 创建新的视频文件名
        filename_base = generate_video_filename()
        m3u8_file = f"{output_dir}{filename_base}.m3u8"
        ts_pattern = f"{output_dir}{filename_base}_%03d.ts"
        
        print(f"开始录制新片段: {filename_base}")
        
        # 构建FFMPEG命令，修复时间戳和音频问题
        cmd = [
            'ffmpeg',
            '-rtsp_transport', 'tcp',
            '-i', DAHUA_RTSP_URL,
            '-c:v', 'copy',
            '-c:a', 'aac',        # 转换音频为AAC格式，更兼容
            '-ar', '44100',       # 标准音频采样率
            '-strict', 'experimental',
            '-f', 'hls',
            '-hls_time', '10',
            '-hls_list_size', '0',
            '-hls_flags', 'independent_segments+append_list+temp_file+program_date_time',
            '-hls_segment_type', 'mpegts',
            '-hls_segment_filename', ts_pattern,
            '-t', str(SEGMENT_DURATION),  # 录制时长
            m3u8_file
        ]
        
        # 启动录制进程
        current_ffmpeg_process = subprocess.Popen(cmd)
        
        # 等待录制完成
        current_ffmpeg_process.wait()
        
        print(f"片段录制完成: {filename_base}")
        
        # 添加EXT-X-ENDLIST标记到m3u8文件末尾，表明视频已完成
        with open(m3u8_file, 'a') as f:
            f.write("#EXT-X-ENDLIST\n")
        
        # 更新主播放列表（可选）
        update_master_playlist()
        
    except Exception as e:
        print(f"录制出错: {e}")
    finally:
        current_ffmpeg_process = None

# 启动直播流录制
def start_live_stream():
    global live_ffmpeg_process
    
    try:
        # 确保直播目录存在
        os.makedirs(live_dir, exist_ok=True)
        
        # 清理已存在的所有直播文件
        try:
            for file in glob.glob(os.path.join(live_dir, "*.ts*")):
                os.remove(file)
            for file in glob.glob(os.path.join(live_dir, "*.tmp")):
                os.remove(file)
            print("已清理旧的直播文件")
        except Exception as e:
            print(f"清理旧文件出错: {e}")
        
        live_ts_pattern = f"{live_dir}live_%03d.ts"
        
        # 构建直播的FFMPEG命令，修复时间戳问题
        live_cmd = [
            'ffmpeg',
            '-rtsp_transport', 'tcp',
            '-i', DAHUA_RTSP_URL,
            '-c:v', 'copy',
            '-c:a', 'aac',        # 转换音频为AAC格式
            '-ar', '44100',       # 标准音频采样率
            '-strict', 'experimental',
            '-f', 'hls',
            '-hls_time', '2',
            '-hls_list_size', '5',
            '-hls_flags', 'delete_segments+append_list+temp_file+program_date_time',
            '-hls_segment_type', 'mpegts',
            '-hls_segment_filename', live_ts_pattern,
            playlist_file
        ]
        
        # 启动直播进程
        live_ffmpeg_process = subprocess.Popen(live_cmd)
        
        # 定期清理旧的TS文件
        threading.Thread(target=periodic_cleanup, daemon=True).start()
    
    except Exception as e:
        print(f"启动直播流出错: {e}")

# 定期执行清理任务
def periodic_cleanup():
    while True:
        time.sleep(30)  # 每30秒执行一次清理
        clean_live_ts_files()

# 更新主播放列表
def update_master_playlist():
    try:
        # 获取所有m3u8文件
        m3u8_files = glob.glob(os.path.join(output_dir, "video_*.m3u8"))
        m3u8_files.sort(reverse=True)  # 最新的放在前面
        
        # 创建主播放列表
        recordings_playlist = f"{output_dir}recordings.m3u8"
        with open(recordings_playlist, "w") as f:
            f.write("#EXTM3U\n")
            f.write("#EXT-X-VERSION:3\n")
            
            for m3u8_file in m3u8_files:
                filename = os.path.basename(m3u8_file)
                duration = 300  # 5分钟
                f.write(f"#EXTINF:{duration},\n")
                f.write(f"{filename}\n")
    except Exception as e:
        print(f"更新主播放列表出错: {e}")

# 连续录制视频片段
def continuous_recording():
    print("启动连续录制...")
    while True:
        record_segment()
        time.sleep(1)  # 小暂停，避免文件冲突

# 添加安全退出的处理
def signal_handler(sig, frame):
    print("正在安全退出...")
    
    # 停止当前的FFMPEG进程
    if current_ffmpeg_process:
        try:
            current_ffmpeg_process.terminate()
            current_ffmpeg_process.wait(timeout=5)
        except:
            current_ffmpeg_process.kill()
    
    # 停止直播FFMPEG进程
    if live_ffmpeg_process:
        try:
            live_ffmpeg_process.terminate()
            live_ffmpeg_process.wait(timeout=5)
        except:
            live_ffmpeg_process.kill()
    
    print("已停止所有录制进程。")
    exit(0)

if __name__ == "__main__":
    # 检查输出目录
    if not os.path.exists(output_dir):
        print(f"创建输出目录: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
    
    # 确保直播目录存在
    os.makedirs(live_dir, exist_ok=True)
    
    # 注册信号处理器，用于优雅退出
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("启动服务器...")
    
    # 启动直播流
    start_live_stream()
    
    # 启动连续录制的线程
    recording_thread = threading.Thread(target=continuous_recording)
    recording_thread.daemon = True
    recording_thread.start()
    
    # 启动Flask服务器
    print("启动Web服务器在 http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
