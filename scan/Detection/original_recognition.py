"""Person and vehicle detection inputs, isolated from alarms and business writes.

Only source adaptation is new: no tracking, regions, baseline differences, model
training or synthetic alarms. Importing this module does not load a model/camera.
"""
from __future__ import annotations

import atexit
import base64
import hashlib
import io
import math
import os
import secrets
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import cv2
import numpy as np
from flask import Flask, Response, jsonify, request
from PIL import Image
from werkzeug.exceptions import RequestEntityTooLarge

ROOT = Path(__file__).resolve().parent
MODEL = ROOT / 'models' / 'yolov8l.pt'
EXPECTED_SHA256 = '18218ea4798da042d9862e6029ca9531adbd40ace19b6c9a75e2e28f1adf30cc'
CLASS_NAMES = {0: 'person', 2: 'car'}
COCO_CLASS_COUNT = 80
RAILAI_CLASSES = {0: 'obstacle', 1: 'person', 2: 'rail', 3: 'signal-and-sign', 4: 'vehicle'}
CURRENT_MODEL = 'current'
RAILAI_MODEL = 'railai'
DEFAULT_PROFILE = 'full640'
PROFILES = {'full640': 640, 'full1280': 1280}
CONFIDENCE = 0.25
NMS_IOU = 0.7
DEVICE = 'cpu'
ACTIVE = {'loading', 'running', 'paused', 'stopping'}
MAX_PIXELS = 16_000_000
ORIGINS = {'http://localhost:8080', 'http://127.0.0.1:8080',
           'http://localhost:8082', 'http://127.0.0.1:8082'}


class InputFailure(ValueError):
    """An actionable error known not to contain connection credentials."""


@dataclass(frozen=True)
class DetectionModel:
    key: str
    path: Path
    sha256: str
    classes: dict[int, str]
    iou: float
    checkpoint_class_count: int | None = None

    def metadata(self, profile):
        return {'modelId': self.key, 'model': self.path.name, 'modelSha256': self.sha256,
                'classes': list(self.classes.values()), 'profile': profile,
                'inputSize': PROFILES[profile], 'confidence': CONFIDENCE, 'iou': self.iou, 'device': DEVICE}


def detection_models():
    railai_path = os.getenv('RAILAI_DETECTION_MODEL_PATH')
    return {
        CURRENT_MODEL: DetectionModel(
            CURRENT_MODEL, MODEL, EXPECTED_SHA256, CLASS_NAMES, NMS_IOU,
            checkpoint_class_count=COCO_CLASS_COUNT,
        ),
        RAILAI_MODEL: DetectionModel(
            RAILAI_MODEL, Path(railai_path) if railai_path else ROOT / 'models' / 'yolov11_best.pt',
            os.getenv('RAILAI_DETECTION_SHA256', '').strip().lower(), RAILAI_CLASSES, 0.45,
        ),
    }


def railai_unavailable(model):
    if model.path.suffix.lower() != '.pt' or not model.path.is_file():
        return '尚未配置 RailAI-Vision 铁路检测权重（.pt）'
    if len(model.sha256) != 64 or any(ch not in '0123456789abcdef' for ch in model.sha256):
        return '尚未配置铁路检测权重的 SHA-256'
    return None


class Detector:
    """Load a configured checkpoint once, after verifying digest and class mapping."""
    def __init__(self, spec=None):
        self.spec = spec or detection_models()[CURRENT_MODEL]
        self.model = None

    def predict(self, frame, profile=DEFAULT_PROFILE):
        if self.model is None:
            if not self.spec.path.is_file():
                raise InputFailure(f'缺少检测权重 {self.spec.path.name}')
            with self.spec.path.open('rb') as stream:
                digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            if digest != self.spec.sha256:
                raise InputFailure('权重文件与配置的 SHA-256 不一致，请核对后重试')
            from ultralytics import YOLO
            model = YOLO(str(self.spec.path))
            classes = {index: str(label).strip().lower() for index, label in dict(model.names).items()}
            if self.spec.checkpoint_class_count is None:
                classes_match = classes == self.spec.classes
            else:
                classes_match = (len(classes) == self.spec.checkpoint_class_count
                                 and all(classes.get(index) == label for index, label in self.spec.classes.items()))
            if model.task != 'detect' or not classes_match:
                raise InputFailure('模型任务或类别顺序与所选检测方案不一致')
            self.model = model
        begin = time.perf_counter()
        result = self.model.predict(frame, conf=CONFIDENCE, iou=self.spec.iou,
                                    classes=list(self.spec.classes),
                                    imgsz=PROFILES[profile], device=DEVICE, verbose=False)[0]
        boxes = [{'label': self.spec.classes[int(cls)], 'confidence': float(conf),
                  'box': [round(float(v), 2) for v in xyxy]}
                 for xyxy, conf, cls in zip(result.boxes.xyxy.tolist(),
                                           result.boxes.conf.tolist(),
                                           result.boxes.cls.tolist())]
        annotated = result.plot()
        return annotated, boxes, (time.perf_counter() - begin) * 1000


