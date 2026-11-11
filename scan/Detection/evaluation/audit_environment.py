"""Record only non-secret hardware/runtime/model facts; no package changes."""
import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path

from workbench import digest,write


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--model',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():
        raise ValueError('Audit output already exists')
    import torch
    import ultralytics
    import psutil
    from ultralytics import YOLO
    model=YOLO(str(args.model))
    result=dict(python=sys.version,executable=sys.executable,platform=platform.platform(),
                memoryBytes=psutil.virtual_memory().total,logicalCores=psutil.cpu_count(),
                torch=torch.__version__,torchCudaBuild=torch.version.cuda,
                cudaAvailable=torch.cuda.is_available(),cudaDevices=torch.cuda.device_count(),
                ultralytics=ultralytics.__version__,modelPath=str(args.model),modelSha256=digest(args.model),
                task=model.task,classes=model.names,parameters=sum(p.numel() for p in model.model.parameters()),
                trainingModel=model.ckpt.get('train_args',{}).get('model'))
    try:
        result['nvidiaSmi']=subprocess.run(['nvidia-smi','--query-gpu=name,memory.total,driver_version','--format=csv,noheader'],
                                          capture_output=True,text=True,timeout=15,check=True).stdout.strip()
    except (OSError,subprocess.SubprocessError) as exc:
        result['nvidiaSmiError']=str(exc)
    write(args.output,result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
