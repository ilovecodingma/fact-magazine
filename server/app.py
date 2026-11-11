# -*- coding: utf-8 -*-
"""독자 PC 에서 도는 작은 백엔드(도커 컨테이너 안): 찍어 둔 사이트 제공 + API(댓글·좋아요·방문 통계·문의·소식 받기·투표·저장) + 운영자 화면(/admin/).
자료는 모두 JSON 문서 한 건씩 `docs(collection, id, data, created, updated)` 에 쌓인다 — 도커 안에서는 PostgreSQL(JSONB, DATABASE_URL), 그 밖에서는 같은 모양의 파일(sqlite, 개발·시험용).
서버 코드는 파이썬 기본 기능 + (PostgreSQL 일 때만) 컨테이너 안에 깔리는 pg8000. 서버가 꺼져 있어도 찍어 둔 화면은 파일로 그대로 열린다."""
import argparse, hashlib, hmac, html, http.server, json, os, re, secrets, socketserver, sqlite3, sys, threading, time, urllib.parse

P = argparse.ArgumentParser()
P.add_argument('--site', default=os.environ.get('SITE_DIR', '/site'))
P.add_argument('--data', default=os.environ.get('DATA_DIR', '/data'))
P.add_argument('--host', default=os.environ.get('HOST', '127.0.0.1'))
P.add_argument('--port', type=int, default=int(os.environ.get('PORT', '8080')))
P.add_argument('--dump', default='', help='모음 이름을 주면 그 모음의 JSON 문서를 출력하고 끝낸다')
ARGS = P.parse_args()
SITE = os.path.abspath(ARGS.site); DATA = os.path.abspath(ARGS.data); os.makedirs(DATA, exist_ok=True)
ADMIN = os.path.join(DATA, 'admin.json'); SECRET_P = os.path.join(DATA, '.secret')
if not os.path.exists(SECRET_P):
    open(SECRET_P, 'w').write(secrets.token_hex(16))
SECRET = open(SECRET_P).read().strip()
LOCK = threading.RLock()
SESS = {}
RATE = {}
BOT = re.compile(r'bot|crawl|spider|slurp|curl|wget|python-requests|monitor|preview', re.I)


# ------------------------------------------------------------------ 문서 저장소(두 가지 바탕, 같은 모양)
class Store:
    """docs(collection, id, data JSON, created, updated). put·get·find·count·update 만 쓴다."""

    def now(self):
        return time.strftime('%Y-%m-%d %H:%M:%S')


class FileStore(Store):
    def __init__(self, path):
        self.path = path
        with self.c() as c:
            c.execute('CREATE TABLE IF NOT EXISTS docs(collection TEXT, id TEXT, data TEXT, created TEXT, updated TEXT, PRIMARY KEY(collection, id))')

    def c(self):
        return sqlite3.connect(self.path, timeout=10)

    def put(self, col, id_, data):
        n = self.now()
        with LOCK, self.c() as c:
            c.execute('INSERT INTO docs VALUES(?,?,?,?,?) ON CONFLICT(collection,id) DO UPDATE SET data=excluded.data, updated=excluded.updated', (col, id_, json.dumps(data, ensure_ascii=False), n, n))

    def get(self, col, id_):
        with LOCK, self.c() as c:
            r = c.execute('SELECT data FROM docs WHERE collection=? AND id=?', (col, id_)).fetchone()
        return json.loads(r[0]) if r else None

    def update(self, col, id_, patch):
        d = self.get(col, id_)
        if d is None:
            return False
        d.update(patch); n = self.now()
        with LOCK, self.c() as c:
            c.execute('UPDATE docs SET data=?, updated=? WHERE collection=? AND id=?', (json.dumps(d, ensure_ascii=False), n, col, id_))
        return True

    def find(self, col, where=None, limit=50, order='desc'):
        with LOCK, self.c() as c:
            rows = c.execute('SELECT id, data, created FROM docs WHERE collection=? ORDER BY created ' + ('DESC' if order == 'desc' else 'ASC') + ', rowid DESC', (col,)).fetchall()
        out = []
        for id_, data, created in rows:
            d = json.loads(data)
            if all(d.get(k) == v for k, v in (where or {}).items()):
                d['_id'] = id_; d['_created'] = created; out.append(d)
                if len(out) >= limit:
                    break
        return out

    def count(self, col, where=None):
        return len(self.find(col, where, limit=10 ** 9))


