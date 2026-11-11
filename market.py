# -*- coding: utf-8 -*-
"""디지털 상품 장터 틀 — 레퍼런스: 검로드(gumroad.com)를 옆에 두고 그대로 옮긴 것(미러). 2026-11-11 에 둘러보기 쪽(gumroad.com/discover)과 상품 쪽 한 건을 받아 화면으로 보고 짜임을 맞췄다(조각: 참고/조각/검로드.json).
옮긴 것(둘러보기): 어두운 바탕 · 머리(이름 글자 + 넓은 찾기 칸 + 로그인·팔기 시작 단추) · 분류 알약 줄(전체가 검은 알약, 끝에 「더 보기」) · 「추천 상품」 큰 카드(그림 왼쪽 + 이름·설명·판매자·분홍 값 딱지·별점, 오른쪽 위 ← 1 / N →)
                 · 「장터에서」 + 정렬 알약(뜨는 것|많이 팔린 것|새로 나온 것) · 왼쪽 거르기 상자(태그·들어 있는 것·값·별점) · 3열 상품 카드(정사각 그림 → 이름 → 판매자 → ★ 평점(수) → 줄 → 분홍 값 딱지)
옮긴 것(상품 쪽): 큰 대표 그림 · 테두리 상자 안 왼쪽(이름 / 판매자 | ★★★★★ N개 평가 / 설명) · 오른쪽(값 딱지 → 들어 있는 것 → 큰 「살래요!」 단추 → 이미 샀나요? → 알림 상자 → 찜·공유 → 환불 안내 → 평가 막대 5~1 → 후기)
본과 다른 것(독자가 알고 바꾼다): **결제가 없다.** 「살래요!」는 손잡이 사는단추에 따라 주문 문의(서버가 받아 운영자 화면에 쌓임) 또는 바깥 판매 주소로 보낸다. 로그인·판매자 가입이 없어 상품은 자료 파일(kits/market/data/products.json)에 운영자가 적는다. 본의 글꼴(ABC Favorit)은 쓰지 않는다.
파이썬 기본 기능만 쓴다."""
import hashlib, html, json, os, re

E = html.escape
PINK = '#ff90e8'

