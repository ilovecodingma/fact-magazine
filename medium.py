# -*- coding: utf-8 -*-
"""1장의 템플릿: 미디엄의 발행물 첫 화면과 글 화면을 잰 값 그대로 옮긴 글 사이트. posts/*.md → <OUT_DIR>/index.html, <OUT_DIR>/p/<이름>/index.html, <OUT_DIR>/m.css. 파이썬 기본 기능만 쓴다.
잰 날 2026-11-12, 잰 곳 medium.com/blog(목록)과 그 안의 글 한 편, 가로 1440(머리·발행물 머리·탭)과 1920(카드·글 화면). 숫자는 CSS 의 주석에 적었다.
옮기지 않은 것: 미디엄의 이름·글자 로고·그림·글. 글꼴 sohne 은 값을 치르는 글꼴이라 가까운 고딕으로, 본문 명조는 source-serif 계열로 맞췄다.
글 파일 머리(선택, 제목 줄 바로 아래): 「부제: …」「그림: 주소 | 그림 설명」「태그: 가, 나」「날짜: 2026-11-12」「글쓴이: …」
사용: python medium.py   (OUT_DIR 환경변수가 없으면 site_local/)"""
import hashlib, html, json, os, re, shutil, sys, time, urllib.request
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('OUT_DIR') or os.path.join(HERE, 'site_local')
BASE = os.environ.get('SITE_BASE', '/')
E = html.escape


def site():
    S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
    lp = os.path.join(HERE, 'site.local.json')
    if os.path.exists(lp):
        S.update(json.load(open(lp, encoding='utf-8')))
    return S


