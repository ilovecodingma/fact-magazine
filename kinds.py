# -*- coding: utf-8 -*-
"""변환한 서비스 종류별 첫 화면 구획(요리법 모음·가게 홈페이지). 기능 이름 목록이 아니라 그 종류의 말로 된 첫 화면을 만든다. 파이썬 기본 기능만 쓴다.
site.local.json 의 "kind" 가 이 파일의 HOMES 에 있으면 build.py 가 첫 화면에 home_body() 를 쓴다. 그림(SVG)은 자료마다 자동으로 만든다."""
import datetime, hashlib, html, json, os, re

E = html.escape

# 변환 설정: demo=예시 자료(demos/<key>/kits)와 예시 이름·소개를 빌려 온다, parts=켜는 기능, labels=메뉴 이름
CFG = {
    '요리법 모음': dict(demo='recipes', parts=['recipes', 'search', 'prefs', 'monetize'], labels={'recipes': '오늘 뭐 먹지', 'search': '재료로 찾기'}, home='recipes', theme_accent='#e4572e'),
    '도구 모음': dict(demo='tools', parts=['calc', 'glossary', 'compare', 'search', 'prefs', 'monetize'], labels={'compare': '요금제 비교'}, home='tools', theme_accent='#2f6fed'),
    '가계부 앱': dict(demo='ledger', parts=['ledger', 'calc', 'dday', 'prefs', 'pwa', 'monetize'], labels={'ledger': '가계부'}, home='ledger', theme_accent='#0ea5e9'),
    '게임 놀이터': dict(demo='games', parts=['games', 'quiz', 'search', 'prefs'], labels={'quiz': '상식 퀴즈'}, home='games', theme_accent='#ff4f8b'),
    '커뮤니티(링크+추천 게시판)': dict(demo='', parts=['board', 'backend', 'contact', 'search', 'prefs'], labels={'board': '게시판'}, home='board', theme_accent='#c2410c'),
    '쇼핑몰(디지털 상품 장터)': dict(demo='', parts=['market', 'backend', 'contact', 'search', 'prefs'], labels={'market': '장터'}, home='market', theme_accent='#ff90e8'),
    '가게 홈페이지': dict(demo='shop', parts=['compare', 'wiki', 'faq', 'search', 'prefs'], labels={'compare': '메뉴', 'wiki': '영업 시간', 'faq': '오는 길·질문'}, home='shop', theme_accent='#b5532a'),
}
HOMES = {'recipes', 'shop', 'tools', 'ledger', 'games', 'board', 'market'}

PAL = [('#fde8d8', '#e4572e'), ('#e3f1e7', '#1c7a46'), ('#fff1c9', '#b7791f'), ('#e4ecfb', '#2f5bd0'), ('#f9e0ea', '#c02669'), ('#e7e2f7', '#5b3fc2')]


def _h(s, n):
    return int(hashlib.md5(s.encode()).hexdigest()[:4], 16) % n


def slug(n):
    return re.sub(r'\s+', '-', n.strip())


def _kind_of(name):
    if re.search(r'국|탕|찌개|전골', name):
        return 'soup'
    if re.search(r'전|부침|튀김', name):
        return 'pan'
    if re.search(r'밥|덮밥|죽|비빔', name):
        return 'rice'
    return 'plate'


