"""Extract source crops around four mechanical event resets, no new truth labels."""
import argparse,json
from pathlib import Path
import cv2,numpy as np
from workbench import write
from inference_strategies import iou

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--dataset',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    audit=json.loads((args.output/'event_cause_audit.json').read_text(encoding='utf-8'))
    cases=[e for e in audit['events'] if e['model']=='baseline' and e['sameIdPreviousEvent'] is not None]
    cases=[cases[i] for i in [0,1,3,4]]
    source=json.loads((args.dataset/'manifest.json').read_text(encoding='utf-8'))['sources'][3]['path']
    previous=args.dataset/'离线视频实验_20261016/core_verification_fixed/runs/ff188df72fd9411e'
    rows=[json.loads(x) for x in (previous/'frames.jsonl').read_text(encoding='utf-8').splitlines()]
    rows={r['frameIndex']:r for r in rows if r['model']=='baseline'}
    preds={r['frame']:r for r in [json.loads(l) for l in (args.output/'baseline_predictions.jsonl').read_text(encoding='utf-8').splitlines()]}
    cap=cv2.VideoCapture(source);fps=cap.get(cv2.CAP_PROP_FPS);pictures=[];evidence=[]
    try:
        for case in cases:
            key=case['trackId'];times=[case['trigger']['lastInsideAt'],case['trigger']['enteredAt'],case['mediaSeconds']]
            indices=[round(t*fps) for t in times]
            boxes=[next(t['box'] for t in rows[i]['tracks'] if t['id']==key) for i in indices]
            crop=[max(0,int(min(b[0] for b in boxes))-100),max(0,int(min(b[1] for b in boxes))-90),
                  min(1920,int(max(b[2] for b in boxes))+100),min(1080,int(max(b[3] for b in boxes))+90)]
            views=[]
            for label,idx,box in zip(['last visible','visible again','repeat event'],indices,boxes):
                cap.set(cv2.CAP_PROP_POS_FRAMES,idx);ok,frame=cap.read();assert ok
                x1,y1,x2,y2=map(int,box);cv2.rectangle(frame,(x1,y1),(x2,y2),(255,180,30),2)
                x,y,right,bottom=crop;view=cv2.resize(frame[y:bottom,x:right],(360,280))
                panel=np.full((330,360,3),250,np.uint8);panel[50:]=view
                cv2.putText(panel,f'{label} id={key}',(8,20),cv2.FONT_HERSHEY_SIMPLEX,.5,(20,30,50),1)
                cv2.putText(panel,f'media={idx/fps:.3f}s frame={idx}',(8,41),cv2.FONT_HERSHEY_SIMPLEX,.48,(20,30,50),1)
                views.append(panel)
            pictures.append(np.hstack(views))
            gap=[]
            for idx in range(indices[0]+10,indices[1],10):
                nearby=[b for b in preds[idx]['boxes'] if int(b[5])==0 and iou(b,boxes[0])>=.3]
                gap.append(dict(frame=idx,mediaSeconds=idx/fps,nearbyPersonScores=[round(b[4],4) for b in nearby],
                                note='spatial overlap only, not a same-person identity label'))
            evidence.append(dict(trackId=key,times=times,crop=crop,gapCandidates=gap))
    finally:cap.release()
    cv2.imencode('.jpg',np.vstack(pictures))[1].tofile(str(args.output/'four_gap_windows.jpg'))
    write(args.output/'four_gap_windows.json',dict(source=source,cases=evidence,groundTruth=False))
    print(json.dumps(evidence))
