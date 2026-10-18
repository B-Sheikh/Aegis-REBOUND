"""Local synthetic-only REBOUND demo. No real patient uploads or external APIs."""
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import json,argparse,threading,webbrowser,os
from rebound.data import patient
from rebound.recap import replay
from rebound.benchmark import predict,probe_value

ROOT=Path(__file__).resolve().parent

class App:
    def __init__(self):
        self.people={f'R-{i:03d}':patient(i) for i in range(64,72)}
        self.cal=json.loads((ROOT/'artifacts/calibration.json').read_text())['filters']['recap']
        self.metrics=json.loads((ROOT/'artifacts/metrics.json').read_text())
    def view(self,body):
        pid=body.get('patient','R-065');t=body.get('t',120)
        if pid not in self.people:raise ValueError('Unknown synthetic patient')
        if type(t) is not int or not 36<=t<=263:raise ValueError('Replay index must be an integer 36..263')
        p=self.people[pid];requested=body.get('probes',[])
        if not isinstance(requested,list) or len(requested)>2:raise ValueError('At most two optional probes')
        probes=[]
        for action in requested:
            at=action.get('t');kind=action.get('action')
            if type(at) is not int or not 36<=at<=t or kind not in ['peak_flow','independent_rr']:raise ValueError('Invalid probe')
            if probes and at-probes[-1]['t']<24:raise ValueError('Probe times must increase by at least 120 minutes')
            probes.append(dict(t=at,action=kind,value=probe_value(p,at,kind)))
        twin=replay(p,t,probes=probes)
        result=twin.result(lambda x:predict(self.cal,[[x]])[0])
        out=dict(ehr=p['ehr'],history=p['stream'][max(0,t-72):t+1],t=t,result=result,
                 mode='Synthetic research sandbox; not for clinical use',probes=probes,
                 issue_time_minutes=t*5,forecast_assumption='Future activity zero; current PM2.5 held constant for two hours')
        if body.get('reveal') is True:
            out['retrospective']=[dict(minute=(i+1)*5,ratio=v) for i,v in enumerate(p['targets'][t+1:t+25])]
        return out

def handler(app):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*a):pass
        def send(self,code,value,mime='application/json'):
            data=value if isinstance(value,bytes) else json.dumps(value,allow_nan=False).encode()
            self.send_response(code);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(data)))
            self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'")
            self.end_headers();self.wfile.write(data)
        def do_GET(self):
            if self.path=='/api/patients':return self.send(200,[p['ehr'] for p in app.people.values()])
            if self.path=='/api/evidence':return self.send(200,app.metrics)
            files={'/':('index.html','text/html; charset=utf-8'),'/app.js':('app.js','application/javascript'),'/style.css':('style.css','text/css')}
            if self.path not in files:return self.send(404,{'error':'Not found'})
            file,mime=files[self.path];self.send(200,(ROOT/'web'/file).read_bytes(),mime)
        def do_POST(self):
            if self.path!='/api/view':return self.send(404,{'error':'Not found'})
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=4096:raise ValueError('Invalid request size')
                body=json.loads(self.rfile.read(length))
                if not isinstance(body,dict):raise ValueError('JSON object required')
                self.send(200,app.view(body))
            except (ValueError,TypeError,KeyError,AttributeError) as e:self.send(400,{'error':str(e)})
    return Handler

def main():
    args=argparse.ArgumentParser();args.add_argument('--host',default='127.0.0.1');args.add_argument('--port',type=int,default=int(os.environ.get('PORT','8766')));args.add_argument('--no-browser',action='store_true');a=args.parse_args()
    server=ThreadingHTTPServer((a.host,a.port),handler(App()));url=f'http://{a.host}:{a.port}'
    print('AEGIS REBOUND | Synthetic research demo | '+url,flush=True)
    if not a.no_browser:threading.Timer(.7,lambda:webbrowser.open(url)).start()
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
