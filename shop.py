# -*- coding: utf-8 -*-
"""가게(2장): 종합 쇼핑몰을 본뜬 템플릿 — 화면은 Next.js(shop/web), 백엔드는 파이썬(shop/api, 기능 묶음을 붙였다 뗐다), 휴대폰에서는 앱으로 깔린다. 결제는 없다.
python run.py 가게 켜기   백엔드(8787)와 화면(3000)을 내 PC 에서 켠다(처음에는 화면에 필요한 것을 받느라 1~2분)
python run.py 가게 끄기 · 가게 상태 · 가게 시험        끄기 · 지금 켜져 있나·붙은 기능 · 백엔드 스스로 시험(15단계)
python run.py 붙여 <기능> · 떼 <기능> · 기능             기능 묶음을 붙였다 뗀다(서버를 끄지 않아도 몇 초 안에 화면이 따라간다)
python run.py 가게 상품다시                             shop/api/data/products.json 을 수정 뒤 상품을 다시 넣는다(주문·상품평은 남는다)"""
import json, os, shutil, sqlite3, subprocess, sys, time, urllib.request
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
SHOP = os.path.join(HERE, 'shop'); WEB = os.path.join(SHOP, 'web'); API = os.path.join(SHOP, 'api')
CONF = os.path.join(API, 'modules.json'); RUN = os.path.join(SHOP, '.run.json'); DB = os.path.join(API, 'data', 'shop.db')
A = sys.argv[1:]
NAMES = {'catalog': '상품', 'cart': '장바구니', 'orders': '주문', 'reviews': '상품평', 'wish': '찜', 'rank': '인기 순위', 'coupons': '쿠폰', 'admin': '운영자'}
NEED = {'cart': ['catalog'], 'orders': ['cart'], 'reviews': ['catalog'], 'wish': ['catalog'], 'rank': ['catalog']}


def alive(url):
    try:
        urllib.request.urlopen(url, timeout=1.5); return True
    except Exception:
        return False


def find(word):
    w = word.strip().lower()
    for k, v in NAMES.items():
        if w in (k, v, v.replace(' ', '')):
            return k
    return next((f[:-3] for f in os.listdir(os.path.join(API, 'modules')) if f.endswith('.py') and f[:-3] == w and f != '__init__.py'), None)


def conf():
    return json.load(open(CONF, encoding='utf-8'))


def features():
    d = conf(); on = d['on']
    allm = sorted(f[:-3] for f in os.listdir(os.path.join(API, 'modules')) if f.endswith('.py') and f != '__init__.py')
    print('기능 묶음(■ 붙어 있음 · □ 떨어져 있음):')
    for m in allm:
        print(f'  {"■" if m in on else "□"} {NAMES.get(m, m)} ({m})')
    return 0


