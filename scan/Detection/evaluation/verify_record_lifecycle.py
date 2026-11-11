"""Real short-video recording EOF and paused-stop checks, without TCP server."""
import argparse
from pathlib import Path
import time

from offline_lab import Manager,create_app
from workbench import write


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--dataset',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Use a new output directory')
    manager=Manager(args.dataset,args.output);app=create_app(manager,8803);client=app.test_client();base='http://127.0.0.1:8803'
    token=client.get('/api/session',base_url=base).get_json()['token'];headers={'Origin':base,'X-Lab-Token':token}
    def state():return manager.active.snapshot()
    def post(path,body):
        response=client.post(path,base_url=base,headers=headers,json=body)
        assert response.status_code<400,response.get_json()
        return response.get_json()
    def until(condition):
        deadline=time.monotonic()+60
        while time.monotonic()<deadline:
            data=state()
            assert data['state']!='failed',data['error']
            if condition(data):return data
            time.sleep(.05)
        raise TimeoutError(str(state()))
    result={}
    try:
        for mode,keyword in [('eof','环境'),('paused_stop','夜晚')]:
            source=next(s for s in manager.sources.values() if keyword in s['name'])
            post('/api/start',dict(sourceId=source['id'],models=['candidate'],points=[],dwellSeconds=2))
            until(lambda s:s['state']=='running' and s['metrics'])
            post('/api/record/start',dict(model='candidate'))
            until(lambda s:s['recordings'] and s['recordings'][0]['frames']>=2)
            if mode=='paused_stop':
                post('/api/control',dict(action='pause'))
                until(lambda s:s['state']=='paused')
                post('/api/control',dict(action='stop'))
            final=until(lambda s:s['state'] in {'finished','stopped'} and s['captureReleased'] and s['writerReleased'])
            manager.active.thread.join(timeout=5)
            assert not manager.active.thread.is_alive()
            final=state()
            record=final['recordings'][0]
            assert record['status']=='ready',record
            assert record['endMediaSeconds']>record['startMediaSeconds']
            result[mode]=dict(runId=final['runId'],state=final['state'],recordingId=record['id'],frames=record['frames'],duration=record['duration'],resourcesReleased=True)
        write(args.output/'verified.json',result)
        print('PASS: candidate recording commits on EOF; recording commits on stop while paused; readers/writers/workers released')
    finally:
        if manager.active and manager.active.thread.is_alive():
            manager.active.stop.set();manager.active.thread.join(timeout=30)
