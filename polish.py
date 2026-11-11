# -*- coding: utf-8 -*-
"""다듬기(polish): 투박한 출발 모습을 걸음마다 고품질로 바꾸는 층 모음. 파이썬 기본 기능만 쓴다.
설정: site.local.json 의 "polish": {"1": "A", "2": "B", ...}(걸음 번호: 고른 안) 또는 환경변수 SITE_POLISH(JSON). 없으면 출발 모습 그대로.
build.py 가 css()·head()·body_class()·nav_html()·mast_extra()·home_body()·img_tag() 를 부른다. 걸음 안내(왜·참고·안)는 다듬기.json."""
import hashlib, html, json, os, re

E = html.escape
CATS = []   # 분야 탭(노트의 첫 태그 가운데 많은 것). build.py 가 노트를 읽은 뒤 채운다


def active(S):
    p = S.get('polish') or {}
    return {int(k): v for k, v in p.items() if str(k).isdigit() and v}


def cat_of(n):
    return (n.get('tags') or ['기타'])[0]


def set_cats(notes):
    global CATS
    cnt = {}
    for n in notes:
        cnt[cat_of(n)] = cnt.get(cat_of(n), 0) + 1
    CATS = [c for c, _ in sorted(cnt.items(), key=lambda x: (-x[1], x[0]))][:6]


# ---------------------------------------------------------------- 1 글자와 줄 간격
FONT_A = "'Pretendard Variable',Pretendard,'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',system-ui,sans-serif"
FONT_B = "'Noto Serif KR','Nanum Myeongjo','Batang',serif"


def css1(opt, base_css):
    f = FONT_A if opt != 'B' else FONT_B
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


# ---------------------------------------------------------------- 2 색과 대비 (주색이 제호·링크·구획 제목·단추·딱지·탭에 반복된다)
def css2(opt):
    if opt == 'B':
        pri, sec, ink, mu, hair, bgs, bgp = '#14532d', '#c2410c', '#14201a', '#46564c', '#d6e4d9', '#eaf3ec', '#f5f9f5'
    else:
        pri, sec, ink, mu, hair, bgs, bgp = '#1e3a8a', '#b45309', '#0f172a', '#475569', '#d9e0ee', '#e8eefb', '#f6f8fc'
    return (f":root{{--pri:{pri};--sec:{sec};--ink:{ink};--mu:{mu};--hair:{hair};--bgs:{bgs};--bg:{bgp};--link:{pri}}}\n"
            f"body.pl2{{background:{bgp}}}body.pl2 .mast{{background:#fff;border-top:6px solid var(--pri);border-bottom:1px solid var(--hair)}}\n"
            "body.pl2 nav.menu{background:#fff;border-bottom:1px solid var(--hair)}body.pl2 nav.menu a:hover{color:var(--pri)}\n"
            "body.pl2 .sec{border-top:0}body.pl2 .sec h2{color:var(--pri);border-left:5px solid var(--sec);padding-left:10px;font-size:18px;letter-spacing:0}\n"
            "body.pl2 .lb{color:var(--pri)}body.pl2 a:hover{color:var(--pri)}body.pl2 .notice{background:var(--bgs);border-color:var(--hair)}\n"
            "body.pl2 .art,body.pl2 .page{background:#fff;padding:28px 34px;margin-top:24px;border:1px solid var(--hair);border-radius:12px}\n"
            "body.pl2 .art h2{border-top:0;border-left:5px solid var(--sec);padding:2px 0 2px 10px;color:var(--pri);font-size:16px}\n"
            "body.pl2 footer{border-top:4px solid var(--pri);background:var(--bgs)}body.pl2 .v.ok{background:#e4f1e8}body.pl2 .v.part{background:#faeed8}body.pl2 .v.no{background:#f8e2df}\n"
            "body.pl2 .tp,body.pl2 .lead{background:#fff}\n")


