"""Explain old rule resets exactly, without guessing human identity."""
import argparse,json
from pathlib import Path
from collections import Counter
from copy import deepcopy
import cv2,numpy as np
from offline_lab import RegionEngine,write

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--dataset',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    original=args.dataset/'离线视频实验_20261016/core_verification_fixed/runs/ff188df72fd9411e'
    run=json.loads((original/'run.json').read_text(encoding='utf-8'))
    frames=[json.loads(line) for line in (original/'frames.jsonl').read_text(encoding='utf-8').splitlines()]
    polygon=np.asarray([[x*1920,y*1080] for x,y in run['config']['points']],np.float32)
    rows=[]
    for model in ['baseline','candidate']:
        engine=RegionEngine(run['config']['points'],2);resets={};entered={};last_event={}
        for frame in [f for f in frames if f['model']==model]:
            t=frame['mediaSeconds'];before=deepcopy(engine.states)
            outside=set()
            for track in frame['tracks']:
                if track['label']!='person':continue
                key=track['id'];b=track['box']
                inside=cv2.pointPolygonTest(polygon,((b[0]+b[2])/2,b[3]),False)>=0
                if not inside:outside.add(key)
                if inside and (key not in before or t-before[key]['last']>engine.grace):
                    if key in before:
                        resets[key]=dict(reason='missing_over_grace',resetAt=t,lastInsideAt=before[key]['last'])
                    reason=resets.get(key,dict(reason='first_observed_inside',resetAt=None))
                    entered[key]=dict(enteredAt=t,**reason)
            emitted=engine.update(frame['tracks'],t,1920,1080)
            for key in before:
                if key not in engine.states:
                    resets[key]=dict(reason='observed_outside' if key in outside else 'missing_over_grace',resetAt=t,lastInsideAt=before[key]['last'])
            for event in emitted:
                key=event['trackId']
                rows.append(dict(model=model,trackId=key,mediaSeconds=t,box=event['box'],
                    trigger=entered[key],sameIdPreviousEvent=last_event.get(key),
                    interpretation='rule-state reset evidence only; not proof of duplicate business event'))
                last_event[key]=t
    for model in ['baseline','candidate']:
        old=[e for e in run['events'] if e['model']==model]
        new=[e for e in rows if e['model']==model]
        assert [(e['trackId'],e['mediaSeconds']) for e in old]==[(e['trackId'],e['mediaSeconds']) for e in new]
    report=dict(oldRun=run['runId'],sourceResolution=[1920,1080],events=rows,
        counts={model:dict(total=sum(e['model']==model for e in rows),
            sameIdRepeat=sum(e['model']==model and e['sameIdPreviousEvent'] is not None for e in rows),
            triggers=dict(Counter(e['trigger']['reason'] for e in rows if e['model']==model))) for model in ['baseline','candidate']},
        limitation='No identity/event truth; outside observations can be real exits or box jitter; missing can be occlusion, misses, or departure.')
    write(args.output,report)
    print(json.dumps(report['counts']))
    print(json.dumps([e for e in rows if e['sameIdPreviousEvent'] is not None][:5]))
