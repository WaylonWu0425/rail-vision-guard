"""Isolated local video lab. Never imports the production service or database."""
from __future__ import annotations

import argparse
from collections import deque
from concurrent.futures import ThreadPoolExecutor,TimeoutError as FutureTimeout
from copy import deepcopy
from datetime import datetime,timezone
import json
import math
from pathlib import Path
import subprocess
import threading
import time
from types import SimpleNamespace
import uuid

import cv2
import numpy as np
import psutil
from flask import Flask,Response,abort,jsonify,request,send_from_directory

from workbench import read,write as atomic_write,digest
from inference_strategies import predict_boxes
from tracking_continuity import profile,ContinuityRegionEngine

HERE=Path(__file__).resolve().parent


def write(path,value):
    # Windows readers/antivirus may briefly deny atomic replacement.
    for attempt in range(8):
        try:
            atomic_write(path,value)
            return
        except PermissionError:
            if attempt==7:
                raise
            time.sleep(.01*(attempt+1))


def utc():
    return datetime.now(timezone.utc).isoformat()


def region_points(value):
    if not isinstance(value,list) or not 3<=len(value)<=20:
        raise ValueError('请绘制3—20个顶点的区域')
    points=[]
    for pair in value:
        if not isinstance(pair,list) or len(pair)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=1 for v in pair):
            raise ValueError('区域坐标必须为0—1内的有限数值')
        points.append(pair)
    if abs(cv2.contourArea(np.asarray(points,dtype=np.float32)))<.0001:
        raise ValueError('区域面积过小或顶点顺序有误')
    return points


class RegionEngine:
    """Source-time dwell; grace is bounded and a track stay emits once."""
    def __init__(self,points,dwell,grace=1.0):
        self.points=points
        self.dwell=dwell
        self.grace=grace
        self.states={}

    def update(self,tracks,seconds,width,height):
        seen=set()
        events=[]
        polygon=np.asarray([[x*width,y*height] for x,y in self.points],dtype=np.float32)
        for track in tracks:
            if track['label']!='person':
                continue
            box=track['box']; identity=track['id']
            inside=cv2.pointPolygonTest(polygon,((box[0]+box[2])/2,box[3]),False)>=0
            if not inside:
                self.states.pop(identity,None)
                continue
            seen.add(identity)
            state=self.states.get(identity)
            if state is None or seconds-state['last']>self.grace:
                state=dict(entered=seconds,last=seconds,emitted=False)
                self.states[identity]=state
            state['last']=seconds
            if not state['emitted'] and seconds-state['entered']>=self.dwell:
                state['emitted']=True
                events.append(dict(trackId=identity,mediaSeconds=seconds,dwellSeconds=seconds-state['entered'],box=box))
        for identity,state in list(self.states.items()):
            if identity not in seen and seconds-state['last']>self.grace:
                del self.states[identity]
        return events


def covered(event,recording):
    return (recording.get('status')=='ready' and event['runId']==recording['runId'] and
            event['model']==recording['model'] and recording['startMediaSeconds']<=event['mediaSeconds']<recording['endMediaSeconds'])


def tracker(hz,name='legacy'):
    from ultralytics.trackers.byte_tracker import BYTETracker
    # Buffer measured in inference updates, not decoded source frames.
    p=profile(name,hz)
    args=SimpleNamespace(tracker_type='bytetrack',track_high_thresh=p['highThreshold'],track_low_thresh=p['lowThreshold'],
                         new_track_thresh=p['newThreshold'],track_buffer=p['bufferUpdates'],match_thresh=.8,fuse_score=True)
    return BYTETracker(args)


