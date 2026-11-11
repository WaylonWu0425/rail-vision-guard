"""Prove/remove task callback reference cycles, without model inference."""
import argparse,gc,weakref,json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from offline_lab import SerialTask,write

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('Use a new evidence file')
    refs=[]
    class Owner:
        def __init__(self,pool):self.task=SerialTask(pool,self.work)
        def work(self):pass
    # Disable automatic GC only in this tiny isolated proof process.
    # Never change GC settings in the real service/soak process.
    was_enabled=gc.isenabled();gc.disable()
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            for _ in range(10):
                owner=Owner(pool);refs.append(weakref.ref(owner));owner.task.start();owner.task.join()
                pool.submit(lambda:None).result();del owner
            before=sum(ref() is not None for ref in refs)
            gc.collect();after=sum(ref() is not None for ref in refs)
    finally:
        if was_enabled:gc.enable()
    result=dict(tasks=10,retainedBeforeExplicitGc=before,retainedAfterExplicitGc=after,
                limitation='Isolated reference-ownership proof, not a measurement of leaked model memory.')
    write(args.output,result);print(json.dumps(result))
