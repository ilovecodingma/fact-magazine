# -*- coding: utf-8 -*-
"""3단계 빌드: data/topics.json 과 notes/*.json 으로 docs/ (정적 화면)를 만든다.
첫 화면 · 확인 노트 쪽 · 고정 쪽(확인하는 방법·소개·문의·개인정보) · feed.xml · sitemap.xml.
「예시」 노트(example:true)는 화면 틀 시험용이라 --example 을 줄 때만 넣는다. 공개본에는 올리지 않는다.
실행: python build.py [--example]"""
import json, os, re, subprocess, sys, glob, html, shutil, datetime
import kitpages as _kp   # 2·3차 키트 쪽(자료 파일 → 쪽)
try:
    sys.stdout.reconfigure(encoding='utf-8')   # 윈도우에서 한글 출력이 깨지지 않게
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.environ['OUT_DIR']) if os.environ.get('OUT_DIR') else os.path.join(HERE, 'docs')   # OUT_DIR 로 다른 폴더에 만들 수 있다(내 값이 들어간 배포본은 저장소에 올리지 않는 dist/ 에)
S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
_local = os.path.join(HERE, 'site.local.json')   # 내 컴퓨터에서만 쓰는 값(저장소에 올리지 않음)이 있으면 덮어쓴다
if os.path.exists(_local):
    S.update(json.load(open(_local, encoding='utf-8')))
for _k, _env in (('base', 'SITE_BASE'), ('games_title', 'GAMES_TITLE'), ('games_desc', 'GAMES_DESC'), ('about', 'SITE_ABOUT'), ('url', 'SITE_URL'), ('name', 'SITE_NAME'), ('tagline', 'SITE_TAGLINE'), ('contact', 'SITE_CONTACT'), ('home_title', 'HOME_TITLE'), ('home_desc', 'HOME_DESC'), ('theme', 'SITE_THEME'), ('accent', 'SITE_ACCENT')):
    if os.environ.get(_env):   # 자동 갱신(GitHub Actions)에서는 저장소 변수가 환경변수로 들어와 site.json 값을 덮어쓴다
        S[_k] = os.environ[_env]
S['url'] = S['url'].rstrip('/')
if os.environ.get('SITE_LABELS'):
    try:
        S['labels'] = json.loads(os.environ['SITE_LABELS'])   # 메뉴·첫 화면 칸 이름 바꾸기(예: {"compare": "메뉴"})
    except Exception:
        pass
LAB = lambda k, d: (S.get('labels') or {}).get(k, d)
GENERIC = [('recipes', '요리법', 'recipes/', '오늘의 추천과 재료로 거르기'), ('quiz', '퀴즈', 'quiz/', '풀어 보는 퀴즈'), ('compare', '비교표', 'compare/', '정렬·거르기 되는 표'), ('wiki', '위키', 'wiki/', '서로 이어진 글'), ('gallery', '사진첩', 'gallery/', '그림 모음'), ('timeline', '타임라인', 'timeline/', '날짜순 기록')]
if os.environ.get('SITE_EXTRAS'):
    try:
        S['extras'] = json.loads(os.environ['SITE_EXTRAS'])
    except Exception:
        print('주의: SITE_EXTRAS 가 JSON 이 아니라 무시했습니다')
if os.environ.get('PARTS'):
    try:
        S['parts'] = json.loads(os.environ['PARTS'])
    except Exception:
        print('주의: PARTS 가 JSON 이 아니라 무시했습니다')
PARTS = S.get('parts') or {}


def part(name, default=True):
    """부품(info·games·issue·shorts·mail·inbox)이 켜져 있는지. site.json 의 parts 에 false 로 적으면 꺼진다."""
    return bool(PARTS.get(name, default))


EX = S.get('extras') or {}   # 쿠팡·유튜브·방송·블로그 값(내 값). 비어 있으면 그 칸은 화면에 안 나온다
KEYWORDS = [k.strip() for k in (os.environ.get('TOPIC_KEYWORDS') or ','.join(S.get('topic_keywords', []))).split(',') if k.strip()]   # 주제 키워드(런북 6절)
BASE, URL = S['base'], S['url']
NOURL = (not URL) or ('프로젝트이름' in URL) or ('내계정' in URL)   # 공개 주소가 아직 안 정해졌으면(기본값 그대로) canonical·RSS·사이트맵은 만들지 않는다
GAMES_SRC = os.path.join(HERE, 'games')   # 게임 원본 폴더(games/<이름>/meta.json + game.js). build.py 가 docs/games/ 로 복사한다 — docs/ 는 매번 지워지므로 원본은 여기에 둔다
E = html.escape
VERDICTS = {'확인됨': 'ok', '일부만 확인됨': 'part', '아직 확인 안 됨': 'no'}

CSS = """:root{--ink:#111;--mu:#595959;--hair:#d4d4d4;--bg:#fff;--ok:#0b5d2f;--part:#8a4b00;--no:#a11a12;--link:#0b3d91;
--serif:'Noto Serif KR','Noto Serif CJK KR','Nanum Myeongjo','Batang',serif;--sans:system-ui,'Malgun Gothic','Apple SD Gothic Neo',sans-serif}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:calc(17px*var(--fz,1))/1.7 var(--serif)}
a{color:inherit;text-decoration:none}a:hover{text-decoration:underline}.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
.dateline{font:13px/1 var(--sans);color:var(--mu);text-align:center;padding:12px 0 10px;border-bottom:1px solid var(--hair)}
.logo{display:block;text-align:center;font:900 46px/1.15 var(--serif);letter-spacing:-.02em;margin:14px 0 12px}.logo:hover{text-decoration:none}
.mast{border-bottom:3px double var(--ink)}
nav.menu{display:flex;justify-content:center;gap:26px;flex-wrap:wrap;font:600 14px/1 var(--sans);padding:12px 0;border-bottom:1px solid var(--ink)}
nav.menu a{color:var(--ink)}
.v{display:inline-block;font:700 12px/1 var(--sans);padding:3px 6px;border:1px solid currentColor;vertical-align:middle;white-space:nowrap}
.v.ok{color:var(--ok)}.v.part{color:var(--part)}.v.no{color:var(--no)}
.lb{font:700 12px/1 var(--sans);letter-spacing:.04em;color:var(--mu)}
.front{display:grid;grid-template-columns:2fr 1fr;gap:0 32px;padding:26px 0 8px}
.lead .lb{display:block;margin-bottom:10px}.lead h2{font:700 38px/1.28 var(--serif);margin:0 0 14px;letter-spacing:-.01em}
.lead p{font-size:18px;color:#333;margin:0 0 14px}.lead .meta,.side .meta{font:13px/1.4 var(--sans);color:var(--mu)}
.side{border-left:1px solid var(--hair);padding-left:28px}.side .it{padding:0 0 16px;margin:0 0 16px;border-bottom:1px solid var(--hair)}.side .it:last-child{border:0}
.side h3{font:700 20px/1.4 var(--serif);margin:6px 0 8px}
.sec{border-top:2px solid var(--ink);margin:28px 0 0;padding:10px 0 0}.sec h2{font:800 15px/1 var(--sans);letter-spacing:.06em;margin:0 0 4px}
.sec .sub{font:13px/1.5 var(--sans);color:var(--mu);margin:0 0 14px}
.cols{column-count:3;column-gap:32px;column-rule:1px solid var(--hair)}
.tp{break-inside:avoid;padding:0 0 16px;margin:0 0 16px;border-bottom:1px solid var(--hair)}
.tp b{display:block;font:700 17px/1.45 var(--serif);margin:4px 0 6px}.tp .lb{font-size:11.5px}
.tp .ln{display:block;font:13px/1.55 var(--sans);color:var(--mu)}.tp .ln a{color:var(--link)}
.empty{font:15px/1.6 var(--sans);color:var(--mu);padding:20px 0}
.art{max-width:680px;margin:0 auto;padding:30px 0 10px}.art .lb{display:block;margin-bottom:12px}
.art h1{font:800 36px/1.3 var(--serif);margin:0 0 14px;letter-spacing:-.015em}
.dek{font:19px/1.6 var(--serif);color:#444;margin:0 0 16px}
.by{font:13px/1.4 var(--sans);color:var(--mu);border-top:1px solid var(--hair);border-bottom:1px solid var(--hair);padding:10px 0;margin:0 0 20px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.art p.sum{font-size:18.5px;line-height:1.85;margin:0 0 8px}
.art h2{font:800 13px/1 var(--sans);letter-spacing:.06em;border-top:2px solid var(--ink);padding-top:10px;margin:32px 0 12px}
ol.fn{margin:0;padding-left:26px}ol.fn li{margin:0 0 14px;font-size:17px;line-height:1.75}ol.fn li::marker{font:700 13px var(--sans);color:var(--mu)}
.src{display:block;font:13px/1.5 var(--sans);color:var(--mu)}.src a{color:var(--link)}
.art ul{margin:0;padding-left:22px}.art li{margin:0 0 8px}.rp{font:14.5px/1.6 var(--sans)}.rp a{color:var(--link)}
.ex{display:inline-block;font:700 12px/1 var(--sans);background:#fff3cd;color:#664d03;padding:4px 8px;margin-bottom:10px}
.page{max-width:680px;margin:0 auto;padding:30px 0}.page h1{font:800 32px/1.3 var(--serif);margin:0 0 16px}.page ul{padding-left:22px}.page li{margin:0 0 10px}
footer{margin-top:40px;padding:16px 0 34px;border-top:3px double var(--ink);font:13px/1.7 var(--sans);color:var(--mu)}footer a{margin-right:14px;color:var(--ink)}
.gm{max-width:520px;margin:0 auto;padding:26px 0 10px}.gm h1{font:800 32px/1.3 var(--serif);margin:6px 0 10px}.gm .dek{margin-bottom:14px}
.gm canvas{display:block;width:100%;max-width:480px;height:auto;aspect-ratio:2/3;margin:0 auto;border:2px solid var(--ink);background:#f7f5ee;touch-action:none;user-select:none;-webkit-user-select:none}
.gm .how{font:14.5px/1.7 var(--sans);color:#333;margin:18px 0 0;padding-left:20px}.gm .note{font:12.5px/1.6 var(--sans);color:var(--mu);margin:10px 0 0}
.ex-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:0 32px}.ex-grid h3{font:800 18px/1.4 var(--serif);margin:14px 0 8px}.ex-grid ul{list-style:none;margin:0;padding:0;font:15px/1.7 var(--sans)}.ex-grid li{padding:6px 0;border-bottom:1px solid var(--hair)}.ex-grid a{color:var(--link)}
.ad-lb{display:inline-block;font:700 11px/1 var(--sans);border:1px solid var(--mu);color:var(--mu);padding:2px 5px;margin-left:6px;vertical-align:middle}.ad-nt{font:12.5px/1.6 var(--sans);color:var(--mu);margin:10px 0 0}
.yt-row{display:flex;gap:12px;flex-wrap:wrap}.yt-row iframe{width:162px;height:288px;border:0;background:#111}
.mdt{border-collapse:collapse;margin:12px 0;font:14.5px/1.6 var(--sans)}.mdt td{border:1px solid var(--hair);padding:6px 10px}.nv p{font-size:inherit;line-height:1.95;margin:0 0 1em}.fz{display:flex;gap:8px;justify-content:flex-end;margin:0 0 10px}.fz button{font:700 13px var(--sans);border:1px solid var(--ink);background:#fff;padding:4px 10px;cursor:pointer;margin:0;width:auto}
.calc label{display:block;font:700 14px var(--sans);margin:14px 0 4px}.calc input{font:18px var(--sans);padding:10px;width:100%;border:1px solid var(--ink);background:#fff}.crs{margin-top:18px;border-top:2px solid var(--ink)}.cr{display:flex;justify-content:space-between;gap:12px;padding:12px 0;border-bottom:1px solid var(--hair);font:16px var(--sans)}.cr b{font:800 22px var(--serif)}
.notice{font:14px/1.5 var(--sans);background:#fff8dc;border:1px solid #e6d9a0;padding:8px 12px;margin:14px 0 0}.notice a{color:var(--link);margin-left:8px}details.fq{border-top:1px solid var(--hair);padding:12px 0}details.fq summary{font:700 17px/1.5 var(--serif);cursor:pointer}details.fq p{font:15px/1.7 var(--sans);color:#333;margin:8px 0 0}pre{overflow-x:auto}
nav.menu{position:relative}details.mn{position:relative}details.mn summary{list-style:none;cursor:pointer;font:600 14px/1 var(--sans)}details.mn summary::-webkit-details-marker{display:none}.mnp{position:absolute;right:0;top:26px;background:#fff;border:1px solid var(--ink);padding:6px 14px;display:flex;flex-direction:column;gap:12px;z-index:20;min-width:140px;text-align:left}
@media(max-width:640px){nav.menu{gap:14px;flex-wrap:nowrap;justify-content:space-between}nav.menu a,details.mn summary{white-space:nowrap}}
:root[data-theme=dark]{--ink:#ececec;--bg:#15171a;--mu:#a8a8a8;--hair:#33363b;--link:#8ab0ff}:root[data-theme=dark] .mnp,:root[data-theme=dark] .calc input,:root[data-theme=dark] .lf input,:root[data-theme=dark] details.mn{background:#1d2024;color:#ececec}:root[data-theme=dark] .notice{background:#2a2614;color:#eee;border-color:#555}:root[data-theme=dark] .lead p,:root[data-theme=dark] .dek{color:#ccc}:root[data-theme=dark] .mdt td,:root[data-theme=dark] .mdt th{border-color:#444}
.prefs{font:13px/2 var(--sans);margin:8px 0 0}.prefs button{width:auto;margin:0 6px 0 0;padding:2px 10px;border:1px solid var(--mu);background:transparent;color:inherit;cursor:pointer;font:13px var(--sans)}
.gl{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:0 28px;margin-top:10px}.gl a{display:block;padding:14px 0 16px;border-bottom:1px solid var(--hair)}.gl a:hover{text-decoration:none}
.gl h3{font:800 22px/1.35 var(--serif);margin:6px 0 6px}.gl p{font:14px/1.65 var(--sans);color:#333;margin:0}
@media(max-width:900px){.cols{column-count:2}.lead h2{font-size:32px}}
@media(max-width:640px){.logo{font-size:34px}.front{grid-template-columns:1fr;padding-top:18px}.side{border-left:0;padding-left:0;border-top:1px solid var(--ink);padding-top:16px;margin-top:12px}
.lead h2{font-size:27px}.cols{column-count:1;column-rule:0}.art h1{font-size:28px}nav.menu{gap:18px}.wrap{padding:0 16px}}"""