def render(frame,tracks,points,seconds,model):
    view=frame.copy(); height,width=view.shape[:2]
    if points:
        polygon=np.asarray([[x*width,y*height] for x,y in points],np.int32)
        cv2.polylines(view,[polygon],True,(0,190,245),2)
    for t in tracks:
        x1,y1,x2,y2=map(int,t['box'])
        cv2.rectangle(view,(x1,y1),(x2,y2),(255,170,35),2)
        cv2.putText(view,f"{t['label']} #{t['id']} {t['confidence']:.0%}",(x1,max(18,y1-5)),cv2.FONT_HERSHEY_SIMPLEX,.5,(255,170,35),1)
    cv2.putText(view,f"OFFLINE {model} media={seconds:.2f}s",(15,30),cv2.FONT_HERSHEY_SIMPLEX,.7,(20,235,235),2)
    return view


class Job:
    def __init__(self,manager,source,config):
        self.manager=manager; self.source=source; self.config=config
        self.id=uuid.uuid4().hex[:16]; self.directory=manager.output/'runs'/self.id
        self.directory.mkdir(parents=True)
        self.lock=threading.RLock(); self.stop=threading.Event(); self.paused=False
        self.state='loading'; self.error=None; self.seconds=0.; self.frame_index=-1
        self.events=[]; self.recordings=[]; self.latest={}; self.tracks={}; self.runtimes={}
        self.record_requested=None; self.record_active=None; self.record_stop=False
        self.started=utc(); self.metrics={}; self.resource_samples=deque(maxlen=1800)
        self.capture_released=False; self.writer_released=True; self.completed_frames=0
        self.thread=SerialTask(manager.executor,self.work)

    def persist(self):
        write(self.directory/'run.json',self.snapshot())

    def snapshot(self):
        with self.lock:
            return deepcopy(dict(runId=self.id,sourceId=self.source['id'],sourceName=self.source['name'],
                sourceSha256=self.source['sha256'],sourceCaptureTime=None,startedAt=self.started,
                mode='offline_replay',state=self.state,error=self.error,mediaSeconds=self.seconds,
                frameIndex=self.frame_index,duration=self.source['duration'],config=self.config,events=self.events,
                recordings=self.recordings,metrics=self.metrics,resourceSamples=list(self.resource_samples),
                recording=bool(self.record_active or self.record_requested),captureReleased=self.capture_released,
                writerReleased=self.writer_released,workerAlive=self.thread.is_alive(),
                workerScope='task; one reusable executor thread retained until Manager.close',framesDecoded=self.completed_frames))

    def request_record(self,model):
        with self.lock:
            if self.state!='running' or self.paused:
                raise ValueError('请先运行视频，再开始手动录像')
            if model not in self.config['models'] or self.record_active or self.record_requested:
                raise ValueError('录像模型无效或已有录像正在进行')
            self.record_requested=model

    def finish_record(self):
        with self.lock:
            active=self.record_active
            if active is None:
                return
            active['writer'].release(); self.writer_released=True; self.record_active=None
            meta=active['meta']; meta['status']='converting'
        try:
            if meta['frames']<1:
                raise ValueError('录像没有有效帧，未入索引')
            import imageio_ffmpeg
            target=self.directory/(meta['id']+'.mp4')
            completed=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-hide_banner','-loglevel','error','-y',
               '-i',str(active['raw']),'-c:v','libx264','-preset','veryfast','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],
               capture_output=True,text=True,timeout=90)
            if completed.returncode!=0 or not target.is_file():
                raise RuntimeError('H.264转换失败：'+completed.stderr[-300:])
            cap=cv2.VideoCapture(str(target))
            try:
                ok,_=cap.read()
                if not ok:
                    raise ValueError('录像无法解码，未入索引')
            finally:
                cap.release()
            complete={**meta,**dict(status='ready',file=target.name,sha256=digest(target),bytes=target.stat().st_size,
                        committedAt=utc(),container='mp4',codec='h264',duration=meta['frames']/meta['fps'])
                      }
        except Exception as exc:
            complete={**meta,**dict(status='failed',error=str(exc),rawFile=active['raw'].name)}
        write(self.directory/(meta['id']+'.json'),complete)
        with self.lock:
            meta.update(complete)
        self.persist()

    def process_record(self,views,fps,index):
        with self.lock:
            if self.record_requested:
                identity='record_'+uuid.uuid4().hex[:12]; model=self.record_requested; self.record_requested=None
                raw=self.directory/(identity+'.raw.mp4'); height,width=views[model].shape[:2]
                writer=cv2.VideoWriter(str(raw),cv2.VideoWriter_fourcc(*'mp4v'),fps,(width,height))
                if not writer.isOpened():
                    writer.release(); raise RuntimeError('录像编码器不可用')
                meta=dict(id=identity,runId=self.id,sourceId=self.source['id'],sourceSha256=self.source['sha256'],
                          model=model,status='recording',startMediaSeconds=index/fps,endMediaSeconds=index/fps,
                          startFrame=index,endFrameExclusive=index,frames=0,fps=fps,requestedAt=utc(),
                          sourceCaptureTime=None,mode='offline_manual_recording')
                self.recordings.append(meta); self.record_active=dict(writer=writer,raw=raw,meta=meta)
                self.writer_released=False
            active=self.record_active
            if active:
                active['writer'].write(views[active['meta']['model']])
                active['meta']['frames']+=1; active['meta']['endMediaSeconds']=(index+1)/fps
                active['meta']['endFrameExclusive']=index+1
            finish=self.record_stop; self.record_stop=False
        if finish:
            self.finish_record()

    def work(self):
        capture=None
        try:
            from ultralytics import YOLO
            capture=cv2.VideoCapture(self.source['path'])
            if not capture.isOpened():
                raise ValueError('原视频无法打开')
            fps=capture.get(cv2.CAP_PROP_FPS); count=int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            if not math.isfinite(fps) or fps<=0 or count<=0:
                raise ValueError('原视频时间基无效')
            width=int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)); height=int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            selected=self.config['models']; hz=self.config['inferenceHz']; interval=max(1,round(fps/hz))
            runtimes={}; trackers={}; engines={}; histories={}; inference_count={}; last_finished={}
            for model in selected:
                if self.stop.is_set():
                    return
                model_path=self.manager.models[model]
                if not model_path.is_file():
                    raise ValueError('模型文件不存在：'+model)
                runtimes[model]=self.manager.load_model(model); trackers[model]=tracker(hz,self.config.get('trackingProfile','legacy'))
                engine_type=ContinuityRegionEngine if self.config.get('trackingProfile')=='continuity_v1' else RegionEngine
                engines[model]=engine_type(self.config['points'],self.config['dwellSeconds']) if self.config['points'] else None
                histories[model]=set(); inference_count[model]=0; last_finished[model]=None
                self.tracks[model]=[]
            self.runtimes={m:dict(sha256=digest(self.manager.models[m]),classes=runtimes[m].names) for m in selected}
            write(self.directory/'provenance.json',dict(source=self.source,models=self.runtimes,config=self.config))
            process=psutil.Process(); process.cpu_percent(); wall_start=time.perf_counter(); index=0
            play_origin=time.perf_counter(); pause_started=None
            self.state='running'
            with (self.directory/'frames.jsonl').open('a',encoding='utf-8') as log, (self.directory/'resources.jsonl').open('a',encoding='utf-8') as resources:
                while not self.stop.is_set():
                    if self.paused:
                        self.state='paused'
                        if pause_started is None:
                            pause_started=time.perf_counter()
                        if self.record_stop:
                            self.record_stop=False; self.finish_record()
                        self.stop.wait(.05); continue
                    if pause_started is not None:
                        play_origin+=time.perf_counter()-pause_started; pause_started=None
                    self.state='running'; tick=time.perf_counter()
                    ok,frame=capture.read()
                    if not ok:
                        if index<count:
                            raise RuntimeError(f'视频读取提前失败，帧{index}/{count}')
                        self.state='finished'; break
                    seconds=index/fps; self.seconds=seconds; self.frame_index=index; self.completed_frames=index+1
                    pending=[]
                    if index%interval==0:
                        for model in selected:
                            before=time.perf_counter()
                            p=profile(self.config.get('trackingProfile','legacy'),hz)
                            boxes=predict_boxes(runtimes[model],frame,self.config['strategy'],p['inferenceConfidence'],'cpu',False)
                            # Only person/car; class names remain model-specific.
                            keep=np.asarray([str(runtimes[model].names[int(v)]).lower() in {'person','car'} for v in boxes.cls],dtype=bool)
                            selected_boxes=boxes[keep]
                            tracked=trackers[model].update(selected_boxes,frame)
                            tracks=[]
                            for row in tracked:
                                x1,y1,x2,y2,identity,confidence,cls=row[:7]
                                if confidence<p['reportConfidence']:
                                    continue
                                tracks.append(dict(id=int(identity),label=str(runtimes[model].names[int(cls)]).lower(),confidence=float(confidence),box=[float(x1),float(y1),float(x2),float(y2)]))
                            self.tracks[model]=tracks; histories[model].update(t['id'] for t in tracks)
                            finished=time.perf_counter(); inference_count[model]+=1
                            previous=last_finished[model]; last_finished[model]=finished
                            model_metrics=dict(inferenceMs=round((finished-before)*1000,2),
                                completedInferenceHz=round(1/(finished-previous),2) if previous else 0,
                                inferenceUpdates=inference_count[model],visibleTracks=len(tracks),observedTrackIds=len(histories[model]))
                            with self.lock:
                                self.metrics[model]=model_metrics
                            transitions=[]
                            if engines[model]:
                                previous_transitions=len(getattr(engines[model],'audit',[]))
                                for event in engines[model].update(tracks,seconds,width,height):
                                    event.update(id='event_'+uuid.uuid4().hex[:12],runId=self.id,sourceId=self.source['id'],model=model,
                                                 frameIndex=index,wallTime=utc(),sourceCaptureTime=None,type='offline_region_dwell',status='pending_review')
                                    pending.append(event)
                                transitions=getattr(engines[model],'audit',[])[previous_transitions:]
                            log.write(json.dumps(dict(frameIndex=index,mediaSeconds=seconds,model=model,tracks=tracks,
                                lowScoreInputCount=int(sum(selected_boxes.conf<.45)),ruleTransitions=transitions,
                                metrics=self.metrics[model]),ensure_ascii=False)+'\n'); log.flush()
                        sample=dict(wallElapsedSeconds=round(time.perf_counter()-wall_start,3),mediaSeconds=seconds,
                                    rssBytes=process.memory_info().rss,processCpuPercent=process.cpu_percent(),threads=process.num_threads())
                        self.resource_samples.append(sample); resources.write(json.dumps(sample)+'\n'); resources.flush()
                    views={m:render(frame,self.tracks[m],self.config['points'],seconds,m) for m in selected}
                    for event in pending:
                        file=event['id']+'.jpg'
                        cv2.imencode('.jpg',views[event['model']])[1].tofile(str(self.directory/file))
                        event['snapshot']=file
                        with self.lock:
                            self.events.append(event)
                        write(self.directory/'events.json',self.events)
                    self.process_record(views,fps,index)
                    if index%max(1,round(fps/5))==0:
                        with self.lock:
                            self.latest={m:cv2.imencode('.jpg',view,[cv2.IMWRITE_JPEG_QUALITY,75])[1].tobytes() for m,view in views.items()}
                    if index%max(1,round(fps*2))==0:
                        self.persist()
                    index+=1
                    self.stop.wait(max(0,(index/fps)-(time.perf_counter()-play_origin)))
        except Exception as exc:
            self.state='failed'; self.error=str(exc)
        finally:
            terminal_state=self.state if self.state in {'failed','finished'} else 'stopped'
            if self.record_active:
                self.state='finalizing'
            if capture is not None:
                capture.release()
            self.capture_released=True
            try:
                if self.record_active:
                    self.finish_record()
                self.state=terminal_state
            except Exception as exc:
                self.state='failed'; self.error='录像收尾失败：'+str(exc)
            finally:
                self.record_requested=None
                self.persist()


