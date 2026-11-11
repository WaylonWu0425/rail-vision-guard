"""Loopback-only image/frame inference API for the supplied NCNN weights."""
import base64
import json
import subprocess
import tempfile
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading

from coupler_inference import CouplerDetector, LABELS
import imageio_ffmpeg
import cv2
import numpy as np

detector = None
lock = threading.Lock()
ORIGINS = {'http://localhost:8080', 'http://127.0.0.1:8080',
           'http://localhost:8082', 'http://127.0.0.1:8082'}


class Handler(BaseHTTPRequestHandler):
    def respond(self, code, data):
        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        if self.headers.get('Origin') in ORIGINS:
            self.send_header('Access-Control-Allow-Origin', self.headers['Origin'])
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        if self.headers.get('Origin') not in ORIGINS:
            self.send_error(403)
            return
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', self.headers['Origin'])
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/health':
            self.respond(200, {'ready': detector is not None, 'model': 'best12_20',
                               'classes': list(LABELS)})
        else:
            self.respond(404, {'error': '未知路径'})

    def do_POST(self):
        if self.path not in ('/predict', '/transcode') or self.headers.get('Origin') not in ORIGINS:
            self.respond(403, {'error': '仅接受本地工作区的识别请求'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if self.path == '/transcode':
                self.transcode(length)
                return
            if not 0 < length <= 16 * 1024 * 1024:
                raise ValueError('图片为空或超过 16 MB')
            data = np.frombuffer(self.rfile.read(length), dtype=np.uint8)
            frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
            if frame is None or frame.shape[0] * frame.shape[1] > 16_000_000:
                raise ValueError('无法解码图片或分辨率超过 1600 万像素')
            with lock:
                objects, elapsed = detector.predict(frame)
            annotated = frame.copy()
            for obj in objects:
                x1, y1, x2, y2 = map(int, obj['box'])
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (54, 194, 233), 2)
                cv2.putText(annotated, f"{obj['label']} {obj['confidence']:.2f}",
                            (x1, max(20, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, .6, (54, 194, 233), 2)
            ok, jpg = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ok:
                raise RuntimeError('无法编码结果画面')
            self.respond(200, {'detections': objects, 'processingMs': round(elapsed, 1),
                               'frame': 'data:image/jpeg;base64,' + base64.b64encode(jpg).decode('ascii')})
        except Exception as exc:
            self.respond(400, {'error': str(exc)})

    def transcode(self, length):
        if not 0 < length <= 512 * 1024 * 1024:
            raise ValueError('视频为空或超过 512 MB')
        with tempfile.TemporaryDirectory(prefix='rail-coupler-video-') as directory:
            source = Path(directory) / 'input.video'
            output = Path(directory) / 'browser.mp4'
            with source.open('wb') as target:
                remaining = length
                while remaining:
                    chunk = self.rfile.read(min(1024 * 1024, remaining))
                    if not chunk:
                        raise ValueError('视频上传不完整')
                    target.write(chunk)
                    remaining -= len(chunk)
            command = [imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error',
                       '-i', str(source), '-map', '0:v:0', '-map', '0:a:0?',
                       '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'veryfast',
                       '-crf', '23', '-c:a', 'aac', '-movflags', '+faststart', '-y', str(output)]
            try:
                result = subprocess.run(command, capture_output=True, timeout=180, check=False,
                                        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            except subprocess.TimeoutExpired as exc:
                raise ValueError('视频转换超时，请截取较短片段后重试') from exc
            if result.returncode or not output.exists():
                raise ValueError('无法转换该视频格式，请换用 MP4/H.264 文件')
            size = output.stat().st_size
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', self.headers['Origin'])
            self.send_header('Content-Type', 'video/mp4')
            self.send_header('Content-Length', str(size))
            self.end_headers()
            with output.open('rb') as stream:
                while chunk := stream.read(1024 * 1024):
                    self.wfile.write(chunk)


if __name__ == '__main__':
    detector = CouplerDetector()
    print('Coupler NCNN service: http://127.0.0.1:5003', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 5003), Handler).serve_forever()
