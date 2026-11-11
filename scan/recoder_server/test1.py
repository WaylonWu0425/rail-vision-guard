import subprocess
from datetime import datetime
import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import glob
import threading
import time

save_dir = 'D:/camera_test/recordings'

os.makedirs(save_dir, exist_ok=True)
RTSP_URL = os.environ.get("CAMERA_RTSP_URL", "")

def record_loop():
    while True:
        now = datetime.now()
        timestamp_str = now.strftime('%Y_%m_%d_%H_%M_%S')
        output_file = os.path.join(save_dir, f'recording_{timestamp_str}.mp4')
        thumb_file = os.path.join(save_dir, f'recording_{timestamp_str}.jpg')
        cmd = [
            'ffmpeg',
            '-rtsp_transport', 'tcp',
            '-i', RTSP_URL,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-t', '600',
            output_file
        ]
        print(f"开始录制，保存到 {output_file} ...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
        if result.returncode == 0:
            print("本段录制完成，准备生成缩略图。")
            # 生成最后一帧缩略图
            thumb_cmd = [
                'ffmpeg', '-sseof', '-1', '-i', output_file, '-vframes', '1', '-q:v', '2', thumb_file, '-y'
            ]
            subprocess.run(thumb_cmd)
        else:
            print("录制失败，3秒后重试。")
            time.sleep(3)

# 启动循环录制线程
threading.Thread(target=record_loop, daemon=True).start()

app = Flask(__name__)
CORS(app)

def generate_missing_thumbnails():
    for file in os.listdir(save_dir):
        if file.endswith('.mp4'):
            base = os.path.splitext(file)[0]
            jpg = os.path.join(save_dir, base + '.jpg')
            mp4 = os.path.join(save_dir, file)
            if not os.path.exists(jpg) and os.path.exists(mp4):
                print(f'补齐缩略图: {jpg}')
                subprocess.run([
                    'ffmpeg', '-sseof', '-1', '-i', mp4, '-vframes', '1', '-q:v', '2', jpg, '-y'
                ])

# 在 Flask 启动前调用
generate_missing_thumbnails()

@app.route('/videos/<path:filename>')
def serve_video(filename):
    file_path = os.path.join(save_dir, filename)
    if os.path.exists(file_path):
        return send_from_directory(save_dir, filename)
    return "文件不存在", 404

def get_video_duration(filepath):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', filepath],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        seconds = float(result.stdout.strip())
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f'{hours:02d}:{minutes:02d}:{secs:02d}'
    except Exception as e:
        print(f'获取视频时长失败: {e}')
        return '00:00:00'

@app.route('/api/list-videos')
def list_videos():
    files = glob.glob(os.path.join(save_dir, "*.mp4"))
    files.sort(reverse=True)
    video_list = []
    # 获取服务端地址
    server_url = request.host_url.rstrip('/')
    for f in files:
        stat = os.stat(f)
        base = os.path.splitext(os.path.basename(f))[0]
        thumb = f"{base}.jpg"
        thumb_path = os.path.join(save_dir, thumb)
        duration = get_video_duration(f)
        video_list.append({
            "filename": os.path.basename(f),
            "size": f"{stat.st_size // 1024} KB",
            "mtime": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            "url": f"{server_url}/videos/{os.path.basename(f)}",
            "thumbnail": f"{server_url}/videos/{thumb}" if os.path.exists(thumb_path) else "",
            "duration": duration
        })
    return jsonify(video_list)

@app.route('/api/delete-video', methods=['POST'])
def delete_video():
    data = request.get_json()
    filename = data.get('filename')
    if not filename or '/' in filename or '\\' in filename:
        return jsonify({'success': False, 'error': '无效的文件名'}), 400
    video_path = os.path.join(save_dir, filename)
    base, _ = os.path.splitext(filename)
    thumb_path = os.path.join(save_dir, base + '.jpg')
    result = {'success': True, 'deleted': []}
    try:
        if os.path.exists(video_path):
            os.remove(video_path)
            result['deleted'].append(filename)
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
            result['deleted'].append(base + '.jpg')
        if not result['deleted']:
            return jsonify({'success': False, 'error': '文件不存在'}), 404
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("Flask服务器启动：http://localhost:5000")
    app.run(host='0.0.0.0', port=5000)