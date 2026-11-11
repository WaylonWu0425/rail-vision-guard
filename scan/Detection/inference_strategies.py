"""Shared full-frame/tiled inference. No database or service imports."""
from __future__ import annotations

import numpy as np

STRATEGIES = {"full640": 640, "full1280": 1280, "tiled640": 640}


def starts(length, tile=960, overlap=0.2):
    if length <= tile:
        return [0]
    positions = list(range(0, length - tile + 1, int(tile * (1 - overlap))))
    if positions[-1] != length - tile:
        positions.append(length - tile)
    return positions


def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    union = max(0, a[2] - a[0]) * max(0, a[3] - a[1]) + max(0, b[2] - b[0]) * max(0, b[3] - b[1]) - intersection
    return intersection / union if union else 0.0


def nms(rows, threshold=0.5):
    pending = sorted(rows, key=lambda r: r[4], reverse=True)
    kept = []
    while pending:
        best = pending.pop(0)
        kept.append(best)
        pending = [r for r in pending if r[5] != best[5] or iou(r, best) <= threshold]
    return np.asarray(kept, dtype=np.float32).reshape(-1, 6)


def predict_boxes(model, frame, strategy="full640", confidence=0.45, device="cpu", half=False):
    """Return Ultralytics Boxes in original coordinates; caller tracks once."""
    from ultralytics.engine.results import Boxes
    from ultralytics.cfg import DEFAULT_CFG_DICT

    if strategy not in STRATEGIES:
        raise ValueError(f"Unknown detection strategy: {strategy}")
    height, width = frame.shape[:2]
    regions = [(0, 0, width, height)]
    if strategy == "tiled640":
        regions = [(x, y, min(x + 960, width), min(y + 960, height))
                   for y in starts(height) for x in starts(width)]
    rows = []
    for x, y, right, bottom in regions:
        options = dict(source=frame[y:bottom, x:right], conf=confidence,
                       imgsz=STRATEGIES[strategy], verbose=False, device=device)
        if half:
            options.update({"quantize": 16} if "quantize" in DEFAULT_CFG_DICT else {"half": True})
        results = model.predict(**options)
        boxes = results[0].boxes
        if boxes is None:
            continue
        for row in boxes.cpu().numpy().data:
            x1, y1, x2, y2, score, cls = row[:6]
            translated = [max(0, min(width, x1 + x)), max(0, min(height, y1 + y)),
                          max(0, min(width, x2 + x)), max(0, min(height, y2 + y)), score, cls]
            if translated[2] > translated[0] and translated[3] > translated[1]:
                rows.append(translated)
    data = nms(rows) if strategy == "tiled640" else np.asarray(rows, dtype=np.float32).reshape(-1, 6)
    return Boxes(data, (height, width))