# ---------------------------------------------------------------- 3 제호와 메뉴 (분야 탭 + 오른쪽 검색·소식 받기)
def css3(opt):
    base = ("body.pl3 .mast .wrap{position:relative}body.pl3 .dateline{font:600 14px/1.2 var(--sans);border:0;padding:10px 0 0;color:var(--mu)}\n"
            "body.pl3 .mast-r{position:absolute;right:20px;top:14px;display:flex;gap:10px;align-items:center}body.pl3 .mast-r a{display:inline-flex;align-items:center;justify-content:center;min-width:38px;height:38px;border-radius:999px;border:1px solid var(--hair);background:#fff;color:var(--ink)}\n"
            "body.pl3 .mast-r a.sub{padding:0 16px;background:var(--pri,#111);border-color:var(--pri,#111);color:#fff;font:700 14px/1 var(--sans)}body.pl3 .mast-r a:hover{text-decoration:none;opacity:.88}\n"
            "body.pl3 nav.menu{scrollbar-width:none;position:sticky;top:0;z-index:30;background:#fff;gap:0;justify-content:flex-start;padding:0;border-top:1px solid var(--hair);border-bottom:1px solid var(--hair);overflow-x:auto;-webkit-overflow-scrolling:touch}\n"
            "body.pl3 nav.menu::-webkit-scrollbar{display:none}body.pl3 nav.menu a,body.pl3 details.mn summary{display:block;padding:14px 18px;font:700 15px/1 var(--sans);white-space:nowrap;border-bottom:3px solid transparent}\n"
            "body.pl3 nav.menu a:hover{text-decoration:none;border-bottom-color:var(--pri,#111)}body.pl3 nav.menu a.on{border-bottom-color:var(--pri,#111);color:var(--pri,#111)}body.pl3 details.mn{margin-left:auto}body.pl3 .mnp{top:46px;right:0}\n")
    if opt == 'B':
        return base + ("body.pl3 .mast .wrap{display:flex;align-items:baseline;gap:16px;flex-wrap:wrap}body.pl3 .dateline{order:3;flex-basis:100%;padding:0 0 8px}\n"
                       "body.pl3 .logo{text-align:left;font:900 34px/1.1 'Noto Serif KR','Nanum Myeongjo',Batang,serif;margin:14px 0 8px;color:var(--pri,#111)}body.pl3 .mast{border-bottom:0}body.pl3 .mast-r{top:12px}\n"
                       "@media(max-width:640px){body.pl3 .logo{font-size:28px}body.pl3 .mast-r{position:static;margin-left:auto}}\n")
    return base + ("body.pl3 .dateline{text-align:center}body.pl3 .logo{font:900 46px/1.1 'Noto Serif KR','Nanum Myeongjo',Batang,serif;letter-spacing:-.04em;margin:6px 0 10px}\n"
                   "@media(max-width:640px){body.pl3 .logo{font-size:30px}body.pl3 .mast-r{top:6px;right:12px}body.pl3 .mast-r a.sub{display:none}body.pl3 .dateline{font-size:12.5px;padding-right:56px;text-align:left}}\n")


