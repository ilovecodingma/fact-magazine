# -*- coding: utf-8 -*-
"""하나의 진입점: 트리거(Claude Code 명령)가 부르는 일을 같은 이름으로 직접 돌릴 수 있다. 파이썬 기본 기능만 쓴다.
사용: python run.py 시작                     환경 점검 + 키트 전부 점검표
      python run.py 키트 계산기               그 키트 실습(꼭 알아야 할 것 → 보이는 브라우저에서 스스로 시험 → 바꿔 보기 제안)
      python run.py 키트 전부                 키트를 차례로(시험이 적힌 키트)
      python run.py 섞기 계산기 용어 게임      고른 키트만 켜고 찍어 메뉴를 하나씩 눌러 보기(한글 이름 가능, 조립 예시 둘을 합칠 때는 섞기 도구함+동네정보)
      python run.py 조립 도구함               조립 예시 하나를 찍어 메뉴를 하나씩 눌러 보기(목록은 python run.py 조립)
      python run.py 사이클                    하루 한 바퀴(올리기·메일 빼고)를 단계별로 돌리기
      python run.py 알기 계산기 5             꼭 알아야 할 것 top-k   (python run.py 알기 하네스)
      python run.py 점검                      doctor
      python run.py 예제정리 [--yes]          주제를 바꿀 때 notes/ 의 예제 노트를 예제/ 로 옮김(독자에게 먼저 묻는다)
      python run.py 올리기전                  구문 검사 + 장·키트·조립·사이클 명령을 한 번씩 실제로 돌려 보기(올리기 전 필수)
      python run.py 진도 [보기|기록 글]        어디까지 했는지
      python run.py 장 1                      장 진행 파일 경로(코스/1장.md)
      python run.py 묶음 [이름]               기능 지도의 여덟 묶음(이름 없으면 목록). 이름을 주면 그 묶음 키트를 켜서 붙이고 하나씩 시험
      python run.py 켜기 계산기 [용어 …]       키트를 켜고 다시 찍어 메뉴·쪽에 생겼는지 한 줄로 확인(끄기 도 같은 모양)
      python run.py 지금                      내 사이트에 지금 켜져 있는 것 목록과 메뉴
      python run.py 전부 [--yes]              묻지 않고 여덟 묶음을 끝까지(묻는 자리는 기본값: 켜 둔다)
      python run.py 독자 [설정 키=값 …]        독자.json(수업 눈높이) 보기·고치기      python run.py 복습   진도·헷갈린 것에서 물음 3개
      python run.py 혼동 <키트> <적을 말>       헷갈려 한 것을 진도에 적기
옵션: --headless(창 없이) --slow 초(단계 간격) --shots 폴더(단계마다 화면을 png 로 저장, 사이클은 단계 결과 쪽) · 보이는 창 위치는 환경변수 SELFTEST_POS=2000,100
설명: 이 파일은 얇은 껍데기다 — 실제 일은 doctor.py·selftest.py·know.py·mix.py·demo.py·run_daily.py 가 한다. 올리기·메일 발송·로그인은 하지 않는다."""
import glob, json, os, subprocess, sys, time
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
A = sys.argv[1:]
PY = [sys.executable, '-X', 'utf8']
FLAGS = [a for a in A if a in ('--headless',)] + (['--slow', A[A.index('--slow') + 1]] if '--slow' in A else []) + (['--shots', os.path.abspath(A[A.index('--shots') + 1])] if '--shots' in A and len(A) > A.index('--shots') + 1 else [])
POS = [a for i, a in enumerate(A) if not a.startswith('--') and (i == 0 or A[i - 1] not in ('--slow', '--shots'))]
SHOTS = os.path.abspath(A[A.index('--shots') + 1]) if '--shots' in A and len(A) > A.index('--shots') + 1 else None
PROG = os.path.join(HERE, '진도.json')


def sh(args, check=False):
    return subprocess.run(PY + args, cwd=HERE).returncode


def prog_load():
    return json.load(open(PROG, encoding='utf-8')) if os.path.exists(PROG) else {'done': [], 'last': ''}


