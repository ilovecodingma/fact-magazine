# -*- coding: utf-8 -*-
"""날마다 순위(trend): 레퍼런스 깃허브 트렌딩(github.com/trending)의 짜임을 옮긴 틀. 파이썬 기본 기능만 쓴다.
본에서 옮긴 것: 검은 머리 띠·아랫줄 메뉴·가운데 큰 제목과 한 줄·상자 머리(항목|만든 사람 + 분류·기간 고르기)·한 줄 한 항목(만든이 / 이름, 설명, 분류 점·별 수·만든 사람들, 오른쪽에 별 단추와 「오늘 별 N개」)·만든 사람 순위(순번·얼굴·이름·대표 항목)·항목 쪽(이름 줄과 별 단추, 왼쪽 소개 글, 오른쪽 About).
본과 다른 것: 로그인이 없다(별은 한 사람이 한 항목에 한 번, 서버가 센다) · 본은 저장소가 저절로 모이지만 여기는 운영자가 자료에 넣거나 방문자가 올린 것을 승인한다 · 갈래(fork) 수·쓰는 말 고르기·따라가기(Follow)는 없다.
서버가 꺼져 있으면 예시 자료의 별 수로 화면만 보인다(별 주기·올리기는 서버가 있어야 한다)."""
import html, json, os

E = html.escape

