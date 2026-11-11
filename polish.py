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
                   "@media(max-width:640px){body.pl3 .logo{font-size:30px}body.pl3 .mast-r{top:6px;right:12px}body.pl3 .mast-r a.sub{display:none}body.pl3 nav.menu.cats{-webkit-mask-image:linear-gradient(90deg,#000 86%,transparent);mask-image:linear-gradient(90deg,#000 86%,transparent)}body.pl3 .dateline{font-size:13px;padding-right:56px;text-align:left}}\n")


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


def css6(opt):
    return ("body.pl6 .nbs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}body.pl6 .nb{display:block;background:#fff;border:1px solid var(--hair);border-radius:10px;padding:16px 18px;border-top:4px solid var(--sec,#b45309)}\n"
            "body.pl6 .nb:hover{text-decoration:none;box-shadow:0 4px 14px rgba(0,0,0,.08)}body.pl6 .nb-c{display:block;font:700 13px/1 var(--sans);color:var(--mu)}body.pl6 .nb b{display:block;font:900 30px/1.2 var(--sans);margin:8px 0 6px;letter-spacing:-.02em}body.pl6 .nb-t{display:block;font:14px/1.5 var(--sans);color:var(--mu)}\n"
            "body.pl6 .duo{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px}body.pl6 .cover{display:block;background:var(--pri,#111);color:#fff;border-radius:12px;padding:22px 26px}body.pl6 .cover:hover{text-decoration:none;opacity:.95}\n"
            "body.pl6 .cover small{display:block;font:700 13px/1 var(--sans);opacity:.8;letter-spacing:.08em}body.pl6 .cover b{display:block;font:900 30px/1.2 'Noto Serif KR',serif;margin:10px 0 8px}body.pl6 .cover ul{margin:0;padding-left:18px;font:15px/1.7 var(--sans)}body.pl6 .cover span{display:inline-block;margin-top:12px;font:700 14px/1 var(--sans);border-bottom:2px solid #fff}\n"
            "body.pl6 .subs{background:#fff;border:1px solid var(--hair);border-radius:12px;padding:22px 26px}body.pl6 .subs b{display:block;font:800 20px/1.4 var(--sans);margin-bottom:6px}body.pl6 .subs p{font:15px/1.7 var(--sans);color:var(--mu);margin:0 0 14px}body.pl6 .subs a.btn{margin:0 8px 8px 0;display:inline-block;padding:10px 16px;border-radius:6px;background:var(--pri,#111);color:#fff;font:700 14px/1 var(--sans)}body.pl6 .subs a.btn.alt{background:#fff;color:var(--pri,#111);border:1px solid var(--pri,#111)}\n"
            "@media(max-width:900px){body.pl6 .nbs{grid-template-columns:repeat(2,minmax(0,1fr))}body.pl6 .duo{grid-template-columns:1fr}}\n")


def css7(opt):
    c = ("body.pl7 .vband{display:flex;gap:12px;align-items:center;flex-wrap:wrap;padding:12px 16px;border-radius:8px;margin:0 0 18px;font:15px/1.5 var(--sans)}body.pl7 .vband b{font:800 17px/1 var(--sans)}\n"
         "body.pl7 .vband.ok{background:#dcefe3;color:#0b4a27}body.pl7 .vband.part{background:#f7e7c8;color:#6b3a00}body.pl7 .vband.no{background:#f6d9d5;color:#8a1610}\n"
         "body.pl7 .nbox{border:2px solid var(--pri,#111);border-radius:12px;padding:16px 20px;margin:0 0 22px;background:#fff}body.pl7 .nbox span{font:700 13px/1 var(--sans);color:var(--mu)}body.pl7 .nbox b{display:block;font:900 44px/1.15 var(--sans);margin:6px 0 4px;letter-spacing:-.02em}body.pl7 .nbox em{font:normal 15px/1.6 var(--sans);color:var(--mu)}\n"
         "body.pl7 ul.srcs{list-style:none;margin:0;padding:0;display:grid;gap:12px}body.pl7 .src-card{border:1px solid var(--hair);border-radius:10px;padding:14px 16px;background:#fff}body.pl7 .src-card p{margin:0 0 10px;font-size:17px;line-height:1.7}\n"
         "body.pl7 .src-meta{display:flex;gap:12px;align-items:center;flex-wrap:wrap;font:14px/1.4 var(--sans);color:var(--mu)}body.pl7 .src-meta b{color:var(--ink)}body.pl7 .src-meta a{margin-left:auto;padding:7px 12px;border:1px solid var(--pri,#111);border-radius:6px;color:var(--pri,#111);font-weight:700}\n"
         "body.pl7 .unc{border:1px dashed var(--sec,#b45309);border-radius:10px;padding:12px 16px 4px;background:#fffaf0}body.pl7 .rel{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:8px}body.pl7 .rel a{display:block;border:1px solid var(--hair);border-radius:10px;overflow:hidden;background:#fff}body.pl7 .rel a:hover{text-decoration:none}\n"
         "body.pl7 .rel .rb{padding:10px 12px 14px;font:700 15px/1.45 var(--sans)}body.pl7 .share{display:flex;gap:10px;flex-wrap:wrap;margin:26px 0 0}body.pl7 .share button,body.pl7 .share a{font:700 14px/1 var(--sans);padding:10px 16px;border:1px solid var(--hair);border-radius:6px;background:#fff;color:var(--ink);cursor:pointer;width:auto}\n"
         "@media(max-width:700px){body.pl7 .rel{grid-template-columns:1fr}body.pl7 .nbox b{font-size:34px}}@media print{body.pl7 .share,body.pl7 .rel,header,nav,footer,.bnav{display:none!important}}\n")
    if opt == 'B':
        c += "body.pl7 .vband{border-left:6px solid currentColor;border-radius:0 8px 8px 0}body.pl7 .nbox{border-width:0;border-left:6px solid var(--sec,#b45309);border-radius:0 12px 12px 0}\n"
    return c


