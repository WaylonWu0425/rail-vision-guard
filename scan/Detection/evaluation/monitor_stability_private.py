"""Read-only supplemental Windows memory sampling of our named soak process."""
import argparse,json,time
from pathlib import Path
import psutil
from workbench import write

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--soak',type=Path,required=True);args=parser.parse_args()
    matches=[]
    for candidate in psutil.process_iter(['pid','cmdline']):
        try:
            command=candidate.info['cmdline'] or []
            if (any(Path(t).name=='verify_offline_stability.py' for t in command) and
                '--output' in command and Path(command[command.index('--output')+1])==args.soak):matches.append(candidate)
        except (psutil.Error,ValueError,IndexError):continue
    if len(matches)!=1:raise RuntimeError('未找到唯一的本轮验收进程，不采样其他程序')
    process=matches[0];rows=[];start=time.monotonic()
    target=args.soak/'supplemental_private.jsonl'
    if target.exists():raise ValueError('使用新的监测目录，不能覆盖旧采样')
    with target.open('w',encoding='utf-8') as log:
        while process.is_running() and time.monotonic()-start<1000:
            try:
                data=process.memory_info()._asdict()
                row=dict(elapsedSinceSupplement=time.monotonic()-start,pid=process.pid,memory=data)
                rows.append(row);log.write(json.dumps(row)+'\n');log.flush()
            except psutil.Error:break
            time.sleep(5)
    write(args.soak/'supplemental_private_summary.json',dict(pid=process.pid,samples=len(rows),
        first=rows[0] if rows else None,last=rows[-1] if rows else None,
        limitation='Supplement begins after warmup; does not replace original RSS acceptance thresholds.'))
    print('Supplemental read-only memory monitoring completed')
