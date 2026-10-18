"""RECAP: Recovery-conditioned Ensemble with Cost-Aware Probing.

Proposed engineering composition, not a proven new filtering theorem:
EHR-conditioned Kalman hypothesis bank + recovery retention variants +
quadrature expected entropy reduction for budgeted optional measurements.
"""
from math import erf,sqrt
import numpy as np

MODES=['ordinary recovery','airway deterioration','sensor drift']
CDF=np.vectorize(lambda v:.5*(1+erf(float(v)/sqrt(2))))

def entropy(w):
    w=np.clip(w,1e-12,1)
    return float(-np.sum(w*np.log(w)))

def normalize(logw):
    a=np.exp(logw-np.max(logw));return a/a.sum()

def update(x,P,H,y,R):
    H=np.atleast_2d(H);y=np.atleast_1d(y)
    S=H@P@H.T+R
    residual=y-H@x
    K=np.linalg.solve(S,H@P).T
    x=x+K@residual
    I=np.eye(4)-K@H
    P=I@P@I.T+K@R@K.T
    _,ld=np.linalg.slogdet(S)
    ll=-.5*(float(residual@np.linalg.solve(S,residual))+ld+len(y)*np.log(2*np.pi))
    return x,P,ll

class Recap:
    def __init__(self,ehr,recovery=True,personal=True):
        self.ehr=ehr;self.models=[];self.t=-1;self.last_valid=-100;self.valid=[];self.actions=[]
        rho_values=[.40,.64,.86] if recovery else [.60]
        prior=np.array([.60,.20+.035*ehr['prior_attacks'],.20]) if personal else np.ones(3)
        prior=prior/prior.sum()
        for mode in range(3):
            for rho in rho_values:
                self.models.append(dict(mode=mode,rho=rho,x=np.array([.03,0.,0.,0.]),
                    P=np.diag([.025,.00003,1.,1.]),weight=prior[mode]/len(rho_values)))
        self.personal=personal

    def transition(self,m,steps,pm):
        # x = obstruction proxy, trend, activity-recovery debt, RR sensor bias.
        mode=m['mode'];rho=m['rho']
        A=np.array([[.995,1,0,0],[0,.93,0,0],[0,0,rho,0],[0,0,0,.98 if mode==2 else .70]])
        u=np.array([max(pm-34,0)*.00019 if mode==1 else 0,0,steps/5*.028,0])
        Q=np.diag([.0003 if mode==1 else .000025,.000004 if mode==1 else .0000002,.13,.14 if mode==2 else .005])
        return A,u,Q

    def step(self,row):
        if row['t']!=self.t+1:raise ValueError('Sequential observations required')
        self.t=row['t'];present=row['rr'] is not None and row['hr'] is not None
        self.valid.append(present)
        logw=[]
        for m in self.models:
            A,u,Q=self.transition(m,row['steps'],row['pm25'])
            x=A@m['x']+u;P=A@m['P']@A.T+Q;ll=0.
            if present:
                baseline_rr=self.ehr['resting_rr'] if self.personal else 16
                baseline_hr=self.ehr['resting_hr'] if self.personal else 70
                y=[row['rr']-baseline_rr-.04*row['steps']/5,row['hr']-baseline_hr-.33*row['steps']/5]
                H=np.array([[7.5,0,1,1],[13,0,2.4,.12]])
                x,P,ll=update(x,P,H,y,np.diag([1.,5.]))
            if row.get('pef_lpm') is not None:
                y=1-row['pef_lpm']/self.ehr['personal_best_lpm']
                x,P,l=update(x,P,[.60,0,.006,0],y,np.array([[.035**2]]));ll+=l
            x[0]=np.clip(x[0],0,1.2);x[1]=np.clip(x[1],-.03,.03)
            x[2]=max(0,x[2]);x[3]=np.clip(x[3],-10,15)
            m['x']=x;m['P']=P
            # Soft forgetting prevents irrevocable collapse to an early hypothesis.
            logw.append(.96*np.log(max(m['weight'],1e-12))+.30*ll)
        # A 1% reset mixture keeps hypotheses recoverable after regime change.
        w=.99*normalize(np.array(logw))+.01/len(self.models)
        for m,v in zip(self.models,w):m['weight']=float(v)
        if present:self.last_valid=self.t

    def component_forecast(self,m):
        x=m['x'].copy();P=m['P'].copy();means=[];variances=[]
        for k in range(24):
            # Exposure persistence is an explicit scenario assumption; no future exposure is read.
            A,u,Q=self.transition(m,0,self.last_pm)
            x=A@x+u;P=A@P@A.T+Q
            h=np.array([-.60,0,-.006,0])
            means.append(float(np.clip(1+h@x,.25,1.1)))
            variances.append(float(h@P@h+.035**2))
        return np.array(means),np.array(variances)

    def risk_components(self):
        # Smooth risk index: maximum geometric mean of three marginal lows.
        # Not a correctly integrated joint crossing probability; calibrated separately.
        risks=[];forecasts=[]
        for m in self.models:
            mean,var=self.component_forecast(m)
            low=CDF((.8-mean)/np.sqrt(var))
            risk=float(np.max((low[:-2]*low[1:-1]*low[2:])**(1/3)))
            risks.append(risk);forecasts.append((mean,var))
        return np.array(risks),forecasts

    def measurement_plan(self):
        """Expected entropy reduction by deterministic Gaussian quadrature.

        Integrates possible outcomes under the current hypothesis mixture.
        Scores reduction in entropy of a latent Bernoulli risk index plus
        0.15 times hypothesis entropy, minus measurement burden.
        This does not equate to proven clinical value of information.
        """
        w=np.array([m['weight'] for m in self.models]);risk,_=self.risk_components()
        hbin=lambda p:entropy(np.array([p,1-p]))
        before=hbin(float(w@risk))+.15*entropy(w)
        nodes,weights=np.polynomial.hermite.hermgauss(9);weights=weights/np.sqrt(np.pi)
        candidates=[('peak_flow',np.array([-.60,0,-.006,0]),1.,.035,.035),
                    ('independent_rr',np.array([7.5,0,1,0]),self.ehr['resting_rr']+.04*self.last_steps/5,1.2,.018)]
        out=[]
        for name,H,offset,noise,cost in candidates:
            mu=np.array([offset+H@m['x'] for m in self.models]);var=np.array([H@m['P']@H+noise**2 for m in self.models])
            after=0.
            for i in range(len(w)):
                for node,qw in zip(nodes,weights):
                    outcome=mu[i]+np.sqrt(2*var[i])*node
                    loglike=-.5*((outcome-mu)**2/var+np.log(2*np.pi*var))
                    posterior=normalize(np.log(np.maximum(w,1e-15))+loglike)
                    after+=w[i]*qw*(hbin(float(posterior@risk))+.15*entropy(posterior))
            gain=max(0,before-after)
            out.append(dict(action=name,expected_gain_nats=round(gain,5),burden_nats=cost,net_score=round(gain-cost,5),
                            predicted_mean=round(float(w@mu),3),unit='fraction personal best' if name=='peak_flow' else 'breaths/min'))
        out.sort(key=lambda a:a['net_score'],reverse=True)
        remaining=max(0,2-len(self.actions))
        recent=bool(self.actions and self.t-self.actions[-1]['t']<24)
        selected=out[0]['action'] if remaining and not recent and out[0]['net_score']>0 else 'wait'
        return dict(selected=selected,candidates=out,budget_remaining=remaining,cooldown=recent,
                    explanation='Model-based expected information gain minus assumed burden; two optional probes/day, 120-minute cooldown. Research simulation only.')

    def observe_probe(self,action,value):
        if action not in ['peak_flow','independent_rr']:raise ValueError('Unknown probe')
        if len(self.actions)>=2:raise ValueError('Two-probe budget exhausted')
        if self.actions and self.t-self.actions[-1]['t']<24:raise ValueError('120-minute cooldown active')
        if not np.isfinite(value):raise ValueError('Finite value required')
        if action=='peak_flow' and not .25<=value<=1.2:raise ValueError('Peak-flow ratio outside supported range')
        if action=='independent_rr' and not 5<=value<=50:raise ValueError('Respiratory rate outside supported range')
        H=np.array([-.60,0,-.006,0]) if action=='peak_flow' else np.array([7.5,0,1,0])
        offset=1 if action=='peak_flow' else self.ehr['resting_rr']+.04*self.last_steps/5;noise=.035 if action=='peak_flow' else 1.2
        ll=[]
        for m in self.models:
            x,P,l=update(m['x'],m['P'],H,value-offset,np.array([[noise**2]]))
            m['x']=x;m['P']=P;ll.append(np.log(max(m['weight'],1e-12))+l)
        for m,w in zip(self.models,normalize(np.array(ll))):m['weight']=float(w)
        self.actions.append(dict(t=self.t,action=action,value=round(value,4)))

    def result(self,calibrator=None,plan=True):
        valid=sum(self.valid[-12:])/min(12,len(self.valid))
        usable=self.t>=36 and self.t-self.last_valid<=3 and valid>=.75
        if not usable:return dict(status='abstain',risk=None,forecast=[],reason='Need 3h history, recent HR/RR and at least 75% completeness in last hour',coverage=valid)
        risk,fs=self.risk_components();w=np.array([m['weight'] for m in self.models])
        mean=sum(a[0]*ww for a,ww in zip(fs,w));var=sum(ww*(a[1]+a[0]**2) for a,ww in zip(fs,w))-mean**2
        raw=float(w@risk)
        p=float(calibrator(raw)) if calibrator else raw
        modes=[float(sum(m['weight'] for m in self.models if m['mode']==i)) for i in range(3)]
        recovery=float(sum(m['weight']*m['rho'] for m in self.models))
        # Expected discrete-time debt half-life; not measured lung recovery time.
        half=float(5*np.log(.5)/np.log(recovery))
        return dict(status='review' if p>=.5 else 'observe',risk=round(p,5),raw_index=raw,coverage=valid,
            hypotheses=[dict(name=name,weight=round(v,5)) for name,v in zip(MODES,modes)],
            disagreement=round(float(w@((risk-raw)**2)),6),
            recovery_half_life_minutes=round(half,2),
            estimated_obstruction_proxy=round(float(sum(m['weight']*m['x'][0] for m in self.models)),4),
            forecast=[dict(minute=(i+1)*5,ratio=round(float(mean[i]),4),low=round(float(max(.25,mean[i]-1.645*np.sqrt(var[i]))),4),
                           high=round(float(min(1.2,mean[i]+1.645*np.sqrt(var[i]))),4)) for i in range(24)],
            plan=self.measurement_plan() if plan else None,actions=self.actions.copy(),
            caveat='Hypothesis weights and latent states are model explanations, not diagnoses; bands are uncalibrated mixture moments.')

    def feed(self,row):
        self.last_pm=row['pm25'];self.last_steps=row['steps'];self.step(row)

def replay(p,t,recovery=True,personal=True,probes=()):
    twin=Recap(p['ehr'],recovery,personal)
    for row in p['stream'][:t+1]:
        twin.feed(row)
        for action in probes:
            if action['t']==row['t']:twin.observe_probe(action['action'],action['value'])
    return twin
