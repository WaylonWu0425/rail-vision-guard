"""Opt-in offline continuity experiment. No production imports or identity claims."""
from inference_strategies import iou


def profile(name,hz=2):
    if name not in {'legacy','low_score','buffered_score','continuity_v1'}:
        raise ValueError('未知跟踪配置')
    return dict(name=name,inferenceConfidence=.45 if name=='legacy' else .1,
                reportConfidence=.45,highThreshold=.25 if name=='legacy' else .45,
                newThreshold=.25 if name=='legacy' else .45,lowThreshold=.1,
                bufferUpdates=max(1,round(hz*(3 if name in {'buffered_score','continuity_v1'} else 1.5))))


class ContinuityRegionEngine:
    """Short missing/edge grace; conservative reciprocal spatial handover.

    Spatial handover is heuristic, not ReID. Never link simultaneous tracks or
    ambiguous matches; only high-confidence observations advance dwell.
    """
    def __init__(self,points,dwell,grace=1.5,exit_grace=1.,handover_iou=.5):
        import numpy as np
        self.points=points;self.dwell=dwell;self.grace=grace
        self.exit_grace=exit_grace;self.handover_iou=handover_iou
        self.states={};self.audit=[];self.sequence=0

    def update(self,tracks,seconds,width,height):
        import cv2
        import numpy as np
        people=[t for t in tracks if t['label']=='person' and t.get('confidence',1)>=.45]
        ids={t['id'] for t in people};events=[]
        polygon=np.asarray([[x*width,y*height] for x,y in self.points],np.float32)
        for key,s in list(self.states.items()):
            if seconds-s['last']>self.grace:
                self.audit.append(dict(action='expired',trackId=key,mediaSeconds=seconds,stayId=s['stay']))
                del self.states[key]
        missing={k:s for k,s in self.states.items() if k not in ids and s['outside'] is None}
        new=[t for t in people if t['id'] not in self.states]
        edges={(t['id'],k) for t in new for k,s in missing.items()
               if iou(t['box'],s['box'])>=self.handover_iou}
        for t in people:
            key=t['id'];box=t['box']
            inside=cv2.pointPolygonTest(polygon,((box[0]+box[2])/2,box[3]),False)>=0
            if key not in self.states and inside:
                matches=[k for new_id,k in edges if new_id==key]
                if len(matches)==1 and sum(k==matches[0] for _,k in edges)==1:
                    old=matches[0];self.states[key]=self.states.pop(old)
                    self.audit.append(dict(action='spatial_handover',fromId=old,toId=key,
                                           mediaSeconds=seconds,stayId=self.states[key]['stay']))
            s=self.states.get(key)
            if not inside:
                if s:
                    if s['outside'] is None:s['outside']=seconds
                    s['last']=seconds
                    if seconds-s['outside']>=self.exit_grace:
                        self.audit.append(dict(action='confirmed_exit',trackId=key,mediaSeconds=seconds,stayId=s['stay']))
                        del self.states[key]
                continue
            if s is None:
                self.sequence+=1
                s=dict(entered=seconds,last=seconds,box=box,emitted=False,outside=None,stay=self.sequence,
                       observed=0.,previous_inside=False)
                self.states[key]=s
            # Missing intervals and outside intervals must not earn dwell credit.
            delta=seconds-s['last']
            if s['outside'] is None and s['previous_inside'] and 0<delta<=.75:
                s['observed']+=delta
            s.update(last=seconds,box=box,outside=None,previous_inside=True)
            if not s['emitted'] and s['observed']>=self.dwell:
                s['emitted']=True
                events.append(dict(trackId=key,stayId=s['stay'],mediaSeconds=seconds,
                                   dwellSeconds=s['observed'],box=box,ruleVersion='continuity_v1'))
        for key,s in self.states.items():
            if key not in ids:s['previous_inside']=False
        return events
