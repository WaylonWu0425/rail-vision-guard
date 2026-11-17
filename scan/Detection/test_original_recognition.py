"""No database/camera/model imports in unit tests; real inference is separate."""
import base64
import hashlib
import io
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np

from original_recognition import Detector, InputFailure, Manager, create_app, decode_image, rtsp_source


class FakeDetector:
    def __init__(self):
        self.calls = 0
        self.profiles = []

    def predict(self, frame, profile):
        self.calls += 1
        self.profiles.append(profile)
        return frame.copy(), [{'label': 'person', 'confidence': .8, 'box': [1, 2, 8, 9]}], 1.5


class FakeCapture:
    def __init__(self, total=4, opened=True, declared=None):
        self.total, self.opened, self.declared = total, opened, declared
        self.index, self.released = 0, False

    def isOpened(self):
        return self.opened

    def get(self, key):
        return {cv2.CAP_PROP_FRAME_WIDTH: 16, cv2.CAP_PROP_FRAME_HEIGHT: 16,
                cv2.CAP_PROP_FPS: 20, cv2.CAP_PROP_FRAME_COUNT: self.declared or self.total}.get(key, 0)

    def read(self):
        if self.index >= self.total:
            return False, None
        self.index += 1
        return True, np.zeros((16, 16, 3), dtype=np.uint8)

    def release(self):
        self.released = True


