"""Persist exact unittest commands/results; no production mutation."""
import argparse,json,subprocess,sys
from pathlib import Path
from workbench import write,digest
from offline_lab import utc

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise ValueError('Use a new evidence file')
    here=Path(__file__).resolve().parent
    commands=[['-m','unittest','test_workbench','test_diagnostics','test_offline_lab','test_tracking_continuity','-q'],
              ['-m','unittest','discover','-s','..','-p','test_detection_logic.py','-q']]
    report=dict(startedAt=utc(),python=sys.executable,commands=[],codeSha256={p.name:digest(p) for p in [here/'offline_lab.py',here/'tracking_continuity.py',here/'test_tracking_continuity.py']})
    for command in commands:
        result=subprocess.run([sys.executable,*command],cwd=here,capture_output=True,text=True,encoding='utf-8',errors='replace')
        report['commands'].append(dict(argv=[sys.executable,*command],returncode=result.returncode,stdout=result.stdout,stderr=result.stderr))
    report.update(finishedAt=utc(),passed=all(r['returncode']==0 for r in report['commands']),
        note='Synthetic unit fixture metrics are not real detection accuracy.')
    write(args.output,report)
    print(json.dumps(dict(passed=report['passed'],evidence=str(args.output)),ensure_ascii=False))
    sys.exit(0 if report['passed'] else 1)