def css8(opt):
    return ("body.pl8 .trust{background:#fff;border-top:1px solid var(--hair);padding:26px 0}body.pl8 .trust .wrap{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}body.pl8 .trust b{display:block;font:800 17px/1.4 var(--sans);color:var(--pri,#111);margin-bottom:6px}body.pl8 .trust p{margin:0;font:15px/1.7 var(--sans);color:var(--mu)}\n"
            "body.pl8 footer.ft{margin-top:0;padding:30px 0 20px;border-top:4px solid var(--pri,#111);background:var(--bgs,#f3f3f3);font:15px/1.8 var(--sans);color:var(--mu)}body.pl8 .ft-grid{display:grid;grid-template-columns:1.6fr 1fr 1fr;gap:28px}body.pl8 .ft b{display:block;color:var(--ink);font:800 16px/1.4 var(--sans);margin-bottom:8px}body.pl8 .ft a{display:block;margin:0 0 6px;color:var(--ink)}\n"
            "body.pl8 .ft-c{margin:18px 0 0;padding-top:14px;border-top:1px solid var(--hair);font:13px/1.7 var(--sans)}\n"
            "@media(max-width:760px){body.pl8 .trust .wrap,body.pl8 .ft-grid{grid-template-columns:1fr}}\n")


def css9(opt):
    return ("body.pl9 .bnav{display:none}\n"
            "@media(max-width:640px){body.pl9{padding-bottom:64px}body.pl9 .bnav{display:flex;position:fixed;left:0;right:0;bottom:0;z-index:50;background:#fff;border-top:1px solid var(--hair);box-shadow:0 -4px 14px rgba(0,0,0,.08)}\n"
            "body.pl9 .bnav a{flex:1;text-align:center;padding:10px 4px 12px;font:700 13px/1.3 var(--sans);color:var(--mu)}body.pl9 .bnav a b{display:block;font-size:20px;line-height:1.2}body.pl9 .bnav a.on,body.pl9 .bnav a:hover{color:var(--pri,#111);text-decoration:none}\n"
            "body.pl9 .bnav a.cta{background:var(--pri,#111);color:#fff}}\n")


def css(act, base_css=''):
    out = []
    if 1 in act: out.append(css1(act[1], base_css))
    if 2 in act: out.append(css2(act[2]))
    if 3 in act: out.append(css3(act[3]))
    if 4 in act: out.append(css4(act[4]))
    if 5 in act: out.append(css5())
    if 6 in act: out.append(css6(act[6]))
    if 7 in act: out.append(css7(act[7]))
    if 8 in act: out.append(css8(act[8]))
    if 9 in act: out.append(css9(act[9]))
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
        big = icon_svg(ic, col, w * 0.5 - h * 0.2, h * 0.2, h * 0.5)   # 판정 글자는 아래 딱지가 맡는다(겹치지 않게)
    else:
        wide = w >= h * 2.5
        size = max(int(h * 0.16), min(int(h * (0.30 if wide else 0.36)), int(w * 0.84 / max(1, 0.82 * len(num)))))
        big = f'<text x="{cx}" y="{h * (0.50 if wide else 0.62)}" text-anchor="middle" font-size="{size}" font-weight="900" fill="{col}" letter-spacing="-2">{E(num)}</text>'
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
    nb = numbers_band(B, notes) if 6 in B.POLISH else ''
    cs = cover_subscribe(B, notes) if 6 in B.POLISH and B.POLISH[6] != 'B' else ''
    return hero + grid + nb + more + cs + topics_h + B.extras_html() + FILTER_JS


