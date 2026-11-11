import sys
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace

import cv2
import numpy as np


PROJECT_DETECTION_DIR = Path(
    r"D:\AAA空信242\比赛\项目代码\视界巡警\station-monitoring-master\scan\Detection"
)
sys.path.insert(0, str(PROJECT_DETECTION_DIR))

import detection_service as service  # noqa: E402


class FakeRepository:
    def __init__(self):
        self.alarms = []

    def create_region_intrusion_alarm(
        self, camera_id, rule, label, track_id, confidence, dwell_seconds
    ):
        self.alarms.append((camera_id, rule.name, label, track_id, confidence, dwell_seconds))
        return len(self.alarms)


class DetectionLogicTest(unittest.TestCase):
    def make_worker(self):
        worker = object.__new__(service.CameraWorker)
        worker.camera_id = 7
        worker.repository = FakeRepository()
        worker.region_rule = service.RegionRule(
            camera_id=7,
            name="站台边缘",
            points=[
                {"x": 0.0, "y": 0.0},
                {"x": 1.0, "y": 0.0},
                {"x": 1.0, "y": 1.0},
                {"x": 0.0, "y": 1.0},
            ],
            enabled=True,
            dwell_seconds=2.0,
            target_classes=["person"],
            cooldown_seconds=30.0,
        )
        worker.region_track_states = {}
        worker._record_detection_event = lambda *args, **kwargs: None
        return worker

    def test_same_track_emits_only_one_region_alarm(self):
        worker = self.make_worker()
        frame = np.zeros((200, 320, 3), dtype=np.uint8)
        detection = service.Detection("person", 0.91, (40, 20, 120, 180), track_id=12)

        worker._handle_region_intrusion([detection], frame, 100.0)
        worker._handle_region_intrusion([detection], frame, 102.1)
        worker._handle_region_intrusion([detection], frame, 108.0)

        self.assertEqual(len(worker.repository.alarms), 1)
        self.assertEqual(worker.repository.alarms[0][3], 12)

    def test_vehicle_does_not_trigger_person_rule(self):
        worker = self.make_worker()
        frame = np.zeros((200, 320, 3), dtype=np.uint8)
        detection = service.Detection("car", 0.90, (40, 20, 180, 180), track_id=7)

        worker._handle_region_intrusion([detection], frame, 100.0)
        worker._handle_region_intrusion([detection], frame, 103.0)

        self.assertEqual(worker.repository.alarms, [])

    def test_person_mask_prevents_foreign_object_false_alarm(self):
        baseline = np.zeros((240, 320, 3), dtype=np.uint8)
        frame = baseline.copy()
        cv2.rectangle(frame, (80, 60), (180, 210), (255, 255, 255), thickness=-1)
        rule = service.ForeignObjectRule(
            camera_id=7,
            baseline_file="baseline.jpg",
            enabled=True,
            dwell_seconds=8.0,
            min_area_ratio=0.002,
        )
        person = service.Detection("person", 0.95, (75, 55, 185, 215), track_id=3)

        unmasked = service.foreign_object_detections(frame, baseline, rule, None)
        masked = service.foreign_object_detections(
            frame, baseline, rule, None, ignored_detections=[person]
        )

        self.assertGreaterEqual(len(unmasked), 1)
        self.assertEqual(masked, [])

    def test_target_class_normalization_keeps_supported_classes(self):
        self.assertEqual(
            service.normalize_target_classes('["car", "person", "car", "bag"]'),
            ["car", "person"],
        )

    def test_gpu_prediction_uses_supported_fp16_quantize_value(self):
        class FakeModel:
            def __init__(self):
                self.options = None

            def predict(self, **options):
                self.options = options
                return [SimpleNamespace(boxes=None)]

        runtime = object.__new__(service.ModelRuntime)
        runtime.model = FakeModel()
        runtime.error = None
        runtime.names = {0: "person", 1: "car"}
        runtime.lock = threading.Lock()
        runtime.device = "cuda:0"
        runtime.half = True
        runtime.strategy = "full640"

        runtime.predict(np.zeros((32, 32, 3), dtype=np.uint8))

        from ultralytics.cfg import DEFAULT_CFG_DICT
        if "quantize" in DEFAULT_CFG_DICT:
            self.assertEqual(runtime.model.options["quantize"], 16)
        else:
            self.assertTrue(runtime.model.options["half"])

    def test_tiled_strategy_updates_tracker_once_in_original_coordinates(self):
        from unittest.mock import patch
        from ultralytics.engine.results import Boxes
        runtime = object.__new__(service.ModelRuntime)
        runtime.model = object()
        runtime.error = None
        runtime.names = {0: "person"}
        runtime.lock = threading.Lock()
        runtime.device = "cpu"
        runtime.half = False
        runtime.strategy = "tiled640"
        boxes = Boxes(np.array([[1000, 10, 1020, 40, .8, 0]], dtype=np.float32), (100, 1920))
        class Tracker:
            calls = 0
            def update(self, value, frame):
                self.calls += 1
                assert value.xyxy.tolist() == [[1000., 10., 1020., 40.]]
                return np.array([[1000,10,1020,40,12,.8,0]], dtype=np.float32)
        tracker = Tracker()
        with patch.object(service, "predict_boxes", return_value=boxes):
            result = runtime.predict(np.zeros((100,1920,3),dtype=np.uint8), tracker)
        self.assertEqual(tracker.calls, 1)
        self.assertEqual(result[0].track_id, 12)


if __name__ == "__main__":
    unittest.main()
