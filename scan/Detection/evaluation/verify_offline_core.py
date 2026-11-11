"""Real video/model workflow through Flask test client; does NOT bind a port."""
import argparse
import io
import json
from pathlib import Path
import time

from offline_lab import Manager,create_app
from workbench import write,digest


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--dataset',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--tracking-profile',default='legacy',choices=['legacy','continuity_v1'])
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Use a new core-test output directory')
    manager=Manager(args.dataset,args.output,args.tracking_profile)
    app=create_app(manager,8803);client=app.test_client();base='http://127.0.0.1:8803'
    token=client.get('/api/session',base_url=base).get_json()['token']
    headers={'Origin':base,'X-Lab-Token':token}
    def get():
        data=client.get('/api/status',base_url=base).get_json()
        return next(r for r in data['runs'] if r['runId']==data['active'])
    def post(path,body):
        response=client.post(path,base_url=base,json=body,headers=headers)
        if response.status_code>=400:raise RuntimeError(str(response.get_json()))
        return response.get_json()
    def wait(predicate,timeout=60,allow_failed=False):
        limit=time.monotonic()+timeout
        while time.monotonic()<limit:
            state=get()
            if state['state']=='failed' and not allow_failed:raise RuntimeError(state['error'])
            if predicate(state):return state
            time.sleep(.1)
        raise TimeoutError(str(get()))
    source=next(s for s in manager.sources.values() if '飞书' in s['name'])
    run=post('/api/start',dict(sourceId=source['id'],models=['baseline','candidate'],strategy='full1280',
                       points=[[.1,.63],[.6,.63],[.6,.99],[.1,.99]],dwellSeconds=2))
    report=dict(runId=run['runId'],transport='Flask test client; no TCP listener',realVideo=True,realModels=True)
    try:
        wait(lambda s:len(s['metrics'])==2)
        post('/api/record/start',dict(model='baseline'))
        wait(lambda s:s['mediaSeconds']>=1)
        post('/api/control',dict(action='pause'))
        paused=wait(lambda s:s['state']=='paused');time.sleep(.7)
        assert get()['mediaSeconds']==paused['mediaSeconds']
        report['pauseMediaFrozen']=True
        post('/api/control',dict(action='resume'))
        wait(lambda s:s['mediaSeconds']>=8)
        post('/api/record/stop',{})
        state=wait(lambda s:any(r['status']=='ready' for r in s['recordings']))
        record=next(r for r in state['recordings'] if r['status']=='ready')
        event=next(e for e in state['events'] if e['recordings'] and e['model']==record['model'])
        prefix=f"/asset/{run['runId']}/"
        with client.get(prefix+record['file'],base_url=base) as response:clip=response.data
        with client.get(prefix+record['id']+'.json',base_url=base) as response:metadata=response.data
        with client.get(prefix+record['file'],base_url=base,headers={'Range':'bytes=0-1023'}) as response:
            assert response.status_code==206
        def upload(data):
            return client.post('/api/record/import',base_url=base,headers=headers,data={
                'video':(io.BytesIO(data),'clip.mp4'),'metadata':(io.BytesIO(metadata),'clip.json')})
        assert upload(clip).status_code==200
        assert upload(b'wrong-video').status_code==400
        report.update(recordingId=record['id'],eventId=event['id'],startMedia=record['startMediaSeconds'],
                      endMedia=record['endMediaSeconds'],eventMedia=event['mediaSeconds'],
                      seekOffset=event['mediaSeconds']-record['startMediaSeconds'],range206=True,
                      importSuccess=True,tamperedImportRejected=True)
        write(args.output/'partial.json',report)
        print(json.dumps(report,ensure_ascii=False),flush=True)
        final=wait(lambda s:s['state']=='finished' and s['captureReleased'] and s['writerReleased'],timeout=240)
        manager.active.thread.join(timeout=5)
        assert not manager.active.thread.is_alive()
        report.update(fullVideoEof=True,framesDecoded=final['framesDecoded'],finalMedia=final['mediaSeconds'],
                      metrics=final['metrics'],resources=final['resourceSamples'],events=final['events'],
                      workerExited=True)
        write(args.output/'verified.json',report)
        short=next(s for s in manager.sources.values() if '环境' in s['name'])
        second=post('/api/start',dict(sourceId=short['id'],models=['candidate'],points=[],dwellSeconds=2))
        assert second['runId']!=run['runId'] and second['events']==[]
        second_done=wait(lambda s:s['state']=='finished' and s['captureReleased'])
        manager.active.thread.join(timeout=5)
        assert second_done['events']==[]
        report.update(newEpochIsolated=True,negativeEof=True,negativeRunId=second['runId'])
        third=post('/api/start',dict(sourceId=short['id'],models=['candidate'],points=[],dwellSeconds=2))
        wait(lambda s:s['mediaSeconds']>.2)
        post('/api/control',dict(action='stop'))
        wait(lambda s:s['state']=='stopped' and s['captureReleased'] and s['writerReleased'])
        manager.active.thread.join(timeout=5)
        assert not manager.active.thread.is_alive()
        report['explicitStopReleased']=True
        corrupt=args.output/'corrupt_fixture.avi';corrupt.write_bytes(b'deliberately invalid test fixture')
        manager.sources['fixture']=dict(id='fixture',name='corrupt test fixture',path=str(corrupt),sha256=digest(corrupt),fps=20,duration=1)
        post('/api/start',dict(sourceId='fixture',models=['candidate'],points=[],dwellSeconds=2))
        broken=wait(lambda s:s['state']=='failed' and s['captureReleased'],allow_failed=True)
        manager.active.thread.join(timeout=5)
        report.update(corruptVideoFailedClearly=True,corruptError=broken['error'])
        write(args.output/'verified.json',report)
        print('PASS: fixed core full-video EOF; no status read/write collision; media freeze; recording/event/range/import; new epoch; stop release; corrupt video failure',flush=True)
    finally:
        if manager.active and manager.active.thread.is_alive():
            manager.active.stop.set();manager.active.thread.join(timeout=30)
        manager.close()


if __name__=='__main__':main()
