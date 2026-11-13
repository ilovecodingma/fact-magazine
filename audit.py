# -*- coding: utf-8 -*-
"""점검(상태 키트): 빌드된 사이트(docs/)를 읽어 문제를 찾는다. 서버·추가 설치 없음.
찾는 것: ① 깨진 내부 링크(없는 쪽·파일) ② 빈 쪽(글자가 거의 없음) ③ 제목·설명 없는 쪽 ④ h1 이 하나가 아닌 쪽 ⑤ 사이트맵에 빠진 쪽(사이트맵이 있을 때)
결과: 화면에 요약 + logs/audit.json (상태 쪽이 읽음) + logs/audit.md.   사용: python audit.py   (먼저 python build.py)
휴대폰 폭에서 넘치는 쪽은 브라우저가 필요해 --mobile 을 줄 때만 본다(Edge·Chrome, 쪽이 많으면 오래 걸림, 최대 40쪽).
사용: python audit.py --mobile"""
import datetime, glob, html, json, os, re, subprocess, sys, urllib.parse
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.abspath(sys.argv[sys.argv.index('--dir') + 1]) if '--dir' in sys.argv else os.path.join(HERE, 'docs')   # --dir site_local : 내 PC 용으로 찍은 폴더를 점검


def site_base():
    S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
    lp = os.path.join(HERE, 'site.local.json')
    if os.path.exists(lp):
        S.update(json.load(open(lp, encoding='utf-8')))
    return os.environ.get('SITE_BASE') or S.get('base', '/')


def exists(path):
    """docs 안에 그 주소의 파일이 있나(폴더면 index.html)."""
    p = os.path.join(DOCS, urllib.parse.unquote(path).lstrip('/'))
    return os.path.isfile(p) or os.path.isfile(os.path.join(p, 'index.html'))