class SerialTask:
    """Thread-compatible task handle on a bounded, reused native worker.

    Repeated new Python workers caused native inference pools to accumulate on
    this Windows runtime. is_alive describes this task, not the retained worker.
    """
    def __init__(self,executor,work):
        self.executor=executor;self.work=work;self.future=None

    def start(self):
        if self.future is not None:raise RuntimeError('任务不能重复启动')
        self.future=self.executor.submit(self.work)
        # The executor now owns the callable. Keeping a bound method here
        # creates Job -> SerialTask -> bound Job.work -> Job after completion,
        # delaying old preview/event/resource buffers until cyclic GC runs.
        self.work=None

    def is_alive(self):
        return self.future is not None and not self.future.done()

    def join(self,timeout=None):
        if self.future is None:return
        try:self.future.result(timeout=timeout)
        except FutureTimeout:return


class Manager:
    def __init__(self,dataset,output,tracking_profile='legacy'):
        profile(tracking_profile)
        self.default_tracking_profile=tracking_profile
        self.executor=ThreadPoolExecutor(max_workers=1,thread_name_prefix='offline-inference')
        self._model_cache={}
        self.output=output; self.output.mkdir(parents=True,exist_ok=True)
        self.models={'baseline':HERE.parent/'models'/'best.pt',
                     'candidate':dataset/'模型候选核查_20261016'/'candidate'/'yolo11n.pt'}
        self.sources={}
        for i,source in enumerate(read(dataset/'manifest.json')['sources']):
            path=Path(source['path']); cap=cv2.VideoCapture(str(path))
            try:
                fps=cap.get(cv2.CAP_PROP_FPS); frames=cap.get(cv2.CAP_PROP_FRAME_COUNT)
                self.sources[str(i)]=dict(id=str(i),name=path.name,path=str(path),sha256=source['sha256'],
                                         fps=fps,duration=frames/fps if fps>0 else 0)
            finally:
                cap.release()
        self.active=None; self.lock=threading.RLock()

    def close(self):
        if self.active:self.active.stop.set()
        self.executor.shutdown(wait=True,cancel_futures=True)
        self._model_cache.clear()

    def load_model(self,name):
        """Single-worker owned, max two models; pin file hashes until restart.

        Detection forward is stateless. Trackers/region/recording state are
        deliberately rebuilt per Job, never cached with these model objects.
        """
        from ultralytics import YOLO
        path=self.models[name]
        if not path.is_file():raise ValueError('模型文件不存在：'+name)
        sha=digest(path)
        if name in self._model_cache:
            entry=self._model_cache[name]
            if entry['sha256']!=sha:raise ValueError('模型文件已变化，请停止并重启离线实验台')
            return entry['model']
        model=YOLO(str(path))
        self._model_cache[name]=dict(sha256=sha,model=model)
        return model

    def start(self,body):
        with self.lock:
            if self.active and self.active.thread.is_alive():
                raise ValueError('已有离线任务，请先停止并等待释放资源')
            source=self.sources.get(str(body.get('sourceId')))
            if source is None:
                raise ValueError('请选择已盘点的本地视频')
            if not Path(source['path']).is_file():
                raise ValueError('原视频文件不存在或已移动，请检查原始目录')
            models=body.get('models',['candidate'])
            if not isinstance(models,list) or not models or len(models)!=len(set(models)) or any(m not in self.models for m in models):
                raise ValueError('模型选项无效')
            if digest(Path(source['path']))!=source['sha256']:
                raise ValueError('原视频发生变化，请重新盘点，不使用旧来源哈希')
            points=region_points(body.get('points')) if body.get('points') else []
            dwell=float(body.get('dwellSeconds',2))
            if not math.isfinite(dwell) or not .5<=dwell<=60:
                raise ValueError('停留时长须在0.5—60秒')
            strategy=body.get('strategy','full1280')
            if strategy not in {'full640','full1280'}:
                raise ValueError('仅支持固定640/1280对照')
            tracking_name=body.get('trackingProfile',self.default_tracking_profile)
            p=profile(tracking_name,2)
            config=dict(models=models,points=points,dwellSeconds=dwell,strategy=strategy,inferenceHz=2,
                        confidence=.45,tracker='ByteTrack',trackerBufferUpdates=p['bufferUpdates'],
                        trackingProfile=tracking_name,trackingParameters=p,
                        modelLifecycle='hash-pinned Manager cache; trackers/region/recordings reset per Job',
                        notice='Offline rule exercise, not a judgment of unauthorized activity; no tracking ground truth')
            self.active=Job(self,source,config); self.active.persist(); self.active.thread.start()
            return self.active

    def snapshots(self):
        result=[]
        for file in sorted((self.output/'runs').glob('*/run.json'),reverse=True):
            if self.active and file.parent.name==self.active.id:
                continue
            result.append(read(file))
        if self.active:
            fresh=self.active.snapshot()
            result=[r for r in result if r['runId']!=fresh['runId']]
            result.insert(0,fresh)
        return result


