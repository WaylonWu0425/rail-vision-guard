"""Local NCNN inference for supplied freight-car/coupler weights. No alarm writes."""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.ncnn-runtime'))
import cv2
import ncnn
import numpy as np

MODEL = ROOT.parent.parent.parent / '模型'
LABELS = ('freight car', 'coupler_far', 'couplers', 'coupler_near')


class CouplerDetector:
    def __init__(self):
        self.net = ncnn.Net()
        if self.net.load_param(str(MODEL / 'best12_20.param')) != 0:
            raise RuntimeError('无法加载老师提供的 NCNN 参数文件')
        if self.net.load_model(str(MODEL / 'best12_20.bin')) != 0:
            raise RuntimeError('无法加载老师提供的 NCNN 权重文件')

    def predict(self, bgr, confidence=0.45):
        start = time.perf_counter()
        h, w = bgr.shape[:2]
        ratio = min(640 / w, 640 / h)
        nw, nh = round(w * ratio), round(h * ratio)
        scaled = cv2.resize(bgr, (nw, nh))
        left, top = (640 - nw) // 2, (640 - nh) // 2
        padded = cv2.copyMakeBorder(scaled, top, 640 - nh - top, left, 640 - nw - left,
                                    cv2.BORDER_CONSTANT, value=(114, 114, 114))
        mat = ncnn.Mat.from_pixels(padded, ncnn.Mat.PixelType.PIXEL_BGR, 640, 640)
        mat.substract_mean_normalize([], [1 / 255] * 3)
        ex = self.net.create_extractor()
        if ex.input('images', mat) != 0:
            raise RuntimeError('模型输入失败')
        status, output = ex.extract('output0')
        if status != 0:
            raise RuntimeError('模型输出失败')
        raw = np.asarray(output).reshape(-1, 68)
        if raw.shape != (8400, 68):
            raise RuntimeError(f'模型输出形状异常：{raw.shape}')
        logits = np.clip(raw[:, 64:], -30, 30)
        scores = 1 / (1 + np.exp(-logits))
        best_class = scores.argmax(axis=1)
        best_score = scores[np.arange(len(raw)), best_class]
        selected = np.flatnonzero(best_score >= confidence)
        if len(selected) == 0:
            return [], (time.perf_counter() - start) * 1000
        selected = selected[np.argsort(best_score[selected])[-1000:]]
        box_logits = raw[selected, :64].reshape(-1, 4, 16)
        box_logits -= box_logits.max(axis=2, keepdims=True)
        probs = np.exp(box_logits)
        distances = (probs / probs.sum(axis=2, keepdims=True) * np.arange(16)).sum(axis=2)
        centers = []
        strides = []
        for stride in (8, 16, 32):
            size = 640 // stride
            y, x = np.indices((size, size))
            centers.append(np.stack((x.ravel() + .5, y.ravel() + .5), axis=1) * stride)
            strides.append(np.full(size * size, stride))
        center = np.concatenate(centers)[selected]
        scale = np.concatenate(strides)[selected, None]
        xyxy = np.concatenate((center - distances[:, :2] * scale,
                               center + distances[:, 2:] * scale), axis=1)
        xyxy[:, [0, 2]] = np.clip((xyxy[:, [0, 2]] - left) / ratio, 0, w)
        xyxy[:, [1, 3]] = np.clip((xyxy[:, [1, 3]] - top) / ratio, 0, h)
        detections = []
        for cls in range(4):
            idx = np.flatnonzero(best_class[selected] == cls)
            if not len(idx):
                continue
            boxes = [[float(a), float(b), float(c-a), float(d-b)] for a, b, c, d in xyxy[idx]]
            keep = cv2.dnn.NMSBoxes(boxes, best_score[selected[idx]].tolist(), confidence, .5)
            for local in np.asarray(keep).reshape(-1):
                i = idx[int(local)]
                detections.append({'classId': cls, 'label': LABELS[cls],
                                   'confidence': round(float(best_score[selected[i]]), 4),
                                   'box': [round(float(v), 1) for v in xyxy[i]]})
        return sorted(detections, key=lambda item: -item['confidence']), (time.perf_counter() - start) * 1000