import themes as _th
THEME = S.get('theme') if S.get('theme') in _th.NAMES else 'paper'   # 겉모습 틀: paper·card·shop·doc·play·one (themes.py)
ACCENT = S.get('accent') or _th.DEFAULT_ACCENT[THEME]
CSS += _th.CSS

WEEK = '월화수목금토일'


def today_ko():
    """머리 줄에 쓰는 오늘 날짜(한국시간)."""
    d = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    return f'{d.year}년 {d.month}월 {d.day}일 {WEEK[d.weekday()]}요일'


FOOT = {'topics': ('주제', 'topics/'), 'today': ('오늘의 추천', 'today/'), 'trends': ('인기 키워드', 'trends/'), 'widget': ('퍼가기', 'widget/'), 'notice': ('바뀐 내역', 'changes/'), 'timeline': ('타임라인', 'timeline/'), 'rank': ('화제 순위', 'rank/'),
        'wiki': ('위키', 'wiki/'), 'faq': ('자주 묻는 질문', 'faq/'), 'schedule': ('일정', 'schedule/'), 'quiz': ('퀴즈', 'quiz/'), 'compare': ('표 비교', 'compare/'), 'gallery': ('사진첩', 'gallery/'), 'links': ('링크 모음', 'links/')}


def page(path, title, desc, body, noindex=False):
    """HTML 쪽 하나를 docs/<path>/index.html 로 쓴다. 종합 일간지 첫 화면 같은 머리(제호·괘선·한 줄 메뉴)를 붙인다."""
    d = os.path.join(OUT, path)
    os.makedirs(d, exist_ok=True)
    explicit_noindex = noindex
    noindex = noindex or DEMO
    canon = f'{URL}/{path}/' if path else f'{URL}/'
    _logo = f'<a class="logo" href="{BASE}">{E(S["name"])}</a>'
    LOGO = f'<h1 style="margin:0">{_logo}</h1>' if not path else _logo   # 첫 화면에는 h1 이 하나 있어야 하므로 제호를 h1 로
    canon_tag = '' if (NOURL or DEMO) else f'<link rel="canonical" href="{canon}">'
    rss_tag = '' if (NOURL or DEMO) else f'<link rel="alternate" type="application/rss+xml" title="{E(S["name"])}" href="{BASE}feed.xml">'
    rss_link = '' if (NOURL or DEMO) else f'<a href="{BASE}feed.xml">RSS</a>'
    robots = '<meta name="robots" content="noindex">' if noindex else ''
    PREF_HEAD = '<script>try{var d=document.documentElement,t=localStorage.getItem("fm_theme"),z=localStorage.getItem("fm_fz");if(t)d.setAttribute("data-theme",t);if(z)d.style.setProperty("--fz",z)}catch(e){}</script>' if part('prefs', False) else ''
    PREFS_UI = ('<p class="prefs">보기 설정: <button type="button" data-fz="-0.1">글자 작게</button><button type="button" data-fz="0.1">글자 크게</button><button type="button" data-th="1">어두운 바탕 켜기/끄기</button></p><script>(function(){var d=document.documentElement;document.querySelectorAll(".prefs button").forEach(function(b){b.onclick=function(){try{if(b.dataset.th){var t=d.getAttribute("data-theme")==="dark"?"light":"dark";d.setAttribute("data-theme",t);localStorage.setItem("fm_theme",t)}else{var z=Math.max(.8,Math.min(1.5,(parseFloat(d.style.getPropertyValue("--fz"))||1)+parseFloat(b.dataset.fz)));d.style.setProperty("--fz",z);localStorage.setItem("fm_fz",z)}}catch(e){}}})})()</script>') if part('prefs', False) else ''
    PWA_HEAD = f'<link rel="manifest" href="{BASE}manifest.webmanifest"><meta name="theme-color" content="{E(ACCENT)}"><link rel="apple-touch-icon" href="{BASE}icon-192.png">' if part('pwa', False) else ''
    PWA_REG = f'<script>if("serviceWorker" in navigator){{navigator.serviceWorker.register("{BASE}sw.js",{{scope:"{BASE}"}}).catch(function(){{}})}}</script>' if part('pwa', False) else ''
    items = [('오늘' if part('info') else '처음', BASE)]   # 메뉴 후보(앞에서부터 보여 주고 5칸을 넘으면 「더 보기」에 접는다)
    if load_games():
        items.append(('게임', BASE + 'games/'))
    if part('issue'):
        items.append(('잡지', BASE + 'issue/'))
    if part('posts', False) and os.path.isdir(os.path.join(HERE, 'posts')):
        items.append(('글', BASE + 'post/'))
    if part('novel', False) and os.path.isdir(os.path.join(HERE, 'novels')):
        items.append(('연재', BASE + 'novel/'))
    if part('toon', False) and os.path.isdir(os.path.join(HERE, 'toons')):
        items.append(('웹툰', BASE + 'toon/'))
    if part('video', False) and EX.get('videos'):
        items.append(('영상', BASE + 'video/'))
    if part('calc', False) and kit_data('calc', 'calculators.json'):
        items.append(('계산기', BASE + 'calc/'))
    if part('glossary', False) and kit_data('glossary', 'terms.json'):
        items.append(('용어', BASE + 'glossary/'))
    if part('schedule', False) and kit_data('schedule', 'events.json'):
        items.append(('일정', BASE + 'schedule/'))
    if part('faq', False) and kit_data('faq', 'faq.json'):
        items.append(('질문', BASE + 'faq/'))
    if part('links', False) and kit_data('links', 'links.json'):
        items.append(('링크', BASE + 'links/'))
    for _k, _n, _u, _d in GENERIC:
        if part(_k, False) and not part('info'):   # 뉴스를 끈 사이트(조립 예시 등)에서는 켜진 키트 칸을 메뉴에도 둔다
            items.append((LAB(_k, _n), BASE + _u))
    if part('search', False):
        items.append(('검색', BASE + 'search/'))
    items += ([('확인하는 방법', BASE + 'how/')] if part('info') else []) + [('소개', BASE + 'about/'), ('문의', BASE + 'contact/')]   # 확인하는 방법은 뉴스를 다루는 사이트에만
    if part('demo', False):
        items.append(('조립 예시', BASE + 'demo/'))
    MAXN = 5
    shown, rest = (items, []) if len(items) <= MAXN + 1 else (items[:MAXN], items[MAXN:])
    GAMES_LINK = ''.join(f'<a href="{u}">{E(n)}</a>' for n, u in shown)
    if rest:
        GAMES_LINK += '<details class="mn"><summary>더 보기</summary><div class="mnp">' + ''.join(f'<a href="{u}">{E(n)}</a>' for n, u in rest) + '</div></details>'
    doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">{canon_tag}{robots}
{rss_tag}<link rel="stylesheet" href="{BASE}style.css">{PWA_HEAD}{PREF_HEAD}</head><body class="th-{THEME}" style="--ac:{E(ACCENT)}">
<header class="mast"><div class="wrap"><div class="dateline">{today_ko()} · {E(S['tagline'])}</div>
{LOGO}</div></header>
<div class="wrap"><nav class="menu">{GAMES_LINK}</nav></div>
<main class="wrap">{_kp.notice_banner(sys.modules[__name__]) if not path else ''}{body}</main>
<footer><div class="wrap"><a href="{BASE}privacy/">개인정보 처리방침</a>{rss_link}{('<a href="' + BASE + 'ebook/">전자책</a>') if part('ebook', False) else ''}{('<a href="' + BASE + 'status/">상태</a>') if part('status', False) else ''}{('<a href="' + BASE + 'kits/">키트</a>') if part('kits', False) else ''}{''.join(f'<a href="{BASE}{u}">{n}</a>' for k, (n, u) in {**FOOT, **_kp.FOOT4}.items() if part(k, False))}{PREFS_UI}{'<p>기사 본문은 싣지 않고 제목·매체·시각·링크만 모아 보여 줍니다. 기사의 저작권은 각 매체에 있습니다.</p>' if part('info') else ''}</div></footer>{PWA_REG}</body></html>"""
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(doc)
    if not explicit_noindex:   # 조립 예시(DEMO)도 사이트 안 검색에는 들어간다(검색 엔진용 noindex 와 별개)
        SEARCH.append((f'{BASE}{path}/' if path else BASE, title, desc))
    return canon


ISSUE_DATES = []   # 노트가 있는 날짜(오래된 순) — load_notes 가 채운다
PDF_SRC = os.path.join(HERE, 'issues_pdf')   # 인쇄용 PDF 원본(issue.py 가 만든다). build.py 가 docs/issue/<날짜>/ 로 복사한다


def issue_pages(notes):
    """그날의 확인 노트를 묶어 「호」 한 편으로: /issue/<날짜>/ (읽기 쪽) + print.html(인쇄용, 글꼴·괘선 인라인) + 목록 /issue/.
    인쇄용 PDF 는 issue.py 가 브라우저 인쇄 기능으로 만들어 issues_pdf/ 에 두면 링크가 붙는다."""
    if not part('issue'):
        return []
    if not notes:   # 노트가 0건이면 호가 없다 — 목록 쪽에 안내를 둔다
        return [page('issue', f'잡지 — {S["name"]}', '확인 노트를 날짜별로 묶은 호 모음', f'<div class="page"><span class="lb">잡지</span><h1>{E(S["name"])} 발행호</h1><p>첫 호를 준비 중입니다. 확인 노트(notes/)를 한 건 쓰면 그날의 호가 만들어집니다.</p></div>')]
    by = {}
    for n in notes:
        by.setdefault(n['date'], []).append(n)
    dates = sorted(by)
    urls = []
    for k, d in enumerate(dates, 1):
        ns = by[d]
        pdf = os.path.join(PDF_SRC, f'{d}.pdf')
        has_pdf = os.path.exists(pdf)
        items = ''.join(f'<div class="tp"><span class="v {VERDICTS[n["verdict"]]}">{E(n["verdict"])}</span><b><a href="{BASE}n/{n["id"]}/">{E(n["title"])}</a></b><span class="ln">{E(n["summary"])}</span></div>' for n in ns)
        link = f'<p class="sub"><a href="{BASE}issue/{d}/{d}.pdf">인쇄용 PDF 내려받기</a></p>' if has_pdf else ''
        body = (f'<div class="page"><span class="lb">제{k}호 · {E(d)}</span><h1>{E(S["name"])} 제{k}호</h1><p>{E(d)} 확인 노트 {len(ns)}건을 묶었습니다.</p>{link}{items}</div>')
        urls.append(page(f'issue/{d}', f'제{k}호 {d} — {S["name"]}', f'{d} 확인 노트 {len(ns)}건 묶음', body))
        # 인쇄용(스타일 인라인, 링크는 글자로 풀어 씀)
        pr = ''.join(f'<h2>{E(n["title"])} <small>[{E(n["verdict"])}]</small></h2><p>{E(n["question"])}</p><p>{E(n["summary"])}</p><ul>' + ''.join(f'<li>{E(f["text"])} <i>({E(f["source"])})</i></li>' for f in n.get('facts', [])) + '</ul>' + (''.join(f'<p>아직 확인 안 된 것: {E(x)}</p>' for x in n.get('unconfirmed', []))) for n in ns)
        doc = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{E(S["name"])} 제{k}호</title><style>@page{{size:A4;margin:18mm}}body{{font:12pt/1.7 "Noto Serif KR","Nanum Myeongjo",Batang,serif;color:#111}}'
               f'h1{{text-align:center;font-size:30pt;margin:0;border-bottom:3px double #111;padding-bottom:8px}}.m{{text-align:center;font:10pt sans-serif;color:#555;margin:6px 0 18px}}h2{{font-size:15pt;border-top:2px solid #111;padding-top:8px;margin-top:20px}}small{{font:9pt sans-serif}}li{{margin:4px 0}}</style></head>'
               f'<body><h1>{E(S["name"])}</h1><div class="m">제{k}호 · {E(d)} · {E(S["tagline"])}</div>{pr}</body></html>')
        os.makedirs(os.path.join(OUT, 'issue', d), exist_ok=True)
        open(os.path.join(OUT, 'issue', d, 'print.html'), 'w', encoding='utf-8').write(doc)
        if has_pdf:
            shutil.copy(pdf, os.path.join(OUT, 'issue', d, f'{d}.pdf'))
    lst = ''.join(f'<a href="{BASE}issue/{d}/"><span class="lb">제{k}호</span><h3>{E(d)} 확인 노트 {len(by[d])}건</h3><p>{E(" · ".join(n["title"] for n in by[d])[:120])}</p></a>' for k, d in reversed(list(enumerate(dates, 1))))
    urls.append(page('issue', f'잡지 — {S["name"]}', '확인 노트를 날짜별로 묶은 호 모음', f'<div class="page"><span class="lb">잡지</span><h1>{E(S["name"])} 발행호</h1><div class="gl">{lst}</div></div>'))
    return urls


def md(text):
    """아주 작은 마크다운 → HTML: # ## ### 제목, - 목록, 1. 목록, | 표 |, **굵게**, [글자](주소), 빈 줄로 문단. 나머지는 글자 그대로(HTML 은 막는다)."""
    def inline(t):
        t = E(t)
        t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
        t = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', r'<a href="\2" rel="noopener nofollow">\1</a>', t)
        return re.sub(r'(?<![">])(https?://[^\s<)]+)', r'<a href="\1" rel="noopener nofollow">\1</a>', t)
    out, para, lst, tbl = [], [], [], []

    def flush():
        nonlocal para, lst, tbl
        if para:
            out.append('<p>' + inline(' '.join(para)) + '</p>'); para = []
        if lst:
            tag = lst[0][0]; out.append(f'<{tag}>' + ''.join(f'<li>{inline(x[1])}</li>' for x in lst) + f'</{tag}>'); lst = []
        if tbl:
            rows = [r for r in tbl if not re.fullmatch(r'\|[\s:|-]+\|?', r.strip())]
            out.append('<table class="mdt">' + ''.join('<tr>' + ''.join(f'<td>{inline(c.strip())}</td>' for c in r.strip().strip('|').split('|')) + '</tr>' for r in rows) + '</table>'); tbl = []
    for line in text.splitlines():
        s = line.rstrip()
        if not s.strip():
            flush(); continue
        m = re.match(r'(#{1,3}) (.+)', s)
        if m:
            flush(); lv = len(m.group(1)); out.append(f'<h{lv + 1}>{inline(m.group(2))}</h{lv + 1}>'); continue
        if s.startswith('|'):
            if para or lst: flush()
            tbl.append(s); continue
        m = re.match(r'(?:- |\* )(.+)', s)
        if m:
            if para or tbl: flush()
            lst.append(('ul', m.group(1))); continue
        m = re.match(r'\d+\. (.+)', s)
        if m:
            if para or tbl: flush()
            lst.append(('ol', m.group(1))); continue
        if lst or tbl: flush()
        para.append(s.strip())
    flush()
    return ''.join(out)