CSS = (".tr{--bg:#fff;--sub:#f6f8fa;--bd:#d1d9e0;--fg:#1f2328;--mu:#59636e;--ln:#0969da;--btn:#f6f8fa;--on:#0969da;background:var(--bg);color:var(--fg);font:14px/1.5 -apple-system,'Segoe UI','Noto Sans KR','Malgun Gothic',Helvetica,Arial,sans-serif;text-align:left}\n"
       ".tr.dark{--bg:#0d1117;--sub:#151b23;--bd:#3d444d;--fg:#f0f6fc;--mu:#9198a1;--ln:#4493f8;--btn:#212830;--on:#1f6feb}\n"
       "@media(prefers-color-scheme:dark){.tr.auto{--bg:#0d1117;--sub:#151b23;--bd:#3d444d;--fg:#f0f6fc;--mu:#9198a1;--ln:#4493f8;--btn:#212830;--on:#1f6feb}}\n"
       ".trfull .tr{min-height:100vh}.tr-meta>span{display:inline-flex;align-items:center;gap:2px}.tr-av{vertical-align:0!important}"
       ".tr *{box-sizing:border-box}.tr a{color:var(--ln);text-decoration:none}.tr a:hover{text-decoration:underline}.tr h1,.tr h2,.tr h3{font-family:inherit!important;letter-spacing:0!important;border:0!important;margin:0;padding:0;color:inherit}.tr [hidden]{display:none!important}\n"
       ".tr-top{background:#010409;color:#fff;display:flex;align-items:center;gap:16px;padding:16px;min-height:68px}.tr-top a{color:#fff;font-weight:600}.tr-top .lg{font-size:18px;font-weight:700;margin-right:8px}.tr-top .sp{flex:1}\n"
       ".tr-top input{width:200px;max-width:34vw;height:34px;background:#010409!important;border:1px solid #3d444d!important;border-radius:6px;color:#fff!important;padding:0 12px;font:14px inherit!important}.tr-top .up{background:#fff;color:#1f2328;border-radius:6px;padding:6px 12px}\n"
       ".tr-sub{background:var(--bg);border-bottom:1px solid var(--bd)}.tr-sub div{max-width:1012px;margin:0 auto;padding:0 16px;display:flex;gap:24px;overflow-x:auto}.tr-sub a{color:var(--mu);padding:16px 0;white-space:nowrap}.tr-sub a.on{color:var(--fg);font-weight:600;box-shadow:inset 0 -2px 0 var(--on)}\n"
       ".tr-hero{background:var(--sub);border-bottom:1px solid var(--bd);text-align:center;padding:40px 16px}.tr-hero h1{font-size:32px;font-weight:600;line-height:1.25}.tr-hero p{font-size:16px;color:var(--mu);margin:4px 0 0}\n"
       ".tr-in{max-width:1012px;margin:0 auto;padding:40px 16px}.tr-box{border:1px solid var(--bd);border-radius:6px}.tr-bh{background:var(--sub);border-bottom:1px solid var(--bd);border-radius:6px 6px 0 0;padding:16px;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}\n"
       ".tr-seg{display:inline-flex}.tr-seg a{border:1px solid var(--bd);padding:5px 16px;font-weight:600;color:var(--fg);background:var(--bg)}.tr-seg a:first-child{border-radius:6px 0 0 6px}.tr-seg a:last-child{border-radius:0 6px 6px 0;margin-left:-1px}.tr-seg a.on{background:var(--on);border-color:var(--on);color:#fff}.tr-seg a:hover{text-decoration:none}\n"
       ".tr-pick{display:flex;gap:28px;flex-wrap:wrap}.tr-pick label{color:var(--mu);font:14px inherit;display:inline-flex;align-items:center;gap:4px;margin:0}.tr-pick select{background:none!important;border:0!important;color:var(--mu)!important;font:600 14px inherit!important;padding:0!important;width:auto!important;cursor:pointer}.tr-pick select option{color:#1f2328;background:#fff}\n"
       ".tr-row{padding:16px;border-top:1px solid var(--bd);position:relative}.tr-row:first-child{border-top:0}.tr-row h2{font-size:20px;font-weight:400;line-height:1.25;padding-right:110px}.tr-row h2 b{font-weight:600}.tr-row h2:before{content:'▣';color:var(--mu);font-size:14px;margin-right:8px;vertical-align:2px}\n"
       ".tr-row p{color:var(--mu);margin:4px 0;max-width:75%;padding-right:16px}.tr-meta{display:flex;flex-wrap:wrap;gap:4px 16px;align-items:center;color:var(--mu);font-size:12px;margin-top:8px}.tr-meta .dot{display:inline-block;width:12px;height:12px;border-radius:50%;vertical-align:-1px;margin-right:4px}.tr-meta .td{margin-left:auto}\n"
       ".tr-av{display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:50%;color:#fff;font:700 10px/1 inherit;margin-left:2px;vertical-align:-4px}\n"
       ".tr-star{position:absolute;right:16px;top:16px;background:var(--btn);color:var(--fg);border:1px solid var(--bd);border-radius:6px;padding:3px 12px;font:600 12px/20px inherit;cursor:pointer;width:auto}.tr-star[aria-pressed=true]{color:#d4a72c;border-color:#d4a72c}.tr-star.big{position:static;font-size:14px;padding:5px 14px}\n"
       ".tr-msg{color:var(--mu);font-size:12px;padding:8px 16px;border-top:1px solid var(--bd)}.tr-msg:empty{display:none}.tr-empty{padding:32px 16px;text-align:center;color:var(--mu)}\n"
       ".tr-dev{display:grid;grid-template-columns:24px 48px minmax(0,1fr) minmax(0,1fr);gap:16px;align-items:start}.tr-dev .no{color:var(--mu);font-size:12px}.tr-dev .ph{width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font:700 20px/1 inherit}.tr-dev h2{padding:0;font-weight:600}.tr-dev h2:before{content:none}.tr-dev .pr small{display:block;color:var(--mu);font-size:12px;letter-spacing:.02em}.tr-dev .pr b{font-size:16px}.tr-dev .pr p{font-size:12px;max-width:none;padding:0}\n"
       ".tr-it{display:flex;justify-content:space-between;align-items:center;gap:12px;padding-bottom:16px;border-bottom:1px solid var(--bd);margin-bottom:24px}.tr-it h1{font-size:20px;font-weight:400}.tr-it h1 b{font-weight:600}.tr-two{display:grid;grid-template-columns:minmax(0,1fr) 296px;gap:24px}\n"
       ".tr-read{border:1px solid var(--bd);border-radius:6px}.tr-read .hd{padding:12px 16px;border-bottom:1px solid var(--bd);font-weight:600;box-shadow:inset 0 -2px 0 #fd8c73;display:inline-block}.tr-read .rb{padding:24px 32px;font-size:16px;line-height:1.6;border-top:1px solid var(--bd)}.tr-read .rb h2{font-size:24px;font-weight:600;padding-bottom:8px;border-bottom:1px solid var(--bd)!important;margin-bottom:16px}.tr-read .rb p{margin:0 0 16px}\n"
       ".tr-ab h3{font-size:16px;font-weight:600;margin-bottom:12px}.tr-ab p{font-size:16px;margin:0 0 12px}.tr-ab .ln{display:block;font-weight:600;margin-bottom:12px;word-break:break-all}.tr-ab .tg span{display:inline-block;background:rgba(9,105,218,.12);color:var(--ln);border-radius:999px;padding:2px 10px;font-size:12px;font-weight:500;margin:0 4px 6px 0}.tr-ab li{list-style:none;color:var(--mu);margin:6px 0}.tr-ab ul{margin:8px 0 0;padding:16px 0 0;border-top:1px solid var(--bd)}\n"
       ".tr-form{max-width:560px;display:grid;gap:12px}.tr-form label{display:grid;gap:4px;font-weight:600;margin:0}.tr-form input,.tr-form textarea,.tr-form select{background:var(--bg)!important;color:var(--fg)!important;border:1px solid var(--bd)!important;border-radius:6px;padding:6px 12px;font:14px inherit!important;width:100%}.tr-form button{background:#1f883d;color:#fff;border:0;border-radius:6px;padding:8px 16px;font:600 14px inherit;cursor:pointer;width:auto;justify-self:start}\n"
       ".tr-ft{max-width:1012px;margin:0 auto;padding:24px 16px 48px;color:var(--mu);font-size:12px;display:flex;gap:16px;flex-wrap:wrap;border-top:1px solid var(--bd)}.tr-ft a{color:var(--mu)}\n"
       ".trfull .mast,.trfull nav.menu,.trfull .bnav,.trfull .notice,.trfull footer,.trfull .trust,.trfull .mon{display:none!important}.trfull main.wrap{max-width:none;padding:0}\n"
       "@media(max-width:760px){.tr-top .nav{display:none}.tr-row p{max-width:none}.tr-row h2{padding-right:70px}.tr-two{grid-template-columns:1fr}.tr-dev{grid-template-columns:20px 40px minmax(0,1fr)}.tr-dev .pr{grid-column:3}.tr-dev .ph{width:40px;height:40px}.tr-hero{padding:24px 16px}.tr-hero h1{font-size:26px}.tr-in{padding:16px 0}.tr-box{border-radius:0;border-left:0;border-right:0}.tr-it,.tr-two{padding-left:16px;padding-right:16px}.tr-meta .td{margin-left:0;width:100%}}\n")