class PgStore(Store):
    """PostgreSQL(JSONB). 컨테이너 안에서만 쓰며 드라이버(pg8000)는 이미지를 만들 때 그 안에 깔린다."""

    def __init__(self, url):
        import pg8000.dbapi as pg
        u = urllib.parse.urlparse(url)
        self.kw = dict(user=urllib.parse.unquote(u.username or ''), password=urllib.parse.unquote(u.password or ''), host=u.hostname, port=u.port or 5432, database=(u.path or '/').lstrip('/'))
        self.pg = pg
        for _ in range(40):   # db 컨테이너가 뜰 때까지 기다린다
            try:
                self.run('CREATE TABLE IF NOT EXISTS docs(collection TEXT, id TEXT, data JSONB, created TIMESTAMP DEFAULT now(), updated TIMESTAMP DEFAULT now(), PRIMARY KEY(collection, id))'); break
            except Exception:
                time.sleep(1.5)

    def run(self, sql, args=(), fetch=False):
        c = self.pg.connect(**self.kw)
        try:
            cur = c.cursor(); cur.execute(sql, args); rows = cur.fetchall() if fetch else None; c.commit(); return rows
        finally:
            c.close()

    def put(self, col, id_, data):
        self.run('INSERT INTO docs(collection,id,data) VALUES(%s,%s,%s::jsonb) ON CONFLICT(collection,id) DO UPDATE SET data=EXCLUDED.data, updated=now()', (col, id_, json.dumps(data, ensure_ascii=False)))

    def get(self, col, id_):
        r = self.run('SELECT data FROM docs WHERE collection=%s AND id=%s', (col, id_), True)
        return (json.loads(r[0][0]) if isinstance(r[0][0], str) else r[0][0]) if r else None

    def update(self, col, id_, patch):
        self.run("UPDATE docs SET data=data || %s::jsonb, updated=now() WHERE collection=%s AND id=%s", (json.dumps(patch, ensure_ascii=False), col, id_))
        return True

    def find(self, col, where=None, limit=50, order='desc'):
        rows = self.run('SELECT id, data, created FROM docs WHERE collection=%s AND data @> %s::jsonb ORDER BY created ' + ('DESC' if order == 'desc' else 'ASC') + ' LIMIT %s', (col, json.dumps(where or {}), limit), True)
        out = []
        for id_, data, created in rows:
            d = json.loads(data) if isinstance(data, str) else dict(data); d['_id'] = id_; d['_created'] = str(created); out.append(d)
        return out

    def count(self, col, where=None):
        return self.run('SELECT COUNT(*) FROM docs WHERE collection=%s AND data @> %s::jsonb', (col, json.dumps(where or {})), True)[0][0]


STORE = None


def store():
    global STORE
    if STORE is None:
        url = os.environ.get('DATABASE_URL', '')
        STORE = PgStore(url) if url.startswith('postgres') else FileStore(os.path.join(DATA, 'app.db'))
    return STORE


def esc(s):
    return html.escape(str(s), quote=True)


def clean(s, n):
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', str(s or '')).strip()[:n]


def iphash(ip):
    return hashlib.sha256((SECRET + ip).encode()).hexdigest()[:16]


def newid():
    return f'{int(time.time() * 1000)}-{secrets.token_hex(3)}'


def limited(ip, group, per=10, sec=60):
    now = time.time(); k = (ip, group); L = [t for t in RATE.get(k, []) if now - t < sec]
    if len(L) >= per:
        RATE[k] = L; return True
    L.append(now); RATE[k] = L; return False


def board_cfg():
    """게시판 손잡이(순위 셈법·한 쪽 줄 수·공개 방식): 사이트를 찍을 때 build 가 써 둔 board.json 을 읽는다."""
    try:
        return json.load(open(os.path.join(SITE, 'board.json'), encoding='utf-8'))
    except Exception:
        return {'gravity': 1.8, 'per_page': 30, 'moderation': 'before'}


def hours_since(created):
    try:
        return max(0.0, (time.time() - time.mktime(time.strptime(str(created)[:19], '%Y-%m-%d %H:%M:%S'))) / 3600)
    except Exception:
        return 0.0


