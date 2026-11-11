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
      python run.py 다듬기 [번호|다음] [--안 A|B] [--shots 폴더]   투박한 출발 모습을 걸음마다 고품질로(안 없이 부르면 안 A·B 미리보기만, --안 을 주면 적용하고 전·후 화면과 점수)
      python run.py 되돌리기 <번호>            그 다듬기 걸음을 끈다(출발 모습 쪽으로)
      python run.py 만듦새 [--shots 폴더]      첫 화면·글 쪽·휴대폰을 재서 점수(빈 영역·그림·최소 글자·대비·넘침·정보량)
      python run.py 비교 [종류]                참고 사이트 화면과 내 첫 화면을 나란히 한 장으로(인터넷 필요)
      python run.py 생각 · 정리 "<독자의 말>" [--한줄 …] [--정함 a;b] [--미정 …] [--미룸 …]   독자의 생각을 정리해 생각.md 에 남기기
      python run.py 참고 [종류]               참고 사이트(실제 사이트와 「이렇게 번다」). --shots 폴더 면 그 사이트 화면을 headless 로 찍어 둔다
      python run.py 기획서                     기획서 한 장(기획서.md, 없으면 양식)
      python run.py 서비스 <종류> [단계 1~9]   서비스 하나를 끝까지: ㉠참고 ㉡기획서 ㉢기능 붙이기 ㉣내용 채우기 ㉤돈 자리 ㉥필수 쪽 ㉦겉모습 ㉧휴대폰 ㉨올릴 준비(종류: 정보 매거진·도구 모음·요리법 모음·가계부 앱)
      python run.py 독자 [설정 키=값 …]        독자.json(수업 눈높이) 보기·고치기      python run.py 복습   진도·헷갈린 것에서 물음 3개
      python run.py 혼동 <키트> <적을 말>       헷갈려 한 것을 진도에 적기
