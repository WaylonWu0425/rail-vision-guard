"""Cross-check real service-run aggregates against the independent replay."""
import argparse,json
from pathlib import Path
from workbench import write,digest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--core-name',default='core_cached_verified');args=p.parse_args()
    compare_path=args.output/'comparison.json';core_path=args.output/args.core_name/'verified.json'
    compare=json.loads(compare_path.read_text(encoding='utf-8'));core=json.loads(core_path.read_text(encoding='utf-8'))
    frames_path=args.output/args.core_name/'runs'/core['runId']/'frames.jsonl'
    frames=[json.loads(line) for line in frames_path.read_text(encoding='utf-8').splitlines()]
    result={}
    for model,data in compare['models'].items():
        expected=data['variants']['continuity_v1']
        actual=dict(observations=sum(len(f['tracks']) for f in frames if f['model']==model),
                    lowInputs=sum(f['lowScoreInputCount'] for f in frames if f['model']==model),
                    events=sum(e['model']==model for e in core['events']))
        assert actual==dict(observations=expected['visibleObservations'],lowInputs=expected['lowScoreInputs'],events=expected['events'])
        result[model]=actual
    filename='service_replay_consistency_final.json' if args.core_name=='core_final_verified' else 'service_replay_consistency.json'
    write(args.output/filename,dict(passed=True,actualRunId=core['runId'],counts=result,
        evidenceSha256={p.name:digest(p) for p in [compare_path,core_path,frames_path]},
        limitation='Aggregate implementation consistency only, not identity/event accuracy.'))
    print('PASS service/replay aggregate consistency: '+json.dumps(result))