CSS = r"""/* 미디엄을 잰 값(2026-11-12). 괄호 안이 원본의 값 */
:root{--ink:#242424;--mu:#6b6b6b;--hair:#f2f2f2;--bg:#fff;--fill:#f9f9f9;--ac:#1a8917;
 --sans:"Pretendard","Helvetica Neue","Apple SD Gothic Neo","Malgun Gothic",Helvetica,Arial,sans-serif;
 --serif:"Source Serif 4","Source Serif Pro","Noto Serif KR","Nanum Myeongjo","Batang",Georgia,serif}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}button{font:inherit;cursor:pointer;background:none;border:0;padding:0;color:inherit}
svg{display:block}
/* 머리: 높이 57, 아래 줄 1px #f2f2f2, 좌우 24 */
.top{height:57px;border-bottom:1px solid var(--hair);display:flex;align-items:center;padding:0 24px;position:sticky;top:0;background:var(--bg);z-index:5}
.logo{font-family:var(--serif);font-weight:700;font-size:30px;letter-spacing:-1.6px;line-height:25px;height:25px;min-width:112px;white-space:nowrap}
.find{margin-left:24px;width:240px;height:40px;border-radius:20px;background:var(--fill);display:flex;align-items:center;padding-left:12px;color:var(--mu)}
.find input{border:0;background:none;outline:0;font:14px/20px var(--sans);color:var(--ink);padding:10px 20px 10px 8px;width:204px}
.top .sp{flex:1}
.write{display:flex;align-items:center;gap:8px;font-size:14px;line-height:20px;color:var(--mu);margin-right:24px}
.pill{height:32px;border-radius:99px;background:#191919;color:#fff;font-size:13px;line-height:20px;padding:5px 12px;border:1px solid #191919}
.signin{font-size:14px;color:var(--mu);margin:0 0 0 16px}
.me{width:32px;height:32px;border-radius:50%;background:var(--hair);margin-left:56px}
/* 발행물 머리: 안쪽 폭 1192(1440 에서 좌우 124), 로고 80x80 둥글기 2, 이름 32/38 500, 따르는 사람 14/20 #6b6b6b */
.in{max-width:1240px;margin:0 auto;padding:0 24px}
.pub{border-bottom:1px solid var(--hair)}
.pub-h{display:flex;gap:20px;padding:32px 0 0}
.pub-logo{width:80px;height:80px;border-radius:2px;background:#000;color:#fff;font:700 44px/80px var(--serif);text-align:center;letter-spacing:-2px;flex:none;overflow:hidden}
.pub-h h1{margin:2px 0 0;font-size:32px;line-height:38px;font-weight:500;letter-spacing:-.448px}
.pub-h p{margin:16px 0 0;font-size:14px;line-height:20px;color:var(--mu)}
.pub-tabs{display:flex;gap:32px;margin-top:33px}
.pub-tabs a{font-size:14px;line-height:20px;color:var(--mu);padding-bottom:16px;border-bottom:1px solid transparent}
.pub-tabs a.on,.pub-tabs a:hover{color:var(--ink);border-bottom-color:var(--ink)}
/* 대표 글: 그림 653x327 둥글기 2, 그림과 글 사이 20, 제목 32/38 500, 부제 16/20, 줄 13/20 */
.hero{display:grid;grid-template-columns:minmax(0,653fr) minmax(0,519fr);gap:20px;margin-top:32px}
.cover{display:block;width:100%;aspect-ratio:653/327;border-radius:2px;object-fit:cover;background:var(--hair)}
.hero h2{margin:0;font-size:32px;line-height:38px;font-weight:500;letter-spacing:-.448px}
.hero h3{margin:10px 0 0;font-size:16px;line-height:20px;font-weight:400}
.meta{margin-top:14px;font-size:13px;line-height:20px;color:var(--mu);display:flex;align-items:center;gap:8px}
.meta i{width:20px;height:20px;border-radius:50%;background:var(--hair);font-style:normal;display:inline-grid;place-items:center;font-size:11px;color:var(--ink)}
/* 카드 3열: 폭 381 사이 24, 그림 381x191, 제목 20/24 500(그림 아래 15), 설명 16/20(제목 아래 10), 대표 글과 사이 48 */
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:48px 24px;margin:48px 0 64px}
.card .cover{aspect-ratio:381/191}
.card h2{margin:15px 0 0;font-size:20px;line-height:24px;font-weight:500}
.card h3{margin:10px 0 0;font-size:16px;line-height:20px;font-weight:400;color:var(--ink)}
/* 글 화면: 폭 680, 태그 알약 높이 28 글자 16, 제목 42/52 700 자간 -0.462, 부제 22/28 #6b6b6b(제목 아래 9) */
.post{max-width:728px;margin:0 auto;padding:32px 24px 0}
.tags{display:flex;flex-wrap:wrap;gap:8px}
.tags a{height:28px;line-height:20px;font-size:14px;padding:4px 12px;border-radius:99px;background:var(--hair)}
.post>h1{margin:12px 0 0;font-size:42px;line-height:52px;font-weight:700;letter-spacing:-.462px}
.post>.sub{margin:9px 0 0;font-size:22px;line-height:28px;font-weight:400;color:var(--mu)}
/* 글쓴이 줄: 얼굴 32 둥글게, 이름 14/20, 읽는 시간 14/20 #6b6b6b, 부제 아래 26 */
.by{display:flex;align-items:center;gap:12px;margin-top:26px;font-size:14px;line-height:20px}
.by i{width:32px;height:32px;border-radius:50%;background:#000;color:#fff;font:700 15px/32px var(--serif);text-align:center;font-style:normal;flex:none}
.by span{color:var(--mu)}
.by .fo{border:1px solid var(--ink);border-radius:99px;font-size:13px;line-height:20px;padding:2px 10px}
/* 단추 띠: 높이 49, 위아래 줄 1px, 안쪽 3px 8px, 글쓴이 줄 아래 32. 왼쪽 박수·응답, 오른쪽 저장·듣기·공유·더 보기(단추 28, 사이 24) */
.bar{margin-top:32px;height:49px;border-top:1px solid var(--hair);border-bottom:1px solid var(--hair);padding:3px 8px;display:flex;align-items:center;color:var(--mu);font-size:13px;line-height:20px}
.bar button{display:flex;align-items:center;gap:4px;height:28px;color:var(--mu)}
.bar button:hover,.bar button.on{color:var(--ink)}
.bar .l{display:flex;gap:24px}.bar .r{display:flex;gap:24px;margin-left:auto}
/* 본문: 명조 20/32 자간 -0.06, 문단 사이 약 34(원본: 위 42.8 아래 -9.2), 그림 폭 680 위 56, 그림 설명 14/20 가운데 위 10, 소제목 24/30 600 */
.body{font-family:var(--serif);font-size:20px;line-height:32px;letter-spacing:-.06px;word-break:keep-all}
.body p{margin:34px 0 0}
.body h2{font-family:var(--sans);margin:52px 0 0;font-size:24px;line-height:30px;font-weight:600;letter-spacing:-.384px}
.body h2+p{margin-top:14px}
.body h3{font-family:var(--sans);margin:40px 0 0;font-size:20px;line-height:24px;font-weight:600}
.body a{text-decoration:underline}
.body b,.body strong{font-weight:700}
.body ul,.body ol{margin:34px 0 0;padding-left:30px}.body li{margin-top:14px;padding-left:0}
.body blockquote{margin:34px 0 0 -20px;padding-left:23px;border-left:3px solid var(--ink);font-style:italic}
.body figure{margin:56px 0 0}.body figure img{display:block;width:100%;border-radius:0}
.body figcaption{margin-top:10px;font:14px/20px var(--sans);color:var(--mu);text-align:center}
.body table{font:16px/24px var(--sans);border-collapse:collapse;width:100%;margin-top:34px}.body td,.body th{border-bottom:1px solid var(--hair);padding:10px 8px;text-align:left;vertical-align:top}
.body tr:first-child td{font-weight:600;border-bottom-color:var(--ink)}
/* 글 끝: 태그, 단추 띠, 글쓴이 상자(바탕 #f9f9f9, 얼굴 48, 이름 20/24 500, 따르기 단추 폭 240), 발행물 줄 */
.end{max-width:728px;margin:0 auto;padding:48px 24px 0}
.end .bar{border:0;margin-top:24px;padding:0}
.who{margin-top:24px;background:var(--fill);border-radius:4px;padding:32px 24px;text-align:center}
.who i{display:block;width:48px;height:48px;border-radius:50%;background:#000;color:#fff;font:700 22px/48px var(--serif);margin:0 auto;font-style:normal}
.who h2{margin:16px 0 0;font-size:20px;line-height:24px;font-weight:500}
.who p{margin:8px 0 0;font-size:14px;line-height:20px;color:var(--mu)}
.who button{margin-top:20px;width:240px;height:38px;border-radius:99px;background:#191919;color:#fff;font-size:14px}
.from{display:flex;gap:16px;margin:40px 0 0;padding-bottom:48px;border-bottom:1px solid var(--hair)}
.from .pub-logo{width:48px;height:48px;font-size:26px;line-height:48px}
.from h2{margin:0;font-size:20px;line-height:24px;font-weight:500}.from p{margin:6px 0 0;font-size:14px;line-height:20px;color:var(--mu)}
.from .fo{margin-left:auto;align-self:flex-start;border:1px solid var(--ink);border-radius:99px;font-size:14px;line-height:20px;padding:7px 16px}
.more{max-width:1240px;margin:0 auto;padding:48px 24px 0}.more>h2{font-size:20px;line-height:24px;font-weight:500;margin:0}
.more .cards{margin-top:32px}
.foot{border-top:1px solid var(--hair);margin-top:32px;padding:24px;font-size:13px;line-height:20px;color:var(--mu);display:flex;gap:16px;flex-wrap:wrap;justify-content:center}
@media(max-width:903px){.hero{grid-template-columns:1fr}.cards{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:551px){
 .find,.write{display:none}.me{margin-left:16px}.top{padding:0 16px}.in{padding:0 16px}
 .pub-logo{width:48px;height:48px;font-size:26px;line-height:48px}.pub-h{gap:12px;padding-top:24px}.pub-h h1{font-size:22px;line-height:28px}.pub-h p{margin-top:6px}
 .cards{grid-template-columns:1fr;gap:32px}.hero h2{font-size:24px;line-height:30px}
 .post{padding:24px 16px 0}.post>h1{font-size:32px;line-height:38px}.post>.sub{font-size:20px;line-height:24px}
 .body{font-size:18px;line-height:28px}.body h2{font-size:20px;line-height:24px}.body blockquote{margin-left:0}.end{padding:32px 16px 0}.who button{width:100%}}
"""