CSS = (".mk{--mkp:#ff90e8;background:#242423;color:#fff;font:16px/1.4 -apple-system,'Segoe UI','Malgun Gothic',system-ui,sans-serif;padding:0 0 60px}.mk a{color:#fff}.mk *{box-sizing:border-box}"
       ".mk-in{max-width:1280px;margin:0 auto;padding:0 64px}.mk-head{display:flex;gap:16px;align-items:center;padding:32px 0 24px}.mk-logo{font:900 44px/1 'Arial Black',system-ui,sans-serif;letter-spacing:-.05em;text-decoration:none}"
       ".mk-search{flex:1;display:flex;align-items:center;gap:10px;background:#000;border:1px solid #555;border-radius:4px;padding:0 16px;height:48px}.mk-search input{flex:1;background:none;border:0;color:#fff;font:16px inherit;outline:0;width:100%}.mk-search input::placeholder{color:#aaa}"
       ".mk-btn{display:inline-flex;align-items:center;height:48px;padding:0 16px;border:1px solid #777;border-radius:4px;text-decoration:none;white-space:nowrap}.mk-btn.light{background:#ddd;color:#000!important;border-color:#ddd}"
       ".mk-cats{display:flex;gap:4px;align-items:center;padding:0 0 36px;border-bottom:1px solid #555;margin:0 -64px;padding-left:64px;padding-right:64px;overflow-x:auto;scrollbar-width:none}.mk-cats a{padding:8px 13px;border-radius:999px;text-decoration:none;white-space:nowrap;border:1px solid transparent;cursor:pointer}.mk-cats a.on{background:#000;border-color:#777}"
       ".mk h2{font:400 20px/1.3 inherit;margin:0}.mk-sec{display:flex;justify-content:space-between;align-items:center;margin:64px 0 16px}.mk-pager{display:flex;gap:12px;align-items:center}.mk-pager a{cursor:pointer;text-decoration:none}"
       ".mk-feat{display:grid;grid-template-columns:378px 1fr;background:#000;border:1px solid #777;border-radius:4px;min-height:378px;max-width:704px;overflow:hidden}.mk-feat img{width:378px;aspect-ratio:1/1;object-fit:cover;display:block;border-right:1px solid #777}.mk-feat .fb{padding:16px 24px;display:flex;flex-direction:column}"
       ".mk-feat h3{font:400 20px/1.3 inherit;margin:0 0 12px}.mk-feat h3 a{text-decoration:none}.mk-feat p{font-size:14px;color:#bbb;margin:0 0 12px;display:-webkit-box;-webkit-line-clamp:6;-webkit-box-orient:vertical;overflow:hidden}.mk-feat .ft{margin-top:auto;display:flex;justify-content:space-between;align-items:center}"
       ".mk-seller{display:inline-flex;gap:8px;align-items:center;text-decoration:underline}.mk-av{width:20px;height:20px;border-radius:50%;border:1px solid #fff;display:inline-block;flex:none}"
       ".mk-price{display:inline-block;background:var(--mkp);color:#000;padding:2px 22px 2px 8px;clip-path:polygon(0 0,100% 0,calc(100% - 12px) 50%,100% 100%,0 100%);font-size:16px;line-height:1.5}"
       ".mk-tabs a{padding:8px 13px;border-radius:999px;text-decoration:none;border:1px solid transparent;cursor:pointer}.mk-tabs a.on{background:#000;border-color:#777}"
       ".mk-main{display:grid;grid-template-columns:272px 1fr;gap:64px;align-items:start}.mk-filt{background:#000;border:1px solid #777;border-radius:4px}.mk-filt>div,.mk-filt summary{padding:16px;border-bottom:1px solid #555;list-style:none;cursor:pointer;display:flex;justify-content:space-between}.mk-filt details:last-child summary{border-bottom:0}.mk-filt details[open] summary{border-bottom:1px solid #555}"
       ".mk-filt summary::-webkit-details-marker{display:none}.mk-filt summary::after{content:'›';font-size:20px;line-height:1}.mk-filt .fo{padding:12px 16px;border-bottom:1px solid #555;display:grid;gap:8px;font-size:15px}.mk-filt .fo a{cursor:pointer;text-decoration:none;color:#ddd}.mk-filt .fo a.on{color:var(--mkp)}.mk-filt input{background:#000;border:1px solid #777;color:#fff;padding:8px;border-radius:4px;width:100%;font:15px inherit}"
       ".mk-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.mk-card{background:#000;border:1px solid #777;border-radius:4px;overflow:hidden;display:flex;flex-direction:column}.mk-card img{width:100%;aspect-ratio:1/1;object-fit:cover;display:block;border-bottom:1px solid #777}"
       ".mk-card .cb{padding:16px;display:grid;gap:10px;flex:1;align-content:start}.mk-card h3{font:400 20px/1.4 inherit;margin:0}.mk-card h3 a{text-decoration:none}.mk-card .cf{padding:16px;border-top:1px solid #777}.mk-star{white-space:nowrap}"
       ".mk-pp{background:#fff;color:#000;padding:64px 0}.mk-pp a{color:#000}.mk-box{max-width:1140px;margin:0 auto;border:1px solid #000}.mk-cover{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;border-bottom:1px solid #000}.mk-cols{display:grid;grid-template-columns:1fr 380px}"
       ".mk-l>*{border-bottom:1px solid #000}.mk-l h1{font:400 40px/1.2 inherit;margin:0;padding:24px}.mk-meta{display:grid;grid-template-columns:1fr auto}.mk-meta>*{padding:16px 24px}.mk-meta>*+*{border-left:1px solid #000}.mk-pp .mk-av{border-color:#000}"
       ".mk-desc{padding:24px;border-bottom:0!important}.mk-desc h3{font:400 20px/1.4 inherit;margin:24px 0 12px}.mk-desc h3:first-child{margin-top:0}.mk-desc p{margin:0 0 16px;line-height:1.5}"
       ".mk-r{border-left:1px solid #000}.mk-buy{padding:24px;display:grid;gap:16px;border-bottom:1px solid #000}.mk-want{display:block;width:100%;text-align:center;background:var(--mkp);color:#000;border:1px solid #000;border-radius:4px;padding:12px;font:16px inherit;cursor:pointer;text-decoration:none}.mk-want:hover{box-shadow:4px 4px 0 #000;transform:translate(-2px,-2px)}"
       ".mk-small{font-size:14px;text-align:center}.mk-note{border:1px solid #000;border-radius:4px;padding:16px}.mk-two{display:grid;grid-template-columns:1fr auto;gap:8px}.mk-out{border:1px solid #000;border-radius:4px;padding:12px 16px;background:#fff;font:16px inherit;cursor:pointer;text-align:left;color:#000;width:auto}"
       ".mk-rate{padding:24px;display:grid;gap:10px}.mk-rate h3{font:400 20px/1.3 inherit;margin:0;display:flex;justify-content:space-between}.mk-bar{display:grid;grid-template-columns:60px 1fr 44px;gap:10px;align-items:center;font-size:15px}.mk-bar i{display:block;height:20px;border:1px solid #000;border-radius:4px;overflow:hidden}.mk-bar i b{display:block;height:100%;background:var(--mkp)}"
       ".mk-rev{border-top:1px solid #000;padding:16px 0 0;margin-top:8px}.mk-rev p{margin:8px 0}.mk-form{display:grid;gap:8px}.mk-form input,.mk-form textarea{font:15px inherit;padding:10px;border:1px solid #000;border-radius:4px;width:100%}.mk-msg{font-size:14px;min-height:1.2em}"
       ".mkfull .mast,.mkfull nav.menu,.mkfull .bnav,.mkfull .notice,.mkfull footer,.mkfull .trust,.mkfull .mon{display:none!important}.mkfull main.wrap{max-width:none;padding:0}.mkfull body{background:#242423}"
       ".mk h1,.mk h2,.mk h3{font-weight:400!important;font-family:inherit!important;letter-spacing:0!important;border:0!important;color:inherit}.mk-card img,.mk-feat img,.mk-cover{height:auto}.mk-form[hidden],.mk [hidden]{display:none!important}"
       ".mk button,.mk input,.mk textarea{font-size:16px;font-family:inherit}.mk-search input{font-size:16px!important;padding:0;border:0!important;background:none!important;color:#fff!important}.mk-out{font-size:16px!important}.mk-want{font-size:16px!important;font-weight:400}"
       ".mk-msg:empty{display:none}.mk-buy{gap:12px}"
       ".mk-feats{display:flex;gap:24px;overflow:hidden;scroll-behavior:smooth}.mk-feats .mk-feat{flex:none;width:704px;max-width:100%}"
       "@media(max-width:1000px){.mk-in{padding:0 16px}.mk-cats{margin:0 -16px;padding-left:16px;padding-right:16px}.mk-main{grid-template-columns:1fr;gap:24px}.mk-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.mk-cols{grid-template-columns:1fr}.mk-r{border-left:0;border-top:1px solid #000}.mk-feat{grid-template-columns:1fr}.mk-feat img{width:100%;height:auto;aspect-ratio:1/1;border-right:0;border-bottom:1px solid #777}.mk-head{flex-wrap:wrap}.mk-logo{font-size:32px}.mk-search{order:3;flex-basis:100%}}"
       "@media(max-width:560px){.mk-grid{grid-template-columns:1fr}.mk-l h1{font-size:30px}.mk-pp{padding:0}}\n")


