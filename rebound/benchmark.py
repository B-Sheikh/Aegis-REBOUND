"""Reproducible patient-disjoint ablations and equal-budget probe experiment."""
from pathlib import Path
import json,time
import numpy as np
from .data import patient,event,public_patient
from .recap import replay,Recap

ROOT=Path(__file__).resolve().parents[1]

def sig(x):return 1/(1+np.exp(-np.clip(x,-30,30)))

def fit_logistic(X,y):
    X=np.asarray(X);y=np.asarray(y);mu=X.mean(0);sd=np.maximum(X.std(0),.001)
    D=np.c_[np.ones(len(X)),(X-mu)/sd];w=np.zeros(D.shape[1]);reg=np.eye(len(w))*2;reg[0,0]=.01
    for _ in range(35):
        p=sig(D@w);delta=np.linalg.solve(D.T@((p*(1-p))[:,None]*D)+reg,D.T@(p-y)+reg@w);w-=delta
        if np.linalg.norm(delta)<1e-7:break
    return dict(mu=mu.tolist(),sd=sd.tolist(),w=w.tolist())

def predict(cal,X):
    X=np.atleast_2d(X);return sig(np.c_[np.ones(len(X)),(X-np.array(cal['mu']))/np.array(cal['sd'])]@np.array(cal['w']))

def baseline(e,s,t,static=True):
    h=s[max(0,t-11):t+1];v=[r for r in h if r['rr'] is not None]
    rr=np.mean([r['rr'] for r in v]) if v else e['resting_rr']
    hr=np.mean([r['hr'] for r in v]) if v else e['resting_hr']
    recent_pef=next((r['pef_lpm']/e['personal_best_lpm'] for r in reversed(s[:t+1]) if r['pef_lpm'] is not None),1)
    dyn=[rr,hr,np.mean([r['steps'] for r in h]),np.mean([r['pm25'] for r in h]),recent_pef]
    return ([e['resting_rr'],e['resting_hr'],e['prior_attacks'],e['age']]+dyn) if static else dyn

def metrics(y,p):
    y=np.asarray(y);p=np.asarray(p);pred=p>=.5
    tp=int(sum(pred&(y==1)));fp=int(sum(pred&(y==0)));fn=int(sum(~pred&(y==1)));tn=int(sum(~pred&(y==0)))
    _,inv,counts=np.unique(p,return_inverse=True,return_counts=True);end=np.cumsum(counts);ranks=(end-counts+1+end)/2
    auc=float((ranks[inv][y==1].sum()-sum(y)*(sum(y)+1)/2)/(sum(y)*(len(y)-sum(y)))) if 0<sum(y)<len(y) else None
    return dict(n=len(y),positive=int(sum(y)),auroc=auc,brier=float(np.mean((y-p)**2)),
        precision=tp/(tp+fp) if tp+fp else None,recall=tp/(tp+fn) if tp+fn else None,
        tp=tp,fp=fp,fn=fn,tn=tn)

def probe_value(p,t,action):
    rng=np.random.default_rng(90000+p['seed']*100+p['ehr']['age']+t)
    if action=='peak_flow':return p['targets'][t]
    # Independent instrument is not affected by wearable bias. It has its own noise.
    z=p['truth'][t]
    return float(p['ehr']['resting_rr']+.04*p['stream'][t]['steps']/5+7.8*z['obstruction']+z['recovery_debt']+rng.normal(0,1.2))

def sequence(p,recovery=True,personal=True,policy='none'):
    twin=Recap(p['ehr'],recovery,personal);out=[]
    for row in p['stream']:
        t=row['t'];twin.feed(row)
        if 36<=t<264 and t%6==0:
            if policy=='adaptive':
                plan=twin.measurement_plan()
                if plan['selected']!='wait':twin.observe_probe(plan['selected'],probe_value(p,t,plan['selected']))
            elif policy=='fixed' and t in [108,204]:
                twin.observe_probe('peak_flow',probe_value(p,t,'peak_flow'))
            r=twin.result(plan=False)
            if r['status']!='abstain':out.append(dict(t=t,raw=r['raw_index'],label=event(p['targets'][t+1:t+25]),
                predicted120=r['forecast'][-1]['ratio'],true120=p['targets'][t+24],
                scenario=p['scenario'],patient=p['ehr']['id']))
    return out,twin.actions

