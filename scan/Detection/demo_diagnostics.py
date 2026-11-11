"""Run safe diagnostics for the local station-monitoring demonstration.

This command does not insert alarms, change camera rules or open RTSP streams.
It reports the state of the Vue/Java/Python services and executes the trained
YOLO model against the supplied simulation photographs.  The result is a
repeatable *functional* check, not an accuracy or mAP evaluation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL = BASE_DIR / "models" / "best.pt"
DEFAULT_IMAGES = BASE_DIR / "simulation_images"
RECOMMENDED_IMAGE_NAMES = (
    "01_baseline_empty_platform.png",
    "02_person_intrusion_v2.png",
    "03_vehicle_access_v3.png",
    "04_unattended_suitcase.png",
)


def request_json(url: str) -> dict:
    try:
        with urlopen(url, timeout=4) as response:  # nosec B310 - fixed localhost URLs
            body = response.read().decode("utf-8", errors="replace")
            result = {"reachable": True, "status": response.status}
            try:
                result["body"] = json.loads(body)
            except ValueError:
                # Vue and Spring roots may return HTML. Reachability still matters.
                result["content_type"] = response.headers.get_content_type()
            return result
    except HTTPError as exc:
        # Authentication protection proves the process is reachable.  Do not
        # require credentials for a harmless local status diagnostic.
        return {"reachable": True, "status": exc.code, "protected": True}
    except (URLError, TimeoutError) as exc:
        return {"reachable": False, "error": str(exc)}


def run_model(
    model_path: Path, image_dir: Path, confidence: float, include_alternatives: bool
) -> list[dict]:
    from ultralytics import YOLO

    model = YOLO(str(model_path))
    results: list[dict] = []
    image_paths = sorted(image_dir.glob("*.png")) + sorted(image_dir.glob("*.jpg"))
    if not include_alternatives:
        image_paths = [
            image_dir / image_name
            for image_name in RECOMMENDED_IMAGE_NAMES
            if (image_dir / image_name).exists()
        ]
    for image_path in image_paths:
        prediction = model(str(image_path), conf=confidence, verbose=False)[0]
        labels = []
        for box in prediction.boxes:
            label = prediction.names[int(box.cls[0])]
            labels.append(
                {
                    "label": str(label),
                    "confidence": round(float(box.conf[0]), 4),
                }
            )
        results.append({"image": image_path.name, "detections": labels})
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--images", type=Path, default=DEFAULT_IMAGES)
    parser.add_argument("--confidence", type=float, default=0.45)
    parser.add_argument(
        "--include-alternatives",
        action="store_true",
        help="同时检测标为备选的图片；默认仅检查 README 推荐演示图。",
    )
    args = parser.parse_args()

    report = {
        "notice": "结果用于演示链路自检，不代表现场精度、漏报率或mAP。",
        "services": {
            "vue": request_json("http://127.0.0.1:8080/"),
            "java": request_json("http://127.0.0.1:8081/"),
            "detection": request_json("http://127.0.0.1:5000/health"),
        },
    }
    if not args.model.exists():
        report["model_check"] = {"ready": False, "error": f"模型不存在：{args.model}"}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2
    if not args.images.exists():
        report["model_check"] = {"ready": False, "error": f"样例目录不存在：{args.images}"}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2

    try:
        report["model_check"] = {
            "ready": True,
            "model": args.model.name,
            "confidence_threshold": args.confidence,
            "image_set": "全部图片" if args.include_alternatives else "README 推荐演示图",
            "results": run_model(
                args.model, args.images, args.confidence, args.include_alternatives
            ),
        }
    except Exception as exc:  # display a diagnosis without hiding the error
        report["model_check"] = {"ready": False, "error": str(exc)}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
