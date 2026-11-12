# -*- coding: utf-8 -*-
"""가게(2장): 종합 쇼핑몰을 본뜬 템플릿 — 화면은 Next.js(shop/web), 백엔드는 파이썬(shop/api, 기능 묶음을 붙였다 뗐다), 휴대폰에서는 앱으로 깔린다. 결제는 없다.
python run.py 가게 켜기 [--열쇠 <운영자 열쇠>]   백엔드(8787)와 화면(3000)을 내 PC 에서 켠다(처음에는 화면에 필요한 것을 받느라 1~2분)
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
    key = A[A.index('--열쇠') + 1] if '--열쇠' in A and len(A) > A.index('--열쇠') + 1 else os.environ.get('SHOP_ADMIN_KEY', '')
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
        print('가게: http://127.0.0.1:3000/   운영자: http://127.0.0.1:3000/admin' + ('' if key else ' (운영자 열쇠를 정하지 않아 운영자 화면은 잠겨 있습니다 — 가게 켜기 --열쇠 <정한 말>)') + '\n휴대폰에서는 같은 와이파이로 이 PC 의 주소를 열고 「홈 화면에 추가」 하면 앱으로 깔립니다(올린 뒤에는 그 주소에서).')
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


def reseed():
    if not os.path.exists(DB):
        print('아직 자료가 없습니다(가게를 한 번 켜면 생깁니다).'); return 0
    c = sqlite3.connect(DB); c.execute('delete from products'); c.commit(); c.close()
    os.utime(CONF, None)   # 백엔드가 다음 요청에서 다시 읽으며 products.json 을 넣는다
    n = len(json.load(open(os.path.join(API, 'data', 'products.json'), encoding='utf-8'))['products'])
    print(f'상품을 다시 넣습니다: {n}개(주문·상품평은 그대로).'); return 0


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
    print(__doc__); return 1


if __name__ == '__main__':
    sys.exit(main())
