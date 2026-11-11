# -*- coding: utf-8 -*-
"""다듬기(polish): 투박한 출발 모습을 걸음마다 한 층씩 고품질로 바꾸는 층 모음. 파이썬 기본 기능만 쓴다.
설정: site.local.json 의 "polish": {"1": "A", "2": "B", ...}(걸음 번호: 고른 안) 또는 환경변수 SITE_POLISH(JSON). 없으면 출발 모습 그대로.
build.py 가 이 파일의 css()·head()·body_class()·home_body()·img_tag() 를 부른다. 걸음 안내(왜·참고·안)는 다듬기.json."""
import hashlib, html, json, os, re

E = html.escape


def active(S):
    p = S.get('polish') or {}
    return {int(k): v for k, v in p.items() if str(k).isdigit() and v}


# ---------------------------------------------------------------- 1 글자와 줄 간격
FONT_A = "'Pretendard Variable',Pretendard,'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',system-ui,sans-serif"
FONT_B = "'Noto Serif KR','Nanum Myeongjo','Batang',serif"


def css1(opt, base_css):
    f = FONT_A if opt != 'B' else FONT_B
    # 기본 CSS 에서 13px 보다 작은 글자를 찾아 13px 로 올리는 규칙을 만든다(메뉴·딱지·표시 글자가 너무 작지 않게)
    small = []
    for sel, body in re.findall(r'([^{}@]+)\{([^{}]*)\}', base_css):
        m = re.search(r'(?:font:[^;}]*?|font-size:)(\d+(?:\.\d+)?)px', body)
        if m and float(m.group(1)) < 13 and sel.strip() and not sel.strip().startswith(':root'):
            small.append(sel.strip())
    up = (',\n'.join(small) + '{font-size:13px}\n') if small else ''
    return (f":root{{--sans:{f};--serif:{FONT_B}}}\n"
            f"body.pl1{{font-family:{f};font-size:calc(17px*var(--fz,1));line-height:1.75;word-break:keep-all;overflow-wrap:anywhere}}\n"
            "body.pl1 h1,body.pl1 h2,body.pl1 h3,body.pl1 .lead h2,body.pl1 .tp b,body.pl1 .art h1{font-family:var(--sans);letter-spacing:-.02em;line-height:1.35}\n"
            "body.pl1 .art,body.pl1 .page{max-width:680px}body.pl1 .art p.sum,body.pl1 .art li,body.pl1 .page li,body.pl1 .page p{font-size:calc(17.5px*var(--fz,1));line-height:1.8}\n"
            "body.pl1 nav.menu a,body.pl1 details.mn summary{font-size:15px}body.pl1 .dek,body.pl1 .lead p,body.pl1 .side h3,body.pl1 .tp b{font-family:var(--sans)}\n" + up)


# ---------------------------------------------------------------- 2 색과 대비
def css2(opt):
    if opt == 'B':
        pri, sec, ink, mu, hair, bgs = '#14532d', '#c2410c', '#14201a', '#4a5a50', '#dbe5dd', '#f4f8f4'
    else:
        pri, sec, ink, mu, hair, bgs = '#1e3a8a', '#b45309', '#0f172a', '#475569', '#dde3ee', '#f3f6fb'
    return (f":root{{--pri:{pri};--sec:{sec};--ink:{ink};--mu:{mu};--hair:{hair};--bgs:{bgs};--link:{pri}}}\n"
            f"body.pl2 .mast{{border-bottom:3px solid var(--pri)}}body.pl2 nav.menu{{border-bottom:1px solid var(--hair)}}body.pl2 nav.menu a:hover{{color:var(--pri)}}\n"
            "body.pl2 .sec{border-top:3px solid var(--pri)}body.pl2 .sec h2,body.pl2 .lb{color:var(--pri)}body.pl2 footer{border-top:3px solid var(--pri);background:var(--bgs)}\n"
            "body.pl2 .art h2{border-top-color:var(--pri)}body.pl2 .notice{background:var(--bgs);border-color:var(--hair)}\n")


