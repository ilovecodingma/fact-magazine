# -*- coding: utf-8 -*-
"""글 → PDF 미리 만들기(pdf 키트): posts/*.md 마다 PDF 를 pdfs/<글>.pdf 로 만든다(내용이 바뀐 글만 다시). 브라우저 인쇄 기능을 쓰므로 추가 설치 없음.
그다음 python build.py 를 돌리면(parts.pdf 켜기) 글 쪽에 「이 글을 PDF 로 내려받기」가 붙는다.   사용: python pdf.py   (--force: 모두 다시)"""
import glob, hashlib, json, os, re, shutil, subprocess, sys, tempfile
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
STATE = os.path.join(HERE, 'data', 'pdf_state.json')


def browser():
    c = [os.environ.get('BROWSER', ''), shutil.which('msedge') or '', shutil.which('chrome') or '', r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Google\Chrome\Application\chrome.exe', '/usr/bin/google-chrome', '/usr/bin/chromium']
    b = next((x for x in c if x and os.path.exists(x)), None)
    if not b:
        sys.exit('Edge 또는 Chrome 을 찾지 못했습니다. 환경변수 BROWSER 에 경로를 주세요.')
    return b


def main():
    import build as B
    st = json.load(open(STATE, encoding='utf-8')) if os.path.exists(STATE) else {}
    os.makedirs(os.path.join(HERE, 'pdfs'), exist_ok=True)
    made = kept = 0
    for f in sorted(glob.glob(os.path.join(HERE, 'posts', '*.md'))):
        slug = os.path.splitext(os.path.basename(f))[0]; t = open(f, encoding='utf-8').read(); h = hashlib.sha256(t.encode()).hexdigest()[:16]
        out = os.path.join(HERE, 'pdfs', slug + '.pdf')
        if st.get(slug) == h and os.path.exists(out) and '--force' not in sys.argv:
            kept += 1; continue
        doc = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>@page{size:A4;margin:18mm}body{font:11.5pt/1.8 "Noto Serif KR","Nanum Myeongjo",Batang,serif}h1{font-size:20pt;border-bottom:2px solid #111;padding-bottom:3mm}table{border-collapse:collapse}td{border:1px solid #999;padding:2mm}</style></head><body>'
               f'<h1>{B.E(B.first_h1(t, slug))}</h1>{B.md(re.sub(chr(94) + "# .+" + chr(10), "", t, count=1))}</body></html>')
        tmp = os.path.join(tempfile.mkdtemp(), 'p.html'); open(tmp, 'w', encoding='utf-8').write(doc)
        subprocess.run([browser(), '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--print-to-pdf=' + out, 'file:///' + tmp.replace(chr(92), '/')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            st[slug] = h; made += 1; print('만듦:', slug)
        else:
            print('실패:', slug)
    os.makedirs(os.path.dirname(STATE), exist_ok=True); json.dump(st, open(STATE, 'w', encoding='utf-8'), indent=1)
    print(f'새로 만든 PDF {made}개, 그대로 둔 것 {kept}개. python build.py 를 다시 돌리세요.')


if __name__ == '__main__':
    main()
