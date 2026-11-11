# -*- coding: utf-8 -*-
"""키트 쪽 만들기(2·3차 키트): 자료 파일 → 쪽. build.py 가 pages(B) 를 불러 쓴다(B = build 모듈).
각 키트는 kits/<이름>/data/ 의 자료 파일 하나를 읽고, parts 가 켜져 있을 때만 쪽을 만든다. 서버 없음.
키트: topics(주제 묶음) today(오늘의 추천) trends(인기 키워드) widget(퍼가기) notice(공지·바뀐 내역) pdf(글 PDF 링크) timeline(타임라인) rank(화제 순위)
      wiki(위키) faq(자주 묻는 질문) schedule(일정) quiz(퀴즈) compare(표 비교) gallery(사진첩) links(링크 모음)"""
import datetime, glob, hashlib, html, json, os, re, shutil, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

E = html.escape
KIT_LINKS = []   # (이름, 주소) — 푸터 「키트」 줄에 나온다


def data(B, kit, name, default=None):
    p = os.path.join(B.KITS_DIR, kit, 'data', name)
    if not os.path.exists(p):
        return default
    return json.load(open(p, encoding='utf-8')) if name.endswith('.json') else open(p, encoding='utf-8').read()


def U(B, u):
    """자료 속 주소: /로 시작하면 사이트 안 주소(BASE 를 붙임), 아니면 그대로."""
    return B.BASE + u[1:] if u.startswith('/') else u


def box(B, label, title, body, desc, path, intro=''):
    return B.page(path, f'{title} — {B.S["name"]}', desc, f'<div class="page"><span class="lb">{E(label)}</span><h1>{E(title)}</h1>{intro}{body}</div>')


# ---------------- 2차 ----------------
def topics(B):
    T = data(B, 'topics', 'topics.json', [])
    if not T:
        return []
    urls, cards = [], ''
    for t in T:
        li = ''.join(f'<div class="tp"><b><a href="{E(U(B, i["url"]))}">{E(i["title"])}</a></b><span class="ln">{E(i.get("desc", ""))}</span></div>' for i in t['items'])
        urls.append(box(B, '주제', t['name'], li, t['intro'][:140], f'topics/{t["key"]}', f'<p class="dek">{E(t["intro"])}</p>'))
        cards += f'<a href="{B.BASE}topics/{t["key"]}/"><span class="lb">주제</span><h3>{E(t["name"])}</h3><p>{E(t["intro"][:90])}</p></a>'
    urls.append(B.page('topics', f'주제별로 보기 — {B.S["name"]}', '주제별 모음', f'<div class="page"><span class="lb">주제</span><h1>주제별로 보기</h1><div class="gl">{cards}</div></div>'))
    KIT_LINKS.append(('주제', 'topics/'))
    return urls


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (kit build)'})
    return urllib.request.urlopen(req, timeout=timeout).read()


def today(B):
    D = data(B, 'today', 'items.json')
    C = data(B, 'today', 'config.json', {'lat': 37.57, 'lon': 126.98, 'place': '서울'})
    if not D:
        return []
    cat, msg = 'mild', '날씨를 불러오지 못해 평소 추천을 보여 드립니다.'
    try:   # 무료·키 없는 날씨 서비스(Open-Meteo). 빌드할 때 한 번만 부른다
        j = json.loads(fetch(f'https://api.open-meteo.com/v1/forecast?latitude={C["lat"]}&longitude={C["lon"]}&current=temperature_2m,precipitation&timezone=Asia%2FSeoul'))
        t, r = j['current']['temperature_2m'], j['current']['precipitation']
        cat = 'rain' if r > 0.1 else ('cold' if t <= 5 else ('hot' if t >= 26 else 'mild'))
        msg = f'{C["place"]} 기준 지금 기온 {t}도{", 비가 오고 있어요" if r > 0.1 else ""}. 날씨 정보: Open-Meteo, 이 쪽을 만든 시각 {datetime.datetime.now():%Y-%m-%d %H:%M}.'
    except Exception:
        pass
    pool = D.get(cat) or D.get('mild') or []
    seed = int(hashlib.md5(str(datetime.date.today()).encode()).hexdigest(), 16)
    pick = [pool[(seed + i * 7) % len(pool)] for i in range(min(3, len(pool)))] if pool else []
    pick = list({p['title']: p for p in pick}.values())
    label = {'rain': '비 오는 날', 'cold': '추운 날', 'hot': '더운 날', 'mild': '무난한 날'}[cat]
    li = ''.join(f'<div class="tp"><b>{E(p["title"])}</b><span class="ln">{E(p.get("desc", ""))}</span></div>' for p in pick)
    KIT_LINKS.append(('오늘의 추천', 'today/'))
    return [box(B, '오늘의 추천', f'오늘의 추천 — {label}', li, f'{label}에 어울리는 것 {len(pick)}가지', 'today', f'<p class="dek">{E(msg)}</p>')]