# ---------------------------------------------------------------- 3 제호와 메뉴
def css3(opt):
    base = ("body.pl3 .dateline{font:600 14px/1.2 var(--sans);border:0;padding:12px 0 0;color:var(--mu)}\n"
            "body.pl3 nav.menu{scrollbar-width:none;position:sticky;top:0;z-index:30;background:var(--bg,#fff);gap:0;justify-content:flex-start;padding:0;border-top:1px solid var(--ink);border-bottom:1px solid var(--hair);overflow-x:auto;-webkit-overflow-scrolling:touch}\n"
            "body.pl3 nav.menu a,body.pl3 details.mn summary{display:block;padding:14px 18px;font:700 15px/1 var(--sans);white-space:nowrap;border-bottom:3px solid transparent}\n"
            "body.pl3 nav.menu a:hover{text-decoration:none;border-bottom-color:var(--pri,#111)}body.pl3 .mnp{top:46px}body.pl3 nav.menu::-webkit-scrollbar{display:none}\n")
    if opt == 'B':   # 좌측 제호 + 탭 바
        return base + ("body.pl3 .mast .wrap{display:flex;align-items:baseline;justify-content:space-between;gap:16px;flex-wrap:wrap}body.pl3 .dateline{order:2;text-align:right;padding:18px 0 0}\n"
                       "body.pl3 .logo{text-align:left;font:900 40px/1.1 'Noto Serif KR','Nanum Myeongjo',Batang,serif;margin:14px 0 12px;color:var(--pri,#111)}body.pl3 .mast{border-bottom:0}\n")
    return base + ("body.pl3 .dateline{text-align:center}body.pl3 .logo{font:900 64px/1.1 'Noto Serif KR','Nanum Myeongjo',Batang,serif;letter-spacing:-.04em;margin:10px 0 14px}\n"
                   "body.pl3 .mast{border-bottom:3px double var(--ink)}body.pl3 nav.menu{justify-content:center}\n"
                   "@media(max-width:640px){body.pl3 .logo{font-size:38px}body.pl3 nav.menu{justify-content:flex-start}}\n")


# ---------------------------------------------------------------- 4 첫 화면 짜임 / 5 그림
def css4(opt):
    c = ("body.pl4 .ph2{display:grid;grid-template-columns:minmax(0,2.1fr) minmax(0,1fr);gap:28px;padding:26px 0 8px}\n"
         "body.pl4 .ph{display:grid;gap:16px;align-content:start}body.pl4 .ph.hasimg{grid-template-columns:1fr}\n"
         "body.pl4 .ph h2{font-size:34px;line-height:1.3;margin:6px 0 12px}body.pl4 .ph p{font-size:18px;color:var(--mu);margin:0 0 12px}\n"
         "body.pl4 .ph-t .meta{font:14px/1.5 var(--sans);color:var(--mu)}body.pl4 .btn{display:inline-block;margin-top:14px;padding:11px 18px;background:var(--pri,#111);color:#fff;font:700 15px/1 var(--sans);border-radius:6px}body.pl4 .btn:hover{text-decoration:none;opacity:.9}\n"
         "body.pl4 .ps{border-left:1px solid var(--hair);padding-left:26px}body.pl4 .ps h2{font:800 14px/1 var(--sans);letter-spacing:.06em;margin:0 0 14px;color:var(--pri,#111)}\n"
         "body.pl4 .ps a.it2{display:flex;gap:12px;padding:14px 0;border-top:1px solid var(--hair);align-items:flex-start}body.pl4 .ps a.it2:hover{text-decoration:none}body.pl4 .ps a.it2:hover b{text-decoration:underline}\n"
         "body.pl4 .ps b{display:block;font:700 17px/1.45 var(--sans);margin:4px 0 0}body.pl4 .ps .meta{font:13px/1.4 var(--sans);color:var(--mu)}\n"
         "body.pl4 .pg{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}body.pl4 .pc{border:1px solid var(--hair);border-radius:10px;overflow:hidden;background:#fff}\n"
         "body.pl4 .pc a{display:block}body.pl4 .pc a:hover{text-decoration:none}body.pl4 .pc a:hover h3{text-decoration:underline}body.pl4 .pc-b{padding:14px 16px 18px}\n"
         "body.pl4 .pc h3{font:700 18px/1.45 var(--sans);margin:8px 0 6px}body.pl4 .pc p{font:15px/1.65 var(--sans);color:var(--mu);margin:0}body.pl4 .pc-d{font:13px/1 var(--sans);color:var(--mu);margin-left:8px}\n"
         "body.pl4 .pt-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}body.pl4 .pt{border:1px solid var(--hair);border-radius:10px;padding:14px 16px;background:#fff}\n"
         "body.pl4 .pt b{display:block;font:700 17px/1.45 var(--sans);margin:6px 0 8px}body.pl4 .pt .ln{display:block;font:14px/1.55 var(--sans);color:var(--mu)}body.pl4 .pt .ln a{color:var(--link)}\n"
         "body.pl4 .sec{margin-top:34px}\n"
         "@media(max-width:900px){body.pl4 .ph2{grid-template-columns:1fr}body.pl4 .ps{border-left:0;padding-left:0;border-top:3px solid var(--pri,#111);padding-top:14px}body.pl4 .pg,body.pl4 .pt-grid{grid-template-columns:repeat(2,minmax(0,1fr))}body.pl4 .ph.hasimg{grid-template-columns:1fr}}\n"
         "@media(max-width:640px){body.pl4 .pg,body.pl4 .pt-grid{grid-template-columns:1fr}body.pl4 .ph h2{font-size:26px}}\n")
    if opt == 'B':   # 카드 중심: 대표 글도 카드 격자 첫 칸처럼, 2열
        c += "body.pl4 .pg{grid-template-columns:repeat(2,minmax(0,1fr))}body.pl4 .pc h3{font-size:20px}body.pl4 .ph h2{font-size:30px}\n"
    return c


