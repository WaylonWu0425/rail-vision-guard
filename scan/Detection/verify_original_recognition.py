"""Real-weight/source functional check; does not produce accuracy claims."""
import argparse
import hashlib
import io
import json
import platform
import subprocess
import sys
import time
from importlib.metadata import version
from pathlib import Path

from original_recognition import create_app, MODEL, EXPECTED_SHA256


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', required=True)
    parser.add_argument('--video', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    inputs = {key: {'path': str(Path(value).resolve()), 'sha256': sha(value)}
              for key, value in [('image', args.image), ('video', args.video), ('model', MODEL)]}
    assert inputs['model']['sha256'] == EXPECTED_SHA256
    unit = subprocess.run([sys.executable, '-m', 'unittest', 'test_original_recognition', '-v'],
                          capture_output=True, text=True, encoding='utf-8')
    report = {'scope': 'original model functional integration only; no accuracy or throughput benchmark',
              'inputs': inputs, 'python': platform.python_version(),
              'versions': {key: version(key) for key in ['ultralytics', 'torch', 'opencv-python', 'flask']},
              'unit': {'exitCode': unit.returncode, 'stdout': unit.stdout, 'stderr': unit.stderr},
              'hardwareCameraTests': 'not performed; no camera availability assumed'}
    app = create_app()
    manager = app.extensions['original_manager']
    client = app.test_client()
    headers = {'X-Original-Token': client.get('/original/config').json['token']}
    results = {}
    try:
        assert unit.returncode == 0
        for mode, source in [('image', args.image), ('video', args.video)]:
            path = Path(source)
            with path.open('rb') as stream:
                response = client.post('/original/jobs', data={'mode': mode, 'file': (io.BytesIO(stream.read()), path.name)}, headers=headers)
            assert response.status_code == 202, response.json
            job = manager.job
            job.future.result(timeout=300)
            state = client.get(f'/original/jobs/{job.id}').json['data']
            assert state['state'] == 'finished', state
            assert state['captureReleased'] and job.source is None
            if mode == 'video':
                assert state['frameIndex'] == state['totalFrames']
                assert not Path(job.cleanup).exists()
            frame = client.get(f'/original/jobs/{job.id}/frame')
            assert frame.status_code == 200 and frame.mimetype == 'image/jpeg'
            (output / f'{mode}_last_frame.jpg').write_bytes(frame.data)
            results[mode] = state
            print(json.dumps({'mode': mode, 'state': state['state'], 'frames': state['frameIndex'], 'counts': state['counts']}, ensure_ascii=False), flush=True)
        assert all(sha(item['path']) == item['sha256'] for item in inputs.values())
        report.update(status='passed', actualResults=results, sourceHashesUnchanged=True)
    except Exception as exc:
        report.update(status='failed', actualResults=results, error=str(exc))
        raise
    finally:
        manager.close()
        report['executorClosed'] = True
        (output / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