def won(p):
    v = f'₩{int(p["price"]):,}' if p.get('price') else '₩0'
    if p.get('pwyw'):
        v += '+'
    if p.get('recurrence'):
        v += f' / {p["recurrence"]}'
    return v


def cover_svg(p, w=600, h=600):
    pal = [('#1b1b3a', '#f4b400'), ('#f6efe0', '#1f5f3f'), ('#0f1b2d', '#4aa3ff'), ('#2d1b2f', '#ff90e8'), ('#fff3c4', '#7a3b00'), ('#102a24', '#3ddc97'), ('#2b2b2b', '#ffffff'), ('#fde2e2', '#b3261e'), ('#e7f0ff', '#1e3a8a')]
    bg, fg = pal[int(hashlib.md5(p['slug'].encode()).hexdigest()[:2], 16) % len(pal)]
    words = p['name'].split(); l1 = ' '.join(words[:2]); l2 = ' '.join(words[2:4])
    cy = h / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="system-ui,Malgun Gothic,sans-serif"><rect width="{w}" height="{h}" fill="{bg}"/>'
            f'<circle cx="{w / 2}" cy="{cy}" r="{min(w, h) * .36}" fill="none" stroke="{fg}" stroke-width="3" opacity=".5"/><circle cx="{w / 2}" cy="{cy}" r="{min(w, h) * .3}" fill="none" stroke="{fg}" stroke-width="1.5" opacity=".35"/>'
            f'<text x="{w / 2}" y="{cy - 6}" text-anchor="middle" font-size="{int(min(w, h) * .085)}" font-weight="900" fill="{fg}">{E(l1)}</text><text x="{w / 2}" y="{cy + min(w, h) * .09}" text-anchor="middle" font-size="{int(min(w, h) * .07)}" font-weight="700" fill="{fg}" opacity=".85">{E(l2)}</text>'
            f'<text x="{w / 2}" y="{h * .9}" text-anchor="middle" font-size="{int(min(w, h) * .035)}" fill="{fg}" opacity=".6">{E(p.get("category", ""))} · 예시 상품</text></svg>')