def create_app(manager,port):
    app=Flask(__name__); app.config['MAX_CONTENT_LENGTH']=100*1024*1024
    token=uuid.uuid4().hex
    @app.before_request
    def guard():
        if request.host not in {f'127.0.0.1:{port}',f'localhost:{port}'}:
            abort(403)
        if request.method=='POST':
            if request.headers.get('Origin') not in {f'http://127.0.0.1:{port}',f'http://localhost:{port}'}:
                return jsonify(error='请从本机离线实验台打开页面',code='origin_rejected'),403
            if request.headers.get('X-Lab-Token')!=token:
                return jsonify(error='会话已更新',code='token_expired'),403
    @app.after_request
    def headers(response):
        if request.path.startswith('/api') or request.path=='/':
            response.headers['Cache-Control']='no-store'
        return response
    @app.errorhandler(ValueError)
    def invalid(exc):
        return jsonify(error=str(exc)),400
    @app.errorhandler(413)
    def too_large(exc):
        return jsonify(error='文件超过100MB，未导入；请保留本地原文件'),413
    @app.get('/')
    def index():
        return (HERE/'offline_lab.html').read_text(encoding='utf-8').replace('__LAB_TOKEN__',token)
    @app.get('/api/session')
    def session():
        if request.headers.get('Sec-Fetch-Site') not in {None,'none','same-origin'}:
            abort(403)
        return jsonify(token=token)
    @app.get('/api/catalog')
    def catalog():
        return jsonify(sources=list(manager.sources.values()),models={m:dict(available=p.is_file(),name=p.name) for m,p in manager.models.items()})
    @app.get('/api/source/<identity>/preview.jpg')
    def source_preview(identity):
        if identity not in manager.sources:
            abort(404)
        cap=cv2.VideoCapture(manager.sources[identity]['path'])
        try:
            ok,frame=cap.read()
            if not ok:
                raise ValueError('原视频首帧无法解码')
            return Response(cv2.imencode('.jpg',frame)[1].tobytes(),mimetype='image/jpeg')
        finally:
            cap.release()
    @app.post('/api/start')
    def start():
        return jsonify(manager.start(request.get_json() or {}).snapshot()),202
    @app.get('/api/status')
    def status():
        runs=manager.snapshots()
        for run in runs:
            for event in run['events']:
                event['recordings']=[dict(id=r['id'],offsetSeconds=event['mediaSeconds']-r['startMediaSeconds']) for r in run['recordings'] if covered(event,r)]
        return jsonify(active=manager.active.id if manager.active else None,runs=runs)
    @app.post('/api/control')
    def control():
        job=manager.active
        if job is None:
            raise ValueError('没有活动任务')
        action=(request.get_json() or {}).get('action')
        with job.lock:
            if action=='stop':
                job.stop.set()
                if job.thread.is_alive():
                    job.state='stopping'
            elif action in {'pause','resume'} and job.thread.is_alive() and job.state in {'running','paused'}:
                job.paused=action=='pause'
            else:
                raise ValueError('当前状态不支持该操作；视频结束后请新建运行批次')
        return jsonify(success=True)
    @app.get('/api/frame/<model>.jpg')
    def frame(model):
        job=manager.active
        if job is None:
            abort(404)
        with job.lock:
            data=job.latest.get(model)
        if data is None:
            return Response(status=204)
        return Response(data,mimetype='image/jpeg',headers={'Cache-Control':'no-store'})
    @app.post('/api/record/start')
    def record_start():
        if manager.active is None:
            raise ValueError('请先开始视频任务')
        manager.active.request_record((request.get_json() or {}).get('model','candidate'))
        return jsonify(accepted=True),202
    @app.post('/api/record/stop')
    def record_stop():
        if manager.active is None:
            raise ValueError('没有活动任务')
        with manager.active.lock:
            manager.active.record_requested=None
            manager.active.record_stop=True
        return jsonify(accepted=True),202
    @app.post('/api/record/import')
    def import_record():
        if 'video' not in request.files or 'metadata' not in request.files:
            raise ValueError('请选择本工具导出的录像及同名JSON索引')
        metadata=request.files['metadata'].read(1024*1024+1)
        if len(metadata)>1024*1024:
            raise ValueError('索引文件过大')
        try:
            meta=json.loads(metadata)
        except (ValueError,UnicodeError):
            raise ValueError('索引不是有效JSON')
        if not isinstance(meta,dict):
            raise ValueError('索引必须是JSON对象')
        candidates=[r for run in manager.snapshots() for r in run['recordings'] if r['id']==meta.get('id') and run['runId']==meta.get('runId') and r['status']=='ready']
        if not candidates:
            raise ValueError('只接受本沙箱已生成的录像索引，不猜测外部文件时间')
        original=candidates[0]
        if any(meta.get(k)!=original.get(k) for k in ('sha256','sourceSha256','model','startMediaSeconds','endMediaSeconds')):
            raise ValueError('索引与沙箱记录不一致，未导入')
        import hashlib
        h=hashlib.sha256(); length=0
        while chunk:=request.files['video'].stream.read(1024*1024):
            h.update(chunk); length+=len(chunk)
        if h.hexdigest()!=original['sha256'] or length!=original['bytes']:
            raise ValueError('录像文件校验不一致，未导入；请保留本地原文件')
        write(manager.output/'imports'/(uuid.uuid4().hex+'.json'),dict(recordingId=original['id'],runId=original['runId'],importedAt=utc(),sha256=h.hexdigest(),duplicate=True))
        return jsonify(saved=True,duplicate=True,message='上传校验成功；录像已存在离线索引，不重复入库')
    @app.get('/asset/<run_id>/<filename>')
    def asset(run_id,filename):
        if len(run_id)!=16 or any(c not in '0123456789abcdef' for c in run_id) or '/' in filename or '\\' in filename:
            abort(404)
        if Path(filename).suffix not in {'.mp4','.json','.jpg','.jsonl'}:
            abort(404)
        return send_from_directory(manager.output/'runs'/run_id,filename,conditional=True)
    return app


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--dataset',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--port',type=int,default=8802)
    parser.add_argument('--tracking-profile',choices=['legacy','low_score','buffered_score','continuity_v1'],default='legacy')
    args=parser.parse_args()
    manager=Manager(args.dataset,args.output,args.tracking_profile)
    import atexit
    atexit.register(lambda: manager.active.stop.set() if manager.active else None)
    try:
        create_app(manager,args.port).run(host='127.0.0.1',port=args.port,threaded=True,debug=False)
    finally:
        manager.close()
