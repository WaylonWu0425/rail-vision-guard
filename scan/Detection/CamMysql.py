from flask import Flask, jsonify
from flask_cors import CORS
import cv2
import base64
from ultralytics import YOLO
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow all cross-origin requests

# MySQL database configuration
DATABASE_URL = "mysql+pymysql://root:admin@localhost/station_monitoring"
try:
    engine = create_engine(DATABASE_URL, echo=True)  # echo=True for debugging
except Exception as e:
    print(f"Database connection failed: {e}")
    raise

# Use the updated declarative_base for SQLAlchemy 2.0+
Base = declarative_base()

# Define Camera model based on your table structure
class Camera(Base):
    __tablename__ = 'camera'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))  # 添加长度
    product_number = Column(Integer)
    status = Column(String(10))  # 添加长度
    ip = Column(String(45))  # IP 地址最大 45 字符
    type = Column(Integer)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow)
    port = Column(Integer)
    username = Column(String(50))  # 用户名最长 50
    password = Column(String(255))  # 密码最长 255
    bridgeType = Column(Integer)
    initViewPoint = Column(Integer)
# Create tables if they don't exist
try:
    Base.metadata.create_all(engine)
except Exception as e:
    print(f"Failed to create tables: {e}")
    raise

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Load YOLOv8 model
path = 'models/best.pt'
try:
    model = YOLO(path)
except Exception as e:
    print(f"Failed to load YOLO model: {e}")
    raise

def get_online_cameras():
    """Retrieve all online cameras (status = 0x00) from the database."""
    try:
        return session.query(Camera).filter(Camera.status == '0x00').all()
    except Exception as e:
        print(f"Error querying online cameras: {e}")
        return []

def generate_rtsp_url(camera):
    """Generate RTSP URL from camera details."""
    return f"rtsp://{camera.username}:{camera.password}@{camera.ip}/cam/realmonitor?channel=1&subtype=0"

def generate_frame(rtsp_url):
    """Generate a single frame from the RTSP stream and process it with YOLO."""
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print(f"Failed to open RTSP stream: {rtsp_url}")
        return None

    ret, frame = cap.read()
    if ret:
        # Perform YOLO inference
        try:
            results = model(frame)
            # Draw YOLO results on the frame
            annotated_frame = results[0].plot()
            # Convert to Base64
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if ret:
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                cap.release()
                return frame_base64
        except Exception as e:
            print(f"YOLO inference failed: {e}")

    cap.release()
    return None

@app.route('/video_feed/<int:camera_id>', methods=['GET'])
def video_feed(camera_id):
    """Serve video feed for a specific camera by ID."""
    camera = session.query(Camera).filter(Camera.id == camera_id, Camera.status == '0x00').first()
    if not camera:
        return jsonify({'error': 'Camera not found or offline'}), 404

    rtsp_url = generate_rtsp_url(camera)
    frame_base64 = generate_frame(rtsp_url)
    if frame_base64:
        return jsonify({'image': frame_base64, 'camera_name': camera.name})
    return jsonify({'error': 'Failed to retrieve frame'}), 500

@app.route('/video_feed', methods=['GET'])
def video_feed_default():
    """Serve video feed for the first online camera if no ID is provided."""
    cameras = get_online_cameras()
    if not cameras:
        return jsonify({'error': 'No online cameras available'}), 404

    # Default to the first online camera
    camera = cameras[0]
    rtsp_url = generate_rtsp_url(camera)
    frame_base64 = generate_frame(rtsp_url)
    if frame_base64:
        return jsonify({'image': frame_base64, 'camera_name': camera.name})
    return jsonify({'error': 'Failed to retrieve frame'}), 500

@app.route('/online_cameras', methods=['GET'])
def online_cameras():
    """Return a list of online cameras."""
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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)