def _img(B, p, wide=False):
    d = os.path.join(B.OUT, 'img'); os.makedirs(d, exist_ok=True)
    name = f'mk_{p["slug"]}{"_w" if wide else ""}.svg'
    open(os.path.join(d, name), 'w', encoding='utf-8').write(cover_svg(p, 1280 if wide else 600, 720 if wide else 600))
    return f'{B.BASE}img/{name}'


def stars(p):
    r = p.get('rating') or {}
    return f'<span class="mk-star">★ {r.get("avg", 0):.1f} ({r.get("count", 0)})</span>' if r.get('count') else ''


def seller(p, color='#4aa3ff'):
    c = '#' + hashlib.md5(p.get('seller', '').encode()).hexdigest()[:6]
    return f'<span class="mk-seller"><i class="mk-av" style="background:{c}"></i>{E(p.get("seller", ""))}</span>'


def _cats(P):
    cats = []
    for p in P:
        if p.get('category') and p['category'] not in cats:
            cats.append(p['category'])
    return cats


def head(B, P, cats, cur=''):
    name = E(B.S['name'])
    pills = f'<a class="{"on" if not cur else ""}" data-cat="" href="{B.BASE}market/">전체</a>' + ''.join(f'<a class="{"on" if c == cur else ""}" data-cat="{E(c)}" href="{B.BASE}market/?cat={E(c)}">{E(c)}</a>' for c in cats[:8]) + (f'<a href="{B.BASE}market/">더 보기 ⌄</a>' if len(cats) > 8 else '')
    return (f'<div class="mk-head"><a class="mk-logo" href="{B.BASE}market/">{name}</a><form class="mk-search" action="{B.BASE}market/" method="get" role="search"><span aria-hidden="true">⌕</span><input name="q" id="mkq" placeholder="상품 찾기" aria-label="상품 찾기"></form>'
            f'<a class="mk-btn" href="/admin/">로그인</a><a class="mk-btn light" href="{B.BASE}market/sell/">팔기 시작</a></div><nav class="mk-cats" aria-label="분류">{pills}</nav>')