def recipe_svg(r, w=600, h=400):
    bg, col = PAL[_h(r['name'], len(PAL))]; k = _kind_of(r['name']); cx = w / 2; cy = h * 0.55; R = h * 0.26
    if k == 'soup':
        body = (f'<ellipse cx="{cx}" cy="{cy + R * .35}" rx="{R * 1.5}" ry="{R * .35}" fill="{col}" opacity=".25"/><path d="M{cx - R * 1.4} {cy - R * .1}h{R * 2.8}a{R * 1.4} {R * 1.2} 0 0 1 -{R * 2.8} 0z" fill="{col}"/>'
                f'<path d="M{cx - R * .5} {cy - R * .55}q-{R * .25} -{R * .35} 0 -{R * .7}M{cx + R * .2} {cy - R * .55}q-{R * .25} -{R * .35} 0 -{R * .7}" fill="none" stroke="{col}" stroke-width="{R * .1}" stroke-linecap="round" opacity=".6"/>')
    elif k == 'pan':
        body = f'<circle cx="{cx}" cy="{cy}" r="{R * 1.25}" fill="{col}"/><circle cx="{cx}" cy="{cy}" r="{R * .95}" fill="{bg}" opacity=".55"/><circle cx="{cx - R * .3}" cy="{cy - R * .2}" r="{R * .18}" fill="{col}"/><circle cx="{cx + R * .35}" cy="{cy + R * .15}" r="{R * .22}" fill="{col}"/>'
    elif k == 'rice':
        body = f'<path d="M{cx - R * 1.3} {cy}h{R * 2.6}a{R * 1.3} {R * 1.1} 0 0 1 -{R * 2.6} 0z" fill="{col}"/><path d="M{cx - R * .9} {cy}a{R * .9} {R * .8} 0 0 1 {R * 1.8} 0z" fill="#fff" opacity=".9"/>'
    else:
        body = f'<circle cx="{cx}" cy="{cy}" r="{R * 1.3}" fill="#fff" stroke="{col}" stroke-width="{R * .12}"/><circle cx="{cx}" cy="{cy}" r="{R * .8}" fill="{col}" opacity=".85"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="\'Noto Serif KR\',\'Nanum Myeongjo\',Batang,serif"><rect width="{w}" height="{h}" fill="{bg}"/>'
            f'<circle cx="{w * .86}" cy="{h * .18}" r="{h * .12}" fill="{col}" opacity=".15"/><circle cx="{w * .1}" cy="{h * .85}" r="{h * .09}" fill="{col}" opacity=".15"/>{body}'
            f'<text x="{w * .05}" y="{h * .14}" font-size="{int(h * .075)}" font-weight="800" fill="{col}" font-family="system-ui,Malgun Gothic,sans-serif">집밥</text></svg>')


def recipe_img(B, r, cls='kd-img', kind='card'):
    w, h = (600, 400) if kind == 'card' else (1200, 400)
    name = f'recipe_{slug(r["name"])}{"" if kind == "card" else "_w"}.svg'
    p = os.path.join(B.OUT, 'img'); os.makedirs(p, exist_ok=True)
    open(os.path.join(p, name), 'w', encoding='utf-8').write(recipe_svg(r, w, h))
    return f'<img class="{cls}" src="{B.BASE}img/{E(name)}" width="{w}" height="{h}" alt="{E(r["name"])} 대표 그림(도형)" loading="lazy">'


