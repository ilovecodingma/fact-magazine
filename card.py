# -*- coding: utf-8 -*-
"""카드 그림 만들기(cards 키트): 확인 노트 → 공유용 그림 한 장(1200x630, 도형과 글자만). 결과: cards/<노트 id>.svg 와 .png (png 는 브라우저로 찍음 — Edge·Chrome 필요).
사용: python card.py            모든 노트(예시 제외)
      python card.py notes/노트.json
그다음 python build.py 를 돌리면(parts.cards) /cards/ 에 내려받기 쪽이 생긴다."""
import glob, html, json, os, re, shutil, subprocess, sys, tempfile
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__)); E = html.escape
COL = {'확인됨': '#0b5d2f', '일부만 확인됨': '#8a4b00', '아직 확인 안 됨': '#a11a12'}


def site_name():
    S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
    lp = os.path.join(HERE, 'site.local.json')
    if os.path.exists(lp):
        S.update(json.load(open(lp, encoding='utf-8')))
    return os.environ.get('SITE_NAME') or S['name']


def wrap(t, n):
    """한 줄에 n 글자 안팎으로 나눈다(공백이 있으면 거기서)."""
    out, cur = [], ''
    for w in t.split(' '):
        if len(cur) + len(w) + 1 > n and cur:
            out.append(cur); cur = w
        else:
            cur = (cur + ' ' + w).strip()
    return out + [cur] if cur else out


def svg(n, name):
    col = COL.get(n['verdict'], '#111')
    num = re.search(r'\d[\d,.]*\s?(?:억|만|천|%p|%|원|명|달러)', n['title'])   # 단위가 붙은 첫 숫자(날짜의 숫자는 피함)
    lines = wrap(n['title'], 22)[:4]
    ty = 270
    tt = ''.join(f'<text x="70" y="{ty + i * 62}" font-size="52" font-weight="800">{E(l)}</text>' for i, l in enumerate(lines))
    big = f'<text x="1130" y="560" text-anchor="end" font-size="110" font-weight="900" fill="{col}">{E(num.group(0).strip())}</text>' if num else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630" font-family="\'Noto Serif KR\',\'Nanum Myeongjo\',Batang,serif">'
            f'<rect width="1200" height="630" fill="#fff"/><rect x="14" y="14" width="1172" height="602" fill="none" stroke="#111" stroke-width="6"/><rect x="26" y="26" width="1148" height="578" fill="none" stroke="#111" stroke-width="2"/>'
            f'<text x="70" y="90" font-size="30" font-weight="900" letter-spacing="2">{E(name)}</text><line x1="70" y1="112" x2="1130" y2="112" stroke="#111" stroke-width="3"/>'
            f'<rect x="70" y="140" width="{40 + 28 * len(n["verdict"])}" height="48" fill="none" stroke="{col}" stroke-width="3"/><text x="90" y="174" font-size="26" font-weight="800" fill="{col}" font-family="system-ui,Malgun Gothic,sans-serif">{E(n["verdict"])}</text>'
            f'{tt}{big}<text x="70" y="580" font-size="24" fill="#555" font-family="system-ui,Malgun Gothic,sans-serif">공식 자료로 한 번 더 확인합니다 · {E(n["date"])}</text></svg>')


def browser():
    c = [os.environ.get('BROWSER', ''), shutil.which('msedge') or '', shutil.which('chrome') or '', r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Google\Chrome\Application\chrome.exe', '/usr/bin/google-chrome', '/usr/bin/chromium']
    return next((x for x in c if x and os.path.exists(x)), None)


def main():
    paths = [a for a in sys.argv[1:] if a.endswith('.json')] or [p for p in sorted(glob.glob(os.path.join(HERE, 'notes', '*.json'))) if not json.load(open(p, encoding='utf-8')).get('example')]
    os.makedirs(os.path.join(HERE, 'cards'), exist_ok=True); br = browser(); name = site_name()
    for p in paths:
        n = json.load(open(p, encoding='utf-8')); out = os.path.join(HERE, 'cards', n['id'])
        s = svg(n, name); open(out + '.svg', 'w', encoding='utf-8').write(s)
        if br:
            tmp = os.path.join(tempfile.mkdtemp(), 'c.html'); open(tmp, 'w', encoding='utf-8').write('<!doctype html><body style="margin:0">' + s)
            subprocess.run([br, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1200,630', '--screenshot=' + out + '.png', 'file:///' + tmp.replace(chr(92), '/')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        print('만듦:', n['id'], '(png 도)' if os.path.exists(out + '.png') else '(svg 만 — 브라우저를 못 찾음)')
    print('python build.py 를 다시 돌리면 /cards/ 에 내려받기가 생깁니다.')


if __name__ == '__main__':
    main()