def first_h1(text, default):
    m = re.search(r'^# (.+)$', text, re.M)
    return m.group(1).strip() if m else default


def pdf_link(slug):
    """pdf 키트(pdf.py)가 만든 pdfs/<글>.pdf 가 있으면 글 위에 내려받기 링크를 붙이고 파일을 docs 로 복사한다."""
    p = os.path.join(HERE, 'pdfs', slug + '.pdf')
    if not part('pdf', False) or not os.path.exists(p):
        return ''
    os.makedirs(os.path.join(OUT, 'pdf'), exist_ok=True)
    shutil.copy(p, os.path.join(OUT, 'pdf', slug + '.pdf'))
    return f'<p class="ad-nt"><a href="{BASE}pdf/{slug}.pdf">이 글을 PDF 로 내려받기</a></p>'


def content_pages():
    """글(posts/*.md)·연재 소설(novels/<작품>/소개.md + 01.md…)·웹툰(toons/<작품>/meta.json + 회차 그림)·영상 모음(extras.videos). 켜진 부품만."""
    urls = []
    # 글
    pdir = os.path.join(DATA_ROOT, 'posts')
    if part('posts', False) and os.path.isdir(pdir):
        posts = []
        for f in sorted(glob.glob(os.path.join(pdir, '*.md'))):
            t = open(f, encoding='utf-8').read(); slug = os.path.splitext(os.path.basename(f))[0]
            posts.append((slug, first_h1(t, slug), t))
        notice = S.get('post_notice') or '세법·제도는 해마다 바뀔 수 있으니 글 끝의 출처에서 현행 내용을 확인하세요.'
        for slug, title, t in posts:
            body = re.sub(r'^# .+\n', '', t, count=1)
            urls.append(page(f'post/{slug}', f'{title} — {S["name"]}', re.sub(r'\s+', ' ', re.sub(r'[#*|\[\]]', '', body))[:140],
                             f'<article class="art"><span class="lb">글</span><h1>{E(title)}</h1><p class="ad-nt" style="margin:0 0 16px">{E(notice)}</p>{pdf_link(slug)}{_kp.post_meta(sys.modules[__name__], slug, title, body)}</article>'))
        lst = ''.join(f'<a href="{BASE}post/{s}/"><span class="lb">글</span><h3>{E(t)}</h3><p>{E(re.sub(chr(10), " ", re.sub(r"^#.*$", "", x, flags=re.M)).strip()[:100])}</p></a>' for s, t, x in posts)
        urls.append(page('post', f'글 — {S["name"]}', '생활·돈 가이드 글 모음', f'<div class="page"><span class="lb">글</span><h1>글</h1><div class="gl">{lst}</div></div>'))
    # 연재 소설
    ndir = os.path.join(DATA_ROOT, 'novels')
    if part('novel', False) and os.path.isdir(ndir):
        cards = ''
        for nd in sorted(glob.glob(os.path.join(ndir, '*'))):
            if not os.path.isdir(nd): continue
            slug = os.path.basename(nd)
            intro = open(os.path.join(nd, '소개.md'), encoding='utf-8').read() if os.path.exists(os.path.join(nd, '소개.md')) else ''
            title = first_h1(intro, slug)
            eps = [(os.path.splitext(os.path.basename(f))[0], open(f, encoding='utf-8').read()) for f in sorted(glob.glob(os.path.join(nd, '[0-9]*.md')))]
            toc = ''.join(f'<li><a href="{BASE}novel/{slug}/{n}/">{E(first_h1(t, n + "화"))}</a></li>' for n, t in eps)
            urls.append(page(f'novel/{slug}', f'{title} — {S["name"]}', re.sub(r'\s+', ' ', re.sub(r'^#.*$', '', intro, flags=re.M)).strip()[:140],
                             f'<article class="art"><span class="lb">연재 소설</span><h1>{E(title)}</h1>{md(re.sub(chr(94) + "# .+" + chr(10), "", intro, count=1))}<h2>회차</h2><ul class="rp">{toc}</ul></article>'))
            for k, (n, t) in enumerate(eps):
                prev = f'<a href="{BASE}novel/{slug}/{eps[k-1][0]}/">← 이전 화</a>' if k > 0 else '<span></span>'
                nxt = f'<a href="{BASE}novel/{slug}/{eps[k+1][0]}/">다음 화 →</a>' if k + 1 < len(eps) else '<span></span>'
                ctl = ('<div class="fz"><button type="button" data-d="-1">가-</button><button type="button" data-d="1">가+</button></div>'
                       '<script>(function(){var a=document.querySelector(".nv"),k="fm_fz",v=17;try{v=+localStorage.getItem(k)||17}catch(e){}function s(){a.style.fontSize=v+"px"}s();'
                       'document.querySelectorAll(".fz button").forEach(function(b){b.onclick=function(){v=Math.max(14,Math.min(26,v+(+b.dataset.d)*2));try{localStorage.setItem(k,v)}catch(e){}s()}})})()</script>')
                urls.append(page(f'novel/{slug}/{n}', f'{first_h1(t, n + "화")} — {title} — {S["name"]}', re.sub(r'\s+', ' ', re.sub(r'^#.*$', '', t, flags=re.M)).strip()[:140],
                                 f'<article class="art"><span class="lb">{E(title)}</span>{ctl}<div class="nv">{md(t).replace('<h2>', '<h1>', 1).replace('</h2>', '</h1>', 1)}</div><div class="by">{prev}<a href="{BASE}novel/{slug}/">목차</a>{nxt}</div></article>'))
            cards += f'<a href="{BASE}novel/{slug}/"><span class="lb">연재 소설</span><h3>{E(title)}</h3><p>{E(re.sub(chr(10), " ", re.sub(r"^#.*$", "", intro, flags=re.M)).strip()[:100])}</p></a>'
        urls.append(page('novel', f'연재 — {S["name"]}', '연재 소설 모음', f'<div class="page"><span class="lb">연재</span><h1>연재 소설</h1><div class="gl">{cards}</div></div>'))
    # 웹툰
    tdir = os.path.join(DATA_ROOT, 'toons')
    if part('toon', False) and os.path.isdir(tdir):
        cards = ''
        for td in sorted(glob.glob(os.path.join(tdir, '*', 'meta.json'))):
            m = json.load(open(td, encoding='utf-8')); slug = os.path.basename(os.path.dirname(td))
            toc = ''.join(f'<li><a href="{BASE}toon/{slug}/{e["id"]}/">{E(e["title"])}</a></li>' for e in m['episodes'])
            urls.append(page(f'toon/{slug}', f'{m["title"]} — {S["name"]}', m['intro'], f'<article class="art"><span class="lb">{E(m.get("kind", "웹툰"))}</span><h1>{E(m["title"])}</h1><p>{E(m["intro"])}</p><h2>회차</h2><ul class="rp">{toc}</ul></article>'))
            for e in m['episodes']:
                imgs = ''.join(f'<img src="{BASE}toon/{slug}/{e["id"]}/{p}" alt="{E(e["title"])} {i}컷" loading="lazy" style="display:block;width:100%;height:auto;margin:0 0 10px;border:1px solid var(--hair)">' for i, p in enumerate(e['panels'], 1))
                urls.append(page(f'toon/{slug}/{e["id"]}', f'{e["title"]} — {m["title"]} — {S["name"]}', m['intro'], f'<article class="art"><span class="lb">{E(m["title"])}</span><h1>{E(e["title"])}</h1>{imgs}<div class="by"><a href="{BASE}toon/{slug}/">회차 목록</a></div></article>'))
                for p in e['panels']:
                    os.makedirs(os.path.join(OUT, 'toon', slug, e['id']), exist_ok=True)
                    shutil.copy(os.path.join(tdir, slug, e['id'], p), os.path.join(OUT, 'toon', slug, e['id'], p))
            cards += f'<a href="{BASE}toon/{slug}/"><span class="lb">{E(m.get("kind", "웹툰"))}</span><h3>{E(m["title"])}</h3><p>{E(m["intro"])}</p></a>'
        urls.append(page('toon', f'웹툰 — {S["name"]}', '웹툰·만화 모음', f'<div class="page"><span class="lb">웹툰</span><h1>웹툰</h1><div class="gl">{cards}</div></div>'))
    # 영상 모음 (값은 extras.videos — 유튜브 주소 목록)
    vids = [v for v in (EX.get('videos') or []) if re.search(r'(youtu\.be/|youtube\.com/(shorts/|watch\?v=))([A-Za-z0-9_-]{11})', v.get('url', ''))]
    if part('video', False) and vids:
        h = ''
        for v in vids:
            vid = re.search(r'(youtu\.be/|youtube\.com/(shorts/|watch\?v=))([A-Za-z0-9_-]{11})', v['url']).group(3)
            sh = '/shorts/' in v['url']
            h += (f'<div class="tp"><b>{E(v.get("title", "영상"))}</b><iframe src="https://www.youtube-nocookie.com/embed/{vid}" loading="lazy" title="{E(v.get("title", "영상"))}" allowfullscreen '
                  f'style="width:{"270px" if sh else "100%"};aspect-ratio:{"9/16" if sh else "16/9"};border:0;background:#111;display:block;margin-top:8px"></iframe><span class="ln"><a href="{E(v["url"])}" rel="noopener nofollow" target="_blank">유튜브에서 보기</a></span></div>')
        urls.append(page('video', f'영상 — {S["name"]}', '확인 노트로 만든 영상 모음', f'<div class="page"><span class="lb">영상</span><h1>영상</h1>{h}</div>'))
    return urls