옵션: --headless(창 없이) --slow 초(단계 간격) --shots 폴더(단계마다 화면을 png 로 저장, 사이클은 단계 결과 쪽) · 보이는 창 위치는 환경변수 SELFTEST_POS=2000,100
설명: 이 파일은 얇은 껍데기다 — 실제 일은 doctor.py·selftest.py·know.py·mix.py·demo.py·run_daily.py 가 한다. 올리기·메일 발송·로그인은 하지 않는다."""
import glob, json, os, re, subprocess, sys, time
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
    """독자 폴더의 선택은 site.local.json(git 추적 제외)에만 쓴다 — 추적되는 site.json 은 건드리지 않는다. site.local.json 에 parts 가 없으면 site.json 의 parts 를 복사해 시작한다."""
    S0 = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
    fp = os.path.join(HERE, 'site.local.json')
    d = json.load(open(fp, encoding='utf-8')) if os.path.exists(fp) else {}
    if 'parts' not in d:
        d['parts'] = dict(S0.get('parts') or {})
    for n in names:
        d['parts'][n] = on
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
        if SHOTS:
            ob, lb_, rb_ = rebuild_local(); _shot_site(ob, [''], f'{"켜기" if on else "끄기"}_{kj["name"]}_1전')
        set_parts(list(kj.get('parts') or [op]) if on else [op], on)
        out, last, rcb = rebuild_local()
        if rcb != 0:
            print(f'✗ 다시 찍기에 실패했습니다: {last}'); rc = 1; continue
        labels, links = menu_of(out)
        if SHOTS:
            _shot_site(out, [''], f'{"켜기" if on else "끄기"}_{kj["name"]}_2후')
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
    off = {k for k, v in (prog_load().get('toggles') or {}).items() if v == '끔'}
    skipped_off = [k['name'] for k in kits_ if k['name'] in off]
    kits_ = [k for k in kits_ if k['name'] not in off]
    if skipped_off:
        print('독자가 꺼 둔 기능은 건너뜁니다(다시 켜지 않음):', ', '.join(skipped_off), '\n', flush=True)
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
        dirty = subprocess.run(['git', 'status', '--porcelain', 'kits/' + kj['name'] + '/data'], cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace').stdout.strip()
        if '건너뜀' in outp and '단계 가운데' not in outp:
            skip += 1
        elif r.returncode == 0:
            ok += 1
        elif dirty:
            ok += 1; print('   ※ 독자가 바꾼 자료라 시험의 ✗ 는 예시 값과 달라서 나온 것입니다(고장 아님). 바꾼 값은 python serve.py --open 으로 직접 확인하세요.', flush=True)
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


KINDS = {
    '정보 매거진': dict(alias=['매거진', '정보', 'magazine'], parts=['info', 'issue', 'search', 'prefs', 'monetize'], theme=('paper', ''), ref='정보 매거진',
        fill='독자 주제의 공식 자료(정부·기관 사이트)를 열어 확인 노트 한 건을 쓴다(notes/ 형식은 런북.md 3절, `python check.py` 로 대조, 예제 노트는 `python run.py 예제정리`로 먼저 옮길지 묻는다). 공식 자료에서 온 숫자는 출처, 못 찾은 것은 「아직 확인 안 됨」.'),
    '도구 모음': dict(alias=['도구', 'tools'], parts=['calc', 'glossary', 'compare', 'search', 'prefs', 'monetize'], theme=('doc', '#2f6fed'), ref='도구 모음',
        fill='독자가 쓰는 계산 하나를 정한다 → kits/calc/data/calculators.json 에 식과 입력칸을 쓴다(식의 근거를 설명에 적고, 모르는 숫자는 「예시」 표시). 용어 3개(glossary)와 비교표 한 장(compare)도 독자 주제로 바꾼다.'),
    '요리법 모음': dict(alias=['요리법', '요리', 'recipes'], parts=['recipes', 'search', 'prefs', 'monetize'], theme=('card', '#e4572e'), ref='요리법 모음',
        fill='독자가 말한 요리 다섯 개의 이름·재료·순서를 kits/recipes/data/recipes.json 에 쓴다(분량·시간은 「예시」 표시).'),
    '가계부 앱': dict(alias=['가계부', 'ledger'], parts=['ledger', 'calc', 'dday', 'prefs', 'pwa', 'monetize'], theme=('card', '#0ea5e9'), ref='가계부 앱',
        fill='계산기 식 하나(예: 이번 달 남은 돈)와 기다리는 날짜 3개(kits/dday/data/dates.json)를 독자 것으로 바꾼다. 가계부 입력은 방문자가 이 기기에서 직접 적는다.'),
}


def kind_find(word):
    w = (word or '').replace(' ', '')
    for k, v in KINDS.items():
        if w == k.replace(' ', '') or w in [a.replace(' ', '') for a in v['alias']]:
            return k
    return None


def ref_load():
    p = os.path.join(HERE, '참고', '서비스.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else []


def ref_cmd(rest):
    R = ref_load()
    if not R:
        print('참고/서비스.json 이 없습니다.'); return 1
    kinds = [r['kind'] for r in R]
    if not rest:
        print('참고 사이트가 있는 종류:'); [print(f'  - {r["kind"]} ({len(r["sites"])}곳)') for r in R]; print('\n사용: python run.py 참고 정보 매거진 [--shots 폴더]'); return 0
    w = ' '.join(rest).replace(' ', '')
    hit = [r for r in R if w in r['kind'].replace(' ', '') or r['kind'].replace(' ', '') in w]
    if not hit:
        print('그 종류가 없습니다:', ', '.join(kinds)); return 1
    r = hit[0]
    print(f'━━ 참고 사이트: {r["kind"]} ━━')
    br = None
    if SHOTS:
        sys.path.insert(0, HERE); import selftest as T; br = T.find_browser(); os.makedirs(SHOTS, exist_ok=True)
    for i, s_ in enumerate(r['sites'], 1):
        print(f'\n[{i}] {s_["url"]}\n  무엇을 하는 곳: {s_["what"]}\n  이렇게 번다: {s_["earns"]}\n  (확인: {s_["checked"]})', flush=True)
        if br:
            host = re.sub(r'[^a-z0-9]+', '_', s_['url'].split('//')[1].lower()).strip('_')[:30]
            out = os.path.join(SHOTS, f'참고_{r["kind"].replace(" ", "")}_{i}_{host}.png')
            try:
                subprocess.run([br, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,860', '--virtual-time-budget=8000', f'--screenshot={out}', s_['url']], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
                print('  화면 저장:', os.path.basename(out), flush=True)
            except Exception:
                print('  (화면 저장 실패: 이 사이트는 건너뜁니다)')
    print(f'\n우리는: {r["ours"]}')
    prog_add('참고 사이트 ' + r['kind']); return 0


def plan_cmd():
    p = os.path.join(HERE, '기획서.md')
    if os.path.exists(p):
        print(open(p, encoding='utf-8').read())
    else:
        print('기획서.md 가 아직 없습니다. 아래 양식을 독자와 한 칸씩 채워 기획서.md 로 저장하세요(한 번에 한 칸씩 묻기).\n'); print(open(os.path.join(HERE, '기획서_양식.md'), encoding='utf-8').read())
    return 0


def apply_name():
    """기획서.md 의 ⑥칸(「이름 — 한 줄 소개」) 또는 --이름/--소개 옵션을 site.local.json 의 name·tagline 에 넣는다."""
    name = tag = None
    if '--이름' in A and len(A) > A.index('--이름') + 1:
        name = A[A.index('--이름') + 1]
    if '--소개' in A and len(A) > A.index('--소개') + 1:
        tag = A[A.index('--소개') + 1]
    p = os.path.join(HERE, '기획서.md')
    if not name and os.path.exists(p):
        for ln in open(p, encoding='utf-8').read().splitlines():
            if ln.strip().startswith('|') and '⑥' in ln:
                cells = [c.strip() for c in ln.strip().strip('|').split('|')]
                if len(cells) >= 2 and cells[1]:
                    parts = re.split(r'\s+[—–-]\s+|\s*/\s*|\s*·\s*', cells[1], maxsplit=1)
                    name = parts[0].strip(); tag = tag or (parts[1].strip() if len(parts) > 1 else None)
    if not name:
        return None
    sp = os.path.join(HERE, 'site.local.json'); d = json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else {}
    d['name'] = name
    if tag:
        d['tagline'] = tag
    json.dump(d, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    return name, tag


def _text_shot(title, blocks, tag):
    """글을 읽기 좋은 한 장으로 그려 SHOTS 에 저장."""
    if not SHOTS:
        return
    import selftest as T
    br = T.find_browser()
    if not br:
        return
    os.makedirs(SHOTS, exist_ok=True); out = os.path.join(SHOTS, f'서비스_{tag}.png'); T.text_png(br, title, blocks, out); print('  화면 저장:', os.path.basename(out), flush=True)


def _shot_site(out_dir, pages, tag, width=1280, height=860):
    """site_local 의 쪽들을 headless 로 찍어 SHOTS 에 저장(--shots 가 없으면 건너뜀). 폭이 좁으면 휴대폰 흉내."""
    if not SHOTS:
        return
    import selftest as T
    os.makedirs(SHOTS, exist_ok=True)
    outs = [os.path.join(SHOTS, f'서비스_{tag}_{n}.png') for n in range(1, len(pages) + 1)]
    if T.shoot_pages(out_dir, pages, outs, width, height, mobile=width < 600):
        for o in outs:
            print('  화면 저장:', os.path.basename(o), flush=True)


def service_cmd(rest):
    if not rest:
        print('종류: ' + ' · '.join(KINDS) + '\n사용: python run.py 서비스 정보 매거진 [단계 1~9] [--shots 폴더]\n단계: 1 참고 사이트 · 2 기획서 · 3 기능 붙이기 · 4 내용 채우기 · 5 돈이 나올 자리 · 6 꼭 있어야 할 쪽 · 7 겉모습 · 8 휴대폰으로 보기 · 9 올릴 준비 점검(「올릴까요」에서 멈춤)\n나머지 예시(`python run.py 조립`)는 「이런 것도 붙일 수 있다」 목록입니다.'); return 0
    step = None
    if rest[-1].isdigit():
        step = int(rest[-1]); rest = rest[:-1]
    kind = kind_find(' '.join(rest))
    if not kind:
        print('종류를 찾지 못했습니다:', ' · '.join(KINDS)); return 1
    K = KINDS[kind]; steps = [step] if step else list(range(1, 10)); rc = 0
    for st in steps:
        print(f'\n━━ [{kind}] 걸음 {st}/9 ━━', flush=True)
        if st == 1:
            rc |= ref_cmd(kind.split())
        elif st == 2:
            print('기획서 한 장을 독자와 쓴다(누구에게·무엇을·날마다/주마다 무엇이 새로 실리나·돈이 나올 길·내가 쓸 시간). 한 번에 한 칸씩 묻고 기획서.md 로 저장.'); plan_cmd()
            pp = os.path.join(HERE, '기획서.md'); src_ = pp if os.path.exists(pp) else os.path.join(HERE, '기획서_양식.md')
            _text_shot('기획서 한 장' + ('' if os.path.exists(pp) else ' (양식 — 독자와 채울 칸)'), [('기획서.md' if os.path.exists(pp) else '기획서_양식.md', open(src_, encoding='utf-8').read())], f'{kind.replace(" ", "")}_2기획서')
        elif st == 3:
            nm = apply_name()
            if nm:
                print(f'기획서 ⑥칸의 이름을 사이트에 넣었습니다: 「{nm[0]}」' + (f' — {nm[1]}' if nm[1] else ''))
            else:
                print('(아직 사이트 이름이 정해지지 않았습니다 — 기획서 ⑥칸을 받거나 `--이름 "…" --소개 "…"` 를 주면 이 걸음부터 그 이름으로 찍습니다)')
            allp = list(json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))['parts'])
            set_parts(allp, False); set_parts(K['parts'], True); out, last, rcb = rebuild_local()
            labels, _ = menu_of(out)
            print(f'기획서에 맞는 기능을 붙였습니다: {", ".join(K["parts"])}  ({last})\n메뉴: {" · ".join(labels)}\n왜 이 기능들인지를 독자에게 한 줄씩 말한다(과외.md 5절).'); _shot_site(out, ['', 'calc/' if 'calc' in K['parts'] else ('recipes/' if 'recipes' in K['parts'] else 'search/')], f'{kind.replace(" ", "")}_3붙이기')
            prog_add(f'서비스 {kind}: 기능 붙임')
        elif st == 4:
            print('내용을 실제로 채운다 — 예시 자료를 지우고 독자 주제로 세션이 자료를 만든다:\n ' + K['fill'] + '\n지어낸 숫자는 「예시」 표시, 공식 자료에서 온 것은 출처를 적는다. 채운 뒤 python serve.py 로 열어 확인.')
            _text_shot('내용 채우기 — ' + kind, [('이 종류에서 채울 것', K['fill']), ('원칙', '예시 자료는 지우고 독자 주제로 바꾼다. 지어낸 숫자는 「예시」 표시, 공식 자료에서 온 것은 출처를 적는다. 모르는 것은 독자에게 묻고 지어내지 않는다.')], f'{kind.replace(" ", "")}_4내용')
        elif st == 5:
            apply_name(); set_parts(['monetize'], True); out, last, rcb = rebuild_local()
            print('돈이 나올 자리를 만들었습니다(광고 칸·제휴 링크 칸(고지 자동)·후원/문의 링크 칸·소식 받기 칸). 값은 site.local.json 의 monetize 에 넣습니다(kits/monetize/README.md).\n광고·제휴·후원 서비스의 가입과 심사는 사람이 합니다 — 에이전트는 안내만 합니다.'); _shot_site(out, [('calc/' if 'calc' in K['parts'] else ('recipes/' if 'recipes' in K['parts'] else 'search/')) + '@bottom', 'disclosure/'], f'{kind.replace(" ", "")}_5돈자리')
        elif st == 6:
            out = os.path.join(HERE, 'site_local')
            if not os.path.isdir(out):
                rebuild_local()
            need = ['about/', '소개'], ['contact/', '문의'], ['privacy/', '개인정보 처리방침'], ['disclosure/', '광고·제휴 고지(광고·제휴가 있을 때)']
            for pth, nm in need:
                ok = os.path.exists(os.path.join(out, pth, 'index.html'))
                print(('✓' if ok else '✗') + f' {nm}  (/{pth})')
            S_ = {}
            try:
                S_ = json.load(open(os.path.join(HERE, 'site.local.json'), encoding='utf-8'))
            except Exception:
                pass
            about = S_.get('about') or ''
            print('소개문(about):', ('있음(' + str(len(about)) + '자)' if about else '없음 — 독자에게 두세 문장으로 받아 site.local.json 의 about 에 넣는다'))
            _shot_site(out, ['about/', 'contact/', 'privacy/', 'disclosure/'], f'{kind.replace(" ", "")}_6필수쪽')
        elif st == 7:
            th, ac = K['theme']
            if SHOTS:   # 고르기 전에 틀 여섯 가지로 첫 화면을 찍어 나란히 보인다
                import selftest as T, tempfile
                names = {'paper': '신문형', 'card': '카드 잡지형', 'shop': '가게형', 'doc': '문서형', 'play': '놀이터형', 'one': '한 장짜리'}
                os.makedirs(SHOTS, exist_ok=True)
                for ti, tn in enumerate(names, 1):
                    tmpd = tempfile.mkdtemp(prefix='theme_')
                    env = dict(os.environ, SITE_BASE='/', SITE_URL='https://프로젝트이름.localhost', OUT_DIR=tmpd, SITE_THEME=tn, SITE_ACCENT=(ac if (tn == th and ac) else ''))
                    subprocess.run(PY + ['build.py'], cwd=HERE, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
                    o = os.path.join(SHOTS, f'서비스_{kind.replace(" ", "")}_7겉모습_{ti}_{tn}.png')
                    if T.shoot_pages(tmpd, [''], [o], 1280, 860):
                        print(f'  화면 저장: {os.path.basename(o)}  ({names[tn]})', flush=True)
            print(f'겉모습 후보(독자와 고른다): 신문형 paper · 카드 잡지형 card · 가게형 shop · 문서형 doc · 놀이터형 play · 한 장짜리 one. 이 종류의 추천: {th} {ac}\n고르면 site.local.json 에 "theme": "…", "accent": "#색" 을 넣고 다시 찍는다(python run.py 지금 → serve).')
            if '--적용' in A:
                pth = os.path.join(HERE, 'site.local.json'); d = json.load(open(pth, encoding='utf-8')) if os.path.exists(pth) else {}
                d['theme'] = th
                if ac:
                    d['accent'] = ac
                json.dump(d, open(pth, 'w', encoding='utf-8'), ensure_ascii=False, indent=2); out, last, rcb = rebuild_local(); print('추천 틀을 적용했습니다:', last); _shot_site(out, [''], f'{kind.replace(" ", "")}_7겉모습')
        elif st == 8:
            out = os.path.join(HERE, 'site_local')
            if not os.path.isdir(out):
                rebuild_local()
            print('휴대폰 폭(390px)으로도 열어 봅니다.'); _shot_site(out, ['', 'search/'], f'{kind.replace(" ", "")}_8휴대폰', 390, 844)
        elif st == 9:
            rb = subprocess.run(PY + ['audit.py', '--dir', 'site_local'], cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace'); print((rb.stdout + rb.stderr).strip()[-900:])
            print('\n주소 값(site.json 의 url·base)과 올릴 곳은 독자가 정합니다. 올리기는 하지 않았습니다.\n▶ 올릴까요? (이 자리에서 멈춥니다 — 독자가 「올려」라고 할 때만, 가입·로그인은 독자 몫)')
    return rc


POLFILE = os.path.join(HERE, '다듬기.json')
THINK = os.path.join(HERE, '생각.md')
MEAS = os.path.join(HERE, '만듦새.json')


def pol_steps():
    return json.load(open(POLFILE, encoding='utf-8'))['steps']


def local_load():
    fp = os.path.join(HERE, 'site.local.json')
    return json.load(open(fp, encoding='utf-8')) if os.path.exists(fp) else {}


def local_save(d):
    json.dump(d, open(os.path.join(HERE, 'site.local.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def cur_polish():
    return {str(k): v for k, v in (local_load().get('polish') or {}).items() if v}


def build_tmp(polish=None):
    """지금 설정(site.local.json)으로 임시 폴더에 찍는다. polish 를 주면 그 층 설정으로(미리보기)."""
    import tempfile
    out = tempfile.mkdtemp(prefix='polish_')
    env = dict(os.environ, SITE_BASE='/', SITE_URL='https://프로젝트이름.localhost', OUT_DIR=out)
    if polish is not None:
        env['SITE_POLISH'] = json.dumps(polish)
    subprocess.run(PY + ['build.py'], cwd=HERE, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return out


def newest_note(out):
    nd = os.path.join(out, 'n')
    ids = sorted(os.listdir(nd), reverse=True) if os.path.isdir(nd) else []
    return ids[0] if ids else None


def score_site(out):
    """첫 화면(PC)·글 쪽(PC)·휴대폰 첫 화면의 만듦새 측정. {'pc':…, 'note':…, 'mobile':…}"""
    import selftest as T
    nid = newest_note(out); res = {}
    pcs = T.measure_site(out, [''] + ([f'n/{nid}/'] if nid else []), 1280, 860, False)
    res['pc'] = pcs[0] if pcs else {}
    if nid and len(pcs) > 1:
        res['note'] = pcs[1]
    mob = T.measure_site(out, [''], 390, 844, True)
    res['mobile'] = mob[0] if mob else {}
    return res


def grade_lines(res):
    import selftest as T
    lines = []; ok_n = tot = 0
    for lab, key in (('PC 첫 화면', 'pc'), ('PC 글 쪽', 'note'), ('휴대폰 첫 화면', 'mobile')):
        m = res.get(key)
        if not m:
            continue
        gl = T.grade(m, imgs_needed=(key != 'note'))
        row = []
        for k, nm, v, th, ok in gl:
            tot += 1; ok_n += 1 if ok else 0
            row.append(f'{nm} {v}{"" if ok else " ✗(" + th + ")"}')
        lines.append(f'  {lab}: ' + ' · '.join(row))
    return lines, ok_n, tot


def shots_for(out, tag):
    if not SHOTS:
        return
    import selftest as T
    os.makedirs(SHOTS, exist_ok=True); nid = newest_note(out)
    jobs = [(['', ], [os.path.join(SHOTS, f'다듬기_{tag}_PC첫화면.png')], 1280, 860, False)]
    if nid:
        jobs.append(([f'n/{nid}/'], [os.path.join(SHOTS, f'다듬기_{tag}_글쪽.png')], 1280, 860, False))
    jobs.append((['', ], [os.path.join(SHOTS, f'다듬기_{tag}_휴대폰.png')], 390, 844, True))
    for pages, outs, w, h, mob in jobs:
        if T.shoot_pages(out, pages, outs, w, h, mob):
            print('  화면 저장:', outs[0], flush=True)


def polish_cmd(rest):
    steps = pol_steps(); cur = cur_polish()
    opt = A[A.index('--안') + 1].upper() if '--안' in A and len(A) > A.index('--안') + 1 else None
    if not rest:
        print('다듬기 걸음(출발 모습 → 고품질). 지금 적용: ' + (', '.join(f'{k}{v}' for k, v in sorted(cur.items(), key=lambda x: int(x[0]))) or '없음(출발 모습)'))
        for st in steps:
            mark = ('적용 ' + cur[str(st['n'])]) if str(st['n']) in cur else ('준비됨' if st['status'] == 'ready' else '준비 중')
            print(f'  {st["n"]:>2}. {st["title"]}  [{mark}]')
        print('\n사용: python run.py 다듬기 1  (안 A·B 미리보기) → 독자가 고르면 python run.py 다듬기 1 --안 A --shots 폴더'); return 0
    if rest[0] in ('다음', 'next'):
        nxt = next((st for st in steps if st['status'] == 'ready' and str(st['n']) not in cur), None)
        if not nxt:
            print('준비된 걸음을 모두 적용했습니다.'); return 0
        n = nxt['n']
    elif rest[0].isdigit():
        n = int(rest[0])
    else:
        print('사용: python run.py 다듬기 [번호|다음]'); return 1
    st = next((x for x in steps if x['n'] == n), None)
    if not st:
        print('그런 걸음이 없습니다'); return 1
    if st['status'] != 'ready':
        print(f'걸음 {n} 「{st["title"]}」 은(는) 아직 준비 중입니다.'); return 0
    print(f'━━ 다듬기 {n}. {st["title"]} ━━\n왜 하는가: {st["why"]}\n참고 사이트는: {st["ref"]}')
    print('안: ' + ' / '.join(f'{k}) {v}' for k, v in st['options'].items()), flush=True)
    pre = build_tmp(cur); shots_for(pre, f'{n}_전')
    if opt is None:   # 미리보기: 안마다 첫 화면을 찍어 독자가 고르게 한다
        import selftest as T
        for o in st['options']:
            out = build_tmp({**cur, str(n): o})
            if SHOTS:
                os.makedirs(SHOTS, exist_ok=True); fp = os.path.join(SHOTS, f'다듬기_{n}_안{o}_PC첫화면.png')
                if T.shoot_pages(out, [''], [fp], 1280, 860):
                    print(f'  미리보기 저장: {fp}  ({o}안)', flush=True)
        print(f'\n독자에게 먼저 묻는다: 「어느 쪽이 마음에 드나요? 왜요?」 → 정리해서 생각.md 에 적고(python run.py 정리 …), 「이렇게 이해했습니다: … 이대로 적용할까요?」 확인 뒤 python run.py 다듬기 {n} --안 A|B')
        return 0
    if opt not in st['options']:
        print('안은 ' + ' · '.join(st['options']) + ' 중 하나입니다'); return 1
    sb = score_site(pre)
    d = local_load(); d.setdefault('polish', {})[str(n)] = opt; local_save(d)
    out, last, rcb = rebuild_local()
    shots_for(out, f'{n}_후')
    sa = score_site(out)
    lb, ob, tb = grade_lines(sb); la, oa, ta = grade_lines(sa)
    print(f'\n적용했습니다: 걸음 {n} · {opt}안 — 점수(통과한 항목) {ob}/{tb} → {oa}/{ta}\n[전]'); print('\n'.join(lb)); print('[후]'); print('\n'.join(la))
    json.dump(sa, open(MEAS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\n확인 물음: {st["ask"]}   (답을 먼저 말하지 않는다 — 힌트: {st["ask_hint"]})')
    prog_add(f'다듬기 {n} {st["title"]} {opt}안')
    return 0


def undo_cmd(rest):
    if not rest or not rest[0].isdigit():
        print('사용: python run.py 되돌리기 <번호>'); return 1
    d = local_load(); p = d.get('polish') or {}
    if str(int(rest[0])) not in p:
        print('그 걸음은 적용돼 있지 않습니다'); return 0
    p.pop(str(int(rest[0]))); d['polish'] = p; local_save(d)
    out, last, rcb = rebuild_local()
    if SHOTS:
        shots_for(out, f'되돌리기{rest[0]}')
    print(f'걸음 {rest[0]} 를 되돌렸습니다({last}). 지금 적용: ' + (', '.join(f'{k}{v}' for k, v in sorted(p.items(), key=lambda x: int(x[0]))) or '없음(출발 모습)')); prog_add(f'다듬기 {rest[0]} 되돌림'); return 0


def quality_cmd():
    out, last, rcb = rebuild_local()
    res = score_site(out); lines, ok_n, tot = grade_lines(res)
    print(f'━━ 만듦새(참고 사이트와 같은 급으로 보이는가) — 통과 {ok_n}/{tot} ━━'); print('\n'.join(lines))
    bad = []
    for lab, key in (('PC 첫 화면', 'pc'), ('휴대폰 첫 화면', 'mobile')):
        m = res.get(key) or {}
        if m.get('minFontEl') and m.get('minFont', 99) < 13:
            bad.append(f'가장 작은 글자 {m["minFont"]}px: {m["minFontEl"]}')
        if m.get('minContrastEl') and m.get('minContrast', 99) < 4.5:
            bad.append(f'낮은 대비 {m["minContrast"]}: {m["minContrastEl"]}')
    for b in bad[:4]:
        print('  ✗', b)
    shots_for(out, '만듦새')
    json.dump(res, open(MEAS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('다듬기로 올릴 수 있는 것: python run.py 다듬기'); return 0 if ok_n == tot else 1


def compare_cmd(rest):
    R = ref_load(); import selftest as T, base64
    kind = ' '.join(rest) if rest else '정보 매거진'
    hit = next((r for r in R if kind.replace(' ', '') in r['kind'].replace(' ', '')), None)
    if not hit or not hit['sites']:
        print('참고 사이트를 찾지 못했습니다'); return 1
    br = T.find_browser(); os.makedirs(SHOTS or os.path.join(HERE, '비교'), exist_ok=True); d = SHOTS or os.path.join(HERE, '비교')
    out = build_tmp(cur_polish()); mine = os.path.join(d, '비교_내화면.png'); ref = os.path.join(d, '비교_참고화면.png')
    T.shoot_pages(out, [''], [mine], 1280, 860)
    subprocess.run([br, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,860', '--virtual-time-budget=8000', f'--screenshot={ref}', hit['sites'][0]['url']], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    import tempfile
    html = '<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#222;color:#fff;font:15px "Malgun Gothic",sans-serif}div{display:flex;gap:12px;padding:12px}figure{margin:0;flex:1}img{width:100%;display:block;border:2px solid #fff}figcaption{padding:6px 0;font-weight:700}</style><div>'
    for cap, fp in (('참고 사이트: ' + hit['sites'][0]['url'], ref), ('우리 사이트(지금 모습)', mine)):
        html += f'<figure><figcaption>{cap}</figcaption><img src="data:image/png;base64,{base64.b64encode(open(fp, "rb").read()).decode()}"></figure>' if os.path.exists(fp) else f'<figure><figcaption>{cap} (화면 없음)</figcaption></figure>'
    html += '</div>'
    hf = os.path.join(tempfile.mkdtemp(), 'c.html'); open(hf, 'w', encoding='utf-8').write(html); res = os.path.join(d, '비교_나란히.png')
    subprocess.run([br, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=2600,1000', f'--screenshot={res}', 'file:///' + hf.replace(chr(92), '/')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    print('나란히 비교 그림:', res); return 0


def think_cmd():
    print(open(THINK, encoding='utf-8').read() if os.path.exists(THINK) else '생각.md 가 아직 없습니다. 독자가 하고 싶은 말을 받으면 python run.py 정리 "<독자의 말>" 로 남기세요.'); return 0


def organize_cmd(rest):
    def opt(k):
        return A[A.index(k) + 1] if k in A and len(A) > A.index(k) + 1 else ''
    words = [w for i, w in enumerate(rest) if not w.startswith('--') and (i == 0 or not rest[i - 1].startswith('--'))]
    said = ' '.join(words).strip()
    if not said:
        print('사용: python run.py 정리 "<독자의 말>" --한줄 "<세션이 정리한 한 줄>" --정함 "a;b" --미정 "c" --미룸 "d"'); return 1
    new = not os.path.exists(THINK)
    with open(THINK, 'a', encoding='utf-8') as f:
        if new:
            f.write('# 생각 — 독자의 말과 세션이 정리한 것\n> 세션이 곧바로 만들지 않고 먼저 정리한 기록입니다. 다음에 열면 이것부터 읽고 「지난번에 이렇게 정하셨습니다」로 시작합니다. 기획서.md 는 여기서 뽑아 만듭니다.\n')
        f.write(f'\n## {time.strftime("%Y-%m-%d %H:%M")}\n- **독자의 말**: {said}\n- **정리한 한 줄**: {opt("--한줄") or "(아직)"}\n')
        for lab, k in (('정한 것', '--정함'), ('아직 안 정한 것', '--미정'), ('미룬 것', '--미룸')):
            if opt(k):
                f.write(f'- **{lab}**: ' + '; '.join(x.strip() for x in opt(k).split(';') if x.strip()) + '\n')
    print('생각.md 에 적었습니다. 확인받기: 「이렇게 이해했습니다: … 이대로 만들까요?」'); return 0



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
    print('① 꼭 알아야 할 것(위에서부터 3가지)')
    mk = (kit_json(k['name']) or {}).get('must_know') or []
    for m_ in mk[:3]:
        print('  -', m_.get('알것', ''))
        if '--풀이' in A:
            print('    까닭:', m_.get('까닭', ''), '/ 모르면:', m_.get('모르면', ''), '/ 근거:', m_.get('근거', ''))
    print('확인 물음(스스로 답해 보세요 — 답은 독자가 먼저 말하게 합니다):')
    for qi, m_ in enumerate(mk[:3], 1):
        print(f'  Q{qi}. 「{m_.get("알것", "")[:40]}」 — 모르면 어떤 일이 생길까요?')
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
    if cmd in ('다듬기', 'polish'):
        return polish_cmd(rest)
    if cmd in ('되돌리기', 'undo'):
        return undo_cmd(rest)
    if cmd in ('만듦새', 'quality'):
        return quality_cmd()
    if cmd in ('비교', 'compare'):
        return compare_cmd(rest)
    if cmd in ('생각', 'think'):
        return think_cmd()
    if cmd in ('정리', 'organize'):
        return organize_cmd(rest)
    if cmd in ('참고', 'ref'):
        return ref_cmd(rest)
    if cmd in ('기획서', 'plan'):
        return plan_cmd()
    if cmd in ('서비스', 'service'):
        return service_cmd(rest)
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
