# -*- coding: utf-8 -*-
"""3단계 빌드: data/topics.json 과 notes/*.json 으로 docs/ (정적 화면)를 만든다.
첫 화면 · 확인 노트 쪽 · 고정 쪽(확인하는 방법·소개·문의·개인정보) · feed.xml · sitemap.xml.
「예시」 노트(example:true)는 화면 틀 시험용이라 --example 을 줄 때만 넣는다. 공개본에는 올리지 않는다.
실행: python build.py [--example]"""
import json, os, sys, glob, html, shutil, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'docs')
S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
_local = os.path.join(HERE, 'site.local.json')   # 내 컴퓨터에서만 쓰는 값(저장소에 올리지 않음)이 있으면 덮어쓴다
if os.path.exists(_local):
    S.update(json.load(open(_local, encoding='utf-8')))
S['url'] = os.environ.get('SITE_URL', S['url']).rstrip('/')   # 자동 갱신(GitHub Actions)에서는 환경변수로 주소를 넣는다
BASE, URL = S['base'], S['url']
E = html.escape
VERDICTS = {'확인됨': 'ok', '일부만 확인됨': 'part', '아직 확인 안 됨': 'no'}

CSS = """:root{--bg:#fff;--fg:#1a1d23;--mu:#5b6270;--bd:#e3e6ec;--card:#f6f7f9;--ok:#157a43;--part:#a35f00;--no:#b3261e;--pri:#2457c5}
@media(prefers-color-scheme:dark){:root{--bg:#14161a;--fg:#eceef2;--mu:#a3a9b5;--bd:#2c3038;--card:#1c1f25;--ok:#5fcf8b;--part:#f0b04a;--no:#ff8a80;--pri:#8ab0ff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.7 system-ui,'Malgun Gothic',sans-serif}
a{color:var(--pri)}header,main,footer{max-width:720px;margin:0 auto;padding:0 16px}
header{padding-top:14px;padding-bottom:10px;border-bottom:1px solid var(--bd)}header b{font-size:20px}header a{text-decoration:none;color:inherit}
nav{display:flex;gap:14px;flex-wrap:wrap;font-size:15px;margin-top:4px}nav a{color:var(--mu)}
h1{font-size:24px;line-height:1.4;margin:22px 0 8px}h2{font-size:19px;margin:28px 0 8px}
.card{display:block;background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:14px 16px;margin:12px 0;text-decoration:none;color:inherit}
.card b{display:block;margin:4px 0}.card small{color:var(--mu)}
.v{display:inline-block;font-size:14px;font-weight:700;border-radius:999px;padding:1px 10px;border:1.5px solid}
.v.ok{color:var(--ok)}.v.part{color:var(--part)}.v.no{color:var(--no)}
ul{padding-left:20px}li{margin:6px 0}.mu{color:var(--mu);font-size:15px}.ex{background:#fff3cd;color:#664d03;padding:2px 8px;border-radius:6px;font-size:14px}
footer{margin-top:40px;padding-top:14px;padding-bottom:30px;border-top:1px solid var(--bd);color:var(--mu);font-size:14px}footer a{margin-right:12px}"""


def page(path, title, desc, body, noindex=False):
    """HTML 쪽 하나를 docs/<path>/index.html 로 쓴다."""
    d = os.path.join(OUT, path)
    os.makedirs(d, exist_ok=True)
    canon = f'{URL}/{path}/' if path else f'{URL}/'
    robots = '<meta name="robots" content="noindex">' if noindex else ''
    doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{canon}">{robots}