FULL_JS = '<script>document.documentElement.classList.add("trfull")</script>'
PERIODS = [('daily', '오늘', 'today'), ('weekly', '이번 주', 'week'), ('monthly', '이번 달', 'month')]
COLORS = ['#3178c6', '#3572A5', '#f1e05a', '#dea584', '#701516', '#e34c26', '#563d7c', '#00ADD8']

JS = r"""(function(){var R=document.getElementById("trl");var C=window.__TR||{};var per=C.period||"daily",cat="",KEY={daily:"today",weekly:"week",monthly:"month"},WORD={daily:"오늘",weekly:"이번 주",monthly:"이번 달"},up=false,mine={};
function api(u,o){return fetch(u,o).then(function(r){return r.json()})}function q(s,e){return (e||document).querySelector(s)}function qa(s,e){return [].slice.call((e||document).querySelectorAll(s))}
function fmt(n){return String(n).replace(/\B(?=(\d{3})+(?!\d))/g,",")}
function paint(){if(!R)return;var rows=qa(".tr-row[data-id]",R);rows.forEach(function(r){var d=r.dataset;r.__n=+d[KEY[per]]+(+(d["l"+KEY[per]]||0));r.hidden=!!cat&&d.cat!==cat;var t=q(".td",r);if(t)t.textContent="☆ "+WORD[per]+" 별 "+fmt(r.__n)+"개";var a=q(".tot",r);if(a)a.textContent="☆ "+fmt(+d.stars+(+(d.ltotal||0)))});
rows.sort(function(a,b){return b.__n-a.__n}).forEach(function(r,i){R.appendChild(r);r.hidden=r.hidden||i>=1e9});var n=0;rows.forEach(function(r){if(!r.hidden){n++;if(n>(C.rows||25))r.hidden=true}});var e=q(".tr-empty",R);if(e)e.hidden=n>0;var m=q("#trm");if(m)R.appendChild(m);
var h=q(".tr-hero p");if(h&&h.dataset.t)h.textContent=h.dataset.t.replace("{w}",WORD[per]);
qa(".tr-dev[data-owner]").forEach(function(r){r.__n=+r.dataset[KEY[per]]});var D=q("#trd");if(D){qa(".tr-dev",D).sort(function(a,b){return b.__n-a.__n}).forEach(function(r,i){D.appendChild(r);q(".no",r).textContent=i+1})}}
function star(b){var id=b.dataset.id,msg=q("#trm");if(!up){if(msg)msg.textContent="별은 서버가 켜져 있어야 쌓입니다(python run.py 서버). 지금은 예시 자료의 별 수로 화면만 보입니다.";return}
api("/api/trend/star",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({id:id})}).then(function(j){if(j.error){if(msg)msg.textContent=j.error;return}mine[id]=j.on;load()})}
function apply(j){var S=j.stars||{};qa("[data-id]").forEach(function(r){var s=S[r.dataset.id]||{};r.dataset.ltotal=s.total||0;r.dataset.ltoday=s.today||0;r.dataset.lweek=s.week||0;r.dataset.lmonth=s.month||0});(j.mine||[]).forEach(function(i){mine[i]=true});
qa(".tr-star").forEach(function(b){var on=!!mine[b.dataset.id];b.setAttribute("aria-pressed",on);var c=q("[data-id='"+b.dataset.id+"']");var tot=c?(+c.dataset.stars+(+(c.dataset.ltotal||0))):0;b.textContent=(on?"★ 별 줌":"☆ 별")+(b.classList.contains("big")?"  "+fmt(tot):"")});
if(R&&j.items){j.items.forEach(function(p){if(q(".tr-row[data-id='"+p.id+"']",R))return;var a=document.createElement("article");a.className="tr-row";a.dataset.id=p.id;a.dataset.cat=p.lang||"";a.dataset.stars=0;a.dataset.today=0;a.dataset.week=0;a.dataset.month=0;var s=S[p.id]||{};a.dataset.ltotal=s.total||0;a.dataset.ltoday=s.today||0;a.dataset.lweek=s.week||0;a.dataset.lmonth=s.month||0;
var h=document.createElement("h2"),l=document.createElement("a");l.href=p.url||"#";l.rel="nofollow noopener";l.appendChild(document.createTextNode((p.owner||"익명")+" / "));var b=document.createElement("b");b.textContent=p.name;l.appendChild(b);h.appendChild(l);var bt=document.createElement("button");bt.type="button";bt.className="tr-star";bt.dataset.id=p.id;bt.textContent="☆ 별";bt.onclick=function(){star(bt)};
var d=document.createElement("p");d.textContent=p.desc||"";var m=document.createElement("div");m.className="tr-meta";m.innerHTML='<span class="lg"></span><span class="tot"></span><span class="td"></span>';q(".lg",m).textContent=p.lang||"";a.appendChild(bt);a.appendChild(h);a.appendChild(d);a.appendChild(m);R.appendChild(a)})}paint()}
function load(){return api("/api/trend").then(function(j){if(j&&j.ok){up=true;apply(j)}}).catch(function(){})}
qa(".tr-star").forEach(function(b){b.onclick=function(){star(b)}});var sp=q("#trper"),sc=q("#trcat");if(sp){sp.value=per;sp.onchange=function(){per=sp.value;paint()}}if(sc)sc.onchange=function(){cat=sc.value;paint()};
var u=new URLSearchParams(location.search);if(u.get("since")&&KEY[u.get("since")]){per=u.get("since");if(sp)sp.value=per}
var f=q("#trf");if(f)f.onsubmit=function(e){e.preventDefault();var o={},mg=q(".tr-fm",f);qa("input,textarea,select",f).forEach(function(i){o[i.name]=i.value});api("/api/trend/submit",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(o)}).then(function(j){mg.textContent=j.error||j.message;if(j.ok)f.reset()}).catch(function(){mg.textContent="올리기는 서버가 켜져 있어야 됩니다(python run.py 서버)."})};
var s=q(".tr-top input");if(s)s.oninput=function(){var v=s.value.trim().toLowerCase();qa(".tr-row[data-id]").forEach(function(r){r.style.display=!v||r.textContent.toLowerCase().indexOf(v)>=0?"":"none"})};
paint();api("/api/health").then(function(h){if(h&&h.ok){var a=q(".tr-top .adm");if(a)a.href="/admin/";return load()}}).catch(function(){})})()"""

