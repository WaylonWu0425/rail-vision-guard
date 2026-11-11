import sys
import unittest
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import workbench as bench
from inference_strategies import starts, nms, predict_boxes


class EvaluationTests(unittest.TestCase):
    def test_tile_edges_covered(self):
        for length in (100, 960, 961, 1920, 2732):
            positions = starts(length)
            self.assertEqual(positions[0], 0)
            self.assertEqual(min(positions[-1] + 960, length), length)
            self.assertTrue(all(b-a <= 960 for a,b in zip(positions,positions[1:])))

    def test_nms_same_class_only(self):
        rows = [[0,0,20,20,.9,0], [1,1,21,21,.8,0], [1,1,21,21,.7,1]]
        self.assertEqual(len(nms(rows)), 2)

    def test_empty_nms(self):
        self.assertEqual(nms([]).shape, (0,6))

    def test_translation(self):
        from ultralytics.engine.results import Boxes
        class FakeModel:
            def predict(self, **opts):
                return [SimpleNamespace(boxes=Boxes(np.array([[10,10,20,20,.8,0]],dtype=np.float32), opts['source'].shape[:2]))]
        result=predict_boxes(FakeModel(),np.zeros((100,1920,3),dtype=np.uint8),'tiled640')
        self.assertEqual(len(result), 3)
        self.assertEqual(result.xyxy[-1].tolist(), [970.,10.,980.,20.])

    def test_unknown_strategy_rejected(self):
        with self.assertRaises(ValueError):
            predict_boxes(None,np.zeros((20,20,3)), 'typo')

    def test_one_to_one_matching(self):
        r=bench.score([[0,0,20,20,.9], [0,0,20,20,.8]],dict(boxes=[[0,0,20,20]], ignore=[],empty=False))
        self.assertEqual((r['tp'],r['fp'],r['fn']), (1,1,0))

    def test_small_missed(self):
        r=bench.score([],dict(boxes=[[0,0,10,20],[20,20,40,52]],ignore=[],empty=False))
        self.assertEqual((r['smallTotal'],r['smallMissed']), (1,1))

    def test_ignore_prediction(self):
        r=bench.score([[0,0,20,20,.9]],dict(boxes=[],ignore=[[0,0,20,20]],empty=True))
        self.assertEqual((r['fp'],r['ignored']), (0,1))

    def test_background_false(self):
        r=bench.score([[0,0,20,20,.9]],dict(boxes=[],ignore=[],empty=True))
        self.assertEqual(r['backgroundFp'], 1)

    def test_review_requires_explicit_empty(self):
        with self.assertRaises(ValueError):
            bench.validate_annotation(dict(boxes=[],ignore=[],reviewed=True),dict(width=100,height=100))

    def test_review_rejects_nan(self):
        with self.assertRaises(ValueError):
            bench.validate_annotation(dict(boxes=[[0,0,float('nan'),20]]),dict(width=100,height=100))

    def test_review_rejects_outside(self):
        with self.assertRaises(ValueError):
            bench.validate_annotation(dict(boxes=[[0,0,101,20]]),dict(width=100,height=100))

    def test_expired_token_refresh_and_real_save(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            bench.write(root/'manifest.json',dict(entries=[dict(id='one',image='one.jpg',width=100,height=100)]))
            args=SimpleNamespace(dataset=root,port=8799)
            first=bench.create_app(args)
            old_token=first.config['REVIEW_TOKEN']
            second=bench.create_app(args)
            client=second.test_client()
            url='http://127.0.0.1:8799'
            body=dict(boxes=[],ignore=[],empty=True,reviewed=True)
            headers={'Origin':url,'X-Review-Token':old_token}
            result=client.post('/annotation/one',base_url=url,json=body,headers=headers)
            self.assertEqual(result.status_code,403)
            self.assertEqual(result.get_json()['code'],'token_expired')
            self.assertFalse((root/'annotations'/'one.json').exists())
            self.assertEqual(client.get('/session',base_url=url,headers={'Sec-Fetch-Site':'cross-site'}).status_code,403)
            response=client.get('/session',base_url=url,headers={'Sec-Fetch-Site':'same-origin'})
            self.assertEqual(response.headers['Cache-Control'],'no-store')
            headers['X-Review-Token']=response.get_json()['token']
            self.assertEqual(client.post('/annotation/one',base_url=url,json=body,headers=headers).status_code,200)
            self.assertTrue(bench.read(root/'annotations'/'one.json')['reviewed'])
            headers['Origin']='http://evil.invalid'
            self.assertEqual(client.post('/annotation/one',base_url=url,json=body,headers=headers).get_json()['code'],'origin_rejected')

    def test_local_api_save_reload_and_csrf(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bench.write(root/'manifest.json',dict(entries=[dict(id='one',image='one.jpg',width=100,height=100)]))
            app = bench.create_app(SimpleNamespace(dataset=root, port=8799))
            client = app.test_client()
            url='http://127.0.0.1:8799'
            self.assertEqual(client.get('/manifest',base_url=url).status_code,200)
            self.assertEqual(client.get('/manifest',base_url='http://evil.invalid:8799').status_code,403)
            body=dict(boxes=[[10,10,30,40]],ignore=[],empty=False,reviewed=True)
            self.assertEqual(client.post('/annotation/one',base_url=url,json=body).status_code,403)
            headers={'X-Review-Token':app.config['REVIEW_TOKEN'],'Origin':url}
            self.assertEqual(client.post('/annotation/one',base_url=url,json=body,headers=headers).status_code,200)
            saved=client.get('/annotation/one',base_url=url).get_json()
            self.assertTrue(saved['reviewed'])
            self.assertEqual(saved['boxes'],body['boxes'])
            self.assertTrue((root/'labels'/'one.txt').read_text().startswith('0 0.20000000'))
            self.assertEqual(client.post('/annotation/missing',base_url=url,json=body,headers=headers).status_code,404)

    def test_unreviewed_dataset_cannot_generate_metrics(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            bench.write(root/'manifest.json',dict(entries=[dict(id='one',split='test')]))
            with self.assertRaisesRegex(ValueError,'No manually reviewed'):
                bench.evaluate(SimpleNamespace(dataset=root, split='test'))

    def test_evaluation_output_is_snapshot_and_partial_cannot_pass_gate(self):
        from unittest.mock import patch
        from ultralytics.engine.results import Boxes
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'images').mkdir()
            import cv2
            cv2.imencode('.jpg',np.zeros((100,100,3),dtype=np.uint8))[1].tofile(str(root/'images'/'one.jpg'))
            bench.write(root/'manifest.json',dict(entries=[dict(id='one',image='one.jpg',group='a',split='test',width=100,height=100),dict(id='two',split='test')]))
            bench.write(root/'annotations'/'one.json',dict(boxes=[[0,0,20,20]],ignore=[],empty=False,reviewed=True))
            model=root/'fake.pt'
            model.write_bytes(b'synthetic-unit-test-only')
            boxes=Boxes(np.array([[0,0,20,20,.9,0]],dtype=np.float32),(100,100))
            with patch('ultralytics.YOLO',return_value=SimpleNamespace(names={0:'person'})), patch.object(bench,'predict_boxes',return_value=boxes):
                bench.evaluate(SimpleNamespace(dataset=root,split='test',output=root/'run',model=model,device='cpu',repeats=1))
            summary=bench.read(root/'run'/'summary.json')
            self.assertFalse(summary['allReviewed'])
            self.assertFalse(summary['activated'])
            for s in summary['summaries'].values():
                self.assertEqual(s['tp'],1)
                self.assertFalse(s['offlineGatePassed'])
            self.assertIn('annotation',bench.read(root/'run'/'full640.json')[0])

    def test_explicit_two_strategy_comparison(self):
        from unittest.mock import patch
        from contextlib import redirect_stdout
        import io
        from ultralytics.engine.results import Boxes
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'images').mkdir()
            import cv2
            cv2.imencode('.jpg',np.zeros((100,100,3),dtype=np.uint8))[1].tofile(str(root/'images'/'one.jpg'))
            bench.write(root/'manifest.json',dict(entries=[dict(id='one',image='one.jpg',group='a',split='test',width=100,height=100)]))
            bench.write(root/'annotations'/'one.json',dict(boxes=[],ignore=[],empty=True,reviewed=True))
            model=root/'fake.pt'
            model.write_bytes(b'synthetic-test-only')
            boxes=Boxes(np.empty((0,6),dtype=np.float32),(100,100))
            with patch('ultralytics.YOLO',return_value=SimpleNamespace(names={0:'person'})), patch.object(bench,'predict_boxes',return_value=boxes), redirect_stdout(io.StringIO()):
                bench.evaluate(SimpleNamespace(dataset=root,split='test',output=root/'run',model=model,device='cpu',repeats=1,strategies=['full640','full1280']))
            summary=bench.read(root/'run'/'summary.json')
            self.assertEqual(set(summary['summaries']),{'full640','full1280'})
            self.assertFalse((root/'run'/'tiled640.json').exists())
            self.assertFalse(summary['activated'])


if __name__ == '__main__':
    unittest.main()