def decode_image(data):
    if not data or len(data) > 16 * 1024 * 1024:
        raise ValueError('图片为空或超过16 MB')
    with Image.open(io.BytesIO(data)) as img:
        if img.width * img.height > MAX_PIXELS:
            raise ValueError('图片超过1600万像素，请缩小后重试')
        if img.format not in {'JPEG', 'PNG', 'WEBP', 'BMP'}:
            raise ValueError('仅支持 JPG、PNG、WebP、BMP 图片')
        # Normalize EXIF orientation so browser preview and inference agree.
        from PIL import ImageOps
        rgb = np.array(ImageOps.exif_transpose(img).convert('RGB'))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def read_camera(camera_id=None):
    """Read existing configuration only; never create tables or write alarms."""
    import pymysql
    import yaml
    import re
    config_file = ROOT.parent.parent / 'station-monitoring-banckend/src/main/resources/application.yaml'
    config = yaml.safe_load(config_file.read_text(encoding='utf-8'))
    ds = config['spring']['datasource']
    match = re.search(r'jdbc:mysql://([^:/?]+)(?::(\d+))?/([^?]+)', str(ds['url']))
    if not match:
        raise RuntimeError('无法读取已有摄像头数据库配置')
    with pymysql.connect(host=match[1], port=int(match[2] or 3306),
                         user=str(ds['username']), password=str(ds.get('password', '')),
                         database=match[3], cursorclass=pymysql.cursors.DictCursor,
                         connect_timeout=3, read_timeout=3) as conn:
        with conn.cursor() as cursor:
            if camera_id is None:
                cursor.execute('SELECT id, name FROM camera ORDER BY id')
                return cursor.fetchall()
            cursor.execute('SELECT id, name, ip, username, password FROM camera WHERE id=%s', (camera_id,))
            camera = cursor.fetchone()
            if not camera:
                raise ValueError('摄像头不存在，请先在摄像头管理中配置')
            return camera


def rtsp_source(camera):
    user, password = [quote(str(camera.get(k) or ''), safe='') for k in ('username', 'password')]
    # Match original Camera_Rtsp.py main stream. No arbitrary URL supplied by client.
    return f"rtsp://{user}:{password}@{camera['ip']}:554/cam/realmonitor?channel=1&subtype=0"


class Job:
    def __init__(self, mode, source, name, cleanup, profile, spec):
        self.id = secrets.token_hex(12)
        self.mode, self.source, self.name = mode, source, name
        self.cleanup = cleanup
        self.profile = profile
        self.spec = spec
        self.state, self.error = 'loading', None
        self.stop = threading.Event()
        self.paused = threading.Event()
        self.lock = threading.Lock()
        self.jpeg = None
        self.original_jpeg = None
        self.data = {'frameIndex': 0, 'mediaSeconds': None, 'totalFrames': None,
                     'sourceFps': None, 'counts': dict.fromkeys(spec.classes.values(), 0),
                     'detections': [], 'processingMs': None, 'completedHz': 0,
                     'frameUpdatedAt': None,
                     'inference': spec.metadata(profile),
                     'width': None, 'height': None, 'captureReleased': False}
        self.last_seen = time.monotonic()
        self.future = None

    def snapshot(self):
        self.last_seen = time.monotonic()
        with self.lock:
            return {'id': self.id, 'mode': self.mode, 'name': self.name,
                    'state': self.state, 'error': self.error, **self.data}


