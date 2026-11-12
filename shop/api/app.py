# -*- coding: utf-8 -*-
"""쇼핑몰 백엔드(파이썬 기본 기능만: http.server + sqlite3). 기능은 modules/ 의 파일 하나가 묶음 하나이고, modules.json 에 이름이 있으면 붙고 없으면 떨어진다.
켜기: python shop/api/app.py [--port 8787]      붙였다 떼기: python run.py 붙여 <이름> · python run.py 떼 <이름> (서버는 다음 요청에서 저절로 다시 읽는다)
결제는 없다. 주문은 「접수」까지이고 그 뒤는 운영자가 처리한다."""
import importlib, json, os, re, sqlite3, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
CONF = os.path.join(HERE, 'modules.json')
DB = os.environ.get('SHOP_DB') or os.path.join(HERE, 'data', 'shop.db')
ADMIN_KEY = os.environ.get('SHOP_ADMIN_KEY', '')   # 시험용. 보통은 운영자가 운영자 화면에서 직접 정한 열쇠(아래 KEYFILE)를 쓴다
KEYFILE = os.path.join(os.path.dirname(DB), 'admin.local.json')   # 열쇠 그대로가 아니라 지문(sha256)만 둔다. git 에 올라가지 않는다


def key_hash(k):
    import hashlib
    return hashlib.sha256(('shop:' + k).encode('utf-8')).hexdigest()


def has_key():
    return bool(ADMIN_KEY) or os.path.exists(KEYFILE)


def key_ok(k):
    if not k:
        return False
    if ADMIN_KEY and k == ADMIN_KEY:
        return True
    try:
        return json.load(open(KEYFILE, encoding='utf-8')).get('hash') == key_hash(k)
    except Exception:
        return False
LOCK = threading.Lock()
_state = {'mtime': 0, 'routes': [], 'on': []}


def db():
    c = sqlite3.connect(DB, timeout=10); c.row_factory = sqlite3.Row
    return c


def rows(cur):
    return [dict(r) for r in cur.fetchall()]


def load():
    """modules.json 이 바뀌었으면 묶음을 다시 읽는다(서버를 껐다 켜지 않아도 붙고 떨어진다)."""
    m = os.path.getmtime(CONF)
    if m == _state['mtime']:
        return
    with LOCK:
        on = json.load(open(CONF, encoding='utf-8'))['on']; routes = []
        os.makedirs(os.path.dirname(DB), exist_ok=True); c = db()
        for name in on:
            mod = importlib.import_module('modules.' + name); importlib.reload(mod)
            if hasattr(mod, 'init'):
                mod.init(c)
            routes += [(meth, re.compile('^' + pat + '$'), fn, name) for meth, pat, fn in mod.ROUTES]
        c.commit(); c.close()
        _state.update(mtime=m, routes=routes, on=on)


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, obj):
        b = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code); self.send_header('Content-Type', 'application/json; charset=utf-8'); self.send_header('Content-Length', str(len(b)))
        self.send_header('Access-Control-Allow-Origin', self.headers.get('Origin') or '*'); self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Device, X-Admin-Key'); self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.end_headers(); self.wfile.write(b)

    def do_OPTIONS(self):
        self.send(200, {})

    def handle_any(self, meth):
        load(); u = urlparse(self.path); q = {k: v[0] for k, v in parse_qs(u.query).items()}
        body = {}
        n = int(self.headers.get('Content-Length') or 0)
        if n:
            try:
                body = json.loads(self.rfile.read(min(n, 200000)).decode('utf-8'))
            except Exception:
                return self.send(400, {'error': '보낸 내용을 읽지 못했습니다'})
        if u.path == '/api/features':
            return self.send(200, {'on': _state['on'], 'admin': has_key()})
        for m, rx, fn, name in _state['routes']:
            g = rx.match(u.path)
            if m == meth and g:
                req = dict(q=q, body=body, device=(self.headers.get('X-Device') or '')[:64], admin=key_ok(self.headers.get('X-Admin-Key') or ''), outside=bool(self.headers.get('Cf-Connecting-Ip') or self.headers.get('Cf-Ray')), args=g.groups())
                c = db()
                try:
                    out = fn(c, req); c.commit()
                except PermissionError:
                    return self.send(403, {'error': '운영자만 할 수 있습니다'})
                except ValueError as e:
                    return self.send(400, {'error': str(e)})
                finally:
                    c.close()
                return self.send(200, out)
        self.send(404, {'error': '없는 주소이거나 그 기능이 지금 떨어져 있습니다'})

    def do_GET(self):
        self.handle_any('GET')

    def do_POST(self):
        self.handle_any('POST')

    def do_PUT(self):
        self.handle_any('PUT')

    def do_DELETE(self):
        self.handle_any('DELETE')


def main():
    port = int(sys.argv[sys.argv.index('--port') + 1]) if '--port' in sys.argv else 8787
    load(); print(f'쇼핑몰 백엔드: http://127.0.0.1:{port}  붙어 있는 기능: {", ".join(_state["on"])}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', port), H).serve_forever()


if __name__ == '__main__':
    main()