def main():
    start=time.time();(ROOT/'artifacts').mkdir(exist_ok=True);(ROOT/'data').mkdir(exist_ok=True)
    train=[patient(i) for i in range(48)];cal=[patient(i) for i in range(48,64)];test=[patient(i) for i in range(64,88)]
    X,Xd,y=[],[],[]
    for p in train:
        for t in range(36,264,6):
            if p['stream'][t]['rr'] is None:continue
            X.append(baseline(p['ehr'],p['stream'],t));Xd.append(baseline(p['ehr'],p['stream'],t,False));y.append(event(p['targets'][t+1:t+25]))
    baselines={'snapshot_fusion':fit_logistic(X,y),'wearable_only':fit_logistic(Xd,y)}
    settings={'recap':(True,True),'no_recovery_bank':(False,True),'no_ehr_personalization':(True,False)}
    calibrators={};rows={};report=dict(seed=71,scope='100% synthetic engineering experiment; no clinical validation',
       split={'train':[p['ehr']['id'] for p in train],'calibration':[p['ehr']['id'] for p in cal],'test':[p['ehr']['id'] for p in test]},
       endpoint='Three consecutive five-minute future PEF observations <80% personal best in next 120 minutes; includes ongoing low states; not a clinically adjudicated attack',
       models={},probe_experiment={},limitations=['Invented nonlinear generator; filter equations intentionally simpler but share assumptions',
           'One population seed, no external clinical validation','Window overlap; no independent-event interpretation',
           'Probe score uses hypothesis-weight updates only and holds component risk indices fixed; not exact full-state Bayesian value of information',
           'Scheduled PEF every four hours for all policies; two optional probes are additional','Uncalibrated Gaussian-mixture bands are descriptive only'])
    for name,(rec,personal) in settings.items():
        print('Filter ablation',name,flush=True)
        calibration=[r for p in cal for r in sequence(p,rec,personal)[0]]
        mapping=fit_logistic([[r['raw']] for r in calibration],[r['label'] for r in calibration]);calibrators[name]=mapping
        results=[r for p in test for r in sequence(p,rec,personal)[0]];rows[name]=results
        probs=predict(mapping,[[r['raw']] for r in results]);m=metrics([r['label'] for r in results],probs)
        m['mae120_ratio']=float(np.mean([abs(r['predicted120']-r['true120']) for r in results]))
        report['models'][name]=m
    reference=rows['recap'];lookup={(p['ehr']['id'],r['t']):(p,r['t']) for p in test for r in p['stream']}
    for name,mapping in baselines.items():
        xx=[baseline(lookup[(r['patient'],r['t'])][0]['ehr'],lookup[(r['patient'],r['t'])][0]['stream'],r['t'],name=='snapshot_fusion') for r in reference]
        report['models'][name]=metrics([r['label'] for r in reference],predict(mapping,xx))
    # Threshold comparator: raised RR after simplistic activity correction.
    threshold=[float(next(row['rr'] for row in reversed(lookup[(r['patient'],r['t'])][0]['stream'][:r['t']+1]) if row['rr'] is not None)>22) for r in reference]
    report['models']['rr_threshold22']=metrics([r['label'] for r in reference],threshold)
    patient_policy_scores={}
    for policy in ['none','fixed','adaptive']:
        print('Probe policy',policy,flush=True)
        results=[];counts=[];patient_scores=[]
        for p in test:
            rr,actions=sequence(p,policy=policy);results+=rr;counts.append(len(actions))
            pp=predict(calibrators['recap'],[[r['raw']] for r in rr])
            patient_scores.append(float(np.mean((pp-np.array([r['label'] for r in rr]))**2)))
        prob=predict(calibrators['recap'],[[r['raw']] for r in results])
        m=metrics([r['label'] for r in results],prob);m['optional_probes']=sum(counts);m['max_optional_per_patient']=max(counts)
        m['mae120_ratio']=float(np.mean([abs(r['predicted120']-r['true120']) for r in results]))
        report['probe_experiment'][policy]=m
        patient_policy_scores[policy]=patient_scores
    # Paired patient bootstrap for Brier difference, adaptive minus fixed.
    diff=np.array(patient_policy_scores['adaptive'])-np.array(patient_policy_scores['fixed']);rng=np.random.default_rng(188)
    draws=rng.integers(0,24,(1000,24));report['paired_probe_brier_difference']=dict(mean=float(diff.mean()),
        patient_bootstrap_95ci=[float(v) for v in np.quantile(diff[draws].mean(1),[.025,.975])],negative_favors='adaptive',draws=1000)
    print('Shift stress test',flush=True)
    shifted=[r for i in range(88,100) for r in sequence(patient(i,seed=93,shift=True))[0]]
    report['shift']=metrics([r['label'] for r in shifted],predict(calibrators['recap'],[[r['raw']] for r in shifted]))
    report['scenario_subgroups']={}
    for kind in ['exercise','airway','sensor','mixed']:
        rr=[r for r in reference if r['scenario']==kind]
        report['scenario_subgroups'][kind]=metrics([r['label'] for r in rr],predict(calibrators['recap'],[[r['raw']] for r in rr]))
    (ROOT/'artifacts/calibration.json').write_text(json.dumps(dict(filters=calibrators,baselines=baselines),indent=2))
    (ROOT/'artifacts/metrics.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    with (ROOT/'artifacts/test_predictions.csv').open('w') as f:
        f.write('patient,t,label,raw_index,probability,predicted120_ratio,true120_ratio,synthetic_scenario\n')
        prob=predict(calibrators['recap'],[[r['raw']] for r in reference])
        for r,p in zip(reference,prob):f.write(f"{r['patient']},{r['t']},{r['label']},{r['raw']},{p},{r['predicted120']},{r['true120']},{r['scenario']}\n")
    for p in test[:8]:
        # Public stream only. Hidden targets/truth are not bundled with patient profile.
        (ROOT/'data'/f"{p['ehr']['id']}.json").write_text(json.dumps(public_patient(p),separators=(',',':')))
    report['runtime_seconds']=round(time.time()-start,1)
    (ROOT/'artifacts/metrics.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    print(json.dumps(report['models'],indent=2));print('Probe',json.dumps(report['probe_experiment'],indent=2));print('Seconds',report['runtime_seconds'])

if __name__=='__main__':main()
