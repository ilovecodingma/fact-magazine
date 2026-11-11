# -*- coding: utf-8 -*-
"""조립 예시(데모) 만들기: demos/demos.json 의 조합마다 사이트를 따로 찍어 docs/demo/<이름>/ 에 둔다(본 사이트 build 뒤에 실행).
조합마다 이름·한 줄 소개·켠 키트가 다르고, 데모는 본 사이트와 내용이 겹치므로 검색에 안 나가게(noindex) 만든다. /demo/ 목록 쪽에 「이렇게 입력하세요」 한 줄·켠 키트·쪽 수·캡처가 나온다.
사용: python build.py → python demo.py   (parts.demo 를 켜면 본 사이트 메뉴에 「조립 예시」가 생긴다)
캡처: demos/shots/<이름>_pc.png, <이름>_m.png 가 있으면 목록 쪽에 보여 준다(없으면 생략)."""
import html, json, os, re, shutil, subprocess, sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
E = html.escape


def main():
    import build as B
    demos = json.load(open(os.path.join(HERE, 'demos', 'demos.json'), encoding='utf-8'))
    only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None   # 하나만 따로 찍기(주소 맨 위 / 기준으로 --out 폴더에 바로)
    if only:
        d = next((x for x in demos if x['key'] == only or x['mix'] == only or x['name'] == only), None)
        if not d:
            sys.exit('조립 예시 이름을 찾지 못했습니다: ' + only + ' (목록: ' + ', '.join(x['key'] for x in demos) + ')')
        out = os.path.abspath(sys.argv[sys.argv.index('--out') + 1]) if '--out' in sys.argv else os.path.join(HERE, 'site_demo_' + d['key'])
        allparts = list(B.S['parts']); parts = {k: False for k in allparts}
        for k in d['kits']:
            kp = os.path.join(HERE, 'kits', k, 'kit.json')
            if not os.path.exists(kp):
                print(f'  ※ kits/{k} 가 없어 건너뜁니다'); continue
            for p in json.load(open(kp, encoding='utf-8')).get('parts', [k]):
                parts[p] = True
        env = dict(os.environ, DEMO='1', OUT_DIR=out, SITE_BASE='/', SITE_URL='https://프로젝트이름.localhost', SITE_NAME=d['name'], SITE_TAGLINE=d['tagline'], SITE_ABOUT=d['about'], HOME_TITLE=d['name'] + ' | 조립 예시',
                   HOME_DESC=d['tagline'], PARTS=json.dumps(parts, ensure_ascii=False), SITE_EXTRAS=json.dumps({'videos': B.EX.get('videos', [])} if d.get('video') else {}, ensure_ascii=False), TOPIC_KEYWORDS='')
        env['SITE_THEME'] = d.get('theme', 'paper'); env['SITE_ACCENT'] = d.get('accent', '')
        if d.get('data_root'):
            env['DATA_ROOT'] = os.path.join(HERE, d['data_root'])
        if d.get('kits_dir'):
            env['KITS_DIR'] = os.path.join(HERE, d['kits_dir'])
        r = subprocess.run([sys.executable, '-X', 'utf8', os.path.join(HERE, 'build.py')], cwd=HERE, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
        print(f'{d["name"]}: ' + (r.stdout.strip().splitlines() or [''])[-1] + f' → {out}')
        sys.exit(r.returncode)
    allparts = list(B.S['parts'])
    out_root = os.path.join(B.OUT, 'demo')
    if os.path.exists(out_root):
        shutil.rmtree(out_root)
    built = {}
    for d in demos:
        parts = {k: False for k in allparts}
        for k in d['kits']:
            kp = os.path.join(HERE, 'kits', k, 'kit.json')
            if not os.path.exists(kp):
                print(f'  ※ 「{d["name"]}」: kits/{k} 가 없어 건너뜁니다(조립 예시 목록을 고쳐 주세요)'); continue
            kit = json.load(open(kp, encoding='utf-8'))
            for p in kit.get('parts', [k]):
                parts[p] = True
        env = dict(os.environ, DEMO='1', OUT_DIR=os.path.join(out_root, d['key']), SITE_BASE=f'{B.BASE}demo/{d["key"]}/', SITE_URL=(f'{B.URL}/demo/{d["key"]}' if not B.NOURL else ''),
                   SITE_NAME=d['name'], SITE_TAGLINE=d['tagline'], SITE_ABOUT=d['about'], HOME_TITLE=d['name'] + ' | 조립 예시', HOME_DESC=d['tagline'], PARTS=json.dumps(parts, ensure_ascii=False),
                   SITE_EXTRAS=json.dumps({'videos': B.EX.get('videos', [])} if d.get('video') else {}, ensure_ascii=False), TOPIC_KEYWORDS='', GAMES_TITLE=d['name'] + ' 게임', GAMES_DESC=d['tagline'], SITE_THEME=d.get('theme', 'paper'), SITE_ACCENT=d.get('accent', ''))
        if d.get('data_root'):
            env['DATA_ROOT'] = os.path.join(HERE, d['data_root'])   # 이 데모의 글·소설·웹툰·전자책 원본 폴더
        if d.get('kits_dir'):
            env['KITS_DIR'] = os.path.join(HERE, d['kits_dir'])
            # 이 데모가 켜는 키트 중 자기 자료 폴더에 없는 것은 본 키트 폴더에서 가져온다(예: search 는 자료가 없음)
        r = subprocess.run([sys.executable, '-X', 'utf8', os.path.join(HERE, 'build.py')], cwd=HERE, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
        m = re.search(r'데모 쪽 (\d+)개', r.stdout)
        built[d['key']] = int(m.group(1)) if m else 0
        print(f'{d["key"]}: 쪽 {built[d["key"]]}개' + ('' if r.returncode == 0 else ' (빌드 실패: ' + r.stderr.strip()[-120:] + ')'))
    # 캡처 복사
    shots = os.path.join(HERE, 'demos', 'shots')
    img = os.path.join(out_root, 'img')
    os.makedirs(img, exist_ok=True)
    cards = ''
    for d in demos:
        pics = ''
        for suf, lab in (('pc', 'PC 폭'), ('m', '휴대폰 폭')):
            f = os.path.join(shots, f'{d["key"]}_{suf}.png')
            if os.path.exists(f):
                shutil.copy(f, os.path.join(img, f'{d["key"]}_{suf}.png'))
                pics += f'<figure style="margin:0;flex:1 1 {"320px" if suf == "pc" else "140px"}"><img src="{B.BASE}demo/img/{d["key"]}_{suf}.png" alt="{E(d["name"])} {lab}" loading="lazy" style="width:100%;border:1px solid #ccc"><figcaption class="mu" style="font:12px var(--sans)">{lab}</figcaption></figure>'
        cards += (f'<div class="tp" style="padding-bottom:24px"><span class="lb">조합 · {E(d["mix"])}</span><h3 style="font:800 24px/1.35 var(--serif);margin:6px 0"><a href="{B.BASE}demo/{d["key"]}/">{E(d["name"])}</a></h3>'
                  f'<p style="margin:0 0 6px">{E(d["tagline"])}</p><span class="ln">켠 키트: {E(" · ".join(d["kits"]))} · 쪽 {built.get(d["key"], 0)}개</span>'
                  f'<span class="ln">이렇게 입력하세요 → <code>{E(d["input_line"])}</code></span>' + (f'<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:12px;align-items:flex-start">{pics}</div>' if pics else '') + '</div>')
    B.page('demo', f'조립 예시 — {B.S["name"]}', '키트를 섞어 만든 사이트 예시 여섯 개', f'<div class="page"><span class="lb">조립 예시</span><h1>조립 예시</h1><p>키트를 섞으면 이런 사이트가 됩니다. 아래 사이트는 모두 같은 저장소의 키트를 다르게 켜서 따로 찍은 것이고, 검색에는 나가지 않습니다.</p>{cards}</div>', noindex=True)
    json.dump(built, open(os.path.join(HERE, 'demos', 'built.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('조립 예시', len(demos), '개 -> ', out_root)


if __name__ == '__main__':
    main()
