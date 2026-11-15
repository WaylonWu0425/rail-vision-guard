"""Offline comparison and guarded camera-to-target ranging for the review page."""
import argparse
import json
import math
import sys
from pathlib import Path

if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parent / '.ncnn-runtime'))

import cv2
import numpy as np

DISTANCE_DEFINITION = 'camera_to_reference_center'


class RangingError(ValueError):
    pass


def number(value, label, *, positive=False):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or (positive and value <= 0)):
        raise RangingError(f'{label}必须是有效的{"正" if positive else ""}数值')
    return float(value)


def required_text(value, label):
    if not isinstance(value, str) or not value.strip() or len(value) > 200:
        raise RangingError(f'请填写{label}（1–200 字符）')
    return value.strip()


def dimensions(value):
    if (not isinstance(value, list) or len(value) != 2
            or any(type(n) is not int or not 0 < n <= 16384 for n in value)):
        raise RangingError('图像尺寸必须是有效的 [宽, 高] 像素值')
    return value


def parse_calibration(archive):
    if not isinstance(archive, dict) or archive.get('format') != 'rail-coupler-ranging-v1':
        raise RangingError('标定档案格式错误，请使用本页模板')
    c = archive.get('calibration')
    if not isinstance(c, dict):
        raise RangingError('缺少相机标定')
    for key, title in (
        ('id', '标定编号'), ('cameraId', '设备或机位编号'), ('lens', '镜头及焦距设置'),
        ('installation', '安装及成像设置'), ('source', '标定来源及日期'),
        ('targetId', '目标或参考面编号'), ('targetReference', '参考面及中心点说明'),
    ):
        required_text(c.get(key), title)
    if c.get('projection') != 'opencv_pinhole':
        raise RangingError('当前接受 OpenCV 针孔相机标定')
    image_size = dimensions(c.get('imageSize'))
    intrinsics = [number(c.get(k), k, positive=k in ('fx', 'fy')) for k in ('fx', 'fy', 'cx', 'cy')]
    fx, fy, cx, cy = intrinsics
    if not (0 <= cx < image_size[0] and 0 <= cy < image_size[1]):
        raise RangingError('标定主点超出图像范围')
    distortion = c.get('distortion')
    if not isinstance(distortion, list) or len(distortion) not in (4, 5, 8, 12, 14):
        raise RangingError('请填入 4、5、8、12 或 14 个 OpenCV 畸变系数')
    distortion = [number(n, '畸变系数') for n in distortion]
    width = number(c.get('targetWidthM'), '参考面实测宽度（米）', positive=True)
    height = number(c.get('targetHeightM'), '参考面实测高度（米）', positive=True)
    criteria = archive.get('criteria')
    if not isinstance(criteria, dict):
        raise RangingError('请填写试验的像素及距离误差门槛')
    return {
        'id': c['id'], 'cameraId': c['cameraId'], 'imageSize': image_size,
        'lens': c['lens'], 'installation': c['installation'], 'source': c['source'],
        'targetId': c['targetId'], 'targetReference': c['targetReference'],
        'cameraMatrix': np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float64),
        'distortion': np.array(distortion, dtype=np.float64),
        'objectPoints': np.array([
            [-width / 2, -height / 2, 0], [width / 2, -height / 2, 0],
            [width / 2, height / 2, 0], [-width / 2, height / 2, 0],
        ], dtype=np.float64),
        'maxReprojectionPx': number(criteria.get('maxReprojectionPx'), '最大重投影误差（像素）', positive=True),
        'maxMeanAbsoluteErrorM': number(criteria.get('maxMeanAbsoluteErrorM'), '平均绝对误差上限（米）', positive=True),
        'maxAbsoluteErrorM': number(criteria.get('maxAbsoluteErrorM'), '单样本绝对误差上限（米）', positive=True),
    }


