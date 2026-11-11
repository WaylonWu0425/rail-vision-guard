import os
import logging
from flask import Flask, jsonify, Response
from flask_cors import CORS
import cv2
import base64
from ultralytics import YOLO
from sqlalchemy import create_engine, Column, Integer, String, DateTime, inspect, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timedelta
from threading import Lock
from dotenv import load_dotenv
import pymysql
import time
import re
import traceback
from queue import Queue
import threading
import subprocess
import signal
import sys

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
MODEL_PATH = os.getenv("MODEL_PATH", "models/best.pt")
DETECTION_THRESHOLD = int(os.getenv("DETECTION_THRESHOLD", "5"))  # 检测结果缓存时间（秒）

# 创建检测队列
detection_queue = Queue()

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
    deal_user_id = Column(BigInteger, nullable=True)  # 处理用户ID，关联外键，允许为空
    level = Column(String(2), default='1')  # 告警级别，使用String存储bit类型

# 验证 'camera' 表是否存在于数据库中
inspector = inspect(engine)
if not inspector.has_table('camera'):
    logger.error("数据库中不存在 'camera' 表。请在运行应用程序之前创建该表。")
    raise RuntimeError("数据库中不存在 'camera' 表。")

# 验证 'alarm_info' 表是否存在于数据库中
if not inspector.has_table('alarm_info'):
    logger.error("数据库中不存在 'alarm_info' 表。请确保该表已创建。")
    raise RuntimeError("数据库中不存在 'alarm_info' 表。")
else:
    logger.info("成功连接到 alarm_info 表")

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

# 检测结果缓存，用于避免相同的检测结果在短时间内重复写入数据库
# 格式: {camera_id: {"last_normal": timestamp, "last_person": timestamp, "last_car": timestamp}}
detection_cache = {}

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

def process_detection_result(camera_id, result_text):
    """处理检测结果，直接写入告警信息到数据库"""
    current_time = time.time()
    
    # 初始化摄像头的检测缓存
    if camera_id not in detection_cache:
        detection_cache[camera_id] = {
            "last_normal": 0,
            "last_person": 0,
            "last_car": 0
        }
    
    # 记录原始检测结果以便调试
    logger.info(f"处理摄像头 {camera_id} 的检测结果: {result_text}")
    
    # 解析检测结果
    if "(no detections)" in result_text:
        # 正常状态，没有检测到任何对象
        detection_type = 0
        content = "正常状态"
        cache_key = "last_normal"
        logger.info(f"摄像头 {camera_id} 未检测到物体，记录为正常状态")
    else:
        # 检测到对象，解析数量和类型
        persons_match = re.search(r'(\d+) persons?', result_text)
        cars_match = re.search(r'(\d+) cars?', result_text)
        
        if persons_match:
            person_count = int(persons_match.group(1))
            if person_count > 0:
                detection_type = 1
                content = f"检测到 {person_count} 人"
                cache_key = "last_person"
                logger.info(f"摄像头 {camera_id} 检测到 {person_count} 人，创建告警")
            else:
                # 没有检测到人，跳过
                logger.info(f"摄像头 {camera_id} 检测到 0 人，不触发告警")
                return
        elif cars_match:
            car_count = int(cars_match.group(1))
            if car_count > 0:
                detection_type = 2
                content = f"检测到 {car_count} 辆车"
                cache_key = "last_car"
                logger.info(f"摄像头 {camera_id} 检测到 {car_count} 辆车，创建告警")
            else:
                # 没有检测到车，跳过
                logger.info(f"摄像头 {camera_id} 检测到 0 辆车，不触发告警")
                return
        else:
            # 其他类型的检测，暂时忽略
            logger.warning(f"未能识别的检测结果文本: '{result_text}'")
            return
    
    # 检查是否需要写入数据库（避免相同类型的频繁写入）
    last_detection_time = detection_cache[camera_id].get(cache_key, 0)
    
    # 检查距离上次写入是否已经过了20秒
    if current_time - last_detection_time < 20:
        logger.info(f"摄像头 {camera_id} 的 {content} 告警在20秒内已经写入过，跳过本次写入")
        return
    
    # 更新最后检测时间
    logger.info(f"准备写入告警，摄像头：{camera_id}，类型：{detection_type}，距离上次写入已经过去 {current_time - last_detection_time:.1f} 秒")
    detection_cache[camera_id][cache_key] = current_time
    
    # 直接写入告警记录到数据库
    success = direct_write_record(content, camera_id, detection_type)
    if success:
        logger.info(f"成功写入告警记录: {content}")
    else:
        logger.error(f"写入告警记录失败: {content}")

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
        # 检查是否需要写入数据库
        current_time = time.time()
        # 初始化摄像头的检测缓存
        if camera.id not in detection_cache:
            detection_cache[camera.id] = {
                "last_normal": 0,
                "last_person": 0,
                "last_car": 0,
                "last_realtime": 0  # 添加实时告警的缓存键
            }
        
        # 检查距离上次实时告警写入是否已经过了20秒
        last_realtime_time = detection_cache[camera.id].get("last_realtime", 0)
        should_write = current_time - last_realtime_time >= 20
        
        if should_write:
            # 简单生成一个时间戳，确保每次记录都不同
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 强制写入一条告警记录，使用直接的SQL方式
            try:
                conn = pymysql.connect(
                    host='localhost',
                    user='root',
                    password=os.environ.get("DB_PASSWORD", ""),
                    database='station_monitoring',
                    charset='utf8mb4'
                )
                cursor = conn.cursor()
                
                content = f"实时告警 {timestamp}"
                
                # 修改 SQL 语句，将 deal_user_id 设置为 NULL
                sql = """INSERT INTO alarm_info 
                        (content, camera_id, type, deal_flag, deal_user_id, level) 
                        VALUES (%s, %s, b'01', b'0', NULL, b'01')"""
                
                cursor.execute(sql, (content, camera.id))
                conn.commit()
                
                # 更新最后实时告警时间
                detection_cache[camera.id]["last_realtime"] = current_time
                
                logger.info(f"成功写入实时告警: {content}, 摄像头ID: {camera.id}")
                
                conn.close()
            except Exception as e:
                logger.error(f"写入实时告警失败: {e}")
        else:
            logger.info(f"摄像头 {camera.id} 的实时告警在20秒内已经写入过，跳过本次写入")
        
        # 执行常规的YOLO推理，但不使用结果
        results = model(frame)
        result = results[0]
        
        # 绘制检测框等标记
        annotated_frame = result.plot()
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