class Manager:
    def __init__(self, detector=None, capture_factory=None, railai_detector=None):
        self.models = detection_models()
        self.detectors = {
            CURRENT_MODEL: detector or Detector(self.models[CURRENT_MODEL]),
            RAILAI_MODEL: railai_detector or Detector(self.models[RAILAI_MODEL]),
        }
        self.capture_factory = capture_factory
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='original-recognition')
        self.lock = threading.Lock()
        self.job = None

    def start(self, mode, source, name, cleanup=None, profile=DEFAULT_PROFILE, model_id=CURRENT_MODEL):
        if not isinstance(profile, str) or profile not in PROFILES:
            raise InputFailure('识别配置不可用，请选择已支持的输入尺寸')
        if mode not in {'image', 'video'} and profile != DEFAULT_PROFILE:
            raise InputFailure('高分辨率复核仅支持图片和录像')
        if not isinstance(model_id, str) or model_id not in self.models:
            raise InputFailure('未知检测模型')
        spec = self.models[model_id]
        if model_id == RAILAI_MODEL:
            if mode not in {'image', 'video'}:
                raise InputFailure('铁路检测模型仅用于导入的图片和录像')
            if profile != DEFAULT_PROFILE:
                raise InputFailure('铁路检测模型使用项目配置的 640 输入')
            reason = railai_unavailable(spec)
            if reason:
                raise InputFailure(reason)
        with self.lock:
            if self.job and (self.job.future is None or not self.job.future.done()):
                raise RuntimeError('已有原版识别任务，请先停止并等待资源释放')
            job = Job(mode, source, name, cleanup, profile, spec)
            self.job = job
            job.future = self.executor.submit(self.work, job)
            return job

    def capture(self, job):
        if self.capture_factory:
            return self.capture_factory(job.source)
        if job.mode == 'usb':
            return cv2.VideoCapture(job.source, cv2.CAP_DSHOW)
        if job.mode == 'rtsp':
            return cv2.VideoCapture(job.source, cv2.CAP_FFMPEG,
                                    [cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000,
                                     cv2.CAP_PROP_READ_TIMEOUT_MSEC, 3000])
        return cv2.VideoCapture(job.source)

    def work(self, job):
        cap = None
        final_state = 'failed'
        completed, start, pause_total = 0, time.monotonic(), 0.0
        try:
            if job.mode != 'image':
                cap = self.capture(job)
                if not cap.isOpened():
                    raise InputFailure('无法打开输入：检查视频编码、摄像头编号或设备网络连接')
                w, h = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                if w * h > MAX_PIXELS:
                    raise InputFailure('视频分辨率超过1600万像素，请降低分辨率')
                fps = cap.get(cv2.CAP_PROP_FPS)
                fps = fps if math.isfinite(fps) and 0 < fps <= 240 else None
                total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                with job.lock:
                    job.data.update(sourceFps=fps, totalFrames=int(total) if math.isfinite(total) and total > 0 else None)
            else:
                fps = None
            while not job.stop.is_set():
                if job.mode in {'usb', 'rtsp'} and time.monotonic() - job.last_seen > 120:
                    raise InputFailure('页面已离开或连接中断，已自动停止并释放摄像头')
                if job.paused.is_set():
                    before = time.monotonic()
                    job.state = 'paused'
                    job.stop.wait(0.05)
                    pause_total += time.monotonic() - before
                    continue
                job.state = 'running'
                if job.mode == 'image':
                    frame = job.source
                else:
                    ok, frame = cap.read()
                    if not ok:
                        if job.mode != 'video':
                            raise InputFailure('摄像头断开或读取失败，请检查连接后重新启动')
                        # A failed decode before the declared end is not successful EOF.
                        total = job.data['totalFrames']
                        if not completed or (total and completed < total - 1):
                            raise InputFailure('视频未完整解码，请换用有效MP4/AVI文件或检查编码')
                        break
                if frame is None or frame.size == 0 or frame.shape[0] * frame.shape[1] > MAX_PIXELS:
                    raise InputFailure('无效画面或分辨率过大')
                annotated, detections, ms = self.detectors[job.spec.key].predict(frame, job.profile)
                ok, jpg = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 85])
                raw_ok, raw_jpg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if not ok or not raw_ok:
                    raise InputFailure('检测画面编码失败')
                completed += 1
                seconds = None
                if job.mode == 'video':
                    position = cap.get(cv2.CAP_PROP_POS_MSEC)
                    if math.isfinite(position) and (position > 0 or completed == 1 and position == 0):
                        seconds = position / 1000
                    elif fps:
                        seconds = (completed - 1) / fps
                with job.lock:
                    job.jpeg = jpg.tobytes()
                    job.original_jpeg = raw_jpg.tobytes()
                    job.data.update(frameIndex=completed, width=frame.shape[1], height=frame.shape[0],
                                    mediaSeconds=seconds,
                                    frameUpdatedAt=datetime.now(timezone.utc).isoformat(),
                                    counts={label: sum(d['label'] == label for d in detections) for label in job.spec.classes.values()},
                                    detections=detections, processingMs=round(ms, 2),
                                    completedHz=round(completed / max(time.monotonic() - start - pause_total, 0.001), 2))
                if job.mode == 'image':
                    break
                # Process each decoded video frame, slowing playback when inference is slow.
                # This is not sampling and not advertised as real-time throughput.
                if job.mode == 'video' and fps:
                    job.stop.wait(max(0, completed / fps - (time.monotonic() - start - pause_total)))
            final_state = 'stopped' if job.stop.is_set() else 'finished'
        except InputFailure as exc:
            job.error = str(exc)
        except Exception:
            # Do not send exception/RTSP text containing credentials to browser or logs.
            job.error = '识别失败：请检查输入格式、设备连接及检测权重。'
        finally:
            if cap is not None:
                cap.release()
            if job.cleanup:
                Path(job.cleanup).unlink(missing_ok=True)
            job.source = None
            with job.lock:
                job.data['captureReleased'] = True
                job.state = final_state

    def close(self):
        if self.job:
            self.job.stop.set()
        self.executor.shutdown(wait=True, cancel_futures=True)