CSS = (".embed .mast,.embed nav.menu,.embed footer,.embed .bnav,.embed .mon,.embed .notice,.embed .ft,.embed .trust{display:none!important}.embed body,.embed main.wrap{padding:0;margin:0;background:#fff}.embed .art,.embed .page{margin:0;border:0;border-radius:0;padding:14px 16px}\n"
       ".kd .kd-tool{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:26px;align-items:start;padding:24px 0 6px}.kd .kd-frame{width:100%;height:520px;border:1px solid var(--hair,#e5e5e5);border-radius:12px;background:#fff}\n"
       ".kd .kd-chips a{display:inline-block;margin:0 8px 8px 0;padding:8px 12px;border:1px solid var(--k);border-radius:999px;color:var(--k);font:700 14px/1 var(--sans,system-ui)}.kd .kd-chips a:hover{background:var(--k);color:#fff;text-decoration:none}\n"
       ".kd .kd-sum{background:linear-gradient(135deg,var(--k),color-mix(in srgb,var(--k) 55%,#000));color:#fff;border-radius:14px;padding:26px 28px;margin:22px 0 14px}.kd .kd-sum small{display:block;font:700 14px/1 var(--sans,system-ui);opacity:.9}.kd .kd-sum b{display:block;font:900 44px/1.2 var(--sans,system-ui);margin:8px 0 2px}.kd .kd-sum span{font:15px/1.5 var(--sans,system-ui);opacity:.95}\n"
       ".kd .kd-quick{display:grid;grid-template-columns:1fr 1fr 2fr auto;gap:8px;background:#fff;border:1px solid var(--hair,#e5e5e5);border-radius:12px;padding:12px}.kd .kd-quick input,.kd .kd-quick select{font:16px var(--sans,system-ui);padding:10px;border:1px solid var(--hair,#ccc);border-radius:6px;width:100%}.kd .kd-quick button{font:700 15px var(--sans,system-ui);background:var(--k);color:#fff;border:0;border-radius:6px;padding:0 18px;cursor:pointer;width:auto}\n"
       ".kd .kd-game{display:block;border-radius:16px;overflow:hidden;background:#fff;border:2px solid var(--k)}.kd .kd-game:hover{text-decoration:none;box-shadow:0 6px 18px rgba(0,0,0,.12)}.kd .kd-gb{padding:12px 16px 16px}.kd .kd-gb b{display:block;font:800 20px/1.3 var(--sans,system-ui)}.kd .kd-gb span{font:14px/1.5 var(--sans,system-ui);color:var(--mu,#555)}\n"
       ".kd .kd-quiz{background:#fff;border:2px dashed var(--k);border-radius:14px;padding:16px 18px}.kd .kd-quiz button{display:block;width:100%;text-align:left;margin:6px 0;padding:11px 14px;border:1px solid var(--hair,#ccc);border-radius:8px;background:#fff;font:16px var(--sans,system-ui);cursor:pointer}.kd .kd-quiz button.ok{border-color:#0b5d2f;background:#e4f1e8}.kd .kd-quiz button.no{border-color:#a11a12;background:#f6d9d5}\n"
       "@media(max-width:760px){.kd .kd-tool{grid-template-columns:1fr}.kd .kd-tool>div{order:-1}.kd .kd-quick{grid-template-columns:1fr 1fr}.kd .kd-sum b{font-size:34px}}\n"
       ".kd-s{font-size:14px;color:var(--mu,#555)}.kd{--k:var(--pri,var(--ac,#e4572e))}.kd .kd-hero{display:grid;grid-template-columns:minmax(0,45fr) minmax(0,55fr);gap:26px;align-items:center;padding:24px 0 6px}\n"
       ".kd-img{display:block;width:100%;height:auto;border-radius:12px;border:1px solid var(--hair,#e5e5e5);background:#f3f3f3}.kd .kd-hero h2{font:800 32px/1.3 var(--sans,system-ui);margin:6px 0 10px;border:0;padding:0}\n"
       ".kd .kd-hero p{font:17px/1.7 var(--sans,system-ui);color:var(--mu,#555);margin:0 0 12px}.kd .kd-btn{display:inline-block;background:var(--k);color:#fff;padding:11px 18px;border-radius:6px;font:700 15px/1 var(--sans,system-ui)}.kd .kd-btn:hover{text-decoration:none;opacity:.9}\n"
       ".kd .kd-chip{display:inline-block;font:700 13px/1 var(--sans,system-ui);border:1px solid var(--k);color:var(--k);padding:4px 8px;border-radius:999px;margin-right:6px}\n"
       ".kd .kd-find{margin:22px 0 8px}.kd .kd-find input{font:18px var(--sans,system-ui);padding:14px 16px;width:100%;border:2px solid var(--k);border-radius:10px;background:#fff}\n"
       ".kd .kd-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}.kd .kd-card{border:1px solid var(--hair,#e5e5e5);border-radius:10px;overflow:hidden;background:#fff}.kd .kd-card a{display:block;height:100%}.kd .kd-card a:hover{text-decoration:none}.kd .kd-card a:hover b{text-decoration:underline}\n"
       ".kd .kd-cb{padding:10px 12px 14px}.kd .kd-cb b{display:block;font:700 16px/1.4 var(--sans,system-ui);margin:0 0 4px}.kd .kd-cb span{font:13px/1.4 var(--sans,system-ui);color:var(--mu,#555)}\n"
       ".kd h2.kd-h{font:800 18px/1.4 var(--sans,system-ui);margin:30px 0 12px;color:var(--k);border-left:5px solid var(--k);padding-left:10px}\n"
       ".kd .kd-banner{background:linear-gradient(135deg,var(--k),color-mix(in srgb,var(--k) 55%,#000));color:#fff;border-radius:14px;padding:34px 30px;margin:22px 0 4px}.kd .kd-banner h2{font:900 40px/1.2 'Noto Serif KR',serif;margin:0 0 8px;color:#fff;border:0;padding:0}.kd .kd-banner p{margin:0 0 14px;font:18px/1.6 var(--sans,system-ui);opacity:.95}\n"
       ".kd .kd-open{display:inline-block;background:#fff;color:var(--k);font:800 15px/1 var(--sans,system-ui);padding:9px 14px;border-radius:999px;margin-right:8px}.kd .kd-banner .kd-btn{background:#fff;color:var(--k)}\n"
       ".kd .kd-menu{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.kd .kd-item{display:flex;gap:12px;background:#fff;border:1px solid var(--hair,#e5e5e5);border-radius:10px;padding:10px;align-items:center}.kd .kd-item img{width:84px;height:56px;border-radius:8px;flex:none;object-fit:cover}.kd .kd-item b{display:block;font:700 16px/1.3 var(--sans,system-ui)}.kd .kd-item span{display:block;font:13px/1.4 var(--sans,system-ui);color:var(--mu,#555)}.kd .kd-item em{font:normal 800 15px var(--sans,system-ui);color:var(--k);margin-left:auto;white-space:nowrap}\n"
       ".kd .kd-info{display:grid;grid-template-columns:1fr 1fr;gap:16px}.kd .kd-box{background:#fff;border:1px solid var(--hair,#e5e5e5);border-radius:10px;padding:14px 16px}.kd .kd-box h3{font:800 16px/1.4 var(--sans,system-ui);margin:0 0 6px;color:var(--k)}.kd .kd-box p,.kd .kd-box li{font:15px/1.7 var(--sans,system-ui);margin:0}.kd .kd-box ul{margin:0;padding-left:18px}\n"
       "@media(max-width:1000px){.kd .kd-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.kd .kd-menu{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:760px){.kd .kd-hero,.kd .kd-info{grid-template-columns:1fr}.kd .kd-hero h2{font-size:25px}.kd .kd-banner h2{font-size:30px}}@media(max-width:560px){.kd .kd-grid,.kd .kd-menu{grid-template-columns:1fr 1fr}}\n")


