#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
摄像头监控系统启动脚本
用于简化服务器启动过程
"""

import os
import sys
import signal
import subprocess
import time
import argparse
import json
import logging
from pathlib import Path
from flask import Flask, jsonify, Response, request, send_file
from flask_cors import CORS
import cv2
import base64
from sqlalchemy import create_engine, Column, Integer, String, DateTime, inspect, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timedelta
from threading import Lock
from dotenv import load_dotenv
import pymysql
import traceback
import threading

# 从 .env 文件加载环境变量  
load_dotenv()

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许所有跨域请求

# 从环境变量中读取配置
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:admin@localhost/station_monitoring")

# 数据库设置
try:
    engine = create_engine(DATABASE_URL, echo=False)  # 生产环境关闭 echo
    logger.info("数据库连接成功")
except Exception as e:
    logger.error(f"数据库连接失败: {e}")
    raise

Base = declarative_base()

# 摄像头模型
class Camera(Base):
    __tablename__ = 'camera'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    product_number = Column(Integer)
    status = Column(String(10))
    ip = Column(String(45))
    type = Column(Integer)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow)
    port = Column(Integer)
    username = Column(String(50))
    password = Column(String(255))
    bridgeType = Column(Integer)
    initViewPoint = Column(Integer)

# 检测结果模型
class AlarmInfo(Base):
    __tablename__ = 'alarm_info'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    content = Column(String(255))  # 检测到的对象描述
    camera_id = Column(BigInteger, nullable=False)  # 关联的摄像头ID
    type = Column(String(2))  # 检测类型，使用String存储bit类型
    deal_flag = Column(String(1), default='0')  # 处理标记，使用String存储bit类型
    create_time = Column(DateTime, default=datetime.utcnow)  # 创建时间
    deal_time = Column(DateTime)  # 处理时间
    deal_user_id = Column(BigInteger, nullable=False)  # 处理用户ID，关联外键
    level = Column(String(2), default='1')  # 告警级别，使用String存储bit类型

# 视频记录模型
class VideoRecord(Base):
    __tablename__ = 'video_record'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    camera_id = Column(BigInteger, nullable=False)
    file_path = Column(String(255))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration = Column(Integer)  # 视频时长（秒）
    file_size = Column(BigInteger)  # 文件大小（字节）
    status = Column(String(1), default='0')  # 0: 录制中, 1: 已完成

# 数据库会话
Session = sessionmaker(bind=engine)
session = Session()

# 有效的用户ID，从数据库中获取第一个用户ID
valid_user_id = 39  # 默认值
try:
    with engine.connect() as connection:
        result = connection.execute("SELECT id FROM user LIMIT 1")
        row = result.fetchone()
        if row:
            valid_user_id = row[0]
            logger.info(f"获取到有效的用户ID: {valid_user_id}")
        else:
            logger.warning("未找到有效的用户ID，将使用默认值39")
except Exception as e:
    logger.error(f"获取有效用户ID失败: {e}")
    logger.info("将使用默认用户ID: 39")

def check_requirements():
    """检查系统要求和依赖项"""
    try:
        import cv2
        import flask
        import numpy
        import sqlalchemy  # 新增数据库依赖
        import ffmpeg     # 新增流媒体处理依赖
        print("✅ 基本依赖项检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少必要的依赖项: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_config():
    """检查摄像头配置"""
    config_file = BASE_DIR / "camera_config.json"
    
    if not config_file.exists():
        print(f"⚠️ 未找到摄像头配置文件: {config_file}")
        print("将创建默认流媒体配置...")
        
        # 创建默认流媒体配置
        default_config = {
            "cameras": [
                {
                    "id": "cam1",
                    "name": "摄像头1",
                    "stream_url": os.environ.get("CAMERA_RTSP_URL", ""),
                    "type": "rtsp",
                    "enabled": True
                }
            ]
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            print("✅ 已创建默认配置文件")
        except Exception as e:
            print(f"❌ 创建配置文件失败: {e}")
            return False
    
    # 验证配置内容
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if not config or "cameras" not in config:
            print("⚠️ 摄像头配置格式无效")
            return False
        
        print(f"✅ 已找到 {len(config['cameras'])} 个摄像头配置")
        return True
    except Exception as e:
        print(f"❌ 配置文件读取失败: {e}")
        return False

def check_directories():
    """检查并创建必要的目录"""
    directories = [
        BASE_DIR / "recordings",
        BASE_DIR / "thumbnails",
    ]
    
    for directory in directories:
        if not directory.exists():
            print(f"创建目录: {directory}")
            directory.mkdir(parents=True, exist_ok=True)
    
    print("✅ 目录检查完成")
    return True

def start_server(port, host="0.0.0.0", debug=False):
    """启动摄像头监控服务器"""
    app_path = BASE_DIR / "backend" / "app.py"
    
    if not app_path.exists():
        print(f"❌ 未找到服务器应用: {app_path}")
        return False
    
    print(f"启动服务器: {host}:{port}")
    
    # 构建环境变量
    env = os.environ.copy()
    env["FLASK_APP"] = str(app_path)
    
    if debug:
        env["FLASK_ENV"] = "development"
        env["FLASK_DEBUG"] = "1"
    
    # 启动服务器
    try:
        server_process = subprocess.Popen(
            [sys.executable, str(app_path)],
            env=env
        )
        
        # 等待启动
        time.sleep(2)
        
        # 检查进程是否还在运行
        if server_process.poll() is not None:
            print(f"❌ 服务器启动失败，退出代码: {server_process.returncode}")
            return False
        
        print(f"✅ 服务器已启动，访问: http://{host}:{port}")
        print("按 Ctrl+C 停止服务器")
        
        # 注册信号处理函数，以便正确关闭服务器
        def signal_handler(sig, frame):
            print("\n正在停止服务器...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print("服务器已停止")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 等待服务器进程结束
        server_process.wait()
        
        return True
    except Exception as e:
        print(f"❌ 服务器启动过程中出错: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="摄像头监控系统启动脚本")
    parser.add_argument("-p", "--port", type=int, default=5000, help="服务器端口号")
    parser.add_argument("--host", default="0.0.0.0", help="服务器主机")
    parser.add_argument("-d", "--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--skip-checks", action="store_true", help="跳过预检查")
    
    args = parser.parse_args()
    
    logger.info("=== 摄像头监控系统 ===")
    
    if not args.skip_checks:
        # 运行预检查
        checks = [
            check_requirements,
            check_directories,
            check_config
        ]
        
        for check in checks:
            if not check():
                logger.error("❌ 预检查失败，退出")
                return False
    
    # 验证数据库连接和表
    try:
        inspector = inspect(engine)
        if not inspector.has_table('camera'):
            logger.error("数据库中不存在 'camera' 表")
            return False
        if not inspector.has_table('alarm_info'):
            logger.error("数据库中不存在 'alarm_info' 表")
            return False
        logger.info("✅ 数据库检查通过")
    except Exception as e:
        logger.error(f"数据库检查失败: {e}")
        return False

    # 启动 Flask 应用
    logger.info(f"\n开始启动服务器: {args.host}:{args.port}")
    try:
        app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)
        return True
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        return False

if __name__ == "__main__":
    # 获取基础目录
    BASE_DIR = Path(__file__).resolve().parent
    
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n程序已被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")
        sys.exit(1)

# 摄像头流管理器，用于保持持久连接
class CameraStream:
    def __init__(self):
        self.streams = {}
        self.locks = {}

    def get_stream(self, camera):
        camera_id = camera.id
        if camera_id not in self.streams:
            try:
                # 从数据库获取摄像头信息
                camera = session.query(Camera).filter(Camera.id == camera_id).first()
                if not camera:
                    logger.error(f"摄像头 {camera_id} 不存在")
                    return None

                # 构建RTSP URL
                rtsp_url = f"rtsp://{camera.username}:{camera.password}@{camera.ip}:{camera.port}/cam/realmonitor?channel=1&subtype=0"
                logger.info(f"尝试连接摄像头 {camera_id} 的RTSP流: {rtsp_url}")

                # 尝试打开视频流
                cap = cv2.VideoCapture(rtsp_url)
                if not cap.isOpened():
                    logger.error(f"无法打开摄像头 {camera_id} 的 RTSP 流: {rtsp_url}")
                    return None

                # 设置缓冲区大小
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
                
                # 测试读取一帧
                ret, frame = cap.read()
                if not ret:
                    logger.error(f"无法从摄像头 {camera_id} 读取帧")
                    cap.release()
                    return None

                self.streams[camera_id] = cap
                self.locks[camera_id] = Lock()
                logger.info(f"成功连接摄像头 {camera_id} 的RTSP流")
            except Exception as e:
                logger.error(f"连接摄像头 {camera_id} 时出错: {e}")
                return None
        return self.streams[camera_id]

    def release_stream(self, camera_id):
        if camera_id in self.streams:
            with self.locks[camera_id]:
                try:
                    self.streams[camera_id].release()
                    del self.streams[camera_id]
                    del self.locks[camera_id]
                    logger.info(f"释放了摄像头 {camera_id} 的 RTSP 流")
                except Exception as e:
                    logger.error(f"释放摄像头 {camera_id} 流时出错: {e}")

    def release_all(self):
        for camera_id in list(self.streams.keys()):
            self.release_stream(camera_id)

camera_stream = CameraStream()

def get_online_cameras():
    """从数据库中获取所有在线摄像头（状态为 0）"""
    try:
        cameras = session.query(Camera).filter(Camera.status == '0').all()
        logger.info(f"获取到 {len(cameras)} 个在线摄像头")
        return cameras
    except Exception as e:
        logger.error(f"查询在线摄像头时出错: {e}")
        return []

def generate_frame(camera):
    """从摄像头流中生成单帧"""
    try:
        stream = camera_stream.get_stream(camera)
        if not stream:
            logger.error(f"无法获取摄像头 {camera.id} 的流")
            return None

        with camera_stream.locks[camera.id]:
            ret, frame = stream.read()
            if not ret:
                logger.warning(f"从摄像头 {camera.id} 读取帧失败")
                camera_stream.release_stream(camera.id)
                return None

            # 调整图像大小以提高性能
            frame = cv2.resize(frame, (640, 480))
            
            # 编码为JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret:
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                return frame_base64
            else:
                logger.warning(f"为摄像头 {camera.id} 编码帧失败")
                return None
    except Exception as e:
        logger.error(f"处理摄像头 {camera.id} 帧时出错: {e}")
        return None

def generate_frames(camera):
    """从摄像头流中生成帧并作为流式响应返回。"""
    while True:
        frame_base64 = generate_frame(camera)
        if frame_base64:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' +
                   base64.b64decode(frame_base64) +
                   b'\r\n')
        else:
            logger.warning(f"为摄像头 {camera.id} 生成帧失败，停止流")
            break

@app.route('/video_feed/<int:camera_id>', methods=['GET'])
def video_feed(camera_id):
    """为特定摄像头提供视频流，按 ID 获取。"""
    camera = session.query(Camera).filter(Camera.id == camera_id, Camera.status == '0').first()
    if not camera:
        logger.warning(f"摄像头 {camera_id} 未找到或处于离线状态")
        return jsonify({'error': '摄像头未找到或离线'}), 404

    return Response(generate_frames(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed', methods=['GET'])
def video_feed_default():
    """如果没有提供摄像头 ID，默认提供第一个在线摄像头的视频流。"""
    cameras = get_online_cameras()
    if not cameras:
        logger.warning("没有在线摄像头")
        return jsonify({'error': '没有在线摄像头'}), 404

    camera = cameras[0]
    return Response(generate_frames(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/online_cameras', methods=['GET'])
def online_cameras():
    """返回在线摄像头的列表。"""
    cameras = get_online_cameras()
    camera_list = [
        {
            'id': cam.id,
            'name': cam.name,
            'ip': cam.ip,
            'status': cam.status
        } for cam in cameras
    ]
    return jsonify({'cameras': camera_list})

@app.teardown_appcontext
def shutdown_session(exception=None):
    """关闭数据库会话并释放摄像头流资源。"""
    session.close()
    camera_stream.release_all()
    logger.info("应用程序上下文已销毁，资源已释放")

def get_video_list(page=1, page_size=10):
    """获取视频记录列表"""
    try:
        # 计算分页
        offset = (page - 1) * page_size
        
        # 查询视频记录
        videos = session.query(VideoRecord).order_by(VideoRecord.start_time.desc())\
            .offset(offset).limit(page_size).all()
        
        # 获取总记录数
        total = session.query(VideoRecord).count()
        
        # 构建返回数据
        video_list = []
        for video in videos:
            # 获取关联的摄像头信息
            camera = session.query(Camera).filter(Camera.id == video.camera_id).first()
            camera_name = camera.name if camera else "未知摄像头"
            
            video_list.append({
                'id': video.id,
                'camera_id': video.camera_id,
                'camera_name': camera_name,
                'file_path': video.file_path,
                'start_time': video.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': video.end_time.strftime('%Y-%m-%d %H:%M:%S') if video.end_time else None,
                'duration': video.duration,
                'file_size': video.file_size,
                'status': video.status
            })
        
        return {
            'total': total,
            'items': video_list,
            'page': page,
            'page_size': page_size
        }
    except Exception as e:
        logger.error(f"获取视频列表失败: {e}")
        return None

@app.route('/api/videos/list', methods=['GET'])
def video_list():
    """获取视频列表的API端点"""
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        
        # 获取recordings目录下的所有视频文件
        record_dir = BASE_DIR / "recordings"
        if not record_dir.exists():
            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'total': 0,
                    'items': [],
                    'page': page,
                    'page_size': page_size
                }
            })

        # 获取所有视频文件
        video_files = []
        for file in record_dir.glob("*.mp4"):
            try:
                # 从文件名解析信息
                parts = file.stem.split('_')
                if len(parts) >= 3:
                    camera_id = int(parts[1])
                    timestamp = parts[2]
                    start_time = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
                    
                    # 获取文件信息
                    file_size = file.stat().st_size
                    duration = 0  # 这里可以添加获取视频时长的代码
                    
                    # 获取摄像头信息
                    camera = session.query(Camera).filter(Camera.id == camera_id).first()
                    camera_name = camera.name if camera else "未知摄像头"
                    
                    video_files.append({
                        'id': len(video_files) + 1,  # 使用文件索引作为ID
                        'camera_id': camera_id,
                        'camera_name': camera_name,
                        'file_path': str(file),
                        'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'file_size': file_size,
                        'duration': duration,
                        'status': '1'  # 已完成
                    })
            except Exception as e:
                logger.error(f"处理视频文件 {file} 时出错: {e}")
                continue

        # 按开始时间排序
        video_files.sort(key=lambda x: x['start_time'], reverse=True)
        
        # 计算分页
        total = len(video_files)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_items = video_files[start_idx:end_idx]

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'total': total,
                'items': page_items,
                'page': page,
                'page_size': page_size
            }
        })
    except Exception as e:
        logger.error(f"获取视频列表失败: {e}")
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        }), 500

@app.route('/api/videos/<int:video_id>/file', methods=['GET'])
def get_video_file(video_id):
    """获取视频文件"""
    try:
        video = session.query(VideoRecord).filter(VideoRecord.id == video_id).first()
        if not video:
            return jsonify({
                'code': 404,
                'message': '视频不存在',
                'data': None
            }), 404
        
        if not os.path.exists(video.file_path):
            return jsonify({
                'code': 404,
                'message': '视频文件不存在',
                'data': None
            }), 404
        
        return send_file(
            video.file_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name=f'video_{video_id}.mp4'
        )
    except Exception as e:
        logger.error(f"获取视频文件失败: {e}")
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        }), 500

# 修改 VideoRecorder 类
class VideoRecorder:
    def __init__(self):
        self.recording_cameras = {}  # 正在录制的摄像头
        self.recording_threads = {}  # 录制线程
        self.recording_locks = {}    # 录制锁

    def start_recording(self, camera_id):
        """开始录制视频"""
        if camera_id in self.recording_cameras:
            return False, "该摄像头已在录制中"

        try:
            # 获取摄像头信息
            camera = session.query(Camera).filter(Camera.id == camera_id).first()
            if not camera:
                return False, "摄像头不存在"

            # 创建录制目录
            record_dir = BASE_DIR / "recordings"
            record_dir.mkdir(parents=True, exist_ok=True)

            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"camera_{camera_id}_{timestamp}.mp4"
            file_path = str(record_dir / filename)

            # 创建录制状态
            self.recording_locks[camera_id] = threading.Lock()
            self.recording_cameras[camera_id] = {
                'file_path': file_path,
                'start_time': datetime.now(),
                'status': '0'  # 录制中
            }

            # 启动录制线程
            thread = threading.Thread(
                target=self._record_video,
                args=(camera, file_path)
            )
            thread.daemon = True
            thread.start()
            self.recording_threads[camera_id] = thread

            return True, "开始录制"
        except Exception as e:
            logger.error(f"开始录制失败: {e}")
            return False, str(e)

    def stop_recording(self, camera_id):
        """停止录制视频"""
        if camera_id not in self.recording_cameras:
            return False, "该摄像头未在录制中"

        try:
            with self.recording_locks[camera_id]:
                # 更新录制状态
                self.recording_cameras[camera_id]['status'] = '1'  # 已完成
                
                # 清理录制状态
                del self.recording_cameras[camera_id]
                del self.recording_threads[camera_id]
                del self.recording_locks[camera_id]

            return True, "停止录制"
        except Exception as e:
            logger.error(f"停止录制失败: {e}")
            return False, str(e)

    def _record_video(self, camera, file_path):
        """录制视频的线程函数"""
        try:
            # 获取摄像头流
            stream = camera_stream.get_stream(camera)
            if not stream:
                raise Exception("无法获取摄像头流")

            # 获取视频参数
            width = int(stream.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(stream.get(cv2.CAP_PROP_FPS))

            # 创建视频写入器
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(file_path, fourcc, fps, (width, height))

            while camera.id in self.recording_cameras:
                with self.recording_locks[camera.id]:
                    ret, frame = stream.read()
                    if ret:
                        out.write(frame)
                    else:
                        break

            # 释放资源
            out.release()
            logger.info(f"视频录制完成: {file_path}")
        except Exception as e:
            logger.error(f"视频录制出错: {e}")

# 创建视频录制管理器实例
video_recorder = VideoRecorder()

# 添加视频录制API路由
@app.route('/api/videos/start-recording', methods=['POST'])
def start_recording():
    """开始录制视频"""
    try:
        data = request.get_json()
        camera_id = data.get('camera_id')
        
        if not camera_id:
            return jsonify({
                'code': 400,
                'message': '缺少摄像头ID',
                'data': None
            }), 400

        success, message = video_recorder.start_recording(camera_id)
        if success:
            return jsonify({
                'code': 200,
                'message': message,
                'data': None
            })
        else:
            return jsonify({
                'code': 500,
                'message': message,
                'data': None
            }), 500
    except Exception as e:
        logger.error(f"开始录制API错误: {e}")
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        }), 500

@app.route('/api/videos/stop-recording', methods=['POST'])
def stop_recording():
    """停止录制视频"""
    try:
        data = request.get_json()
        camera_id = data.get('camera_id')
        
        if not camera_id:
            return jsonify({
                'code': 400,
                'message': '缺少摄像头ID',
                'data': None
            }), 400

        success, message = video_recorder.stop_recording(camera_id)
        if success:
            return jsonify({
                'code': 200,
                'message': message,
                'data': None
            })
        else:
            return jsonify({
                'code': 500,
                'message': message,
                'data': None
            }), 500
    except Exception as e:
        logger.error(f"停止录制API错误: {e}")
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        }), 500

# 修改视频流路由
@app.route('/api/video/stream/<int:camera_id>', methods=['GET'])
def video_stream(camera_id):
    """为特定摄像头提供视频流"""
    try:
        # 获取摄像头信息
        camera = session.query(Camera).filter(Camera.id == camera_id, Camera.status == '0').first()
        if not camera:
            logger.warning(f"摄像头 {camera_id} 未找到或处于离线状态")
            return jsonify({
                'code': 404,
                'message': '摄像头未找到或离线',
                'data': None
            }), 404

        def generate():
            while True:
                frame_base64 = generate_frame(camera)
                if frame_base64:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' +
                           base64.b64decode(frame_base64) +
                           b'\r\n')
                else:
                    logger.warning(f"为摄像头 {camera_id} 生成帧失败，停止流")
                    break
                time.sleep(0.033)  # 约30fps

        return Response(
            generate(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        logger.error(f"视频流错误: {e}")
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        }), 500

@app.route('/api/video/stream', methods=['GET'])
def video_stream_default():
    """提供默认摄像头的视频流"""
    try:
        cameras = get_online_cameras()
        if not cameras:
            logger.warning("没有在线摄像头")
            return jsonify({
                'code': 404,
                'message': '没有在线摄像头',
                'data': None
            }), 404

        camera = cameras[0]
        return video_stream(camera.id)
    except Exception as e:
        logger.error(f"默认视频流错误: {e}")
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        }), 500

# 添加获取摄像头列表的API
@app.route('/api/cameras', methods=['GET'])
def get_cameras():
    """获取所有摄像头列表"""
    try:
        cameras = get_online_cameras()
        camera_list = [
            {
                'id': cam.id,
                'name': cam.name,
                'ip': cam.ip,
                'port': cam.port,
                'status': cam.status,
                'type': cam.type
            } for cam in cameras
        ]
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': camera_list
        })
    except Exception as e:
        logger.error(f"获取摄像头列表失败: {e}")
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        }), 500

# 添加视频文件下载API
@app.route('/api/videos/<int:video_id>/download', methods=['GET'])
def download_video(video_id):
    """下载视频文件"""
    try:
        # 获取recordings目录下的所有视频文件
        record_dir = BASE_DIR / "recordings"
        if not record_dir.exists():
            return jsonify({
                'code': 404,
                'message': '视频文件不存在',
                'data': None
            }), 404

        # 查找对应的视频文件
        video_files = list(record_dir.glob("*.mp4"))
        if video_id <= 0 or video_id > len(video_files):
            return jsonify({
                'code': 404,
                'message': '视频不存在',
                'data': None
            }), 404

        video_file = video_files[video_id - 1]
        return send_file(
            str(video_file),
            mimetype='video/mp4',
            as_attachment=True,
            download_name=video_file.name
        )
    except Exception as e:
        logger.error(f"下载视频文件失败: {e}")
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        }), 500 