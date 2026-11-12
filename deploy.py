# -*- coding: utf-8 -*-
"""올려: 지금 사이트를 찍어 남에게 보여 줄 수 있는 주소를 받는다(Vercel). 파이썬 기본 기능 + Node.js(npx).
python run.py 올려            로그인 없이도 된다 — 60분 동안 열리는 임시 주소가 바로 나온다. Vercel 에 로그인돼 있으면 사라지지 않는 주소로 올린다.
python run.py 올려 상태       마지막으로 받은 주소와 남은 시간
임시 주소를 계속 쓰려면 출력의 「계속 쓰는 주소」를 브라우저로 열어 가입·로그인한다(그것은 사람이 한다). 그 뒤부터는 같은 명령이 사라지지 않는 주소로 올린다.
2장의 가게는 화면만 이 길로 올라간다(백엔드는 올리기.md)."""
import json, os, re, shutil, subprocess, sys, time, urllib.request
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

if os.name == 'nt':   # 막 깐 Node.js·Git 이 아직 PATH 에 안 잡혔어도 쓰이게
    for _d in (r'C:\Program Files\nodejs', r'C:\Program Files\Git\cmd'):
        if os.path.isdir(_d) and _d.lower() not in os.environ.get('PATH', '').lower():
            os.environ['PATH'] = _d + os.pathsep + os.environ.get('PATH', '')
HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, 'dist_deploy'); PROG = os.path.join(HERE, '진도.json')
A = sys.argv[1:]


def prog():
    return json.load(open(PROG, encoding='utf-8')) if os.path.exists(PROG) else {'done': [], 'last': ''}


def npx(args, cwd, timeout=300):
    r = subprocess.run('npx --yes vercel ' + args, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
    return r.returncode, (r.stdout or '') + '\n' + (r.stderr or '')


def opens(url):
    for _ in range(6):
        try:
            if urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15).status == 200:
                return True
        except Exception:
            time.sleep(3)
    return False


def state():
    d = prog().get('deploy')
    if not d:
        print('아직 올린 적이 없습니다. python run.py 올려'); return 0
    left = (d.get('expires', 0) - time.time()) / 60 if d.get('temp') else None
    print(f'주소: {d["url"]}' + (f'  (임시 — {"%.0f분 남음" % left if left > 0 else "사라졌습니다. 다시 올려 로 새 주소를 받습니다"})' if left is not None else '  (사라지지 않는 주소)'))
    if d.get('claim') and left and left > 0:
        print('계속 쓰는 주소(브라우저로 열어 가입·로그인): ' + d['claim'])
    return 0


def main():
    if A and A[0] == '상태':
        return state()
    if not shutil.which('node'):
        print('✗ 이 PC 에 Node.js 가 없습니다. python run.py 준비 로 점검하고 깔 수 있습니다(독자에게 한 번 묻고). 깐 뒤 다시 「올려」.'); return 1
    t0 = time.time()
    shutil.rmtree(DIST, ignore_errors=True)
    r = subprocess.run([sys.executable, '-X', 'utf8', 'build.py'], cwd=HERE, env=dict(os.environ, OUT_DIR=DIST, SITE_BASE='/'), capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0 or not os.path.exists(os.path.join(DIST, 'index.html')):
        print('✗ 사이트를 찍지 못했습니다:', (r.stderr or r.stdout)[-300:]); return 1
    print('찍었습니다: ' + (r.stdout.strip().splitlines() or [''])[-1].split('->')[0].strip(), flush=True)
    rc, who = npx('whoami', DIST, 90); logged = rc == 0 and 'Logged out' not in who and 'Error' not in who
    print('올리는 중…' + (' (Vercel 에 로그인돼 있어 사라지지 않는 주소로)' if logged else ' (로그인 없이 임시 주소로)'), flush=True)
    rc, out = npx('deploy --prod --yes' if logged else 'deploy --temporary --yes', DIST)
    if logged:
        m = re.findall(r'https://[a-z0-9.-]+\.vercel\.app', out); url = m[-1] if m else ''; claim = ''; exp = 0
    else:
        m = re.search(r'([a-z0-9-]+\.tmp\.now)', out); url = 'https://' + m.group(1) if m else ''
        c = re.search(r'https://vercel\.com/claim-deployment\?code=[0-9a-f-]+', out); claim = c.group(0) if c else ''
        e = re.search(r'"expiresAt":\s*(\d+)', out); exp = int(e.group(1)) / 1000 if e else time.time() + 3600
    if not url:
        print('✗ 주소를 받지 못했습니다. 나온 말의 끝:\n' + out.strip()[-500:]); return 1
    ok = opens(url + '/')
    d = prog(); d['deploy'] = dict(url=url, temp=not logged, claim=claim, expires=exp, t=time.strftime('%Y-%m-%d %H:%M'))
    d['done'].append({'t': time.strftime('%Y-%m-%d %H:%M'), 'what': '올림: ' + url}); d['last'] = '올림: ' + url
    json.dump(d, open(PROG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\n{"✓" if ok else "✗"} 올렸습니다 — {time.time() - t0:.0f}초' + ('' if ok else ' (주소는 받았지만 아직 열리지 않습니다. 잠시 뒤 다시 열어 보세요)'))
    print('┌─ 남에게 보여 줄 주소 ' + '─' * 32)
    print('│ ' + url)
    if not logged:
        print(f'│ 지금부터 {max(0, (exp - time.time()) / 60):.0f}분 동안 누구나 열 수 있습니다(휴대폰으로도).')
        print('│ 사라지지 않게 계속 쓰려면 아래 주소를 브라우저로 열어 가입·로그인하세요.')
        print('│ ' + claim)
    print('└' + '─' * 52)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