SEARCH = []   # 사이트 안 검색 색인(쪽 주소·제목·설명) — page() 가 채운다
KITS_DIR = os.path.abspath(os.environ['KITS_DIR']) if os.environ.get('KITS_DIR') else os.path.join(HERE, 'kits')   # 데모 조합은 자기 자료 폴더를 쓸 수 있다
DATA_ROOT = os.path.abspath(os.environ['DATA_ROOT']) if os.environ.get('DATA_ROOT') else HERE   # 글·소설·웹툰·전자책 원본 폴더의 위치(데모는 자기 폴더를 쓴다)
DEMO = bool(os.environ.get('DEMO'))   # 데모(조립 예시)는 본 사이트와 내용이 겹치므로 검색에 안 나가게 한다(noindex, 사이트맵·RSS 없음)
SAFE_EXPR = re.compile(r'^[A-Za-z0-9_+\-*/().,%<>=!?:&| ]+$')


def kit_data(kit, name):
    p = os.path.join(KITS_DIR, kit, 'data', name)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def calc_pages():
    """계산기 키트: kits/calc/data/calculators.json → /calc/ 목록과 계산기마다 쪽(브라우저에서 바로 계산, 서버 없음).
    식은 이 파일의 JS 식이므로 허용 글자만 쓰게 검사한다(Math.pow 같은 수학 함수만)."""
    if not part('calc', False):
        return []
    calcs = kit_data('calc', 'calculators.json') or []
    urls, cards = [], ''
    for c in calcs:
        exprs = [v['expr'] for v in c.get('vars', [])] + [r['expr'] for r in c['results']]
        if any(not SAFE_EXPR.match(x) or re.search(r'constructor|window|document|eval|Function|import|fetch', x) for x in exprs):
            print('계산기 식에 허용되지 않는 글자가 있어 건너뜀:', c['slug']); continue
        fields = ''.join(f'<label for="i_{i["id"]}">{E(i["label"])}{(" (" + E(i["unit"]) + ")") if i.get("unit") else ""}</label><input id="i_{i["id"]}" type="number" inputmode="decimal" step="any" value="{E(str(i.get("default", 0)))}">' for i in c['inputs'])
        data = json.dumps({'inputs': [i['id'] for i in c['inputs']], 'vars': c.get('vars', []), 'results': c['results']}, ensure_ascii=False)
        js = ('<script>(function(){var C=%s;function f(e,x){return new Function("v","with(v){return ("+e+")}")(x)}function fmt(n,k){if(!isFinite(n))return "계산할 수 없음";'
              'if(k=="won")return Math.round(n).toLocaleString("ko-KR")+"원";if(k=="pct")return (Math.round(n*100)/100)+"%%";return (Math.round(n*100)/100).toLocaleString("ko-KR")}'
              'function run(){var v={Math:Math};C.inputs.forEach(function(i){v[i]=parseFloat(document.getElementById("i_"+i).value)||0});'
              'C.vars.forEach(function(x){v[x.id]=f(x.expr,v)});var h="";C.results.forEach(function(r){h+="<div class=\\"cr\\"><span>"+r.label+"</span><b>"+fmt(f(r.expr,v),r.format)+"</b></div>"});document.getElementById("cr").innerHTML=h}'
              'document.querySelectorAll(".calc input").forEach(function(i){i.addEventListener("input",run)});run()})()</script>') % data
        body = (f'<article class="art"><span class="lb">계산기</span><h1>{E(c["title"])}</h1><p class="dek">{E(c["desc"])}</p><div class="calc">{fields}</div><div id="cr" class="crs"></div>'
                f'<p class="ad-nt">{E(c.get("note", "참고용 계산입니다. 실제 금액은 상품·세금·수수료에 따라 다릅니다."))}</p></article>{js}')
        urls.append(page(f'calc/{c["slug"]}', f'{c["title"]} — {S["name"]}', c['desc'], body))
        cards += f'<a href="{BASE}calc/{c["slug"]}/"><span class="lb">계산기</span><h3>{E(c["title"])}</h3><p>{E(c["desc"])}</p></a>'
    if urls:
        urls.append(page('calc', f'계산기 — {S["name"]}', '숫자를 넣으면 바로 계산되는 작은 계산기 모음', f'<div class="page"><span class="lb">계산기</span><h1>계산기</h1><div class="gl">{cards}</div></div>'))
    return urls


