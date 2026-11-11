# -*- coding: utf-8 -*-
"""만지는 재미를 위한 명령: 나누기(레퍼런스를 조각으로) · 손잡이(돌려 보기) · 바꿔/바꿨다(작은 고침) · 간직과 되돌리기(마지막·처음). run.py 가 부른다. 파이썬 기본 기능만 쓴다.
고치기 전 모습은 .간직/<번호>/ 에 저절로 간직한다(site.local.json 과 kits/*/data, notes, posts — git 에는 올라가지 않는다)."""
import json, os, shutil, time

HERE = os.path.dirname(os.path.abspath(__file__))
KEEP = os.path.join(HERE, '.간직')
PIECES = os.path.join(HERE, '참고', '조각')
PLAT = os.path.join(HERE, '참고', '플랫폼.json')


# ---------------------------------------------------------------- 간직·되돌리기
def _items():
    out = ['site.local.json', 'notes', 'posts']
    kd = os.path.join(HERE, 'kits')
    out += [os.path.join('kits', k, 'data') for k in sorted(os.listdir(kd)) if os.path.isdir(os.path.join(kd, k, 'data'))]
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
    for old in nums[:-30]:   # 서른 개까지만(처음 모습 0번은 남긴다)
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
        print('사용: python run.py 바꿔 "<무엇을 어떻게>"   예: 바꿔 "한 줄 소개를 「퇴근길 5분 경제」로"\n세션이 이 말을 받아 해당 자료·설정만 고친 뒤 python run.py 바꿨다 로 다시 찍고 전·후를 보입니다.'); return 1
    n = snap(what); os.makedirs(KEEP, exist_ok=True)
    before = None
    if R.SHOTS:
        import selftest as T
        os.makedirs(R.SHOTS, exist_ok=True); before = os.path.join(R.SHOTS, f'바꿔_{n}_전.png'); T.shoot_pages(R.build_tmp(R.cur_polish()), [''], [before], 1280, 860)
    json.dump({'n': n, 'what': what, 'before': before, 't0': time.time()}, open(PENDING, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'지금 모습을 간직했습니다({n}번). 이제 세션이 「{what}」에 해당하는 것만 고칩니다.\n'
          '[어디를 고치나] 이름·한 줄 소개·색·틀 → site.local.json / 글·노트 → notes/·posts/ / 계산기·용어·일정 같은 자료 → kits/<기능>/data/ / 크기·폭 같은 값 → python run.py 손잡이\n'
          '[막아 둔 것] build.py·run.py 같은 틀 파일은 이 길로 고치지 않습니다(망가질 수 있어, 필요하면 먼저 독자에게 알리고 따로 합니다).\n고친 뒤: python run.py 바꿨다 "<무엇을 고쳤는지 한 줄>"'); return 0


def changed_cmd(R, rest):
    if not os.path.exists(PENDING):
        print('먼저 python run.py 바꿔 "<무엇을 어떻게>" 로 시작하세요(고치기 전 모습을 간직합니다).'); return 1
    p = json.load(open(PENDING, encoding='utf-8')); os.remove(PENDING)
    out, last, rc = R.rebuild_local()
    if rc != 0:
        print('찍기에 실패했습니다. python run.py 되돌리기 로 고치기 전으로 돌아갈 수 있습니다.'); return 1
    did = ' '.join(rest).strip() or p['what']
    if R.SHOTS and p.get('before') and os.path.exists(p['before']):
        import selftest as T
        after = os.path.join(R.SHOTS, f'바꿔_{p["n"]}_후.png'); T.shoot_pages(out, [''], [after], 1280, 860)
        R.side_by_side(p['before'], after, os.path.join(R.SHOTS, f'바꿔_{p["n"]}_전후.png'), '고치기 전', '고친 뒤')
    print(f'고쳤습니다: {did}  ({time.time() - p["t0"]:.0f}초, {last})\n되돌리려면 python run.py 되돌리기\n[물음] 왜 그렇게 바꾸고 싶으셨나요? — 답을 내_서비스 한 장에 적습니다(python run.py 내서비스 칸 …).\n\n여기서 멈추고 독자에게 묻습니다.')
    R.prog_add('바꿈: ' + did); return 0


# ---------------------------------------------------------------- 손잡이
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
        T.shoot_pages(pre, [('board/' if nm in ('순위셈법', '한쪽줄수', '공개방식', '게시판글자') else (f'n/{nid}/' if (nid and nm != '목록열') else ''))], [before], 1280, 860)
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
        nid = R.newest_note(out); after = os.path.join(R.SHOTS, f'손잡이_{nm}_후.png'); T.shoot_pages(out, [('board/' if nm in ('순위셈법', '한쪽줄수', '공개방식', '게시판글자') else (f'n/{nid}/' if (nid and nm != '목록열') else ''))], [after], 1280, 860)
        R.side_by_side(before, after, os.path.join(R.SHOTS, f'손잡이_{nm}_전후.png'), '돌리기 전', f'{nm} = {val}')
    need = KN.NEED.get(nm)
    print(f'돌렸습니다: {nm} = {val}{d["unit"] if val != "기본" else ""}  (레퍼런스는 {d["ref"]}{d["unit"]}, {time.time() - t0:.0f}초)' + (f'\n※ 이 손잡이는 다듬기 {need} 을 얹어야 화면에 보입니다.' if need and str(need) not in cur else ''))
    print(f'[원래 그 플랫폼은 이렇게 해 두었고, 그 까닭은] {d["why"]}\n[물음] 왜 그쪽으로 돌리셨나요? — 답을 내_서비스 한 장에 적습니다.\n되돌리려면 python run.py 되돌리기\n\n여기서 멈추고 독자에게 묻습니다.')
    R.prog_add(f'손잡이 {nm}={val}'); return 0


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
            print(f'\n[물음] 이 조각이 없으면 {d["name"]} 은(는) 어떻게 될까요?\n[독자가 해 볼 일] 위 명령으로 이 조각을 내 사이트에 켜 보고(전·후 화면), 다시 꺼 봅니다.\n\n여기서 멈추고 독자에게 묻습니다.'); return 0
        print(f'━━ 나누기 · {d["name"]} ━━\n{d["one_line"]}\n(근거: {d.get("source", "")})\n')
        for p in P:
            print(f'  {p["n"]:>2}. {p["name"]:<14} [{p["ours"]}] {"· 서버 필요" if p.get("server") else ""} — {p["does"]}')
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