def home_body(B, kind):
    cfg = CFG.get(kind) or {}
    if cfg.get('home') == 'recipes':
        return _recipes_home(B)
    if cfg.get('home') == 'shop':
        return _shop_home(B)
    if cfg.get('home') == 'market':
        import market as MK
        return MK.home_body(B)
    if cfg.get('home') == 'board':
        import board as BD
        return BD.home_body(B)
    if cfg.get('home') == 'tools':
        return _tools_home(B)
    if cfg.get('home') == 'ledger':
        return _ledger_home(B)
    if cfg.get('home') == 'games':
        return _games_home(B)
    return ''


def _recipes_home(B):
    R = B.kit_data('recipes', 'recipes.json') or []
    if not R:
        return '<div class="page"><p>요리법 자료(kits/recipes/data/recipes.json)가 아직 없습니다.</p></div>'
    today = datetime.date.today(); pick = R[(today.year * 372 + today.month * 31 + today.day) % len(R)]
    mins = lambda r: f'약 {5 * len(r["steps"]) + 5}분'
    hero = (f'<section class="kd-hero"><a href="{B.BASE}recipes/{E(slug(pick["name"]))}/" tabindex="-1">{recipe_img(B, pick)}</a><div><span class="kd-chip">오늘의 추천</span><h2><a href="{B.BASE}recipes/{E(slug(pick["name"]))}/">{E(pick["name"])}</a></h2>'
            f'<p>재료 {len(pick["ingredients"])}가지 · {len(pick["steps"])}단계 · {mins(pick)} · 2인분 <span class="kd-s">(시간·인분은 예시)</span></p><p>{E(", ".join(i.split()[0] for i in pick["ingredients"][:5]))} …</p><a class="kd-btn" href="{B.BASE}recipes/{E(slug(pick["name"]))}/">만드는 법 보기 →</a></div></section>')
    find = '<div class="kd-find"><input id="kdq" type="search" placeholder="냉장고에 있는 재료로 찾기 (예: 두부, 감자)" aria-label="재료로 요리 찾기"></div>'
    cards = ''.join(f'<article class="kd-card" data-t="{E((r["name"] + " " + " ".join(r["ingredients"])).lower())}"><a href="{B.BASE}recipes/{E(slug(r["name"]))}/">{recipe_img(B, r)}<div class="kd-cb"><b>{E(r["name"])}</b><span>{mins(r)} · 재료 {len(r["ingredients"])} · {len(r["steps"])}단계</span></div></a></article>' for r in R[:16])
    js = ('<script>(function(){var q=document.getElementById("kdq");if(!q)return;q.addEventListener("input",function(){var v=q.value.trim().toLowerCase();document.querySelectorAll(".kd-card").forEach(function(c){c.style.display=!v||c.dataset.t.indexOf(v)>=0?"":"none"})})})()</script>')
    more = f'<p><a class="kd-btn" href="{B.BASE}recipes/">요리법 {len(R)}가지 모두 보기 →</a></p>'
    return f'<div class="kd">{hero}{find}<h2 class="kd-h">오늘 뭐 먹지 — 요리 카드</h2><div class="kd-grid">{cards}</div>{more}</div>{js}'