IC = {
    'find': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7"/><path d="m16.5 16.5 4 4" stroke-linecap="round"/></svg>',
    'write': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1"><path d="M14 4H5a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-9" stroke-linecap="round"/><path d="m11.5 12.5 8.5-9 1 1-8.5 9-2 1z"/></svg>',
    'clap': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"><path d="M9.2 12.6 6.4 9.8a1.2 1.2 0 0 1 1.7-1.7l4.3 4.3M8.1 8.1 7 7a1.2 1.2 0 0 1 1.7-1.7l4.6 4.6M9.6 6.2a1.2 1.2 0 0 1 1.7-1.7l5.5 5.5c2.2 2.2 2.6 5.6.4 7.8s-5.9 2.3-8.2 0l-4.3-4.3a1.2 1.2 0 0 1 1.7-1.7l2.4 2.4"/><path d="M13.5 3v2M16.5 3.6l-1 1.7M10.6 3.6l1 1.7" stroke-linecap="round"/></svg>',
    'talk': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1"><path d="M12 4.5c4.7 0 8 3 8 6.8s-3.3 6.8-8 6.8c-.6 0-1.2-.05-1.8-.15L6 20v-3.3c-1.3-1.2-2-2.9-2-5.4 0-3.800 3.300-6.800 8-6.800z" stroke-linejoin="round"/></svg>',
    'save': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1"><path d="M7 5.5a1 1 0 0 1 1-1h8a1 1 0 0 1 1 1V19l-5-3.5L7 19z" stroke-linejoin="round"/></svg>',
    'play': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1"><circle cx="12" cy="12" r="8"/><path d="M10.5 9v6l5-3z" fill="currentColor" stroke="none"/></svg>',
    'share': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"><path d="M12 15V4m0 0L8.5 7.5M12 4l3.5 3.5M6 12v6.5a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V12"/></svg>',
    'more': '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><circle cx="6" cy="12" r="1.3"/><circle cx="12" cy="12" r="1.3"/><circle cx="18" cy="12" r="1.3"/></svg>',
}