# ---------------------------------------------------------------- 4 첫 화면 짜임 / 5 그림
def css4(opt):
    c = ("body.pl4 .ph{display:grid;gap:26px;padding:26px 0 6px;align-items:center}body.pl4 .ph.hasimg{grid-template-columns:minmax(0,45fr) minmax(0,55fr)}\n"
         "body.pl4 .ph h2{font-size:32px;line-height:1.3;margin:6px 0 12px}body.pl4 .ph p{font-size:17px;color:var(--mu);margin:0 0 12px}\n"
         "body.pl4 .ph-t .meta{font:14px/1.5 var(--sans);color:var(--mu)}body.pl4 .btn{display:inline-block;margin-top:14px;padding:11px 18px;background:var(--pri,#111);color:#fff;font:700 15px/1 var(--sans);border-radius:6px}body.pl4 .btn:hover{text-decoration:none;opacity:.9;color:#fff}\n"
         "body.pl4 .pg{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px}body.pl4 .pc{border:1px solid var(--hair);border-radius:10px;overflow:hidden;background:#fff}\n"
         "body.pl4 .pc a{display:block;height:100%}body.pl4 .pc a:hover{text-decoration:none}body.pl4 .pc a:hover h3{text-decoration:underline}body.pl4 .pc-b{padding:12px 14px 16px}\n"
         "body.pl4 .pc h3{font:700 16px/1.45 var(--sans);margin:8px 0 6px}body.pl4 .pc p{font:14px/1.6 var(--sans);color:var(--mu);margin:0}body.pl4 .pc-d{font:13px/1 var(--sans);color:var(--mu);margin-left:8px}\n"
         "body.pl4 .pt-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}body.pl4 .pt{border:1px solid var(--hair);border-radius:10px;overflow:hidden;background:#fff}body.pl4 .pt-b{padding:12px 16px 16px}\n"
         "body.pl4 .pt b{display:block;font:700 17px/1.45 var(--sans);margin:6px 0 8px}body.pl4 .pt .ln{display:block;font:14px/1.55 var(--sans);color:var(--mu)}body.pl4 .pt .ln a{color:var(--link)}\n"
         "body.pl4 .sec{margin-top:30px}body.pl4 .cat-note{font:14px/1.5 var(--sans);color:var(--mu)}\n"
         "@media(max-width:1000px){body.pl4 .pg{grid-template-columns:repeat(2,minmax(0,1fr))}body.pl4 .pt-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}\n"
         "@media(max-width:760px){body.pl4 .ph.hasimg{grid-template-columns:1fr}body.pl4 .ph h2{font-size:25px}}\n"
         "@media(max-width:560px){body.pl4 .pg,body.pl4 .pt-grid{grid-template-columns:1fr}}\n")
    if opt == 'B':   # 카드 중심: 큰 카드 2열(글이 많을 때)
        c += "body.pl4 .pg{grid-template-columns:repeat(2,minmax(0,1fr))}body.pl4 .pc h3{font-size:19px}\n"
    return c


def css5():
    return ("body.pl5 .pimg{display:block;width:100%;height:auto;background:#f3f3f3}\n"
            "body.pl5 .ph-img{display:block;border-radius:12px;overflow:hidden;border:1px solid var(--hair)}\n"
            "body.pl5 .pt .pimg{aspect-ratio:2/1}body.pl5 .lead .pimg{border-radius:10px;margin:0 0 14px;border:1px solid var(--hair)}\n"
            "body.pl5 .art .pimg{border-radius:10px;margin:0 0 16px;border:1px solid var(--hair);aspect-ratio:3/1}\n")


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


# ---------------------------------------------------------------- 3: 분야 탭 메뉴와 제호 오른쪽(검색·소식 받기)
SEARCH_ICON = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg>'


def nav_html(B, items, path):
    """분야 탭(노트 태그에서 자동) + 「더 보기」(기능 메뉴). 분야 탭은 첫 화면의 카드를 걸러 보여 준다(?cat=이름)."""
    BASE = B.BASE
    tabs = f'<a href="{BASE}" data-cat="" class="{"on" if not path else ""}">전체</a>' + ''.join(f'<a href="{BASE}?cat={E(c)}" data-cat="{E(c)}">{E(c)}</a>' for c in CATS)
    more = ''.join(f'<a href="{u}">{E(n)}</a>' for n, u in items[1:])
    return f'<div class="wrap"><nav class="menu cats">{tabs}<details class="mn"><summary>더 보기</summary><div class="mnp">{more}</div></details></nav></div>'


def mast_extra(B):
    BASE = B.BASE; M = (B.S.get('monetize') or {}); nl = (M.get('newsletter') or {}).get('url')
    srch = f'<a class="ic" href="{BASE}search/" aria-label="사이트 안 검색">{SEARCH_ICON}</a>' if B.part('search', False) else ''
    sub_url = nl or (BASE + 'feed.xml' if not (B.NOURL or B.DEMO) else BASE + 'contact/')
    return f'<div class="mast-r">{srch}<a class="sub" href="{E(sub_url)}">소식 받기</a></div>'