# ---------------------------------------------------------------- 6 오늘의 숫자 띠·호 표지·소식 받기
NOTES = []


def set_notes(notes):
    global NOTES
    NOTES = notes


def _num(n):
    try:
        import card as C
        return C.big_number(n)
    except Exception:
        return ''


def numbers_band(B, notes):
    items = [(n, _num(n)) for n in notes if _num(n)][:4]
    if not items:
        return ''
    boxes = ''.join(f'<a class="nb" href="{B.BASE}n/{n["id"]}/" data-cat="{E(cat_of(n))}"><span class="nb-c">{E(cat_of(n))} · {E(n["verdict"])}</span><b style="color:{COLR.get(n["verdict"], "#111")}">{E(num)}</b><span class="nb-t">{E(n["title"][:34])}{"…" if len(n["title"]) > 34 else ""}</span></a>' for n, num in items)
    return f'<section class="sec"><h2>오늘의 숫자</h2><div class="nbs">{boxes}</div></section>'


def cover_subscribe(B, notes):
    BASE = B.BASE; n0 = notes[0]; same = [n for n in notes if n['date'] == n0['date']][:3]
    href = BASE + (f'issue/{n0["date"]}/' if B.part('issue') else f'n/{n0["id"]}/')
    cover = (f'<a class="cover" href="{href}"><small>오늘 호 · {E(n0["date"])}</small><b>{E(B.S["name"])}</b><ul>' + ''.join(f'<li>{E(n["title"][:40])}</li>' for n in same) + '</ul><span>이번 호 보기 →</span></a>')
    M = (B.S.get('monetize') or {}); nl = (M.get('newsletter') or {}).get('url')
    btn = (f'<a class="btn" href="{E(nl)}" rel="noopener" target="_blank">메일로 받기</a>' if nl else '') + (f'<a class="btn alt" href="{BASE}feed.xml">RSS 로 받기</a>' if not (B.NOURL or B.DEMO) else '') + f'<a class="btn alt" href="{BASE}contact/">문의하기</a>'
    subs = f'<div class="subs"><b>새 확인 노트를 받아 보세요</b><p>공식 자료로 확인한 노트를 올릴 때마다 알려 드립니다. 광고성 메일은 보내지 않습니다.</p>{btn}</div>'
    return f'<section class="sec"><h2>오늘 호와 소식 받기</h2><div class="duo">{cover}{subs}</div></section>'


# ---------------------------------------------------------------- 7 글 쪽(판정 띠·핵심 숫자·출처 카드·관련 글·공유)
VDESC = {'확인됨': '공식 자료에서 같은 내용을 직접 찾았습니다.', '일부만 확인됨': '일부만 찾았고 나머지는 찾지 못했습니다.', '아직 확인 안 됨': '공식 자료에서 찾지 못했습니다. 틀렸다는 뜻은 아닙니다.'}


def related_notes(n, k=3):
    tags = set(n.get('tags') or [])
    sc = sorted((m for m in NOTES if m['id'] != n['id']), key=lambda m: (-len(tags & set(m.get('tags') or [])), m['date']), reverse=False)
    sc = sorted(sc, key=lambda m: -len(tags & set(m.get('tags') or [])))
    return sc[:k]


