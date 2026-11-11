"""Read-only shape probe for the supplied NCNN railway model."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.ncnn-runtime'))
import ncnn
import numpy as np

model = ROOT.parent.parent.parent / '模型'
net = ncnn.Net()
print('load param:', net.load_param(str(model / 'best12_20.param')))
print('load bin:', net.load_model(str(model / 'best12_20.bin')))
frame = np.zeros((640, 640, 3), dtype=np.uint8)
mat = ncnn.Mat.from_pixels(frame, ncnn.Mat.PixelType.PIXEL_BGR, 640, 640)
mat.substract_mean_normalize([], [1 / 255] * 3)
ex = net.create_extractor()
print('input:', ex.input('images', mat))
result, output = ex.extract('output0')
print('extract:', result, 'shape:', np.array(output).shape, 'w/h/c:', output.w, output.h, output.c)