def _shop_home(B):
    S = B.S; menu = B.kit_data('compare', 'table.json') or {}
    rows = menu.get('rows') or []
    hours = ''
    wd = os.path.join(B.KITS_DIR, 'wiki', 'data', '영업 시간.md')
    if os.path.exists(wd):
        hours = [ln[2:].strip() for ln in open(wd, encoding='utf-8').read().splitlines() if ln.startswith('- ')]
    today = '월화수목금토일'[datetime.date.today().weekday()]
    open_line = (hours[0] if hours else '영업 시간은 영업 시간 쪽에서 확인하세요')
    banner = (f'<section class="kd-banner"><h2>{E(S["name"])}</h2><p>{E(S["tagline"])}</p><span class="kd-open">오늘({today}) · {E(open_line)}</span> <a class="kd-btn kd-open" href="{B.BASE}compare/">메뉴 보기</a></section>')
    items = ''
    for i, r in enumerate(rows[:9]):
        nm = str(r[0]); bg, col = PAL[_h(nm, len(PAL))]
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 168 112"><rect width="168" height="112" fill="{bg}"/><ellipse cx="84" cy="62" rx="52" ry="30" fill="{col}"/><ellipse cx="84" cy="52" rx="44" ry="24" fill="{col}" opacity=".7"/><path d="M60 40q24 -22 48 0" fill="none" stroke="#fff" stroke-width="4" opacity=".6"/></svg>'
        fn = f'menu_{i}.svg'; p = os.path.join(B.OUT, 'img'); os.makedirs(p, exist_ok=True); open(os.path.join(p, fn), 'w', encoding='utf-8').write(svg)
        items += f'<div class="kd-item"><img src="{B.BASE}img/{fn}" alt="" width="168" height="112" loading="lazy"><div><b>{E(nm)}</b><span>{E(str(r[1])[:30])}</span></div><em>{E(str(r[2]))}</em></div>'
    menu_h = f'<h2 class="kd-h">오늘의 빵 메뉴</h2><div class="kd-menu">{items}</div><p><a class="kd-btn" href="{B.BASE}compare/">메뉴 전체 보기 →</a></p>' if items else ''
    faq = B.kit_data('faq', 'faq.json') or []
    faq_li = ''.join(f'<li><b>{E(x["q"])}</b><br>{E(x["a"])}</li>' for x in faq[:3])
    hours_li = ''.join(f'<li>{E(h)}</li>' for h in (hours or [])[:5])
    info = (f'<h2 class="kd-h">가게 정보</h2><div class="kd-info"><div class="kd-box"><h3>영업 시간</h3><ul>{hours_li or "<li>영업 시간 쪽에서 확인하세요</li>"}</ul><p style="margin-top:8px"><span class="kd-s">(가상 가게 — 시간·가격은 예시)</span></p></div>'
            f'<div class="kd-box"><h3>자주 묻는 것</h3><ul>{faq_li or "<li>자료를 넣으면 여기에 나옵니다</li>"}</ul></div></div>')
    return f'<div class="kd">{banner}{menu_h}{info}</div>'


def _icon(kind, col, bg, w=600, h=300):
    import polish as P
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="{bg}"/><circle cx="{w * .88}" cy="{h * .18}" r="{h * .12}" fill="{col}" opacity=".15"/>'
            + P.icon_svg(kind, col, w / 2 - h * 0.26, h * 0.16, h * 0.52) + '</svg>')


def _img(B, name, svg, cls='kd-img', w=600, h=300):
    p = os.path.join(B.OUT, 'img'); os.makedirs(p, exist_ok=True)
    open(os.path.join(p, name), 'w', encoding='utf-8').write(svg)
    return f'<img class="{cls}" src="{B.BASE}img/{E(name)}" width="{w}" height="{h}" alt="" loading="lazy" style="max-width:100%;height:auto">'


def _calc_kind(c):
    t = c.get('title', '') + c.get('desc', '')
    return 'coin' if re.search(r'원|금|저축|이자|비용|요금|돈', t) else ('bars' if re.search(r'평균|점수|통계', t) else 'doc')