def note_body(B, n, extra_html=''):
    BASE = B.BASE; V = B.VERDICTS; v = n['verdict']
    li = lambda xs: ''.join(f'<li>{E(x)}</li>' for x in xs)
    num = _num(n)
    wide = img_tag(B, n, 'pimg', '', 'wide')
    ex = '<span class="ex">예시 — 화면 틀 시험용 가짜 노트입니다</span>' if n.get('example') else ''
    facts = ''.join(f'<li class="src-card"><p>{E(f["text"])}</p><div class="src-meta"><b>{E(f["source"])}</b><span>확인 시각 {E(n["checked_at"][:16])}</span><a href="{E(f["url"])}" rel="noopener nofollow" target="_blank">출처 열기 ↗</a></div></li>' for f in n.get('facts', []))
    reports = ''.join(f'<li><a href="{E(r["url"])}" rel="noopener nofollow">{E(r["title"])}</a> · {E(r["source"])}</li>' for r in n.get('reports', []))
    rel = related_notes(n)
    relh = ('<h2>관련 확인 노트</h2><div class="rel">' + ''.join(f'<a href="{BASE}n/{m["id"]}/">{img_tag(B, m, "pimg", "")}<div class="rb">{E(m["title"])}</div></a>' for m in rel) + '</div>') if rel else ''
    share = (f'<div class="share"><button type="button" onclick="navigator.clipboard&&navigator.clipboard.writeText(location.href).then(function(){{this.textContent=\'복사했습니다\'}}.bind(this))">링크 복사</button>'
             '<button type="button" onclick="window.print()">인쇄</button>' + (f'<a href="{BASE}feed.xml">RSS</a>' if not (B.NOURL or B.DEMO) else '') + '</div>')
    return (f'<article class="art">{ex}{wide}<span class="lb">확인 노트 · {E(cat_of(n))}</span><h1>{E(n["title"])}</h1><p class="dek">{E(n["question"])}</p>'
            f'<div class="vband {V[v]}"><b>{E(v)}</b><span>{E(VDESC.get(v, ""))}</span></div>'
            f'<div class="by"><span>{E(n["date"])}</span><span>확인 시각 {E(n["checked_at"])}</span></div>'
            + (f'<div class="nbox"><span>핵심 숫자</span><b style="color:{COLR.get(v, "#111")}">{E(num)}</b><em>{E(n["question"])}</em></div>' if num else '')
            + f'<p class="sum">{E(n["summary"])}</p>'
            + (f'<h2>확인한 사실과 출처</h2><ul class="srcs">{facts}</ul>' if facts else '')
            + (f'<h2>매체마다 다르게 전한 점</h2><ul>{li(n["differs"])}</ul>' if n.get('differs') else '')
            + (f'<h2>아직 확인 안 된 것</h2><div class="unc"><ul>{li(n["unconfirmed"])}</ul></div>' if n.get('unconfirmed') else '')
            + (f'<h2>관련 기사</h2><ul class="rp">{reports}</ul>' if reports else '') + extra_html + relh + share + '</article>')


# ---------------------------------------------------------------- 8 푸터·믿을 근거 / 9 아래 고정 메뉴 (완성된 쪽 HTML 을 한 번 손본다)
def post(B, doc, items, path):
    act = B.POLISH; BASE = B.BASE; name = E(B.S['name'])
    if 8 in act:
        links = ''.join(f'<a href="{u}">{E(n)}</a>' for n, u in items[:6])
        legal = (f'<a href="{BASE}about/">소개</a><a href="{BASE}contact/">문의</a><a href="{BASE}privacy/">개인정보 처리방침</a>' + (f'<a href="{BASE}disclosure/">광고·제휴 고지</a>' if B.part('monetize', False) else '')
                 + (f'<a href="{BASE}how/">확인하는 방법</a>' if B.part('info') else '') + ('' if (B.NOURL or B.DEMO) else f'<a href="{BASE}feed.xml">RSS</a>'))
        trust = ('<section class="trust"><div class="wrap"><div><b>공식 자료로만 판정합니다</b><p>정부·기관이 직접 낸 자료에서 숫자와 날짜를 찾아 맞춰 봅니다. 찾지 못한 것은 지어내지 않고 「아직 확인 안 됨」으로 둡니다.</p></div>'
                 '<div><b>출처를 눌러 확인합니다</b><p>확인한 사실마다 출처 링크와 확인 시각을 붙입니다. 기사 본문은 옮기지 않고 제목·매체·링크만 모읍니다.</p></div>'
                 '<div><b>틀리면 고칩니다</b><p>정정 요청은 문의 쪽으로 받습니다. 고친 내용은 노트에 적고, 판정이 바뀌면 그 사실을 알립니다.</p></div></div></section>') if B.part('info') else ''
        foot = (f'{trust}<footer class="ft"><div class="wrap"><div class="ft-grid"><div><b>{name}</b><p>{E(B.S.get("about") or B.S["tagline"])}</p></div><div><b>둘러보기</b>{links}</div><div><b>알림</b>{legal}</div></div>'
                f'<p class="ft-c">{"기사 본문은 싣지 않고 제목·매체·시각·링크만 모아 보여 줍니다. 기사의 저작권은 각 매체에 있습니다. " if B.part("info") else ""}© {name}</p></div></footer>')
        doc = re.sub(r'<footer>.*?</footer>', lambda m: foot, doc, count=1, flags=re.S)
    if 9 in act:
        it = items[:3]
        icons = ['⌂', '☰', '⌕']
        cells = ''.join(f'<a href="{u}" class="{"on" if (u == BASE and not path) else ""}"><b>{icons[i]}</b>{E(n)}</a>' for i, (n, u) in enumerate(it))
        M = (B.S.get('monetize') or {}); nl = (M.get('newsletter') or {}).get('url')
        sub = nl or (BASE + 'feed.xml' if not (B.NOURL or B.DEMO) else BASE + 'contact/')
        cells += f'<a href="{E(sub)}" class="{"cta" if act[9] == "B" else ""}"><b>✉</b>소식 받기</a>'
        doc = doc.replace('</body>', f'<nav class="bnav" aria-label="아래 메뉴">{cells}</nav></body>', 1)
    return doc
