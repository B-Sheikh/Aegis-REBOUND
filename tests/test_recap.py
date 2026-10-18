import unittest,copy,json
import numpy as np
from pathlib import Path
from rebound.data import patient,event,public_patient
from rebound.recap import replay,Recap
from rebound.benchmark import probe_value

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=patient(65)
    def test_future_isolation(self):
        p=copy.deepcopy(self.p);a=replay(p,120).result()
        for row in p['stream'][121:]:row.update(rr=50,hr=190,steps=1000,pef_lpm=80,pm25=500)
        p['truth']=[];p['targets']=[];p['scenario']='unavailable'
        self.assertEqual(a,replay(p,120).result())
    def test_public_contract_hides_ground_truth(self):
        p=public_patient(self.p)
        self.assertEqual(set(p),{'ehr','stream'})
        self.assertEqual(replay(self.p,120).result(),replay(p,120).result())
    def test_missing_data_abstains(self):
        r=replay(patient(66),174).result()
        self.assertEqual(r['status'],'abstain');self.assertIsNone(r['risk']);self.assertEqual(r['forecast'],[])
    def test_weights_and_covariance(self):
        m=replay(self.p,130);r=m.result()
        self.assertAlmostEqual(sum(v['weight'] for v in r['hypotheses']),1,places=4)
        for model in m.models:self.assertGreater(np.linalg.eigvalsh(model['P']).min(),-1e-9)
        self.assertEqual(len(r['forecast']),24)
        json.dumps(r,allow_nan=False)
    def test_probe_updates_state(self):
        m=replay(patient(66),130);a=m.result();m.observe_probe('peak_flow',.65);b=m.result()
        self.assertNotEqual(a['hypotheses'],b['hypotheses']);self.assertEqual(len(m.actions),1)
    def test_budget_and_cooldown(self):
        m=replay(self.p,120);m.observe_probe('peak_flow',.9)
        with self.assertRaises(ValueError):m.observe_probe('peak_flow',.9)
        for row in self.p['stream'][121:145]:m.feed(row)
        m.observe_probe('independent_rr',20)
        for row in self.p['stream'][145:169]:m.feed(row)
        with self.assertRaises(ValueError):m.observe_probe('peak_flow',.9)
        self.assertEqual(m.measurement_plan()['selected'],'wait')
    def test_plan_is_pure_no_hidden_measurement(self):
        m=replay(self.p,120);a=copy.deepcopy(m.models);p=m.measurement_plan()
        for before,after in zip(a,m.models):np.testing.assert_array_equal(before['x'],after['x'])
        self.assertEqual(m.actions,[])
        for c in p['candidates']:self.assertAlmostEqual(c['net_score'],c['expected_gain_nats']-c['burden_nats'],places=4)
    def test_ehr_changes_twin(self):
        p=copy.deepcopy(self.p);p['ehr']['resting_rr']+=3
        self.assertNotEqual(replay(p,120).result()['hypotheses'],replay(self.p,120).result()['hypotheses'])
    def test_sequential_cadence(self):
        m=Recap(self.p['ehr'])
        with self.assertRaises(ValueError):m.feed(self.p['stream'][2])
    def test_endpoint_strict_boundary(self):
        self.assertEqual(event([.8,.79,.79]),0);self.assertEqual(event([.79,.79,.79]),1)
    def test_probe_limits(self):
        for action,value in [('peak_flow',float('nan')),('independent_rr',80),('peak_flow',2),('drug',1)]:
            with self.subTest(action=action,value=value):
                with self.assertRaises(ValueError):replay(self.p,120).observe_probe(action,value)
    def test_repeatability(self):
        self.assertEqual(self.p,patient(65));self.assertEqual(probe_value(self.p,120,'peak_flow'),self.p['targets'][120])

class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app import App
        cls.app=App()
    def test_snapshot_and_reveal_boundary(self):
        a=self.app.view({'patient':'R-065','t':120})
        self.assertNotIn('truth',a);self.assertNotIn('retrospective',a)
        self.assertTrue(all(v['t']<=120 for v in a['history']))
        b=self.app.view({'patient':'R-065','t':120,'reveal':True})
        self.assertEqual(a['result'],b['result']);self.assertEqual(len(b['retrospective']),24)
    def test_probe_reconstruction(self):
        a=self.app.view({'patient':'R-065','t':120,'probes':[{'t':120,'action':'peak_flow','value':-999}]})
        self.assertEqual(a['probes'][0]['value'],self.app.people['R-065']['targets'][120])
        self.assertEqual(a['result']['plan']['budget_remaining'],1)
    def test_bad_requests(self):
        for body in [{'t':True},{'t':-1},{'patient':'real-person'},{'t':120,'probes':[{'t':121,'action':'peak_flow'}]},
                     {'t':120,'probes':[{'t':100,'action':'peak_flow'},{'t':110,'action':'peak_flow'}]}]:
            with self.subTest(body=body):
                with self.assertRaises(ValueError):self.app.view(body)
    def test_patient_split_and_final_artifacts(self):
        root=Path(__file__).resolve().parents[1];d=json.loads((root/'artifacts/metrics.json').read_text())
        a,b,c=[set(d['split'][k]) for k in ['train','calibration','test']]
        self.assertFalse(a&b or b&c or a&c);self.assertEqual([len(a),len(b),len(c)],[48,16,24])
        self.assertEqual(d['models']['recap']['n'],904)
        self.assertLessEqual(d['probe_experiment']['adaptive']['max_optional_per_patient'],2)

if __name__=='__main__':unittest.main(verbosity=2)
