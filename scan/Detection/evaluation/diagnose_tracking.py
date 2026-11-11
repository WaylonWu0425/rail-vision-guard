"""Cache real predictions once, replay tracking ablations; no production writes."""
import argparse,json,time
from pathlib import Path
from collections import Counter,defaultdict
import cv2,numpy as np
from offline_lab import Manager,tracker,RegionEngine,write,digest,predict_boxes
from tracking_continuity import ContinuityRegionEngine,profile
from inference_strategies import iou

def main():
    p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    previous=args.dataset/'离线视频实验_20261016/core_verification_fixed/runs/ff188df72fd9411e'
    original=json.loads((previous/'run.json').read_text(encoding='utf-8'))
    frames=[json.loads(l) for l in (previous/'frames.jsonl').read_text(encoding='utf-8').splitlines()]
    hints=[]
    for model in ['baseline','candidate']:
        seen={};last={}
        for f in [r for r in frames if r['model']==model]:
            now=f['mediaSeconds'];current={t['id'] for t in f['tracks']}
            for t in f['tracks']:
                if t['label']!='person':continue
                if t['id'] not in seen:
                    for key,old in last.items():
                        if key not in current and 0<now-old['time']<=1.5 and iou(t['box'],old['box'])>=.5:
                            hints.append(dict(model=model,mediaSeconds=now,previousId=key,newId=t['id'],iou=iou(t['box'],old['box']),verdict='spatial candidate only; not verified same person'))
                    seen[t['id']]=now
                last[t['id']]=dict(time=now,box=t['box'])
    write(args.output/'old_run_diagnosis.json',dict(originalRun=original['runId'],possibleIdBreaks=hints,
        confirmedImplementationProblems=['upstream .45 removes all ByteTrack low-score detections','outside observation immediately resets old region state','event state keyed only by track ID'],
        limitations='No identity ground truth; hints cannot prove ID switches or false alerts.'))
    # Contact sheet: five evenly distributed real event screenshots, not new labels.
    events=original['events'];chosen=[events[round(i*(len(events)-1)/4)] for i in range(5)] if events else []
    panels=[]
    for e in chosen:
        image=cv2.imdecode(np.fromfile(str(previous/e['snapshot']),np.uint8),cv2.IMREAD_COLOR)
        image=cv2.resize(image,(640,360));cv2.putText(image,f"{e['model']} t={e['mediaSeconds']:.2f}s id={e['trackId']}",(8,345),cv2.FONT_HERSHEY_SIMPLEX,.55,(0,255,255),1)
        panels.append(image)
    if panels:cv2.imencode('.jpg',np.vstack(panels))[1].tofile(str(args.output/'five_event_cases.jpg'))
    manager=Manager(args.dataset,args.output/'sandbox');source=manager.sources['3']
    if digest(Path(source['path']))!=source['sha256']:
        raise ValueError('素材哈希已变化，停止使用旧缓存')
    from ultralytics import YOLO
    from ultralytics.engine.results import Boxes
    report=dict(source=source,models={},humanIdentityGroundTruth=False,productionEnabled=False)
    prior=json.loads((args.output/'comparison.json').read_text(encoding='utf-8')) if (args.output/'comparison.json').exists() else None
    for name,path in manager.models.items():
        if not path.is_file():raise ValueError('模型文件缺失，不自动下载：'+str(path))
        cache=args.output/(name+'_predictions.jsonl')
        if cache.exists():
            previous=prior['models'].get(name) if prior else None
            if (not previous or prior['source']['sha256']!=source['sha256'] or
                previous['modelSha256']!=digest(path) or previous['cacheSha256']!=digest(cache)):
                raise ValueError('缓存缺少完整来源记录或哈希不一致，请使用新的输出目录，不覆盖旧证据')
        if not cache.exists():
            model=YOLO(str(path));cap=cv2.VideoCapture(source['path']);fps=cap.get(cv2.CAP_PROP_FPS);index=0
            try:
                with cache.open('w',encoding='utf-8') as log:
                    while True:
                        ok,image=cap.read()
                        if not ok:break
                        if index%round(fps/2)==0:
                            tick=time.perf_counter();b=predict_boxes(model,image,'full1280',.1,'cpu',False)
                            mask=np.asarray([str(model.names[int(c)]).lower() in {'person','car'} for c in b.cls],bool)
                            log.write(json.dumps(dict(frame=index,seconds=index/fps,shape=list(image.shape[:2]),
                                boxes=b[mask].data.tolist(),names=model.names,inferenceMs=(time.perf_counter()-tick)*1000))+'\n');log.flush()
                        index+=1
            finally:cap.release()
            print('cached '+name,flush=True)
        rows=[json.loads(l) for l in cache.read_text(encoding='utf-8').splitlines()]
        interval=max(1,round(source['fps']/2));expected=(round(source['fps']*source['duration'])+interval-1)//interval
        if len(rows)!=expected or any(r['frame']!=i*interval for i,r in enumerate(rows)):
            raise ValueError('预测缓存不完整或帧顺序不一致，不生成对照结论')
        variants={}
        for variant in ['legacy','low_score','buffered_score','continuity_v1']:
            cfg=profile(variant);track=tracker(2,variant)
            engine=(ContinuityRegionEngine if variant=='continuity_v1' else RegionEngine)(original['config']['points'],2)
            identities=set();events=[];counts=[];low=0;out=args.output/(name+'_'+variant+'_tracks.jsonl')
            with out.open('w',encoding='utf-8') as log:
                for row in rows:
                    data=np.asarray(row['boxes'],np.float32).reshape(-1,6);data=data[data[:,4]>=cfg['inferenceConfidence']]
                    low+=int(sum(data[:,4]<.45));tracked=track.update(Boxes(data,tuple(row['shape'])))
                    visible=[]
                    for t in tracked:
                        if t[5]<.45:continue
                        visible.append(dict(id=int(t[4]),box=list(map(float,t[:4])),confidence=float(t[5]),label=row['names'][str(int(t[6]))]))
                    identities.update(t['id'] for t in visible);counts.append(len(visible))
                    emitted=engine.update(visible,row['seconds'],row['shape'][1],row['shape'][0]);events+=emitted
                    log.write(json.dumps(dict(mediaSeconds=row['seconds'],tracks=visible,events=emitted))+'\n')
            variants[variant]=dict(parameters=cfg,observedIds=len(identities),events=len(events),
                visibleObservations=sum(counts),lowScoreInputs=low,updates=len(rows),
                handovers=getattr(engine,'audit',[]),eventDetails=events)
        report['models'][name]=dict(modelSha256=digest(path),cacheSha256=digest(cache),variants=variants)
    write(args.output/'comparison.json',report)
    print(json.dumps({m:{v:{k:d[k] for k in ['observedIds','events','visibleObservations','lowScoreInputs']} for v,d in data['variants'].items()} for m,data in report['models'].items()},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
