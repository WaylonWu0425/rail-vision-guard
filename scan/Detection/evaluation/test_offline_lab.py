import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from offline_lab import RegionEngine,region_points,covered,create_app,Manager,write

POLYGON=[[0,0],[1,0],[1,1],[0,1]]


def person(identity=1):
    return dict(id=identity,label='person',box=[10,10,30,50])


class OfflineLogicTest(unittest.TestCase):
    def test_transient_windows_replace_retried(self):
        from unittest.mock import patch
        with patch('offline_lab.atomic_write',side_effect=[PermissionError(),None]) as save,patch('offline_lab.time.sleep'):
            write(Path('not-written-in-unit-test.json'),{})
            self.assertEqual(save.call_count,2)

    def test_status_does_not_read_active_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'runs'/'active').mkdir(parents=True)
            (root/'runs'/'active'/'run.json').write_text('deliberately invalid; must not be opened')
            manager=object.__new__(Manager);manager.output=root
            manager.active=SimpleNamespace(id='active',snapshot=lambda:dict(runId='active',state='running'))
            self.assertEqual(manager.snapshots(),[dict(runId='active',state='running')])

    def test_one_event_per_stay(self):
        engine=RegionEngine(POLYGON,2)
        events=[]
        for t in (0,.5,1,1.5,2,2.5,3):
            events+=engine.update([person()],t,100,100)
        self.assertEqual(len(events),1)
        self.assertEqual(events[0]['mediaSeconds'],2)

    def test_pause_does_not_advance_dwell(self):
        engine=RegionEngine(POLYGON,2)
        for _ in range(10):
            self.assertEqual(engine.update([person()],0,100,100),[])

    def test_missing_long_gap_resets_dwell(self):
        engine=RegionEngine(POLYGON,2)
        engine.update([person()],0,100,100)
        engine.update([],1.5,100,100)
        self.assertEqual(engine.update([person()],2,100,100),[])

    def test_vehicle_is_not_person_event(self):
        engine=RegionEngine(POLYGON,0)
        track=person();track['label']='car'
        self.assertEqual(engine.update([track],0,100,100),[])

    def test_invalid_region(self):
        for points in ([],[[0,0],[1,0],[float('nan'),1]],[[0,0],[1,0],[2,1]],[[0,0],[.1,0],[.2,0]]):
            with self.assertRaises(ValueError):region_points(points)

    def test_recording_matches_run_model_and_media_time(self):
        event=dict(runId='one',model='candidate',mediaSeconds=5)
        record=dict(status='ready',runId='one',model='candidate',startMediaSeconds=4,endMediaSeconds=6)
        self.assertTrue(covered(event,record))
        self.assertFalse(covered({**event,'model':'baseline'},record))
        self.assertFalse(covered({**event,'runId':'two'},record))
        self.assertFalse(covered({**event,'mediaSeconds':6},record))

    def test_api_security_and_bad_upload(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            manager=SimpleNamespace(sources={},models={},output=root,active=None,snapshots=lambda:[])
            app=create_app(manager,8802);client=app.test_client();url='http://127.0.0.1:8802'
            session=client.get('/api/session',base_url=url).get_json()
            headers={'Origin':url,'X-Lab-Token':session['token']}
            self.assertEqual(client.post('/api/control',base_url=url,json={'action':'stop'}).status_code,403)
            self.assertEqual(client.get('/api/status',base_url='http://evil.invalid:8802').status_code,403)
            self.assertEqual(client.post('/api/record/import',base_url=url,headers=headers,data={}).status_code,400)
            self.assertEqual(client.post('/api/record/import',base_url=url,headers=headers,data={'video':(io.BytesIO(b'fake'),'test.mp4'),'metadata':(io.BytesIO(b'not-json'),'test.json')}).status_code,400)
            self.assertEqual(client.get('/asset/not-a-run/private.json',base_url=url).status_code,404)


if __name__=='__main__':unittest.main()