def css5():
    return ("body.pl5 .pimg{display:block;width:100%;height:auto;aspect-ratio:3/2;object-fit:cover;background:#f3f3f3}\n"
            "body.pl5 .ph .pimg{aspect-ratio:16/8}\n"
            "body.pl5 .ph-img{display:block;border-radius:12px;overflow:hidden;border:1px solid var(--hair)}\n"
            "body.pl5 .ps .pimg{width:84px;height:56px;border-radius:6px;flex:none}\n"
            "body.pl5 .lead .pimg,body.pl5 .art .pimg{border-radius:10px;margin:0 0 14px;border:1px solid var(--hair)}body.pl5 .art .pimg{aspect-ratio:16/7}\n")


def css(act, base_css=''):
    out = []
    if 1 in act: out.append(css1(act[1], base_css))
    if 2 in act: out.append(css2(act[2]))
    if 3 in act: out.append(css3(act[3]))
    if 4 in act: out.append(css4(act[4]))
    if 5 in act: out.append(css5())
    return '\n'.join(out)


def head(act):
    h = ''
    if 1 in act or 3 in act:
        h += '<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    if 1 in act and act[1] != 'B':
        h += '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">'
    if (1 in act and act[1] == 'B') or 3 in act:
        h += '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700;900&display=swap">'
    return h


def body_class(act):
    return ('pl ' + ' '.join(f'pl{n}' for n in sorted(act))) if act else ''


# ---------------------------------------------------------------- 대표 그림(SVG, 노트마다 자동 생성)
TINT = {'확인됨': '#e4f1e8', '일부만 확인됨': '#faeed8', '아직 확인 안 됨': '#f8e2df'}
COLR = {'확인됨': '#0b5d2f', '일부만 확인됨': '#8a4b00', '아직 확인 안 됨': '#a11a12'}
GLYPH = {'확인됨': '✓', '일부만 확인됨': '△', '아직 확인 안 됨': '?'}


def thumb_svg(B, n, opt='A'):
    try:
        import card as C
        num = C.big_number(n)
    except Exception:
        num = ''
    col = COLR.get(n['verdict'], '#111'); tint = TINT.get(n['verdict'], '#eee')
    cat = (n.get('tags') or [''])[0]
    if opt == 'B' or not num:   # 판정 아이콘형
        big = f'<text x="300" y="250" text-anchor="middle" font-size="190" font-weight="900" fill="{col}" font-family="system-ui,Malgun Gothic,sans-serif">{GLYPH.get(n["verdict"], "?")}</text>'
    else:
        size = max(54, min(150, int(520 / max(1, 0.82 * len(num)))))
        big = f'<text x="300" y="{190 + size // 3}" text-anchor="middle" font-size="{size}" font-weight="900" fill="{col}" letter-spacing="-2">{E(num)}</text>'
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" font-family="\'Noto Serif KR\',\'Nanum Myeongjo\',Batang,serif">'
            f'<rect width="600" height="400" fill="{tint}"/><rect width="14" height="400" fill="{col}"/>'
            f'<text x="44" y="64" font-size="28" font-weight="800" fill="{col}" font-family="system-ui,Malgun Gothic,sans-serif">{E(cat)}</text>'
            f'<rect x="430" y="34" width="140" height="42" rx="21" fill="{col}"/><text x="500" y="63" text-anchor="middle" font-size="20" font-weight="800" fill="#fff" font-family="system-ui,Malgun Gothic,sans-serif">{E(n["verdict"])}</text>'
            f'{big}<line x1="44" y1="330" x2="556" y2="330" stroke="{col}" stroke-width="2" opacity=".4"/>'
            f'<text x="44" y="366" font-size="22" fill="#333" font-family="system-ui,Malgun Gothic,sans-serif">공식 자료로 한 번 더 확인 · {E(n["date"])}</text></svg>')