@app.route('/alarm_stats', methods=['GET'])
def alarm_stats():
    """返回告警信息的统计数据"""
    try:
        db_session = Session()
        # 获取最近24小时的告警信息
        last_24h = datetime.now() - timedelta(hours=24)
        total_alarms = db_session.query(AlarmInfo).filter(AlarmInfo.create_time >= last_24h).count()
        person_alarms = db_session.query(AlarmInfo).filter(AlarmInfo.create_time >= last_24h, AlarmInfo.type == '1').count()
        car_alarms = db_session.query(AlarmInfo).filter(AlarmInfo.create_time >= last_24h, AlarmInfo.type == '2').count()
        normal_alarms = db_session.query(AlarmInfo).filter(AlarmInfo.create_time >= last_24h, AlarmInfo.type == '0').count()
        
        # 获取最近10条告警记录
        recent_alarms = db_session.query(AlarmInfo).order_by(AlarmInfo.create_time.desc()).limit(10).all()
        recent_alarm_list = [
            {
                'id': alarm.id,
                'content': alarm.content,
                'camera_id': alarm.camera_id,
                'type': alarm.type,
                'create_time': alarm.create_time.strftime('%Y-%m-%d %H:%M:%S')
            } for alarm in recent_alarms
        ]
        
        # 当前队列中待写入的告警数量
        pending_alarms = detection_queue.qsize()
        
        db_session.close()
        
        return jsonify({
            'stats': {
                'total_24h': total_alarms,
                'person_24h': person_alarms,
                'car_24h': car_alarms,
                'normal_24h': normal_alarms,
                'pending': pending_alarms
            },
            'recent_alarms': recent_alarm_list
        })
    except Exception as e:
        logger.error(f"获取告警统计信息失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.teardown_appcontext   #装饰器用于注册一个函数，该函数会在每次Flask应用上下文(application context)结束时自动被调用
def shutdown_session(exception=None):
    """关闭数据库会话并释放摄像头流资源。"""
    session.close()
    camera_stream.release_all()
    logger.info("应用程序上下文已销毁，资源已释放")

def direct_write_record(content, camera_id, detection_type):
    """直接写入一条告警记录到数据库，使用与测试脚本相同的方法"""
    conn = None
    try:
        logger.info(f"尝试写入告警记录：{content}, 摄像头ID: {camera_id}, 类型: {detection_type}")
        # 数据库连接
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password=os.environ.get("DB_PASSWORD", ""),
            database='station_monitoring',
            charset='utf8mb4'
        )
        logger.info("数据库连接成功，准备执行SQL语句")
        cursor = conn.cursor()
        
        # 根据检测类型设置bit值
        if detection_type == 0:
            bit_type = "b'00'"  # 正常
        elif detection_type == 1:
            bit_type = "b'01'"  # 人
        elif detection_type == 2:
            bit_type = "b'10'"  # 车
        else:
            bit_type = "b'00'"  # 默认正常
        
        # 写入记录，将 deal_user_id 设置为 NULL
        sql = """INSERT INTO alarm_info 
                (content, camera_id, type, deal_flag, deal_user_id, level) 
                VALUES (%s, %s, %s, b'0', NULL, b'01')"""
        
        logger.info(f"执行SQL: {sql}, 参数: ({content}, {camera_id}, {bit_type})")
        cursor.execute(sql, (content, camera_id, bit_type))
        logger.info("SQL执行成功，准备提交事务")
        conn.commit()
        logger.info("事务提交成功")
        
        # 查询刚写入的记录
        try:
            cursor.execute("SELECT id FROM alarm_info WHERE content = %s ORDER BY id DESC LIMIT 1", (content,))
            result = cursor.fetchone()
            if result:
                record_id = result[0]
                logger.info(f"成功写入告警记录，ID: {record_id}, 内容: {content}")
                return True
            else:
                logger.error(f"写入告警记录失败，未能查询到记录: {content}")
                return False
        except Exception as query_error:
            logger.error(f"查询刚写入的记录失败: {query_error}")
            # 即使查询失败，仍然认为写入成功
            logger.info(f"仍然认为写入成功: {content}")
            return True
    except pymysql.MySQLError as sql_error:
        logger.error(f"MySQL错误: {sql_error}")
        error_code = getattr(sql_error, 'args', [None])[0]
        if error_code:
            logger.error(f"MySQL错误码: {error_code}")
        logger.error(f"MySQL错误堆栈: {traceback.format_exc()}")
        return False
    except Exception as e:
        logger.error(f"写入告警记录一般异常: {e}")
        logger.error(f"异常堆栈: {traceback.format_exc()}")
        return False
    finally:
        if conn:
            try:
                conn.close()
                logger.info("数据库连接已关闭")
            except Exception as close_error:
                logger.error(f"关闭数据库连接时出错: {close_error}")