def main():
    if not os.path.isdir(DOCS):
        sys.exit('docs/ 가 없습니다. 먼저 python build.py 를 돌리세요.')
    base = site_base()
    bp = os.path.join(DOCS, '.base')
    built = open(bp, encoding='utf-8').read().strip() if os.path.exists(bp) else None
    if built != base:
        sys.exit(f'docs/ 는 주소 기준 「{built or "알 수 없음"}」 로 찍힌 것이고 지금 설정은 「{base}」 입니다. 이대로 점검하면 거짓 문제가 수천 건 나오니, 먼저 python build.py 로 다시 찍으세요(내 PC 용은 python serve.py).')
    pages = sorted(glob.glob(os.path.join(DOCS, '**', '*.html'), recursive=True))
    pages = [p for p in pages if not p.endswith('print.html')]
    problems = []
    sitemap = ''
    sp = os.path.join(DOCS, 'sitemap.xml')
    if os.path.exists(sp):
        sitemap = open(sp, encoding='utf-8').read()
    for p in pages:
        rel = os.path.relpath(p, DOCS).replace('\\', '/')
        h = open(p, encoding='utf-8').read()
        if re.search(r'name="robots" content="noindex"', h):
            continue   # 검색에 안 나가는 쪽(상태 쪽 등)은 점검 대상에서 뺀다
        if not re.search(r'<title>[^<]{2,}</title>', h):
            problems.append(f'{rel}: 제목 없음')
        if not re.search(r'<meta name="description" content="[^"]{5,}"', h):
            problems.append(f'{rel}: 설명 없음')
        n1 = len(re.findall(r'<h1[\s>]', h))
        if n1 != 1:
            problems.append(f'{rel}: h1 이 {n1}개')
        main_html = re.search(r'<main[^>]*>(.*?)</main>', h, re.S)
        text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', re.sub(r'(?s)<(script|style).*?</\1>', ' ', main_html.group(1) if main_html else h)))
        if len(text.strip()) < 40 and not re.search(r'<(img|canvas|iframe|input)', main_html.group(1) if main_html else ''):   # 그림·게임·영상만 있는 쪽은 비어 있지 않은 것으로 본다

            problems.append(f'{rel}: 빈 쪽(본문 글자 {len(text.strip())}자)')
        if '[확인 필요]' in text or '[미확인]' in text:   # 비워 둔 자리 표시가 그대로 사이트에 실리지 않게
            problems.append(f'{rel}: 「[확인 필요]」 표시가 그대로 남아 있음(채우거나 지우기)')
        for href in re.findall(r'(?:href|src)="([^"#?]+)', re.sub(r'(?s)<script.*?</script>', ' ', h)):   # 스크립트 안의 글자 조각은 링크가 아니다
            if href.startswith(('http', 'mailto:', 'data:', 'javascript:', '/admin/', '/api/')):   # /admin/·/api/ 는 서버(server/app.py)가 내는 주소
                continue
            if href.startswith(base) or (href.startswith('/') and base == '/'):
                target = href[len(base):] if base != '/' else href[1:]
            elif href.startswith('/'):
                problems.append(f'{rel}: 사이트 밖 절대 주소 {href}'); continue
            else:
                target = os.path.normpath(os.path.join(os.path.dirname(rel), href)).replace('\\', '/')
            if target and not exists(target):
                problems.append(f'{rel}: 깨진 링크 {href}')
        if sitemap and rel != '404.html':
            loc = ('' if rel == 'index.html' else rel[:-len('index.html')]) if rel.endswith('index.html') else rel
            if loc and f'/{loc}' not in sitemap and not rel.startswith(('games/',)) and 'status/' not in rel:
                problems.append(f'{rel}: 사이트맵에 없음')
    at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    os.makedirs(os.path.join(HERE, 'logs'), exist_ok=True)
    out = {'at': at, 'pages': len(pages), 'problems': len(problems), 'list': problems}
    json.dump(out, open(os.path.join(HERE, 'logs', 'audit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open(os.path.join(HERE, 'logs', 'audit.md'), 'w', encoding='utf-8').write(f'# 점검 {at}\n\n쪽 {len(pages)}개, 문제 {len(problems)}건\n\n' + ''.join(f'- {x}\n' for x in problems))
    print(f'점검 {at}: 쪽 {len(pages)}개, 문제 {len(problems)}건')
    for x in problems[:25]:
        print('  -', x)
    if '--mobile' in sys.argv:
        mobile(pages[:40])
    return 0


def mobile(pages):
    """휴대폰 폭(390px)에서 가로로 넘치는 쪽 찾기: 브라우저로 열어 scrollWidth 를 본다(가상 시간, 느림)."""
    import shutil, tempfile
    br = next((c for c in [os.environ.get('BROWSER', ''), shutil.which('msedge') or '', r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', shutil.which('chrome') or ''] if c and os.path.exists(c)), None)
    if not br:
        print('  (휴대폰 폭 점검: Edge·Chrome 을 찾지 못해 건너뜀)'); return
    print('  휴대폰 폭 점검은 쪽마다 브라우저를 한 번씩 열어 느립니다(최대 40쪽).')
    for p in pages:
        t = open(p, encoding='utf-8').read() + '<script>document.title="W"+document.documentElement.scrollWidth</script>'
        tmp = os.path.join(tempfile.mkdtemp(), 'x.html'); open(tmp, 'w', encoding='utf-8').write(t)
        r = subprocess.run([br, '--headless=new', '--disable-gpu', '--window-size=390,800', '--virtual-time-budget=2000', '--dump-dom', 'file:///' + tmp.replace('\\', '/')], capture_output=True, text=True, encoding='utf-8', errors='replace')
        m = re.search(r'<title>W(\d+)</title>', r.stdout)
        if m and int(m.group(1)) > 400:
            print(f'  넘침: {os.path.relpath(p, DOCS)} (폭 {m.group(1)}px)')


if __name__ == '__main__':
    sys.exit(main())
