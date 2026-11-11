import unittest
from diagnose_errors import diagnose


def record(truth,predictions,tp,fp,fn,empty=False):
    return dict(id='synthetic',annotation=dict(boxes=truth,ignore=[],empty=empty),
                predictions=predictions,tp=tp,fp=fp,fn=fn)


class DiagnosisTest(unittest.TestCase):
    def test_background_on_explicit_empty(self):
        d=diagnose(record([],[[0,0,20,20,.9,0]],0,1,0,True))
        self.assertEqual(d['predictions'][0]['kind'],'background_on_empty')

    def test_duplicate_is_candidate_not_fact(self):
        d=diagnose(record([[0,0,20,20]],[[0,0,20,20,.9,0],[1,1,21,21,.8,0]],1,1,0))
        self.assertEqual(d['predictions'][1]['kind'],'duplicate_candidate')

    def test_loose_box_is_localization_candidate(self):
        d=diagnose(record([[0,0,20,20]],[[0,0,10,10,.9,0]],0,1,1))
        self.assertEqual(d['predictions'][0]['kind'],'localization_candidate')
        self.assertEqual(d['misses'][0]['kind'],'miss_with_nearby_prediction')

    def test_missing_without_prediction(self):
        d=diagnose(record([[0,0,20,20]],[],0,0,1))
        self.assertEqual(d['misses'][0]['kind'],'miss_no_nearby_prediction')

    def test_unknown_is_not_background_assertion(self):
        d=diagnose(record([[0,0,20,20]],[[70,70,90,90,.9,0]],0,1,1))
        self.assertEqual(d['predictions'][0]['kind'],'unmatched_candidate')

    def test_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            diagnose(record([],[],1,0,0))


if __name__=='__main__':
    unittest.main()
