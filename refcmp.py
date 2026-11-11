# -*- coding: utf-8 -*-
"""레퍼런스(히트한 플랫폼)를 잰 값과 우리 사이트의 지금 값을 나란히 놓는다. 평가(잘 만들었다)가 아니라 차이만 말한다. 파이썬 기본 기능만 쓴다.
run.py 가 부른다: 레퍼런스(차이표) · 레퍼런스 바꾸기 <이름> · 레퍼런스 값 키=값 · 만듦새(기본 점검 + 차이표) · 다듬기 걸음의 [레퍼런스는/우리는] 줄."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, '참고', '레퍼런스.json')

ROWS_A = [('본문 글자 크기(px)', 'body_px'), ('줄 높이(글자의 몇 배)', 'line_height'), ('본문 폭(px)', 'body_width'), ('한 줄 길이(글자 크기의 몇 배)', 'line_em'), ('본문 글꼴', 'body_font'),
          ('제목 크기(px)', 'title_px'), ('제목 ÷ 본문', 'title_ratio'), ('소제목 크기(px)', 'h2_px'), ('글 그림 폭(px)', 'img_width'), ('글 머리 정보', 'head'), ('글에 붙은 단추', 'actions')]
ROWS_L = [('목록 열 수', 'cols'), ('카드 제목 크기(px)', 'card_title_px'), ('카드 설명 크기(px)', 'card_desc_px'), ('분류 탭', 'tabs')]
STEP_KEYS = {1: [('article', k) for k in ('body_px', 'line_height', 'body_width', 'line_em', 'body_font')], 3: [('list', 'tabs')], 4: [('list', 'cols'), ('list', 'card_title_px'), ('list', 'card_desc_px')],
             5: [('article', 'img_width')], 7: [('article', 'title_px'), ('article', 'title_ratio'), ('article', 'h2_px')], 10: [('article', 'head'), ('article', 'actions')]}
NAMES = {k: nm for nm, k in ROWS_A + ROWS_L}


def load():
    return json.load(open(REF, encoding='utf-8'))


def save(d):
    json.dump(d, open(REF, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def current():
    d = load(); return d['current'], d['refs'][d['current']]


def ours(T, out, note_path):
    """우리 사이트의 지금 값: 글 쪽과 첫 화면을 재서 {'article':…, 'list':…}"""
    res = T.measure_site(out, ([note_path] if note_path else []) + [''], 1280, 860, False)
    a = (res[0].get('ref') or {}).get('article', {}) if note_path and res else {}
    l = (res[-1].get('ref') or {}).get('list', {}) if res else {}
    return {'article': a, 'list': l}


def fmt(v):
    if isinstance(v, list):
        return '·'.join(v) if v else '없음'
    if isinstance(v, bool):
        return '있음' if v else '없음'
    return '—' if v is None else str(v)


def diff(r, o):
    if r is None or o is None:
        return '(잰 값 없음)'
    if isinstance(r, list):
        miss = [x for x in r if x not in (o or [])]
        return '같음' if not miss else '우리에 없는 것: ' + '·'.join(miss)
    if isinstance(r, bool):
        return '같음' if bool(o) == r else '다름'
    if isinstance(r, (int, float)) and isinstance(o, (int, float)):
        d = round(o - r, 2)
        return '같음' if abs(d) < 0.011 else (f'+{d:g}' if d > 0 else f'{d:g}')
    return '같음' if str(r) == str(o) else '다름'


def table(o):
    name, R = current(); lines = [f'레퍼런스: {name} (잰 날 {R.get("measured")}, 잰 쪽 {R.get("url")}, {R.get("by", "")})', f'  {"항목":<22} {"레퍼런스":<28} {"우리 지금":<24} 차이']
    n_same = n_all = 0
    for sec, rows in (('article', ROWS_A), ('list', ROWS_L)):
        lines.append('  [글 쪽]' if sec == 'article' else '  [목록 쪽]')
        for nm, k in rows:
            r = (R.get(sec) or {}).get(k); v = (o.get(sec) or {}).get(k); df = diff(r, v)
            n_all += 1; n_same += 1 if df == '같음' else 0
            lines.append(f'  {nm:<22} {fmt(r):<28} {fmt(v):<24} {df}')
    lines.append(f'  → {n_all}개 항목 가운데 {n_same}개가 레퍼런스와 같고 {n_all - n_same}개가 다릅니다(다른 것이 틀린 것은 아닙니다 — 어떤 경우에 따르고 어떤 경우에 다르게 갈지는 독자가 고릅니다).')
    return lines, n_same, n_all


def step_lines(n, o):
    """다듬기 걸음 n 에서 볼 레퍼런스 값과 우리 값."""
    keys = STEP_KEYS.get(n)
    if not keys:
        return []
    name, R = current(); out = []
    for sec, k in keys:
        r = (R.get(sec) or {}).get(k); v = (o.get(sec) or {}).get(k)
        out.append(f'  {NAMES[k]}: {name} {fmt(r)} / 우리 지금 {fmt(v)} ({diff(r, v)})')
    return out


def switch(name):
    d = load()
    if name not in d['refs']:
        d['refs'][name] = {'url': '', 'measured': '', 'by': '독자 세션이 그 사이트를 열어 잼', 'article': {k: None for _, k in ROWS_A}, 'list': {k: None for _, k in ROWS_L}}
        msg = (f'새 레퍼런스 「{name}」 자리를 만들었습니다(값은 비어 있음). 독자 세션이 그 사이트의 글 쪽과 목록 쪽을 열어 재서 넣습니다 — 남의 사이트 화면은 저장소에 넣지 않습니다.\n'
               '넣는 법: python run.py 레퍼런스 값 url=https://… measured=오늘날짜 body_px=18 line_height=1.7 body_width=700 line_em=39 title_px=40 title_ratio=2.2 h2_px=24 img_width=700 cols=3 card_title_px=22 card_desc_px=16 tabs=true head=주제태그,글쓴이,읽는시간,날짜 actions=좋아요,댓글,저장,공유')
    else:
        msg = f'레퍼런스를 「{name}」로 바꿨습니다.'
    d['current'] = name; save(d); return msg


def set_values(pairs):
    d = load(); R = d['refs'][d['current']]
    for kv in pairs:
        if '=' not in kv:
            continue
        k, v = kv.split('=', 1); k = k.strip(); v = v.strip()
        if k in ('url', 'measured', 'by'):
            R[k] = v; continue
        sec = 'article' if k in dict((b, a) for a, b in ROWS_A) else ('list' if k in dict((b, a) for a, b in ROWS_L) else None)
        if not sec:
            print('  모르는 키:', k); continue
        if k in ('head', 'actions'):
            val = [x.strip() for x in v.split(',') if x.strip()]
        elif k == 'tabs':
            val = v.lower() in ('true', '1', '있음', 'yes')
        elif k == 'body_font':
            val = v
        else:
            try:
                val = float(v) if '.' in v else int(v)
            except ValueError:
                val = v
        R.setdefault(sec, {})[k] = val
    save(d); return f'레퍼런스 「{d["current"]}」 값을 적었습니다.'