def post_view(S, p):
    return {'id': p['_id'], 'title': p['title'], 'url': p.get('url', ''), 'text': p.get('text', ''), 'name': p.get('name', '익명'), 'kind': p.get('kind', 'all'), 'points': p.get('points', 1),
            'hours': round(hours_since(p['_created']), 2), 'comments': S.count('pcomments', {'pid': p['_id'], 'status': 'approved'})}


def check_pw(pw):
    if not os.path.exists(ADMIN):
        return False
    a = json.load(open(ADMIN, encoding='utf-8'))
    h = hashlib.pbkdf2_hmac('sha256', pw.encode(), bytes.fromhex(a['salt']), a['iters']).hex()
    return hmac.compare_digest(h, a['hash'])


ADMIN_HTML = '''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>운영자 화면</title>
<style>:root{--ink:#0f172a;--mu:#475569;--pri:#1e3a8a;--hair:#d9e0ee}*{box-sizing:border-box}body{margin:0;background:#f6f8fc;color:var(--ink);font:16px/1.6 system-ui,"Malgun Gothic",sans-serif}main{max-width:900px;margin:0 auto;padding:16px}
h1{font-size:22px;margin:8px 0 14px}h2{font-size:15px;margin:22px 0 8px;color:var(--pri)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}.box{background:#fff;border:1px solid var(--hair);border-radius:10px;padding:12px 14px}.box b{display:block;font-size:28px;line-height:1.2}.box span{color:var(--mu);font-size:14px}
table{width:100%;border-collapse:collapse;background:#fff;border:1px solid var(--hair);border-radius:10px;overflow:hidden}td,th{padding:8px 10px;border-bottom:1px solid var(--hair);text-align:left;font-size:15px;vertical-align:top}button{font:700 14px system-ui;padding:8px 12px;border:1px solid var(--pri);background:#fff;color:var(--pri);border-radius:6px;cursor:pointer}button.p{background:var(--pri);color:#fff}
input{font:16px system-ui;padding:10px;border:1px solid var(--hair);border-radius:6px;width:100%;max-width:320px}.mu{color:var(--mu);font-size:14px}.tbl{overflow-x:auto}pre{background:#fff;border:1px solid var(--hair);border-radius:8px;padding:10px;overflow:auto;font-size:13px}</style></head><body><main>
<h1>운영자 화면</h1><div id="app"><p class="mu">불러오는 중…</p></div></main>
<script>(function(){var A=document.getElementById("app");function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})}
function api(p,o){o=o||{};o.credentials="same-origin";return fetch(p,o).then(function(r){return r.json().then(function(j){j._s=r.status;return j})})}
function login(msg){A.innerHTML='<p>운영자 암호를 입력하세요.</p><p><input id="pw" type="password" autocomplete="current-password" placeholder="암호"></p><p><button class="p" id="go">들어가기</button> <span class="mu">'+esc(msg||"")+'</span></p>';
 document.getElementById("go").onclick=function(){api("/api/admin/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({password:document.getElementById("pw").value})}).then(function(j){if(j.ok)load();else login(j.error||"안 됩니다")})};
 document.getElementById("pw").onkeydown=function(e){if(e.key==="Enter")document.getElementById("go").click()}}
function act(kind,id,a){api("/api/admin/"+kind,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({id:id,action:a})}).then(load)}
function load(){api("/api/admin/summary").then(function(j){if(j._s===401)return login();if(j.error&&!j.today&&j.today!==0)return A.innerHTML='<p>'+esc(j.error)+'</p>';
 var h='<div class="grid"><div class="box"><b>'+j.today+'</b><span>오늘 방문</span></div><div class="box"><b>'+j.week+'</b><span>7일 방문</span></div><div class="box"><b>'+j.pending+'</b><span>승인 기다리는 댓글</span></div><div class="box"><b>'+j.contacts+'</b><span>새 문의</span></div><div class="box"><b>'+j.subscribers+'</b><span>소식 받기 신청</span></div><div class="box"><b>'+j.likes+'</b><span>좋아요</span></div></div>';
 h+='<h2>인기 쪽(7일)</h2><div class="tbl"><table>'+j.popular.map(function(r){return '<tr><td>'+esc(r.path)+'</td><td>'+r.n+'</td></tr>'}).join("")+'</table></div>';
 h+='<h2>새 댓글</h2><div class="tbl"><table>'+(j.comments.map(function(c){return '<tr><td><b>'+esc(c.name)+'</b> <span class="mu">'+esc(c.slug)+' · '+esc(c.status)+'</span><br>'+esc(c.body)+'</td><td><button class="p" onclick="window.__a(\\'comment\\',\\''+esc(c._id)+'\\',\\'approve\\')">승인</button> <button onclick="window.__a(\\'comment\\',\\''+esc(c._id)+'\\',\\'hide\\')">숨김</button></td></tr>'}).join("")||'<tr><td class="mu">없음</td></tr>')+'</table></div>';
 h+='<h2>문의</h2><div class="tbl"><table>'+(j.contact_list.map(function(c){return '<tr><td><b>'+esc(c.name)+'</b> <span class="mu">'+esc(c.email)+' · '+esc(c._created)+'</span><br>'+esc(c.message)+'</td><td><button onclick="window.__a(\\'contact\\',\\''+esc(c._id)+'\\',\\'hide\\')">숨김</button></td></tr>'}).join("")||'<tr><td class="mu">없음</td></tr>')+'</table></div>';
 h+='<h2>게시판 — 승인 기다리는 글·댓글 (신고 '+(j.flags||0)+'건)</h2><div class="tbl"><table>'+((j.board||[]).map(function(c){return '<tr><td><b>['+esc(c.what)+']</b> '+esc(c.title)+' <span class="mu">'+esc(c.name)+'</span></td><td><button class="p" onclick="window.__b(\\''+esc(c._id)+'\\',\\''+esc(c.what)+'\\',\\'approve\\')">승인</button> <button onclick="window.__b(\\''+esc(c._id)+'\\',\\''+esc(c.what)+'\\',\\'hide\\')">숨김</button></td></tr>'}).join("")||'<tr><td class="mu">없음</td></tr>')+'</table></div>';
 h+='<h2>하루 한 바퀴 기록 · 올릴 묶음</h2><div class="box"><div class="mu">'+esc(j.daily||"기록 없음")+'</div><div style="margin-top:8px">'+j.bundles.map(function(b){return esc(b.name)+' '+b.n+'개'}).join(" · ")+'</div></div>';
 h+='<h2>자료(JSON 문서)</h2><p class="mu">방문자가 쌓은 것은 모두 JSON 문서 한 건씩입니다. 모음: '+j.collections.map(esc).join(", ")+'</p><p><button onclick="window.__docs()">댓글 문서 보기</button></p><pre id="docs"></pre>';
 h+='<p><button onclick="window.__out()">나가기</button></p>';A.innerHTML=h})}
window.__a=act;window.__b=function(id,what,a){api("/api/admin/board",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({id:id,what:what,action:a})}).then(load)};window.__docs=function(){api("/api/admin/docs?collection=comments").then(function(j){document.getElementById("docs").textContent=JSON.stringify(j.docs||j,null,1)})};
window.__out=function(){api("/api/admin/logout",{method:"POST"}).then(function(){login()})};load()})()</script></body></html>'''