def trends(B):
    items = []
    try:
        root = ET.fromstring(fetch('https://trends.google.com/trending/rss?geo=KR'))
        ns = {'ht': 'https://trends.google.com/trending/rss'}
        for it in root.iter('item'):
            news = [{'title': (n.findtext('ht:news_item_title', '', ns) or '').strip(), 'url': (n.findtext('ht:news_item_url', '', ns) or '').strip(), 'source': (n.findtext('ht:news_item_source', '', ns) or '').strip()} for n in it.findall('ht:news_item', ns)]
            items.append({'keyword': (it.findtext('title') or '').strip(), 'traffic': (it.findtext('ht:approx_traffic', '', ns) or '').strip(), 'news': [n for n in news if n['url'].startswith('http')][:4]})
        items = [x for x in items if x['keyword']][:20]
        if items:
            os.makedirs(os.path.join(B.HERE, 'data'), exist_ok=True)
            json.dump({'at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), 'items': items}, open(os.path.join(B.HERE, 'data', 'trends_cache.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    except Exception:
        pass
    at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    if not items:   # 못 불러오면 마지막으로 성공한 것
        cp = os.path.join(B.HERE, 'data', 'trends_cache.json')
        if os.path.exists(cp):
            c = json.load(open(cp, encoding='utf-8')); items, at = c['items'], c['at'] + '(마지막으로 불러온 것)'
    # 거르기(기본 켜짐): 내 주제 낱말과 겹치는 것만 남기고, 사건·사고·사람 소식으로 보이는 낱말은 뺀다. 조건은 kits/trends/data/config.json
    cfg = data(B, 'trends', 'config.json', {}) or {}
    topic = [w for w in (cfg.get('topic_words') or B.KEYWORDS) if w]
    block = cfg.get('block_words', ['사고', '사망', '숨진', '구속', '체포', '재판', '열애', '결혼', '이혼', '불륜', '폭행', '피해자', '용의자', '논란', '소환'])
    total = len(items)
    if cfg.get('mode', 'topic_only') == 'topic_only':
        if not topic:
            return [box(B, '인기 키워드', '인기 키워드', '<p>내 주제 낱말이 아직 없어 목록을 보여 주지 않습니다. kits/trends/data/config.json 의 topic_words(또는 site.json 의 topic_keywords)에 내 주제 낱말을 넣으세요. 사람 이름이나 사건 소식이 그대로 나오는 것을 막기 위한 기본 설정입니다.</p>', '인기 키워드', 'trends')]
        items = [x for x in items if any(w in x['keyword'] or any(w in n['title'] for n in x['news']) for w in topic) and not any(b in x['keyword'] or any(b in n['title'] for n in x['news']) for b in block)]
        print(f'  인기 키워드 거르기: {total}개 중 주제 낱말 {topic} 에 맞는 {len(items)}개만 남김')
        if not items:
            return [box(B, '인기 키워드', '오늘의 인기 키워드', f'<p>오늘 구글 트렌드 {total}개 가운데 내 주제 낱말에 맞는 키워드가 없습니다. 주제 낱말을 늘리거나 내일 다시 확인하세요.</p>', '인기 키워드', 'trends')]
    if not items:
        return [box(B, '인기 키워드', '인기 키워드', '<p>이번 빌드에서 구글 트렌드 목록을 불러오지 못했습니다. 다음 빌드에서 다시 시도합니다.</p>', '인기 키워드', 'trends')]
    urls = []
    for n, x in enumerate(items, 1):
        li = ''.join(f'<li><a href="{E(w["url"])}" rel="noopener nofollow" target="_blank">{E(w["title"])}</a> <span class="mu">{E(w["source"])}</span></li>' for w in x['news'])
        urls.append(box(B, '인기 키워드', x['keyword'], f'<h2>관련 보도</h2><ul class="rp">{li or "<li>관련 보도 목록이 없습니다.</li>"}</ul><p class="ad-nt">제목과 링크만 보여 줍니다. 목록은 구글 트렌드 RSS 이며 기사의 저작권은 각 매체에 있습니다.</p>', f'오늘 많이 찾는 검색어 「{x["keyword"]}」 관련 보도 목록', f'trends/{n}', f'<p class="dek">{E(x["traffic"] + " 검색" if x["traffic"] else "")}</p>'))
    lst = ''.join(f'<li><a href="{B.BASE}trends/{n}/"><b>{E(x["keyword"])}</b></a> <span class="mu">{E(x["traffic"])}</span></li>' for n, x in enumerate(items, 1))
    urls.append(box(B, '인기 키워드', '오늘의 인기 키워드', f'<ul class="rp">{lst}</ul>', '구글 트렌드(한국) 급상승 검색어', 'trends', f'<p class="dek">구글 트렌드 RSS 기준 {at}</p>'))
    KIT_LINKS.append(('인기 키워드', 'trends/'))
    return urls


def widget(B):
    """퍼가기 위젯: /embed/ (바깥 쪽에 끼워 넣는 작은 목록, 검색 제외) + /widget/ (끼우는 코드 안내)."""
    notes = [json.load(open(p, encoding='utf-8')) for p in sorted(glob.glob(os.path.join(B.HERE, 'notes', '*.json')), reverse=True)]
    notes = [n for n in notes if not n.get('example')][:5]
    full = (B.URL if not B.NOURL else '') + B.BASE if not B.NOURL else B.BASE
    base_abs = (B.URL + '/') if not B.NOURL else B.BASE
    li = ''.join(f'<li><a href="{base_abs}n/{E(n["id"])}/" target="_blank" rel="noopener">{E(n["title"])}</a> <small>[{E(n["verdict"])}]</small></li>' for n in notes) or '<li>준비 중</li>'
    doc = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="robots" content="noindex"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{{font:14px/1.6 system-ui,"Malgun Gothic",sans-serif;margin:8px;color:#111}}'
           f'h1{{font:800 15px "Noto Serif KR",serif;border-bottom:2px solid #111;margin:0 0 6px;padding-bottom:4px}}ul{{margin:0;padding-left:18px}}a{{color:#0b3d91}}</style></head><body><h1>{E(B.S["name"])} 최근 확인 노트</h1><ul>{li}</ul></body></html>')
    os.makedirs(os.path.join(B.OUT, 'embed'), exist_ok=True)
    open(os.path.join(B.OUT, 'embed', 'index.html'), 'w', encoding='utf-8').write(doc)
    code = f'<iframe src="{base_abs}embed/" width="320" height="260" style="border:1px solid #ccc" loading="lazy" title="{E(B.S["name"])}"></iframe>'
    body = (f'<p>내 블로그나 다른 사이트에 아래 한 줄을 붙여 넣으면 최근 확인 노트 목록이 나옵니다.</p><pre style="white-space:pre-wrap;background:#f4f4f4;padding:12px;font:13px/1.5 monospace">{E(code)}</pre>'
            f'<h2>미리보기</h2><iframe src="{base_abs}embed/" width="320" height="260" style="border:1px solid #ccc" loading="lazy" title="미리보기"></iframe>')
    KIT_LINKS.append(('퍼가기', 'widget/'))
    return [box(B, '퍼가기', '퍼가기 위젯', body, '내 사이트에 붙이는 최근 확인 노트 목록', 'widget')]


def notice_banner(B):
    """첫 화면 위쪽 한 줄 공지(kits/notice/data/notice.md 의 첫 줄). 값이 없으면 빈 글자."""
    if not B.part('notice', False):
        return ''
    t = (data(B, 'notice', 'notice.md', '') or '').strip().splitlines()
    t = t[0].strip() if t else ''
    return f'<div class="notice">{E(t)} <a href="{B.BASE}changes/">바뀐 내역</a></div>' if t else ''


def notice(B):
    C = data(B, 'notice', 'changes.json', [])
    li = ''.join(f'<div class="tp"><span class="lb">{E(c["date"])}</span><b>{E(c["title"])}</b><span class="ln">{E(c.get("body", ""))}</span></div>' for c in sorted(C, key=lambda x: x['date'], reverse=True))
    KIT_LINKS.append(('바뀐 내역', 'changes/'))
    return [box(B, '바뀐 내역', '바뀐 내역', li or '<p>아직 적은 내역이 없습니다.</p>', '사이트에서 바뀐 내용을 날짜순으로 적습니다', 'changes')]


# ---------------- 3차 ----------------
def timeline(B):
    T = sorted(data(B, 'timeline', 'timeline.json', []), key=lambda x: x['date'])
    if not T:
        return []
    li = ''.join(f'<div class="tp"><span class="lb">{E(t["date"])}</span><b>{E(t["title"])}</b><span class="ln" style="font-size:15px;color:#333">{E(t.get("body", ""))}</span>' + (f'<span class="ln">출처: <a href="{E(t["url"])}" rel="noopener nofollow">{E(t.get("source", "링크"))}</a></span>' if t.get('url') else '') + '</div>' for t in T)
    KIT_LINKS.append(('타임라인', 'timeline/'))
    return [box(B, '타임라인', data(B, 'timeline', 'title.txt', '타임라인').strip(), li, '일어난 일을 시간순으로 정리', 'timeline')]


def rank(B):
    rows = [l.split('\t') for l in (data(B, 'rank', 'titles.tsv', '') or '').splitlines() if '\t' in l]
    if not rows:
        return []
    STOP = set('속보 단독 종합 관련 대한 위해 통해'.split())
    def words(t):
        return {re.sub(r'(은|는|이|가|을|를|의|에|도|로)$', '', w) if len(w) > 2 else w for w in re.findall(r'[0-9A-Za-z가-힣]+', t) if len(w) >= 2 and w not in STOP}
    groups = []
    for src, title in rows:
        w = words(title); best, bn = None, 0
        for g in groups:
            n = len(w & g['seed'])
            if n >= 2 and n / min(len(w), len(g['seed'])) >= 0.4 and n > bn:
                best, bn = g, n
        (best['items'].append((src, title)) if best else groups.append({'seed': w, 'items': [(src, title)]}))
    ranked = sorted(groups, key=lambda g: (-len({s for s, _ in g['items']}), -len(g['items'])))
    li = ''.join(f'<div class="tp"><span class="lb">{k}위 · {len({s for s, _ in g["items"]})}곳이 다룸</span><b>{E(g["items"][0][1])}</b>' + ''.join(f'<span class="ln">{E(s)} — {E(t)}</span>' for s, t in g['items'][:4]) + '</div>' for k, g in enumerate(ranked[:10], 1))
    KIT_LINKS.append(('화제 순위', 'rank/'))
    return [box(B, '화제 순위', '같은 화제끼리 묶은 순위', li, '제목 목록을 같은 화제끼리 묶어 몇 곳이 다뤘는지로 순위를 매깁니다', 'rank', '<p class="dek">제목 목록(kits/rank/data/titles.tsv)을 낱말이 겹치는 것끼리 묶어 서로 다른 곳이 많이 다룬 순서로 보여 줍니다.</p>')]


def wiki(B):
    wd = os.path.join(B.KITS_DIR, 'wiki', 'data')
    files = sorted(glob.glob(os.path.join(wd, '*.md')))
    if not files:
        return []
    docs = {}
    for f in files:
        t = open(f, encoding='utf-8').read(); slug = os.path.splitext(os.path.basename(f))[0]
        docs[slug] = (B.first_h1(t, slug), t)
    back = {s: [] for s in docs}
    for s, (_, t) in docs.items():
        for m in re.findall(r'\[\[([^\]]+)\]\]', t):
            if m in docs and s not in back[m]:
                back[m].append(s)
    urls = []
    for s, (title, t) in docs.items():
        body = re.sub(r'\[\[([^\]]+)\]\]', lambda m: f'[{m.group(1)}]({B.BASE}wiki/{m.group(1)}/)' if m.group(1) in docs else m.group(1), re.sub(r'^# .+\n', '', t, count=1))
        html_ = B.md(body)
        html_ = re.sub(r'<a href="(' + re.escape(B.BASE) + r'wiki/[^"]+)"', r'<a href="\1"', html_)
        bl = ''.join(f'<li><a href="{B.BASE}wiki/{b}/">{E(docs[b][0])}</a></li>' for b in back[s])
        urls.append(B.page(f'wiki/{s}', f'{title} — {B.S["name"]}', re.sub(r'\s+', ' ', re.sub(r'[#*\[\]]', '', body))[:140],
                           f'<article class="art"><span class="lb">위키</span><h1>{E(title)}</h1>{html_}' + (f'<h2>이 문서를 가리키는 문서</h2><ul class="rp">{bl}</ul>' if bl else '') + f'<div class="by"><a href="{B.BASE}wiki/">위키 목록</a></div></article>'))
    lst = ''.join(f'<li><a href="{B.BASE}wiki/{s}/"><b>{E(t)}</b></a></li>' for s, (t, _) in docs.items())
    urls.append(B.page('wiki', f'위키 — {B.S["name"]}', '문서끼리 링크로 이어진 위키', f'<div class="page"><span class="lb">위키</span><h1>위키</h1><ul class="rp">{lst}</ul></div>'))
    KIT_LINKS.append(('위키', 'wiki/'))
    return urls


def faq(B):
    F = data(B, 'faq', 'faq.json', [])
    if not F:
        return []
    li = ''.join(f'<details class="fq"><summary>{E(x["q"])}</summary><p>{E(x["a"])}</p></details>' for x in F)
    ld = json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': x['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': x['a']}} for x in F]}, ensure_ascii=False)
    KIT_LINKS.append(('자주 묻는 질문', 'faq/'))
    return [box(B, '자주 묻는 질문', '자주 묻는 질문', li + f'<script type="application/ld+json">{ld}</script>', f'자주 묻는 질문 {len(F)}개와 답', 'faq')]


def schedule(B):
    S_ = sorted(data(B, 'schedule', 'events.json', []), key=lambda x: x['date'])
    if not S_:
        return []
    js = ('<script>(function(){var t=new Date();t.setHours(0,0,0,0);var up=document.getElementById("up"),pa=document.getElementById("pa");document.querySelectorAll(".ev").forEach(function(e){var d=new Date(e.dataset.d+"T00:00:00");(d<t?pa:up).appendChild(e)});'
          'if(!up.children.length)up.innerHTML="<p class=\\"mu\\">다가오는 일정이 없습니다.</p>";document.getElementById("pah").style.display=pa.children.length?"":"none"})()</script>')
    evs = ''.join(f'<div class="tp ev" data-d="{E(e["date"])}"><span class="lb">{E(e["date"])}</span><b>{E(e["title"])}</b><span class="ln">{E(e.get("note", ""))}</span></div>' for e in S_)
    body = f'<h2>다가오는 일정</h2><div id="up"></div><h2 id="pah">지난 일정</h2><div id="pa" style="opacity:.55"></div><div style="display:none">{evs}</div>'
    # JS 가 꺼져 있어도 보이도록: 전체 목록을 noscript 로도 둔다
    body = body.replace('<div style="display:none">' + evs + '</div>', evs.replace('class="tp ev"', 'class="tp ev"'))
    KIT_LINKS.append(('일정', 'schedule/'))
    return [box(B, '일정', '일정', body + js, '날짜별 일정. 지난 일정은 아래로 내려갑니다', 'schedule', '<p class="dek">오늘 날짜를 기준으로 지난 일정은 자동으로 아래로 내려갑니다(쪽을 다시 찍지 않아도 됩니다).</p>')]


def quiz(B):
    Q = data(B, 'quiz', 'quiz.json')
    if not Q:
        return []
    qs = json.dumps(Q['questions'], ensure_ascii=False)
    js = ('<script>(function(){var Q=%s,box=document.getElementById("qz"),k="fm_quiz_best";var h="";Q.forEach(function(q,i){h+="<div class=\\"tp\\"><b>"+(i+1)+". "+q.q+"</b>";q.options.forEach(function(o,j){h+="<label style=\\"display:block;font:15px var(--sans);margin:6px 0\\"><input type=\\"radio\\" name=\\"q"+i+"\\" value=\\""+j+"\\" style=\\"width:auto;margin-right:8px\\">"+o+"</label>"});h+="<div class=\\"ex\\" id=\\"x"+i+"\\" style=\\"display:none;font:14px var(--sans);color:#444\\"></div></div>"});'
          'h+="<button type=\\"button\\" id=\\"go\\" style=\\"font:700 16px var(--sans);padding:10px 20px;border:2px solid #111;background:#111;color:#fff;cursor:pointer;width:auto\\">채점하기</button><p id=\\"rs\\" style=\\"font:700 18px var(--serif)\\"></p>";box.innerHTML=h;'
          'document.getElementById("go").onclick=function(){var s=0;Q.forEach(function(q,i){var c=document.querySelector("input[name=q"+i+"]:checked"),x=document.getElementById("x"+i);x.style.display="block";if(c&&+c.value===q.answer){s++;x.textContent="맞았습니다. "+q.explain}else{x.textContent="정답은 「"+q.options[q.answer]+"」. "+q.explain}});'
          'var m="";try{var b=+localStorage.getItem(k)||0;if(s>b){localStorage.setItem(k,s);b=s}m=" (이 브라우저의 최고 "+b+"점)"}catch(e){}document.getElementById("rs").textContent=s+" / "+Q.length+"점"+m}})()</script>') % qs
    KIT_LINKS.append(('퀴즈', 'quiz/'))
    return [box(B, '퀴즈', Q['title'], '<div id="qz"></div>' + js, Q.get('desc', '풀어 보는 퀴즈'), 'quiz', f'<p class="dek">{E(Q.get("desc", ""))} 결과는 이 브라우저에만 저장됩니다.</p>')]


def compare(B):
    T = data(B, 'compare', 'table.json')
    if not T:
        return []
    th = ''.join(f'<th data-c="{i}" style="cursor:pointer">{E(c)} ↕</th>' for i, c in enumerate(T['columns']))
    tr = ''.join('<tr>' + ''.join(f'<td>{E(str(c))}</td>' for c in r) + '</tr>' for r in T['rows'])
    js = ('<script>(function(){var t=document.getElementById("tb"),b=t.tBodies[0],f=document.getElementById("ft");t.tHead.querySelectorAll("th").forEach(function(h){h.onclick=function(){var c=+h.dataset.c,asc=h.dataset.a!=="1";h.dataset.a=asc?"1":"0";'
          'var r=[].slice.call(b.rows);r.sort(function(x,y){var a=x.cells[c].textContent,z=y.cells[c].textContent,na=parseFloat(a.replace(/,/g,"")),nz=parseFloat(z.replace(/,/g,""));var v=(!isNaN(na)&&!isNaN(nz))?na-nz:a.localeCompare(z,"ko");return asc?v:-v});r.forEach(function(x){b.appendChild(x)})}});'
          'f.oninput=function(){var q=f.value.toLowerCase();[].forEach.call(b.rows,function(r){r.style.display=r.textContent.toLowerCase().indexOf(q)>=0?"":"none"})}})()</script>')
    body = (f'<input id="ft" type="search" placeholder="거르기(글자를 치면 줄이 걸러집니다)" style="font:16px var(--sans);padding:10px;width:100%;border:2px solid #111;margin:0 0 12px"><div style="overflow-x:auto"><table class="mdt" id="tb"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'
            f'<p class="ad-nt">{E(T.get("note", ""))}</p>{js}')
    KIT_LINKS.append(('표 비교', 'compare/'))
    return [box(B, '비교', T['title'], body, T.get('desc', '표 비교'), 'compare', f'<p class="dek">{E(T.get("desc", ""))} 제목 칸을 누르면 정렬됩니다.</p>')]


def gallery(B):
    gd = os.path.join(B.KITS_DIR, 'gallery', 'data')
    caps = data(B, 'gallery', 'captions.json', {})
    imgs = sorted(f for f in os.listdir(gd) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.webp'))) if os.path.isdir(gd) else []
    if not imgs:
        return []
    os.makedirs(os.path.join(B.OUT, 'gallery'), exist_ok=True)
    cells = ''
    for f in imgs:
        shutil.copy(os.path.join(gd, f), os.path.join(B.OUT, 'gallery', f))
        c = caps.get(f, os.path.splitext(f)[0])
        cells += f'<a href="{B.BASE}gallery/{f}" class="gi" data-c="{E(c)}"><img src="{B.BASE}gallery/{f}" alt="{E(c)}" loading="lazy" style="width:100%;aspect-ratio:1/1;object-fit:cover;border:1px solid #ccc;display:block"><span class="ln" style="font:13px var(--sans)">{E(c)}</span></a>'
    js = ('<div id="lb" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:9;align-items:center;justify-content:center;flex-direction:column;cursor:zoom-out"><img id="li" style="max-width:92vw;max-height:80vh;background:#fff"><p id="lc" style="color:#fff;font:15px var(--sans)"></p></div>'
          '<script>(function(){var l=document.getElementById("lb"),i=document.getElementById("li"),c=document.getElementById("lc");document.querySelectorAll(".gi").forEach(function(a){a.addEventListener("click",function(e){e.preventDefault();i.src=a.href;c.textContent=a.dataset.c;l.style.display="flex"})});l.onclick=function(){l.style.display="none"};document.addEventListener("keydown",function(e){if(e.key=="Escape")l.style.display="none"})})()</script>')
    KIT_LINKS.append(('사진첩', 'gallery/'))
    return [box(B, '사진첩', '사진첩', f'<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px">{cells}</div>{js}', f'그림 {len(imgs)}장을 작게 모아 보고 눌러 크게 보는 사진첩', 'gallery', '<p class="dek">그림을 누르면 크게 보입니다(닫기: 화면 누르기 또는 Esc).</p>')]


def links(B):
    L = data(B, 'links', 'links.json', [])
    if not L:
        return []
    body = ''.join(f'<h2>{E(g["category"])}</h2><ul class="rp">' + ''.join(f'<li><a href="{E(i["url"])}" rel="noopener nofollow" target="_blank">{E(i["name"])}</a> <span class="mu">{E(i.get("desc", ""))}</span></li>' for i in g['items']) + '</ul>' for g in L)
    KIT_LINKS.append(('링크 모음', 'links/'))
    return [box(B, '링크 모음', '링크 모음', body, '분류별로 모은 유용한 링크', 'links', '<p class="dek">깨진 링크는 <code>python linkcheck.py</code> 로 점검합니다.</p>')]


ORDER = [('topics', topics), ('today', today), ('trends', trends), ('widget', widget), ('notice', notice), ('timeline', timeline), ('rank', rank), ('wiki', wiki), ('faq', faq), ('schedule', schedule), ('quiz', quiz), ('compare', compare), ('gallery', gallery), ('links', links)]


def pages(B):
    KIT_LINKS.clear()
    urls = []
    for name, fn in ORDER:
        if B.part(name, False):
            try:
                urls += fn(B)
            except Exception as e:   # 한 키트가 실패해도 나머지 빌드는 계속
                print('키트 건너뜀:', name, repr(e)[:120])
    return urls