def inline(t):
    t = E(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', r'<a href="\2" rel="noopener nofollow">\1</a>', t)
    return t


def md(text):
    out, para, lst, tbl, quote = [], [], [], [], []

    def flush():
        nonlocal para, lst, tbl, quote
        if para:
            out.append('<p>' + inline(' '.join(para)) + '</p>'); para = []
        if quote:
            out.append('<blockquote>' + inline(' '.join(quote)) + '</blockquote>'); quote = []
        if lst:
            tag = lst[0][0]; out.append(f'<{tag}>' + ''.join(f'<li>{inline(x[1])}</li>' for x in lst) + f'</{tag}>'); lst = []
        if tbl:
            rows = [r for r in tbl if not re.fullmatch(r'\|[\s:|-]+\|?', r.strip())]
            out.append('<table>' + ''.join('<tr>' + ''.join(f'<td>{inline(c.strip())}</td>' for c in r.strip().strip('|').split('|')) + '</tr>' for r in rows) + '</table>'); tbl = []
    for line in text.splitlines():
        s = line.rstrip()
        if not s.strip():
            flush(); continue
        m = re.match(r'!\[([^\]]*)\]\(([^)\s]+)\)', s.strip())
        if m:
            flush(); out.append(f'<figure><img src="{E(m.group(2))}" alt="{E(m.group(1))}" loading="lazy">' + (f'<figcaption>{E(m.group(1))}</figcaption>' if m.group(1) else '') + '</figure>'); continue
        m = re.match(r'(#{2,3}) (.+)', s)
        if m:
            flush(); out.append(f'<h{len(m.group(1))}>{inline(m.group(2))}</h{len(m.group(1))}>'); continue
        if s.startswith('> '):
            if para or lst or tbl: flush()
            quote.append(s[2:]); continue
        if s.startswith('|'):
            if para or lst or quote: flush()
            tbl.append(s); continue
        m = re.match(r'(?:- |\* )(.+)', s)
        if m:
            if para or tbl or quote: flush()
            lst.append(('ul', m.group(1))); continue
        m = re.match(r'\d+\. (.+)', s)
        if m:
            if para or tbl or quote: flush()
            lst.append(('ol', m.group(1))); continue
        if lst or tbl or quote: flush()
        para.append(s.strip())
    flush()
    return '\n'.join(out)


def load_posts():
    P = []; pdir = os.path.join(HERE, 'posts')
    for f in sorted(os.listdir(pdir)) if os.path.isdir(pdir) else []:
        if not f.endswith('.md') or f.startswith('_'):
            continue
        fp = os.path.join(pdir, f); L = open(fp, encoding='utf-8').read().splitlines()
        title = next((x[2:].strip() for x in L if x.startswith('# ')), f[:-3]); i = next((k for k, x in enumerate(L) if x.startswith('# ')), -1) + 1
        meta = {}
        while i < len(L) and (not L[i].strip() or re.match(r'(부제|그림|태그|꼬리표|날짜|글쓴이)\s*:', L[i])):
            m = re.match(r'(부제|그림|태그|꼬리표|날짜|글쓴이)\s*:\s*(.*)', L[i])
            if m:
                meta[m.group(1)] = m.group(2).strip()
            i += 1
        body = '\n'.join(L[i:]); plain = re.sub(r'[#>*|\[\]()!-]', ' ', body); first = next((x.strip() for x in body.splitlines() if x.strip() and not x.startswith(('#', '|', '!', '>', '-'))), '')
        img, cap = (meta.get('그림', '').split('|') + [''])[:2] if meta.get('그림') else ('', '')
        P.append(dict(slug=f[:-3], title=title, sub=meta.get('부제') or (first[:110] + ('…' if len(first) > 110 else '')), has_sub=bool(meta.get('부제')), img=img.strip(), cap=cap.strip(),
                      tags=[t.strip() for t in (meta.get('태그') or meta.get('꼬리표') or '').split(',') if t.strip()], date=meta.get('날짜') or time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime(fp))),
                      by=meta.get('글쓴이', ''), mins=max(1, round(len(re.sub(r'\s+', '', plain)) / 500)), html=md(body)))
    P.sort(key=lambda p: p['date'], reverse=True)
    return P