# ---------------------------------------------------------------- 5 대표 그림(SVG): 판정 색 + 분야 아이콘 + 큰 숫자, 표시 비율과 같은 비율로 그려 잘리지 않게
TINT = {'확인됨': '#dcefe3', '일부만 확인됨': '#f7e7c8', '아직 확인 안 됨': '#f6d9d5'}
COLR = {'확인됨': '#0b5d2f', '일부만 확인됨': '#8a4b00', '아직 확인 안 됨': '#a11a12'}
GLYPH = {'확인됨': '✓', '일부만 확인됨': '△', '아직 확인 안 됨': '?'}


def icon_for(n):
    t = (n.get('title', '') + ' ' + ' '.join(n.get('tags') or []))
    if re.search(r'청약|주택|부동산|전세|월세|아파트', t):
        return 'house'
    if re.search(r'수출|취업|고용|통계|지수|성장|물가', t):
        return 'bars'
    if re.search(r'세금|세액|과세|채권|국고|입찰|대출|금리|연금|보험|적금', t):
        return 'coin'
    if re.search(r'유류|유가|연료|에너지|전기|가스', t):
        return 'drop'
    return 'doc'


def icon_svg(kind, col, x, y, s):
    """분야 아이콘(도형만). (x,y)=왼쪽 위, s=한 변."""
    u = s / 100.0
    if kind == 'house':
        return f'<g transform="translate({x},{y}) scale({u})" fill="none" stroke="{col}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"><path d="M10 48 50 14l40 34"/><path d="M20 42v44h60V42"/><path d="M42 86V60h16v26"/></g>'
    if kind == 'bars':
        return f'<g transform="translate({x},{y}) scale({u})" fill="{col}"><rect x="10" y="56" width="16" height="34" rx="3"/><rect x="36" y="36" width="16" height="54" rx="3"/><rect x="62" y="16" width="16" height="74" rx="3"/><rect x="6" y="92" width="88" height="5" rx="2"/></g>'
    if kind == 'coin':
        return f'<g transform="translate({x},{y}) scale({u})" fill="none" stroke="{col}" stroke-width="7"><circle cx="50" cy="50" r="38"/><circle cx="50" cy="50" r="24"/><path d="M50 36v28M43 43h14M43 57h14" stroke-linecap="round"/></g>'
    if kind == 'drop':
        return f'<g transform="translate({x},{y}) scale({u})" fill="none" stroke="{col}" stroke-width="7" stroke-linejoin="round"><path d="M50 8C50 8 18 46 18 64a32 32 0 0 0 64 0C82 46 50 8 50 8Z"/></g>'
    return f'<g transform="translate({x},{y}) scale({u})" fill="none" stroke="{col}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"><path d="M22 8h40l18 18v66H22z"/><path d="M62 8v18h18M34 48h32M34 62h32M34 76h22"/></g>'


def pattern_defs(col, key):
    h = int(hashlib.md5(key.encode()).hexdigest()[:2], 16) % 3
    if h == 0:
        return f'<pattern id="pt" width="26" height="26" patternUnits="userSpaceOnUse"><circle cx="5" cy="5" r="2.4" fill="{col}" opacity=".16"/></pattern>'
    if h == 1:
        return f'<pattern id="pt" width="24" height="24" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="24" fill="{col}" opacity=".08"/></pattern>'
    return f'<pattern id="pt" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M0 30V0h30" fill="none" stroke="{col}" opacity=".12" stroke-width="2"/></pattern>'