_MADE = set()


def img_tag(B, n, cls='pimg', alt=''):
    """노트의 대표 그림(그림 층이 켜져 있을 때만). 그림 파일은 docs/img/<노트 id>.svg 로 한 번 쓴다."""
    act = B.POLISH
    if 5 not in act:
        return ''
    p = os.path.join(B.OUT, 'img'); os.makedirs(p, exist_ok=True)
    f = os.path.join(p, n['id'] + '.svg')
    if f not in _MADE:
        open(f, 'w', encoding='utf-8').write(thumb_svg(B, n, act[5])); _MADE.add(f)
    return f'<img class="{cls}" src="{B.BASE}img/{E(n["id"])}.svg" width="600" height="400" alt="{E(alt or ("대표 그림: " + n["title"]))}" loading="lazy">'


# ---------------------------------------------------------------- 4 첫 화면(대표 글 + 최신 목록 + 카드 + 매체 소식)
def home_body(B, notes, topics, notice=''):
    V = B.VERDICTS; BASE = B.BASE
    n0 = notes[0]; side = notes[1:5]; rest = notes[5:]
    vtag = lambda n: f'<span class="v {V[n["verdict"]]}">{E(n["verdict"])}</span>'
    hi = img_tag(B, n0, 'pimg', '')
    hero = (f'<section class="ph{" hasimg" if hi else ""}">' + (f'<a class="ph-img" href="{BASE}n/{n0["id"]}/" tabindex="-1">{hi}</a>' if hi else '')
            + f'<div class="ph-t"><span class="lb">오늘의 확인 노트</span><h2><a href="{BASE}n/{n0["id"]}/">{E(n0["title"])}</a></h2><p>{E(n0["summary"][:110])}{"…" if len(n0["summary"]) > 110 else ""}</p>'
              f'<div class="meta">{vtag(n0)} &nbsp;{E(n0["date"])} · 확인 {E(n0["checked_at"])}</div><a class="btn" href="{BASE}n/{n0["id"]}/">노트 읽기 →</a></div></section>')
    side_h = ''
    if side:
        side_h = '<aside class="ps"><h2>최신 확인 노트</h2>' + ''.join(
            f'<a class="it2" href="{BASE}n/{m["id"]}/">{img_tag(B, m, "pimg", "")}<span><span class="meta">{vtag(m)} {E(m["date"])}</span><b>{E(m["title"])}</b></span></a>' for m in side) + '</aside>'
    front = f'<section class="ph2">{hero}{side_h}</section>'
    grid = ''
    if rest:
        grid = '<section class="sec"><h2>지난 확인 노트</h2><div class="pg">' + ''.join(
            f'<article class="pc"><a href="{BASE}n/{m["id"]}/">{img_tag(B, m, "pimg", "")}<div class="pc-b">{vtag(m)}<span class="pc-d">{E(m["date"])}</span><h3>{E(m["title"])}</h3><p>{E(m["summary"][:70])}…</p></div></a></article>' for m in rest) + '</div></section>'
    note = f' {E(notice)}' if notice else ''
    tp = ''.join(f'<div class="pt"><span class="lb">{t["media_count"]}개 매체</span><b>{E(t["title"])}</b>'
                 + ''.join(f'<span class="ln"><a href="{E(i["link"])}" rel="noopener nofollow">{E(i["source"])}</a> {E(i["title"][:46])}</span>' for i in t['items'][:3]) + '</div>' for t in topics[:12])
    topics_h = (f'<section class="sec"><h2>여러 매체가 함께 다룬 소식</h2><p class="sub">제목·매체·링크만 모았습니다. 이 가운데 제도·숫자·날짜가 걸린 소식을 골라 확인 노트로 씁니다.{note}</p><div class="pt-grid">{tp}</div></section>') if tp else ''
    return front + grid + topics_h + B.extras_html()