COVERS = os.path.join(HERE, 'posts', '_cover')


def photo(p):
    """그림을 정하지 않은 글에 사진 한 장을 붙인다: 글마다 늘 같은 사진(이름으로 고름)을 한 번 받아 posts/_cover/ 에 두고, 찍을 때 사이트 안으로 복사한다.
    사진은 Lorem Picsum(picsum.photos)이 내주는 Unsplash 의 무료 사진이다. 인터넷이 안 되면 색 띠로 남는다."""
    fp = os.path.join(COVERS, p['slug'] + '.jpg')
    if not os.path.exists(fp) and os.environ.get('NO_PHOTO') != '1':
        try:
            os.makedirs(COVERS, exist_ok=True); seed = hashlib.md5(p['slug'].encode()).hexdigest()[:10]
            r = urllib.request.urlopen(urllib.request.Request(f'https://picsum.photos/seed/{seed}/1306/654', headers={'User-Agent': 'Mozilla/5.0'}), timeout=15)
            b = r.read()
            if len(b) > 5000:
                open(fp, 'wb').write(b)
                log = os.path.join(COVERS, '_사진출처.json'); L = json.load(open(log, encoding='utf-8')) if os.path.exists(log) else {}
                L[p['slug'] + '.jpg'] = dict(q='(낱말 없이 저절로 고른 사진)', title='', source='Lorem Picsum (picsum.photos) — Unsplash 의 무료 사진', license='Unsplash License', page=f'https://picsum.photos/seed/{seed}/1306/654', by='')
                json.dump(L, open(log, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        except Exception:
            pass
    if not os.path.exists(fp):
        return ''
    os.makedirs(os.path.join(OUT, 'cover'), exist_ok=True); shutil.copy2(fp, os.path.join(OUT, 'cover', p['slug'] + '.jpg'))
    return BASE + 'cover/' + p['slug'] + '.jpg'


def cover(p, cls='cover'):
    if not p['img']:
        p['img'] = photo(p)
    if p['img']:
        return f'<img class="{cls}" src="{E(p["img"])}" alt="" loading="lazy">'
    h = int(hashlib.md5(p['slug'].encode()).hexdigest()[:6], 16); a, b = h % 360, (h // 7) % 360
    return f'<div class="{cls}" style="background:linear-gradient(135deg,hsl({a} 70% 78%),hsl({b} 75% 62%))"></div>'


def shell(S, title, desc, body):
    name = S.get('name') or '내 사이트'; ac = S.get('accent')
    style = f'<style>:root{{--ac:{E(ac)}}}.pill,.who button{{background:{E(ac)};border-color:{E(ac)}}}.pub-logo,.by i,.who i{{background:{E(ac)}}}</style>' if ac else ''
    return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)}</title><meta name="description" content="{E(desc)}">'
            f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,700&display=swap"><link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">'
            f'<link rel="stylesheet" href="{BASE}m.css">{style}</head><body>'
            f'<header class="top"><a class="logo" href="{BASE}">{E(name)}</a><label class="find">{IC["find"]}<input placeholder="찾기" aria-label="찾기"></label><span class="sp"></span>'
            f'<a class="write" href="{BASE}">{IC["write"]}글쓰기</a><a class="pill" href="{BASE}">소식 받기</a><span class="me" aria-hidden="true"></span></header>'
            f'{body}<footer class="foot"><span>{E(name)}</span><span>{E(S.get("tagline", ""))}</span></footer></body></html>')


def meta_line(S, p):
    by = p['by'] or S.get('name') or ''
    return f'<div class="meta"><i>{E(by[:1])}</i><span>{E(by)}</span><span>·</span><span>{E(p["date"])}</span><span>·</span><span>읽는 데 {p["mins"]}분</span></div>'


