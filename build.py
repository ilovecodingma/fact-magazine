# -*- coding: utf-8 -*-
"""3단계 빌드: data/topics.json 과 notes/*.json 으로 docs/ (정적 화면)를 만든다.
첫 화면 · 확인 노트 쪽 · 고정 쪽(확인하는 방법·소개·문의·개인정보) · feed.xml · sitemap.xml.
「예시」 노트(example:true)는 화면 틀 시험용이라 --example 을 줄 때만 넣는다. 공개본에는 올리지 않는다.
실행: python build.py [--example]"""
import json, os, sys, glob, html, shutil, datetime
try:
    sys.stdout.reconfigure(encoding='utf-8')   # 윈도우에서 한글 출력이 깨지지 않게
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'docs')
S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
_local = os.path.join(HERE, 'site.local.json')   # 내 컴퓨터에서만 쓰는 값(저장소에 올리지 않음)이 있으면 덮어쓴다
if os.path.exists(_local):
    S.update(json.load(open(_local, encoding='utf-8')))
for _k, _env in (('about', 'SITE_ABOUT'), ('url', 'SITE_URL'), ('name', 'SITE_NAME'), ('tagline', 'SITE_TAGLINE'), ('contact', 'SITE_CONTACT'), ('home_title', 'HOME_TITLE'), ('home_desc', 'HOME_DESC')):
    if os.environ.get(_env):   # 자동 갱신(GitHub Actions)에서는 저장소 변수가 환경변수로 들어와 site.json 값을 덮어쓴다
        S[_k] = os.environ[_env]
S['url'] = S['url'].rstrip('/')
KEYWORDS = [k.strip() for k in (os.environ.get('TOPIC_KEYWORDS') or ','.join(S.get('topic_keywords', []))).split(',') if k.strip()]   # 주제 키워드(런북 6절)
BASE, URL = S['base'], S['url']
E = html.escape
VERDICTS = {'확인됨': 'ok', '일부만 확인됨': 'part', '아직 확인 안 됨': 'no'}

CSS = """:root{--ink:#111;--mu:#595959;--hair:#d4d4d4;--bg:#fff;--ok:#0b5d2f;--part:#8a4b00;--no:#a11a12;--link:#0b3d91;
--serif:'Noto Serif KR','Noto Serif CJK KR','Nanum Myeongjo','Batang',serif;--sans:system-ui,'Malgun Gothic','Apple SD Gothic Neo',sans-serif}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.7 var(--serif)}
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
@media(max-width:900px){.cols{column-count:2}.lead h2{font-size:32px}}
@media(max-width:640px){.logo{font-size:34px}.front{grid-template-columns:1fr;padding-top:18px}.side{border-left:0;padding-left:0;border-top:1px solid var(--ink);padding-top:16px;margin-top:12px}
.lead h2{font-size:27px}.cols{column-count:1;column-rule:0}.art h1{font-size:28px}nav.menu{gap:18px}.wrap{padding:0 16px}}"""


WEEK = '월화수목금토일'


def today_ko():
    """머리 줄에 쓰는 오늘 날짜(한국시간)."""
    d = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    return f'{d.year}년 {d.month}월 {d.day}일 {WEEK[d.weekday()]}요일'


def page(path, title, desc, body, noindex=False):
    """HTML 쪽 하나를 docs/<path>/index.html 로 쓴다. 종합 일간지 첫 화면 같은 머리(제호·괘선·한 줄 메뉴)를 붙인다."""
    d = os.path.join(OUT, path)
    os.makedirs(d, exist_ok=True)
    canon = f'{URL}/{path}/' if path else f'{URL}/'
    robots = '<meta name="robots" content="noindex">' if noindex else ''
    doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{canon}">{robots}
