"""Analyze completed evidence only; never mark an unfinished run as passed."""
import argparse,json,statistics
from pathlib import Path
from workbench import write

def lines(path):
    if not path.is_file():return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--soak-name',default='stability_30min_fixed');args=parser.parse_args()
    soak=args.output/args.soak_name;verified=soak/'verified.json'
    if not verified.is_file():raise RuntimeError('30分钟尚未完成或已失败，不生成完成报告；查看progress.json/failure.json')
    result=json.loads(verified.read_text(encoding='utf-8'))
    assert result['status']=='completed' and result['elapsedWallSeconds']>=1800
    samples=lines(soak/'soak_resources.jsonl');jobs=[]
    for file in sorted((soak/'runs').glob('*/run.json')):
        run=json.loads(file.read_text(encoding='utf-8'));data=lines(file.parent/'resources.jsonl')
        tail=[r for r in data if r['mediaSeconds']>=10]
        lag=[r['wallElapsedSeconds']-r['mediaSeconds'] for r in tail]
        n=len(lag)//3
        growth=(statistics.mean(lag[-n:])-statistics.mean(lag[:n])) if n else None
        per_run=[s for s in samples if s['runId']==run['runId']]
        jobs.append(dict(runId=run['runId'],source=run['sourceName'],state=run['state'],
            framesDecoded=run['framesDecoded'],eventsByModel={m:sum(e['model']==m for e in run['events']) for m in run['config']['models']},
            recordingsReady=sum(r['status']=='ready' for r in run['recordings']),
            allRecordingsReady=all(r['status']=='ready' for r in run['recordings']),
            captureReleased=run['captureReleased'],writerReleased=run['writerReleased'],
            mediaLagGrowthSeconds=growth,mediaLagGrowthWarning=growth is not None and growth>2,
            firstHandles=per_run[0]['handles'] if per_run else None,lastHandles=per_run[-1]['handles'] if per_run else None))
    result['jobAnalysis']=jobs
    result['queueNote']='No asynchronous frame queue exists; positive late-vs-early wall-minus-media growth >2s is a pacing warning. Pause time is included. No camera/network latency claim.'
    result['anyPacingWarning']=any(j['mediaLagGrowthWarning'] for j in jobs)
    result['status']='completed_with_warnings' if result['resourceWarning'] or result['anyPacingWarning'] else 'completed_no_declared_warning'
    result['notValidated']=['identity/true-event accuracy','camera/network disconnect recovery','browser soak','production integration']
    result['soakDirectory']=args.soak_name
    write(args.output/(args.soak_name+'_summary.json'),result)
    write(args.output/'稳定性汇总.json',result)
    print(json.dumps({k:result[k] for k in ['status','elapsedWallSeconds','resourceWarning','anyPacingWarning','processRssPeakMB','rssMeanGrowthMB','rssLateSlopeMBPerMinute']},ensure_ascii=False))