def thumb_svg(B, n, opt='A', w=600, h=400):
    """노트의 대표 그림. 표시 칸과 같은 비율(w:h)로 그려서 잘리지 않는다."""
    try:
        import card as C
        num = C.big_number(n)
    except Exception:
        num = ''
    v = n['verdict']; col = COLR.get(v, '#111'); tint = TINT.get(v, '#eee'); cat = cat_of(n); ic = icon_for(n)
    cx = w * 0.5; pad = int(w * 0.06); fs = int(h * 0.07)
    if opt == 'B' or not num:
        big = icon_svg(ic, col, w * 0.5 - h * 0.22, h * 0.26, h * 0.44) + f'<text x="{cx}" y="{h * 0.84}" text-anchor="middle" font-size="{int(h * 0.1)}" font-weight="800" fill="{col}" font-family="system-ui,Malgun Gothic,sans-serif">{E(v)}</text>'
    else:
        size = max(int(h * 0.16), min(int(h * 0.36), int(w * 0.84 / max(1, 0.82 * len(num)))))
        big = f'<text x="{cx}" y="{h * 0.62}" text-anchor="middle" font-size="{size}" font-weight="900" fill="{col}" letter-spacing="-2">{E(num)}</text>'
    corner = icon_svg(ic, col, w - h * 0.34 - pad, pad * 0.9, h * 0.28).replace('<g ', '<g opacity="0.55" ', 1) if (opt != 'B' and num) else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="\'Noto Serif KR\',\'Nanum Myeongjo\',Batang,serif">'
            f'<defs>{pattern_defs(col, n["id"])}</defs><rect width="{w}" height="{h}" fill="{tint}"/><rect width="{w}" height="{h}" fill="url(#pt)"/>'
            f'<rect width="{int(w * .025)}" height="{h}" fill="{col}"/>' + corner
            + f'<text x="{pad + int(w * .02)}" y="{pad + fs}" font-size="{fs}" font-weight="800" fill="{col}" font-family="system-ui,Malgun Gothic,sans-serif">{E(cat)}</text>'
            f'<rect x="{pad + int(w * .02)}" y="{h - pad - int(h * .13)}" width="{int(w * .36)}" height="{int(h * .1)}" rx="{int(h * .05)}" fill="{col}"/>'
            f'<text x="{pad + int(w * .02) + int(w * .18)}" y="{h - pad - int(h * .13) + int(h * .07)}" text-anchor="middle" font-size="{int(h * .06)}" font-weight="800" fill="#fff" font-family="system-ui,Malgun Gothic,sans-serif">{E(v)}</text>'
            f'{big}</svg>')


def topic_svg(t, w=600, h=300):
    key = t.get('title', '')
    col = '#334155'; tint = '#e8edf5'; kinds = ['bars', 'doc', 'coin', 'house', 'drop']
    ic = kinds[int(hashlib.md5(key.encode()).hexdigest()[:2], 16) % len(kinds)]
    mc = t.get('media_count', 0)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="system-ui,Malgun Gothic,sans-serif"><defs>{pattern_defs(col, key)}</defs>'
            f'<rect width="{w}" height="{h}" fill="{tint}"/><rect width="{w}" height="{h}" fill="url(#pt)"/>' + icon_svg(ic, col, w - h * 0.62, h * 0.1, h * 0.5).replace('<g ', '<g opacity="0.5" ', 1)
            + f'<text x="{w * .06}" y="{h * .62}" font-size="{int(h * .42)}" font-weight="900" fill="#1e293b">{mc}</text><text x="{w * .06 + len(str(mc)) * h * .26}" y="{h * .62}" font-size="{int(h * .13)}" font-weight="800" fill="#1e293b"> 개 매체</text>'
            f'<text x="{w * .06}" y="{h * .84}" font-size="{int(h * .1)}" fill="#475569">같은 소식을 함께 다뤘습니다</text></svg>')


_MADE = set()


def _write(B, name, svg):
    p = os.path.join(B.OUT, 'img'); os.makedirs(p, exist_ok=True)
    f = os.path.join(p, name)
    if f not in _MADE:
        open(f, 'w', encoding='utf-8').write(svg); _MADE.add(f)


def img_tag(B, n, cls='pimg', alt='', kind='card'):
    """노트의 대표 그림(그림 층이 켜져 있을 때만). kind: card(3:2)·wide(3:1, 글 쪽 위). 파일은 docs/img/ 에 한 번 쓴다."""
    act = B.POLISH
    if 5 not in act:
        return ''
    w, h = (600, 400) if kind == 'card' else (1200, 400)
    name = f'{n["id"]}{"" if kind == "card" else "_w"}.svg'
    _write(B, name, thumb_svg(B, n, act[5], w, h))
    return f'<img class="{cls}" src="{B.BASE}img/{E(name)}" width="{w}" height="{h}" alt="{E(alt or ("대표 그림: " + n["title"]))}" loading="lazy">'