def glossary_pages():
    """용어 사전 키트: kits/glossary/data/terms.json 한 파일 → /glossary/ 목록 + 용어마다 쪽."""
    if not part('glossary', False):
        return []
    terms = kit_data('glossary', 'terms.json') or []
    if not terms:
        return []
    slug = lambda t: re.sub(r'\s+', '-', t.strip())
    names = {t['term'] for t in terms}
    urls = []
    for t in terms:
        see = ''.join(f'<li><a href="{BASE}glossary/{slug(x)}/">{E(x)}</a></li>' for x in t.get('see', []) if x in names)
        body = (f'<article class="art"><span class="lb">용어 사전</span><h1>{E(t["term"])}</h1><p class="dek">{E(t["short"])}</p>{md(t["body"])}'
                + (f'<h2>함께 보기</h2><ul class="rp">{see}</ul>' if see else '') + f'<div class="by"><a href="{BASE}glossary/">용어 목록</a></div></article>')
        urls.append(page(f'glossary/{slug(t["term"])}', f'{t["term"]}이란? — {S["name"]}', t['short'], body))
    lst = ''.join(f'<li><a href="{BASE}glossary/{slug(t["term"])}/"><b>{E(t["term"])}</b></a> — {E(t["short"])}</li>' for t in sorted(terms, key=lambda x: x['term']))
    urls.append(page('glossary', f'용어 사전 — {S["name"]}', f'돈·생활 용어 {len(terms)}개를 쉬운 말로 풀었습니다', f'<div class="page"><span class="lb">용어 사전</span><h1>용어 사전 <small style="font:14px var(--sans);color:var(--mu)">{len(terms)}개</small></h1><ul class="rp">{lst}</ul></div>'))
    return urls


def search_page():
    """사이트 안 검색 키트: 찍을 때 만든 색인 파일(search.json)을 브라우저에서 찾는다(서버 없음). 색인 파일은 build 끝에 쓴다."""
    if not part('search', False):
        return []
    js = ('<script>(function(){var q=document.getElementById("q"),o=document.getElementById("o"),D=[];'
          'fetch("%ssearch.json").then(function(r){return r.json()}).then(function(d){D=d;go()}).catch(function(){o.textContent="검색 색인을 불러오지 못했습니다."});'
          'function esc(s){return s.replace(/[&<>]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;"}[c]})}'
          'function go(){var t=q.value.trim().toLowerCase();if(!t){o.innerHTML="<p class=\\"mu\\">찾을 글자를 입력하세요. 쪽 "+D.length+"개에서 찾습니다.</p>";return}'
          'var w=t.split(/\\s+/),r=[];D.forEach(function(p){var h=(p[1]+" "+p[2]).toLowerCase(),s=0;for(var i=0;i<w.length;i++){if(h.indexOf(w[i])<0){s=-1;break}s+=p[1].toLowerCase().indexOf(w[i])>=0?3:1}if(s>0)r.push([s,p])});'
          'r.sort(function(a,b){return b[0]-a[0]});o.innerHTML=r.length?r.slice(0,30).map(function(x){return "<div class=\\"tp\\"><b><a href=\\""+x[1][0]+"\\">"+esc(x[1][1])+"</a></b><span class=\\"ln\\">"+esc(x[1][2].slice(0,90))+"</span></div>"}).join(""):"<p class=\\"mu\\">찾는 글이 없습니다.</p>"}'
          'q.addEventListener("input",go);var m=location.search.match(/[?&]q=([^&]*)/);if(m){try{q.value=decodeURIComponent(m[1])}catch(e){}}})()</script>') % BASE
    body = (f'<div class="page"><span class="lb">검색</span><h1>사이트 안 검색</h1><input id="q" type="search" placeholder="찾을 글자" autofocus '
            f'style="font:18px var(--sans);padding:12px;width:100%;border:2px solid var(--ink)"><div id="o" style="margin-top:16px"></div></div>{js}')
    return [page('search', f'검색 — {S["name"]}', '이 사이트의 글·노트·게임을 찾습니다', body)]


def write_search_index():
    if not part('search', False):
        return
    seen, out = set(), []
    for u, t, d in SEARCH:
        if u in seen or u.rstrip('/').endswith('/search'):
            continue
        seen.add(u); out.append([u, t, re.sub(r'\s+', ' ', d)[:160]])
    open(os.path.join(OUT, 'search.json'), 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, separators=(',', ':')))


def status_page(notes):
    """상태 쪽 키트: 사람이 아침에 한 번 보는 쪽(검색에는 안 나가게 noindex). 마지막 수집·피드별 건수와 실패·노트/글/게임 수·대조·점검·최근 커밋."""
    if not part('status', False):
        return []
    def jl(p):
        p = os.path.join(HERE, p)
        return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None
    items = jl('data/items.json') or {}
    chk = jl('data/checked.json') or {}
    aud = jl('logs/audit.json') or {}
    held = len(glob.glob(os.path.join(HERE, '보류', '*.json')))
    n_posts = len(glob.glob(os.path.join(HERE, 'posts', '*.md'))) if part('posts', False) else 0
    n_eps = len(glob.glob(os.path.join(HERE, 'novels', '*', '[0-9]*.md'))) if part('novel', False) else 0
    try:
        last = subprocess.run(['git', 'log', '-1', '--format=%cd · %s', '--date=format:%Y-%m-%d %H:%M'], cwd=HERE, capture_output=True, text=True, encoding='utf-8', timeout=10).stdout.strip()
    except Exception:
        last = '(git 정보를 읽지 못함)'
    feed_rows = ''.join(f'<tr><td>{E(x["source"])} {E(x["section"])}</td><td>{x["count"]}건</td><td>{E(x["error"]) or "정상"}</td></tr>' for x in items.get('log', []))
    bad = [x for x in items.get('log', []) if x['error'] or not x['count']]
    rows = [('마지막 수집', items.get('collected_at', '기록 없음')), ('마지막 빌드', datetime.datetime.now().strftime('%Y-%m-%d %H:%M')), ('수집한 기사(최근 3일)', f'{len(items.get("items", []))}건'),
            ('피드', f'{len(items.get("log", []))}곳 중 문제 {len(bad)}곳'), ('확인 노트', f'{len(notes)}건 (대조 통과 기록 {len(chk)}건 · 보류 {held}건)'), ('글·소설 회차', f'{n_posts}편 · {n_eps}화'),
            ('게임', f'{len(load_games())}개'), ('점검(audit.py)', (f'쪽 {aud.get("pages")}개, 문제 {aud.get("problems")}건 ({aud.get("at")})' if aud else '아직 안 돌림 — python audit.py')), ('최근 커밋', last)]
    t = ''.join(f'<tr><th>{E(k)}</th><td>{E(v)}</td></tr>' for k, v in rows)
    body = (f'<div class="page"><span class="lb">상태</span><h1>상태</h1><table class="mdt"><tbody>{t}</tbody></table><h2>피드별</h2><table class="mdt"><tbody>{feed_rows or "<tr><td>기록 없음</td></tr>"}</tbody></table>'
            + (('<h2>점검에서 나온 문제 (앞 20건)</h2><ul>' + ''.join(f'<li>{E(x)}</li>' for x in aud.get('list', [])[:20]) + '</ul>') if aud.get('list') else '') + '</div>')
    page('status', f'상태 — {S["name"]}', '운영 상태', body, noindex=True)
    return []   # 사이트맵에는 넣지 않는다