def _tools_home(B):
    C = B.kit_data('calc', 'calculators.json') or []
    if not C:
        return '<div class="page"><p>계산기 자료(kits/calc/data/calculators.json)가 아직 없습니다.</p></div>'
    c0 = C[0]
    hero = (f'<section class="kd-tool"><iframe class="kd-frame" title="{E(c0["title"])}" src="{B.BASE}calc/{E(c0["slug"])}/?embed=1" loading="lazy"></iframe>'
            f'<div>{_img(B, "calc_hero.svg", _icon(_calc_kind(c0), "#1e3a8a", "#e8eefb", 600, 200), "kd-img", 600, 200)}<span class="kd-chip" style="margin-top:12px">바로 계산해 보세요</span><h2 style="font:800 30px/1.3 var(--sans,system-ui);margin:8px 0 8px;border:0;padding:0">{E(c0["title"])}</h2><p style="font:17px/1.7 var(--sans,system-ui);color:var(--mu,#555)">{E(c0["desc"])}</p>'
            f'<div class="kd-chips">' + ''.join(f'<a href="{B.BASE}calc/{E(c["slug"])}/">{E(c["title"])}</a>' for c in C[1:6]) + f'</div><a class="kd-btn" href="{B.BASE}calc/{E(c0["slug"])}/">크게 열어서 계산하기 →</a></div></section>')
    cards = ''.join(f'<article class="kd-card"><a href="{B.BASE}calc/{E(c["slug"])}/">{_img(B, f"calc_{i}.svg", _icon(_calc_kind(c), "#1e3a8a", "#e8eefb"))}<div class="kd-cb"><b>{E(c["title"])}</b><span>{E(c["desc"][:44])}</span></div></a></article>' for i, c in enumerate(C[:8]))
    terms = (B.kit_data('glossary', 'terms.json') or [])[:8]
    gl = ''.join(f'<a href="{B.BASE}glossary/{E(re.sub(chr(32), chr(45), t["term"]))}/">{E(t["term"])}</a>' for t in terms)
    gh = f'<h2 class="kd-h">알아 두면 좋은 용어</h2><div class="kd-chips">{gl}</div>' if gl else ''
    return f'<div class="kd">{hero}<h2 class="kd-h">계산기 모음</h2><div class="kd-grid">{cards}</div>{gh}</div>'


def _ledger_home(B):
    D = B.kit_data('dday', 'dates.json') or []; C = B.kit_data('calc', 'calculators.json') or []
    today = datetime.date.today()
    dd = ''
    for x in sorted(D, key=lambda x: x['date'])[:4]:
        try:
            n = (datetime.date.fromisoformat(x['date']) - today).days
        except Exception:
            continue
        dd += f'<div class="kd-box"><h3>{E(x["title"])}</h3><p>{x["date"]} · ' + (f'D-{n}' if n > 0 else ('오늘' if n == 0 else f'{-n}일 지남')) + '</p></div>'
    cats = ['식비', '교통', '생활', '여가', '기타']
    form = ('<form class="kd-quick" id="kdq2"><input id="kda" type="number" inputmode="numeric" min="1" placeholder="금액(원)" aria-label="금액" required><select id="kdc" aria-label="분류">' + ''.join(f'<option>{c}</option>' for c in cats)
            + '</select><input id="kdm" maxlength="40" placeholder="메모(예: 점심)" aria-label="메모"><button type="submit">적기</button></form>')
    js = ('<script>(function(){var K="fm_ledger";function get(){try{return JSON.parse(localStorage.getItem(K)||"[]")}catch(e){return[]}}function mon(){var m=new Date().toISOString().slice(0,7),s=0;get().forEach(function(r){if(String(r.d).slice(0,7)===m)s+=+r.a||0});return s}'
          'function draw(){document.getElementById("kdsum").textContent=mon().toLocaleString("ko-KR")+"원"}draw();'
          'document.getElementById("kdq2").onsubmit=function(e){e.preventDefault();var a=parseFloat(document.getElementById("kda").value);if(!a)return;var R=get();R.push({d:new Date().toISOString().slice(0,10),c:document.getElementById("kdc").value,m:document.getElementById("kdm").value,a:a});try{localStorage.setItem(K,JSON.stringify(R))}catch(x){}document.getElementById("kda").value="";document.getElementById("kdm").value="";draw()}})()</script>')
    band = (f'<section class="kd-sum"><span style="float:right;width:92px">{_img(B, "wallet.svg", _icon("coin", "#ffffff", "transparent", 300, 300), "", 300, 300)}</span><small>이번 달 쓴 돈(이 기기에만 저장)</small><b id="kdsum">0원</b><span>아래 칸에 바로 적으면 합계가 올라갑니다. 전체 목록·CSV 내보내기는 <a href="{B.BASE}ledger/" style="color:#fff;text-decoration:underline">가계부</a>에서.</span></section>')
    app = (f'<h2 class="kd-h">홈 화면에 올리기</h2><div class="kd-box"><p>이 사이트는 앱처럼 설치할 수 있습니다. 인터넷이 없어도 열리고, 적은 내용은 이 기기에만 남습니다. <a class="kd-btn" style="margin-left:10px" href="{B.BASE}app/">설치하는 법 보기 →</a></p></div>') if B.part('pwa', False) else ''
    cc = ''.join(f'<article class="kd-card"><a href="{B.BASE}calc/{E(c["slug"])}/">{_img(B, f"calc_{i}.svg", _icon(_calc_kind(c), "#0369a1", "#e0f2fe"))}<div class="kd-cb"><b>{E(c["title"])}</b><span>{E(c["desc"][:44])}</span></div></a></article>' for i, c in enumerate(C[:4]))
    return f'<div class="kd">{band}{form}{("<h2 class=kd-h>기다리는 날</h2><div class=kd-info>" + dd + "</div>") if dd else ""}<h2 class="kd-h">계산기</h2><div class="kd-grid">{cc}</div>{app}</div>{js}'