def create_app(manager=None, camera_reader=read_camera):
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 513 * 1024 * 1024
    manager = manager or Manager()
    app.extensions['original_manager'] = manager
    token = secrets.token_urlsafe(32)

    @app.before_request
    def guard():
        if request.remote_addr not in {'127.0.0.1', '::1', None}:
            return jsonify(success=False, message='仅允许本机访问'), 403
        if request.host not in {'localhost', '127.0.0.1', 'localhost:5002', '127.0.0.1:5002'}:
            return jsonify(success=False, message='无效访问主机'), 403
        if request.headers.get('Origin') and request.headers['Origin'] not in ORIGINS:
            return jsonify(success=False, message='不允许的网页来源'), 403
        if request.method == 'OPTIONS':
            return Response(status=204)
        if request.method != 'GET' and not secrets.compare_digest(request.headers.get('X-Original-Token', ''), token):
            return jsonify(success=False, message='页面会话已更新，请刷新后重试'), 403

    @app.after_request
    def cors(response):
        origin = request.headers.get('Origin')
        if origin in ORIGINS:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Vary'] = 'Origin'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Original-Token'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

    @app.errorhandler(RequestEntityTooLarge)
    def too_big(_):
        return jsonify(success=False, message='视频超过512 MB，请先截取较短片段'), 413

    @app.get('/original/config')
    def config():
        railai = manager.models[RAILAI_MODEL]
        railai_reason = railai_unavailable(railai)
        return jsonify(success=True, token=token, model=MODEL.name, classes=list(CLASS_NAMES.values()),
                       modelSha256=EXPECTED_SHA256, confidence=CONFIDENCE, iou=NMS_IOU,
                       inputSize=PROFILES[DEFAULT_PROFILE], device=DEVICE,
                       profiles=[{'id': profile, 'inputSize': size} for profile, size in PROFILES.items()],
                       railai={'configured': railai_reason is None, 'reason': railai_reason,
                               **railai.metadata(DEFAULT_PROFILE)},
                       defaultProfile=DEFAULT_PROFILE, alarmsEnabled=False, trackingEnabled=False)

    @app.get('/original/cameras')
    def cameras():
        try:
            return jsonify(success=True, data=camera_reader())
        except Exception:
            return jsonify(success=False, message='无法读取设备列表，请确认MySQL和摄像头配置；图片和本地视频不受影响'), 503

    @app.post('/original/jobs')
    def start():
        cleanup = None
        try:
            payload = request.get_json(silent=True) or request.form
            mode = payload.get('mode')
            profile = payload.get('profile', DEFAULT_PROFILE)
            model_id = payload.get('modelId', CURRENT_MODEL)
            if mode in {'image', 'video'}:
                upload = request.files.get('file')
                if not upload or not upload.filename:
                    raise ValueError('请先选择文件')
                name = upload.filename.replace('\\', '/').split('/')[-1][:120]
                if mode == 'image':
                    source = decode_image(upload.read(16 * 1024 * 1024 + 1))
                else:
                    suffix = Path(name).suffix.lower()
                    if suffix not in {'.mp4', '.avi', '.mov', '.mkv', '.webm'}:
                        raise ValueError('支持 MP4、AVI、MOV、MKV、WebM 视频')
                    folder = ROOT / '.original-inputs'
                    folder.mkdir(exist_ok=True)
                    with tempfile.NamedTemporaryFile(dir=folder, suffix=suffix, delete=False) as f:
                        cleanup = f.name
                        size = 0
                        while chunk := upload.stream.read(1024 * 1024):
                            size += len(chunk)
                            if size > 512 * 1024 * 1024:
                                raise ValueError('视频超过512 MB，请先截取片段')
                            f.write(chunk)
                    if size == 0:
                        raise ValueError('视频文件为空')
                    source = cleanup
            elif mode == 'usb':
                value = payload.get('deviceIndex', 0)
                if isinstance(value, bool) or str(value) not in [str(i) for i in range(10)]:
                    raise ValueError('本机摄像头编号必须为0—9')
                source, name = int(value), f'本机摄像头 {value}'
            elif mode == 'rtsp':
                try:
                    camera_id = int(payload.get('cameraId', 0))
                except (ValueError, TypeError):
                    raise ValueError('请选择已配置的网络摄像头')
                camera = camera_reader(camera_id)
                source, name = rtsp_source(camera), camera.get('name') or f'摄像头 {camera_id}'
            else:
                raise ValueError('不支持的输入方式')
            job = manager.start(mode, source, name, cleanup, profile=profile, model_id=model_id)
            return jsonify(success=True, data=job.snapshot()), 202
        except ValueError as exc:
            if cleanup:
                Path(cleanup).unlink(missing_ok=True)
            return jsonify(success=False, message=str(exc)), 400
        except RuntimeError as exc:
            if cleanup:
                Path(cleanup).unlink(missing_ok=True)
            return jsonify(success=False, message=str(exc)), 409
        except Exception:
            if cleanup:
                Path(cleanup).unlink(missing_ok=True)
            return jsonify(success=False, message='输入读取失败，请检查文件、数据库或设备配置'), 400

    def get_job(job_id):
        job = manager.job
        return job if job and secrets.compare_digest(job.id, job_id) else None

    @app.get('/original/jobs/<job_id>')
    def status(job_id):
        job = get_job(job_id)
        if not job:
            return jsonify(success=False, message='任务不存在或服务已重启'), 404
        return jsonify(success=True, data=job.snapshot())

    @app.get('/original/jobs/<job_id>/frame')
    def frame(job_id):
        job = get_job(job_id)
        if not job or not job.jpeg:
            return Response(status=404)
        return Response(job.jpeg, mimetype='image/jpeg')

    @app.get('/original/jobs/<job_id>/snapshot')
    def snapshot(job_id):
        job = get_job(job_id)
        if not job:
            return jsonify(success=False, message='任务不存在或服务已重启'), 404
        since = request.args.get('after', 0, type=int)
        job.last_seen = time.monotonic()
        with job.lock:
            data = {'id': job.id, 'mode': job.mode, 'name': job.name, 'state': job.state,
                    'error': job.error, **job.data}
            original = job.original_jpeg if job.data['frameIndex'] != since else None
        if original is not None:
            data['originalJpeg'] = base64.b64encode(original).decode('ascii')
        return jsonify(success=True, data=data)

    @app.post('/original/jobs/<job_id>/<action>')
    def control(job_id, action):
        job = get_job(job_id)
        if not job:
            return jsonify(success=False, message='任务不存在'), 404
        if action == 'stop':
            job.stop.set()
        elif action in {'pause', 'resume'} and job.mode == 'video' and job.state in ACTIVE:
            job.paused.set() if action == 'pause' else job.paused.clear()
        else:
            return jsonify(success=False, message='此任务不支持该操作'), 400
        return jsonify(success=True, data=job.snapshot())

    return app


if __name__ == '__main__':
    application = create_app()
    atexit.register(application.extensions['original_manager'].close)
    application.run(host='127.0.0.1', port=5002, debug=False, use_reloader=False, threaded=True)