GUIDE = ('<h2>안내</h2><p>이곳은 요즘 사람들이 반긴 것을 날마다 순위로 보여 줍니다. 마음에 드는 항목에 별(☆)을 주면 그 항목이 올라갑니다.</p>'
         '<p><b>순위는 이렇게 정합니다.</b> 고른 기간(오늘·이번 주·이번 달) 동안 받은 별이 많은 차례입니다. 지금까지 받은 별이 아무리 많아도 그 기간에 받은 별이 적으면 내려갑니다. 그래서 날마다 얼굴이 바뀝니다.</p>'
         '<p><b>별은 한 사람이 한 항목에 한 번</b>입니다. 다시 누르면 거둡니다. 가입은 없습니다.</p><p><b>올리기.</b> 누구나 항목을 올릴 수 있고, 운영자가 확인한 뒤 순위에 들어갑니다. 광고·남의 것을 자기 것처럼 올린 것은 싣지 않습니다.</p>')


def load(B):
    p = os.path.join(B.KITS_DIR, 'trend', 'data', 'items.json')
    if not os.path.exists(p):
        p = os.path.join(B.HERE, 'kits', 'trend', 'data', 'items.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else []


def config(B):
    K = B.S.get('knobs') or {}
    per = {'오늘': 'daily', '이번주': 'weekly', '이번달': 'monthly'}.get(K.get('trend_period'), 'daily')
    return {'period': per, 'rows': int(K.get('trend_rows', 25)), 'theme': {'밝게': 'light', '어둡게': 'dark'}.get(K.get('trend_theme'), 'auto'), 'moderation': 'before'}


def _color(s):
    return COLORS[sum(ord(c) for c in s) % len(COLORS)]


def _av(name, cls='tr-av'):
    return f'<span class="{cls}" style="background:{_color(name)}" title="{E(name)}">{E(name[:1])}</span>'


def top(B, cur):
    b = B.BASE
    nav = ''.join(f'<a class="{"on" if k == cur else ""}" href="{b}{u}">{t}</a>' for k, t, u in (('home', '둘러보기', ''), ('trend', '순위', 'trend/'), ('submit', '올리기', 'trend/submit/'), ('guide', '안내', 'trend/guide/')))
    return (f'<div class="tr-top"><a class="lg" href="{b}">{E(B.S["name"])}</a><span class="sp"></span><input type="search" placeholder="찾기" aria-label="찾기"><a class="adm" href="{b}trend/guide/">로그인</a><a class="up" href="{b}trend/submit/">올리기</a></div>'
            f'<div class="tr-sub"><div>{nav}</div></div>')


def wrap(B, cur, inner, full, hero=None):
    c = config(B)
    h = f'<div class="tr-hero"><h1>{hero[0]}</h1><p data-t="{E(hero[1])}">{E(hero[1].replace("{w}", dict((a, b) for a, b, _ in PERIODS)[c["period"]]))}</p></div>' if hero else ''
    ft = f'<div class="tr-ft"><span>© {E(B.S["name"])}</span><a href="{B.BASE}trend/guide/">안내</a><a href="{B.BASE}privacy/">개인정보</a><a href="{B.BASE}contact/">문의</a><a href="{B.BASE}about/">소개</a></div>'
    return (f'<div class="tr {c["theme"]}">{top(B, cur)}{h}<div class="tr-in">{inner}</div>{ft}</div>'
            f'<script>window.__TR={json.dumps({"period": c["period"], "rows": c["rows"]})};{JS}</script>' + (FULL_JS if full else ''))


def box_head(B, P, on, with_cat=True):
    cats = []
    for p in P:
        if p.get('lang') and p['lang'] not in cats:
            cats.append(p['lang'])
    seg = f'<nav class="tr-seg"><a class="{"on" if on == "items" else ""}" href="{B.BASE}trend/">항목</a><a class="{"on" if on == "makers" else ""}" href="{B.BASE}trend/makers/">만든 사람</a></nav>'
    pick = ('<div class="tr-pick">' + (('<label>분류: <select id="trcat"><option value="">전체</option>' + ''.join(f'<option>{E(c)}</option>' for c in cats) + '</select></label>') if with_cat else '')
            + '<label>기간: <select id="trper">' + ''.join(f'<option value="{k}">{t}</option>' for k, t, _ in PERIODS) + '</select></label></div>')
    return f'<div class="tr-bh">{seg}{pick}</div>'


def row(B, p, key):
    makers = ''.join(_av(m) for m in (p.get('makers') or [])[:5])
    return (f'<article class="tr-row" data-id="{E(p["id"])}" data-cat="{E(p.get("lang", ""))}" data-stars="{int(p.get("stars", 0))}" data-today="{int(p.get("today", 0))}" data-week="{int(p.get("week", 0))}" data-month="{int(p.get("month", 0))}">'
            f'<button type="button" class="tr-star" data-id="{E(p["id"])}" aria-pressed="false">☆ 별</button>'
            f'<h2><a href="{B.BASE}trend/{E(p["id"])}/">{E(p["owner"])} / <b>{E(p["name"])}</b></a></h2><p>{E(p.get("desc", ""))}</p>'
            f'<div class="tr-meta"><span class="lg"><i class="dot" style="background:{_color(p.get("lang", ""))}"></i>{E(p.get("lang", ""))}</span><span class="tot">☆ {int(p.get("stars", 0)):,}</span>'
            + (f'<span>만든 사람 {makers}</span>' if makers else '') + f'<span class="td">☆ 오늘 별 {int(p.get(key, 0)):,}개</span></div></article>')


def list_body(B, full):
    P = load(B); c = config(B); key = dict((a, k) for a, _, k in PERIODS)[c['period']]
    rows = ''.join(row(B, p, key) for p in sorted(P, key=lambda p: -int(p.get(key, 0))))
    inner = f'<div class="tr-box">{box_head(B, P, "items")}<div id="trl">{rows}<div class="tr-empty" hidden>이 분류에는 아직 뜨는 항목이 없습니다.</div><div class="tr-msg" id="trm" role="status"></div></div></div>'
    return wrap(B, 'trend', inner, full, ('지금 뜨는 것', '이곳 사람들이 {w} 가장 반긴 것을 봅니다.'))


def makers_body(B, full):
    P = load(B); M = {}
    for p in P:
        m = M.setdefault(p['owner'], {'today': 0, 'week': 0, 'month': 0, 'best': p})
        for k in ('today', 'week', 'month'):
            m[k] += int(p.get(k, 0))
        if int(p.get('week', 0)) > int(m['best'].get('week', 0)):
            m['best'] = p
    c = config(B); key = dict((a, k) for a, _, k in PERIODS)[c['period']]
    rows = ''
    for i, (o, m) in enumerate(sorted(M.items(), key=lambda x: -x[1][key]), 1):
        b = m['best']
        rows += (f'<article class="tr-row tr-dev" data-owner="{E(o)}" data-today="{m["today"]}" data-week="{m["week"]}" data-month="{m["month"]}"><span class="no">{i}</span>{_av(o, "ph")}<h2><a href="{B.BASE}trend/{E(b["id"])}/">{E(o)}</a></h2>'
                 f'<div class="pr"><small>🔥 대표 항목</small><b><a href="{B.BASE}trend/{E(b["id"])}/">{E(b["name"])}</a></b><p>{E(b.get("desc", "")[:90])}</p></div></article>')
    inner = f'<div class="tr-box">{box_head(B, P, "makers", False)}<div id="trd">{rows}</div></div>'
    return wrap(B, 'trend', inner, full, ('지금 뜨는 것', '{w} 뜨는 것을 만든 사람들입니다.'))


def item_body(B, p, full):
    tags = ''.join(f'<span>{E(t)}</span>' for t in p.get('tags', []))
    read = ''.join(f'<p>{E(x)}</p>' for x in (p.get('readme') or [p.get('desc', '')]))
    link = f'<a class="ln" href="{E(p["url"])}" rel="nofollow noopener">🔗 {E(p["url"].split("//")[-1])}</a>' if p.get('url') else ''
    inner = (f'<div data-id="{E(p["id"])}" data-stars="{int(p.get("stars", 0))}"><div class="tr-it"><h1><a href="{B.BASE}trend/">{E(p["owner"])}</a> / <b>{E(p["name"])}</b></h1><button type="button" class="tr-star big" data-id="{E(p["id"])}" aria-pressed="false">☆ 별  {int(p.get("stars", 0)):,}</button></div>'
             f'<div class="tr-two"><div class="tr-read"><span class="hd">소개</span><div class="rb"><h2>{E(p["name"])}</h2>{read}</div></div>'
             f'<aside class="tr-ab"><h3>About</h3><p>{E(p.get("desc", ""))}</p>{link}<div class="tg">{tags}</div><ul><li>☆ 별 {int(p.get("stars", 0)):,}개</li><li>오늘 {int(p.get("today", 0)):,} · 이번 주 {int(p.get("week", 0)):,} · 이번 달 {int(p.get("month", 0)):,}</li><li>분류: {E(p.get("lang", ""))}</li><li>만든 사람: {E(" · ".join(p.get("makers") or [p["owner"]]))}</li></ul></aside></div><div class="tr-msg" id="trm" role="status"></div></div>')
    return wrap(B, 'trend', inner, full)


def submit_body(B, full):
    cats = []
    for p in load(B):
        if p.get('lang') and p['lang'] not in cats:
            cats.append(p['lang'])
    inner = ('<h2 style="font-size:24px;font-weight:600;margin-bottom:16px">항목 올리기</h2><form class="tr-form" id="trf"><label>이름<input name="name" required maxlength="60"></label><label>만든이<input name="owner" maxlength="30" placeholder="비우면 익명"></label>'
             '<label>한 줄 설명<textarea name="desc" rows="3" required maxlength="200"></textarea></label><label>주소<input name="url" type="url" placeholder="https://…" required></label>'
             '<label>분류<select name="lang">' + ''.join(f'<option>{E(c)}</option>' for c in cats) + '</select></label><button type="submit">올리기</button><p class="tr-fm" role="status" style="color:var(--mu)"></p></form>'
             '<p style="color:var(--mu);margin-top:16px">운영자가 확인한 뒤 순위에 들어갑니다. 처음에는 별 0개로 시작합니다.</p>')
    return wrap(B, 'submit', inner, full)


def pages(B):
    if not B.part('trend', False):
        return []
    P = load(B); full = B.S.get('kind', '').startswith('날마다 순위')
    json.dump(config(B), open(os.path.join(B.OUT, 'trend.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    u = [B.page('trend', f'지금 뜨는 것 — {B.S["name"]}', '기간 동안 별을 많이 받은 차례로 보는 순위', list_body(B, full)),
         B.page('trend/makers', f'뜨는 것을 만든 사람 — {B.S["name"]}', '뜨는 항목을 만든 사람 순위', makers_body(B, full)),
         B.page('trend/submit', f'항목 올리기 — {B.S["name"]}', '순위에 항목을 올리기', submit_body(B, full), noindex=True),
         B.page('trend/guide', f'안내 — {B.S["name"]}', '순위를 정하는 법과 별·올리기 안내', wrap(B, 'guide', f'<div style="max-width:720px;font-size:16px;line-height:1.7">{GUIDE}</div>', full))]
    for p in P:
        u.append(B.page(f'trend/{p["id"]}', f'{p["owner"]} / {p["name"]} — {B.S["name"]}', p.get('desc', p['name'])[:150], item_body(B, p, full)))
    return u


def home_body(B):
    return list_body(B, True)