def _games_home(B):
    G = B.load_games(); Q = (B.kit_data('quiz', 'quiz.json') or {}).get('questions') or []
    pal = [('#ffe4ec', '#e11d63'), ('#e5e0ff', '#5b3fc2'), ('#d8f5ee', '#0f766e'), ('#fff1c9', '#b7791f')]
    cards = ''
    for i, g in enumerate(G):
        bg, col = pal[i % len(pal)]
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 300"><rect width="600" height="300" fill="{bg}"/><circle cx="470" cy="80" r="70" fill="{col}" opacity=".18"/><circle cx="110" cy="230" r="50" fill="{col}" opacity=".18"/>'
               f'<rect x="215" y="95" width="170" height="110" rx="34" fill="{col}"/><circle cx="260" cy="150" r="20" fill="#fff"/><rect x="250" y="146" width="20" height="8" rx="3" fill="{col}"/><rect x="256" y="140" width="8" height="20" rx="3" fill="{col}"/><circle cx="335" cy="140" r="9" fill="#fff"/><circle cx="360" cy="162" r="9" fill="#fff"/></svg>')
        cards += f'<a class="kd-game" href="{B.BASE}games/{E(g["slug"])}/">{_img(B, f"game_{i}.svg", svg)}<div class="kd-gb"><b>{E(g["title"])}</b><span>{E(g.get("kind", "게임"))} · {E(g.get("desc", "")[:40])}…</span></div></a>'
    quiz = ''
    if Q:
        qd = Q[(datetime.date.today().toordinal()) % len(Q)]
        opts = ''.join(f'<button type="button" data-i="{i}">{E(o)}</button>' for i, o in enumerate(qd['options']))
        quiz = (f'<h2 class="kd-h">오늘의 퀴즈</h2><div class="kd-quiz" id="kdz"><b>{E(qd["q"])}</b>{opts}<p id="kdex" style="margin:8px 0 0;font:15px/1.6 var(--sans,system-ui)"></p></div>'
                f'<script>(function(){{var A={int(qd["answer"])},E={json.dumps(qd.get("explain", ""), ensure_ascii=False)},bs=document.querySelectorAll("#kdz button");bs.forEach(function(b){{b.onclick=function(){{bs.forEach(function(x){{x.disabled=true}});bs[A].className="ok";if(+b.dataset.i!==A)b.className="no";document.getElementById("kdex").textContent=(+b.dataset.i===A?"정답! ":"아쉬워요. ")+E}}}})}})()</script>')
    return f'<div class="kd"><section class="kd-banner"><h2>{E(B.S["name"])}</h2><p>{E(B.S["tagline"])}</p></section><h2 class="kd-h">오늘 한 판</h2><div class="kd-grid" style="grid-template-columns:repeat(auto-fit,minmax(240px,1fr))">{cards}</div>{quiz}</div>'
