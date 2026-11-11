import os
import logging
from flask import Flask, jsonify, Response
from flask_cors import CORS
import cv2
import base64
from ultralytics import YOLO
from sqlalchemy import create_engine, Column, Integer, String, DateTime, inspect
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from threading import Lock
from dotenv import load_dotenv

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
MODEL_PATH = os.getenv("MODEL_PATH", "Detection/models/best.pt")

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



# 验证 'camera' 表是否存在于数据库中
inspector = inspect(engine)
if not inspector.has_table('camera'):
    logger.error("数据库中不存在 'camera' 表。请在运行应用程序之前创建该表。")
    raise RuntimeError("数据库中不存在 'camera' 表。")

# 数据库会话
Session = sessionmaker(bind=engine)
session = Session()

# 加载 YOLO 模型
try:
    model = YOLO(MODEL_PATH)
    logger.info("YOLO 模型加载成功")
except Exception as e:
    logger.error(f"YOLO 模型加载失败: {e}")
    raise

# 摄像头流管理器，用于保持持久连接
class CameraStream:
    def __init__(self):
        self.streams = {}
        self.locks = {}

    def get_stream(self, camera):
        camera_id = camera.id
        if camera_id not in self.streams:
            rtsp_url = f"rtsp://{camera.username}:{camera.password}@{camera.ip}/cam/realmonitor?channel=1&subtype=0"
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                logger.error(f"无法打开摄像头 {camera_id} 的 RTSP 流: {rtsp_url}")
                return None
            self.streams[camera_id] = cap
            self.locks[camera_id] = Lock()
            logger.info(f"为摄像头 {camera_id} 打开 RTSP 流")
        return self.streams[camera_id]

    def release_stream(self, camera_id):
        if camera_id in self.streams:
            with self.locks[camera_id]:
                self.streams[camera_id].release()
                del self.streams[camera_id]
                del self.locks[camera_id]
                logger.info(f"释放了摄像头 {camera_id} 的 RTSP 流")

    def release_all(self):
        for camera_id in list(self.streams.keys()):
            self.release_stream(camera_id)

camera_stream = CameraStream()

def get_online_cameras():
    """从数据库中获取所有在线摄像头（状态为 0）。"""
    try:
        cameras = session.query(Camera).filter(Camera.status == '0').all()
        logger.info(f"获取到 {len(cameras)} 个在线摄像头")
        return cameras
    except Exception as e:
        logger.error(f"查询在线摄像头时出错: {e}")
        return []

def generate_frame(camera):
    """从摄像头流中生成单帧并使用 YOLO 进行处理。"""
    stream = camera_stream.get_stream(camera)
    if not stream:
        return None

    with camera_stream.locks[camera.id]:
        ret, frame = stream.read()
        if not ret:
            logger.warning(f"从摄像头 {camera.id} 读取帧失败")
            camera_stream.release_stream(camera.id)  # 如果读取失败，则释放流
            return None

    # 执行 YOLO 推理
    try:
        results = model(frame)
        annotated_frame = results[0].plot()
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        if ret:
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            return frame_base64
        else:
            logger.warning(f"为摄像头 {camera.id} 编码帧失败")
            return None
    except Exception as e:
        logger.error(f"为摄像头 {camera.id} 执行 YOLO 推理失败: {e}")
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

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)