def card(S, p):
    return f'<a class="card" href="{BASE}p/{E(p["slug"])}/">{cover(p)}<h2>{E(p["title"])}</h2><h3>{E(p["sub"])}</h3>{meta_line(S, p)}</a>'


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True); open(path, 'w', encoding='utf-8').write(text)


def main():
    S = site(); P = load_posts(); name = S.get('name') or '내 사이트'
    cats = [c['name'] for c in (S.get('cats') or []) if isinstance(c, dict) and c.get('name')] or sorted({t for p in P for t in p['tags']})[:5]
    tabs = '<a class="on" href="' + BASE + '">전체</a>' + ''.join(f'<a href="{BASE}">{E(c)}</a>' for c in cats)
    head = (f'<section class="pub"><div class="in"><div class="pub-h"><div class="pub-logo">{E(name[:2])}</div><div><h1>{E(name)}</h1><p>{E(S.get("tagline", ""))} · 글 {len(P)}편</p></div></div><nav class="pub-tabs">{tabs}</nav></div></section>')
    if P:
        h = P[0]
        hero = f'<a class="hero" href="{BASE}p/{E(h["slug"])}/">{cover(h)}<div><h2>{E(h["title"])}</h2><h3>{E(h["sub"])}</h3>{meta_line(S, h)}</div></a>'
        lst = f'<div class="cards">{"".join(card(S, p) for p in P[1:])}</div>' if len(P) > 1 else '<div style="height:64px"></div>'
    else:
        hero, lst = '', '<div style="height:64px"></div>'
    write(os.path.join(OUT, 'index.html'), shell(S, S.get('home_title') or name, S.get('home_desc') or S.get('tagline', ''), head + f'<main class="in">{hero}{lst}</main>'))
    for p in P:
        by = p['by'] or name
        tags = f'<div class="tags">{"".join(f"<a>{E(t)}</a>" for t in p["tags"])}</div>' if p['tags'] else ''
        bar = (f'<div class="bar"><div class="l"><button aria-label="박수">{IC["clap"]}</button><button aria-label="응답">{IC["talk"]}</button></div>'
               f'<div class="r"><button aria-label="저장">{IC["save"]}</button><button aria-label="듣기">{IC["play"]}</button><button aria-label="공유">{IC["share"]}</button><button aria-label="더 보기">{IC["more"]}</button></div></div>')
        if not p['img']:
            p['img'] = photo(p)
        fig = f'<figure><img src="{E(p["img"])}" alt="">' + (f'<figcaption>{E(p["cap"])}</figcaption>' if p['cap'] else '') + '</figure>' if p['img'] else ''
        art = (f'<article class="post">{tags}<h1>{E(p["title"])}</h1>' + (f'<p class="sub">{E(p["sub"])}</p>' if p['has_sub'] else '')
               + f'<div class="by"><i>{E(by[:1])}</i><b style="font-weight:400">{E(by)}</b><button class="fo">따르기</button><span>읽는 데 {p["mins"]}분</span><span>·</span><span>{E(p["date"])}</span></div>{bar}<div class="body">{fig}{p["html"]}</div></article>')
        end = (f'<section class="end">{tags}{bar}<div class="who"><i>{E(by[:1])}</i><h2>글쓴이 {E(by)}</h2><p>{E(S.get("tagline", ""))}</p><button>따르기</button></div>'
               f'<div class="from"><div class="pub-logo">{E(name[:2])}</div><div><h2>{E(name)}에 실린 글</h2><p>글 {len(P)}편</p></div><a class="fo" href="{BASE}">모두 보기</a></div></section>')
        rest = [q for q in P if q['slug'] != p['slug']][:3]
        more = f'<section class="more"><h2>{E(name)}의 다른 글</h2><div class="cards">{"".join(card(S, q) for q in rest)}</div></section>' if rest else ''
        write(os.path.join(OUT, 'p', p['slug'], 'index.html'), shell(S, f'{p["title"]} — {name}', p['sub'], art + end + more))
    write(os.path.join(OUT, 'm.css'), CSS)
    allp = sum(1 for r, _, fs in os.walk(OUT) for f in fs if f == 'index.html')
    print(f'글 {len(P)}편, 페이지 {allp}개(첫 화면 1 · 글 {len(P)} · 소개·문의 같은 고정 페이지 {allp - len(P) - 1}) -> {os.path.relpath(OUT, HERE)}/')
    return 0


if __name__ == '__main__':
    sys.exit(main())
