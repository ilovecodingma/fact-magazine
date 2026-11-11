# -*- coding: utf-8 -*-
"""자가 시험: 키트를 켜서 찍고, **창이 보이는 브라우저**를 띄워 단계마다 화면에 「지금 무엇을 하는지」 띠를 보여 주며 실제 입력(누르기·글자 넣기)을 보낸다.
터미널에는 단계별 ✓/✗ 와 본 값이 나오고, 끝에 한 줄 「N단계 가운데 M단계 통과」. 파이썬 기본 기능만 쓴다(브라우저 제어는 아래 작은 웹소켓 클라이언트로).
사용: python selftest.py calc              한 키트(이름은 영문·한글 별명 모두)
      python selftest.py calc quiz search   여러 개
      python selftest.py --all              selftest 가 적힌 키트 전부
      python selftest.py calc --headless    창을 띄우지 않고 같은 단계를 돈다(화면 없는 환경은 자동으로 이렇게 알리고 돈다)
      python selftest.py calc --slow 1.2    단계 사이 간격(초, 기본 0.8)
단계는 kits/<이름>/kit.json 의 selftest 에 적는다:
  {"parts": [...켤 부품(없으면 kit 의 parts)], "extra_parts": [...], "steps": [{"say": "띠에 보일 말", "goto": "calc/", "click": "css", "type": ["css", "넣을 글자"], "wait": 0.5, "expect": {"sel": "css", "contains": "글자", "regex": "정규식", "min_count": 1}}]}
기대한 글자가 화면에 없으면 ✗ 로 표시하고 이유를 적는다(본 값을 같이 보여 줌)."""
import base64, glob, hashlib, json, os, platform, re, shutil, socket, socketserver, struct, subprocess, sys, tempfile, threading, time, urllib.request
import http.server
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ARGS = sys.argv[1:]
SHOTS = os.path.abspath(ARGS[ARGS.index('--shots') + 1]) if '--shots' in ARGS and len(ARGS) > ARGS.index('--shots') + 1 else None   # 단계마다 그 시점의 화면을 이 폴더에 저장


def take_shot(pg, prefix, i, line):
    """--shots 폴더에 <앞이름>_<번호>_<단계 한 줄>.png 로 지금 화면을 저장한다(창이 없어도 됨)."""
    if not SHOTS:
        return
    try:
        os.makedirs(SHOTS, exist_ok=True)
        safe = lambda t: re.sub(r'[\\/:*?"<>|\s]+', '_', t).strip('_')[:40]
        r = pg.call('Page.captureScreenshot', format='png')
        open(os.path.join(SHOTS, f'{safe(prefix)}_{i:02d}_{safe(line)}.png'), 'wb').write(base64.b64decode(r['data']))
    except Exception as e:
        print('  (화면 저장 실패:', repr(e)[:60], ')')


def pos_args():
    """보이는 창 모드에서 창 위치: 환경 변수 SELFTEST_POS=2000,100"""
    v = os.environ.get('SELFTEST_POS', '').strip()
    return [f'--window-position={v}'] if re.fullmatch(r'-?\d+,-?\d+', v) else []
ALIAS = {'계산기': 'calc', '용어': 'glossary', '용어사전': 'glossary', '퀴즈': 'quiz', '검색': 'search', '상태': 'status', '게임': 'games', '일정': 'schedule', '질문': 'faq', '링크': 'links', '표비교': 'compare', '표 비교': 'compare',
         '사진첩': 'gallery', '가계부': 'ledger', '설문': 'survey', '디데이': 'dday', '타임라인': 'timeline', '위키': 'wiki', '전자책': 'ebook', '잡지': 'issue', '태그': 'tags', '보기설정': 'prefs', '앱': 'pwa'}