def attach(word, on):
    k = find(word)
    if not k:
        print(f'그런 기능이 없습니다: {word}. 있는 것 — ' + ' · '.join(NAMES.values()) + '\n없는 기능은 shop/api/modules/<이름>.py 한 파일로 새로 만들어 붙입니다(ROUTES 와 init 만 있으면 됩니다).'); return 1
    d = conf(); cur = d['on']
    if on:
        add = [x for x in NEED.get(k, []) if x not in cur] + ([k] if k not in cur else [])
        d['on'] = cur + add; did = '붙였습니다: ' + ', '.join(NAMES.get(x, x) for x in add) if add else f'{NAMES.get(k, k)} 은(는) 이미 붙어 있습니다'
    else:
        gone = [k] + [x for x, ns in NEED.items() if k in ns and x in cur]
        gone = gone + [x for x, ns in NEED.items() if any(g in ns for g in gone) and x in cur and x not in gone]
        d['on'] = [x for x in cur if x not in gone]; did = '뗐습니다: ' + ', '.join(NAMES.get(x, x) for x in gone if x in cur) + ' (남긴 자료는 지우지 않았습니다 — 다시 붙이면 돌아옵니다)'
    json.dump(d, open(CONF, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(did + ('\n켜져 있는 가게는 몇 초 안에 화면이 따라갑니다.' if alive('http://127.0.0.1:8787/api/features') else '')); return 0


def start():
    if not shutil.which('node'):
        print('✗ 이 PC 에 Node.js 가 없습니다. 화면(Next.js)을 켜려면 nodejs.org 에서 받아 깔아야 합니다(설치는 직접). 백엔드만은 python shop/api/app.py 로 켤 수 있습니다.'); return 1
    key = os.environ.get('SHOP_ADMIN_KEY', '')   # 시험에서만 쓴다. 운영자 비밀번호는 독자가 운영자 화면에서 직접 정한다(세션은 비밀번호를 정하지도 받지도 않는다)
    os.makedirs(os.path.join(HERE, 'logs'), exist_ok=True); st = {}
    kw = dict(creationflags=0x00000008 | 0x00000200) if os.name == 'nt' else dict(start_new_session=True)
    if not alive('http://127.0.0.1:8787/api/features'):
        log = open(os.path.join(HERE, 'logs', '가게_백엔드.log'), 'a', encoding='utf-8')
        st['api'] = subprocess.Popen([sys.executable, '-X', 'utf8', os.path.join(API, 'app.py')], cwd=API, env=dict(os.environ, SHOP_ADMIN_KEY=key), stdout=log, stderr=log, stdin=subprocess.DEVNULL, **kw).pid
    if not os.path.isdir(os.path.join(WEB, 'node_modules')):
        print('화면에 필요한 것을 받습니다(처음 한 번, 1~2분)…', flush=True)
        r = subprocess.run('npm install --no-audit --no-fund', cwd=WEB, shell=True, capture_output=True, text=True, errors='replace')
        if r.returncode != 0:
            print('✗ 받지 못했습니다:', (r.stderr or '')[-300:]); return 1
    if not alive('http://127.0.0.1:3000/'):
        log = open(os.path.join(HERE, 'logs', '가게_화면.log'), 'a', encoding='utf-8')
        st['web'] = subprocess.Popen('npx next dev -p 3000', cwd=WEB, shell=True, stdout=log, stderr=log, stdin=subprocess.DEVNULL, **kw).pid
    old = json.load(open(RUN, encoding='utf-8')) if os.path.exists(RUN) else {}
    old.update(st); json.dump(old, open(RUN, 'w', encoding='utf-8'))
    t0 = time.time()
    while time.time() - t0 < 90 and not (alive('http://127.0.0.1:8787/api/features') and alive('http://127.0.0.1:3000/')):
        time.sleep(1)
    a, w = alive('http://127.0.0.1:8787/api/features'), alive('http://127.0.0.1:3000/')
    print(f'{"✓" if a else "✗"} 백엔드(파이썬) http://127.0.0.1:8787   {"✓" if w else "✗"} 화면(Next.js) http://127.0.0.1:3000   — {time.time() - t0:.0f}초')
    if a and w:
        print('가게: http://127.0.0.1:3000/   운영자: http://127.0.0.1:3000/admin' + ('' if key else ' (운영자 비밀번호는 이 주소를 열어 직접 정합니다 — 이 PC 에서만 정할 수 있습니다)') + '\n휴대폰에서는 같은 와이파이로 이 PC 의 주소를 열고 「홈 화면에 추가」 하면 앱으로 깔립니다(올린 뒤에는 그 주소에서).')
        if '--headless' not in A and '--열지않음' not in A:
            try:
                os.startfile('http://127.0.0.1:3000/') if os.name == 'nt' else None
            except Exception:
                pass
    else:
        print('켜지지 않은 쪽의 기록: logs/가게_백엔드.log · logs/가게_화면.log')
    return 0 if a and w else 1


def stop():
    for port in (8787, 3000):
        if os.name == 'nt':
            r = subprocess.run(f'netstat -ano | findstr LISTENING | findstr :{port}', shell=True, capture_output=True, text=True)
            for pid in {ln.split()[-1] for ln in r.stdout.splitlines() if ln.split() and ln.split()[1].endswith(f':{port}')}:
                subprocess.run(['taskkill', '/F', '/T', '/PID', pid], capture_output=True)
        else:
            subprocess.run(f'lsof -ti tcp:{port} | xargs kill', shell=True, capture_output=True)
    if os.path.exists(RUN):
        t = json.load(open(RUN, encoding='utf-8')).get('tunnel')
        if t:
            kill(t); forget_url()
        os.remove(RUN)
    print('가게를 껐습니다(자료는 shop/api/data/shop.db 에 그대로 있습니다).'); return 0


def status():
    a, w = alive('http://127.0.0.1:8787/api/features'), alive('http://127.0.0.1:3000/')
    print(f'백엔드 {"켜짐" if a else "꺼짐"} · 화면 {"켜짐" if w else "꺼짐"}'); features()
    if os.path.exists(DB):
        c = sqlite3.connect(DB)
        def n(t):
            try:
                return c.execute(f'select count(*) from {t}').fetchone()[0]
            except Exception:
                return 0
        print(f'상품 {n("products")}개 · 주문 {n("orders")}건 · 상품평 {n("reviews")}개')
    return 0


def cloudflared():
    """바깥 주소를 붙여 주는 프로그램(cloudflared)을 찾는다. 없으면 Cloudflare 의 공식 배포 주소에서 shop/.bin/ 으로 받는다(윈도우·리눅스)."""
    import platform, urllib.request
    exe = 'cloudflared.exe' if os.name == 'nt' else 'cloudflared'
    for c in (os.environ.get('CLOUDFLARED'), shutil.which('cloudflared'), os.path.join(SHOP, '.bin', exe)):
        if c and os.path.exists(c):
            return c
    arch = 'arm64' if platform.machine().lower() in ('arm64', 'aarch64') else 'amd64'
    name = None if sys.platform == 'darwin' else (f'cloudflared-windows-{arch}.exe' if os.name == 'nt' else f'cloudflared-linux-{arch}')
    if not name:
        print('이 컴퓨터에는 cloudflared 를 직접 깔아야 합니다(맥: brew install cloudflared). 깐 뒤 다시 「올려」 하면 됩니다.'); return None
    dst = os.path.join(SHOP, '.bin', exe); os.makedirs(os.path.dirname(dst), exist_ok=True)
    print('바깥 주소를 붙여 주는 프로그램(cloudflared)을 Cloudflare 의 공식 배포 주소에서 받습니다(처음 한 번, shop/.bin/ 에만 둡니다)…', flush=True)
    try:
        urllib.request.urlretrieve('https://github.com/cloudflare/cloudflared/releases/latest/download/' + name, dst)
        if os.name != 'nt':
            os.chmod(dst, 0o755)
        return dst
    except Exception as e:
        print('✗ 받지 못했습니다:', repr(e)[:120]); return None


def forget_url():
    """바깥 주소를 닫았으면 「올린 주소」 기록도 지운다(닫힌 주소가 상태창·홍보 글에 남지 않게)."""
    pg = os.path.join(HERE, '진도.json')
    if os.path.exists(pg):
        d = json.load(open(pg, encoding='utf-8'))
        if (d.get('deploy') or {}).get('live') == 'pc':
            d.pop('deploy'); json.dump(d, open(pg, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def kill(pid):
    subprocess.run(['taskkill', '/F', '/PID', str(pid)], capture_output=True) if os.name == 'nt' else subprocess.run(['kill', str(pid)], capture_output=True)


def share():
    import re
    run = json.load(open(RUN, encoding='utf-8')) if os.path.exists(RUN) else {}
    if len(A) > 1 and A[1] == '끄기':
        pid = run.pop('tunnel', None)
        if pid:
            kill(pid); json.dump(run, open(RUN, 'w', encoding='utf-8')); forget_url()
        print('바깥 주소를 닫았습니다.' if pid else '열어 둔 바깥 주소가 없습니다.'); return 0
    if not (alive('http://127.0.0.1:8787/api/features') and alive('http://127.0.0.1:3000/')):
        print('가게가 꺼져 있어 먼저 켭니다…', flush=True)
        if start() != 0:
            return 1
        run = json.load(open(RUN, encoding='utf-8')) if os.path.exists(RUN) else {}
    cf = cloudflared()
    if not cf:
        return 1
    os.makedirs(os.path.join(HERE, 'logs'), exist_ok=True); log = os.path.join(HERE, 'logs', 'shop_tunnel.log')
    if os.path.exists(log):
        os.remove(log)
    kw = dict(creationflags=0x00000008 | 0x00000200) if os.name == 'nt' else dict(start_new_session=True)
    t0 = time.time(); p = subprocess.Popen([cf, 'tunnel', '--url', 'http://127.0.0.1:3000', '--no-autoupdate', '--logfile', log], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, **kw)
    url = ''
    while time.time() - t0 < 60 and not url:
        time.sleep(2)
        try:
            m = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', open(log, encoding='utf-8', errors='replace').read()); url = m.group(0) if m else ''
        except Exception:
            pass
    if not url:
        kill(p.pid); print('✗ 바깥 주소를 받지 못했습니다(기록: logs/shop_tunnel.log).'); return 1
    if run.get('tunnel'):
        kill(run['tunnel'])
    run['tunnel'] = p.pid; json.dump(run, open(RUN, 'w', encoding='utf-8'))
    ok = False
    for _ in range(10):
        time.sleep(3)
        try:
            ok = urllib.request.urlopen(urllib.request.Request(url + '/api/features', headers={'User-Agent': 'Mozilla/5.0'}), timeout=15).status == 200
        except Exception:
            ok = False
        if ok:
            break
    pg = os.path.join(HERE, '진도.json'); d = json.load(open(pg, encoding='utf-8')) if os.path.exists(pg) else {'done': [], 'last': ''}
    d['deploy'] = dict(url=url, temp=True, claim='', expires=time.time() + 86400 * 365, live='pc', t=time.strftime('%Y-%m-%d %H:%M'))
    d['done'].append({'t': time.strftime('%Y-%m-%d %H:%M'), 'what': '올림: ' + url}); d['last'] = '올림: ' + url
    json.dump(d, open(pg, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\n{"✓" if ok else "✗"} 가게에 바깥 주소를 붙였습니다 — {time.time() - t0:.0f}초' + ('' if ok else ' (주소는 받았지만 아직 열리지 않습니다. 잠시 뒤 다시 열어 보세요)'))
    print('┌─ 남에게 보여 줄 주소 ' + '─' * 32)
    print('│ ' + url)
    print('│ 이 PC 와 가게가 켜져 있는 동안 누구나 열 수 있습니다(휴대폰으로 열어 「홈 화면에 추가」 하면 앱으로 깔립니다).')
    print('│ 담기·주문·상품평이 모두 됩니다. 운영자 화면은 ' + url + '/admin')
    print('│ PC 나 가게를 끄면 닫히고, 다시 열면 주소가 새로 나옵니다. 닫기: python run.py 가게 공유 끄기')
    print('└' + '─' * 52)
    return 0 if ok else 1


def find_product(word):
    R = []
    if os.path.exists(DB):
        c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
        R = [dict(r) for r in c.execute('select * from products')]; c.close()
    w = word.strip()
    return next((p for p in R if str(p['id']) == w), None) or next((p for p in R if w and w in p['name']), None)


def soldout():
    """가게 품절 <번호|이름 일부> [풀기] — 품절이면 화면에 「품절」이 뜨고 담기지 않는다. products.json 에도 적어 상품다시 뒤에도 남는다."""
    rest = [a for a in A[1:] if not a.startswith('--')]
    if not rest:
        print('사용: python run.py 가게 품절 <번호|이름 일부> [풀기]'); return 1
    p = find_product(rest[0])
    if not p:
        print('그런 상품이 없습니다(가게를 한 번 켠 뒤에 됩니다). python run.py 가게 상태'); return 1
    stock = 99 if len(rest) > 1 and rest[1] == '풀기' else 0
    c = sqlite3.connect(DB); c.execute('update products set stock=? where id=?', (stock, p['id'])); c.commit(); c.close()
    fp = os.path.join(API, 'data', 'products.json'); d = json.load(open(fp, encoding='utf-8'))
    for x in d['products']:
        if x['name'] == p['name']:
            if stock:
                x.pop('stock', None)
            else:
                x['stock'] = 0
    json.dump(d, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{p["id"]}번 「{p["name"]}」: ' + ('다시 팔기로 했습니다.' if stock else '품절로 바꿨습니다 — 화면에 「품절」이 뜨고 장바구니에 담기지 않습니다.') + (' 켜져 있는 가게는 새로 열면 반영됩니다.' if alive('http://127.0.0.1:8787/api/features') else ''))
    return 0


def promo():
    """가게 홍보 <번호|이름 일부> — 상품 하나로 홍보 글·짧은 문구·정사각 카드 그림을 promo_out/shop_<번호>/ 에 만든다. 올리지는 않는다."""
    import base64, html as H
    rest = [a for a in A[1:] if not a.startswith('--')]
    p = find_product(rest[0]) if rest else None
    if not p:
        print('사용: python run.py 가게 홍보 <번호|이름 일부>   (가게를 한 번 켠 뒤에 됩니다)'); return 1
    S = json.load(open(os.path.join(WEB, 'site.json'), encoding='utf-8'))
    pg = os.path.join(HERE, '진도.json'); dep = (json.load(open(pg, encoding='utf-8')).get('deploy') or {}) if os.path.exists(pg) else {}
    run = json.load(open(RUN, encoding='utf-8')) if os.path.exists(RUN) else {}
    url = (dep.get('url', '') + '/p/' + str(p['id'])) if dep.get('url') and dep.get('live') == 'pc' and run.get('tunnel') and alive(dep['url'] + '/api/features') else ''
    off = round((p['was'] - p['price']) * 100 / p['was']) if p['was'] > p['price'] else 0
    price = f'{p["price"]:,}원' + (f' ({off}% 할인, 원래 {p["was"]:,}원)' if off else '')
    out = os.path.join(HERE, 'promo_out', f'shop_{p["id"]}'); os.makedirs(out, exist_ok=True)
    where = url or '(가게 주소 — python run.py 올려 가게 로 받은 주소를 넣습니다)'
    open(os.path.join(out, '홍보글.md'), 'w', encoding='utf-8').write(f'# {p["name"]}\n\n{p["desc"]}\n\n- 값: {price}\n- 파는 곳: {S["name"]} — {S.get("tagline", "")}\n- 결제: 무통장 입금\n\n보러 가기: {where}\n')
    open(os.path.join(out, '문구_짧게.txt'), 'w', encoding='utf-8').write(f'{p["name"]} {p["price"]:,}원' + (f' ({off}%↓)' if off else '') + f' — {S["name"]}\n')
    open(os.path.join(out, '문구_보통.txt'), 'w', encoding='utf-8').write(f'{p["name"]}. {p["desc"]} {price}. {S["name"]}에서 {where}\n')
    img = os.path.join(WEB, 'public', 'p', f'{p["id"]}.jpg'); src = ('data:image/jpeg;base64,' + base64.b64encode(open(img, 'rb').read()).decode()) if os.path.exists(img) else ''
    card = os.path.join(out, 'card.html')
    open(card, 'w', encoding='utf-8').write(f'<!doctype html><meta charset="utf-8"><style>html,body{{margin:0;width:1080px;height:1080px;font-family:"Pretendard","Malgun Gothic",sans-serif;background:{H.escape(p["color"])}}}'
        'img{position:absolute;inset:0;width:1080px;height:1080px;object-fit:cover}.b{position:absolute;left:0;right:0;bottom:0;padding:56px 64px;color:#fff;background:linear-gradient(180deg,transparent,rgba(0,0,0,.78))}'
        '.s{font-size:34px;opacity:.9}.n{font-size:72px;font-weight:800;line-height:1.2;letter-spacing:-2px;margin:10px 0 18px}.p{font-size:56px;font-weight:800}.o{color:#ff6b57;margin-right:18px}</style>'
        + (f'<img src="{src}">' if src else '') + f'<div class="b"><div class="s">{H.escape(S["name"])}</div><div class="n">{H.escape(p["name"])}</div><div class="p">' + (f'<span class="o">{off}%</span>' if off else '') + f'{p["price"]:,}원</div></div>')
    png = os.path.join(out, '카드.png'); made = False
    try:
        sys.path.insert(0, HERE); import selftest as T
        br = T.find_browser()
        if br:
            subprocess.run([br, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1080,1080', f'--screenshot={png}', 'file:///' + card.replace(os.sep, '/')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
            made = os.path.exists(png)
    except Exception:
        pass
    print(f'「{p["name"]}」 홍보 묶음을 만들었습니다(올리지 않았습니다): promo_out/shop_{p["id"]}/')
    print('  홍보글.md · 문구_짧게.txt · 문구_보통.txt' + (' · 카드.png(1080×1080)' if made else ' · 카드 그림은 못 만들었습니다(브라우저 없음)'))
    print('[사람이 승인하면 이어지는 것] 블로그·SNS 에 올리기 — 운영자가 로그인한 화면에서. 값과 주소가 가게와 같은지 한 번 더 봅니다.' + ('' if url else ' (가게 주소가 아직 없어 주소 자리는 비워 두었습니다)'))
    return 0


def reseed():
    """products.json 으로 상품을 다시 넣는다. 이름이 그대로인 상품의 상품평·찜·본 횟수는 새 번호로 따라가고, 없어진 상품의 것은 치운다(다른 상품에 붙지 않게). 주문은 그대로 남는다."""
    if not os.path.exists(DB):
        print('아직 자료가 없습니다(가게를 한 번 켜면 생깁니다).'); return 0
    P = json.load(open(os.path.join(API, 'data', 'products.json'), encoding='utf-8'))['products']
    c = sqlite3.connect(DB)
    old = {r[0]: r[1] for r in c.execute('select id, name from products')}
    c.execute('delete from products')
    for x in P:
        c.execute('insert into products(name,cat,price,was,emoji,color,desc,badge,stock) values(?,?,?,?,?,?,?,?,?)', (x['name'], x['cat'], x['price'], x.get('was') or x['price'], x.get('emoji', '📦'), x.get('color', '#eef2ff'), x.get('desc', ''), x.get('badge', ''), int(x.get('stock', 99))))
    new = {r[1]: r[0] for r in c.execute('select id, name from products')}
    tables = [t for t in ('reviews', 'wish', 'views', 'cart') if c.execute("select name from sqlite_master where name=?", (t,)).fetchone()]
    kept = gone = 0
    for t in tables:
        c.execute(f'update {t} set pid = -pid')   # 번호가 겹치지 않게 잠깐 옮겨 두고
        for oid, name in old.items():
            if name in new:
                kept += c.execute(f'update or ignore {t} set pid=? where pid=?', (new[name], -oid)).rowcount
        gone += c.execute(f'delete from {t} where pid < 0').rowcount
    c.commit(); c.close()
    print(f'상품을 다시 넣었습니다: {len(P)}개. 이름이 그대로인 상품의 상품평·찜은 따라갔고({kept}건), 없어진 상품의 것은 치웠습니다({gone}건). 주문은 그대로입니다.' + (' 켜져 있는 가게는 새로 열면 반영됩니다.' if alive('http://127.0.0.1:8787/api/features') else ''))
    return 0


def main():
    c = A[0] if A else ''
    if c == '붙여' and len(A) > 1:
        return attach(A[1], True)
    if c == '떼' and len(A) > 1:
        return attach(A[1], False)
    if c == '기능':
        return features()
    if c == '켜기':
        return start()
    if c == '끄기':
        return stop()
    if c == '상태':
        return status()
    if c == '시험':
        return subprocess.run([sys.executable, '-X', 'utf8', os.path.join(SHOP, 'smoke.py')]).returncode
    if c == '상품다시':
        return reseed()
    if c == '공유':
        return share()
    if c == '품절':
        return soldout()
    if c == '홍보':
        return promo()
    print(__doc__); return 1


if __name__ == '__main__':
    sys.exit(main())
