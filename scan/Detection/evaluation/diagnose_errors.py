"""Create a read-only, original-coordinate diagnostic viewer from frozen runs."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil


def serve(output,port):
    from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
    class ReadOnlyHandler(SimpleHTTPRequestHandler):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,directory=str(output),**kwargs)
        def setup(self):
            super().setup()
            self.connection.settimeout(15)
        def do_GET(self):
            navigation = (self.headers.get('Sec-Fetch-Mode') == 'navigate' and
                          self.headers.get('Sec-Fetch-Dest') == 'document' and
                          self.path.split('?')[0] in {'/','/index.html'})
            if self.headers.get('Host') not in {f'127.0.0.1:{port}',f'localhost:{port}'} or (self.headers.get('Sec-Fetch-Site') not in {None,'none','same-origin'} and not navigation):
                self.send_error(403)
                return
            super().do_GET()
        def do_HEAD(self):
            if self.headers.get('Host') not in {f'127.0.0.1:{port}',f'localhost:{port}'}:
                self.send_error(403)
                return
            super().do_HEAD()
        def list_directory(self,path):
            self.send_error(403)
            return None
    if not (output/'index.html').is_file():
        raise ValueError('Build diagnostic output first')
    ThreadingHTTPServer(('127.0.0.1',port),ReadOnlyHandler).serve_forever()

from workbench import read, write, digest
from inference_strategies import STRATEGIES, iou


def diagnose(record):
    truth = record['annotation']['boxes']
    matched, tags, unmatched = set(), [], []
    for pred in sorted(record['predictions'], key=lambda p:p[4], reverse=True):
        candidates = [(iou(pred,b),i) for i,b in enumerate(truth) if i not in matched]
        overlap,index = max(candidates,default=(0,-1))
        if overlap >= .5:
            matched.add(index)
            tags.append(dict(box=pred,kind='matched',gt=index,iou=overlap))
            continue
        if any(max(0,min(pred[2],b[2])-max(pred[0],b[0])) * max(0,min(pred[3],b[3])-max(pred[1],b[1])) / max((pred[2]-pred[0])*(pred[3]-pred[1]),1) >= .5 for b in record['annotation']['ignore']):
            tags.append(dict(box=pred,kind='ignored'))
            continue
        best_overlap,best_index = max([(iou(pred,b),i) for i,b in enumerate(truth)],default=(0,-1))
        kind = ('background_on_empty' if record['annotation']['empty'] else
                'duplicate_candidate' if best_index in matched and best_overlap >= .5 else
                'localization_candidate' if best_overlap >= .1 else 'unmatched_candidate')
        tags.append(dict(box=pred,kind=kind,gt=best_index,iou=best_overlap))
        unmatched.append(pred)
    misses=[]
    for index,box in enumerate(truth):
        if index not in matched:
            overlap=max((iou(box,p) for p in record['predictions']),default=0)
            misses.append(dict(box=box,gt=index,bestIou=overlap,
                               kind='miss_with_nearby_prediction' if overlap >= .1 else 'miss_no_nearby_prediction'))
    if (len(matched),len(unmatched),len(misses)) != (record['tp'],record['fp'],record['fn']):
        raise ValueError(f"Diagnostic matching differs from evaluation: {record['id']}")
    return dict(predictions=tags,misses=misses,tp=record['tp'],fp=record['fp'],fn=record['fn'])


def build(args):
    if args.output.exists():
        raise ValueError('Use a new output directory; diagnostics never overwrite prior evidence')
    manifest=read(args.dataset/'manifest.json')
    entries={e['id']:e for e in manifest['entries']}
    cases={}
    provenance=[]
    summary={}
    model_hash=None
    for run in args.runs:
        run_summary=read(run/'summary.json')
        if model_hash is not None and model_hash != run_summary['modelSha256']:
            raise ValueError('Do not compare different model hashes in one diagnostic report')
        model_hash=run_summary['modelSha256']
        provenance.append(dict(run=str(run),summarySha256=digest(run/'summary.json'),split=run_summary['split']))
        for strategy in STRATEGIES:
            records=read(run/(strategy+'.json'))
            counts=Counter()
            for record in records:
                key=record['id']
                entry=entries[key]
                if digest(args.dataset/'images'/entry['image']) != record['imageSha256']:
                    raise ValueError('Image changed since evaluation: '+key)
                if key not in cases:
                    cases[key]=dict(id=key,entry=entry,annotation=record['annotation'],strategies={},tags=[])
                if record['annotation'] != cases[key]['annotation'] or strategy in cases[key]['strategies']:
                    raise ValueError('Conflicting snapshots or duplicate strategy: '+key)
                diagnosis=diagnose(record)
                cases[key]['strategies'][strategy]=diagnosis
                counts.update(p['kind'] for p in diagnosis['predictions'])
                counts.update(m['kind'] for m in diagnosis['misses'])
            summary[run_summary['split']+'/'+strategy]=dict(counts)
    for case in cases.values():
        case['tags']=sorted({p['kind'] for d in case['strategies'].values() for p in d['predictions'] if p['kind'] not in {'matched','ignored'}} |
                            {m['kind'] for d in case['strategies'].values() for m in d['misses']})
    # Representative selection balances failure types and sources, not an accuracy sample.
    chosen=[]
    for tag in ('miss_no_nearby_prediction','background_on_empty','duplicate_candidate','localization_candidate','unmatched_candidate','miss_with_nearby_prediction'):
        candidates=sorted([c for c in cases.values() if tag in c['tags']],key=lambda c:(not c['id'].startswith('photo_'),-sum(d['fp']+d['fn'] for d in c['strategies'].values()),c['id']))
        groups=set()
        for c in candidates:
            if c['entry']['group'] not in groups:
                groups.add(c['entry']['group'])
                if c['id'] not in chosen:
                    chosen.append(c['id'])
            if len(groups)>=3:
                break
    for c in sorted(cases.values(),key=lambda c:(-sum(d['fp']+d['fn'] for d in c['strategies'].values()),c['id'])):
        if len(chosen)>=16:
            break
        if c['id'] not in chosen:
            chosen.append(c['id'])
    args.output.mkdir(parents=True)
    (args.output/'assets').mkdir()
    for case in cases.values():
        source=args.dataset/'images'/case['entry']['image']
        target=args.output/'assets'/case['entry']['image']
        shutil.copyfile(source,target)
        case['image']='assets/'+case['entry']['image']
        case['currentAnnotationMatchesSnapshot'] = all(read(args.dataset/'annotations'/(case['id']+'.json')).get(k) == case['annotation'].get(k) for k in ('boxes','ignore','empty','reviewed'))
    payload=dict(version=1,modelSha256=model_hash,provenance=provenance,summary=summary,
                 representativeIds=chosen,cases=list(cases.values()),
                 note='Read-only diagnosis, not new evaluation. Candidate tags require visual review; repeated frames are not independent events.')
    write(args.output/'diagnostics.json',payload)
    template=(Path(__file__).parent/'diagnostics.html').read_text(encoding='utf-8')
    data=json.dumps(payload,ensure_ascii=False).replace('<','\\u003c')
    (args.output/'index.html').write_text(template.replace('__DIAGNOSTIC_DATA__',data),encoding='utf-8')
    print(json.dumps(dict(cases=len(cases),representatives=len(chosen),counts=summary),ensure_ascii=False,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--dataset',type=Path)
    parser.add_argument('--runs',type=Path,nargs='+')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--serve',action='store_true')
    parser.add_argument('--port',type=int,default=8801)
    args=parser.parse_args()
    if args.serve:
        serve(args.output,args.port)
    elif args.dataset is None or not args.runs:
        parser.error('Building requires --dataset and --runs')
    else:
        build(args)
