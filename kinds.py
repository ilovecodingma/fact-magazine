# -*- coding: utf-8 -*-
"""변환한 서비스 종류별 첫 화면 구획(요리법 모음·가게 홈페이지). 기능 이름 목록이 아니라 그 종류의 말로 된 첫 화면을 만든다. 파이썬 기본 기능만 쓴다.
site.local.json 의 "kind" 가 이 파일의 HOMES 에 있으면 build.py 가 첫 화면에 home_body() 를 쓴다. 그림(SVG)은 자료마다 자동으로 만든다."""
import datetime, hashlib, html, json, os, re

E = html.escape

# 변환 설정: demo=예시 자료(demos/<key>/kits)와 예시 이름·소개를 빌려 온다, parts=켜는 기능, labels=메뉴 이름
CFG = {
    '요리법 모음': dict(demo='recipes', parts=['recipes', 'search', 'prefs', 'monetize'], labels={'recipes': '오늘 뭐 먹지', 'search': '재료로 찾기'}, home='recipes', theme_accent='#e4572e'),
    '가게 홈페이지': dict(demo='shop', parts=['compare', 'wiki', 'faq', 'search', 'prefs'], labels={'compare': '메뉴', 'wiki': '영업 시간', 'faq': '오는 길·질문'}, home='shop', theme_accent='#b5532a'),
}
HOMES = {'recipes', 'shop'}

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


CSS = (".kd-s{font-size:14px;color:var(--mu,#555)}.kd{--k:var(--pri,var(--ac,#e4572e))}.kd .kd-hero{display:grid;grid-template-columns:minmax(0,45fr) minmax(0,55fr);gap:26px;align-items:center;padding:24px 0 6px}\n"
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
