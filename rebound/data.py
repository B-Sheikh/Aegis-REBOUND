"""Independent nonlinear toy world. Exports only observations to inference.

No clinical validity. Hidden simulator states are available to scoring only.
Five-minute samples; primary endpoint uses future observed peak-flow probes.
"""
import numpy as np

def patient(index, seed=71, shift=False):
    rng=np.random.default_rng(seed*100003+index)
    n=288
    attacks=int(rng.integers(0,5)); rr0=round(float(rng.uniform(13,19)),1)
    hr0=round(float(rng.uniform(58,83)),1); personal_best=int(rng.integers(350,620))
    ehr=dict(id=f"R-{index:03d}",age=int(rng.integers(22,66)),asthma_years=int(rng.integers(2,22)),
             prior_attacks=attacks,personal_best_lpm=personal_best,resting_rr=rr0,resting_hr=hr0,
             diagnosis="Asthma (synthetic)",source="Invented EHR and sensors; no real person")
    # Latent scenario labels never become inputs. Every scenario contains walking.
    kind=index%4
    activity=np.zeros(n);pm=np.maximum(5,rng.normal(22,4,n))
    for start in [36,92,144,208,248]:
        width=int(rng.integers(3,7));activity[start:start+width]=rng.uniform(35,95)
    if kind in [1,3]:pm[95:165]+=rng.uniform(35,90)
    if kind==0:pm[95:130]+=20
    inflammation=.015;debt=0.;bias=0.;truth=[];stream=[];target=[]
    gain=rng.uniform(.006,.012)*(1+attacks*.07)
    retention=rng.uniform(.36,.65)
    if shift:retention=.85;gain*=.6
    for t in range(n):
        # Nonlinear latent obstruction is not the filter's linear transition.
        drive=max(pm[t]-34,0)*gain*(1 if kind in [1,3] else .06)
        inflammation=np.clip(.985*inflammation+drive*.09+.004*np.sin(t/13)+rng.normal(0,.003),0,.98)
        if kind==3 and t>160:inflammation+=.002
        debt=(retention+.24*inflammation)*debt+activity[t]*.028
        if kind==2 and 100<=t<=175:bias=min(7,bias+.22)
        else:bias*=.94
        ratio=np.clip(1-.60*inflammation**1.1-.006*debt, .35,1.08)
        independent_pef=float(np.clip(ratio+rng.normal(0,.025 if not shift else .05),.3,1.1))
        rr=rr0+.040*activity[t]+debt+7.8*inflammation+bias+rng.normal(0,.6)
        hr=hr0+.33*activity[t]+2.4*debt+13*inflammation+.12*bias+rng.normal(0,1.8)
        if shift:rr+=2*np.sin(t/19)
        # Periodic measured PEF is sparse. Held-out optional measurements are not preloaded in UI.
        pef=round(independent_pef*personal_best,1) if t%48==0 else None
        missing=168<=t<=177 and index%6==0
        stream.append(dict(t=t,minute=t*5,rr=None if missing else round(float(rr),2),
            hr=None if missing else round(float(hr),2),steps=int(activity[t]*5),pm25=round(float(pm[t]),1),pef_lpm=pef))
        target.append(round(independent_pef,5))
        truth.append(dict(obstruction=round(float(inflammation),4),recovery_debt=round(float(debt),4),sensor_bias=round(float(bias),4)))
    return dict(ehr=ehr,stream=stream,targets=target,truth=truth,scenario=['exercise','airway','sensor','mixed'][kind],seed=seed)

def public_patient(p):return dict(ehr=p['ehr'],stream=p['stream'])

def event(values):
    low=np.asarray(values)<.8
    return int(np.any(low[:-2]&low[1:-1]&low[2:]))