def ebook_pages():
    """전자책 키트: ebook.py 가 만든 PDF(ebooks/*.pdf)를 /ebook/ 에 내려받기로 둔다."""
    if not part('ebook', False):
        return []
    pdfs = sorted(glob.glob(os.path.join(DATA_ROOT, 'ebooks', '*.pdf')))
    if not pdfs:
        return [page('ebook', f'전자책 — {S["name"]}', '글을 묶은 전자책', '<div class="page"><span class="lb">전자책</span><h1>전자책</h1><p>글과 연재 소설을 표지·차례가 있는 PDF 한 권으로 묶어 내려받게 하는 쪽입니다. 아직 만든 책이 없습니다. python ebook.py 로 글·연재를 PDF 한 권으로 묶으세요.</p></div>')]
    li = ''
    os.makedirs(os.path.join(OUT, 'ebook'), exist_ok=True)
    for p in pdfs:
        n = os.path.basename(p); shutil.copy(p, os.path.join(OUT, 'ebook', n))
        li += f'<div class="tp"><b>{E(os.path.splitext(n)[0])}</b><span class="ln"><a href="{BASE}ebook/{n}">PDF 내려받기</a> · {round(os.path.getsize(p) / 1024)}KB</span></div>'
    return [page('ebook', f'전자책 — {S["name"]}', '글과 연재를 묶은 전자책(PDF)', f'<div class="page"><span class="lb">전자책</span><h1>전자책</h1><p>글과 연재 소설을 표지와 차례가 있는 한 권으로 묶은 전자책입니다. PDF 파일로 내려받아 휴대폰이나 컴퓨터에서 읽거나 인쇄할 수 있습니다.</p>{li}</div>')]


def kits_page():
    """키트 목록 쪽(/kits/): kits/*/kit.json 의 한 줄 입력을 그대로 보여 준다(독자가 복사해 쓰는 쪽)."""
    if not part('kits', False):
        return []
    ks = [json.load(open(p, encoding='utf-8')) for p in sorted(glob.glob(os.path.join(KITS_DIR, '*', 'kit.json')))]
    if not ks:
        return []
    li = ''.join(f'<div class="tp"><span class="lb">{E(k["name"])}</span><b>{E(k["title"])}</b><span class="ln">이렇게 입력하세요 → <code>{E(k["input_line"])}</code></span><span class="ln">나오는 것: {E(k["gives"])}</span><span class="ln">2분 안에 보는 결과: {E(k["see"])}</span>' + ('<span class="ln"><b>꼭 알아야 할 것 3가지</b> · ' + ' · '.join(f'{i}) {E(m["알것"][:48])}' for i, m in enumerate([x for x in k.get('must_know', []) if x.get('근거') != '일반'][:3], 1)) + '</span>' if k.get('must_know') else '') + '</div>' for k in ks)
    return [page('kits', f'키트 — {S["name"]}', '5~10분에 하나씩 따라 해 보는 작은 하네스 모음', f'<div class="page"><span class="lb">키트</span><h1>키트</h1><p>하나만 켜 보고, 두세 개 해 본 뒤 섞어 봅니다. 아래 입력 문장을 Claude Code 에 그대로 붙여 넣으세요. 섞는 법: <code>python mix.py 키트1 키트2</code></p>{li}</div>')]


def load_games():
    """games/<이름>/meta.json 을 읽어 목록(order 순)으로. 게임 폴더가 없으면 빈 목록."""
    out = []
    if not part('games'):
        return out
    for mp in sorted(glob.glob(os.path.join(GAMES_SRC, '*', 'meta.json'))):
        m = json.load(open(mp, encoding='utf-8'))
        m['slug'] = os.path.basename(os.path.dirname(mp))
        out.append(m)
    return sorted(out, key=lambda m: m.get('order', 99))


def game_pages():
    """게임 목록 쪽(/games/)과 게임마다 쪽(/games/<이름>/)을 만들고 원본 파일을 docs/games/<이름>/ 로 복사한다."""
    games = load_games()
    if not games:
        return []
    urls = []
    items = ''.join(f'<a href="{BASE}games/{g["slug"]}/"><span class="lb">{E(g.get("kind", "게임"))}</span><h3>{E(g["title"])}</h3><p>{E(g.get("intro", g["desc"]))}</p></a>' for g in games)
    body = f'<div class="page"><span class="lb">게임</span><h1>{E(S["name"])} 웹 게임</h1><p>{E(S.get("games_desc", "설치 없이 브라우저에서 바로 할 수 있는 작은 게임입니다."))}</p><div class="gl">{items}</div></div>'
    urls.append(page('games', S.get('games_title') or f'{S["name"]} 웹 게임', S.get('games_desc', '브라우저에서 바로 하는 작은 게임 모음'), body))
    for g in games:
        how = ''.join(f'<li>{E(x)}</li>' for x in g.get('how', []))
        b = (f'<div class="gm"><span class="lb">{E(g.get("kind", "게임"))}</span><h1>{E(g["title"])}</h1><p class="dek">{E(g.get("intro", g["desc"]))}</p>'
             f'<canvas id="g" width="720" height="1080"></canvas><ol class="how">{how}</ol>'
             + (f'<p class="note">판 {g.get("ver", 1)} — 바뀐 것: {E(g["changes"])}</p>' if g.get('changes') else f'<p class="note">판 {g.get("ver", 1)}</p>') +
             f'<p class="note">최고 기록은 이 브라우저에만 저장됩니다. 서버로 보내지 않습니다. <a href="{BASE}games/">다른 게임 보기</a></p></div><script src="game.js?v={g.get("ver", 1)}"></script>')
        urls.append(page(f'games/{g["slug"]}', f'{g["title"]} — {S["name"]}', g['desc'], b))
        src = os.path.join(GAMES_SRC, g['slug'])
        for f in os.listdir(src):
            if f != 'meta.json':
                shutil.copy(os.path.join(src, f), os.path.join(OUT, 'games', g['slug'], f))
    return urls


def load_notes(with_example):
    notes = []
    for p in sorted(glob.glob(os.path.join(HERE, 'notes', '*.json')), reverse=True):
        n = json.load(open(p, encoding='utf-8'))
        if n.get('example') and not with_example:
            continue
        if n.get('verdict') not in VERDICTS:
            print('판정 값이 이상해 건너뜀:', os.path.basename(p)); continue
        notes.append(n)
    ISSUE_DATES[:] = sorted({n['date'] for n in notes}) if part('issue') else []
    return notes


def note_page(n):
    """확인 노트 한 편 — 기사처럼: 큰 명조 제목, 질문(부제), 날짜·판정 줄, 좁은 본문, 사실마다 각주 번호와 출처."""
    v = VERDICTS[n['verdict']]
    ex = '<span class="ex">예시 — 화면 틀 시험용 가짜 노트입니다</span>' if n.get('example') else ''
    li = lambda xs: ''.join(f'<li>{E(x)}</li>' for x in xs)
    facts = ''.join(f'<li>{E(f["text"])}<span class="src">출처 · <a href="{E(f["url"])}" rel="noopener nofollow">{E(f["source"])}</a></span></li>' for f in n.get('facts', []))
    reports = ''.join(f'<li><a href="{E(r["url"])}" rel="noopener nofollow">{E(r["title"])}</a> · {E(r["source"])}</li>' for r in n.get('reports', []))
    body = (f'<article class="art">{ex}<span class="lb">확인 노트</span><h1>{E(n["title"])}</h1><p class="dek">{E(n["question"])}</p>'
            f'<div class="by"><span class="v {v}">{E(n["verdict"])}</span><span>{E(n["date"])}</span><span>확인 시각 {E(n["checked_at"])}</span></div>'
            f'<p class="sum">{E(n["summary"])}</p>'
            + (f'<h2>확인한 사실</h2><ol class="fn">{facts}</ol>' if facts else '')
            + (f'<h2>매체마다 다르게 전한 점</h2><ul>{li(n["differs"])}</ul>' if n.get('differs') else '')
            + (f'<h2>아직 확인 안 된 것</h2><ul>{li(n["unconfirmed"])}</ul>' if n.get('unconfirmed') else '')
            + (f'<h2>관련 기사</h2><ul class="rp">{reports}</ul>' if reports else '') + _kp.related_html(sys.modules[__name__], '노트', n['id']) + '</article>')
    return page(f'n/{n["id"]}', f'{n["title"]} — {S["name"]}', n['summary'][:150], body, noindex=bool(n.get('example')))


def filter_topics(topics):
    """주제 키워드가 있으면 묶음 제목이나 기사 제목에 키워드가 든 묶음만 남긴다. 0건이면 필터 없이 보여 주고 알린다. (남은 묶음, 안내 글)"""
    if not KEYWORDS:
        return topics, ''
    hit = {k: [t for t in topics if k in t['title'] or any(k in i['title'] for i in t['items'])] for k in KEYWORDS}
    keep = [t for t in topics if any(t in v for v in hit.values())]
    for k, v in hit.items():   # 어떤 낱말이 어떤 묶음을 불러왔는지 — 무관한 묶음이 보이면 그 낱말을 더 구체적으로 바꾼다
        print(f'  키워드 「{k}」 → 묶음 {len(v)}건' + (': ' + ' / '.join(t['title'][:22] for t in v[:3]) if v else ''))
    if keep:
        return keep, ''
    print('주의: 키워드', KEYWORDS, '에 맞는 묶음이 0건이라 필터 없이 보여 줍니다. 피드(feeds.json)나 키워드를 바꿔 보세요.')
    return topics, '주제 키워드에 맞는 소식이 아직 없어 전체 소식을 보여 줍니다.'


