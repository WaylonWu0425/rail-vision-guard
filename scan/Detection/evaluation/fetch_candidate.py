"""Download one named official asset, with provenance, into a new directory."""
import argparse
import json
from pathlib import Path
import urllib.request
import urllib.error

from workbench import digest,write


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():
        raise ValueError('Candidate directory already exists; will not overwrite weights')
    api='https://api.github.com/repos/ultralytics/assets/releases/tags/v8.3.0'
    request=urllib.request.Request(api,headers={'User-Agent':'station-monitoring-local-evaluation'})
    fallback_reason=None
    revision=None
    try:
        with urllib.request.urlopen(request,timeout=30) as response:
            release=json.load(response)
        asset=next(a for a in release['assets'] if a['name']=='yolo11n.pt')
        url=asset['browser_download_url']
        if not url.startswith('https://github.com/ultralytics/assets/releases/download/v8.3.0/'):
            raise ValueError('Unexpected official asset URL')
    except urllib.error.HTTPError as exc:
        if exc.code not in {403,429}:
            raise
        fallback_reason=f'GitHub API HTTP {exc.code}; official Ultralytics Hugging Face repository used'
        api='https://huggingface.co/api/models/Ultralytics/YOLO11?blobs=true'
        with urllib.request.urlopen(urllib.request.Request(api,headers={'User-Agent':'station-monitoring-local-evaluation'}),timeout=30) as response:
            info=json.load(response)
        revision=info['sha']
        sibling=next(s for s in info['siblings'] if s['rfilename']=='yolo11n.pt')
        asset=dict(name='yolo11n.pt',size=sibling['size'],id=sibling.get('blobId'),
                   digest='sha256:'+sibling['lfs']['sha256'])
        url=f'https://huggingface.co/Ultralytics/YOLO11/resolve/{revision}/yolo11n.pt'
    if not 1000000<asset['size']<50000000:
        raise ValueError('Unexpected official asset size')
    args.output.mkdir(parents=True)
    temporary=args.output/'yolo11n.pt.part'
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'station-monitoring-local-evaluation'}),timeout=60) as response,temporary.open('xb') as target:
        total=0
        while chunk:=response.read(1024*1024):
            total+=len(chunk)
            if total>50000000:
                raise ValueError('Asset exceeds expected upper size')
            target.write(chunk)
    if temporary.stat().st_size!=asset['size']:
        raise ValueError('Incomplete asset download')
    sha=digest(temporary)
    official=asset.get('digest')
    if official and official!='sha256:'+sha:
        raise ValueError('Official asset digest mismatch')
    temporary.rename(args.output/'yolo11n.pt')
    write(args.output/'provenance.json',dict(name=asset['name'],url=url,releaseApi=api,assetId=asset['id'],
          bytes=asset['size'],sha256=sha,officialDigest=official,
          revision=revision,fallbackReason=fallback_reason,
          officialDigestChecked=bool(official),license='AGPL-3.0 / Enterprise; obligations require separate review before distribution/deployment',
          purpose='Local offline evaluation only; not a production replacement'))
    print(json.dumps(dict(file=str(args.output/'yolo11n.pt'),bytes=asset['size'],sha256=sha,officialDigestChecked=bool(official)),ensure_ascii=False))
