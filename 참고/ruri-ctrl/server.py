
import json,queue,threading,sys
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
TOK=open(__file__.replace('server.py','token.txt')).read().strip()
Q=queue.Queue();R={};EV={};ID=[0];LOCK=threading.Lock();GEN=[0]
class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def _j(self,o,code=200):
        b=json.dumps(o).encode();self.send_response(code);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b)
    def _auth(self):
        if self.headers.get('X-Tok')!=TOK: self._j({'error':'auth'},403); return False
        return True
    def do_GET(self):
        if not self._auth(): return
        if self.path.startswith('/poll'):
            with LOCK: GEN[0]+=1; me=GEN[0]
            import time
            end=time.time()+20; c=None
            while time.time()<end and GEN[0]==me:
                try: c=Q.get(timeout=0.5); break
                except queue.Empty: pass
            try: self._j(c or {})
            except Exception:
                if c: Q.put(c)
        else: self._j({'ok':1})
    def do_POST(self):
        if not self._auth(): return
        n=int(self.headers.get('Content-Length',0)); d=json.loads(self.rfile.read(n) or b'{}')
        if self.path=='/cmd':
            with LOCK: ID[0]+=1; i=ID[0]
            d['id']=i; EV[i]=threading.Event(); Q.put(d)
            EV[i].wait(d.get('timeout',90)); self._j(R.pop(i,{'error':'timeout (extension not connected?)'}))
        elif self.path=='/result':
            R[d['id']]=d; EV[d['id']].set(); self._j({})
ThreadingHTTPServer(('127.0.0.1',8765),H).serve_forever()
