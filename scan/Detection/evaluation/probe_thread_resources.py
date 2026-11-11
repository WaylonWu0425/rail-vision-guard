"""Real-model repeated-worker probe, not a speed or accuracy benchmark."""
import argparse,gc,threading,time,json
from pathlib import Path
import cv2,psutil
from concurrent.futures import ThreadPoolExecutor
from offline_lab import Manager,predict_boxes,write

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--threads',type=int,default=0);p.add_argument('--iterations',type=int,default=12)
    p.add_argument('--worker-mode',choices=['new_thread','serial'],default='new_thread')
    p.add_argument('--reuse-models',action='store_true');args=p.parse_args()
    if args.output.exists():raise ValueError('Use a new output path')
    import torch
    from ultralytics import YOLO
    if args.threads:torch.set_num_threads(args.threads)
    manager=Manager(args.dataset,args.output.parent/('probe_sandbox_'+str(args.threads)))
    capture=cv2.VideoCapture(manager.sources['3']['path']);ok,frame=capture.read();capture.release();assert ok
    process=psutil.Process();rows=[];errors=[]
    def sample():return dict(rssMB=process.memory_info().rss/1048576,threads=process.num_threads(),handles=process.num_handles())
    def worker():
        try:
            # Match the two-model construction and first-forward sequence.
            models=[manager.load_model(name) if args.reuse_models else YOLO(str(path)) for name,path in manager.models.items()]
            for _ in range(2):
                for model in models:predict_boxes(model,frame,'full1280',.1,'cpu',False)
        except BaseException as exc:errors.append(str(exc))
    with ThreadPoolExecutor(max_workers=1) as executor:
        for index in range(args.iterations):
            if args.worker_mode=='serial':executor.submit(worker).result(timeout=90)
            else:
                t=threading.Thread(target=worker);t.start();t.join(timeout=90);assert not t.is_alive()
            assert not errors,errors
            before=sample();gc.collect();time.sleep(.1);after=sample()
            rows.append(dict(iteration=index+1,beforeGc=before,afterGc=after));print(json.dumps(rows[-1]),flush=True)
    write(args.output,dict(workerMode=args.worker_mode,reuseModels=args.reuse_models,cpuThreads=torch.get_num_threads(),samples=rows,errors=errors))
    manager.close()