LIST_JS = r"""(function(){var G=document.getElementById("mkg");if(!G)return;var cards=[].slice.call(G.children),S={cat:"",q:"",tag:"",ft:"",min:"",max:"",rate:"",sort:"trend"};
function q(k){var m=location.search.match(new RegExp("[?&]"+k+"=([^&]*)"));return m?decodeURIComponent(m[1].replace(/[+]/g," ")):""}
S.cat=q("cat");S.q=q("q");var qi=document.getElementById("mkq");if(qi)qi.value=S.q;
function draw(){var L=cards.filter(function(c){var d=c.dataset;return (!S.cat||d.cat===S.cat)&&(!S.q||d.t.indexOf(S.q.toLowerCase())>=0)&&(!S.tag||(" "+d.tags+" ").indexOf(" "+S.tag+" ")>=0)&&(!S.ft||d.ft===S.ft)&&(!S.min||+d.price>=+S.min)&&(!S.max||+d.price<=+S.max)&&(!S.rate||+d.rate>=+S.rate)});
 L.sort(function(a,b){return S.sort==="best"?b.dataset.sales-a.dataset.sales:(S.sort==="new"?a.dataset.days-b.dataset.days:b.dataset.trend-a.dataset.trend)});
 cards.forEach(function(c){c.style.display="none"});L.forEach(function(c){c.style.display="";G.appendChild(c)});var e=document.getElementById("mke");if(e)e.hidden=L.length>0;
 document.querySelectorAll(".mk-cats a[data-cat]").forEach(function(a){a.classList.toggle("on",a.dataset.cat===S.cat)});
 document.querySelectorAll("[data-sort]").forEach(function(a){a.classList.toggle("on",a.dataset.sort===S.sort)});
 document.querySelectorAll("[data-f]").forEach(function(a){a.classList.toggle("on",S[a.dataset.f]===a.dataset.v)})}
document.querySelectorAll("[data-sort]").forEach(function(a){a.onclick=function(){S.sort=a.dataset.sort;draw()}});
document.querySelectorAll("[data-f]").forEach(function(a){a.onclick=function(){S[a.dataset.f]=S[a.dataset.f]===a.dataset.v?"":a.dataset.v;draw()}});
["min","max"].forEach(function(k){var i=document.getElementById("mk"+k);if(i)i.oninput=function(){S[k]=i.value;draw()}});
var F=[].slice.call(document.querySelectorAll(".mk-feat")),fi=0,pg=document.getElementById("mkpg"),fs=document.getElementById("mkfs");function feat(){if(fs&&F[fi])fs.scrollLeft=F[fi].offsetLeft-fs.offsetLeft;if(pg)pg.textContent=(fi+1)+" / "+F.length}
document.querySelectorAll("[data-fp]").forEach(function(a){a.onclick=function(){fi=(fi+(+a.dataset.fp)+F.length)%F.length;feat()}});feat();draw()})();"""

