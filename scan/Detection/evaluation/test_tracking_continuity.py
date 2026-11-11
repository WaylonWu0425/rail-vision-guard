import unittest
import numpy as np
from offline_lab import tracker,RegionEngine,SerialTask,Manager
from tracking_continuity import ContinuityRegionEngine,profile
from ultralytics.engine.results import Boxes

P=[[0,0],[.8,0],[.8,1],[0,1]]
def person(key=1,box=None,score=.8):
    return dict(id=key,label='person',box=box or [10,10,30,50],confidence=score)

class ContinuityTests(unittest.TestCase):
    def test_once_and_short_missing_no_extra_credit(self):
        e=ContinuityRegionEngine(P,1)
        self.assertEqual(e.update([person()],0,100,100),[])
        e.update([], .5,100,100)
        self.assertEqual(e.update([person()],1,100,100),[])
        self.assertEqual(e.update([person()],1.5,100,100),[])
        self.assertEqual(len(e.update([person()],2,100,100)),1)
        self.assertEqual(e.update([person()],2.5,100,100),[])
    def test_id_handover_preserves_emitted(self):
        e=ContinuityRegionEngine(P,.5)
        e.update([person()],0,100,100);self.assertEqual(len(e.update([person()],.5,100,100)),1)
        self.assertEqual(e.update([person(2)],1,100,100),[])
        self.assertEqual(e.audit[-1]['action'],'spatial_handover')
    def test_two_people_not_merged(self):
        e=ContinuityRegionEngine(P,.5)
        e.update([person()],0,100,100);e.update([person()],.5,100,100)
        e.update([person(),person(2)],1,100,100)
        self.assertEqual(len(e.update([person(),person(2)],1.5,100,100)),1)
    def test_ambiguous_handover_refused(self):
        e=ContinuityRegionEngine(P,1)
        e.update([person(1),person(2)],0,100,100)
        e.update([person(3)],.5,100,100)
        self.assertEqual(e.states[3]['observed'],0)
        self.assertFalse(any(a['action']=='spatial_handover' for a in e.audit))
    def test_confirmed_exit_then_reenter(self):
        e=ContinuityRegionEngine(P,.5);e.update([person()],0,100,100)
        self.assertEqual(len(e.update([person()],.5,100,100)),1)
        outside=person(box=[81,10,99,50])
        e.update([outside],1,100,100);e.update([outside],2,100,100)
        e.update([person()],2.5,100,100)
        self.assertEqual(len(e.update([person()],3,100,100)),1)
    def test_boundary_jitter_does_not_realert(self):
        e=ContinuityRegionEngine(P,.5);e.update([person()],0,100,100);e.update([person()],.5,100,100)
        e.update([person(box=[81,10,99,50])],1,100,100)
        self.assertEqual(e.update([person()],1.5,100,100),[])
    def test_low_confidence_cannot_trigger(self):
        e=ContinuityRegionEngine(P,0)
        self.assertEqual(e.update([person(score=.2)],0,100,100),[])
    def test_low_score_keeps_existing_track_not_new(self):
        t=tracker(2,'continuity_v1')
        def update(score):
            return t.update(Boxes(np.asarray([[10,10,30,50,score,0]],np.float32),(100,100)))
        first=update(.8);second=update(.2);third=update(.8)
        self.assertEqual(int(first[0,4]),int(second[0,4]))
        self.assertEqual(int(first[0,4]),int(third[0,4]))
        self.assertEqual(len(tracker(2,'continuity_v1').update(Boxes(np.asarray([[10,10,30,50,.2,0]],np.float32),(100,100)))),0)
    def test_invalid_profile(self):
        with self.assertRaises(ValueError):profile('unknown')

    def test_new_id_far_away_does_not_inherit_event(self):
        e=ContinuityRegionEngine(P,.5)
        e.update([person()],0,100,100);e.update([person()],.5,100,100)
        far=person(2,[50,10,70,50])
        self.assertEqual(e.update([far],1,100,100),[])
        self.assertEqual(len(e.update([far],1.5,100,100)),1)

    def test_long_missing_starts_new_stay(self):
        e=ContinuityRegionEngine(P,.5)
        e.update([person()],0,100,100);e.update([person()],.5,100,100)
        self.assertEqual(e.update([person()],3,100,100),[])
        self.assertEqual(len(e.update([person()],3.5,100,100)),1)

    def test_two_new_ids_competing_for_old_state_not_merged(self):
        e=ContinuityRegionEngine(P,.5)
        e.update([person()],0,100,100);e.update([person()],.5,100,100)
        e.update([person(2),person(3)],1,100,100)
        self.assertFalse(any(a['action']=='spatial_handover' for a in e.audit))

    def test_same_timestamp_does_not_earn_dwell(self):
        e=ContinuityRegionEngine(P,.5)
        for _ in range(10):self.assertEqual(e.update([person()],0,100,100),[])

    def test_vehicle_does_not_trigger(self):
        e=ContinuityRegionEngine(P,0);car=person();car['label']='car'
        self.assertEqual(e.update([car],0,100,100),[])

    def test_task_worker_is_reused_and_bounded(self):
        from concurrent.futures import ThreadPoolExecutor
        import threading
        ids=[]
        with ThreadPoolExecutor(max_workers=1) as pool:
            for _ in range(10):
                task=SerialTask(pool,lambda:ids.append(threading.get_ident()))
                task.start();task.join(timeout=2)
                self.assertFalse(task.is_alive())
            self.assertEqual(len(set(ids)),1)
            with self.assertRaises(RuntimeError):task.start()

    def test_model_cache_reuses_same_object(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fixture.pt';path.write_bytes(b'test fixture, not weights')
            manager=object.__new__(Manager);manager.models={'baseline':path};manager._model_cache={}
            with patch('ultralytics.YOLO',return_value=object()) as load:
                first=manager.load_model('baseline');second=manager.load_model('baseline')
                self.assertIs(first,second);self.assertEqual(load.call_count,1)

    def test_model_cache_rejects_changed_weights(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fixture.pt';path.write_bytes(b'first fixture')
            manager=object.__new__(Manager);manager.models={'baseline':path};manager._model_cache={}
            with patch('ultralytics.YOLO',return_value=object()):manager.load_model('baseline')
            path.write_bytes(b'changed fixture')
            with self.assertRaises(ValueError):manager.load_model('baseline')

    def test_completed_task_does_not_retain_bound_owner(self):
        from concurrent.futures import ThreadPoolExecutor
        import weakref
        class Owner:
            def __init__(self,pool):self.task=SerialTask(pool,self.run)
            def run(self):pass
        with ThreadPoolExecutor(max_workers=1) as pool:
            owner=Owner(pool);reference=weakref.ref(owner)
            owner.task.start();owner.task.join(timeout=2)
            # Worker barrier ensures its previous WorkItem was released too.
            pool.submit(lambda:None).result(timeout=2)
            self.assertIsNone(owner.task.work)
            del owner
            self.assertIsNone(reference())

if __name__=='__main__':unittest.main()
