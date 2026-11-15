"""Loopback-only image/frame inference API for the supplied NCNN weights."""
import base64
import json
import subprocess
import tempfile
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import os
import secrets
import shutil
import time
from urllib.parse import parse_qs, urlsplit

from coupler_inference import CouplerDetector, LABELS
from coupler_ranging import compare, estimate
import imageio_ffmpeg
import cv2
import numpy as np

detector = None
lock = threading.Lock()
MEDIA_DIR = Path(tempfile.gettempdir()) / 'rail-coupler-browser-media'
MEDIA_DIR.mkdir(exist_ok=True)
ORIGINS = {'http://localhost:8080', 'http://127.0.0.1:8080',
           'http://localhost:8082', 'http://127.0.0.1:8082'}
RANGING_ROUTES = ('/ranging/compare', '/ranging/estimate')


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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_DELETE(self):
        token = self.path.removeprefix('/media/')
        if not self.path.startswith('/media/') or self.headers.get('Origin') not in ORIGINS \
                or len(token) != 32 or any(char not in '0123456789abcdef' for char in token):
            self.respond(403, {'error': '无效媒体请求'})
            return
        (MEDIA_DIR / (token + '.mp4')).unlink(missing_ok=True)
        self.respond(200, {'released': True})

    def do_GET(self):
        if self.path.startswith('/media/'):
            self.serve_media(self.path.removeprefix('/media/'))
        elif self.path == '/health':
            self.respond(200, {'ready': detector is not None, 'model': 'best12_20',
                               'classes': list(LABELS), 'profiles': ['web640', 'apk320'],
                               'ranging': 'rail-coupler-ranging-v1'})
        else:
            self.respond(404, {'error': '未知路径'})

    def serve_media(self, token):
        if len(token) != 32 or any(char not in '0123456789abcdef' for char in token):
            self.send_error(404)
            return
        path = MEDIA_DIR / (token + '.mp4')
        if not path.is_file():
            self.send_error(404)
            return
        size = path.stat().st_size
        start, end = 0, size - 1
        requested = self.headers.get('Range', '')
        if requested:
            try:
                unit, values = requested.split('=', 1)
                first, last = values.split('-', 1)
                if unit != 'bytes' or not first: raise ValueError()
                start = int(first)
                end = min(size - 1, int(last)) if last else size - 1
                if start < 0 or start > end or start >= size: raise ValueError()
            except ValueError:
                self.send_response(416)
                self.send_header('Content-Range', f'bytes */{size}')
                self.end_headers()
                return
        self.send_response(206 if requested else 200)
        if self.headers.get('Origin') in ORIGINS:
            self.send_header('Access-Control-Allow-Origin', self.headers['Origin'])
        self.send_header('Content-Type', 'video/mp4')
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(end - start + 1))
        if requested: self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.end_headers()
        with path.open('rb') as stream:
            stream.seek(start)
            remaining = end - start + 1
            while remaining:
                chunk = stream.read(min(1024 * 1024, remaining))
                if not chunk: break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def do_POST(self):
        route = urlsplit(self.path)
        if route.path not in ('/predict', '/transcode', '/transcode-link', *RANGING_ROUTES) or self.headers.get('Origin') not in ORIGINS:
            self.respond(403, {'error': '仅接受本地工作区的识别请求'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if route.path in ('/transcode', '/transcode-link'):
                self.transcode(length, as_link=route.path == '/transcode-link')
                return
            if route.path in RANGING_ROUTES:
                if not 0 < length <= 256 * 1024:
                    raise ValueError('测距请求为空或超过 256 KB')
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError('测距请求格式错误')
                archive = payload.get('archive')
                result = compare(archive)[1] if route.path.endswith('/compare') else estimate(archive, payload.get('frame'))
                self.respond(200, result)
                return
            if not 0 < length <= 16 * 1024 * 1024:
                raise ValueError('图片为空或超过 16 MB')
            data = np.frombuffer(self.rfile.read(length), dtype=np.uint8)
            frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
            if frame is None or frame.shape[0] * frame.shape[1] > 16_000_000:
                raise ValueError('无法解码图片或分辨率超过 1600 万像素')
            profile = parse_qs(route.query).get('profile', ['web640'])[0]
            with lock:
                objects, elapsed = detector.predict(frame, profile=profile)
            annotated = frame.copy()
            for obj in objects:
                x1, y1, x2, y2 = map(int, obj['box'])
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (54, 194, 233), 2)
                cv2.putText(annotated, f"{obj['label']} {obj['confidence']:.2f}",
                            (x1, max(20, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, .6, (54, 194, 233), 2)
            ok, jpg = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ok:
                raise RuntimeError('无法编码结果画面')
            self.respond(200, {'detections': objects, 'processingMs': round(elapsed, 1), 'profile': profile,
                               'frame': 'data:image/jpeg;base64,' + base64.b64encode(jpg).decode('ascii')})
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            return
        except Exception as exc:
            self.respond(400, {'error': str(exc)})

    def transcode(self, length, as_link=False):
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
            supplied_ffmpeg = Path(os.environ.get('RAIL_FFMPEG_PATH') or '')
            ffmpeg = str(supplied_ffmpeg) if supplied_ffmpeg.is_file() else imageio_ffmpeg.get_ffmpeg_exe()
            command = [ffmpeg, '-nostdin', '-hide_banner', '-loglevel', 'error',
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
            if as_link:
                for previous in MEDIA_DIR.glob('*.mp4'):
                    if time.time() - previous.stat().st_mtime > 3600:
                        previous.unlink(missing_ok=True)
                token = secrets.token_hex(16)
                shutil.move(str(output), str(MEDIA_DIR / (token + '.mp4')))
                self.respond(200, {'url': f'http://127.0.0.1:5003/media/{token}', 'bytes': size})
                return
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