BUY_JS = r"""(function(){var w=document.getElementById("mkwant");if(!w)return;var mode=w.dataset.mode,box=document.getElementById("mkform"),msg=document.getElementById("mkmsg");
if(mode==="link")return;
w.onclick=function(e){e.preventDefault();box.hidden=!box.hidden;if(!box.hidden)box.querySelector("input").focus()};
box.onsubmit=function(e){e.preventDefault();var f=box,amt=f.amount?f.amount.value:"";
 fetch("/api/contact",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:f.name.value,email:f.email.value,message:"[주문 문의] "+w.dataset.name+" / "+w.dataset.price+(amt?" / 내가 정한 값 "+amt+"원":"")+" / "+f.note.value})}).then(function(r){return r.json()}).then(function(j){msg.textContent=j.ok?"주문 문의를 보냈습니다. 판매자가 메일로 안내합니다(결제는 이 사이트에서 하지 않습니다).":(j.error||"보내지 못했습니다");msg.style.color=j.ok?"#0b5d2f":"#a11a12";if(j.ok)f.reset()}).catch(function(){msg.textContent="서버가 켜져 있을 때 됩니다(python run.py 서버). 그때까지는 문의 쪽으로 보내 주세요.";msg.style.color="#a11a12"})};
var wl=document.getElementById("mkwl");if(wl){var K="fm_mk_wish",L=[];try{L=JSON.parse(localStorage.getItem(K)||"[]")}catch(e){}function p(){wl.firstChild.textContent=L.indexOf(w.dataset.slug)>=0?"찜했습니다 ":"찜하기 "}p();wl.onclick=function(){var i=L.indexOf(w.dataset.slug);if(i>=0)L.splice(i,1);else L.push(w.dataset.slug);try{localStorage.setItem(K,JSON.stringify(L))}catch(e){}p()}}
var sh=document.getElementById("mksh");if(sh)sh.onclick=function(){if(navigator.clipboard)navigator.clipboard.writeText(location.href).then(function(){sh.textContent="주소를 복사했습니다"})}})();"""

FULL_JS = '<script>document.documentElement.classList.add("mkfull")</script>'


