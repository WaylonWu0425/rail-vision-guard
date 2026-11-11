"""One real image, all strategies; no truth labels, alarms or database writes."""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from inference_strategies import STRATEGIES,predict_boxes
from workbench import image


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--image',type=Path,required=True)
    args=parser.parse_args()
    from ultralytics import YOLO
    model=YOLO(str(Path(__file__).resolve().parent.parent/'models'/'best.pt'))
    frame=image(args.image)
    for strategy in STRATEGIES:
        start=time.perf_counter()
        boxes=predict_boxes(model,frame,strategy)
        assert all(0<=r[0]<r[2]<=frame.shape[1] and 0<=r[1]<r[3]<=frame.shape[0] for r in boxes.data)
        print(json.dumps(dict(strategy=strategy,boxes=len(boxes),smokeOnly=True,elapsedMs=round((time.perf_counter()-start)*1000,2))),flush=True)