def prog_add(text):
    d = prog_load(); d['done'].append({'t': time.strftime('%Y-%m-%d %H:%M'), 'what': text}); d['last'] = text
    json.dump(d, open(PROG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def kits():
    out = {}
    for p in sorted(glob.glob(os.path.join(HERE, 'kits', '*', 'kit.json'))):
        k = json.load(open(p, encoding='utf-8')); out[k['name']] = k
    return out


LAST_OUT = {}   # 사이클 단계별 출력(점검 결과를 화면으로 찍는 데 쓴다)


def text_png(br, title, blocks, out):
    """글을 읽기 좋은 쪽으로 그려 찍는다(폴더 목록이나 파일 경로가 화면에 나오지 않게)."""
    import html as H, tempfile
    body = ''.join(f'<h2>{H.escape(h)}</h2><pre>{H.escape(t)}</pre>' for h, t in blocks)
    doc = ('<!doctype html><meta charset="utf-8"><title>' + H.escape(title) + '</title><style>body{margin:0;background:#f6f4ef;font:17px/1.7 "Malgun Gothic",system-ui,sans-serif;color:#111}'
           'main{max-width:860px;margin:0 auto;padding:28px 24px}h1{font-size:26px;border-bottom:3px double #111;padding-bottom:10px}h2{font-size:15px;color:#b5532a;margin:22px 0 6px}'
           'pre{white-space:pre-wrap;word-break:break-word;font:inherit;background:#fff;border:1px solid #ddd;border-radius:10px;padding:14px 16px;margin:0}</style><main><h1>' + H.escape(title) + '</h1>' + body + '</main>')
    f = os.path.join(tempfile.mkdtemp(), 't.html'); open(f, 'w', encoding='utf-8').write(doc)
    subprocess.run([br, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1100,900', f'--screenshot={out}', 'file:///' + f.replace(chr(92), '/')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)


def cycle_shot(i, title, script):
    """사이클 단계가 끝난 뒤 그 결과를 headless 로 찍는다: 1 첫 화면·호·새 노트, 2 알림 문구·블로그 글(읽기 좋게 그린 쪽), 3 카드 그림, 4 점검 결과(상태 쪽이 켜져 있으면 그 쪽도)."""
    import selftest as T, shutil
    docs = os.path.join(HERE, 'docs')
    br = T.find_browser()
    if not br:
        print('  (브라우저가 없어 화면 저장을 건너뜁니다)'); return
    os.makedirs(SHOTS, exist_ok=True)
    pages = []
    if i == 1:
        pages = [p for p in ('index.html', 'issue/index.html') if os.path.exists(os.path.join(docs, p))]
        nd = os.path.join(docs, 'n')   # 확인 노트 쪽은 n/<노트 id>/
        if os.path.isdir(nd):
            pages += ['n/' + n + '/index.html' for n in sorted(os.listdir(nd), reverse=True)[:1] if os.path.exists(os.path.join(nd, n, 'index.html'))]
    elif i == 4 and os.path.exists(os.path.join(docs, 'status', 'index.html')):
        pages = ['status/index.html']
    if pages:
        srv, port = T.start_server(docs)
        try:
            for n, p in enumerate(pages, 1):
                out = os.path.join(SHOTS, f'사이클_{i}_{n}_{p.replace("/", "_").replace(".html", "")}.png')
                subprocess.run([br, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1100,900', f'--screenshot={out}', f'http://127.0.0.1:{port}/{p}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
                print('  화면 저장:', os.path.basename(out), flush=True)
        finally:
            srv.shutdown()
    if i == 2:
        d = os.path.join(HERE, 'promo_out')
        subs = sorted(x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x)))[:1] if os.path.isdir(d) else []
        for sdir in subs:
            blocks = []
            for f in ('알림_짧게.txt', '알림_보통.txt', '블로그글.md'):
                fp = os.path.join(d, sdir, f)
                if os.path.exists(fp):
                    t = open(fp, encoding='utf-8').read().strip()
                    blocks.append((f.replace('_', ' ').rsplit('.', 1)[0], chr(10).join(t.splitlines()[:14]) + (chr(10) + '…' if len(t.splitlines()) > 14 else '')))
            out = os.path.join(SHOTS, f'사이클_2_1_promo_{sdir}.png'); text_png(br, '알림 문구와 블로그 글 — ' + sdir, blocks, out); print('  화면 저장:', os.path.basename(out), flush=True)
    if i == 3:
        d = os.path.join(HERE, 'cards')
        for n, f in enumerate([f for f in sorted(os.listdir(d)) if f.endswith('.png')][:2] if os.path.isdir(d) else [], 1):
            shutil.copy(os.path.join(d, f), os.path.join(SHOTS, f'사이클_3_{n}_{f}')); print('  그림 저장:', f, flush=True)
    if i == 4 and LAST_OUT.get(4):
        out = os.path.join(SHOTS, '사이클_4_점검결과.png'); text_png(br, '점검(audit) 결과', [('python audit.py', LAST_OUT[4][-2500:])], out); print('  화면 저장:', os.path.basename(out), flush=True)


def info_on():
    """site.json(+site.local.json)에서 뉴스(info) 부품이 켜져 있나."""
    S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
    lp = os.path.join(HERE, 'site.local.json')
    if os.path.exists(lp):
        S.update(json.load(open(lp, encoding='utf-8')))
    return bool((S.get('parts') or {}).get('info', True))



GFILE = os.path.join(HERE, 'groups.json')
READER = os.path.join(HERE, '독자.json')


def gload():
    return json.load(open(GFILE, encoding='utf-8'))


def kit_json(name):
    p = os.path.join(HERE, 'kits', name, 'kit.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def own_part(kj):
    """이 키트를 켜고 끌 때 바꾸는 부품(site.json parts 의 키): 키트 이름이 부품이면 그것, 아니면 kit.json parts 의 첫 번째."""
    S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
    if kj['name'] in S['parts']:
        return kj['name']
    return (kj.get('parts') or [None])[0]


def set_parts(names, on):
    """site.json(과 site.local.json 에 parts 가 있으면 그쪽도)의 parts 를 바꾼다."""
    for f in ('site.json', 'site.local.json'):
        fp = os.path.join(HERE, f)
        if not os.path.exists(fp):
            continue
        d = json.load(open(fp, encoding='utf-8'))
        if f == 'site.local.json' and 'parts' not in d:
            continue
        for n in names:
            d.setdefault('parts', {})[n] = on
        json.dump(d, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def eff_parts():
    S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
    lp = os.path.join(HERE, 'site.local.json')
    parts = dict(S.get('parts') or {})
    if os.path.exists(lp):
        parts.update(json.load(open(lp, encoding='utf-8')).get('parts') or {})
    return parts


def rebuild_local():
    out = os.path.join(HERE, 'site_local')
    env = dict(os.environ, SITE_BASE='/', SITE_URL='https://프로젝트이름.localhost', OUT_DIR=out)
    r = subprocess.run(PY + ['build.py'], cwd=HERE, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return out, (r.stdout.strip().splitlines() or [''])[-1], r.returncode


def menu_of(out):
    """site_local 첫 화면의 메뉴 칸(이름)과 모든 링크 주소."""
    import re as _re
    ip = os.path.join(out, 'index.html')
    h = open(ip, encoding='utf-8').read() if os.path.exists(ip) else ''
    nav = _re.search(r'<nav class="menu">(.*?)</nav>', h, _re.S)
    labels = _re.findall(r'<a href="[^"]*">([^<]+)</a>', nav.group(1)) if nav else []
    return labels, set(_re.findall(r'href="(/[^"]*)"', h))


def find_kit(word):
    sys.path.insert(0, HERE); import selftest as T
    k = T.resolve(word)
    return kit_json(k['name']) if k else None


def toggle(words, on):
    G = gload()['paths']
    if not words:
        print('사용: python run.py ' + ('켜기' if on else '끄기') + ' 계산기 [용어 …]'); return 1
    rc = 0
    for w in words:
        kj = find_kit(w)
        if not kj:
            print(f'「{w}」 키트를 찾지 못했습니다(python run.py 키트 로 목록)'); rc = 1; continue
        op = own_part(kj)
        if not op:
            print(f'「{kj["title"]}」 은(는) 사이트 화면에 붙는 기능이 아니라 돌려서 파일을 만드는 도구라 켜고 끌 것이 없습니다. python run.py 키트 {kj["name"]} 로 돌려 보세요.'); continue
        before_labels, _ = menu_of(os.path.join(HERE, 'site_local')) if os.path.isdir(os.path.join(HERE, 'site_local')) else ([], set())
        set_parts(list(kj.get('parts') or [op]) if on else [op], on)
        out, last, rcb = rebuild_local()
        if rcb != 0:
            print(f'✗ 다시 찍기에 실패했습니다: {last}'); rc = 1; continue
        labels, links = menu_of(out)
        path = G.get(kj['name'])
        present = ('/' + path in links) if path else None
        name = kj.get('title', kj['name'])
        if path is None:
            print(f'{"✓" if on else "✓"} 「{name}」 {"켰습니다" if on else "껐습니다"}(화면에 따로 쪽이 생기지 않는 기능입니다). 지금 메뉴: {" · ".join(labels)}')
        elif on:
            print(('✓' if present else '△') + f' 「{name}」 켰습니다 — ' + ('쪽 /' + path + ' 이 사이트 링크에 생겼습니다' if present else '링크가 첫 화면에 보이지 않습니다(자료가 비어 있거나 메뉴 밖일 수 있음)') + f'. 지금 메뉴: {" · ".join(labels)}')
        else:
            print(('✓' if not present else '△') + f' 「{name}」 껐습니다 — ' + ('메뉴·링크에서 빠졌습니다' if not present else '아직 링크가 남아 있습니다(다른 기능이 같은 쪽을 쓸 수 있음)') + f'. 지금 메뉴: {" · ".join(labels)}')
        prog_group_toggle(kj['name'], on)
    return rc


def prog_group_toggle(kit, on):
    d = prog_load(); d.setdefault('toggles', {})[kit] = '켬' if on else '끔'
    d['done'].append({'t': time.strftime('%Y-%m-%d %H:%M'), 'what': f'{"켜기" if on else "끄기"} {kit}'}); d['last'] = d['done'][-1]['what']
    json.dump(d, open(PROG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def now_list():
    G = gload(); P = eff_parts(); out = os.path.join(HERE, 'site_local')
    if not os.path.isdir(out):
        rebuild_local()
    labels, _ = menu_of(out)
    on_kits = []
    for g in G['groups']:
        for kn in g['kits']:
            kj = kit_json(kn)
            if kj and own_part(kj) and P.get(own_part(kj)):
                on_kits.append((g['name'], kj.get('title', kn)))
    print('지금 내 사이트에 켜져 있는 것:', len(on_kits), '개')
    cur = None
    for gn, t in on_kits:
        if gn != cur:
            print(f'  [{gn}]', end=' '); cur = gn
        print(t, end=' · ')
    print('\n메뉴(첫 화면 위):', ' · '.join(labels) or '(없음)')
    print('내 PC 에서 열려면: python serve.py --open')


def group_find(word):
    G = gload()['groups']
    if word.isdigit() and 1 <= int(word) <= len(G):
        return G[int(word) - 1]
    w = word.replace(' ', '')
    return next((g for g in G if w in (g['key'], g['name'].replace(' ', '')) or (w and w in g['name'].replace(' ', ''))), None)


def run_group(g, headless_flags):
    print(f'━━ 묶음 「{g["name"]}」 ━━\n{g["intro"]}\n', flush=True)
    kits_ = [kit_json(k) for k in g['kits']]; kits_ = [k for k in kits_ if k]
    # ㉠ 화면에 붙는 키트를 한꺼번에 켜서 내 PC 사이트에 붙인다
    ons = []
    for kj in kits_:
        op = own_part(kj)
        if op:
            ons += list(kj.get('parts') or [op])
    if ons:
        set_parts(sorted(set(ons)), True); out, last, rcb = rebuild_local()
        print(f'㉠ 이 묶음의 화면 기능을 내 사이트에 붙였습니다({last})', flush=True)
    labels, _ = menu_of(os.path.join(HERE, 'site_local'))
    print('   메뉴:', ' · '.join(labels), '\n', flush=True)
    ok = skip = bad = 0
    sys.path.insert(0, HERE); import selftest as T
    for n, kj in enumerate(kits_, 1):
        print(f'── ({n}/{len(kits_)}) {kj.get("title", kj["name"])} ──', flush=True)
        for m in (kj.get('must_know') or [])[:1]:
            print('㉢ 설명:', m.get('알것', ''), flush=True)
        r = subprocess.run(PY + ['selftest.py', kj['name']] + headless_flags, cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace')
        outp = r.stdout.strip()
        print('\n'.join('   ' + l for l in outp.splitlines()[-9:]), flush=True)
        if '건너뜀' in outp and '단계 가운데' not in outp:
            skip += 1
        elif r.returncode == 0:
            ok += 1
        else:
            bad += 1
        if kj.get('try_change'):
            print('㉣ 해 볼 일:', kj['try_change'], flush=True)
        print(f'   ㉤ 이 기능은 켜 둘까요, 끌까요?  →  끄려면 python run.py 끄기 {kj["name"]}', flush=True)
    print(f'\n묶음 「{g["name"]}」 결과: 통과 {ok} · 건너뜀 {skip} · 안 됨 {bad}', flush=True)
    now_list()
    d = prog_load(); d.setdefault('groups', {})[g['key']] = {'t': time.strftime('%Y-%m-%d %H:%M'), 'ok': ok, 'skip': skip, 'bad': bad}
    d['done'].append({'t': time.strftime('%Y-%m-%d %H:%M'), 'what': f'묶음 {g["name"]}(통과 {ok}·건너뜀 {skip}·안 됨 {bad})'}); d['last'] = d['done'][-1]['what']
    json.dump(d, open(PROG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return 0 if bad == 0 else 1


def reader_cmd(rest):
    d = json.load(open(READER, encoding='utf-8')) if os.path.exists(READER) else {}
    if rest and rest[0] == '설정':
        for kv in rest[1:]:
            if '=' in kv:
                k, v = kv.split('=', 1); d[k.strip()] = v.strip()
        json.dump(d, open(READER, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print('독자.json 에 적었습니다')
    print('독자.json:', json.dumps(d, ensure_ascii=False) if d else '(아직 없음 — 과외.md 의 「처음에 독자를 묻는다」 를 따라 한 번 묻고 `python run.py 독자 설정 해본것=… 만들고싶은것=… 시간=…` 로 적습니다)')
    return 0


def review_cmd():
    import random
    d = prog_load(); G = gload(); pool = []
    seen = [x['what'] for x in d['done'] if x['what'].startswith('키트 ')]
    names = [w.split()[1] for w in seen if len(w.split()) > 1]
    for c in d.get('confused', [])[-6:]:
        kj = kit_json(c['kit'])
        if kj:
            pool += [(0, kj, m) for m in (kj.get('must_know') or [])[:2]]
    for nm in names[-6:]:
        kj = kit_json(nm)
        if kj:
            pool += [(1, kj, m) for m in (kj.get('must_know') or [])]
    if not pool:
        print('아직 복습할 진도가 없습니다. python run.py 키트 계산기 처럼 한 가지를 먼저 해 보세요.'); return 0
    pool.sort(key=lambda x: x[0]); picked, used = [], set()
    for pr, kj, m in pool:
        if m['알것'] in used:
            continue
        used.add(m['알것']); picked.append((kj, m))
        if len(picked) == 3:
            break
    print('복습 물음 3개(답은 독자가 먼저 말하게 하고, 이 줄 아래 「정답 메모」는 에이전트만 봅니다):')
    for i, (kj, m) in enumerate(picked, 1):
        print(f'Q{i}. [{kj.get("title", kj["name"])}] 「{m["알것"][:40]}」 를 모르면 어떤 일이 생길까요?')
    print('— 정답 메모(에이전트용) —')
    for i, (kj, m) in enumerate(picked, 1):
        print(f'A{i}. {m.get("모르면", "")} (까닭: {m.get("까닭", "")})')
    return 0


def confuse_cmd(rest):
    if len(rest) < 2:
        print('사용: python run.py 혼동 <키트> <헷갈려 한 말>'); return 1
    d = prog_load(); d.setdefault('confused', []).append({'t': time.strftime('%Y-%m-%d %H:%M'), 'kit': rest[0], 'what': ' '.join(rest[1:])})
    json.dump(d, open(PROG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print('적었습니다'); return 0


def all_cmd():
    G = gload(); rc = 0
    fl = FLAGS if FLAGS else ['--headless']
    for g in G['groups']:
        rc |= run_group(g, fl)
    print('\n━━ 여덟 묶음을 끝까지 돌았습니다(묻는 자리는 기본값: 통과한 기능은 켜 둠) ━━'); now_list(); return rc


def find_demo(word):
    """조립 예시를 키(tools)·조합 이름(도구 모음)·사이트 이름(한입 도구함)으로 찾는다. 공백 무시, 하나로 좁혀질 때만."""
    D = json.load(open(os.path.join(HERE, 'demos', 'demos.json'), encoding='utf-8'))
    w = word.replace(' ', '')
    for f in (lambda d: [d['key']], lambda d: [d['mix'], d['name']]):
        hit = [d for d in D if w in [x.replace(' ', '') for x in f(d)]]
        if len(hit) == 1:
            return hit[0]
    hit = [d for d in D if w and any(w in x.replace(' ', '') for x in (d['key'], d['mix'], d['name']))]
    return hit[0] if len(hit) == 1 else None


def one_kit(name):
    sys.path.insert(0, HERE)
    import selftest as T
    k = T.resolve(name)
    if not k:
        print(f'「{name}」 키트를 찾지 못했습니다. 목록: python run.py 키트'); return 1
    print(f'━━ {k.get("title", k["name"])} ━━')
    print('① 꼭 알아야 할 것(위에서부터 3가지)'); sh(['know.py', k['name'], '3'])
    print('② 보는 앞에서 스스로 시험'); rc = sh(['selftest.py', k['name']] + FLAGS)
    ex = os.path.join(HERE, 'kits', k['name'], '설명.md')
    if os.path.exists(ex):
        print(f'③ 설명 뼈대: kits/{k["name"]}/설명.md (에이전트가 독자 눈높이로 풀어 설명할 것)')
    if k.get('try_change'):
        print('④ 바꿔 보기 제안:', k['try_change'])
    print(f'⑤ 내 PC 에서 직접 열려면: python mix.py --add {k["name"]}  →  python serve.py --open')
    note = ''
    if rc != 0:
        dirty = subprocess.run(['git', 'status', '--porcelain', 'kits/' + k['name']], cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace').stdout.strip()
        if dirty:
            note = '(바꾼 자료 때문)'
            print('※ 이 키트의 자료를 바꾸셨습니다. 자가 시험은 예시 값(기본 자료)을 기준으로 하므로, 바꾼 뒤의 ✗ 는 고장이 아니라 「예시 값과 달라서」 나오는 것입니다. 바꾼 값으로 화면이 열리는지는 python serve.py --open 으로 직접 확인하세요.')
    prog_add(f'키트 {k["name"]} 실습' + ('' if rc == 0 else '(시험에 실패한 단계 있음' + note + ')'))
    return rc


def main():
    if not POS:
        print(__doc__); return 0
    cmd, rest = POS[0], POS[1:]
    if cmd in ('시작', 'start'):
        rc = sh(['doctor.py', '--quick'])   # 환경 점검도 doctor 가 맨 앞에서 한다
        prog_add('시작(환경·키트 점검)'); print('\n다음: python run.py 키트 계산기  /  python run.py 조립  /  python run.py 사이클'); return rc
    if cmd in ('점검', 'doctor'):
        return sh(['doctor.py'] + (['--quick'] if '--quick' in A else []))
    if cmd in ('키트', 'kit'):
        if not rest:
            K = kits(); print('키트(자가 시험이 있는 것에 ✓):'); [print(f'  {"✓" if k.get("selftest") else " "} {n:20} {k["title"]}') for n, k in K.items()]
            print('\n사용: python run.py 키트 계산기  ·  python run.py 키트 전부'); return 0
        if rest[0] == '전부':
            rc = 0; n = 0
            for k in kits().values():
                if k.get('selftest'):
                    rc |= one_kit(k['name']); n += 1
            print(f'\n키트 {n}개 실습 끝. 점검표: python run.py 점검'); return rc
        return one_kit(rest[0])
    if cmd in ('섞기', 'mix'):
        if not rest:
            print('사용: python run.py 섞기 계산기 용어 게임'); return 1
        sys.path.insert(0, HERE); import selftest as T
        names = []   # 키트 이름 + 조립 예시 이름(「도구함+동네정보」처럼 +로 이으면 예시들의 키트를 합친다)
        for r in rest:
            for w in r.split('+'):
                d = find_demo(w); k = T.resolve(w)
                got = k['name'] if k else None
                for n in ([got] if got else (d['kits'] if d else [w])):
                    if n not in names:
                        names.append(n)
        print('켜는 키트:', ' '.join(names))
        sh(['mix.py'] + names); out = os.path.join(HERE, 'site_local')
        env = dict(os.environ, SITE_BASE='/', SITE_URL='https://프로젝트이름.localhost', OUT_DIR=out)
        r = subprocess.run(PY + ['build.py'], cwd=HERE, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace'); print((r.stdout.strip().splitlines() or [''])[-1])
        rc = sh(['selftest.py', '--tour', out, '섞은 사이트(' + ' + '.join(rest) + ')'] + FLAGS)
        print('내 PC 에서 직접 열려면: python serve.py --open'); prog_add('섞기 ' + ' '.join(rest)); return rc
    if cmd in ('조립', 'assemble'):
        D = json.load(open(os.path.join(HERE, 'demos', 'demos.json'), encoding='utf-8'))
        if not rest:
            print('조립 예시:'); [print(f'  {d["key"]:12} {d["name"]} — {d["tagline"][:50]}') for d in D]; print('\n사용: python run.py 조립 <이름>'); return 0
        d0 = find_demo(' '.join(rest))
        if not d0:
            print('조립 예시를 찾지 못했습니다. 목록: python run.py 조립 (이름은 도구함·동네 정보처럼 한글도 됩니다)'); return 1
        rest = [d0['key']]
        out = os.path.join(HERE, 'site_demo_' + rest[0])
        if sh(['demo.py', '--only', rest[0], '--out', out]) != 0:
            return 1
        rc = sh(['selftest.py', '--tour', out, '조립 예시 ' + rest[0]] + FLAGS)
        print(f'내 PC 에서 직접 열려면: python -m http.server --directory site_demo_{rest[0]} 또는 python serve.py (조립 예시 목록 /demo/)'); prog_add('조립 ' + rest[0]); return rc
    if cmd in ('사이클', 'cycle'):
        print('━━ 하루 한 바퀴(올리기·메일 제외) ━━', flush=True)
        steps = [('수집·묶기·대조·화면·호·쇼츠', ['run_daily.py'], '수집 건수·묶음·대조 결과·쪽 수·호 PDF·쇼츠는 위 출력의 단계별 줄'), ('알림 문구·블로그 글(promo)', ['promo.py'], 'promo_out/ 폴더'), ('공유용 카드 그림', ['card.py', '--square'], 'cards/ 폴더(png·svg)'), ('점검(audit)', ['audit.py'], '아래 점검 결과 줄')]
        for i, (t, a, where) in enumerate(steps, 1):
            print(f'\n[{i}/{len(steps)}] {t} — {time.strftime("%H:%M:%S")}  (결과는 {where})', flush=True)
            if i in (2, 3) and not info_on():
                print('  건너뜀: 이 사이트는 뉴스 기능이 꺼져 있어 확인 노트가 없습니다(알림 문구·카드는 노트로 만듭니다).', flush=True); continue
            if i == 4:
                r4 = subprocess.run(PY + a, cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace'); print(r4.stdout + r4.stderr, flush=True); LAST_OUT[4] = r4.stdout + r4.stderr
            else:
                sh(a)
            sys.stdout.flush()
            if SHOTS:
                cycle_shot(i, t, a[0])
        print('\n올릴 묶음(만들어져 있는 것, 아직 올리지 않았습니다):', flush=True)
        for d, what in (('promo_out', '알림 문구·블로그 글'), ('cards', '공유용 카드 그림'), ('shorts', '쇼츠 영상'), ('넘김', '역할끼리 넘긴 파일')):
            p = os.path.join(HERE, d)
            n = len([f for f in os.listdir(p) if not f.startswith('.')]) if os.path.isdir(p) else 0
            print(f'  - {d}/ ({what}): {n}개', flush=True)
        print('\n여기서 사람이 올립니다: 블로그·영상·인스타에 올리기와 소식지 메일 발송은 사람 승인 후에(이 사이클은 올리지 않았습니다). 결과 화면은 python serve.py --open 으로 열어 볼 수 있습니다.', flush=True)
        prog_add('사이클 한 바퀴(예행)'); return 0
    if cmd in ('올리기전', 'precheck'):
        import ast
        bad = 0
        for f in sorted(glob.glob(os.path.join(HERE, '*.py'))):
            try:
                ast.parse(open(f, encoding='utf-8').read())
            except SyntaxError as e:
                bad += 1; print(f'✗ 구문 오류 {os.path.basename(f)} {e.lineno}행: {e.msg}')
        print('구문 검사:', '모두 통과' if not bad else f'{bad}개 파일에 오류')
        for t in (['장', '1'], ['장', '2'], ['장', '3'], ['진도'], ['키트'], ['조립'], ['알기', '계산기', '1'], ['키트', '계산기', '--headless', '--slow', '0.1'], ['조립', 'tools', '--headless', '--slow', '0.1']):
            r = subprocess.run(PY + ['run.py'] + t, cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace')
            ok = r.returncode == 0 and 'Traceback' not in r.stderr and '없습니다' not in r.stdout.split(chr(10))[0]
            bad += 0 if ok else 1; print(('✓' if ok else '✗'), 'run.py ' + ' '.join(t))
        r = subprocess.run(PY + ['run_daily.py', '--dry'], cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace'); ok = r.returncode == 0
        bad += 0 if ok else 1; print(('✓' if ok else '✗'), 'run_daily.py --dry')
        print(chr(10) + '올려도 됩니다' if not bad else chr(10) + f'올리지 마세요: {bad}건 실패'); return 1 if bad else 0
    if cmd in ('예제정리', 'cleanup'):
        import re as _re, shutil
        nd = os.path.join(HERE, 'notes'); ex = os.path.join(HERE, '예제')
        fs = [f for f in sorted(os.listdir(nd)) if _re.match(r'\d{4}-\d{2}-\d{2}-', f)] if os.path.isdir(nd) else []
        print('옮길 예제 노트(날짜로 시작하는 작성자의 노트):', len(fs), '개  ※ 예시-수출.json 은 화면 시험용이라 그대로 둡니다')
        for f in fs[:8]:
            print('  -', f)
        if '--yes' in A:
            os.makedirs(ex, exist_ok=True)
            for f in fs:
                shutil.move(os.path.join(nd, f), os.path.join(ex, f))
            print('예제/ 로 옮겼습니다(지우지 않았습니다).'); prog_add('예제 노트를 예제/ 로 옮김')
        else:
            print('옮기려면 독자에게 먼저 묻고: python run.py 예제정리 --yes')
        return 0
    if cmd in ('켜기', 'on'):
        return toggle(rest, True)
    if cmd in ('끄기', 'off'):
        return toggle(rest, False)
    if cmd in ('지금', 'now'):
        now_list(); return 0
    if cmd in ('묶음', 'group'):
        G = gload()['groups']
        if not rest:
            print('기능 지도의 여덟 묶음:'); [print(f'  {i}. {g["name"]} ({len(g["kits"])}개) — {g["intro"][:40]}') for i, g in enumerate(G, 1)]
            print('\n사용: python run.py 묶음 도구와자료  (또는 번호)'); return 0
        g = group_find(' '.join(rest))
        if not g:
            print('묶음을 찾지 못했습니다: python run.py 묶음'); return 1
        return run_group(g, FLAGS or ['--headless'])
    if cmd in ('전부', 'all'):
        return all_cmd()
    if cmd in ('독자', 'reader'):
        return reader_cmd(rest)
    if cmd in ('복습', 'review'):
        return review_cmd()
    if cmd in ('혼동', 'confused'):
        return confuse_cmd(rest)
    if cmd in ('알기', 'know'):
        return sh(['know.py'] + rest)
    if cmd in ('진도', 'progress'):
        if rest and rest[0] == '기록':
            prog_add(' '.join(rest[1:]) or '진행'); print('기록했습니다'); return 0
        d = prog_load(); print('마지막:', d['last'] or '(없음)')
        for x in d['done'][-12:]:
            print(' ', x['t'], x['what'])
        return 0
    if cmd in ('장', 'chapter'):
        n = rest[0] if rest else '1'
        p = os.path.join(HERE, '코스', f'{n}장.md'); print(p if os.path.exists(p) else f'코스/{n}장.md 가 없습니다'); return 0
    print(__doc__); return 1


if __name__ == '__main__':
    sys.exit(main())
