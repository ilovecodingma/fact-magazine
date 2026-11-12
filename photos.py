# -*- coding: utf-8 -*-
"""사진 여러 장을 한꺼번에: 목록대로 한 번에 받고, 받은 사진을 한 장의 「모아 보기」 그림으로 만들어 세션이 한 번에 확인하게 한다. 파이썬 기본 기능만 쓴다.
python photos.py 목록.json            목록의 사진을 한꺼번에 받고 모아 보기 그림을 만든다
python photos.py 목록.json --보기만    받지 않고, 이미 있는 사진으로 모아 보기 그림만 다시 만든다
목록.json 의 모양(세션이 임시로 쓴다):
[{"q": "soap bar", "to": "shop/web/public/p/1.jpg", "square": true, "name": "라벤더 비누"},
 {"q": "camping tent", "to": "posts/_cover/first-night.jpg", "name": "첫 캠핑"}]
모아 보기 그림에서 안 맞는 번호만 python photo.py "<낱말>" <자리> [--square] --pick 2 로 다시 받고, python photos.py 목록.json --보기만 으로 다시 본다.
한 장씩 받고 한 장씩 열어 보는 것보다 훨씬 빠르다(열여섯 장이면 1~2분)."""
import html, json, os, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))


def one(it):
    cmd = [sys.executable, '-X', 'utf8', os.path.join(HERE, 'photo.py'), it['q'], it['to']] + (['--square'] if it.get('square') else []) + (['--pick', str(it['pick'])] if it.get('pick') else [])
    for k in range(2):
        r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if r.returncode == 0:
            return True, (r.stdout.strip().splitlines() or [''])[0]
        time.sleep(3)
    return False, (r.stdout or r.stderr).strip().splitlines()[-1][:120] if (r.stdout or r.stderr).strip() else '받지 못함'


def sheet(L):
    """받은 사진을 번호·이름·낱말과 함께 한 화면에 늘어놓고 브라우저로 찍는다."""
    out = os.path.join(tempfile.gettempdir(), 'photos_sheet_' + str(os.getpid())); os.makedirs(out, exist_ok=True)
    cells = []
    for i, it in enumerate(L, 1):
        fp = os.path.join(HERE, it['to'])
        img = f'<img src="file:///{html.escape(os.path.abspath(fp).replace(os.sep, "/"))}?t={time.time()}">' if os.path.exists(fp) else '<div class="no">없음</div>'
        cells.append(f'<figure>{img}<figcaption><b>{i}</b> {html.escape(it.get("name") or "")}<br><small>{html.escape(it["q"])} → {html.escape(it["to"])}</small></figcaption></figure>')
    cols = 4 if len(L) > 6 else 3
    page = ('<!doctype html><meta charset="utf-8"><style>body{margin:16px;font:14px/1.4 sans-serif;background:#fff}'
            f'.g{{display:grid;grid-template-columns:repeat({cols},1fr);gap:12px}}figure{{margin:0;border:1px solid #ddd}}img,.no{{width:100%;height:220px;object-fit:cover;display:block;background:#eee}}'
            '.no{display:flex;align-items:center;justify-content:center;color:#b00;font-size:20px}figcaption{padding:6px 8px}b{font-size:18px;color:#c00}small{color:#666}</style>'
            f'<div class="g">{"".join(cells)}</div>')
    hp = os.path.join(out, 'sheet.html'); open(hp, 'w', encoding='utf-8').write(page)
    rows = (len(L) + cols - 1) // cols; h = min(2400, rows * 300 + 40)
    r = subprocess.run(['node', os.path.join(HERE, 'refshot.js'), 'file:///' + hp.replace(os.sep, '/'), out, 'sheet', '1280', str(h), 'jpg'], cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace', shell=(os.name == 'nt'))
    shots = sorted(f for f in os.listdir(out) if f.startswith('sheet_') and f.endswith('.jpg'))
    return [os.path.join(out, f) for f in shots], (r.stdout or r.stderr)[-200:]


def main():
    A = sys.argv[1:]
    if not A or not os.path.exists(A[0]):
        print('사용: python photos.py 목록.json [--보기만]   (목록의 모양은 파일 머리말에)'); return 1
    L = json.load(open(A[0], encoding='utf-8'))
    L = [it for it in L if it.get('q') and it.get('to')]
    t0 = time.time(); bad = []
    if '--보기만' not in A:
        with ThreadPoolExecutor(max_workers=4) as ex:
            res = list(ex.map(one, L))
        for i, (it, (ok, msg)) in enumerate(zip(L, res), 1):
            print(f'  {"✓" if ok else "✗"} {i:>2}. {it.get("name") or it["q"]} — {msg[:110]}')
            if not ok:
                bad.append(i)
        print(f'{len(L) - len(bad)}장 받음' + (f', 못 받은 것 {len(bad)}장({", ".join(map(str, bad))}) — 낱말을 더 짧고 흔한 것으로 바꿔 photo.py 로 다시' if bad else '') + f' · {time.time() - t0:.0f}초')
    shots, tail = sheet(L)
    if shots:
        print('모아 보기 그림(이 그림을 열어 번호별로 확인한다 — 내용과 안 맞거나, 얼굴이 크게 나오거나, 상표가 보이는 번호만 다시 받는다):')
        for s in shots:
            print('  ' + s)
    else:
        print('모아 보기 그림을 만들지 못했습니다(브라우저 없음?). 사진을 하나씩 열어 확인합니다. ' + tail)
    return 1 if len(bad) == len(L) and L else 0


if __name__ == '__main__':
    sys.exit(main())
