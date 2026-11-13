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
def _slug():
    try:
        s = str(json.load(open(os.path.join(HERE, 'site.local.json'), encoding='utf-8')).get('slug') or '')
    except Exception:
        s = ''
    s = re.sub(r'[^a-z0-9-]+', '-', s.lower()).strip('-')[:40]
    return s or 'my-site'


import hashlib as _h, tempfile as _t
ROOT = os.path.join(_t.gettempdir(), 'site_deploy_' + _h.md5(HERE.encode('utf-8')).hexdigest()[:8]); DIST = os.path.join(ROOT, _slug()); PROG = os.path.join(HERE, '진도.json')
A = sys.argv[1:]


def prog():
    return json.load(open(PROG, encoding='utf-8')) if os.path.exists(PROG) else {'done': [], 'last': ''}


def npx(args, cwd, timeout=150):
    """Vercel 도구를 돌린다. 멈춰 서면(응답 없음) 기다리지 않고 끊어, 부른 쪽이 다시 시도하거나 실패를 말하게 한다."""
    cmd = 'npx --yes vercel ' + args + (' ' + os.environ['VERCEL_ARGS'] if os.environ.get('VERCEL_ARGS') else '')   # VERCEL_ARGS: 시험할 때 덧붙이는 옵션
    p = subprocess.Popen(cmd, cwd=cwd, shell=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
    try:
        out, _ = p.communicate(timeout=timeout); return p.returncode, out or ''
    except subprocess.TimeoutExpired:
        if os.name == 'nt':   # 자식 프로세스까지 함께 끈다
            subprocess.run(['taskkill', '/PID', str(p.pid), '/T', '/F'], capture_output=True)
        else:
            p.kill()
        try:
            p.communicate(timeout=10)
        except Exception:
            pass
        return 124, f'(응답이 없어 {timeout}초 뒤에 끊었습니다)'


def sitemap(base):
    """올릴 사본의 페이지 주소를 모아 sitemap.xml 을 쓰고 robots.txt 에 그 자리를 적는다(검색 사이트가 내 글을 찾아가는 목록). 임시 주소에는 만들지 않는다."""
    urls = []
    for root, ds, fs in os.walk(DIST):
        ds[:] = [x for x in ds if not x.startswith('.')]
        if 'index.html' in fs:
            rel = os.path.relpath(root, DIST).replace(os.sep, '/')
            urls.append(base.rstrip('/') + '/' + ('' if rel == '.' else rel + '/'))
    urls.sort(key=lambda u: (u.count('/'), u))
    if not urls:
        return 0
    open(os.path.join(DIST, 'sitemap.xml'), 'w', encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{u}</loc></url>' for u in urls) + '</urlset>')
    open(os.path.join(DIST, 'robots.txt'), 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\nSitemap: {base.rstrip("/")}/sitemap.xml\n')
    return len(urls)


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
    print(f'주소: {d["url"]}' + (f'  (임시 — {"%.0f분 남음" % left if left > 0 else "사라졌습니다. 다시 올려 로 새 주소를 받습니다"})' if left is not None else '  (고정 주소)'))
    if d.get('claim') and left and left > 0:
        print('계속 쓰는 주소(브라우저로 열어 가입·로그인): ' + d['claim'])
    return 0


def ascii_names(DIST, quiet=False):
    """한글 같은 영어 밖 글자가 든 파일·폴더 이름을 영어 이름으로 바꾸고, 화면 안의 링크도 같이 고친다. 바꾼 개수를 돌려준다(배포·앱이 함께 쓴다)."""
    # 한글 같은 영어 밖 글자가 든 파일·폴더 이름은 로그인 없는 올리기가 거절한다 — 올릴 사본에서만 영어 이름으로 바꾸고 화면 안의 링크도 같이 고친다
    import hashlib, urllib.parse
    ren = {}
    for root, ds, fs in os.walk(DIST, topdown=False):
        for n in fs + ds:
            if any(ord(ch) > 127 for ch in n):
                stem, ext = os.path.splitext(n)
                new = 'k' + hashlib.md5(n.encode('utf-8')).hexdigest()[:10] + (ext if all(ord(ch) < 128 for ch in ext) else '')
                os.rename(os.path.join(root, n), os.path.join(root, new)); ren[n] = new
    if ren:
        keys = sorted(ren, key=len, reverse=True)
        for root, _, fs in os.walk(DIST):
            for f in fs:
                if f.rsplit('.', 1)[-1].lower() in ('html', 'css', 'js', 'json', 'xml', 'txt', 'webmanifest', 'svg'):
                    fp = os.path.join(root, f)
                    try:
                        t = open(fp, encoding='utf-8').read()
                    except Exception:
                        continue
                    t2 = t
                    for k in keys:
                        for old in ('/' + k, '/' + urllib.parse.quote(k), '/' + urllib.parse.quote(k).lower()):
                            t2 = t2.replace(old + '"', '/' + ren[k] + '"').replace(old + "'", '/' + ren[k] + "'").replace(old + '/', '/' + ren[k] + '/').replace(old + ')', '/' + ren[k] + ')').replace(old + '?', '/' + ren[k] + '?').replace(old + '#', '/' + ren[k] + '#').replace(old + ' ', '/' + ren[k] + ' ')
                    if t2 != t:
                        open(fp, 'w', encoding='utf-8', newline='').write(t2)
        if not quiet:
            print(f'(이름에 한글이 든 파일·폴더 {len(ren)}개는 배포할 사본에서 영어 이름으로 바꿨습니다)', flush=True)
    return len(ren)


def main():
    if A and A[0] == '상태':
        return state()
    if not shutil.which('node'):
        print('✗ 이 PC 에 Node.js 가 없습니다. python run.py 준비 가 점검하고 깝니다. 깐 뒤 다시 「올려」.'); return 1
    t0 = time.time()
    keep = os.path.join(ROOT, '_vercel_' + _slug())   # 어느 프로젝트로 올렸는지 적힌 폴더(.vercel)는 남겨서 같은 주소로 다시 올라가게 한다
    if os.path.isdir(os.path.join(DIST, '.vercel')):
        shutil.rmtree(keep, ignore_errors=True); shutil.move(os.path.join(DIST, '.vercel'), keep)
    shutil.rmtree(DIST, ignore_errors=True); os.makedirs(ROOT, exist_ok=True)
    shutil.rmtree(os.path.join(HERE, 'dist_deploy'), ignore_errors=True)   # 예전 판이 저장소 안에 남긴 사본
    r = subprocess.run([sys.executable, '-X', 'utf8', 'build.py'], cwd=HERE, env=dict(os.environ, OUT_DIR=DIST, SITE_BASE='/'), capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0 or not os.path.exists(os.path.join(DIST, 'index.html')):
        print('✗ 빌드 실패:', (r.stderr or r.stdout)[-300:]); return 1
    print('빌드했습니다: ' + (r.stdout.strip().splitlines() or [''])[-1].split('->')[0].strip(), flush=True)
    if os.path.isdir(keep):
        shutil.rmtree(os.path.join(DIST, '.vercel'), ignore_errors=True); shutil.move(keep, os.path.join(DIST, '.vercel'))
    for root, _, fs in os.walk(DIST):   # 빈 파일이 하나라도 있으면 로그인 없는 올리기가 거절된다(크기 0) — 한 글자를 넣어 둔다
        for f in fs:
            fp = os.path.join(root, f)
            if os.path.getsize(fp) == 0:
                open(fp, 'w').write(' ')
    ascii_names(DIST)
    apk = os.path.join(HERE, 'android_app', 'out', 'app.apk')
    if os.path.exists(apk):   # 앱을 만들어 두었으면 내려받기 화면과 APK 를 사이트의 /app/ 에 같이 올린다
        os.makedirs(os.path.join(DIST, 'app'), exist_ok=True); shutil.copyfile(apk, os.path.join(DIST, 'app', 'app.apk'))
        pg = os.path.join(HERE, 'android_app', 'out', 'app', 'index.html')
        if os.path.exists(pg):
            shutil.copyfile(pg, os.path.join(DIST, 'app', 'index.html'))
        print('앱(APK)과 내려받기 화면을 /app/ 에 같이 올립니다', flush=True)
    rc, who = npx('whoami', DIST, 90); logged = rc == 0 and 'Logged out' not in who and 'Error' not in who
    link = os.path.join(DIST, '.vercel'); mode = 'in' if logged else 'out'; mf = os.path.join(link, '_mode.txt')
    if os.path.isdir(link) and (open(mf, encoding='utf-8').read().strip() if os.path.exists(mf) else '') != mode:
        shutil.rmtree(link, ignore_errors=True)   # 로그인 상태가 바뀌었으면 예전에 이어 둔 기록은 쓸 수 없다(그대로 두면 배포가 멈춰 선다)
    print('배포하는 중…' + (' (Vercel 에 로그인돼 있어 고정 주소로)' if logged else ' (로그인 없이 임시 배포로)'), flush=True)
    prev = (prog().get('deploy') or {})
    known = prev.get('url', '') if logged and not prev.get('temp') and prev.get('slug') == _slug() else ''
    if known:
        sitemap(known)
    rc, out = npx('deploy --prod --yes' if logged else 'deploy --temporary --yes', DIST)
    if rc != 0 and 'vercel.app' not in out and 'tmp.now' not in out and os.path.isdir(os.path.join(DIST, '.vercel')):   # 예전에 이어 둔 프로젝트가 계정에서 지워졌다: 이은 기록을 버리고 새로 올린다
        shutil.rmtree(os.path.join(DIST, '.vercel'), ignore_errors=True); known = ''
        rc, out = npx('deploy --prod --yes' if logged else 'deploy --temporary --yes', DIST)
    if logged:
        m = re.findall(r'https://[a-z0-9.-]+\.vercel\.app', out); url = m[-1] if m else ''; claim = ''; exp = 0
    else:
        m = re.search(r'([a-z0-9-]+\.tmp\.now)', out); url = 'https://' + m.group(1) if m else ''
        c = re.search(r'https://vercel\.com/claim-deployment\?code=[0-9a-f-]+', out); claim = c.group(0) if c else ''
        e = re.search(r'"expiresAt":\s*(\d+)', out); exp = int(e.group(1)) / 1000 if e else time.time() + 3600
    if not url:
        try:
            import cases; cases.mark('deploy.fail')
        except Exception:
            pass
        print('✗ 배포 실패 — 주소를 받지 못했습니다. 나온 말의 끝:\n' + out.strip()[-500:]); return 1
    if logged and not known:   # 사라지지 않는 주소를 방금 처음 알았다: 주소 목록 파일을 만들어 한 번 더 올린다(다음부터는 한 번에)
        n = sitemap(url)
        if n:
            npx('deploy --prod --yes', DIST)
    try:
        os.makedirs(os.path.join(DIST, '.vercel'), exist_ok=True); open(os.path.join(DIST, '.vercel', '_mode.txt'), 'w', encoding='utf-8').write('in' if logged else 'out')
    except Exception:
        pass
    ok = opens(url + '/')
    d = prog(); d['deploy'] = dict(url=url, slug=_slug(), temp=not logged, claim=claim, expires=exp, t=time.strftime('%Y-%m-%d %H:%M'))
    d['done'].append({'t': time.strftime('%Y-%m-%d %H:%M'), 'what': '올림: ' + url}); d['last'] = '올림: ' + url
    json.dump(d, open(PROG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\n{"✓" if ok else "✗"} 배포했습니다 — {time.time() - t0:.0f}초' + ('' if ok else ' (주소는 받았지만 아직 열리지 않습니다. 잠시 뒤 다시 열어 보세요)'))
    print('┌─ 남에게 보여 줄 주소 ' + '─' * 32)
    print('│ ' + url)
    if not logged:
        print(f'│ 임시 배포입니다 — 지금부터 {max(0, (exp - time.time()) / 60):.0f}분 동안 누구나 열 수 있습니다(휴대폰으로도).')
        print('│ 고정 주소로 계속 쓰려면 아래 주소를 브라우저로 열어 가입·로그인하세요.')
        print('│ ' + claim)
    print('└' + '─' * 52)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
