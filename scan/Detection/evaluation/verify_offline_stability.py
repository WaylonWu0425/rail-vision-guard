"""Wall-clock multi-epoch soak with real models/video, no TCP/production writes."""
import argparse,json,statistics,time,traceback
from pathlib import Path
import psutil
from offline_lab import Manager,create_app,write,utc

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--dataset',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--seconds',type=int,default=1800)
    parser.add_argument('--condition-label',default='not specified')
    args=parser.parse_args()
    if args.seconds<1800:raise ValueError('30分钟验收不得缩短；短测请用其他测试脚本')
    if args.output.exists():raise ValueError('必须使用新的输出目录')
    manager=Manager(args.dataset,args.output)
    client=create_app(manager,8803).test_client();base='http://127.0.0.1:8803'
    token=client.get('/api/session',base_url=base).get_json()['token']
    headers={'Origin':base,'X-Lab-Token':token}
    def post(path,body):
        r=client.post(path,base_url=base,headers=headers,json=body)
        assert r.status_code<400,(path,r.get_json())
        return r.get_json()
    process=psutil.Process();process.cpu_percent()
    started=time.monotonic();deadline=started+args.seconds
    report=dict(startedAt=utc(),requestedWallSeconds=args.seconds,status='running',
        conditionLabel=args.condition_label,
        mode='offline multi-epoch Flask test-client soak; no browser or camera',
        workerScope='one reusable inference worker; workerExited flags refer to per-run task completion',
        modelLifecycle='two hash-pinned cached models; independent trackers/region/recordings per Job',
        trackingProfile='continuity_v1',productionEnabled=False,runs=[],samples=0)
    write(args.output/'progress.json',report)
    jobs=0;last_announcement=-60;rss=[];last_media=-1;last_progress=time.monotonic()
    pause_check=None;pause_until=None;record_started=False;record_stopped=False
    source_ids=['3','0','1','2']
    try:
        with (args.output/'soak_resources.jsonl').open('w',encoding='utf-8') as log:
            while time.monotonic()<deadline:
                active=manager.active
                if active is None or not active.thread.is_alive():
                    if active:
                        state=active.snapshot()
                        assert state['state']=='finished',state['error']
                        assert state['captureReleased'] and state['writerReleased']
                        assert all(r['status']=='ready' for r in state['recordings']),state['recordings']
                        report['runs'].append(dict(runId=state['runId'],sourceId=state['sourceId'],
                            state=state['state'],framesDecoded=state['framesDecoded'],events=len(state['events']),
                            recordings=len(state['recordings']),captureReleased=True,writerReleased=True,workerExited=True))
                    source=source_ids[jobs%len(source_ids)]
                    post('/api/start',dict(sourceId=source,models=['baseline','candidate'],strategy='full1280',
                        points=[[.1,.63],[.6,.63],[.6,.99],[.1,.99]],dwellSeconds=2,trackingProfile='continuity_v1'))
                    jobs+=1;last_media=-1;last_progress=time.monotonic()
                    pause_check=None;pause_until=None;record_started=False;record_stopped=False
                    active=manager.active
                state=active.snapshot()
                assert state['state']!='failed',state['error']
                now=time.monotonic()
                if state['mediaSeconds']!=last_media:
                    last_media=state['mediaSeconds'];last_progress=now
                assert now-last_progress<90,'90秒媒体时间未推进'
                if state['state']=='running' and state['mediaSeconds']>=.5 and not record_started:
                    post('/api/record/start',dict(model='candidate'));record_started=True
                if state['duration']>10 and state['state']=='running' and state['mediaSeconds']>=6 and pause_check is None:
                    post('/api/control',dict(action='pause'));pause_check='requested'
                if state['state']=='paused' and pause_check=='requested':
                    pause_check=state['mediaSeconds'];pause_until=now+1.1
                if state['state']=='paused' and isinstance(pause_check,(int,float)):
                    assert state['mediaSeconds']==pause_check,'暂停期间媒体时间发生变化'
                    if now>=pause_until:
                        post('/api/control',dict(action='resume'));pause_until=None
                if state['state']=='running' and state['mediaSeconds']>=9 and record_started and not record_stopped:
                    post('/api/record/stop',{});record_stopped=True
                elapsed=now-started
                sample=dict(wallSeconds=elapsed,rssBytes=process.memory_info().rss,
                    threads=process.num_threads(),handles=process.num_handles(),cpuPercent=process.cpu_percent(),
                    runId=state['runId'],mediaSeconds=state['mediaSeconds'],state=state['state'])
                rss.append(sample);log.write(json.dumps(sample)+'\n');log.flush()
                report.update(elapsedWallSeconds=round(elapsed,2),activeRun=state['runId'],samples=len(rss),completedRuns=len(report['runs']))
                if elapsed-last_announcement>=60:
                    write(args.output/'progress.json',report)
                    print(json.dumps({k:report[k] for k in ['status','elapsedWallSeconds','completedRuns','activeRun']},ensure_ascii=False),flush=True)
                    last_announcement=elapsed
                time.sleep(.5)
        if manager.active and manager.active.thread.is_alive():
            post('/api/control',dict(action='stop'));manager.active.thread.join(timeout=120)
        assert not manager.active.thread.is_alive(),'截止后线程未退出'
        end=manager.active.snapshot()
        assert end['state'] in {'finished','stopped'},end['error']
        assert end['captureReleased'] and end['writerReleased']
        assert all(r['status']=='ready' for r in end['recordings']),end['recordings']
        report['finalRun']=dict(runId=end['runId'],state=end['state'],workerExited=True,
            recordings=len(end['recordings']),captureReleased=True,writerReleased=True)
        # Warm-up excluded; diagnostics are not a proof of absence of leaks.
        early=[s['rssBytes'] for s in rss if 300<=s['wallSeconds']<600]
        late=[s['rssBytes'] for s in rss if s['wallSeconds']>=args.seconds-300]
        trend=[s for s in rss if s['wallSeconds']>=600]
        xs=[s['wallSeconds']/60 for s in trend];ys=[s['rssBytes']/1048576 for s in trend]
        xm=statistics.mean(xs);ym=statistics.mean(ys)
        slope=sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/sum((x-xm)**2 for x in xs)
        growth=(statistics.mean(late)-statistics.mean(early))/1048576
        report.update(status='completed',elapsedWallSeconds=time.monotonic()-started,finishedAt=utc(),
            processRssPeakMB=max(s['rssBytes'] for s in rss)/1048576,
            rssMeanGrowthMB=growth,rssLateSlopeMBPerMinute=slope,
            resourceWarning=growth>100 or slope>1,
            resourceWarningRule='after warmup: last5min mean minus min5-10 mean >100MB OR min10-end slope >1MB/min',
            threadRange=[min(s['threads'] for s in rss),max(s['threads'] for s in rss)],
            handleRange=[min(s['handles'] for s in rss),max(s['handles'] for s in rss)],
            limitation='Process RSS excludes browser/ffmpeg; repeated fixed clips are not camera/network/general accuracy validation')
        print('COMPLETED '+json.dumps({k:report[k] for k in ['elapsedWallSeconds','resourceWarning','rssMeanGrowthMB','rssLateSlopeMBPerMinute'] }),flush=True)
    except BaseException as exc:
        report.update(status='failed',error=str(exc),traceback=traceback.format_exc(),elapsedWallSeconds=time.monotonic()-started)
        write(args.output/'failure.json',report)
        raise
    finally:
        if manager.active and manager.active.thread.is_alive():
            manager.active.stop.set();manager.active.thread.join(timeout=120)
        manager.close()
        report['executorClosed']=True
        if report['status']=='completed':write(args.output/'verified.json',report)
        write(args.output/'progress.json',report)

if __name__=='__main__':main()