def extras_html():
    """첫 화면 아래 「영상·게임·블로그·추천」 단. 값(site.local.json 또는 SITE_EXTRAS)이 있는 칸만 나온다.
    쿠팡 같은 제휴 링크는 확인 노트 본문과 섞지 않고 이 단에만 두며 「광고」 표시와 수수료 고지 문구를 붙인다."""
    cols = []
    yt = EX.get('youtube') or {}
    ids = [i for i in yt.get('shorts', []) if re.fullmatch(r'[A-Za-z0-9_-]{11}', str(i))]
    live = EX.get('live') or {}
    if ids or live.get('url') or yt.get('channel_url'):
        h = ''
        if ids:
            h += '<div class="yt-row">' + ''.join(f'<iframe src="https://www.youtube-nocookie.com/embed/{i}" loading="lazy" title="쇼츠" allow="encrypted-media; picture-in-picture" allowfullscreen></iframe>' for i in ids[:4]) + '</div>'
        links = []
        if live.get('url'):
            links.append(f'<li><a href="{E(live["url"])}" rel="noopener nofollow" target="_blank">{E(live.get("title", "실시간 방송 보러 가기"))}</a></li>')   # 방송이 없을 때 빈 상자가 되지 않게 링크만 둔다
        if yt.get('channel_url'):
            links.append(f'<li><a href="{E(yt["channel_url"])}" rel="noopener nofollow" target="_blank">{E(yt.get("channel_title", "유튜브 채널"))}</a></li>')
        cols.append('<div><h3>영상</h3>' + h + ('<ul>' + ''.join(links) + '</ul>' if links else '') + '</div>')
    if load_games():
        cols.append(f'<div><h3>게임</h3><ul>' + ''.join(f'<li><a href="{BASE}games/{g["slug"]}/">{E(g["title"])}</a></li>' for g in load_games()) + '</ul></div>')
    blogs = [b for b in EX.get('blogs', []) if b.get('url', '').startswith('http')]
    if blogs:
        cols.append('<div><h3>블로그</h3><ul>' + ''.join(f'<li><a href="{E(b["url"])}" rel="noopener nofollow" target="_blank">{E(b.get("name", b["url"]))}</a></li>' for b in blogs) + '</ul></div>')
    cp = EX.get('coupang') or {}
    items = [i for i in cp.get('items', []) if i.get('url', '').startswith('https://link.coupang.com/')]
    if items:
        note = cp.get('notice') or '이 영역은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받을 수 있습니다.'
        cols.append('<div><h3>추천<span class="ad-lb">광고</span></h3><ul>' + ''.join(f'<li><a href="{E(i["url"])}" rel="sponsored nofollow noopener" target="_blank">{E(i.get("name", "쿠팡 상품"))}</a></li>' for i in items[:6]) + f'</ul><p class="ad-nt">{E(note)}</p></div>')
    return f'<section class="sec"><h2>영상 · 게임 · 추천</h2><div class="ex-grid">{"".join(cols)}</div></section>' if cols else ''


def _png(size, rgb):
    """아이콘 PNG 를 파이썬 기본 기능(zlib)만으로 그린다: 색 바탕에 흰 고리와 가운데 점(모양 아이콘)."""
    import zlib, struct
    cx = cy = size / 2; R1, R2, R3 = size * .34, size * .22, size * .09
    rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            d = ((x + .5 - cx) ** 2 + (y + .5 - cy) ** 2) ** .5
            col = (255, 255, 255) if (R2 <= d <= R1 or d <= R3) else rgb
            row += bytes(col)
        rows.append(bytes(row))
    raw = b''.join(rows)
    ck = lambda t, b: struct.pack('>I', len(b)) + t + b + struct.pack('>I', zlib.crc32(t + b) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + ck(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0)) + ck(b'IDAT', zlib.compress(raw, 9)) + ck(b'IEND', b'')


