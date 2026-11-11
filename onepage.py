# -*- coding: utf-8 -*-
"""한 장 요약 인쇄(onepage 키트): 글·확인 노트 → A4 한 장 점검표 PDF(핵심 세 줄 + 체크칸). 브라우저 인쇄 기능을 쓰므로 추가 설치 없음. 결과: onepage/<이름>.pdf
사용: python onepage.py        글(posts/*.md)과 노트(notes/*.json, 예시 제외) 모두
그다음 python build.py 를 돌리면(parts.onepage) /onepage/ 에 내려받기가 생긴다."""
import glob, html, json, os, re, shutil, subprocess, sys, tempfile
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); E = html.escape
CSS = ('@page{size:A4;margin:16mm}body{font:11pt/1.7 "Noto Serif KR","Nanum Myeongjo",Batang,serif;color:#111}h1{font-size:19pt;border-bottom:3px double #111;padding-bottom:3mm;margin:0 0 5mm}'
       'h2{font-size:12pt;border-top:2px solid #111;padding-top:2mm;margin:6mm 0 2mm}li{margin:2mm 0}.k{list-style:none;padding-left:0}.k li:before{content:"\\2610  "}')


def browser():
    c = [os.environ.get('BROWSER', ''), shutil.which('msedge') or '', shutil.which('chrome') or '', r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Google\Chrome\Application\chrome.exe', '/usr/bin/google-chrome', '/usr/bin/chromium']
    b = next((x for x in c if x and os.path.exists(x)), None)
    if not b:
        sys.exit('Edge 또는 Chrome 을 찾지 못했습니다. 환경변수 BROWSER 에 경로를 주세요.')
    return b


def pdf(name, title, three, checks):
    doc = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>{CSS}</style></head><body><h1>{E(title)}</h1><h2>핵심 세 줄</h2><ol>' + ''.join(f'<li>{E(x)}</li>' for x in three[:3]) +
           '</ol><h2>점검표</h2><ul class="k">' + ''.join(f'<li>{E(x)}</li>' for x in checks[:12]) + '</ul></body></html>')
    tmp = os.path.join(tempfile.mkdtemp(), 'p.html'); open(tmp, 'w', encoding='utf-8').write(doc)
    out = os.path.join(HERE, 'onepage', name + '.pdf')
    subprocess.run([browser(), '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--print-to-pdf=' + out, 'file:///' + tmp.replace(chr(92), '/')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    print('만듦:' if os.path.exists(out) and os.path.getsize(out) > 800 else '실패:', name)


def main():
    import build as B
    os.makedirs(os.path.join(HERE, 'onepage'), exist_ok=True)
    for p in sorted(glob.glob(os.path.join(HERE, 'notes', '*.json'))):
        n = json.load(open(p, encoding='utf-8'))
        if n.get('example'):
            continue
        pdf(n['id'], n['title'], [n['question'], n['summary'], '판정: ' + n['verdict']], [f['text'] for f in n.get('facts', [])] + ['아직 확인 안 된 것: ' + x for x in n.get('unconfirmed', [])])
    for f in sorted(glob.glob(os.path.join(B.DATA_ROOT, 'posts', '*.md'))):
        t = open(f, encoding='utf-8').read(); slug = os.path.splitext(os.path.basename(f))[0]
        paras = [x.strip() for x in re.sub(r'^#.*$', '', t, flags=re.M).split('\n\n') if x.strip() and not x.startswith(('|', '-'))]
        heads = re.findall(r'^#{2,3} (.+)$', t, re.M)
        pdf(slug, B.first_h1(t, slug), [re.split(r'(?<=[.!?다])\s', p, 1)[0] for p in paras[:3]], heads or ['본문을 읽고 확인하기'])
    print('python build.py 를 다시 돌리면 /onepage/ 에 내려받기가 생깁니다.')


if __name__ == '__main__':
    main()
