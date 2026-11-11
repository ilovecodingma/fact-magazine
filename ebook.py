# -*- coding: utf-8 -*-
"""전자책 키트: 글(posts/*.md)과 연재 소설(novels/작품/)을 표지·차례가 있는 PDF 한 권으로 묶는다. 브라우저 인쇄 기능을 쓰므로 추가 설치가 없다.
사용: python ebook.py                 ebooks/<사이트이름>-모음.pdf 를 만든다
      python ebook.py --title 책이름   책 제목 바꾸기
그다음 python build.py 를 돌리면 /ebook/ 에 내려받기가 생긴다(site.json 의 parts.ebook 켜기)."""
import glob, html, json, os, re, shutil, subprocess, sys, tempfile
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
E = html.escape


def browser():
    cands = [os.environ.get('BROWSER', ''), shutil.which('msedge') or '', shutil.which('chrome') or '', shutil.which('google-chrome') or '', shutil.which('chromium') or '',
             r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
             r'C:\Program Files\Google\Chrome\Application\chrome.exe', '/usr/bin/google-chrome', '/usr/bin/chromium', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    br = next((c for c in cands if c and os.path.exists(c)), None)
    if not br:
        sys.exit('Edge 또는 Chrome 을 찾지 못했습니다. 환경변수 BROWSER 에 실행 파일 경로를 주세요.')
    return br


def main():
    import build as B   # 마크다운 변환(md)과 사이트 이름을 빌드와 같은 것으로 쓴다(빌드를 실행하지는 않음)
    title = sys.argv[sys.argv.index('--title') + 1] if '--title' in sys.argv else f'{B.S["name"]} 모음'
    chapters = []   # (구분, 제목, 본문 html)
    for f in sorted(glob.glob(os.path.join(B.DATA_ROOT, 'posts', '*.md'))):
        t = open(f, encoding='utf-8').read()
        chapters.append(('글', B.first_h1(t, os.path.basename(f)), B.md(re.sub(r'^# .+\n', '', t, count=1))))
    for nd in sorted(glob.glob(os.path.join(B.DATA_ROOT, 'novels', '*'))):
        if not os.path.isdir(nd):
            continue
        intro = open(os.path.join(nd, '소개.md'), encoding='utf-8').read() if os.path.exists(os.path.join(nd, '소개.md')) else ''
        chapters.append(('연재', B.first_h1(intro, os.path.basename(nd)) + ' — 소개', B.md(re.sub(r'^# .+\n', '', intro, count=1))))
        for f in sorted(glob.glob(os.path.join(nd, '[0-9]*.md'))):
            t = open(f, encoding='utf-8').read()
            chapters.append(('연재', B.first_h1(t, os.path.basename(f)), B.md(re.sub(r'^# .+\n', '', t, count=1))))
    if not chapters:
        sys.exit('묶을 글이 없습니다(posts/·novels/ 에 원고를 넣으세요).')
    toc = ''.join(f'<li>{E(k)} · {E(t)}</li>' for k, t, _ in chapters)
    body = ''.join(f'<section class="ch"><div class="k">{E(k)}</div><h2>{E(t)}</h2>{h}</section>' for k, t, h in chapters)
    doc = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{E(title)}</title><style>@page{{size:A5;margin:16mm 14mm}}'
           'body{font:11pt/1.8 "Noto Serif KR","Nanum Myeongjo",Batang,serif;color:#111}.cover{height:230mm;display:flex;flex-direction:column;justify-content:center;text-align:center;page-break-after:always;border:3px double #111;padding:10mm}'
           '.cover h1{font-size:30pt;margin:0 0 10mm}.cover p{font:11pt sans-serif;color:#555}.toc{page-break-after:always}.toc li{margin:3mm 0}.ch{page-break-before:always}.k{font:9pt sans-serif;color:#666}'
           'h2{font-size:16pt;border-bottom:2px solid #111;padding-bottom:3mm}table{border-collapse:collapse}td{border:1px solid #999;padding:2mm}</style></head>'
           f'<body><div class="cover"><h1>{E(title)}</h1><p>{E(B.S["name"])}</p><p>글 {sum(1 for c in chapters if c[0] == "글")}편 · 연재 {sum(1 for c in chapters if c[0] == "연재")}화</p></div>'
           f'<div class="toc"><h2>차례</h2><ol>{toc}</ol></div>{body}</body></html>')
    os.makedirs(os.path.join(B.DATA_ROOT, 'ebooks'), exist_ok=True)
    tmp = os.path.join(tempfile.mkdtemp(), 'book.html')
    open(tmp, 'w', encoding='utf-8').write(doc)
    out = os.path.join(B.DATA_ROOT, 'ebooks', re.sub(r'[\\/:*?"<>|\s]+', '-', title) + '.pdf')
    subprocess.run([browser(), '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--print-to-pdf=' + out, 'file:///' + tmp.replace('\\', '/')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    if not (os.path.exists(out) and os.path.getsize(out) > 2000):
        sys.exit('PDF 를 만들지 못했습니다.')
    pages = len(re.findall(rb'/Type\s*/Page[^s]', open(out, 'rb').read()))
    print(f'만듦: {out} (약 {pages}쪽, {round(os.path.getsize(out) / 1024)}KB, 글 {sum(1 for c in chapters if c[0] == "글")}편·연재 {sum(1 for c in chapters if c[0] == "연재")}화). python build.py 를 다시 돌리면 /ebook/ 에 내려받기가 생깁니다.')


if __name__ == '__main__':
    main()
