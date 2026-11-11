"""Local-only sample preparation, human review and reviewed-only evaluation."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import time
import threading
import uuid

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from inference_strategies import STRATEGIES, iou, predict_boxes


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def image(path):
    frame = cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError(f"Cannot decode {path}")
    return frame


def prepare(args):
    root = args.dataset
    if (root / "manifest.json").exists():
        raise ValueError("Dataset exists; refusing to overwrite review work")
    (root / "images").mkdir(parents=True, exist_ok=True)
    entries, sources = [], []
    # Split whole sources, never adjacent frames. No training in this round.
    for number, path in enumerate(sorted(args.videos.iterdir())):
        if path.suffix.lower() not in {".avi", ".mp4"}:
            continue
        cap = cv2.VideoCapture(str(path))
        try:
            count, fps = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), cap.get(cv2.CAP_PROP_FPS)
            if not cap.isOpened() or count <= 0 or fps <= 0:
                raise ValueError(f"Invalid video {path}")
            source_id = path.stem
            split = "test" if "飞书" in path.name or "环境" in path.name else "tune"
            sha = digest(path)
            sources.append(dict(path=str(path), sha256=sha, group=source_id, split=split))
            for index in np.linspace(0, count - 1, 20, dtype=int):
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(index))
                ok, frame = cap.read()
                if not ok:
                    raise ValueError(f"Decode failed: {path} frame {index}")
                key = f"video_{number:02}_{int(index):06}"
                cv2.imencode(".jpg", frame)[1].tofile(str(root / "images" / (key + ".jpg")))
                entries.append(dict(id=key, image=key + ".jpg", source=str(path), sourceSha256=sha,
                                    group=source_id, split=split, seconds=round(int(index) / fps, 3),
                                    width=frame.shape[1], height=frame.shape[0], priority=False))
        finally:
            cap.release()
    excluded = []
    for path in sorted(args.photos.iterdir()):
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            continue
        if path.stem in {"20261016-162715", "20261016-162721"}:
            excluded.append(dict(path=str(path), sha256=digest(path), reason="Existing detection overlays; display evidence only"))
            continue
        frame = image(path)
        key = "photo_" + path.stem
        cv2.imencode(".jpg", frame)[1].tofile(str(root / "images" / (key + ".jpg")))
        # All photos kept together conservatively, including similar backgrounds.
        entries.append(dict(id=key, image=key + ".jpg", source=str(path), sourceSha256=digest(path),
                            group="photos_same_source_unknown", split="test", seconds=None,
                            width=frame.shape[1], height=frame.shape[0], priority=True,
                            provenance="User confirmed original surveillance" if path.stem == "20261016-162712" else "User provided"))
    write(root / "manifest.json", dict(version=1, note="Small-sample case validation; no generalization claim", sources=sources,
                                        excluded=excluded, entries=entries))
    prioritize(args)
    print(f"Prepared {len(entries)} images; priority=10")


def prioritize(args):
    manifest = read(args.dataset / "manifest.json")
    entries = manifest["entries"]
    for entry in entries:
        entry["priority"] = entry["seconds"] is None
    groups = sorted(set(e["group"] for e in entries if e["seconds"] is not None),
                    key=lambda g: (0 if "飞书" in g else 1 if "环境" in g else 2, g))
    for group in groups:
        group_entries = sorted([e for e in entries if e["group"] == group], key=lambda e:e["seconds"])
        selected = [group_entries[0], group_entries[-1]] if "飞书" in group or "环境" in group else [group_entries[0]]
        for entry in selected:
            if sum(e["priority"] for e in entries) < 10:
                entry["priority"] = True
    entries.sort(key=lambda e: (not e["priority"], e["id"]))
    write(args.dataset / "manifest.json", manifest)


def prelabel(args):
    from ultralytics import YOLO
    model = YOLO(str(args.model))
    manifest = read(args.dataset / "manifest.json")
    for entry in manifest["entries"]:
        if args.priority and not entry["priority"]:
            continue
        path = args.dataset / "annotations" / (entry["id"] + ".json")
        if path.exists():
            continue
        boxes = predict_boxes(model, image(args.dataset / "images" / entry["image"]), "full640", 0.45, "cpu")
        persons = [r[:4].tolist() for r in boxes.data if str(model.names[int(r[5])]).lower() == "person"]
        write(path, dict(reviewed=False, empty=False, boxes=persons, ignore=[],
                         prelabel=dict(strategy="full640", confidence=0.45, modelSha256=digest(args.model))))
        print(entry["id"], len(persons), "unreviewed", flush=True)


def validate_annotation(payload, entry):
    if not isinstance(payload, dict):
        raise ValueError("Invalid annotation")
    result = {}
    for key in ("boxes", "ignore"):
        values = payload.get(key, [])
        if not isinstance(values, list) or len(values) > 1000:
            raise ValueError("Invalid rectangles")
        for box in values:
            if not isinstance(box, list) or len(box) != 4 or any(type(v) not in (int, float) or not np.isfinite(v) for v in box):
                raise ValueError("Invalid coordinates")
            x1, y1, x2, y2 = box
            if not (0 <= x1 < x2 <= entry["width"] and 0 <= y1 < y2 <= entry["height"]):
                raise ValueError("Rectangle outside image")
        result[key] = values
    result["reviewed"] = payload.get("reviewed") is True
    result["empty"] = payload.get("empty") is True
    if result["reviewed"] and not result["boxes"] and not result["empty"]:
        raise ValueError("无人员时请明确勾选“确认无人”")
    if result["empty"] and result["boxes"]:
        raise ValueError("有人员框时不能确认无人")
    return result


def create_app(args):
    from flask import Flask, abort, jsonify, request, send_from_directory
    app = Flask(__name__)
    token = uuid.uuid4().hex
    app.config["REVIEW_TOKEN"] = token
    app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
    manifest = read(args.dataset / "manifest.json")
    entries = {e["id"]: e for e in manifest["entries"]}
    review_lock = threading.RLock()

    @app.before_request
    def local_only():
        if request.host not in {f"127.0.0.1:{args.port}", f"localhost:{args.port}"}:
            abort(403)
        if request.method == "POST":
            if request.headers.get("Origin") not in {f"http://127.0.0.1:{args.port}", f"http://localhost:{args.port}"}:
                return jsonify(error="保存来源校验失败，请从本机工作台地址打开页面", code="origin_rejected"), 403
            if request.headers.get("X-Review-Token") != token:
                return jsonify(error="服务重启后会话已更新，正在重新获取保存凭证", code="token_expired"), 403

    @app.after_request
    def no_stale_session(response):
        if request.path in {"/", "/session", "/manifest"} or request.path.startswith("/annotation/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/session")
    def session():
        if request.headers.get("Sec-Fetch-Site") not in {None, "none", "same-origin"}:
            abort(403)
        if request.headers.get("Origin") not in {None, f"http://127.0.0.1:{args.port}", f"http://localhost:{args.port}"}:
            abort(403)
        return jsonify(token=token)

    @app.get("/")
    def index():
        return (HERE / "review.html").read_text(encoding="utf-8").replace("__TOKEN__", token)

    @app.get("/manifest")
    def get_manifest():
        return jsonify(manifest)

    @app.get("/image/<key>")
    def get_image(key):
        if key not in entries:
            abort(404)
        return send_from_directory(args.dataset / "images", entries[key]["image"])

    @app.route("/annotation/<key>", methods=["GET", "POST"])
    def annotation(key):
        with review_lock:
            return handle_annotation(key)

    def handle_annotation(key):
        if key not in entries:
            abort(404)
        path = args.dataset / "annotations" / (key + ".json")
        if request.method == "GET":
            return jsonify(read(path) if path.exists() else dict(boxes=[], ignore=[], reviewed=False, empty=False))
        try:
            data = validate_annotation(request.get_json(), entries[key])
        except (ValueError, TypeError) as exc:
            return jsonify(error=str(exc)), 400
        previous = read(path) if path.exists() else {}
        data["prelabel"] = previous.get("prelabel")
        data["reviewedAt"] = time.strftime("%Y-%m-%dT%H:%M:%S%z") if data["reviewed"] else None
        if path.exists():
            archive = args.dataset / "history" / key / (str(time.time_ns()) + ".json")
            write(archive, previous)
        write(path, data)
        entry = entries[key]
        labels = args.dataset / "labels" / (key + ".txt")
        labels.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        for x1, y1, x2, y2 in data["boxes"]:
            lines.append(f"0 {(x1+x2)/2/entry['width']:.8f} {(y1+y2)/2/entry['height']:.8f} {(x2-x1)/entry['width']:.8f} {(y2-y1)/entry['height']:.8f}")
        labels.write_text("\n".join(lines), encoding="utf-8")
        return jsonify(saved=True, reviewed=data["reviewed"])

    return app


def serve(args):
    from werkzeug.serving import WSGIRequestHandler
    class LocalRequestHandler(WSGIRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(15)
    create_app(args).run(host="127.0.0.1", port=args.port, threaded=True,
                         request_handler=LocalRequestHandler, debug=False)


def score(predictions, annotation):
    truth = annotation["boxes"]
    matched, ignored, false = set(), 0, []
    for row in sorted(predictions, key=lambda r: r[4], reverse=True):
        candidates = [(iou(row, box), n) for n, box in enumerate(truth) if n not in matched]
        best = max(candidates, default=(0, -1))
        if best[0] >= 0.5:
            matched.add(best[1])
        elif any(max(0, min(row[2], b[2]) - max(row[0], b[0])) * max(0, min(row[3], b[3]) - max(row[1], b[1])) / max((row[2]-row[0])*(row[3]-row[1]), 1) >= 0.5 for b in annotation["ignore"]):
            ignored += 1
        else:
            false.append(row)
    return dict(tp=len(matched), fp=len(false), fn=len(truth)-len(matched),
                smallTotal=sum(b[3]-b[1] < 32 for b in truth),
                smallMissed=sum(b[3]-b[1] < 32 for n,b in enumerate(truth) if n not in matched),
                backgroundFp=len(false) if annotation["empty"] else 0,
                missed=[b for n,b in enumerate(truth) if n not in matched], falseBoxes=false, ignored=ignored)


def evaluate(args):
    from ultralytics import YOLO
    import psutil
    manifest = read(args.dataset / "manifest.json")
    selected = []
    for entry in manifest["entries"]:
        path = args.dataset / "annotations" / (entry["id"] + ".json")
        if entry["split"] == args.split and path.exists():
            annotation = read(path)
            if annotation["reviewed"]:
                selected.append((entry, validate_annotation(annotation, entry)))
    if not selected:
        raise ValueError("No manually reviewed images in requested split; no accuracy report generated")
    expected = sum(e["split"] == args.split for e in manifest["entries"])
    complete = len(selected) == expected
    has_background = any(a["empty"] for _, a in selected)
    args.output.mkdir(parents=True, exist_ok=False)
    write(args.output / "frozen_manifest.json", manifest)
    model = YOLO(str(args.model))
    summaries = {}
    selected_strategies = getattr(args, "strategies", list(STRATEGIES))
    if "full640" not in selected_strategies:
        raise ValueError("Include full640 as the within-model strategy baseline")
    for strategy in selected_strategies:
        first = image(args.dataset / "images" / selected[0][0]["image"])
        predict_boxes(model, first, strategy, device=args.device, half=args.device.startswith("cuda"))
        results, timings, memory = [], [], []
        loop_start = time.perf_counter()
        for entry, annotation in selected:
            frame = image(args.dataset / "images" / entry["image"])
            predictions = None
            for _ in range(args.repeats):
                if args.device.startswith("cuda"):
                    import torch
                    torch.cuda.synchronize()
                start = time.perf_counter()
                boxes = predict_boxes(model, frame, strategy, device=args.device, half=args.device.startswith("cuda"))
                if args.device.startswith("cuda"):
                    torch.cuda.synchronize()
                timings.append((time.perf_counter()-start)*1000)
                memory.append(psutil.Process().memory_info().rss)
                predictions = [r.tolist() for r in boxes.data if str(model.names[int(r[5])]).lower() == "person"]
            result = score(predictions, annotation)
            results.append(dict(id=entry["id"], group=entry["group"], imageSha256=digest(args.dataset / "images" / entry["image"]),
                                annotation=annotation, predictions=predictions, **result))
        totals = {k: sum(r[k] for r in results) for k in ("tp", "fp", "fn", "smallTotal", "smallMissed", "backgroundFp")}
        tp, fp, fn = (totals[k] for k in ("tp", "fp", "fn"))
        summaries[strategy] = dict(**totals, precision=tp/(tp+fp) if tp+fp else None,
                                   recall=tp/(tp+fn) if tp+fn else None,
                                   medianMs=statistics.median(timings), p95Ms=float(np.percentile(timings, 95)),
                                   offlineFps=len(timings)/(time.perf_counter()-loop_start), peakSampledRss=max(memory),
                                   cases=len(results))
        write(args.output / (strategy + ".json"), results)
    base = summaries["full640"]
    for name, s in summaries.items():
        s["offlineGatePassed"] = bool(args.split == "test" and complete and has_background and name != "full640" and base["precision"] is not None and s["precision"] is not None and
                                       s["smallMissed"] < base["smallMissed"] and s["precision"] >= base["precision"] and
                                       s["backgroundFp"] <= base["backgroundFp"])
    import platform
    import ultralytics
    candidates = [name for name, s in summaries.items() if s["offlineGatePassed"]]
    recommendation = min(candidates, key=lambda name: summaries[name]["p95Ms"]) if candidates else "full640"
    write(args.output / "summary.json", dict(modelSha256=digest(args.model), device=args.device,
                                             offlineRecommendation=recommendation, activated=False,
                                             python=platform.python_version(), ultralytics=ultralytics.__version__,
                                             halfPrecision=args.device.startswith("cuda"),
                                             strategies=selected_strategies,
                                             reviewedCount=len(selected), expectedCount=expected, allReviewed=complete,
                                             split=args.split, repeats=args.repeats, confidence=0.45,
                                             note="Small sample; real-camera 30-minute acceptance NOT completed. No automatic activation.",
                                             summaries=summaries))
    print(json.dumps(summaries, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare", "prioritize", "prelabel", "serve", "evaluate"])
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--videos", type=Path)
    parser.add_argument("--photos", type=Path)
    parser.add_argument("--model", type=Path, default=HERE.parent / "models" / "best.pt")
    parser.add_argument("--priority", action="store_true")
    parser.add_argument("--port", type=int, default=8799)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--split", choices=["tune", "test"], default="test")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--strategies", choices=list(STRATEGIES), nargs="+", default=list(STRATEGIES))
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("repeats must be positive")
    if args.command == "evaluate" and args.output is None:
        parser.error("--output required")
    globals()[args.command](args)


if __name__ == "__main__":
    main()
