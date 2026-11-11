"""Real-model offline smoke test; writes ONLY the lab's isolated run directory."""
import argparse
import json
from pathlib import Path
import time

import requests

from workbench import write


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--url',default='http://127.0.0.1:8803')
    args=parser.parse_args(); base=args.url.rstrip('/')
    session=requests.Session()
    token=session.get(base+'/api/session',timeout=5).json()['token']
    headers={'Origin':base,'X-Lab-Token':token}
    def get(path):
        r=session.get(base+path,timeout=10);r.raise_for_status();return r.json()
    def post(path,body):
        r=session.post(base+path,json=body,headers=headers,timeout=15)
        if not r.ok:raise RuntimeError(f'{path}: {r.status_code} {r.text}')
        return r.json()
    def active():
        data=get('/api/status');return next(r for r in data['runs'] if r['runId']==data['active'])
    def until(predicate,timeout=60):
        end=time.monotonic()+timeout
        while time.monotonic()<end:
            state=active()
            if state['state']=='failed':raise RuntimeError(state['error'])
            if predicate(state):return state
            time.sleep(.2)
        raise TimeoutError('Offline lab condition timed out: '+str(active()['state']))
    current=get('/api/status')
    if current['active'] and any(r['runId']==current['active'] and not r['captureReleased'] for r in current['runs']):
        raise RuntimeError('A user job is active; do not interrupt it')
    source=next(s for s in get('/api/catalog')['sources'] if '飞书' in s['name'])
    started=post('/api/start',dict(sourceId=source['id'],models=['baseline','candidate'],strategy='full1280',
                     points=[[.1,.63],[.6,.63],[.6,.99],[.1,.99]],dwellSeconds=2))
    result=dict(runId=started['runId'],source=source['name'],purpose='Offline real-model functional test, not accuracy evaluation')
    try:
        until(lambda s:len(s['metrics'])==2 and s['state']=='running')
        concurrent=session.post(base+'/api/start',json=dict(sourceId=source['id']),headers=headers,timeout=10)
        assert concurrent.status_code==400
        result['concurrentStartRejected']=True
        post('/api/record/start',dict(model='baseline'))
        until(lambda s:s['recording'] and s['mediaSeconds']>=1)
        post('/api/control',dict(action='pause'))
        paused=until(lambda s:s['state']=='paused')
        seconds=paused['mediaSeconds'];time.sleep(.8)
        assert active()['mediaSeconds']==seconds
        result['pauseMediaClockFrozen']=True
        post('/api/control',dict(action='resume'))
        until(lambda s:s['mediaSeconds']>=8)
        post('/api/record/stop',{})
        state=until(lambda s:any(r['status']=='ready' for r in s['recordings']),timeout=60)
        record=next(r for r in state['recordings'] if r['status']=='ready')
        linked=[e for e in state['events'] if e.get('recordings')]
        assert linked,'Manual recording did not cover an offline event'
        event=next(e for e in linked if e['model']==record['model'])
        result.update(recordingId=record['id'],eventId=event['id'],mediaStart=record['startMediaSeconds'],
                      mediaEnd=record['endMediaSeconds'],eventMedia=event['mediaSeconds'],
                      seekOffset=event['mediaSeconds']-record['startMediaSeconds'])
        clip=session.get(base+f"/asset/{state['runId']}/{record['file']}",timeout=15)
        clip.raise_for_status();metadata=session.get(base+f"/asset/{state['runId']}/{record['id']}.json",timeout=10).content
        partial=session.get(base+f"/asset/{state['runId']}/{record['file']}",headers={'Range':'bytes=0-1023'},timeout=10)
        assert partial.status_code==206
        result['rangePlayback']=True
        imported=session.post(base+'/api/record/import',headers=headers,
                    files={'video':('clip.mp4',clip.content,'video/mp4'),'metadata':('clip.json',metadata,'application/json')},timeout=20)
        assert imported.status_code==200 and imported.json()['duplicate'] is True
        bad=session.post(base+'/api/record/import',headers=headers,
                    files={'video':('clip.mp4',b'not the recording','video/mp4'),'metadata':('clip.json',metadata,'application/json')},timeout=10)
        assert bad.status_code==400
        result.update(uploadValidated=True,tamperedUploadRejected=True)
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
            page=browser.new_page(viewport={'width':1600,'height':1000})
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(base)
            page.wait_for_function("document.querySelector('#baseImage').naturalWidth>0 && document.getElementById('events').textContent.includes('轨迹')")
            page.screenshot(path=str(args.output/'offline_lab.png'))
            page.locator('#events button').filter(has_text='关联录像').first.click()
            page.wait_for_function("document.getElementById('playback').readyState>=1")
            duration=page.locator('#playback').evaluate('v=>v.duration')
            assert duration>0
            page.locator('#playback').evaluate('v=>{v.currentTime=Math.min(1,v.duration/2)}')
            page.wait_for_function("document.getElementById('playback').currentTime>0")
            assert not errors,errors
            result.update(browserRendered=True,browserSeek=True,browserVideoDuration=duration,pageErrors=errors)
            browser.close()
        print(json.dumps(result,ensure_ascii=False),flush=True)
        write(args.output/('verification_'+result['runId']+'_partial.json'),result)
        final=until(lambda s:s['state']=='finished' and s['captureReleased'] and s['writerReleased'],timeout=240)
        result.update(eofReleased=True,framesDecoded=final['framesDecoded'],mediaSeconds=final['mediaSeconds'],
                      resources=final['resourceSamples'],events=final['events'],metrics=final['metrics'])
        write(args.output/('verification_'+result['runId']+'_complete.json'),result)
        # Start short negative video as a new epoch, check no old events leak.
        short=next(s for s in get('/api/catalog')['sources'] if '环境' in s['name'])
        again=post('/api/start',dict(sourceId=short['id'],models=['candidate'],strategy='full1280',points=[],dwellSeconds=2))
        assert again['runId']!=result['runId'] and again['events']==[]
        finished=until(lambda s:s['state']=='finished' and s['captureReleased'],timeout=60)
        assert finished['events']==[]
        result.update(replayUsesNewRun=True,negativeRunId=finished['runId'],noOldEventsLeaked=True)
        write(args.output/('verification_'+result['runId']+'_complete.json'),result)
        print('PASS: full-source EOF; resources released; new run isolated; no old events inherited',flush=True)
    except Exception:
        post('/api/control',dict(action='stop'))
        raise


if __name__=='__main__':main()
