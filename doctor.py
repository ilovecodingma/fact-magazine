# -*- coding: utf-8 -*-
"""환경 점검 + 키트 전부 한 번씩 찍어 보기 + 「기능 점검표」 만들기. 파이썬 기본 기능만 쓴다.
사용: python doctor.py              환경 점검 → 키트마다 한 번씩 찍어 → 점검표(기능_점검표.md)
      python doctor.py --env        환경 점검만
      python doctor.py --quick      키트 찍기만 빠르게(영상·네트워크가 필요한 것은 건너뜀)
설명: 점검은 공개 주소·GitHub·로그인 없이 내 컴퓨터 안에서만 한다(내 사이트 설정 site.local.json 은 쓰지 않고 키트만 따로 찍는다). 없는 도구는 설치 방법만 알려 주고 그 키트는 「건너뜀」으로 적는다.
점검표 칸: 키트 이름 · 결과(됨 / 안 됨 / 건너뜀) · 이유."""
import glob, json, os, platform, re, shutil, subprocess, sys, tempfile, time, urllib.request
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ARGS = sys.argv[1:]
PY = [sys.executable, '-X', 'utf8']
OKS = []   # (키트, 결과, 이유)


def find_browser():
    c = [os.environ.get('BROWSER', ''), shutil.which('msedge') or '', shutil.which('chrome') or '', shutil.which('google-chrome') or '', shutil.which('chromium') or '',
         r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Google\Chrome\Application\chrome.exe',
         '/usr/bin/google-chrome', '/usr/bin/chromium', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    return next((x for x in c if x and os.path.exists(x)), None)


def env_check():
    """필요한 것이 있는지 본다. 없는 것은 설치 방법을 알려 준다."""
    r = {}
    r['python'] = (sys.version_info >= (3, 9), f'Python {platform.python_version()}', '파이썬 3.9 이상이 필요합니다(python.org 에서 설치).')
    g = shutil.which('git')
    r['git'] = (bool(g), 'git 있음' if g else 'git 없음', '저장소 받기·올리기에 필요합니다. 윈도우 `winget install Git.Git`, 맥 `brew install git`, 리눅스 `sudo apt install git`.')
    b = find_browser()
    r['browser'] = (bool(b), os.path.basename(b) if b else '브라우저 없음', 'Edge 또는 Chrome 이 필요합니다(PDF·카드 그림·쇼츠). 환경변수 BROWSER 에 실행 파일 경로를 줄 수도 있습니다.')
    f = os.environ.get('FFMPEG') or shutil.which('ffmpeg')
    r['ffmpeg'] = (bool(f), 'ffmpeg 있음' if f else 'ffmpeg 없음', '쇼츠 영상에 필요합니다. 윈도우 `winget install Gyan.FFmpeg`, 맥 `brew install ffmpeg`, 리눅스 `sudo apt install ffmpeg`(이미 있으면 환경변수 FFMPEG 에 경로).')
    try:
        net = False
        for u in ('https://www.google.com/', 'https://example.com/', 'https://www.korea.kr/'):   # 하나라도 열리면 인터넷이 되는 것
            try:
                urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (doctor)'}), timeout=8)
                net = True
                break
            except Exception:
                continue
    except Exception:
        net = False
    r['internet'] = (net, '인터넷 됨' if net else '인터넷 안 됨', '뉴스 수집·날씨·링크 점검에 필요합니다(없으면 그 키트는 건너뜀).')
    print('== 환경 점검 ==')
    for k, (ok, msg, how) in r.items():
        print(f'  {"✔" if ok else "✘"} {k:9} {msg}' + ('' if ok else f'\n      → {how}'))
    return r


def run(cmd, env=None, timeout=240):
    e = dict(os.environ, **(env or {}))
    p = subprocess.run(cmd, cwd=HERE, env=e, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
    return p.returncode, (p.stdout + p.stderr)


def page_count(out):
    m = re.search(r'쪽 (\d+)개', out)
    return int(m.group(1)) if m else 0


def main():
    env = env_check()
    if '--env' in ARGS:
        return
    kits = [json.load(open(p, encoding='utf-8')) for p in sorted(glob.glob(os.path.join(HERE, 'kits', '*', 'kit.json')))]
    S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
    allparts = list(S['parts'])
    tmp = tempfile.mkdtemp(prefix='doctor_')
    base_env = dict(SITE_BASE='/', SITE_URL='https://프로젝트이름.localhost', SITE_EXTRAS='{}', TOPIC_KEYWORDS='')
    print('\n== 키트 점검(하나씩 켜서 찍어 보기) ==')
    t0 = time.time()
    rc, out = run(PY + ['build.py'], dict(base_env, PARTS=json.dumps({k: False for k in allparts}), OUT_DIR=os.path.join(tmp, 'base')))
    n0 = page_count(out)
    for k in kits:
        name, parts = k['name'], k.get('parts', [])
        need_browser = name in ('issue', 'ebook', 'onepage', 'pdf', 'cards', 'shorts', 'promo-blog') and False
        res, why = None, ''
        # 1) 켤 부품이 없는 키트 = 내 컴퓨터에서 실행하는 도구
        if not parts:
            if name.startswith(('keyword-', 'content-', 'promo-')):
                res, why = '건너뜀', '내 컴퓨터에서 실행하는 도구(일부는 바깥 서비스에 요청) — 점검표에서는 실행하지 않음. README 의 「이렇게 입력하세요」로 직접 해 보세요.'
            else:
                res, why = '건너뜀', '켤 부품이 없는 도구'
        elif name == 'inbox':
            res, why = '건너뜀', '메일 읽기(IMAP) 설정이 있어야 합니다(사람 몫, mail.local.json). 화면이 없는 도구라 실행하지 않음.'
        else:
            # 2) 브라우저·ffmpeg 가 필요한 키트는 도구가 없으면 건너뜀
            if name == 'video':
                res, why = '건너뜀', '내 유튜브 영상 주소(site.local.json 의 extras.videos)가 있어야 쪽이 생김 — 사람이 넣는 값'
            elif name in ('issue', 'ebook', 'pdf', 'onepage', 'cards') and not env['browser'][0]:
                res, why = '건너뜀', '브라우저(Edge·Chrome)가 없어 PDF·그림을 만들 수 없음 — ' + env['browser'][2]
            elif name == 'shorts' and not (env['browser'][0] and env['ffmpeg'][0]):
                res, why = '건너뜀', '쇼츠는 브라우저와 ffmpeg 가 모두 필요함 — ' + (env['ffmpeg'][2] if not env['ffmpeg'][0] else env['browser'][2])
            elif name in ('news', 'today', 'trends') and not env['internet'][0]:
                res, why = '건너뜀', '인터넷이 필요함'
        if res is None:
            op = dict(base_env, PARTS=json.dumps({p: (p in parts) for p in allparts}), OUT_DIR=os.path.join(tmp, name))
            if name == 'demo':
                op['PARTS'] = json.dumps({p: (p in ('demo',)) for p in allparts})
            try:
                rc, out = run(PY + ['build.py'], op)
                n = page_count(out)
                if rc != 0:
                    res, why = '안 됨', '빌드가 실패함: ' + out.strip().splitlines()[-1][:120]
                elif n > n0 or name in ('notfound', 'prefs', 'related', 'readtime', 'tags', 'ebook', 'issue', 'news', 'status', 'demo', 'cards', 'onepage', 'pdf', 'shorts', 'mail'):
                    res, why = '됨', f'쪽 {n}개를 찍음(키트 없이 {n0}개)'
                else:
                    res, why = '안 됨', f'쪽이 늘지 않음({n}개) — 자료 파일이 비었거나 부품이 켜지지 않음'
            except Exception as e:
                res, why = '안 됨', '실행 중 오류: ' + repr(e)[:100]
        # 3) 실행 스크립트가 있는 키트는 한 번 더 시험(도구가 있을 때만)
        if res == '됨' and '--quick' not in ARGS:
            script = {'cards': ['card.py'], 'onepage': ['onepage.py'], 'pdf': ['pdf.py'], 'ebook': ['ebook.py'], 'mail': ['mail.py'], 'promo': ['promo.py'], 'issue': ['issue.py']}.get(name)
            if script and os.path.exists(os.path.join(HERE, script[0])):
                try:
                    rc, out = run(PY + script, timeout=300)
                    if rc != 0:
                        res, why = '안 됨', f'{script[0]} 실행 실패: ' + out.strip().splitlines()[-1][:120]
                    else:
                        why += f' · {script[0]} 도 돌아감'
                except Exception as e:
                    res, why = '안 됨', f'{script[0]} 오류: ' + repr(e)[:80]
            if name == 'shorts':
                notes = [p for p in sorted(glob.glob(os.path.join(HERE, 'notes', '*.json'))) if not json.load(open(p, encoding='utf-8')).get('example')]
                if notes:
                    try:
                        rc, out = run(PY + ['shorts.py', notes[0]], timeout=300)
                        res, why = ('됨', why + ' · 쇼츠 한 편 만들어짐') if rc == 0 else ('안 됨', 'shorts.py 실패: ' + out.strip().splitlines()[-1][:120])
                    except Exception as e:
                        res, why = '안 됨', 'shorts.py 오류: ' + repr(e)[:80]
                else:
                    why += ' · 노트가 없어 영상은 안 만들어 봄'
        OKS.append((name, res, why))
        print(f'  {"✔" if res == "됨" else ("–" if res == "건너뜀" else "✘")} {name:22} {res:4} {why[:100]}')
    shutil.rmtree(tmp, ignore_errors=True)
    ok = sum(1 for _, r, _ in OKS if r == '됨'); sk = sum(1 for _, r, _ in OKS if r == '건너뜀'); bad = sum(1 for _, r, _ in OKS if r == '안 됨')
    md = ['# 기능 점검표', '', f'점검 시각: {time.strftime("%Y-%m-%d %H:%M")} · 키트 {len(OKS)}개 중 **됨 {ok} / 건너뜀 {sk} / 안 됨 {bad}** · 걸린 시간 {round(time.time() - t0)}초', '',
          '## 환경', ''] + [f'- {"✔" if v[0] else "✘"} {k}: {v[1]}' + ('' if v[0] else f' — {v[2]}') for k, v in env.items()] + ['', '## 키트', '', '| 키트 | 결과 | 이유 |', '|---|---|---|'] + [f'| {n} | {r} | {w.replace("|", "/")} |' for n, r, w in OKS]
    open(os.path.join(HERE, '기능_점검표.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(f'\n점검표: 됨 {ok} · 건너뜀 {sk} · 안 됨 {bad} → 기능_점검표.md ({round(time.time() - t0)}초)')
    if bad:
        print('※ 「안 됨」은 이유를 보고 고치거나 그 키트를 건너뛰세요.')


if __name__ == '__main__':
    main()
