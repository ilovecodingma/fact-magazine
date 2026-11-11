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
    """비어 있는 포트(연결도 안 되고 묶어 볼 수도 있는 것). 여러 시험이 동시에 돌아도 겹치지 않게 시작 번호를 흩뿌린다."""
    import random
    base = start + random.randint(0, 300)
    for p in range(base, base + 100):
        s = socket.socket(); s.settimeout(0.2)
        busy = s.connect_ex(('127.0.0.1', p)) == 0; s.close()
        if busy:
            continue
        t = socket.socket()
        try:
            t.bind(('127.0.0.1', p)); t.close(); return p
        except OSError:
            t.close()
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
    if st.get('extras'):
        env['SITE_EXTRAS'] = json.dumps(st['extras'], ensure_ascii=False)   # 예: 영상 모음 키트의 예시 영상 주소
    env.update({k: str(v) for k, v in (st.get('env') or {}).items()})
    r = subprocess.run([sys.executable, '-X', 'utf8', os.path.join(HERE, 'build.py')], cwd=HERE, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.returncode == 0, r.stdout + r.stderr


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_error(self, code, message=None, explain=None):   # 없는 주소에는 404.html(길 안내)을 보여 준다(실제 호스팅처럼)
        p = os.path.join(self.directory, '404.html')
        if code == 404 and os.path.exists(p):
            body = open(p, 'rb').read(); self.send_response(404); self.send_header('Content-Type', 'text/html; charset=utf-8'); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
        else:
            super().send_error(code, message, explain)


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



def text_png(br, title, blocks, out):
    """글을 읽기 좋은 쪽으로 그려 찍는다(폴더 목록·파일 경로가 화면에 나오지 않게). blocks = [(소제목, 글)]"""
    import html as H
    body = ''.join(f'<h2>{H.escape(h)}</h2><pre>{H.escape(t)}</pre>' for h, t in blocks)
    doc = ('<!doctype html><meta charset="utf-8"><title>' + H.escape(title) + '</title><style>body{margin:0;background:#f6f4ef;font:17px/1.7 "Malgun Gothic",system-ui,sans-serif;color:#111}'
           'main{max-width:900px;margin:0 auto;padding:28px 24px}h1{font-size:26px;border-bottom:3px double #111;padding-bottom:10px}h2{font-size:15px;color:#b5532a;margin:22px 0 6px}'
           'pre{white-space:pre-wrap;word-break:break-word;font:inherit;background:#fff;border:1px solid #ddd;border-radius:10px;padding:14px 16px;margin:0}</style><main><h1>' + H.escape(title) + '</h1>' + body + '</main>')
    f = os.path.join(tempfile.mkdtemp(), 't.html'); open(f, 'w', encoding='utf-8').write(doc)
    subprocess.run([br, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1100,900', f'--screenshot={out}', 'file:///' + f.replace(chr(92), '/')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)


def shoot_pages(directory, pages, outs, width=1280, height=860, mobile=False):
    """사이트 폴더의 쪽들을 지정한 화면 크기(휴대폰이면 모바일 흉내)로 찍어 outs 경로에 저장. 헤드리스 브라우저의 최소 창 너비에 걸리지 않게 CDP 로 크기를 정한다."""
    srv, port = start_server(directory); br = find_browser()
    if not br:
        srv.shutdown(); return False
    dp = free_port(9400); prof = tempfile.mkdtemp(prefix='stprof_')
    proc = subprocess.Popen([br, '--headless=new', f'--remote-debugging-port={dp}', f'--user-data-dir={prof}', '--no-first-run', '--disable-gpu', 'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ok = True
    try:
        tabs = None
        for _ in range(60):
            try:
                tabs = json.loads(urllib.request.urlopen(f'http://127.0.0.1:{dp}/json', timeout=2).read())
                if tabs: break
            except Exception:
                time.sleep(0.25)
        pg = Page(WS(next(t for t in tabs if t['type'] == 'page')['webSocketDebuggerUrl'])); pg.call('Page.enable')
        pg.call('Emulation.setDeviceMetricsOverride', width=width, height=height, deviceScaleFactor=1, mobile=bool(mobile))
        for u, out in zip(pages, outs):
            bottom = u.endswith('@bottom'); u = u[:-7] if bottom else u
            pg.call('Page.navigate', url=f'http://127.0.0.1:{port}/{u}'); time.sleep(1.2)
            if bottom:
                pg.ev('window.scrollTo(0, document.body.scrollHeight)'); time.sleep(0.4)
            r = pg.call('Page.captureScreenshot', format='png'); open(out, 'wb').write(base64.b64decode(r['data']))
    except Exception as e:
        print('  (화면 저장 실패:', repr(e)[:60], ')'); ok = False
    finally:
        try:
            proc.terminate(); proc.wait(timeout=5)
        except Exception:
            proc.kill()
        srv.shutdown(); shutil.rmtree(prof, ignore_errors=True)
    return ok



def png_empty_ratio(data, block=32):
    """PNG(RGB/RGBA 8비트, Chrome 이 저장한 것)를 직접 읽어 「배경색 한 가지로만 채워진 칸」의 비율을 잰다(빈 영역 비율)."""
    import zlib, struct
    pos = 8; idat = b''; w = h = 0; ct = 6
    while pos < len(data):
        ln, = struct.unpack('>I', data[pos:pos + 4]); typ = data[pos + 4:pos + 8]; body = data[pos + 8:pos + 8 + ln]; pos += 12 + ln
        if typ == b'IHDR':
            w, h, bd, ct = struct.unpack('>IIBB', body[:10])
        elif typ == b'IDAT':
            idat += body
    ch = {2: 3, 6: 4}.get(ct, 4); raw = zlib.decompress(idat); stride = w * ch; rows = []; prev = bytearray(stride); i = 0
    for y in range(h):
        f = raw[i]; line = bytearray(raw[i + 1:i + 1 + stride]); i += 1 + stride
        for x in range(stride):
            a_ = line[x - ch] if x >= ch else 0; b_ = prev[x]; c_ = prev[x - ch] if x >= ch else 0
            if f == 1: line[x] = (line[x] + a_) & 255
            elif f == 2: line[x] = (line[x] + b_) & 255
            elif f == 3: line[x] = (line[x] + (a_ + b_) // 2) & 255
            elif f == 4:
                pa, pb, pc = abs(b_ - c_), abs(a_ - c_), abs(a_ + b_ - 2 * c_)
                line[x] = (line[x] + (a_ if pa <= pb and pa <= pc else (b_ if pb <= pc else c_))) & 255
        rows.append(line); prev = line
    from collections import Counter
    cnt = Counter(bytes(rows[y][x * ch:x * ch + 3]) for y in range(0, h, 7) for x in range(0, w, 7)); bg = cnt.most_common(1)[0][0]
    empty = tot = 0
    for by in range(0, h - block + 1, block):
        for bx in range(0, w - block + 1, block):
            tot += 1; same = True
            for y in range(by, by + block, 4):
                row = rows[y]
                for x in range(bx, bx + block, 4):
                    if bytes(row[x * ch:x * ch + 3]) != bg:
                        same = False; break
                if not same: break
            empty += 1 if same else 0
    return empty / max(1, tot)


MEASURE_JS = r"""(function(){
 function lum(c){var a=c.map(function(v){v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)});return 0.2126*a[0]+0.7152*a[1]+0.0722*a[2]}
 function parse(s){var m=s.match(/rgba?\(([^)]+)\)/);if(!m)return null;var p=m[1].split(',').map(parseFloat);return {c:p.slice(0,3),a:p.length>3?p[3]:1}}
 function bgOf(e){while(e){var p=parse(getComputedStyle(e).backgroundColor);if(p&&p.a>0.5)return p.c;e=e.parentElement}return [255,255,255]}
 var vw=innerWidth,vh=innerHeight,minF=999,minC=99,minFEl='',minCEl='',imgs=0,info=0,seen=0;
 var all=document.querySelectorAll('body *');
 all.forEach(function(e){var cs=getComputedStyle(e);if(cs.display==='none'||cs.visibility==='hidden')return;var r=e.getBoundingClientRect();if(r.width<2||r.height<2)return;
  var own=''; e.childNodes.forEach(function(n){if(n.nodeType===3)own+=n.textContent}); own=own.trim();
  if(own.length>=2){var fs=parseFloat(cs.fontSize);if(fs<minF){minF=fs;minFEl=e.tagName.toLowerCase()+'.'+(e.className||'')+' "'+own.slice(0,14)+'"'}
   var fg=parse(cs.color);if(fg){var bg=bgOf(e),L1=lum(fg.c),L2=lum(bg),ratio=(Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);if(ratio<minC){minC=ratio;minCEl=e.tagName.toLowerCase()+' "'+own.slice(0,14)+'"'}}
   if(r.top<vh&&r.bottom>0&&r.left<vw)info++}
  if((e.tagName==='IMG'||e.tagName==='SVG'||e.tagName==='CANVAS'||e.tagName==='svg')&&r.top<vh&&r.bottom>0&&r.width>60&&r.height>40)imgs++;
 });
 var crop=0;document.querySelectorAll('img').forEach(function(im){var r=im.getBoundingClientRect();if(r.width<40||r.top>vh||r.bottom<0||!im.naturalWidth||!im.naturalHeight)return;var cs=getComputedStyle(im);var q=(r.width/r.height)/(im.naturalWidth/im.naturalHeight);if(Math.abs(q-1)>0.06&&cs.objectFit!=='contain')crop++});
 var cats=document.querySelectorAll('nav.menu a[data-cat]').length;
 return JSON.stringify({imgCrop:crop,cats:cats,minFont:Math.round(minF*10)/10,minFontEl:minFEl,minContrast:Math.round(minC*100)/100,minContrastEl:minCEl,imgs:imgs,info:info,overflow:document.documentElement.scrollWidth-innerWidth,pageH:document.documentElement.scrollHeight,vh:vh})
})()"""


def measure_site(directory, pages, width=1280, height=860, mobile=False):
    """만듦새 재기: 쪽마다 (빈 영역 비율, 첫 화면 그림 수, 가장 작은 글자, 가장 낮은 대비, 가로 넘침, 첫 화면 정보량)을 CDP 로 잰다."""
    srv, port = start_server(directory); br = find_browser(); res = []
    if not br:
        srv.shutdown(); return res
    dp = free_port(9400); prof = tempfile.mkdtemp(prefix='stprof_')
    proc = subprocess.Popen([br, '--headless=new', f'--remote-debugging-port={dp}', f'--user-data-dir={prof}', '--no-first-run', '--disable-gpu', 'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        tabs = None
        for _ in range(60):
            try:
                tabs = json.loads(urllib.request.urlopen(f'http://127.0.0.1:{dp}/json', timeout=2).read())
                if tabs: break
            except Exception:
                time.sleep(0.25)
        pg = Page(WS(next(t for t in tabs if t['type'] == 'page')['webSocketDebuggerUrl'])); pg.call('Page.enable')
        pg.call('Emulation.setDeviceMetricsOverride', width=width, height=height, deviceScaleFactor=1, mobile=bool(mobile))
        for u in pages:
            pg.call('Page.navigate', url=f'http://127.0.0.1:{port}/{u}'); time.sleep(1.6)
            m = json.loads(pg.ev(MEASURE_JS) or '{}')
            shot = base64.b64decode(pg.call('Page.captureScreenshot', format='png')['data'])
            try:
                m['empty'] = round(png_empty_ratio(shot), 3)
            except Exception as e:
                m['empty'] = None
            res.append(m)
    finally:
        try:
            proc.terminate(); proc.wait(timeout=5)
        except Exception:
            proc.kill()
        srv.shutdown(); shutil.rmtree(prof, ignore_errors=True)
    return res


# 만듦새 기준(참고 사이트와 같은 급으로 보이는가): 빈 영역·그림·글자·대비·넘침·정보량
THRESH = {'imgCrop': ('그림 잘림(그림 비율≠표시 비율)', 0, '<='), 'cats': ('분야 탭 수', 3, '>='), 'empty': ('첫 화면 빈 영역 비율', 0.55, '<='), 'imgs': ('첫 화면 그림 카드 수', 4, '>='), 'minFont': ('가장 작은 글자(px)', 13, '>='), 'minContrast': ('가장 낮은 대비', 4.5, '>='), 'overflow': ('가로 넘침(px)', 2, '<='), 'info': ('첫 화면 정보량(글 덩어리)', 14, '>=')}


def grade(m, imgs_needed=True, empty_needed=True, min_imgs=4, cats_needed=True):
    """측정값 m → [(키, 이름, 값, 기준, 통과)]"""
    out = []
    for k, (nm, th, op) in THRESH.items():
        v = m.get(k)
        if v is None:
            continue
        if k == 'imgs' and not imgs_needed:
            continue
        if k == 'cats' and not cats_needed:
            continue
        if k == 'imgs':
            th = min_imgs
        if k == 'empty' and not empty_needed:
            continue   # 글 쪽은 본문 폭이 좁아 양옆이 비는 게 정상이라 빈 영역은 첫 화면만 잰다
        ok = (v <= th) if op == '<=' else (v >= th)
        out.append((k, nm, v, f'{op}{th}', ok))
    return out

def internet_ok():
    for u in ('https://www.naver.com', 'https://www.google.com'):
        try:
            urllib.request.urlopen(u, timeout=4); return True
        except Exception:
            continue
    return False


def missing_needs(needs):
    """selftest.needs 의 항목(ffmpeg·internet) 가운데 이 PC 에 없는 것의 안내 문구. 다 있으면 ''"""
    for n in needs:
        if n == 'ffmpeg' and not (os.environ.get('FFMPEG') or shutil.which('ffmpeg')):
            return 'ffmpeg 가 있으면 됩니다(윈도우 `winget install Gyan.FFmpeg`)'
        if n == 'internet' and not internet_ok():
            return '인터넷이 연결되어 있으면 됩니다(자동완성 서비스에 천천히 요청)'
    return ''


def run_script_kit(kit):
    """화면이 없는 키트: 키트 폴더를 임시 폴더에 복사해 예시 입력으로 돌리고, 나온 파일을 보여 준다(저장소 파일은 건드리지 않는다).
    selftest.runs = [{say, cmd:[스크립트, 인자…]({out}=임시 키트 폴더), cwd:'kit'|'repo', show:'결과.md'|'stdout', expect:{contains|regex|min_chars}, timeout}]"""
    name = kit['name']; st = kit['selftest']
    print(f'\n■ {kit.get("title", name)} — 자가 시험(예시 입력으로 돌려 결과를 읽습니다)')
    work = os.path.join(tempfile.mkdtemp(prefix='selftest_'), 'kit'); shutil.copytree(os.path.join(HERE, 'kits', name), work)
    br = find_browser(); passed = total = 0
    for i, r in enumerate(st['runs'], 1):
        total += 1; say = r.get('say', '')
        cwd = HERE if r.get('cwd') == 'repo' else work
        cmd = [sys.executable, '-X', 'utf8'] + [a.replace('{out}', work) for a in r['cmd']]
        try:
            p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=r.get('timeout', 120), env=dict(os.environ, PYTHONIOENCODING='utf-8'))
            shp = r.get('show', 'stdout').replace('{out}', work)
            text = p.stdout if shp == 'stdout' else (open(os.path.join(cwd, shp), encoding='utf-8').read() if os.path.exists(os.path.join(cwd, shp)) else '')
            good = p.returncode == 0; ex = r.get('expect') or {}
            if 'contains' in ex: good = good and ex['contains'] in text
            if 'regex' in ex: good = good and bool(re.search(ex['regex'], text))
            if 'min_chars' in ex: good = good and len(text.strip()) >= ex['min_chars']
            res = re.sub(r'\s+', ' ', text).strip()[:70] or (p.stderr.strip()[-70:] or '(출력 없음)')
        except Exception as e:
            good = False; res = '오류: ' + repr(e)[:80]; text = res
        passed += 1 if good else 0
        print(f'  {"✓" if good else "✗"} {i}. {say[:60]}  → {res}')
        if SHOTS and br:
            os.makedirs(SHOTS, exist_ok=True)
            safe = lambda t: re.sub(r'[\\/:*?"<>|\s]+', '_', t).strip('_')[:40]
            text_png(br, f'{kit.get("title", name)} — {say}', [('결과', '\n'.join(text.strip().splitlines()[:40]))], os.path.join(SHOTS, f'{safe(name)}_{i:02d}_{safe(say)}.png'))
    print(f'  → {total}단계 가운데 {passed}단계 통과' + ('' if passed == total else '  ※ ✗ 단계의 「본 값」을 보고 이유를 알려 주세요'))
    return (passed, total)


def run_kit(kit, headless, slow):
    name = kit['name']; st = kit.get('selftest')
    if not st:
        print(f'– {name}: selftest 가 아직 없습니다(건너뜀)'); return None
    if st.get('skip'):
        print(f'– {kit.get("title", name)}: 건너뜀: {st["skip"]}'); return ('skip', st['skip'])
    if st.get('needs'):
        miss = missing_needs(st['needs'])
        if miss:
            print(f'– {kit.get("title", name)}: 건너뜀: {miss}'); return ('skip', miss)
    for pc in (st.get('pre') or []):   # 시험 전에 돌릴 준비 명령(예: 카드 그림 만들기)
        subprocess.run([sys.executable, '-X', 'utf8'] + pc, cwd=HERE, capture_output=True, timeout=180)
    if st.get('runs'):
        return run_script_kit(kit)
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
                if 'eval' in step:   # 화면 안에서 식을 풀어 본 값이 기대와 같은지(예: 서비스 워커가 준비됐는지)
                    val = pg.ev(step['eval']); res = str(val)[:70]
                    if 'equals' in step:
                        good = val == step['equals']
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
        if r and not isinstance(r[0], str):
            tp += r[0]; tt += r[1]
    if len(names) > 1:
        print(f'\n전체: {tt}단계 가운데 {tp}단계 통과')
    return 0 if tp == tt else 1


if __name__ == '__main__':
    sys.exit(main())