# ---------------- 최소 웹소켓 클라이언트(브라우저 원격 제어용) ----------------
class WS:
    def __init__(self, url):
        m = re.match(r'ws://([^:/]+):(\d+)(/.*)', url)
        self.s = socket.create_connection((m.group(1), int(m.group(2))), timeout=30)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f'GET {m.group(3)} HTTP/1.1\r\nHost: {m.group(1)}:{m.group(2)}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
        buf = b''
        while b'\r\n\r\n' not in buf:
            buf += self.s.recv(4096)
        self.buf = buf.split(b'\r\n\r\n', 1)[1]

    def send(self, text):
        data = text.encode('utf-8'); n = len(data); mask = os.urandom(4)
        head = bytes([0x81]) + (bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack('>H', n) if n < 65536 else bytes([0x80 | 127]) + struct.pack('>Q', n))
        self.s.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def _read(self, n):
        while len(self.buf) < n:
            chunk = self.s.recv(65536)
            if not chunk:
                raise ConnectionError('브라우저 연결이 끊겼습니다')
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def recv(self):
        msg = b''
        while True:
            b1, b2 = self._read(2)
            n = b2 & 0x7F
            if n == 126:
                n = struct.unpack('>H', self._read(2))[0]
            elif n == 127:
                n = struct.unpack('>Q', self._read(8))[0]
            data = self._read(n)
            op = b1 & 0x0F
            if op == 8:
                raise ConnectionError('브라우저가 연결을 닫았습니다')
            if op in (1, 0):
                msg += data
                if b1 & 0x80:
                    return msg.decode('utf-8', 'ignore')

    def close(self):
        try:
            self.s.close()
        except Exception:
            pass


class Page:
    def __init__(self, ws):
        self.ws, self.id = ws, 0

    def call(self, method, **params):
        self.id += 1; i = self.id
        self.ws.send(json.dumps({'id': i, 'method': method, 'params': params}))
        while True:
            d = json.loads(self.ws.recv())
            if d.get('id') == i:
                return d.get('result', {})

    def ev(self, expr):
        r = self.call('Runtime.evaluate', expression=expr, returnByValue=True, awaitPromise=True)
        return (r.get('result') or {}).get('value')