def measure(calibration, frame_size, corners):
    if dimensions(frame_size) != calibration['imageSize']:
        raise RangingError('画面分辨率与标定档案不一致')
    if not isinstance(corners, list) or len(corners) != 4:
        raise RangingError('请标注四个可见的参考面角点')
    points = []
    width, height = frame_size
    for pair in corners:
        if not isinstance(pair, list) or len(pair) != 2:
            raise RangingError('每个角点需要两个像素坐标')
        x, y = (number(n, '角点坐标') for n in pair)
        if not (0 < x < width - 1 and 0 < y < height - 1):
            raise RangingError('参考面贴边或被裁切，请选择四角完整的画面')
        points.append((x, y))
    image_points = np.array(points, dtype=np.float64)
    sides = np.roll(image_points, -1, axis=0) - image_points
    next_sides = np.roll(sides, -1, axis=0)
    cross = sides[:, 0] * next_sides[:, 1] - sides[:, 1] * next_sides[:, 0]
    lengths = np.linalg.norm(sides, axis=1)
    if min(lengths) < 3 or np.any(cross <= 0) or np.any(cross / lengths < 3):
        raise RangingError('角点应按左上、右上、右下、左下标注，且参考面需清晰可辨')
    object_points = calibration['objectPoints']
    matrix = calibration['cameraMatrix']
    distortion = calibration['distortion']
    candidates = []
    for method in (cv2.SOLVEPNP_IPPE, cv2.SOLVEPNP_ITERATIVE):
        try:
            _, rotations, translations, _ = cv2.solvePnPGeneric(
                object_points, image_points, matrix, distortion, flags=method,
            )
            for rotation, translation in zip(rotations, translations):
                pose, _ = cv2.Rodrigues(rotation)
                camera_points = object_points @ pose.T + translation.reshape(1, 3)
                if not np.isfinite(camera_points).all() or np.any(camera_points[:, 2] <= 0):
                    continue
                projected, _ = cv2.projectPoints(object_points, rotation, translation, matrix, distortion)
                residuals = projected.reshape(-1, 2) - image_points
                rms = float(np.sqrt(np.mean(np.sum(residuals ** 2, axis=1))))
                distance = float(np.linalg.norm(translation))
                if math.isfinite(rms) and math.isfinite(distance):
                    candidates.append((rms, distance))
        except cv2.error:
            continue
        if candidates and min(candidates)[0] <= calibration['maxReprojectionPx']:
            break
    if not candidates:
        raise RangingError('无法得到位于相机前方的有效位姿')
    rms, distance = min(candidates)
    if rms > calibration['maxReprojectionPx']:
        raise RangingError(f'重投影误差 {rms:.2f} px 超过设定上限，请复查角点')
    return {'distanceM': distance, 'reprojectionPx': rms}


def compare(archive):
    calibration = parse_calibration(archive)
    samples = archive.get('samples')
    if not isinstance(samples, list) or len(samples) > 100:
        raise RangingError('样本应为一个列表，最多 100 条')
    rows = []
    seen = set()
    for sample in samples:
        if not isinstance(sample, dict):
            raise RangingError('样本条目格式错误')
        source = required_text(sample.get('frameRef'), '样本原始帧标识')
        if source in seen:
            raise RangingError(f'样本帧重复：{source}')
        seen.add(source)
        row = {'frameRef': source}
        try:
            if sample.get('kind') != 'field_measured' or sample.get('sameSetup') is not True:
                raise RangingError('须提供同一相机和参考面的独立实测样本')
            row['referenceMethod'] = required_text(sample.get('referenceMethod'), '实测工具与测量基准')
            row['referenceM'] = number(sample.get('referenceM'), '相机到参考面中心实测距离', positive=True)
            row.update(measure(calibration, sample.get('imageSize'), sample.get('corners')))
            row['errorM'] = row['distanceM'] - row['referenceM']
        except RangingError as exc:
            row['reason'] = str(exc)
        rows.append(row)
    valid = [row for row in rows if 'errorM' in row]
    errors = [abs(row['errorM']) for row in valid]
    references = sorted({row['referenceM'] for row in valid})
    mae = sum(errors) / len(errors) if errors else None
    max_error = max(errors) if errors else None
    reasons = []
    if len(references) < 3:
        reasons.append('至少需要三个不同距离的独立有效实测样本')
    if len(valid) != len(rows):
        reasons.append('存在无效样本，请核对逐条结果')
    if mae is not None and mae > calibration['maxMeanAbsoluteErrorM']:
        reasons.append('平均绝对误差超过档案设定的上限')
    if max_error is not None and max_error > calibration['maxAbsoluteErrorM']:
        reasons.append('最大绝对误差超过档案设定的上限')
    report = {key: calibration[key] for key in (
        'id', 'cameraId', 'lens', 'installation', 'source', 'targetId', 'targetReference', 'imageSize',
    )}
    report.update(
        status='pending' if not rows else 'failed' if reasons else 'passed',
        definition=DISTANCE_DEFINITION, reasons=reasons, samples=rows, validCount=len(valid),
        meanAbsoluteErrorM=mae, maxAbsoluteErrorM=max_error,
        observedRangeM=[references[0], references[-1]] if len(references) >= 2 else None,
    )
    return calibration, report


def estimate(archive, frame):
    calibration, report = compare(archive)
    if report['status'] != 'passed':
        raise RangingError('档案尚未通过实测对照')
    if not isinstance(frame, dict) or frame.get('sameSetup') is not True:
        raise RangingError('请确认当前画面与标定的相机、镜头、成像设置及参考面一致')
    result = measure(calibration, frame.get('imageSize'), frame.get('corners'))
    low, high = report['observedRangeM']
    if not low <= result['distanceM'] <= high:
        raise RangingError('估算值超出实测样本覆盖范围')
    return {
        **result, 'definition': DISTANCE_DEFINITION, 'calibrationId': calibration['id'],
        'observedRangeM': report['observedRangeM'], 'meanAbsoluteErrorM': report['meanAbsoluteErrorM'],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='离线比较相机至参考面中心的估算距离与实测距离')
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    try:
        _, result = compare(json.loads(args.archive.read_text(encoding='utf-8-sig')))
    except (OSError, ValueError) as exc:
        parser.exit(2, f'{exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    raise SystemExit(0 if result['status'] == 'passed' else 1)
