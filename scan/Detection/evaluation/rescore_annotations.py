"""Rescore frozen predictions after human corrections; never rerun inference."""
import argparse
from copy import deepcopy

from workbench import read,write,digest,validate_annotation,score
from inference_strategies import STRATEGIES


def rescore(dataset,run,output):
    if output.exists():
        raise ValueError('Choose a new output directory')
    manifest=read(dataset/'manifest.json')
    entries={e['id']:e for e in manifest['entries']}
    original=read(run/'summary.json')
    updated=deepcopy(original)
    updated.update(annotationOnlyRescore=True,inferenceRerun=False,predictionSourceRun=str(run),
                   timingSourceRun=str(run),activated=False,
                   note='Human annotation correction only. Predictions and historical timing reused; not model improvement. Real-camera acceptance incomplete.')
    changed=set()
    pending={}
    for strategy in STRATEGIES:
        records=read(run/(strategy+'.json'))
        for record in records:
            entry=entries[record['id']]
            if digest(dataset/'images'/entry['image']) != record['imageSha256']:
                raise ValueError('Image changed: '+record['id'])
            annotation=validate_annotation(read(dataset/'annotations'/(record['id']+'.json')),entry)
            if not annotation['reviewed']:
                raise ValueError('Human review incomplete: '+record['id'])
            if annotation!=record['annotation']:
                changed.add(record['id'])
            record['annotation']=annotation
            record.update(score(record['predictions'],annotation))
        totals={k:sum(r[k] for r in records) for k in ('tp','fp','fn','smallTotal','smallMissed','backgroundFp')}
        tp,fp,fn=(totals[k] for k in ('tp','fp','fn'))
        updated['summaries'][strategy].update(**totals,precision=tp/(tp+fp) if tp+fp else None,
                                               recall=tp/(tp+fn) if tp+fn else None)
        pending[strategy]=records
    base=updated['summaries']['full640']
    for name,s in updated['summaries'].items():
        s['offlineGatePassed']=bool(original['split']=='test' and original['allReviewed'] and
                                      any(r['annotation']['empty'] for r in pending[name]) and name!='full640' and
                                      base['precision'] is not None and s['precision'] is not None and
                                      s['smallMissed']<base['smallMissed'] and s['precision']>=base['precision'] and
                                      s['backgroundFp']<=base['backgroundFp'])
    candidates=[n for n,s in updated['summaries'].items() if s['offlineGatePassed']]
    updated['offlineRecommendation']=min(candidates,key=lambda n:updated['summaries'][n]['p95Ms']) if candidates else 'full640'
    updated['changedAnnotationIds']=sorted(changed)
    output.mkdir(parents=True)
    write(output/'frozen_manifest.json',manifest)
    for strategy,records in pending.items():
        write(output/(strategy+'.json'),records)
    write(output/'summary.json',updated)
    print('Changed annotations:',sorted(changed))
    for name,s in updated['summaries'].items():
        print(name,{k:s[k] for k in ('tp','fp','fn','precision','recall','offlineGatePassed')})


if __name__=='__main__':
    from pathlib import Path
    parser=argparse.ArgumentParser()
    for name in ('dataset','run','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    rescore(args.dataset,args.run,args.output)