class RecognitionTests(unittest.TestCase):
    def setUp(self):
        self.detector = FakeDetector()
        self.capture = FakeCapture()
        self.manager = Manager(self.detector, lambda _: self.capture)
        self.app = create_app(self.manager, lambda cid=None: ([{'id': 1, 'name': 'test'}] if cid is None else
                               {'id': 1, 'name': 'test', 'ip': '192.0.2.1', 'username': 'u', 'password': 'SECRET'}))
        self.client = self.app.test_client()
        self.token = self.client.get('/original/config').json['token']
        self.headers = {'X-Original-Token': self.token}

    def tearDown(self):
        self.manager.close()

    def image_request(self, profile=None):
        _, image = cv2.imencode('.png', np.zeros((16, 16, 3), dtype=np.uint8))
        data = {'mode': 'image', 'file': (io.BytesIO(image.tobytes()), '样本.png')}
        if profile is not None:
            data['profile'] = profile
        return self.client.post('/original/jobs', data=data, headers=self.headers)

    def wait(self):
        self.manager.job.future.result(timeout=5)
        return self.manager.job.snapshot()

    def test_image_detection_and_preview(self):
        response = self.image_request()
        self.assertEqual(response.status_code, 202)
        state = self.wait()
        self.assertEqual(state['state'], 'finished')
        self.assertEqual(state['counts'], {'person': 1, 'car': 0})
        self.assertTrue(state['captureReleased'])
        self.assertIsNone(self.manager.job.source)
        frame = self.client.get(f"/original/jobs/{state['id']}/frame")
        self.assertEqual(frame.mimetype, 'image/jpeg')
        self.assertEqual(self.detector.calls, 1)
        self.assertEqual(self.detector.profiles, ['full640'])

    def test_offline_profile_is_reported_with_its_frame(self):
        response = self.image_request('full1280')
        self.assertEqual(response.status_code, 202)
        state = self.wait()
        result = self.client.get(f"/original/jobs/{state['id']}/snapshot").json['data']
        self.assertEqual(result['inference']['inputSize'], 1280)
        self.assertEqual(result['inference']['modelSha256'], self.client.get('/original/config').json['modelSha256'])
        self.assertEqual(self.detector.profiles, ['full1280'])

    def test_unknown_profile_and_live_detail_mode_are_rejected(self):
        self.assertEqual(self.image_request('unknown').status_code, 400)
        response = self.client.post('/original/jobs', json={'mode': 'usb', 'profile': 'full1280'}, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIsNone(self.manager.job)

    def test_missing_railai_weights_do_not_fall_back_to_current_model(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {'RAILAI_DETECTION_MODEL_PATH': str(Path(directory) / 'missing.pt')}):
                manager = Manager(self.detector)
            try:
                client = create_app(manager).test_client()
                config = client.get('/original/config').json
                self.assertFalse(config['railai']['configured'])
                _, image = cv2.imencode('.png', np.zeros((16, 16, 3), dtype=np.uint8))
                response = client.post('/original/jobs', data={
                    'mode': 'image', 'modelId': 'railai', 'file': (io.BytesIO(image.tobytes()), 'sample.png'),
                }, headers={'X-Original-Token': config['token']})
                self.assertEqual(response.status_code, 400)
                self.assertEqual(self.detector.calls, 0)
            finally:
                manager.close()

    def test_railai_checkpoint_identity_and_output_are_separate_from_current_model(self):
        with tempfile.TemporaryDirectory() as directory:
            weights = Path(directory) / 'five-classes.pt'
            weights.write_bytes(b'test fixture, never loaded as a checkpoint')
            sha256 = hashlib.sha256(weights.read_bytes()).hexdigest()
            with patch.dict(os.environ, {'RAILAI_DETECTION_MODEL_PATH': str(weights), 'RAILAI_DETECTION_SHA256': sha256}):
                railai = FakeDetector()
                manager = Manager(self.detector, railai_detector=railai)
            try:
                with self.assertRaises(InputFailure):
                    manager.start('usb', 0, 'camera', model_id='railai')
                job = manager.start('image', np.zeros((16, 16, 3), dtype=np.uint8), 'frame', model_id='railai')
                job.future.result(timeout=5)
                state = job.snapshot()
                self.assertEqual(state['state'], 'finished')
                self.assertEqual(state['inference']['modelSha256'], sha256)
                self.assertEqual(state['inference']['iou'], .45)
                self.assertEqual(state['counts'], {'obstacle': 0, 'person': 1, 'rail': 0, 'signal-and-sign': 0, 'vehicle': 0})
                self.assertEqual(self.detector.calls, 0)
                self.assertEqual(railai.calls, 1)
                weights.write_bytes(b'changed after configuration')
                with self.assertRaisesRegex(InputFailure, 'SHA-256'):
                    Detector(manager.models['railai']).predict(np.zeros((16, 16, 3), dtype=np.uint8))
            finally:
                manager.close()

    def test_snapshot_image_and_detection_share_same_frame(self):
        self.image_request()
        state = self.wait()
        url = f"/original/jobs/{state['id']}/snapshot"
        result = self.client.get(url).json['data']
        raw = np.frombuffer(base64.b64decode(result['originalJpeg']), dtype=np.uint8)
        image = cv2.imdecode(raw, cv2.IMREAD_COLOR)
        self.assertEqual(image.shape[:2], (result['height'], result['width']))
        self.assertEqual(result['frameIndex'], 1)
        self.assertEqual(result['detections'], state['detections'])
        self.assertTrue(result['frameUpdatedAt'])
        unchanged = self.client.get(f"{url}?after=1").json['data']
        self.assertNotIn('originalJpeg', unchanged)
        self.assertEqual(unchanged['frameIndex'], state['frameIndex'])

    def test_video_each_frame_and_upload_removed(self):
        response = self.client.post('/original/jobs', data={'mode': 'video', 'file': (io.BytesIO(b'fake-input'), 'video.mp4')}, headers=self.headers)
        self.assertEqual(response.status_code, 202)
        path = self.manager.job.cleanup
        state = self.wait()
        self.assertEqual(state['frameIndex'], 4)
        self.assertEqual(self.detector.calls, 4)
        self.assertAlmostEqual(state['mediaSeconds'], .15)
        self.assertTrue(self.capture.released)
        self.assertFalse(Path(path).exists())

    def test_invalid_video_extension(self):
        response = self.client.post('/original/jobs', data={'mode': 'video', 'file': (io.BytesIO(b'bad'), 'bad.py')}, headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_corrupt_image_rejected(self):
        response = self.client.post('/original/jobs', data={'mode': 'image', 'file': (io.BytesIO(b'bad'), 'bad.png')}, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIsNone(self.manager.job)

    def test_pause_resume_and_stop(self):
        self.capture.total = 200
        self.client.post('/original/jobs', json={'mode': 'usb', 'deviceIndex': 0}, headers=self.headers)
        # USB cannot be paused; use video mode for pause test, no source file needed in injected unit test.
        self.manager.job.stop.set()
        self.wait()
        self.capture = FakeCapture(total=200)
        job = self.manager.start('video', 'test-only', 'test')
        deadline = time.monotonic() + 2
        while job.data['frameIndex'] < 2 and time.monotonic() < deadline:
            time.sleep(.01)
        self.client.post(f'/original/jobs/{job.id}/pause', headers=self.headers)
        time.sleep(.15)
        count = job.data['frameIndex']
        time.sleep(.15)
        self.assertEqual(job.data['frameIndex'], count)
        self.client.post(f'/original/jobs/{job.id}/resume', headers=self.headers)
        time.sleep(.15)
        self.assertGreater(job.data['frameIndex'], count)
        self.client.post(f'/original/jobs/{job.id}/stop', headers=self.headers)
        self.assertEqual(self.wait()['state'], 'stopped')
        self.assertTrue(self.capture.released)

    def test_no_second_task_queued(self):
        self.capture = FakeCapture(total=200)
        self.manager.start('video', 'test-only', 'test')
        with self.assertRaises(RuntimeError):
            self.manager.start('image', np.zeros((16, 16, 3), np.uint8), 'second')

    def test_incomplete_video_is_failure(self):
        self.capture = FakeCapture(total=1, declared=8)
        self.manager.start('video', 'test-only', 'test')
        self.assertEqual(self.wait()['state'], 'failed')
        self.assertTrue(self.capture.released)

    def test_failed_camera_no_fake_results(self):
        self.capture = FakeCapture(opened=False)
        response = self.client.post('/original/jobs', json={'mode': 'usb', 'deviceIndex': 0}, headers=self.headers)
        self.assertEqual(response.status_code, 202)
        state = self.wait()
        self.assertEqual(state['state'], 'failed')
        self.assertEqual(state['frameIndex'], 0)
        self.assertIsNone(self.manager.job.jpeg)
        self.assertTrue(self.capture.released)

    def test_live_disconnect_is_failure(self):
        self.manager.start('usb', 0, 'test')
        self.assertEqual(self.wait()['state'], 'failed')

    def test_usb_index_validation(self):
        for value in (-1, 10, 'rtsp://bad', 1.5, True):
            response = self.client.post('/original/jobs', json={'mode': 'usb', 'deviceIndex': value}, headers=self.headers)
            self.assertEqual(response.status_code, 400)

    def test_token_and_origin_and_host(self):
        self.assertEqual(self.client.post('/original/jobs', json={'mode': 'usb'}).status_code, 403)
        self.assertEqual(self.client.get('/original/config', headers={'Origin': 'https://bad.invalid'}).status_code, 403)
        self.assertEqual(self.client.get('/original/config', base_url='http://bad.invalid').status_code, 403)
        self.assertEqual(self.client.get('/original/config', environ_overrides={'REMOTE_ADDR': '192.0.2.1'}).status_code, 403)
        response = self.client.options('/original/jobs', headers={'Origin': 'http://localhost:8080'})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], 'http://localhost:8080')

    def test_camera_list_has_no_credentials(self):
        response = self.client.get('/original/cameras')
        self.assertNotIn('SECRET', response.get_data(as_text=True))

    def test_rtsp_uses_config_not_arbitrary_url_and_hides_credentials(self):
        response = self.client.post('/original/jobs', json={'mode': 'rtsp', 'cameraId': 1, 'url': 'http://bad.invalid'}, headers=self.headers)
        self.assertEqual(response.status_code, 202)
        state = self.wait()
        self.assertNotIn('SECRET', str(state))
        self.assertNotIn('rtsp://', str(state))

    def test_escaped_rtsp_credentials(self):
        source = rtsp_source({'ip': '192.0.2.1', 'username': 'u@', 'password': 'p#'})
        self.assertIn('u%40:p%23@192.0.2.1:554', source)

    def test_no_alarm_or_tracking_contract(self):
        data = self.client.get('/original/config').json
        self.assertFalse(data['alarmsEnabled'])
        self.assertFalse(data['trackingEnabled'])
        self.assertEqual(data['confidence'], .25)

    def test_image_pixel_guard(self):
        from PIL import Image
        stream = io.BytesIO()
        Image.new('1', (4001, 4000)).save(stream, format='PNG')
        with self.assertRaises(ValueError):
            decode_image(stream.getvalue())


if __name__ == '__main__':
    unittest.main(verbosity=2)
