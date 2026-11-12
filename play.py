# -*- coding: utf-8 -*-
"""에이전트와 고쳐 가는 길: 본(본뜬 출발점 띄우기) · 바꿔/바꿨다(말 한 줄로 무엇이든 고치고 스스로 확인) · 간직과 되돌리기(마지막·처음) · 손잡이 · 나누기. run.py 가 부른다. 파이썬 기본 기능만 쓴다.
고치기 전 모습은 .간직/<번호>/ 에 저절로 간직한다(설정·글·기능 자료·틀 파일 — git 에는 올라가지 않는다)."""
import json, os, shutil, time

HERE = os.path.dirname(os.path.abspath(__file__))
KEEP = os.path.join(HERE, '.간직')
PIECES = os.path.join(HERE, '참고', '조각')
PLAT = os.path.join(HERE, '참고', '플랫폼.json')


# ---------------------------------------------------------------- 간직·되돌리기
def _items():
    """간직하는 것: 내 설정·글·기능 자료와 틀 파일(*.py·server·kits) 전부. 그래서 무엇을 고쳐도 돌아온다."""
    out = ['site.local.json', 'site.json', '다듬기.json', 'notes', 'posts', 'kits', 'server']
    out += ['shop/api/modules', 'shop/api/modules.json', 'shop/api/data/products.json', 'shop/web/app', 'shop/web/components', 'shop/web/lib', 'shop/web/site.json', 'shop/web/public']
    out += sorted(f for f in os.listdir(HERE) if f.endswith('.py'))
    return out