def load(B):
    p = os.path.join(B.KITS_DIR, 'market', 'data', 'products.json')
    if not os.path.exists(p):
        p = os.path.join(B.HERE, 'kits', 'market', 'data', 'products.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else []


def card(B, p):
    r = p.get('rating') or {}
    return (f'<article class="mk-card" data-cat="{E(p.get("category", ""))}" data-t="{E((p["name"] + " " + p.get("seller", "")).lower())}" data-tags="{E(" ".join(p.get("tags", [])))}" data-ft="{E(p.get("filetype", ""))}" data-price="{int(p.get("price", 0))}" data-rate="{r.get("avg", 0)}" data-sales="{int(p.get("sales", 0))}" data-days="{int(p.get("days", 0))}" data-trend="{int(p.get("sales", 0)) / (int(p.get("days", 0)) + 2):.3f}">'
            f'<a href="{B.BASE}market/{E(p["slug"])}/" tabindex="-1"><img src="{_img(B, p)}" alt="" width="600" height="600" loading="lazy"></a><div class="cb"><h3><a href="{B.BASE}market/{E(p["slug"])}/">{E(p["name"])}</a></h3>{seller(p)}{stars(p)}</div><div class="cf"><span class="mk-price">{E(won(p))}</span></div></article>')


def list_body(B, full, home=False):
    P = load(B)
    cats = []
    for p in P:
        if p.get('category') and p['category'] not in cats:
            cats.append(p['category'])
    feats = [p for p in P if p.get('featured')] or P[:3]
    fh = ''.join(f'<div class="mk-feat"><a href="{B.BASE}market/{E(p["slug"])}/" tabindex="-1"><img src="{_img(B, p)}" alt="" width="600" height="600"></a><div class="fb"><h3><a href="{B.BASE}market/{E(p["slug"])}/">{E(p["name"])}</a></h3><p>{E(p.get("summary", ""))}</p>{seller(p)}<div class="ft"><span class="mk-price">{E(won(p))}</span>{stars(p)}</div></div></div>' for p in feats)
    tags = []
    for p in P:
        for t in p.get('tags', []):
            if t not in tags:
                tags.append(t)
    fts = sorted({p.get('filetype', '') for p in P if p.get('filetype')})
    filt = ('<aside class="mk-filt"><div>거르기</div>'
            '<details><summary>태그</summary><div class="fo">' + ''.join(f'<a data-f="tag" data-v="{E(t)}">{E(t)}</a>' for t in tags[:10]) + '</div></details>'
            '<details><summary>들어 있는 것</summary><div class="fo">' + ''.join(f'<a data-f="ft" data-v="{E(t)}">{E(t)}</a>' for t in fts) + '</div></details>'
            '<details><summary>값</summary><div class="fo"><input id="mkmin" type="number" inputmode="numeric" placeholder="최소 값(원)" aria-label="최소 값"><input id="mkmax" type="number" inputmode="numeric" placeholder="최대 값(원)" aria-label="최대 값"></div></details>'
            '<details><summary>별점</summary><div class="fo">' + ''.join(f'<a data-f="rate" data-v="{n}">{"★" * n} 이상</a>' for n in (4, 3, 2, 1)) + '</div></details></aside>')
    K = B.S.get('knobs') or {}
    cols = int(K.get('market_cols', 3))
    return (('' if home else '<h1 style="position:absolute;left:-9999px;top:0">장터</h1>') + f'{FULL_JS if full else ""}<div class="mk" style="--mkp:{E(K.get("market_color", PINK))}"><div class="mk-in">{head(B, P, cats)}'
            f'<div class="mk-sec"><h2>추천 상품</h2><span class="mk-pager"><a data-fp="-1" aria-label="앞">←</a><span id="mkpg">1 / {len(feats)}</span><a data-fp="1" aria-label="다음">→</a></span></div><div class="mk-feats" id="mkfs">{fh}</div>'
            f'<div class="mk-sec"><h2>장터에서</h2><span class="mk-tabs"><a data-sort="trend" class="on">뜨는 것</a><a data-sort="best">많이 팔린 것</a><a data-sort="new">새로 나온 것</a></span></div>'
            f'<div class="mk-main">{filt}<div><div class="mk-grid" id="mkg" style="grid-template-columns:repeat({cols},minmax(0,1fr))">{"".join(card(B, p) for p in P)}</div><p id="mke" hidden>조건에 맞는 상품이 없습니다.</p></div></div></div></div><script>{LIST_JS}</script>')


def product_body(B, p, full):
    K = B.S.get('knobs') or {}
    mode = 'link' if (K.get('buy_mode') == '바깥주소' and p.get('buy_url')) else 'ask'
    pwyw = bool(p.get('pwyw')) and K.get('pwyw') != '끔'
    r = p.get('rating') or {}; dist = r.get('dist') or [0, 0, 0, 0, 0]
    desc = ''.join((f'<h3>{E(x[2:].strip())}</h3>' if x.startswith('# ') else f'<p>{E(x)}</p>') for x in p.get('desc', []))
    bars = ''.join(f'<div class="mk-bar"><span>{5 - i}점</span><i><b style="width:{dist[i]}%"></b></i><span>{dist[i]}%</span></div>' for i in range(5))
    revs = ''.join(f'<div class="mk-rev"><span>{"★" * int(v.get("stars", 5))}</span><p>{E(v.get("text", ""))}</p><span class="mk-seller" style="text-decoration:none"><i class="mk-av" style="background:#ddd"></i>{E(v.get("by", ""))} (예시 후기)</span></div>' for v in p.get('reviews', []))
    want = (f'<a class="mk-want" id="mkwant" data-mode="link" href="{E(p["buy_url"])}" rel="noopener nofollow">살래요!</a><p class="mk-small">바깥 판매 쪽으로 넘어갑니다. 결제는 그곳에서 합니다.</p>' if mode == 'link' else
            f'<a class="mk-want" id="mkwant" href="#" data-mode="ask" data-slug="{E(p["slug"])}" data-name="{E(p["name"])}" data-price="{E(won(p))}">살래요!</a>'
            f'<form class="mk-form" id="mkform" hidden><input name="name" maxlength="40" placeholder="이름" aria-label="이름"><input name="email" type="email" required maxlength="120" placeholder="안내받을 메일 주소" aria-label="메일 주소">'
            + ('<input name="amount" type="number" inputmode="numeric" min="' + str(int(p.get('price', 0))) + '" placeholder="내고 싶은 값(원, ' + f'{int(p.get("price", 0)):,}' + ' 이상)" aria-label="내고 싶은 값">' if pwyw else '')
            + '<textarea name="note" maxlength="500" placeholder="남길 말(선택)" aria-label="남길 말"></textarea><button class="mk-want" type="submit">주문 문의 보내기</button></form><p class="mk-msg" id="mkmsg" role="status"></p>'
              '<p class="mk-small">이 사이트는 결제를 받지 않습니다. 주문 문의를 보내면 판매자가 메일로 안내합니다.</p>')
    note = f'<div class="mk-note">{E(p["note"])}</div>' if p.get('note') else ''
    return (f'{FULL_JS if full else ""}<div class="mk" style="--mkp:{E(K.get("market_color", PINK))}"><div class="mk-in">{head(B, [], _cats(load(B)), p.get('category', ''))}</div><div class="mk-pp"><div class="mk-in"><div class="mk-box"><img class="mk-cover" src="{_img(B, p, True)}" alt="{E(p["name"])} 대표 그림" width="1280" height="720">'
            f'<div class="mk-cols"><div class="mk-l"><h1>{E(p["name"])}</h1><div class="mk-meta"><div>{seller(p)}</div><div>{"★" * round(r.get("avg", 0))} {r.get("count", 0)}개 평가</div></div><div class="mk-desc">{desc}</div></div>'
            f'<div class="mk-r"><div class="mk-buy"><div><span class="mk-price">{E(won(p))}</span></div><div style="font-size:14px">들어 있는 것: {E(p.get("includes", ""))}</div>{want}{note}'
            f'<div class="mk-two"><button class="mk-out" id="mkwl" type="button">찜하기 <span aria-hidden="true">⌄</span></button><button class="mk-out" id="mksh" type="button">공유</button></div><p class="mk-small" style="text-decoration:underline">{E(p.get("refund", "환불 안내는 판매자에게 문의하세요"))}</p></div>'
            f'<div class="mk-rate"><h3><span>평가</span><span>★ {r.get("avg", 0):g} ({r.get("count", 0)}개 평가)</span></h3>{bars}{revs}</div></div></div></div></div></div></div><script>{BUY_JS}</script>')


SELL = ('<h1>팔기 시작</h1><p>이 장터는 가입해서 올리는 곳이 아니라, 운영자가 상품을 자료 파일에 한 건씩 적어 여는 작은 가게입니다.</p>'
        '<h2>상품 올리는 법</h2><ul><li><code>kits/market/data/products.json</code> 에 한 건을 더합니다(이름·한 줄 설명·값·들어 있는 것·분류·태그).</li><li>다시 찍으면(<code>python run.py 바꿨다</code>) 둘러보기와 상품 쪽이 생깁니다.</li></ul>'
        '<h2>결제는 어떻게 하나요</h2><p>이 틀에는 결제가 없습니다. 「살래요!」는 주문 문의를 보내거나(서버가 받아 운영자 화면에 쌓임), 바깥 판매 쪽 주소로 넘깁니다(손잡이 사는단추). 결제·정산·세금은 혼자 다루기 어려워 결제 대행사나 장터 서비스에 맡깁니다.</p>')


def pages(B):
    if not B.part('market', False):
        return []
    P = load(B); full = B.S.get('kind', '').startswith('쇼핑몰')
    u = [B.page('market', f'장터 — {B.S["name"]}', '혼자 만든 디지털 상품을 둘러보고 주문 문의를 보내는 장터', list_body(B, full)),
         B.page('market/sell', f'팔기 시작 — {B.S["name"]}', '이 장터에 상품을 올리는 법', f'<div class="page">{SELL}</div>')]
    for p in P:
        u.append(B.page(f'market/{p["slug"]}', f'{p["name"]} — {B.S["name"]}', p.get('summary', p['name'])[:150], product_body(B, p, full)))
    return u


def home_body(B):
    return list_body(B, True, True)