COLLECTIONS = ['visits', 'comments', 'likes', 'contacts', 'subscribers', 'poll_votes', 'kv', 'posts', 'post_votes', 'pcomments', 'flags']


class H(http.server.SimpleHTTPRequestHandler):
    server_version = 'FactMagazine'

    def __init__(self, *a, **k):
        super().__init__(*a, directory=SITE, **k)

    def log_message(self, *a):
        pass

    def ip(self):
        return self.client_address[0]

    def send_json(self, obj, code=200, extra=None):
        b = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code); self.send_header('Content-Type', 'application/json; charset=utf-8'); self.send_header('Content-Length', str(len(b))); self.send_header('Cache-Control', 'no-store'); self.send_header('X-Content-Type-Options', 'nosniff')
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers(); self.wfile.write(b)

    def body(self):
        n = int(self.headers.get('Content-Length') or 0)
        if n > 8192:
            return None
        try:
            return json.loads(self.rfile.read(n).decode('utf-8') or '{}')
        except Exception:
            return None

    def authed(self):
        m = re.search(r'adm=([A-Za-z0-9]+)', self.headers.get('Cookie') or '')
        return bool(m and SESS.get(m.group(1), 0) > time.time())

    def send_error(self, code, message=None, explain=None):
        p = os.path.join(SITE, '404.html')
        if code == 404 and os.path.exists(p) and not self.path.startswith('/api/'):
            b = open(p, 'rb').read(); self.send_response(404); self.send_header('Content-Type', 'text/html; charset=utf-8'); self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)
        else:
            super().send_error(code, message, explain)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query)
        if u.path in ('/admin', '/admin/'):
            b = ADMIN_HTML.encode('utf-8'); self.send_response(200); self.send_header('Content-Type', 'text/html; charset=utf-8'); self.send_header('Content-Length', str(len(b))); self.send_header('X-Robots-Tag', 'noindex'); self.end_headers(); self.wfile.write(b); return
        if u.path.startswith('/api/'):
            try:
                return self.api_get(u.path, q)
            except Exception as e:
                return self.send_json({'error': '서버 안에서 오류가 났습니다: ' + type(e).__name__}, 500)
        return super().do_GET()

    def api_get(self, path, q):
        S = store()
        if path == '/api/health':
            return self.send_json({'ok': True, 'time': time.strftime('%Y-%m-%d %H:%M:%S'), 'db': 'postgres' if isinstance(S, PgStore) else 'file', 'features': ['visit', 'comments', 'likes', 'contact', 'subscribe', 'poll', 'kv', 'search', 'board']})
        if path == '/api/comments':
            slug = clean(q.get('slug', [''])[0], 120)
            rows = S.find('comments', {'slug': slug, 'status': 'approved'}, 50)
            return self.send_json({'ok': True, 'comments': [{'name': r['name'], 'body': r['body'], 'created': r['_created']} for r in rows]})
        if path == '/api/likes':
            return self.send_json({'ok': True, 'likes': S.count('likes', {'slug': clean(q.get('slug', [''])[0], 120)})})
        if path == '/api/poll':
            poll = clean(q.get('id', [''])[0], 60); res = {}
            for r in S.find('poll_votes', {'poll': poll}, 10000):
                res[r['opt']] = res.get(r['opt'], 0) + 1
            return self.send_json({'ok': True, 'results': res})
        if path == '/api/search':
            qq = clean(q.get('q', [''])[0], 60).lower(); hits = []
            sp = os.path.join(SITE, 'search.json')
            if qq and os.path.exists(sp):
                for it in json.load(open(sp, encoding='utf-8')):
                    try:
                        u_, t, d = it[1][0], it[1][1], (it[1][2] if len(it[1]) > 2 else '')
                    except Exception:
                        continue
                    if qq in (t + ' ' + d).lower():
                        hits.append({'url': u_, 'title': t})
            return self.send_json({'ok': True, 'hits': hits[:20]})
        if path == '/api/kv':
            r = S.get('kv', clean(q.get('k', [''])[0], 80))
            return self.send_json({'ok': True, 'v': (r or {}).get('v')})
        if path == '/api/board':
            cfg = board_cfg(); kind = clean(q.get('kind', ['all'])[0], 10); sort = clean(q.get('sort', ['top'])[0], 10)
            try:
                pg = max(1, int(q.get('page', ['1'])[0]))
            except ValueError:
                pg = 1
            L = [post_view(S, p) for p in S.find('posts', {'status': 'approved'}, 500)]
            if kind in ('ask', 'show'):
                L = [p for p in L if p['kind'] == kind]
            if sort == 'new':
                L.sort(key=lambda p: p['hours'])
            else:   # 점수를 지난 시간의 거듭제곱으로 나눈다 — 시간이 지나면 저절로 내려간다
                L.sort(key=lambda p: -(p['points'] / ((p['hours'] + 2) ** float(cfg.get('gravity', 1.8)))))
            n = int(cfg.get('per_page', 30))
            return self.send_json({'ok': True, 'posts': L[(pg - 1) * n: pg * n], 'more': len(L) > pg * n})
        if path == '/api/board/item':
            pid = clean(q.get('id', [''])[0], 60); p = S.get('posts', pid)
            if not p or p.get('status') != 'approved':
                return self.send_json({'ok': False, 'error': '없는 글'}, 404)
            p['_id'] = pid; p['_created'] = p.get('created') or ''
            full = next((x for x in S.find('posts', {'status': 'approved'}, 500) if x['_id'] == pid), None)
            cs = [{'id': c['_id'], 'parent': c.get('parent', ''), 'name': c.get('name', '익명'), 'body': c['body'], 'hours': round(hours_since(c['_created']), 2)} for c in S.find('pcomments', {'pid': pid, 'status': 'approved'}, 500, 'asc')]
            return self.send_json({'ok': True, 'post': post_view(S, full) if full else None, 'comments': cs})
        if path == '/api/admin/summary':
            if not self.authed():
                return self.send_json({'error': '로그인이 필요합니다'}, 401)
            return self.send_json(self.summary())
        if path == '/api/admin/docs':
            if not self.authed():
                return self.send_json({'error': '로그인이 필요합니다'}, 401)
            col = clean(q.get('collection', [''])[0], 40)
            if col not in COLLECTIONS:
                return self.send_json({'error': '없는 모음'}, 404)
            return self.send_json({'ok': True, 'docs': S.find(col, None, 50)})
        return self.send_json({'error': '없는 API'}, 404)

    def summary(self):
        S = store(); day = time.strftime('%Y-%m-%d')
        days = [time.strftime('%Y-%m-%d', time.localtime(time.time() - i * 86400)) for i in range(7)]
        pages = {}
        week = today = 0
        for d in days:
            for r in S.find('visits', {'day': d}, 10000):
                week += r['n']; today += r['n'] if d == day else 0; pages[r['path']] = pages.get(r['path'], 0) + r['n']
        out = {'today': today, 'week': week, 'pending': S.count('comments', {'status': 'pending'}), 'contacts': S.count('contacts', {'status': 'new'}), 'subscribers': S.count('subscribers', {'status': 'on'}), 'likes': S.count('likes'),
               'popular': [{'path': p, 'n': n} for p, n in sorted(pages.items(), key=lambda x: -x[1])[:8]],
               'comments': [{k: r.get(k) for k in ('_id', 'slug', 'name', 'body', 'status')} for r in S.find('comments', None, 40) if r.get('status') != 'hidden'][:15],
               'contact_list': [{k: r.get(k) for k in ('_id', 'name', 'email', 'message', '_created')} for r in S.find('contacts', {'status': 'new'}, 15)],
               'board': [{'_id': r['_id'], 'what': '글', 'title': r['title'], 'name': r.get('name', ''), 'status': r.get('status')} for r in S.find('posts', {'status': 'pending'}, 20)]
                        + [{'_id': r['_id'], 'what': '댓글', 'title': r['body'][:80], 'name': r.get('name', ''), 'status': r.get('status')} for r in S.find('pcomments', {'status': 'pending'}, 20)],
               'flags': S.count('flags'),
               'collections': COLLECTIONS}
        lf = os.path.join(DATA, 'logs', 'daily.md')
        out['daily'] = ''.join(open(lf, encoding='utf-8').readlines()[-2:]).strip() if os.path.exists(lf) else ''
        out['bundles'] = []
        for nm in ('promo_out', 'cards', 'shorts'):
            d = os.path.join(DATA, 'share', nm)
            out['bundles'].append({'name': nm, 'n': len(os.listdir(d)) if os.path.isdir(d) else 0})
        return out

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        if not u.path.startswith('/api/'):
            return self.send_json({'error': '없는 주소'}, 404)
        try:
            return self.api_post(u.path)
        except Exception as e:
            return self.send_json({'error': '서버 안에서 오류가 났습니다: ' + type(e).__name__}, 500)

    def api_post(self, path):
        S = store(); ip = self.ip(); b = self.body()
        if b is None:
            return self.send_json({'error': '요청이 너무 크거나 형식이 맞지 않습니다'}, 400)
        now = time.strftime('%Y-%m-%d %H:%M:%S'); day = time.strftime('%Y-%m-%d')
        if path == '/api/visit':
            if BOT.search(self.headers.get('User-Agent') or ''):
                return self.send_json({'ok': True, 'counted': False})
            p = re.sub(r'[?#].*$', '', clean(b.get('path'), 200))
            if not p.startswith('/') or limited(ip, 'visit', 60, 60):
                return self.send_json({'ok': True, 'counted': False})
            with LOCK:
                id_ = f'{day}|{p}'; d = S.get('visits', id_) or {'day': day, 'path': p, 'n': 0}
                d['n'] += 1; S.put('visits', id_, d)
            return self.send_json({'ok': True, 'counted': True})
        if path == '/api/admin/login':
            if limited(ip, 'login', 5, 60):
                return self.send_json({'error': '로그인 시도가 너무 잦습니다. 1분 뒤에 다시 해 주세요'}, 429)
            if not os.path.exists(ADMIN):
                return self.send_json({'error': '운영자 암호가 아직 없습니다. python run.py 서버 암호 로 먼저 정하세요'}, 403)
            if not check_pw(str(b.get('password', ''))):
                return self.send_json({'error': '암호가 맞지 않습니다'}, 401)
            tok = secrets.token_hex(20); SESS[tok] = time.time() + 8 * 3600
            return self.send_json({'ok': True}, 200, {'Set-Cookie': f'adm={tok}; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800'})
        if path.startswith('/api/admin/'):
            if not self.authed():
                return self.send_json({'error': '로그인이 필요합니다'}, 401)
            if path == '/api/admin/logout':
                m = re.search(r'adm=([A-Za-z0-9]+)', self.headers.get('Cookie') or '')
                if m:
                    SESS.pop(m.group(1), None)
                return self.send_json({'ok': True})
            if path == '/api/admin/comment':
                st = {'approve': 'approved', 'hide': 'hidden'}.get(str(b.get('action')))
                if not st or not b.get('id'):
                    return self.send_json({'error': '잘못된 요청'}, 400)
                S.update('comments', str(b['id']), {'status': st})   # 지우지 않고 숨김 처리
                return self.send_json({'ok': True})
            if path == '/api/admin/board':
                st = {'approve': 'approved', 'hide': 'hidden'}.get(str(b.get('action')))
                if not st or not b.get('id'):
                    return self.send_json({'error': '잘못된 요청'}, 400)
                col = 'pcomments' if b.get('what') == '댓글' or S.get('pcomments', str(b['id'])) else 'posts'
                S.update(col, str(b['id']), {'status': st})   # 지우지 않고 숨김
                return self.send_json({'ok': True})
            if path == '/api/admin/contact':
                if str(b.get('action')) != 'hide' or not b.get('id'):
                    return self.send_json({'error': '잘못된 요청'}, 400)
                S.update('contacts', str(b['id']), {'status': 'hidden'})
                return self.send_json({'ok': True})
            return self.send_json({'error': '없는 API'}, 404)
        if limited(ip, 'write', 8, 60):
            return self.send_json({'error': '잠시 뒤에 다시 해 주세요(요청이 너무 잦습니다)'}, 429)
        if path == '/api/board':
            cfg = board_cfg(); title = clean(b.get('title'), 120); url = clean(b.get('url'), 300); text = clean(b.get('text'), 2000); name = clean(b.get('name'), 30) or '익명'
            if len(title) < 4 or (url and not re.match(r'https?://[^\s]+$', url)) or (not url and len(text) < 5):
                return self.send_json({'error': '제목(4자 이상)과, 링크 주소(https://…) 또는 5자 이상의 글이 필요합니다'}, 400)
            kind = 'ask' if title.startswith('묻습니다') else ('show' if title.startswith('보여 줍니다') else 'all')
            st = 'approved' if cfg.get('moderation') == 'after' else 'pending'
            S.put('posts', newid(), {'title': title, 'url': url, 'text': text, 'name': name, 'kind': kind, 'points': 1, 'status': st, 'ip': iphash(ip)})
            return self.send_json({'ok': True, 'shown': st == 'approved', 'message': '글을 올렸습니다.' if st == 'approved' else '글을 받았습니다. 운영자가 승인하면 보입니다.'})
        if path == '/api/board/vote':
            pid = clean(b.get('id'), 60); p = S.get('posts', pid)
            if not p or p.get('status') != 'approved':
                return self.send_json({'error': '없는 글'}, 404)
            vid = f'{pid}|{iphash(ip)}'
            with LOCK:   # 한 사람이 한 글에 한 번만
                if not S.get('post_votes', vid):
                    S.put('post_votes', vid, {'pid': pid}); p = S.get('posts', pid); S.update('posts', pid, {'points': int(p.get('points', 1)) + 1})
            return self.send_json({'ok': True, 'points': S.get('posts', pid).get('points', 1)})
        if path == '/api/board/comment':
            cfg = board_cfg(); pid = clean(b.get('id'), 60); body_ = clean(b.get('body'), 1000); name = clean(b.get('name'), 30) or '익명'; par = clean(b.get('parent'), 60)
            p = S.get('posts', pid)
            if not p or p.get('status') != 'approved' or len(body_) < 2:
                return self.send_json({'error': '댓글을 2글자 이상 적어 주세요'}, 400)
            st = 'approved' if cfg.get('moderation') == 'after' else 'pending'
            S.put('pcomments', newid(), {'pid': pid, 'parent': par, 'name': name, 'body': body_, 'status': st, 'ip': iphash(ip)})
            return self.send_json({'ok': True, 'shown': st == 'approved', 'message': '댓글을 달았습니다.' if st == 'approved' else '댓글을 받았습니다. 운영자가 승인하면 보입니다.'})
        if path == '/api/board/flag':
            tid = clean(b.get('id'), 60)
            if tid:
                S.put('flags', f'{tid}|{iphash(ip)}', {'target': tid})
            return self.send_json({'ok': True})
        if path == '/api/comments':
            slug = clean(b.get('slug'), 120); name = clean(b.get('name'), 30) or '익명'; txt = clean(b.get('body'), 600)
            if not slug or len(txt) < 2:
                return self.send_json({'error': '내용을 2글자 이상 적어 주세요'}, 400)
            S.put('comments', newid(), {'slug': slug, 'name': name, 'body': txt, 'status': 'pending', 'ip': iphash(ip)})
            return self.send_json({'ok': True, 'message': '댓글을 받았습니다. 운영자가 승인하면 보입니다.'})
        if path == '/api/like':
            slug = clean(b.get('slug'), 120)
            if not slug:
                return self.send_json({'error': '대상이 없습니다'}, 400)
            S.put('likes', f'{slug}|{iphash(ip)}|{day}', {'slug': slug, 'day': day})
            return self.send_json({'ok': True, 'likes': S.count('likes', {'slug': slug})})
        if path == '/api/contact':
            name = clean(b.get('name'), 40); email = clean(b.get('email'), 120); msg = clean(b.get('message'), 1500)
            if len(msg) < 5 or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
                return self.send_json({'error': '메일 주소와 5글자 이상의 내용이 필요합니다'}, 400)
            S.put('contacts', newid(), {'name': name or '이름 없음', 'email': email, 'message': msg, 'status': 'new'})
            return self.send_json({'ok': True, 'message': '문의를 받았습니다. 확인하는 대로 메일로 답하겠습니다.'})
        if path == '/api/subscribe':
            email = clean(b.get('email'), 120)
            if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
                return self.send_json({'error': '메일 주소를 확인해 주세요'}, 400)
            S.put('subscribers', email.lower(), {'email': email, 'status': 'on'})
            return self.send_json({'ok': True, 'message': '소식 받기를 신청했습니다.'})
        if path == '/api/poll':
            poll = clean(b.get('id'), 60); opt = clean(b.get('option'), 60)
            if not poll or not opt:
                return self.send_json({'error': '선택이 없습니다'}, 400)
            S.put('poll_votes', f'{poll}|{iphash(ip)}', {'poll': poll, 'opt': opt}); res = {}
            for r in S.find('poll_votes', {'poll': poll}, 10000):
                res[r['opt']] = res.get(r['opt'], 0) + 1
            return self.send_json({'ok': True, 'results': res})
        if path == '/api/kv':
            k = clean(b.get('k'), 80); v = b.get('v')
            if not k or len(json.dumps(v, ensure_ascii=False)) > 6000:
                return self.send_json({'error': '저장할 수 없는 크기입니다'}, 400)
            S.put('kv', k, {'v': v})
            return self.send_json({'ok': True})
        return self.send_json({'error': '없는 API'}, 404)


class Srv(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def handle_error(self, *a):
        pass


if __name__ == '__main__':
    if ARGS.dump:
        print(json.dumps(store().find(ARGS.dump, None, 10000, 'asc'), ensure_ascii=False, indent=1)); sys.exit(0)
    store()
    srv = Srv((ARGS.host, ARGS.port), H)
    print(f'서버가 켜졌습니다 → http://{ARGS.host}:{ARGS.port}/  (사이트 {SITE} · 자료 {"PostgreSQL" if isinstance(store(), PgStore) else DATA})', flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