# ---------------- 브라우저·서버 ----------------
def find_browser():
    c = [os.environ.get('BROWSER', ''), shutil.which('msedge') or '', shutil.which('chrome') or '', shutil.which('google-chrome') or '', shutil.which('chromium') or '',
         r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Google\Chrome\Application\chrome.exe',
         '/usr/bin/google-chrome', '/usr/bin/chromium', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    return next((x for x in c if x and os.path.exists(x)), None)


def has_display():
    if platform.system() == 'Linux':
        return bool(os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'))
    return True


def free_port(start):
    for p in range(start, start + 50):
        s = socket.socket(); s.settimeout(0.2)
        busy = s.connect_ex(('127.0.0.1', p)) == 0; s.close()
        if not busy:
            return p
    return start


def resolve(name):
    kits = {}
    for p in glob.glob(os.path.join(HERE, 'kits', '*', 'kit.json')):
        k = json.load(open(p, encoding='utf-8')); kits[k['name']] = k
    key = ALIAS.get(name, name)
    return kits.get(key) or next((v for kk, v in kits.items() if key in kk or key in v.get('title', '')), None)


def build_site(kit, out):
    st = kit['selftest']
    S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
    parts = {p: False for p in S['parts']}
    for p in st.get('parts', kit.get('parts', [])) + st.get('extra_parts', []):
        parts[p] = True
    LOOK = {'calc': ('한입 계산소', '숫자를 넣으면 바로 계산해 주는 작은 가게', 'shop'), 'glossary': ('한입 용어 사전', '어려운 말을 짧게 풀어 줍니다', 'doc'), 'quiz': ('한입 퀴즈 놀이터', '풀면서 배우는 작은 퀴즈', 'play'), 'search': ('한입 찾기', '사이트 안 글을 낱말로 찾습니다', 'card'), 'status': ('한입 상태판', '수집과 점검 결과를 한눈에', 'one')}
    nm, tg, th = LOOK.get(kit['name'], ('한입 ' + kit.get('title', kit['name']), '키트 시험용 사이트', 'card'))
    env = dict(os.environ, SITE_BASE='/', SITE_URL='https://프로젝트이름.localhost', SITE_EXTRAS='{}', PARTS=json.dumps(parts), OUT_DIR=out, TOPIC_KEYWORDS='', SITE_NAME=nm, SITE_TAGLINE=tg, SITE_THEME=th)
    r = subprocess.run([sys.executable, '-X', 'utf8', os.path.join(HERE, 'build.py')], cwd=HERE, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.returncode == 0, r.stdout + r.stderr


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def start_server(directory):
    port = free_port(8820)
    handler = lambda *a, **k: Quiet(*a, directory=directory, **k)
    class Srv(socketserver.ThreadingTCPServer):
        def handle_error(self, *a):   # 브라우저가 연결을 먼저 끊는 정상 상황의 오류 출력은 숨긴다
            pass
    srv = Srv(('127.0.0.1', port), handler); srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, port


BANNER_JS = r"""(function(){var d=document.getElementById('__st');if(!d){d=document.createElement('div');d.id='__st';d.style.cssText='position:fixed;left:0;right:0;top:0;z-index:2147483647;background:#111;color:#fff;font:700 16px/1.5 system-ui,Malgun Gothic,sans-serif;padding:10px 16px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.4)';(document.body||document.documentElement).appendChild(d)}document.documentElement.style.paddingTop='48px';d.textContent=%s})()"""
HILITE_JS = r"""(function(s){var e=document.querySelector(s);if(!e)return false;e.scrollIntoView({block:'center'});e.style.outline='4px solid #e0245e';e.style.outlineOffset='3px';return true})(%s)"""
CENTER_JS = r"""(function(s){var e=document.querySelector(s);if(!e)return null;e.scrollIntoView({block:'center'});var r=e.getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2}})(%s)"""


def run_kit(kit, headless, slow):
    name = kit['name']; st = kit.get('selftest')
    if not st:
        print(f'– {name}: selftest 가 아직 없습니다(건너뜀)'); return None
    out = os.path.join(tempfile.mkdtemp(prefix='selftest_'), 'site')
    print(f'\n■ {kit.get("title", name)} — 자가 시험')
    ok, log = build_site(kit, out)
    if not ok:
        print('  ✗ 사이트를 찍지 못했습니다:', log.strip().splitlines()[-1][:120]); return (0, 1)
    srv, port = start_server(out)
    base = f'http://127.0.0.1:{port}/'
    br = find_browser()
    if not br:
        print('  ✗ 브라우저(Edge·Chrome)를 찾지 못해 화면 시험을 못 합니다 — 설치 방법은 python doctor.py --env'); srv.shutdown(); return (0, 1)
    vis = not headless and has_display()
    if not vis:
        print('  (화면이 없는 환경이거나 --headless 라서 창을 띄우지 않고 같은 단계를 돕니다)')
    dp = free_port(9400)
    prof = tempfile.mkdtemp(prefix='stprof_')
    args = [br, f'--remote-debugging-port={dp}', f'--user-data-dir={prof}', '--no-first-run', '--no-default-browser-check', '--window-size=1100,900', '--disable-gpu'] + pos_args() + ['about:blank']
    if not vis:
        args.insert(1, '--headless=new')
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    passed = total = 0
    try:
        tabs = None
        for _ in range(60):
            try:
                tabs = json.loads(urllib.request.urlopen(f'http://127.0.0.1:{dp}/json', timeout=2).read());
                if tabs: break
            except Exception:
                time.sleep(0.25)
        pg = Page(WS(next(t for t in tabs if t['type'] == 'page')['webSocketDebuggerUrl']))
        pg.call('Page.enable'); pg.call('Emulation.setDeviceMetricsOverride', width=1100, height=900, deviceScaleFactor=1, mobile=False)
        for i, step in enumerate(st['steps'], 1):
            total += 1; res = '?'; good = True; say = step.get('say', '')
            try:
                if 'goto' in step:
                    pg.call('Page.navigate', url=base + step['goto']); time.sleep(1.2 + (0.6 if slow > 1 else 0))
                if say:
                    pg.ev(BANNER_JS % json.dumps(f'[{i}/{len(st["steps"])}] {say}', ensure_ascii=False))
                time.sleep(slow * 0.6)
                if 'offline' in step:   # 인터넷을 끄거나 켠다(오프라인에서도 열리는지 보려고)
                    pg.call('Network.enable'); pg.call('Network.emulateNetworkConditions', offline=bool(step['offline']), latency=0, downloadThroughput=-1, uploadThroughput=-1); time.sleep(0.3)
                if step.get('reload'):
                    pg.call('Page.reload'); time.sleep(1.6 + slow * 0.3)
                    pg.ev(BANNER_JS % json.dumps(f'[{i}/{len(st["steps"])}] {say}', ensure_ascii=False))
                if 'eval' in step:   # 화면 안에서 식을 풀어 본 값이 기대와 같은지(예: 서비스 워커가 준비됐는지)
                    val = pg.ev(step['eval']); res = str(val)[:70]
                    if 'equals' in step:
                        good = val == step['equals']
                if step.get('installable'):   # 브라우저가 「설치할 수 있는 앱」으로 보는지
                    errs = pg.call('Page.getInstallabilityErrors').get('installabilityErrors', [])
                    good = not errs; res = '설치 가능' if good else '설치 막는 것: ' + ', '.join(e.get('errorId', '?') for e in errs)
                if 'pick_all' in step or 'pick' in step:   # 퀴즈 자료(quiz.json)의 정답 번호를 읽어 그 보기를 고른다(자료를 바꿔도 시험이 맞게)
                    qd = json.load(open(os.path.join(HERE, 'kits', 'quiz', 'data', 'quiz.json'), encoding='utf-8'))['questions']
                    todo = [(i2, step['pick_all']) for i2 in range(len(qd))] if 'pick_all' in step else [(step['pick'][0], step['pick'][1])]
                    for qi, how in todo:
                        if qi >= len(qd):
                            continue
                        ans = qd[qi]['answer']; val = ans if how == 'right' else (ans + 1) % len(qd[qi]['options'])
                        sel2 = f"input[name=q{qi}][value='{val}']"
                        if not pg.ev(HILITE_JS % json.dumps(sel2)):
                            good = False; res = f'화면에서 {sel2} 를 찾지 못함'; break
                        c = pg.ev(CENTER_JS % json.dumps(sel2)); pg.call('Input.dispatchMouseEvent', type='mousePressed', x=c['x'], y=c['y'], button='left', clickCount=1); pg.call('Input.dispatchMouseEvent', type='mouseReleased', x=c['x'], y=c['y'], button='left', clickCount=1); time.sleep(slow * 0.15)
                    if good:
                        res = f'{len(todo)}문항 ' + ('정답' if todo and todo[0][1] == 'right' else '오답') + '으로 고름'
                for key in ('click', 'type'):
                    if key in step:
                        sel, txt = (step['click'], None) if key == 'click' else (step['type'][0], step['type'][1])
                        if not pg.ev(HILITE_JS % json.dumps(sel)):
                            good = False; res = f'화면에서 {sel} 를 찾지 못함'; break
                        time.sleep(slow * 0.5)
                        c = pg.ev(CENTER_JS % json.dumps(sel))
                        pg.call('Input.dispatchMouseEvent', type='mousePressed', x=c['x'], y=c['y'], button='left', clickCount=1); pg.call('Input.dispatchMouseEvent', type='mouseReleased', x=c['x'], y=c['y'], button='left', clickCount=1)
                        if txt is not None:
                            pg.ev(f'document.querySelector({json.dumps(sel)}).select&&document.querySelector({json.dumps(sel)}).select()'); pg.call('Input.insertText', text=txt)
                time.sleep(step.get('wait', 0.4) + slow * 0.3)
                ex = step.get('expect')
                if ex and ('{N' in json.dumps(ex, ensure_ascii=False)):
                    nq = len(json.load(open(os.path.join(HERE, 'kits', 'quiz', 'data', 'quiz.json'), encoding='utf-8'))['questions'])
                    ex = json.loads(json.dumps(ex, ensure_ascii=False).replace('{N1}', str(nq - 1)).replace('{N}', str(nq)))
                if good and ex:
                    sel = ex.get('sel', 'body')
                    if 'min_count' in ex:
                        n = pg.ev(f'document.querySelectorAll({json.dumps(sel)}).length') or 0
                        good = n >= ex['min_count']; res = f'{sel} {n}개'
                    else:
                        txt = pg.ev(f'(document.querySelector({json.dumps(sel)})||{{}}).innerText||""') or ''
                        flat = re.sub(r'\s+', ' ', txt).strip()
                        res = flat[:70]
                        if 'contains' in ex and ex['contains'] in flat:   # 기대한 글자 둘레를 보여 준다(본 값)
                            i0 = flat.index(ex['contains']); res = ('…' if i0 > 25 else '') + flat[max(0, i0 - 25): i0 + len(ex['contains']) + 35]
                        if 'contains' in ex:
                            good = ex['contains'] in txt
                        if 'regex' in ex:
                            good = bool(re.search(ex['regex'], txt))
                        if 'not_contains' in ex:
                            good = good and ex['not_contains'] not in txt
                elif good and res == '?':
                    res = '실행함'
            except Exception as e:
                good = False; res = '오류: ' + repr(e)[:80]
            passed += 1 if good else 0
            print(f'  {"✓" if good else "✗"} {i}. {say[:60]}  → {res}')
            take_shot(pg, name, i, say or res)
            time.sleep(slow * 0.4)
        try:
            shot = os.path.join(HERE, 'selftest_shots'); os.makedirs(shot, exist_ok=True)
            r = pg.call('Page.captureScreenshot', format='png'); open(os.path.join(shot, f'{name}.png'), 'wb').write(base64.b64decode(r['data']))
        except Exception:
            pass
        if vis:
            time.sleep(1.5)
    finally:
        try:
            proc.terminate(); proc.wait(timeout=5)
        except Exception:
            proc.kill()
        srv.shutdown(); shutil.rmtree(prof, ignore_errors=True)
    print(f'  → {total}단계 가운데 {passed}단계 통과' + ('' if passed == total else '  ※ ✗ 단계의 「본 값」을 보고 이유를 알려 주세요'))
    return (passed, total)


def tour(directory, title, headless, slow):
    """찍어 둔 사이트의 메뉴를 하나씩 눌러 열리는지(404 가 아닌지, 제목이 있는지) 보인다. directory = 주소 맨 위(/)로 찍은 사이트 폴더."""
    srv, port = start_server(directory); base = f'http://127.0.0.1:{port}/'
    br = find_browser()
    if not br:
        print('  ✗ 브라우저를 찾지 못해 둘러보기를 못 합니다'); srv.shutdown(); return (0, 1)
    vis = not headless and has_display()
    if not vis:
        print('  (창을 띄우지 않고 같은 단계를 돕니다)')
    dp = free_port(9400); prof = tempfile.mkdtemp(prefix='stprof_')
    args = [br, f'--remote-debugging-port={dp}', f'--user-data-dir={prof}', '--no-first-run', '--no-default-browser-check', '--window-size=1100,900', '--disable-gpu'] + pos_args() + ['about:blank']
    if not vis:
        args.insert(1, '--headless=new')
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    passed = total = 0
    try:
        tabs = None
        for _ in range(60):
            try:
                tabs = json.loads(urllib.request.urlopen(f'http://127.0.0.1:{dp}/json', timeout=2).read())
                if tabs: break
            except Exception:
                time.sleep(0.25)
        pg = Page(WS(next(t for t in tabs if t['type'] == 'page')['webSocketDebuggerUrl'])); pg.call('Page.enable')
        pg.call('Page.navigate', url=base); time.sleep(1.5)
        links = pg.ev("JSON.stringify([].map.call(document.querySelectorAll('nav.menu a'),function(a){return [a.textContent.trim(),a.getAttribute('href')]}))") or '[]'
        links = json.loads(links)
        hidden = pg.ev("JSON.stringify([].map.call(document.querySelectorAll('details.mn .mnp a'),function(a){return [a.textContent.trim(),a.getAttribute('href')]}))") or '[]'
        seen = {h for _, h in links}
        links += [x for x in json.loads(hidden) if x[1] not in seen]
        for i, (label, href) in enumerate(links, 1):
            total += 1
            pg.call('Page.navigate', url=base.rstrip('/') + href if href.startswith('/') else base + href); time.sleep(0.9 + slow * 0.4)
            pg.ev(BANNER_JS % json.dumps(f'[{i}/{len(links)}] 메뉴 「{label}」 를 눌러 열어 봅니다', ensure_ascii=False)); time.sleep(slow * 0.5)
            h1 = pg.ev("(document.querySelector('h1')||{}).innerText||''") or ''
            good = bool(h1.strip()) and '찾는 쪽이 없습니다' not in h1
            passed += 1 if good else 0
            print(f'  {"✓" if good else "✗"} {i}. 메뉴 「{label}」 → {re.sub(chr(10), " ", h1)[:50] or "(제목 없음)"}')
            take_shot(pg, title, i, '메뉴_' + label)
        if vis:
            time.sleep(1.2)
    finally:
        try:
            proc.terminate(); proc.wait(timeout=5)
        except Exception:
            proc.kill()
        srv.shutdown(); shutil.rmtree(prof, ignore_errors=True)
    print(f'  → 메뉴 {total}칸 가운데 {passed}칸이 열렸습니다')
    return (passed, total)


def main():
    if '--tour' in ARGS:   # python selftest.py --tour <사이트 폴더> [제목]
        i = ARGS.index('--tour'); d = ARGS[i + 1]; t = ARGS[i + 2] if len(ARGS) > i + 2 and not ARGS[i + 2].startswith('--') else d
        print(f'\n■ {t} — 메뉴 둘러보기')
        r = tour(os.path.abspath(d), t, '--headless' in ARGS, float(ARGS[ARGS.index('--slow') + 1]) if '--slow' in ARGS else 0.8)
        return 0 if r[0] == r[1] else 1
    headless = '--headless' in ARGS
    slow = float(ARGS[ARGS.index('--slow') + 1]) if '--slow' in ARGS else 0.8
    names = [a for i, a in enumerate(ARGS) if not a.startswith('--') and (i == 0 or ARGS[i - 1] not in ('--slow', '--shots'))]
    if '--all' in ARGS:
        names = [json.load(open(p, encoding='utf-8'))['name'] for p in sorted(glob.glob(os.path.join(HERE, 'kits', '*', 'kit.json'))) if json.load(open(p, encoding='utf-8')).get('selftest')]
    if not names:
        have = [json.load(open(p, encoding='utf-8'))['name'] for p in sorted(glob.glob(os.path.join(HERE, 'kits', '*', 'kit.json'))) if json.load(open(p, encoding='utf-8')).get('selftest')]
        print('자가 시험이 있는 키트:', ', '.join(have) or '(없음)'); print('사용: python selftest.py 키트이름 [--headless] [--slow 초] · python selftest.py --all'); return 0
    tp = tt = 0
    for n in names:
        k = resolve(n)
        if not k:
            print(f'「{n}」 키트를 찾지 못했습니다'); continue
        r = run_kit(k, headless, slow)
        if r:
            tp += r[0]; tt += r[1]
    if len(names) > 1:
        print(f'\n전체: {tt}단계 가운데 {tp}단계 통과')
    return 0 if tp == tt else 1


if __name__ == '__main__':
    sys.exit(main())