def snap(what):
    """지금 모습을 간직한다. 돌려주는 값 = 번호."""
    os.makedirs(KEEP, exist_ok=True)
    nums = sorted(int(x) for x in os.listdir(KEEP) if x.isdigit())
    n = (nums[-1] + 1) if nums else 0
    d = os.path.join(KEEP, str(n)); os.makedirs(d)
    for it in _items():
        src = os.path.join(HERE, it)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(d, it))
        elif os.path.isfile(src):
            os.makedirs(os.path.dirname(os.path.join(d, it)) or d, exist_ok=True); shutil.copy2(src, os.path.join(d, it))
    json.dump({'t': time.strftime('%Y-%m-%d %H:%M:%S'), 'what': what, 'had_local': os.path.exists(os.path.join(HERE, 'site.local.json'))}, open(os.path.join(d, '_무엇.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    for old in nums[:-20]:   # 스무 개까지만(처음 모습 0번은 남긴다)
        if old != 0:
            shutil.rmtree(os.path.join(KEEP, str(old)), ignore_errors=True)
    return n


def snaps():
    if not os.path.isdir(KEEP):
        return []
    out = []
    for x in sorted((int(x) for x in os.listdir(KEEP) if x.isdigit())):
        try:
            m = json.load(open(os.path.join(KEEP, str(x), '_무엇.json'), encoding='utf-8'))
        except Exception:
            m = {'t': '', 'what': ''}
        out.append((x, m))
    return out


def restore(n, drop_later=True):
    d = os.path.join(KEEP, str(n)); m = json.load(open(os.path.join(d, '_무엇.json'), encoding='utf-8'))
    for it in _items():
        src = os.path.join(d, it); dst = os.path.join(HERE, it)
        if os.path.isdir(src):
            shutil.rmtree(dst, ignore_errors=True); shutil.copytree(src, dst)
        elif os.path.isfile(src):
            shutil.copy2(src, dst)
    if not m.get('had_local') and os.path.exists(os.path.join(HERE, 'site.local.json')):
        os.remove(os.path.join(HERE, 'site.local.json'))
    if drop_later:
        for x, _ in snaps():
            if x > n or (x == n and n != 0):
                shutil.rmtree(os.path.join(KEEP, str(x)), ignore_errors=True)
    return m


def undo_cmd(R, rest):
    """되돌리기 (마지막) · 되돌리기 처음 · 되돌리기 목록. 숫자(다듬기 걸음)는 run.py 의 걸음 되돌리기가 맡는다."""
    L = snaps()
    if rest and rest[0] == '목록':
        print('간직해 둔 모습(고치기 직전마다 저절로 간직합니다):'); [print(f'  {x}. {m["t"]} — {m["what"]} 하기 전') for x, m in L] or print('  (없음)'); return 0
    if not L:
        print('되돌릴 것이 없습니다(아직 아무것도 바꾸지 않았습니다).'); return 0
    if os.path.exists(PENDING):   # 하던 고침이 있었으면 접는다(되돌린 뒤의 바꿨다 가 엉뚱한 기준과 견주지 않게)
        os.remove(PENDING)
    if rest and rest[0] == '처음':
        m = restore(L[0][0]); what = '처음 모습(맨 처음 무언가를 바꾸기 전)'
    else:
        m = restore(L[-1][0]); what = f'「{m["what"]}」 하기 전 모습'
    out, last, rc = R.rebuild_local()
    R.shots_for(out, '되돌리기')
    print(f'되돌렸습니다 → {what}. ({last})\n겁내지 않아도 됩니다: 무엇을 바꾸든 python run.py 되돌리기 한 줄로 돌아옵니다(처음 모습은 되돌리기 처음, 목록은 되돌리기 목록).'); R.prog_add('되돌리기: ' + what); return 0


# ---------------------------------------------------------------- 바꿔 / 바꿨다 (걸음 없이 하는 작은 고침)
PENDING = os.path.join(KEEP, '_바꾸는중.json')


def change_cmd(R, rest):
    what = ' '.join(rest).strip()
    if not what:
        print('사용: python run.py 바꿔 "<독자가 한 말 그대로>"   예: 바꿔 "글마다 댓글을 달 수 있게"\n고치기 전 모습을 간직한 뒤 세션이 고치고, python run.py 바꿨다 로 스스로 확인하고 전·후를 보입니다.'); return 1
    n = snap(what); os.makedirs(KEEP, exist_ok=True)
    before = None
    if R.SHOTS:
        import selftest as T
        os.makedirs(R.SHOTS, exist_ok=True); before = os.path.join(R.SHOTS, f'바꿔_{n}_전.png'); T.shoot_pages(R.build_tmp(R.cur_polish()), [''], [before], 1280, 860)
    json.dump({'n': n, 'what': what, 'before': before, 't0': time.time()}, open(PENDING, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'지금 모습을 간직했습니다({n}번) — 설정·글·자료·틀 파일 전부. 이제 「{what}」를 고칩니다.\n'
          '[어디든 고쳐도 됩니다] 이름·소개·색 → site.local.json / 글 → notes/·posts/ / 기능 자료 → kits/<기능>/data/ / 화면 틀·새 기능 → *.py·kits/·server/\n'
          '[고친 뒤] python run.py 바꿨다 "<무엇을 고쳤는지 한 줄>" — 구문·찍기를 스스로 확인하고, 깨졌으면 알려 줍니다(python run.py 되돌리기 한 줄로 돌아옴).'); return 0


def _check():
    """고친 뒤 스스로 확인: 틀 파일 구문 → 사이트 찍기. 돌려주는 값 = 안 된 것 목록."""
    import ast
    bad = []
    for f in sorted(x for x in os.listdir(HERE) if x.endswith('.py')):
        try:
            ast.parse(open(os.path.join(HERE, f), encoding='utf-8').read())
        except SyntaxError as e:
            bad.append(f'{f} {e.lineno}행: {e.msg}')
    return bad


def _changed(n):
    """간직해 둔 n번과 지금을 견줘 달라진 파일 이름들."""
    import filecmp
    d = os.path.join(KEEP, str(n)); out = []

    def walk(rel):
        a = os.path.join(d, rel); b = os.path.join(HERE, rel)
        if os.path.isdir(a) or os.path.isdir(b):
            names = set(os.listdir(a) if os.path.isdir(a) else []) | set(os.listdir(b) if os.path.isdir(b) else [])
            for x in sorted(names):
                if x != '__pycache__':
                    walk(os.path.join(rel, x))
        elif not (os.path.isfile(a) and os.path.isfile(b) and filecmp.cmp(a, b, shallow=False)):
            out.append(rel.replace(os.sep, '/'))
    for it in _items():
        if os.path.exists(os.path.join(d, it)) or os.path.exists(os.path.join(HERE, it)):
            walk(it)
    return out


def _seen(out, want):
    """찍힌 사이트(html·css·js)에 그 글자가 있는지."""
    seen = {w: False for w in want}
    if not want:
        return seen
    for root, _, fs in os.walk(out):
        for f in fs:
            if f.endswith(('.html', '.css', '.js', '.json', '.xml')):
                try:
                    t = open(os.path.join(root, f), encoding='utf-8', errors='replace').read()
                except Exception:
                    continue
                for w in want:
                    if not seen[w] and w in t:
                        seen[w] = True
        if all(seen.values()):
            break
    return seen


def _flow(said, did, files, check, secs):
    """흐름 한 줄을 기록/흐름.md 에 쌓는다: 들어온 말 → 한 일 → 고친 파일 → 스스로 확인 → 걸린 시간 → 되돌리는 한 줄."""
    fp = os.path.join(HERE, '기록', '흐름.md'); os.makedirs(os.path.dirname(fp), exist_ok=True)
    new = not os.path.exists(fp)
    with open(fp, 'a', encoding='utf-8') as f:
        if new:
            f.write('# 흐름 — 말 한 줄이 들어와 무엇이 되었나\n\n| 때 | 들어온 말 | 한 일 | 고친 파일 | 스스로 확인 | 걸린 시간 | 되돌리기 |\n|---|---|---|---|---|---|---|\n')
        c = lambda x: str(x).replace('|', '/').replace('\n', ' ')
        f.write(f'| {time.strftime("%m-%d %H:%M")} | {c(said)} | {c(did)} | {c(", ".join(files) or "-")} | {check} | {secs:.0f}초 | python run.py 되돌리기 |\n')


def changed_cmd(R, rest):
    if not os.path.exists(PENDING):
        print('먼저 python run.py 바꿔 "<독자가 한 말>" 로 시작하세요(고치기 전 모습을 간직합니다).'); return 1
    p = json.load(open(PENDING, encoding='utf-8'))
    if not os.path.isdir(os.path.join(KEEP, str(p['n']))):
        os.remove(PENDING); print('견줄 기준(고치기 전 모습)이 없습니다 — 그 사이에 되돌렸습니다. python run.py 바꿔 "<독자가 한 말>" 로 다시 시작하세요.'); return 1
    bad = _check()
    if bad:
        print('✗ 확인에서 걸렸습니다(구문):\n  ' + '\n  '.join(bad) + '\n고쳐서 다시 python run.py 바꿨다 를 부르거나, python run.py 되돌리기 로 고치기 전으로 돌아갑니다.'); return 1
    out, last, rc = R.rebuild_local()
    if rc != 0:
        print('✗ 확인에서 걸렸습니다(사이트 찍기). 위 오류를 고쳐 다시 python run.py 바꿨다 를 부르거나, python run.py 되돌리기 로 돌아갑니다.'); return 1
    want = [R.A[i + 1] for i, a in enumerate(R.A[:-1]) if a == '--보임']   # 시킨 것이 화면에 나타났는가: 찍힌 사이트에서 이 글자들을 찾는다
    rest = [x for x in rest if x not in want]
    did = ' '.join(rest).strip() or p['what']
    seen = _seen(out, want); miss = [w for w in want if not seen[w]]
    files = _changed(p['n']); secs = time.time() - p['t0']
    if not miss:
        os.remove(PENDING)   # 안 보이는 것이 있으면 접지 않는다: 고쳐서 다시 바꿨다 를 부르면 같은 기준과 견준다
    _flow(p['what'], did, files, '구문 ✓ · 찍기 ✓' + (f' · 화면에 나타남 {len(want) - len(miss)}/{len(want)}' if want else ''), secs)
    if R.SHOTS and p.get('before') and os.path.exists(p['before']):
        import selftest as T
        after = os.path.join(R.SHOTS, f'바꿔_{p["n"]}_후.png'); T.shoot_pages(out, [''], [after], 1280, 860)
        R.side_by_side(p['before'], after, os.path.join(R.SHOTS, f'바꿔_{p["n"]}_전후.png'), '고치기 전', '고친 뒤')
    print(f'✓ 고쳤습니다: {did}  ({secs:.0f}초)\n  고친 파일: ' + (', '.join(files[:8]) or '(없음)') + (f' 외 {len(files) - 8}개' if len(files) > 8 else ''))
    if want:
        print(f'{"✓" if not miss else "✗"} 시킨 것이 화면에 나타났는가: {len(want) - len(miss)}/{len(want)}' + (' — 안 보이는 것: ' + ', '.join(f'「{m}」' for m in miss) + ' → 고쳐서 다시 확인하거나 독자에게 그대로 말합니다' if miss else ''))
    else:
        print('– 시킨 것이 화면에 나타났는지는 아직 보지 않았습니다(--보임 "화면에 보여야 할 글자" 를 붙이면 찍힌 사이트에서 찾아 줍니다).')
    print(f'✓ 스스로 확인: 틀 파일 구문 통과 · 사이트 찍기 통과({last})\n마음에 안 들면 python run.py 되돌리기 한 줄로 고치기 전으로 돌아갑니다.\n[다음] 고친 화면을 독자에게 열어 보이고, 다음에 바꾸고 싶은 것을 한 줄로 받습니다.')
    if miss:
        print('아직 끝나지 않았습니다 — 고친 뒤 같은 줄로 python run.py 바꿨다 … --보임 … 을 다시 부르면 됩니다(다시 바꿔 를 부르지 않아도 됩니다).'); return 1
    R.prog_add('바꿈: ' + did); status_cmd(R); return 0


# ---------------------------------------------------------------- 상태창 (잰 것만 적는다)
def status_cmd(R, rest=None):
    """게임의 상태창처럼: 네 고개(만들었다·올렸다·고쳐 봤다·운영팀)와 지금까지 잰 숫자, 다음에 열리는 것."""
    done = [x['what'] for x in R.prog_load().get('done', [])]; L = R.local_load()
    mirrors = [w[2:].strip() for w in done if w.startswith('본 ')]
    changes = [w for w in done if w.startswith('바꿈: ')]; undos = [w for w in done if w.startswith('되돌리기')]
    autos = [w for w in done if w.startswith('자동 ')]
    url = str(L.get('url') or ''); live = url.startswith('http') and 'localhost' not in url and '프로젝트이름' not in url
    card = R.svc_load(); filled = sum(1 for c in R.SVC_CARDS if card.get(c)); files = set()
    fp = os.path.join(HERE, '기록', '흐름.md')
    if os.path.exists(fp):
        for ln in open(fp, encoding='utf-8').read().splitlines()[4:]:
            c = [x.strip() for x in ln.strip('|').split('|')]
            if len(c) >= 4 and c[3] != '-':
                files.update(x.strip() for x in c[3].split(','))
    sched = False
    if os.name == 'nt' and any('예약' in a for a in autos):
        import subprocess
        sched = subprocess.run(['schtasks', '/Query', '/TN', 'MyServiceDaily'], capture_output=True).returncode == 0
    q = [('만들었다', bool(mirrors), '본뜬 것: ' + (', '.join(dict.fromkeys(mirrors)) or '아직')),
         ('올렸다', live, '공개 주소: ' + (url if live else '아직')),
         ('고쳐 봤다', len(changes) >= 3, f'말 한 줄로 고친 것 {len(changes)}번 · 되돌린 것 {len(undos)}번 · 손댄 파일 {len(files)}개'),
         ('운영팀', any('맛보기' in a for a in autos), f'사람 없이 돈 것 {sum(1 for a in autos if "맛보기" in a)}번 · 방송 화면 {"켜 봄" if any("방송" in a for a in autos) else "아직"} · 날마다 예약 {"걸림" if sched else "아직"}')]
    lv = sum(1 for _, ok, _ in q if ok)
    nxt = next((n for n, ok, _ in q if not ok), None)
    hint = {'만들었다': '「시작하자」', '고쳐 봤다': '바꾸고 싶은 것을 한 줄로(세 번이면 열립니다)', '올렸다': '「올려 보자」', '운영팀': '「3장을 진행해 보자」'}
    name = L.get('name') or '내 사이트'
    print('┌─ 상태창 ' + '─' * 44)
    print(f'│ {name}   고개 {lv}/4   내 서비스 한 장 {filled}/{len(R.SVC_CARDS)}칸')
    for n, ok, d in q:
        print(f'│ {"■" if ok else "□"} {n:<6} {d}')
    print('│ 다음에 열리는 것: ' + (f'{nxt} — {hint[nxt]}' if nxt else '없음 — 튜토리얼 끝. 이제부터는 차례가 없습니다'))
    print('└' + '─' * 52)
    return 0


# ---------------------------------------------------------------- 본(유명 플랫폼을 본뜬 출발점) 띄우기
MIRRORS = {
    '가게': dict(name='종합 쇼핑몰', ref='쿠팡', shop=True),
    '글': dict(name='글 읽는 곳', ref='미디엄', polish={}, frame='medium'),
    '게시판': dict(name='링크와 추천 게시판', ref='해커 뉴스', kind='커뮤니티(링크+추천 게시판)'),
    '장터': dict(name='디지털 상품 장터', ref='검로드', kind='쇼핑몰(디지털 상품 장터)'),
    '순위': dict(name='날마다 순위', ref='깃허브 트렌딩', kind='날마다 순위(트렌딩)'),
}


def mirror_cmd(R, rest):
    """본 [글|게시판|장터|순위] — 독자가 고르는 걸음 없이, 본뜬 출발점을 한 번에 띄운다(튜토리얼의 첫 화면)."""
    if not rest or rest[0] not in MIRRORS:
        print('━━ 본 — 본뜬 출발점을 한 번에 띄웁니다 ━━')
        for k, m in MIRRORS.items():
            print(f'  python run.py 본 {k:<4} {m["name"]} (본: {m["ref"]})' + (' — 화면 Next.js + 백엔드 파이썬 + 앱, 결제 없음' if m.get('shop') else '' if 'polish' in m else ' — 받는 것이 있어 서버가 붙습니다'))
        return 0 if not rest else 1
    key = rest[0]; m = MIRRORS[key]; t0 = time.time(); snap(f'본 {key} 띄우기')
    if m.get('shop'):
        return R.sh(['shop.py', '켜기'] + [a for a in R.A[2:]]) or (R.prog_add('본 가게') or status_cmd(R))
    if 'polish' in m:
        L = R.local_load(); L['polish'] = dict(m['polish']); L['frame'] = m.get('frame', ''); R.local_save(L)
        out, last, rc = R.rebuild_local()
    else:
        R.record_choice('변환', '바꿈', f'본 {key} 로 시작')
        if '--적용' not in R.A:
            R.A.append('--적용')
        rc = R.convert_cmd([m['kind']]); out = os.path.join(HERE, 'site_local'); last = ''
    if rc != 0:
        print('✗ 띄우지 못했습니다. python run.py 되돌리기 로 돌아갈 수 있습니다.'); return 1
    R.shots_for(out, '본_' + key)
    print(f'\n✓ 「{m["name"]}」(본: {m["ref"]})을 띄웠습니다 — {time.time() - t0:.0f}초. {last}\n[다음] python serve.py --open --no-demo 로 열어 독자에게 보이고, 코스의 첫 과제(이름을 내 것으로)로 갑니다. 처음으로 돌아가려면 python run.py 되돌리기 처음')
    R.prog_add('본 ' + key); status_cmd(R); return 0


# ---------------------------------------------------------------- 손잡이
def _first_product():
    try:
        P = json.load(open(os.path.join(HERE, 'kits', 'market', 'data', 'products.json'), encoding='utf-8'))
        return next((p['slug'] for p in P if p.get('pwyw')), P[0]['slug'])
    except Exception:
        return ''


def knob_cmd(R, rest):
    import knobs as KN
    L = R.local_load(); K = L.get('knobs') or {}; cur = R.cur_polish()
    if not rest:
        print('━━ 손잡이 — 돌려 보면 화면이 바로 바뀝니다 ━━')
        for nm, d in KN.DEFS.items():
            v = K.get(d['key']); need = KN.NEED.get(nm)
            print(f'  {nm:<6} 지금 {v if v is not None else "기본"} · 레퍼런스 {d["ref"]}{d["unit"]} · 돌릴 수 있는 값 {" / ".join(str(x) for x in d["vals"])}' + (f'  (다듬기 {need} 을 얹은 뒤에 보입니다)' if need and str(need) not in cur else ''))
        print('\n돌려 보기: python run.py 손잡이 본문폭 760 [--shots 폴더]   ·   원래대로: python run.py 손잡이 본문폭 기본   ·   되돌리기: python run.py 되돌리기'); return 0
    nm = rest[0]
    if nm not in KN.DEFS:
        print('그런 손잡이가 없습니다: ' + ' · '.join(KN.DEFS)); return 1
    d = KN.DEFS[nm]
    if len(rest) < 2:
        print(f'━━ 손잡이 · {nm} ━━\n지금 {K.get(d["key"], "기본")} · 레퍼런스 {d["ref"]}{d["unit"]}\n[원래 그 플랫폼은 이렇게 해 두었고, 그 까닭은] {d["why"]}\n돌릴 수 있는 값: {" / ".join(str(x) for x in d["vals"])}'); return 0
    before = None
    if R.SHOTS:
        import selftest as T
        os.makedirs(R.SHOTS, exist_ok=True); before = os.path.join(R.SHOTS, f'손잡이_{nm}_전.png'); pre = R.build_tmp(cur); nid = R.newest_note(pre)
        T.shoot_pages(pre, [('trend/' if nm.startswith('순위') and nm != '순위셈법' else 'market/' if nm in ('상품열', '딱지색') else ('market/' + _first_product() + '/') if nm in ('사는단추', '값정하기') else 'board/' if nm in ('순위셈법', '한쪽줄수', '공개방식', '게시판글자') else (f'n/{nid}/' if (nid and nm != '목록열') else ''))], [before], 1280, 860)
    if rest[1] != '기본' and KN.parse(nm, rest[1]) is None:
        print(f'그 값으로는 돌릴 수 없습니다(화면이 망가질 수 있는 값은 막아 둡니다). 돌릴 수 있는 값: {" / ".join(str(x) for x in d["vals"])}'); return 1
    snap(f'손잡이 {nm} → {rest[1]}')
    if rest[1] == '기본':
        K.pop(d['key'], None); val = '기본'
    else:
        val = KN.parse(nm, rest[1]); K[d['key']] = val
    L['knobs'] = K; R.local_save(L); t0 = time.time(); out, last, rc = R.rebuild_local()
    if R.SHOTS and before:
        import selftest as T
        nid = R.newest_note(out); after = os.path.join(R.SHOTS, f'손잡이_{nm}_후.png'); T.shoot_pages(out, [('trend/' if nm.startswith('순위') and nm != '순위셈법' else 'market/' if nm in ('상품열', '딱지색') else ('market/' + _first_product() + '/') if nm in ('사는단추', '값정하기') else 'board/' if nm in ('순위셈법', '한쪽줄수', '공개방식', '게시판글자') else (f'n/{nid}/' if (nid and nm != '목록열') else ''))], [after], 1280, 860)
        R.side_by_side(before, after, os.path.join(R.SHOTS, f'손잡이_{nm}_전후.png'), '돌리기 전', f'{nm} = {val}')
    need = KN.NEED.get(nm)
    print(f'돌렸습니다: {nm} = {val}{d["unit"] if val != "기본" else ""}  (레퍼런스는 {d["ref"]}{d["unit"]}, {time.time() - t0:.0f}초)' + (f'\n※ 이 손잡이는 다듬기 {need} 을 얹어야 화면에 보입니다.' if need and str(need) not in cur else ''))
    print(f'[원래 그 플랫폼은 이렇게 해 두었고, 그 까닭은] {d["why"]}\n[물음] 왜 그쪽으로 돌리셨나요? — 답을 내_서비스 한 장에 적습니다.\n되돌리려면 python run.py 되돌리기\n\n여기서 멈추고 독자에게 묻습니다.')
    R.prog_add(f'손잡이 {nm}={val}'); return 0


# ---------------------------------------------------------------- 조각 하나만 켜고 끄기 · 내 분류
SOLO_NAMES = {'readtime': '읽는 시간', 'tags': '주제 태그', 'save': '저장', 'listen': '듣기'}


def piece_cmd(R, rest):
    """나누기에서 본 조각 하나만 내 사이트에 켰다 끈다(다듬기 10 을 통째로 얹지 않고)."""
    files = _piece_files(); L = R.local_load(); solo = list(L.get('solo') or [])
    if len(rest) < 2 or not rest[1].isdigit():
        print('━━ 조각 — 하나만 켰다 꺼 보기 ━━\n지금 켜 둔 조각: ' + (' · '.join(SOLO_NAMES.get(s, s) for s in solo) or '(없음)'))
        for k, fpath in files.items():
            sw = [f'{x["n"]}. {x["name"]}' for x in json.load(open(fpath, encoding='utf-8'))['pieces'] if x.get('switch')]
            if sw:
                print(f'[{k}] 바로 켜고 끌 수 있는 조각: ' + ' · '.join(sw))
        print('\n사용: python run.py 조각 미디엄 2 켜기 [--shots 폴더]  ·  조각 미디엄 2 끄기  ·  되돌리기: python run.py 되돌리기'); return 0
    key = next((k for k in files if rest[0].replace(' ', '') in k.replace(' ', '')), None)
    if not key:
        print('조각 표가 있는 곳: ' + ' · '.join(files)); return 1
    d = json.load(open(files[key], encoding='utf-8')); x = next((q for q in d['pieces'] if q['n'] == int(rest[1])), None)
    if not x:
        print('그 번호의 조각이 없습니다'); return 1
    act = rest[2] if len(rest) > 2 else '켜기'
    if not x.get('switch'):
        print(f'{x["n"]}. {x["name"]} 은(는) 단추 하나로 켜고 끄는 조각이 아닙니다.\n우리 저장소: {x["ours"]} — {x["how"]}' + ('\n서버가 있어야 합니다(2장).' if x.get('server') else '')); return 0
    if '10' in R.cur_polish():
        print(f'다듬기 10 을 이미 얹어 이 조각이 켜져 있습니다. 끄고 켜는 것은 손잡이로: python run.py 손잡이   (읽는시간·저장·듣기)'); return 0
    sw = x['switch']; on = act not in ('끄기', '끔', 'off')
    if on == (sw in solo):
        print(f'{x["name"]}: 이미 {"켜져" if on else "꺼져"} 있습니다.'); return 0
    before = None
    if R.SHOTS:
        import selftest as T
        os.makedirs(R.SHOTS, exist_ok=True); before = os.path.join(R.SHOTS, f'조각_{x["name"]}_전.png'); pre = R.build_tmp(R.cur_polish()); nid = R.newest_note(pre)
        T.shoot_pages(pre, [f'n/{nid}/' if nid else ''], [before], 1280, 860)
    snap(f'조각 {x["name"]} {"켜기" if on else "끄기"}')
    solo = (solo + [sw]) if on else [s for s in solo if s != sw]
    L['solo'] = solo; R.local_save(L); out, last, rc = R.rebuild_local()
    if before:
        import selftest as T
        nid = R.newest_note(out); after = os.path.join(R.SHOTS, f'조각_{x["name"]}_후.png'); T.shoot_pages(out, [f'n/{nid}/' if nid else ''], [after], 1280, 860)
        R.side_by_side(before, after, os.path.join(R.SHOTS, f'조각_{x["name"]}_전후.png'), '전', f'{x["name"]} {"켬" if on else "끔"}')
    print(f'{"켰습니다" if on else "껐습니다"}: {d["name"]} 의 조각 {x["n"]}. {x["name"]}  (지금 켜 둔 조각: {" · ".join(SOLO_NAMES.get(s, s) for s in solo) or "없음"})')
    print(f'어디에 보이나: 글 한 편을 열면 {"글 머리(날짜 앞)" if sw in ("readtime", "tags") else "글 맨 아래 단추 줄"}에 있습니다.\n[그 플랫폼이 이 조각을 둔 까닭] {x["why"]}')
    print(f'[물음] 켜 두니 어떤가요 — 내 사이트에 둘까요, 뺄까요? 까닭도 한마디.\n{"끄려면 python run.py 조각 " + key + " " + str(x["n"]) + " 끄기" if on else "다시 켜려면 … 켜기"}  ·  되돌리기: python run.py 되돌리기\n\n여기서 멈추고 독자에게 묻습니다.')
    R.prog_add(f'조각 {x["name"]} {"켬" if on else "끔"}'); return 0


def cats_cmd(R, rest):
    """독자가 말한 분류를 목록의 분류 탭으로. 분류마다 '이름=낱말,낱말' 로 그 분류에 들어갈 글을 가리는 낱말을 줄 수 있다."""
    import glob, polish as PL
    L = R.local_load(); cur = L.get('cats') or []
    def count(C):
        PL.CUSTOM = C; cnt = {}; N = 0
        for f in glob.glob(os.path.join(R.HERE, 'notes', '*.json')):
            try:
                n = json.load(open(f, encoding='utf-8'))
            except Exception:
                continue
            if isinstance(n, dict) and n.get('title'):
                c = PL.cat_of(n); cnt[c] = cnt.get(c, 0) + 1; N += 1
        return cnt, N
    if not rest:
        cnt, N = count(cur)
        print('━━ 분류 — 목록 위 분류 탭을 내 말로 ━━\n지금: ' + (' · '.join(c['name'] + (f'({",".join(c["words"])})' if c.get('words') else '') for c in cur) if cur else '기본(글의 첫 태그 가운데 많은 것)'))
        print('글이 들어간 수(notes/ 기준): ' + ' · '.join(f'{k} {v}건' for k, v in sorted(cnt.items(), key=lambda t: -t[1])))
        print('\n사용: python run.py 분류 "절약=아끼,할인" "제도=지원금,신청" 투자   ·   원래대로: python run.py 분류 기본\n(= 뒤는 그 분류에 넣을 글을 가리는 낱말. 없으면 분류 이름이 태그·제목·요약에 있는 글이 들어갑니다. 어디에도 안 맞는 글은 「기타」)'); return 0
    snap('분류 ' + ' '.join(rest))
    if rest[0] == '기본':
        L.pop('cats', None); C = []
    else:
        C = []
        for a in rest[:6]:
            nm, _, ws = a.partition('='); nm = nm.strip()
            if nm:
                C.append({'name': nm, 'words': [w.strip() for w in ws.replace('，', ',').split(',') if w.strip()]})
        L['cats'] = C
    R.local_save(L); cnt, N = count(C); R.rebuild_local()
    print('분류를 바꿨습니다: ' + (' · '.join(c['name'] for c in C) if C else '기본으로 되돌림'))
    print('글이 들어간 수(notes/ 기준): ' + ' · '.join(f'{k} {v}건' for k, v in sorted(cnt.items(), key=lambda t: -t[1])))
    empty = [c['name'] for c in C if not cnt.get(c['name'])]
    if empty:
        print('글이 한 건도 없어 탭에 안 나오는 분류: ' + ' · '.join(empty) + '  → 그 분류에 넣을 낱말을 주거나(이름=낱말,낱말) 그 주제의 글을 먼저 씁니다.')
    if C and cnt.get('기타', 0) > N / 2:
        print(f'※ 글의 절반 넘게({cnt["기타"]}/{N}) 「기타」로 갔습니다. 분류 낱말을 더 주면 줄어듭니다.')
    if '3' not in R.cur_polish():
        print('※ 분류 탭 줄은 다듬기 3(메뉴를 분야 탭으로)을 얹어야 목록 위에 보입니다. 지금은 카드와 글 머리의 분류 이름만 바뀝니다.')
    print('[물음] 이 분류로 처음 온 사람이 자기가 찾는 글을 바로 찾을까요? 빠진 분류가 있나요?\n되돌리려면 python run.py 되돌리기\n\n여기서 멈추고 독자에게 묻습니다.')
    R.prog_add('분류 ' + ('·'.join(c['name'] for c in C) or '기본')); return 0


# ---------------------------------------------------------------- 나누기: 레퍼런스를 조각으로
def _piece_files():
    return {os.path.splitext(f)[0]: os.path.join(PIECES, f) for f in sorted(os.listdir(PIECES)) if f.endswith('.json')} if os.path.isdir(PIECES) else {}


def split_cmd(R, rest):
    files = _piece_files()
    plats = json.load(open(PLAT, encoding='utf-8')).get('platforms', []) if os.path.exists(PLAT) else []
    if not rest:
        print('━━ 나누기 — 레퍼런스 사이트를 기능 조각으로 ━━\n[조각 표가 있는 곳] ' + (' · '.join(files) or '(없음)'))
        if plats:
            print('[조사 자료만 있는 곳(우리 기능과의 짝은 아직 맞추지 않음)] ' + ' · '.join(f'{p["name"]}({p.get("group", "")})' for p in plats))
        print('\n사용: python run.py 나누기 미디엄  ·  나누기 미디엄 7(조각 하나 자세히)  ·  나누기 새로 "<사이트 이름>"(독자가 좋아하는 사이트를 같은 틀로)'); return 0
    if rest[0] == '새로':
        nm = ' '.join(rest[1:]).strip()
        if not nm:
            print('사용: python run.py 나누기 새로 "<사이트 이름>"'); return 1
        os.makedirs(PIECES, exist_ok=True); fp = os.path.join(PIECES, nm + '.json')
        if not os.path.exists(fp):
            json.dump({'name': nm, 'one_line': '', 'source': '독자 세션이 그 사이트를 열어 보고 채움(화면은 저장하지 않음). 잰 날: ', 'pieces': [{'n': 1, 'name': '', 'does': '', 'visitor': '', 'why': '', 'ours': '있음|비슷함|없음', 'how': '', 'solo': '됨|혼자 어려움', 'server': False}]}, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'조각 표 틀을 만들었습니다: 참고/조각/{nm}.json\n세션이 할 일: 그 사이트의 첫 화면과 항목 쪽을 열어 보고(화면은 저장하지 않음) 조각마다 「무엇을 하는가 / 방문자에게 무슨 일이 생기는가 / 왜 다시 오게 하는가·무엇으로 버는 데 쓰이는가 / 우리 저장소의 어느 기능인가(있음·비슷함·없음) / 혼자 되는가」를 채웁니다. 독자에게 먼저: 「그 사이트에서 가장 자주 누르는 것은 무엇인가요?」\n채운 뒤 python run.py 나누기 {nm}'); return 0
    key = next((k for k in files if rest[0].replace(' ', '') in k.replace(' ', '')), None)
    if key:
        d = json.load(open(files[key], encoding='utf-8')); P = d['pieces']
        if len(rest) > 1 and rest[1].isdigit():
            p = next((x for x in P if x['n'] == int(rest[1])), None)
            if not p:
                print('그 번호의 조각이 없습니다'); return 1
            print(f'━━ {d["name"]} 의 조각 {p["n"]}. {p["name"]} ━━\n무엇을 하는가: {p["does"]}\n방문자에게 생기는 일: {p["visitor"]}\n왜(다시 오게·버는 데): {p["why"]}\n우리 저장소: {p["ours"]} — {p["how"]}\n혼자 되는가: {p["solo"]}' + ('\n서버가 있어야 합니다(2장에서 다룹니다).' if p.get('server') else '\n서버 없이 됩니다(1장에서 켜 봅니다).'))
            if p.get('switch'):
                print(f'바로 켜 보기: python run.py 조각 {key} {p["n"]} 켜기 [--shots 폴더]   ·   끄기: … 끄기')
            print(f'\n[물음] 이 조각이 없으면 {d["name"]} 은(는) 어떻게 될까요?\n[독자가 해 볼 일] 위 명령으로 이 조각을 내 사이트에 켜 보고(전·후 화면), 다시 꺼 봅니다.\n\n여기서 멈추고 독자에게 묻습니다.'); return 0
        print(f'━━ 나누기 · {d["name"]} ━━\n{d["one_line"]}\n(근거: {d.get("source", "")})\n')
        for p in P:
            print(f'  {p["n"]:>2}. {p["name"]:<14} [{p["ours"]}] {"· 서버 필요" if p.get("server") else ""}{"· 바로 켜고 끔" if p.get("switch") else ""} — {p["does"]}')
        if d.get('earns'):
            print(f'\n버는 길(확인된 것만): python run.py 참고 {key}')
        if d.get('biggest_diff'):
            print(f'\n※ 본과 가장 크게 다른 것: {d["biggest_diff"]}')
        have = sum(1 for p in P if p['ours'].startswith('있음')); near = sum(1 for p in P if p['ours'].startswith('비슷')); none = len(P) - have - near
        print(f'\n조각 {len(P)}개: 우리 저장소에 있음 {have} · 비슷함 {near} · 없음 {none} / 서버 없이 되는 것 {sum(1 for p in P if not p.get("server"))}개')
        print(f'[독자에게 말할 것] 사이트 하나도 이렇게 조각으로 나눠 볼 수 있습니다. 조각을 하나씩 골라 자세히 보고(python run.py 나누기 {key} <번호>) 내 사이트에 켜 봅니다.\n[물음] 이 가운데 없으면 {d["name"]} 이(가) 아니게 되는 조각은 무엇일까요?\n\n여기서 멈추고 독자에게 묻습니다.')
        if R.SHOTS:
            R._text_shot(f'나누기 · {d["name"]}', [('조각', '\n'.join(f'{p["n"]}. {p["name"]} [{p["ours"]}] — {p["does"]}' for p in P))], '나누기_' + key)
        R.prog_add('나누기 ' + key); return 0
    KO = {'hackernews': '해커뉴스', 'substack': '서브스택', 'gumroad': '검로드', 'producthunt': '프로덕트헌트', 'linktree': '링크트리', 'wordle': '워들', 'naver-kin': '지식인지식iN', 'clien': '클리앙', 'danawa': '다나와', '10000recipe': '만개의레시피'}
    w_ = ''.join(rest).replace(' ', '').lower()
    p = next((x for x in plats if w_ and w_ in (x['name'] + x.get('slug', '') + KO.get(x.get('slug', ''), '')).replace(' ', '').lower()), None)
    if not p:
        print('그 레퍼런스가 없습니다. python run.py 나누기 로 목록을 보세요.'); return 1
    print(f'━━ 나누기 · {p["name"]} ({p.get("group", "")}) — 조사 자료 ━━\n{p.get("one_line", "")}\n[왜 다시 오는가] {p.get("loop", "")}\n[그 플랫폼다운 기능]')
    for i, f in enumerate(p.get('features', []), 1):
        print(f'  {i}. {f}')
    lay = p.get('layout') or {}
    for nm, k in (('첫 화면', 'home'), ('항목 쪽', 'item')):
        if lay.get(k):
            print(f'[{nm}에 놓인 순서] ' + ' → '.join(lay[k]))
    for m in p.get('money', []):
        print(f'[버는 길] {m.get("how", "")} (근거: {m.get("evidence", "")[:80]})')
    so = p.get('solo') or {}
    print('[혼자 되는 것] ' + ' / '.join(so.get('can', [])) + '\n[혼자 못 하는 것] ' + ' / '.join(so.get('cannot', [])))
    print('\n※ 우리 저장소 기능과의 짝(있음·비슷함·없음)은 아직 맞추지 않았습니다. 조각 표가 있는 곳은 지금 미디엄뿐입니다.\n\n여기서 멈추고 독자에게 묻습니다: 「이 사이트에서 없으면 안 되는 조각은 무엇일까요?」'); return 0
