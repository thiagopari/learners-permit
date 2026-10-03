"""Warehouse fleet service: runs the sim, serves telemetry + layout, handles demo faults
and bandit commissioning. Stdlib http.server so it runs anywhere on the box (no pip)."""
import json, threading, time, random
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from math import comb
import sim

WH = sim.Warehouse(n=20)
LOCK = threading.Lock()
TICK_HZ = 8

def loop():
    dt = 1.0/TICK_HZ
    while True:
        with LOCK: WH.tick()
        time.sleep(dt)
threading.Thread(target=loop, daemon=True).start()

# ---- bandit commissioning (verified math) ----
def p_at_least(s,f,thr=0.8):
    n=s+f+1
    return sum(comb(n,k)*thr**k*(1-thr)**(n-k) for k in range(s+1))

def commission(rates, thr=0.8, conf=0.95, batch=4, cap=40, rng=random):
    """Thompson-sampling bandit over candidate routes/robots (the verified algorithm).
    rates: {arm: true_success_rate}. Returns the winning arm + per-batch log for the dashboard."""
    arms=list(rates); s=dict.fromkeys(arms,0); f=dict.fromkeys(arms,0); log=[]
    while sum(s.values())+sum(f.values())<cap:
        picks=[max(arms,key=lambda a: rng.betavariate(1+s[a],1+f[a])) for _ in range(batch)]
        for a in picks:
            if rng.random()<rates[a]: s[a]+=1
            else: f[a]+=1
        best=max(arms,key=lambda a: p_at_least(s[a],f[a],thr)); pb=p_at_least(s[best],f[best],thr)
        log.append({"best":best,"s":s[best],"n":s[best]+f[best],"p":round(pb,3),
                    "counts":{a:f"{s[a]}/{s[a]+f[a]}" for a in arms}})
        if pb>=conf: return {"decision":"pass","policy":best,"trials":sum(s.values())+sum(f.values()),"log":log}
        if all(p_at_least(s[a],f[a],thr)<=1-conf for a in arms):
            return {"decision":"fail","trials":sum(s.values())+sum(f.values()),"log":log}
    return {"decision":"inconclusive","trials":sum(s.values())+sum(f.values()),"log":log}

class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        b = body if isinstance(body,bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type",ctype)
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Content-Length",str(len(b)))
        self.end_headers(); self.wfile.write(b)
    def log_message(self,*a): pass
    def do_GET(self):
        u=urlparse(self.path); q=parse_qs(u.query)
        if u.path=="/" or u.path=="/index.html":
            try: self._send(200, open("static/index.html","rb").read(), "text/html")
            except FileNotFoundError: self._send(404,{"err":"no index"})
        elif u.path=="/api/layout":
            with LOCK: self._send(200, WH.layout())
        elif u.path=="/api/telemetry":
            with LOCK: self._send(200, WH.telemetry())
        elif u.path=="/api/inventory":
            with LOCK: self._send(200, WH.inventory())
        elif u.path=="/api/commission":
            # demo: current (untrusted) route ~5%, proposed route ~95%
            prop=float(q.get("rate",["0.95"])[0])
            self._send(200, commission({"current_route":0.05,"proposed_route":prop}))
        else: self._send(404,{"err":"not found"})
    def do_POST(self):
        u=urlparse(self.path)
        n=int(self.headers.get("Content-Length",0)); body=json.loads(self.rfile.read(n) or b"{}")
        if u.path=="/api/inject":
            with LOCK: WH.inject[int(body["robot"])]=body.get("fault","stuck")
            self._send(200,{"ok":True})
        elif u.path=="/api/clear":
            with LOCK: WH.inject.clear()
            self._send(200,{"ok":True})
        elif u.path=="/api/shrink":
            with LOCK: n=WH.shrink(int(body.get("zone",0)), int(body.get("units",6)))
            self._send(200,{"ok":True,"units_removed":n})
        else: self._send(404,{"err":"not found"})

if __name__=="__main__":
    ThreadingHTTPServer(("0.0.0.0",3000), H).serve_forever()