<link rel="alternate" type="application/rss+xml" title="{E(S['name'])}" href="{BASE}feed.xml"><link rel="stylesheet" href="{BASE}style.css"></head><body>
<header class="mast"><div class="wrap"><div class="dateline">{today_ko()} · {E(S['tagline'])}</div>
<a class="logo" href="{BASE}">{E(S['name'])}</a></div></header>
<div class="wrap"><nav class="menu"><a href="{BASE}">오늘</a><a href="{BASE}how/">확인하는 방법</a><a href="{BASE}about/">소개</a><a href="{BASE}contact/">문의</a></nav></div>
<main class="wrap">{body}</main>
<footer><div class="wrap"><a href="{BASE}privacy/">개인정보 처리방침</a><a href="{BASE}feed.xml">RSS</a><p>기사 본문은 싣지 않고 제목·매체·시각·링크만 모아 보여 줍니다. 기사의 저작권은 각 매체에 있습니다.</p></div></footer></body></html>"""
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(doc)
    return canon


def load_notes(with_example):
    notes = []
    for p in sorted(glob.glob(os.path.join(HERE, 'notes', '*.json')), reverse=True):
        n = json.load(open(p, encoding='utf-8'))
        if n.get('example') and not with_example:
            continue
        if n.get('verdict') not in VERDICTS:
            print('판정 값이 이상해 건너뜀:', os.path.basename(p)); continue
        notes.append(n)
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
            + (f'<h2>관련 기사</h2><ul class="rp">{reports}</ul>' if reports else '') + '</article>')
    return page(f'n/{n["id"]}', f'{n["title"]} — {S["name"]}', n['summary'][:150], body, noindex=bool(n.get('example')))


def filter_topics(topics):
    """주제 키워드가 있으면 묶음 제목이나 기사 제목에 키워드가 든 묶음만 남긴다. 0건이면 필터 없이 보여 주고 알린다. (남은 묶음, 안내 글)"""
    if not KEYWORDS:
        return topics, ''
    keep = [t for t in topics if any(k in t['title'] or any(k in i['title'] for i in t['items']) for k in KEYWORDS)]
    if keep:
        return keep, ''
    print('주의: 키워드', KEYWORDS, '에 맞는 묶음이 0건이라 필터 없이 보여 줍니다. 피드(feeds.json)나 키워드를 바꿔 보세요.')
    return topics, '주제 키워드에 맞는 소식이 아직 없어 전체 소식을 보여 줍니다.'


def home(notes, topics, notice=''):
    """첫 화면 — 머리기사 하나를 크게, 나머지 노트는 오른쪽 단, 아래에 「함께 다룬 소식」을 여러 단 목록으로."""
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
            f'<div class="cols">{tp}</div></section>')
    return page('', S.get('home_title') or f'{S["name"]} — {S["tagline"]}', S.get('home_desc') or S['tagline'], body)   # 첫 화면 제목·설명은 따로 정할 수 있다(검색 결과에 그대로 보이는 문구)


def static_pages():
    how = ('<h1>확인하는 방법</h1><p>뉴스에서 본 제도·숫자·날짜를 공식 기관 자료와 맞춰 보고 세 가지로 판정합니다.</p>'
           '<ul><li><span class="v ok">확인됨</span> 공식 자료에서 같은 내용을 직접 찾았습니다.</li><li><span class="v part">일부만 확인됨</span> 일부만 찾았고 나머지는 찾지 못했습니다.</li>'
           '<li><span class="v no">아직 확인 안 됨</span> 공식 자료에서 찾지 못했습니다. 틀렸다는 뜻이 아닙니다.</li></ul>'
           '<p>확인한 사실마다 출처 링크를 붙입니다. 찾지 못한 것은 「아직 확인 안 된 것」 칸에 따로 적고 지어서 채우지 않습니다. 연예인·정치인·사건 당사자 이야기는 다루지 않습니다.</p>')
    about = '<h1>소개</h1><p>' + E(S.get('about') or f'「{S["name"]}」은 여러 매체가 함께 다룬 소식 가운데 제도·숫자·날짜를 공식 자료와 맞춰 보는 작은 정보 사이트입니다. 수집과 빌드는 자동으로 돌고, 확인 노트는 사람이 살피는 흐름 안에서 에이전트가 씁니다.') + '</p>'
    contact = f'<h1>문의</h1><p>{E(S["contact"])}</p>'
    priv = ('<h1>개인정보 처리방침</h1><p>이 사이트는 회원가입·댓글·결제를 받지 않고 방문자의 개인정보를 직접 수집하지 않습니다. '
            '호스팅 서비스(GitHub Pages)가 접속 기록을 남길 수 있으며 이는 해당 서비스의 방침을 따릅니다.</p>')
    for path, t, b in (('how', '확인하는 방법', how), ('about', '소개', about), ('contact', '문의', contact), ('privacy', '개인정보 처리방침', priv)):
        page(path, f'{t} — {S["name"]}', t, f'<div class="page">{b}</div>')
    return ['how/', 'about/', 'contact/', 'privacy/']


def feed(notes):
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
    tp = os.path.join(HERE, 'data', 'topics.json')
    topics = json.load(open(tp, encoding='utf-8'))['topics'] if os.path.exists(tp) else []
    notes = load_notes(with_example)
    topics, notice = filter_topics(topics)
    urls = [home(notes, topics, notice)] + [f'{URL}/{p}' for p in static_pages()] + [note_page(n) for n in notes]
    feed(notes)
    open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{u}</loc></url>' for u in urls) + '</urlset>')
    open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {URL}/sitemap.xml\n')
    print(f'노트 {len(notes)}건, 주제 {len(topics)}건, 쪽 {len(urls)}개 -> docs/')


if __name__ == '__main__':
    main()