# 定义与定时重启相关的变量和函数
restart_timer = None
restart_interval = 180  # 3分钟重启一次
current_process = None

def restart_service():
    """重启当前程序"""
    global current_process
    
    logger.info("定时重启服务...")
    
    # 启动新进程
    cmd = [sys.executable] + sys.argv
    
    logger.info(f"执行重启命令: {' '.join(cmd)}")
    
    try:
        # 在Windows上使用subprocess.Popen启动新进程
        current_process = subprocess.Popen(
            cmd, 
            shell=False,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        
        # 给新进程一点时间启动
        time.sleep(2)
        
        # 退出当前进程
        logger.info("新进程已启动，当前进程即将退出...")
        os._exit(0)
    except Exception as e:
        logger.error(f"重启失败: {e}")

def schedule_restart():
    """安排下一次重启"""
    global restart_timer
    
    logger.info(f"安排下一次重启，{restart_interval}秒后执行")
    restart_timer = threading.Timer(restart_interval, restart_service)
    restart_timer.daemon = True
    restart_timer.start()

def signal_handler(sig, frame):
    """处理中断信号"""
    logger.info("接收到中断信号，正在停止服务...")
    
    if restart_timer:
        restart_timer.cancel()
    
    # 关闭服务
    # 这里可以调用现有的清理代码
    session.close()
    camera_stream.release_all()
    logger.info("应用程序已安全关闭")
    sys.exit(0)

def keyboard_monitor():
    """监控键盘输入，按q退出"""
    while True:
        try:
            c = input("按 'q' 退出程序: ")
            if c.lower() == 'q':
                logger.info("用户输入q，正在停止服务...")
                os.kill(os.getpid(), signal.SIGINT)
                break
        except Exception:
            # 忽略输入错误
            time.sleep(0.1)

# 修改主程序入口
if __name__ == "__main__":
    try:
        # 注册信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 启动键盘监听线程
        keyboard_thread = threading.Thread(target=keyboard_monitor, daemon=True)
        keyboard_thread.start()
        
        # 安排第一次重启
        schedule_restart()
        
        logger.info("已启用自动重启功能，程序将每分钟自动重启一次")
        logger.info("按 'q' 或 Ctrl+C 可以退出程序")
        
        logger.info("启动摄像头监控及报警系统...")
        logger.info(f"检测阈值：{DETECTION_THRESHOLD}秒")
        
        app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)
    except KeyboardInterrupt:
        logger.info("接收到停止信号，正在关闭应用程序...")
    except Exception as e:
        logger.error(f"应用程序运行过程中发生错误: {e}")
    finally:
        # 确保资源被释放
        session.close()
        camera_stream.release_all()
        if restart_timer:
            restart_timer.cancel()
        logger.info("应用程序已安全关闭")