def write_pwa():
    """홈 화면에 추가되는 앱처럼: manifest + 아이콘 + 서비스 워커(오프라인에서도 열림). 서버가 필요 없다."""
    h = ACCENT.lstrip('#'); rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) if len(h) == 6 else (17, 17, 17)
    for sz in (192, 512):
        open(os.path.join(OUT, f'icon-{sz}.png'), 'wb').write(_png(sz, rgb))
    short = S['name'][:12]
    open(os.path.join(OUT, 'manifest.webmanifest'), 'w', encoding='utf-8').write(json.dumps({'name': S['name'], 'short_name': short, 'description': S['tagline'], 'start_url': BASE, 'scope': BASE, 'display': 'standalone', 'background_color': '#ffffff', 'theme_color': ACCENT,
        'icons': [{'src': f'{BASE}icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'}, {'src': f'{BASE}icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'}]}, ensure_ascii=False))
    files = []
    for dp, dn, fn in os.walk(OUT):
        for f in fn:
            rel = os.path.relpath(os.path.join(dp, f), OUT).replace(os.sep, '/')
            if f == 'index.html':
                files.append(BASE + (rel[:-10] if rel != 'index.html' else ''))
            elif f in ('style.css', 'search.json', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png') or rel.endswith(('.svg', '.js', '.json')) and f != 'sw.js':
                files.append(BASE + rel)
    import hashlib
    hm = hashlib.md5()
    for u in sorted(files):   # 내용이 바뀌면 버전이 바뀌어 옛 저장본을 버린다
        rp = os.path.join(OUT, u[len(BASE):] or '', 'index.html') if u.endswith('/') or u == BASE else os.path.join(OUT, u[len(BASE):])
        hm.update(u.encode())
        if os.path.isfile(rp):
            hm.update(open(rp, 'rb').read())
    ver = hm.hexdigest()[:8]
    sw = ('const V="app-%s",A=%s;self.addEventListener("install",function(e){e.waitUntil(caches.open(V).then(function(c){return c.addAll(A)}).then(function(){return self.skipWaiting()}))});'
          'self.addEventListener("activate",function(e){e.waitUntil(caches.keys().then(function(ks){return Promise.all(ks.filter(function(k){return k!==V}).map(function(k){return caches.delete(k)}))}).then(function(){return self.clients.claim()}))});'
          'self.addEventListener("fetch",function(e){if(e.request.method!=="GET")return;e.respondWith(caches.match(e.request,{ignoreSearch:true}).then(function(r){return r||fetch(e.request)}))});') % (ver, json.dumps(files))
    open(os.path.join(OUT, 'sw.js'), 'w', encoding='utf-8').write(sw)


def home(notes, topics, notice=''):
    """첫 화면 — 머리기사 하나를 크게, 나머지 노트는 오른쪽 단, 아래에 「함께 다룬 소식」을 여러 단 목록으로."""
    if not part('info'):   # 정보 부품이 꺼진 서비스(예: 게임 모음)의 첫 화면은 게임 목록
        secs = [('게임', 'games/', 'games', lambda: load_games(), '웹 게임'), ('계산기', 'calc/', 'calc', lambda: kit_data('calc', 'calculators.json'), '숫자를 넣으면 바로 계산'), ('용어 사전', 'glossary/', 'glossary', lambda: kit_data('glossary', 'terms.json'), '돈·생활 용어 풀이'),
                ('글', 'post/', 'posts', lambda: os.path.isdir(os.path.join(HERE, 'posts')), '생활·돈 가이드 글'), ('연재', 'novel/', 'novel', lambda: os.path.isdir(os.path.join(HERE, 'novels')), '연재 소설'), ('웹툰', 'toon/', 'toon', lambda: os.path.isdir(os.path.join(HERE, 'toons')), '웹툰·만화'),
                ('전자책', 'ebook/', 'ebook', lambda: True, '글을 묶은 PDF 전자책'), ('일정', 'schedule/', 'schedule', lambda: True, '날짜별 일정'), ('자주 묻는 질문', 'faq/', 'faq', lambda: True, '질문과 답'), ('링크 모음', 'links/', 'links', lambda: True, '분류별 링크'), ('검색', 'search/', 'search', lambda: True, '사이트 안 검색')] + [(LAB(k, n), u, k, (lambda: True), d) for k, n, u, d in GENERIC]
        gl = ''.join(f'<a href="{BASE}{u}"><span class="lb">{E(n)}</span><h3>{E(n)}</h3><p>{E(d)}</p></a>' for n, u, k, ok, d in secs if part(k, False) and ok())
        mix = ''   # 켜진 키트의 실제 내용을 첫 화면에 모아 보여 준다
        if part('games', False) and load_games():
            mix += '<section class="sec"><h2>게임</h2><div class="gl">' + ''.join(f'<a href="{BASE}games/{g["slug"]}/"><span class="lb">{E(g.get("kind", "게임"))}</span><h3>{E(g["title"])}</h3><p>{E(g.get("intro", g["desc"])[:70])}</p></a>' for g in load_games()) + '</div></section>'
        if part('calc', False) and kit_data('calc', 'calculators.json'):
            mix += '<section class="sec"><h2>계산기</h2><div class="gl">' + ''.join(f'<a href="{BASE}calc/{c["slug"]}/"><span class="lb">계산기</span><h3>{E(c["title"])}</h3><p>{E(c["desc"])}</p></a>' for c in kit_data('calc', 'calculators.json')) + '</div></section>'
        if part('glossary', False) and kit_data('glossary', 'terms.json'):
            ts = kit_data('glossary', 'terms.json')[:6]
            mix += '<section class="sec"><h2>용어</h2><ul class="rp">' + ''.join(f'<li><a href="{BASE}glossary/{re.sub(chr(32), chr(45), t["term"])}/"><b>{E(t["term"])}</b></a> — {E(t["short"])}</li>' for t in ts) + f'</ul><p class="sub"><a href="{BASE}glossary/">용어 전체 보기</a></p></section>'
        if part('schedule', False) and kit_data('schedule', 'events.json'):   # 다가오는 일정 3개(찍은 날 기준)
            today_s = datetime.date.today().isoformat()
            ev = [e for e in sorted(kit_data('schedule', 'events.json'), key=lambda x: x['date']) if e['date'] >= today_s][:3]
            if ev:
                mix += '<section class="sec"><h2>다가오는 일정</h2>' + ''.join(f'<div class="tp"><span class="lb">{E(e["date"])}</span><b>{E(e["title"])}</b><span class="ln">{E(e.get("note", ""))}</span></div>' for e in ev) + f'<p class="sub"><a href="{BASE}schedule/">일정 전체 보기</a></p></section>'
        if part('faq', False) and kit_data('faq', 'faq.json'):
            mix += '<section class="sec"><h2>자주 묻는 질문</h2><ul class="rp">' + ''.join(f'<li><a href="{BASE}faq/">{E(x["q"])}</a></li>' for x in kit_data('faq', 'faq.json')[:3]) + '</ul></section>'
        if part('links', False) and kit_data('links', 'links.json'):
            mix += '<section class="sec"><h2>링크</h2>' + ''.join(f'<div class="tp"><span class="lb">{E(g["category"])}</span>' + ''.join(f'<span class="ln"><a href="{E(i["url"])}" rel="noopener nofollow" target="_blank">{E(i["name"])}</a> — {E(i.get("desc", ""))}</span>' for i in g['items'][:3]) + '</div>' for g in kit_data('links', 'links.json')[:2]) + f'<p class="sub"><a href="{BASE}links/">링크 모음 보기</a></p></section>'
        if part('posts', False) and os.path.isdir(os.path.join(HERE, 'posts')):
            ps = sorted(glob.glob(os.path.join(HERE, 'posts', '*.md')))[-3:]
            if ps:
                mix += '<section class="sec"><h2>글</h2><ul class="rp">' + ''.join(f'<li><a href="{BASE}post/{os.path.splitext(os.path.basename(f))[0]}/">{E(first_h1(open(f, encoding="utf-8").read(), os.path.basename(f)))}</a></li>' for f in ps) + '</ul></section>'
        covered = {'게임': '게임', '계산기': '계산기', '용어 사전': '용어', '글': '글', '일정': '다가오는 일정', '자주 묻는 질문': '자주 묻는 질문', '링크 모음': '링크'}   # 첫 화면에 내용이 이미 나온 키트는 카드에서 뺀다
        gl = ''.join(f'<a href="{BASE}{u}"><span class="lb">{E(n)}</span><h3>{E(n)}</h3><p>{E(d)}</p></a>' for n, u, k, ok, d in secs if part(k, False) and ok() and f'<h2>{covered.get(n, chr(0))}</h2>' not in mix)
        return page('', S.get('home_title') or S['name'], S.get('home_desc') or S['tagline'], f'<div class="page"><h2 style="font:800 28px/1.3 var(--serif);margin:0 0 10px">{E(S["name"])}</h2><p>{E(S["tagline"])}</p><div class="gl">{gl}</div></div>' + mix + extras_html())
    if notes:
        n = notes[0]
        lead = (f'<div class="lead"><span class="lb">오늘의 확인 노트</span><a href="{BASE}n/{n["id"]}/"><h2>{E(n["title"])}</h2></a>'
                f'<p>{E(n["summary"])}</p><div class="meta"><span class="v {VERDICTS[n["verdict"]]}">{E(n["verdict"])}</span> &nbsp;{E(n["date"])}</div></div>')
        side = ''.join(f'<div class="it"><div class="meta"><span class="v {VERDICTS[m["verdict"]]}">{E(m["verdict"])}</span> &nbsp;{E(m["date"])}</div>'
                       f'<a href="{BASE}n/{m["id"]}/"><h3>{E(m["title"])}</h3></a></div>' for m in notes[1:6])
        front = f'<section class="front">{lead}<aside class="side">{side}</aside></section>'
    else:
        front = '<p class="empty">오늘의 확인 노트를 준비 중입니다.</p>'
    tp = ''.join(f'<div class="tp"><span class="lb">{t["media_count"]}개 매체</span><b>{E(t["title"])}</b>'
                 + ''.join(f'<span class="ln"><a href="{E(i["link"])}" rel="noopener nofollow">{E(i["source"])}</a> {E(i["title"][:46])}</span>' for i in t['items'][:4]) + '</div>' for t in topics[:12])
    note = f' {E(notice)}' if notice else ''
    body = (front + f'<section class="sec"><h2>여러 매체가 함께 다룬 소식</h2><p class="sub">제목·매체·링크만 모았습니다. 이 가운데 제도·숫자·날짜가 걸린 소식을 골라 확인 노트로 씁니다.{note}</p>'
            f'<div class="cols">{tp}</div></section>') + extras_html()
    return page('', S.get('home_title') or f'{S["name"]} — {S["tagline"]}', S.get('home_desc') or S['tagline'], body)   # 첫 화면 제목·설명은 따로 정할 수 있다(검색 결과에 그대로 보이는 문구)


DESC = {'how': '뉴스의 제도·숫자·날짜를 공식 자료와 맞춰 보는 방법과 판정 기준', 'about': '이 사이트가 하는 일과 만드는 방식', 'contact': '문의와 정정 요청 방법', 'privacy': '이 사이트의 개인정보 처리 방침'}


def static_pages():
    how = ('<h1>확인하는 방법</h1><p>뉴스에서 본 제도·숫자·날짜를 공식 기관 자료와 맞춰 보고 세 가지로 판정합니다.</p>'
           '<ul><li><span class="v ok">확인됨</span> 공식 자료에서 같은 내용을 직접 찾았습니다.</li><li><span class="v part">일부만 확인됨</span> 일부만 찾았고 나머지는 찾지 못했습니다.</li>'
           '<li><span class="v no">아직 확인 안 됨</span> 공식 자료에서 찾지 못했습니다. 틀렸다는 뜻이 아닙니다.</li></ul>'
           '<p>확인한 사실마다 출처 링크를 붙입니다. 찾지 못한 것은 「아직 확인 안 된 것」 칸에 따로 적고 지어서 채우지 않습니다. 연예인·정치인·사건 당사자 이야기는 다루지 않습니다.</p>')
    about = '<h1>소개</h1><p>' + E(S.get('about') or f'「{S["name"]}」은 여러 매체가 함께 다룬 소식 가운데 제도·숫자·날짜를 공식 자료와 맞춰 보는 작은 정보 사이트입니다. 수집과 빌드는 자동으로 돌고, 확인 노트는 사람이 살피는 흐름 안에서 에이전트가 씁니다.') + '</p>'
    contact = f'<h1>문의</h1><p>{E(S["contact"])}</p><p>정정을 요청할 때는 어느 노트의 어느 문장인지와 근거가 되는 공식 자료 주소를 함께 알려 주세요. 확인한 뒤 노트를 고치고 바뀐 내용을 노트에 적습니다.</p>'
    priv = ('<h1>개인정보 처리방침</h1><p>이 사이트는 회원가입·댓글·결제를 받지 않고 방문자의 개인정보를 직접 수집하지 않습니다. '
            '호스팅 서비스(GitHub Pages)가 접속 기록을 남길 수 있으며 이는 해당 서비스의 방침을 따릅니다.</p>')
    for path, t, b in (*((('how', '확인하는 방법', how),) if part('info') else ()), ('about', '소개', about), ('contact', '문의', contact), ('privacy', '개인정보 처리방침', priv)):
        page(path, f'{t} — {S["name"]}', DESC.get(path, t), f'<div class="page">{b}</div>')
    return (['how/'] if part('info') else []) + ['about/', 'contact/', 'privacy/']


def feed(notes):
    if NOURL:
        return
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    items = ''.join(f'<item><title>{E(n["title"])}</title><link>{URL}/n/{n["id"]}/</link><guid>{URL}/n/{n["id"]}/</guid><description>{E(n["verdict"] + " — " + n["summary"])}</description></item>' for n in notes[:30])
    open(os.path.join(OUT, 'feed.xml'), 'w', encoding='utf-8').write(
        f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{E(S["name"])}</title><link>{URL}/</link><description>{E(S["tagline"])}</description><lastBuildDate>{now:%a, %d %b %Y %H:%M:%S +0900}</lastBuildDate>{items}</channel></rss>')


def main():
    with_example = '--example' in sys.argv
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    open(os.path.join(OUT, 'style.css'), 'w', encoding='utf-8').write(CSS)
    open(os.path.join(OUT, '.nojekyll'), 'w').write('')
    open(os.path.join(OUT, '.base'), 'w', encoding='utf-8').write(BASE)   # audit 가 설정과 다른 주소로 찍힌 docs 를 알아보게
    tp = os.path.join(HERE, 'data', 'topics.json')
    topics = json.load(open(tp, encoding='utf-8'))['topics'] if os.path.exists(tp) else []
    notes = load_notes(with_example) if part('info') else []   # info 부품이 꺼져 있으면 뉴스·노트는 만들지 않는다
    if not part('info'):
        topics = []
    topics, notice = filter_topics(topics)
    urls = [home(notes, topics, notice)] + [f'{URL}/{p}' for p in static_pages()] + [note_page(n) for n in notes] + game_pages() + issue_pages(notes) + content_pages() + calc_pages() + glossary_pages() + search_page() + ebook_pages() + kits_page() + _kp.pages(sys.modules[__name__]) + status_page(notes)
    if not DEMO:
        feed(notes)
    write_search_index()
    if part('pwa', False):
        write_pwa()
    if DEMO:
        print(f'데모 쪽 {len(urls)}개 -> ' + (os.path.relpath(OUT, HERE) if OUT.startswith(HERE) else os.path.basename(OUT))); return
    if not NOURL:   # 공개 주소가 정해졌을 때만 사이트맵을 만든다
        open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8').write(
            '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{u}</loc></url>' for u in urls) + '</urlset>')
    open(os.path.join(OUT, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\n' + ('' if NOURL else f'Sitemap: {URL}/sitemap.xml\n'))
    if NOURL:
        print('안내: site.json 의 url 이 기본값이라 canonical·RSS·사이트맵을 만들지 않았습니다. 공개 주소가 정해지면 url 을 넣고 다시 빌드하세요.')
    print(f'노트 {len(notes)}건, 주제 {len(topics)}건, 쪽 {len(urls)}개 -> docs/')


if __name__ == '__main__':
    main()