<link rel="alternate" type="application/rss+xml" title="{E(S['name'])}" href="{BASE}feed.xml"><link rel="stylesheet" href="{BASE}style.css"></head><body>
<header><a href="{BASE}"><b>{E(S['name'])}</b></a><div class="mu">{E(S['tagline'])}</div>
<nav><a href="{BASE}">오늘</a><a href="{BASE}how/">확인하는 방법</a><a href="{BASE}about/">소개</a><a href="{BASE}contact/">문의</a></nav></header>
<main>{body}</main>
<footer><a href="{BASE}privacy/">개인정보 처리방침</a><a href="{BASE}feed.xml">RSS</a><p>기사 본문은 싣지 않고 제목·매체·시각·링크만 모아 보여 줍니다. 기사의 저작권은 각 매체에 있습니다.</p></footer></body></html>"""
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
    v = VERDICTS[n['verdict']]
    ex = '<p><span class="ex">예시 — 화면 틀 시험용 가짜 노트입니다</span></p>' if n.get('example') else ''
    li = lambda xs: ''.join(f'<li>{E(x)}</li>' for x in xs)
    facts = ''.join(f'<li>{E(f["text"])} <span class="mu">— <a href="{E(f["url"])}" rel="noopener nofollow">{E(f["source"])}</a></span></li>' for f in n.get('facts', []))
    reports = ''.join(f'<li><a href="{E(r["url"])}" rel="noopener nofollow">{E(r["title"])}</a> <span class="mu">{E(r["source"])}</span></li>' for r in n.get('reports', []))
    body = (f'{ex}<p class="mu">{E(n["date"])} 확인 노트</p><h1>{E(n["title"])}</h1><p><b>{E(n["question"])}</b></p>'
            f'<p><span class="v {v}">{E(n["verdict"])}</span></p><p>{E(n["summary"])}</p>'
            f'<h2>확인한 사실</h2><ul>{facts}</ul>'
            + (f'<h2>매체마다 다르게 전한 점</h2><ul>{li(n["differs"])}</ul>' if n.get('differs') else '')
            + (f'<h2>아직 확인 안 된 것</h2><ul>{li(n["unconfirmed"])}</ul>' if n.get('unconfirmed') else '')
            + (f'<h2>관련 기사</h2><ul>{reports}</ul>' if reports else '')
            + f'<p class="mu">확인 시각 {E(n["checked_at"])}</p>')
    return page(f'n/{n["id"]}', f'{n["title"]} — {S["name"]}', n['summary'][:150], body, noindex=bool(n.get('example')))


def home(notes, topics):
    cards = ''.join(f'<a class="card" href="{BASE}n/{n["id"]}/"><small>{E(n["date"])}</small><b>{E(n["title"])}</b><span class="v {VERDICTS[n["verdict"]]}">{E(n["verdict"])}</span></a>' for n in notes[:6])
    cards = cards or '<p class="mu">오늘의 확인 노트를 준비 중입니다.</p>'
    tp = ''.join(f'<div class="card"><small>{t["media_count"]}개 매체가 함께 다룸 · {E(" · ".join(t["media"]))}</small><b>{E(t["title"])}</b>'
                 + ''.join(f'<div class="mu">· <a href="{E(i["link"])}" rel="noopener nofollow">{E(i["source"])}</a> {E(i["title"][:46])}</div>' for i in t['items'][:4]) + '</div>' for t in topics[:8])
    body = f'<h1>오늘의 확인 노트</h1>{cards}<h2>오늘 여러 매체가 함께 다룬 소식</h2><p class="mu">제목·매체·링크만 모았습니다. 이 가운데 제도·숫자·날짜가 걸린 소식을 골라 확인 노트로 씁니다.</p>{tp}'
    return page('', f'{S["name"]} — {S["tagline"]}', S['tagline'], body)


def static_pages():
    how = ('<h1>확인하는 방법</h1><p>뉴스에서 본 제도·숫자·날짜를 공식 기관 자료와 맞춰 보고 세 가지로 판정합니다.</p>'
           '<ul><li><span class="v ok">확인됨</span> 공식 자료에서 같은 내용을 직접 찾았습니다.</li><li><span class="v part">일부만 확인됨</span> 일부만 찾았고 나머지는 찾지 못했습니다.</li>'
           '<li><span class="v no">아직 확인 안 됨</span> 공식 자료에서 찾지 못했습니다. 틀렸다는 뜻이 아닙니다.</li></ul>'
           '<p>확인한 사실마다 출처 링크를 붙입니다. 찾지 못한 것은 「아직 확인 안 된 것」 칸에 따로 적고 지어서 채우지 않습니다. 연예인·정치인·사건 당사자 이야기는 다루지 않습니다.</p>')
    about = ('<h1>소개</h1><p>「한 번 더 확인」은 여러 매체가 함께 다룬 생활·경제 소식 가운데 제도·숫자·날짜를 공식 자료와 맞춰 보는 작은 정보 매거진입니다. '
             '수집과 빌드는 자동으로 돌고, 확인 노트는 사람이 살피는 흐름 안에서 에이전트가 씁니다. 에이전트 여러 개가 역할을 나눠 일하는 과정을 보여 주는 실습 사이트이기도 합니다.</p>')
    contact = f'<h1>문의</h1><p>{E(S["contact"])}</p>'
    priv = ('<h1>개인정보 처리방침</h1><p>이 사이트는 회원가입·댓글·결제를 받지 않고 방문자의 개인정보를 직접 수집하지 않습니다. '
            '호스팅 서비스(GitHub Pages)가 접속 기록을 남길 수 있으며 이는 해당 서비스의 방침을 따릅니다.</p>')
    for path, t, b in (('how', '확인하는 방법', how), ('about', '소개', about), ('contact', '문의', contact), ('privacy', '개인정보 처리방침', priv)):
        page(path, f'{t} — {S["name"]}', t, b)
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
    urls = [home(notes, topics)] + [f'{URL}/{p}' for p in static_pages()] + [note_page(n) for n in notes]
    feed(notes)
    open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{u}</loc></url>' for u in urls) + '</urlset>')
    open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {URL}/sitemap.xml\n')
    print(f'노트 {len(notes)}건, 주제 {len(topics)}건, 쪽 {len(urls)}개 -> docs/')


if __name__ == '__main__':
    main()