def topic_img(B, t, i):
    if 5 not in B.POLISH:
        return ''
    name = f'topic{i}.svg'; _write(B, name, topic_svg(t))
    return f'<img class="pimg" src="{B.BASE}img/{name}" width="600" height="300" alt="" loading="lazy">'


# ---------------------------------------------------------------- 4 첫 화면(대표 글 + 그림 카드 한 줄 + 매체 소식 카드)
FILTER_JS = ('<script>(function(){var m=location.search.match(/[?&]cat=([^&]*)/);if(!m)return;var c=decodeURIComponent(m[1]);'
             'document.querySelectorAll("[data-cat]").forEach(function(e){if(e.tagName==="A"&&e.closest("nav"))return;if(e.dataset.cat!==c)e.style.display="none"});'
             'document.querySelectorAll("nav.cats a").forEach(function(a){a.classList.toggle("on",a.dataset.cat===c)})})()</script>')


def home_body(B, notes, topics, notice=''):
    V = B.VERDICTS; BASE = B.BASE
    n0 = notes[0]; row = notes[1:5]; rest = notes[5:]
    vtag = lambda n: f'<span class="v {V[n["verdict"]]}">{E(n["verdict"])}</span>'
    hi = img_tag(B, n0, 'pimg', '')
    hero = (f'<section class="ph{" hasimg" if hi else ""}" data-cat="{E(cat_of(n0))}">' + (f'<a class="ph-img" href="{BASE}n/{n0["id"]}/" tabindex="-1">{hi}</a>' if hi else '')
            + f'<div class="ph-t"><span class="lb">오늘의 확인 노트 · {E(cat_of(n0))}</span><h2><a href="{BASE}n/{n0["id"]}/">{E(n0["title"])}</a></h2><p>{E(n0["summary"][:100])}{"…" if len(n0["summary"]) > 100 else ""}</p>'
              f'<div class="meta">{vtag(n0)} &nbsp;{E(n0["date"])} · 확인 {E(n0["checked_at"])}</div><a class="btn" href="{BASE}n/{n0["id"]}/">노트 읽기 →</a></div></section>')

    def card(m):
        return (f'<article class="pc" data-cat="{E(cat_of(m))}"><a href="{BASE}n/{m["id"]}/">{img_tag(B, m, "pimg", "")}<div class="pc-b">{vtag(m)}<span class="pc-d">{E(m["date"])}</span>'
                f'<h3>{E(m["title"])}</h3><p>{E(m["summary"][:56])}…</p></div></a></article>')
    grid = ('<section class="sec"><h2>최신 확인 노트</h2><div class="pg">' + ''.join(card(m) for m in row) + '</div></section>') if row else ''
    more = ('<section class="sec"><h2>지난 확인 노트</h2><div class="pg">' + ''.join(card(m) for m in rest) + '</div></section>') if rest else ''
    note = f' {E(notice)}' if notice else ''
    tp = ''.join(f'<div class="pt">{topic_img(B, t, i)}<div class="pt-b"><span class="lb">{t["media_count"]}개 매체</span><b>{E(t["title"])}</b>'
                 + ''.join(f'<span class="ln"><a href="{E(i_["link"])}" rel="noopener nofollow">{E(i_["source"])}</a> {E(i_["title"][:46])}</span>' for i_ in t['items'][:3]) + '</div></div>' for i, t in enumerate(topics[:12]))
    topics_h = (f'<section class="sec"><h2>여러 매체가 함께 다룬 소식</h2><p class="sub">제목·매체·링크만 모았습니다. 이 가운데 제도·숫자·날짜가 걸린 소식을 골라 확인 노트로 씁니다.{note}</p><div class="pt-grid">{tp}</div></section>') if tp else ''
    return hero + grid + more + topics_h + B.extras_html() + FILTER_JS
