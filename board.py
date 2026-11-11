# -*- coding: utf-8 -*-
"""게시판(링크+추천) 틀 — 레퍼런스: 해커 뉴스. 글자 위주 목록·추천(▲)·점수÷시간 순위·새 글/묻는 글/보여 주기 탭·들여쓴 댓글·접기·지침 쪽·글 올리기.
방문자가 글을 올리는 종류라 서버(python run.py 서버)가 있어야 돈다. 서버가 꺼져 있으면 예시 글(kits/board/data/sample.json)로 화면만 보인다.
손잡이: 순위셈법(시간이 지나면 얼마나 빨리 내려가나)·한쪽줄수·공개방식 → build 가 board.json 으로 써 주고 서버와 화면이 함께 읽는다. 파이썬 기본 기능만 쓴다."""
import html, json, os

E = html.escape

CSS = (".bd{font:16px/1.6 var(--sans,system-ui);max-width:860px;margin:18px auto 0}.bd-tabs{display:flex;gap:4px;flex-wrap:wrap;border-bottom:2px solid var(--pri,#111);margin:0 0 6px}.bd-tabs a{padding:8px 14px;font-weight:700;color:var(--ink,#111);cursor:pointer}"
       ".bd-tabs a.on{background:var(--pri,#111);color:#fff}.bd-row{display:grid;grid-template-columns:34px 30px 1fr;gap:4px;padding:8px 0;border-bottom:1px solid var(--hair,#e5e5e5);align-items:start}.bd-n{color:var(--mu,#666);text-align:right;padding-top:2px}"
       ".bd-v{border:0;background:none;cursor:pointer;font-size:18px;line-height:1.2;color:var(--mu,#666);width:auto;padding:0}.bd-v.on{color:var(--pri,#c2410c)}.bd-t{font-weight:700;font-size:17px;color:var(--ink,#111)}.bd-h{color:var(--mu,#666);font-size:14px;margin-left:6px}"
       ".bd-m{display:block;color:var(--mu,#666);font-size:14px}.bd-m a{color:var(--mu,#666);text-decoration:underline;cursor:pointer}.bd form{display:grid;gap:8px;margin:14px 0;max-width:640px}.bd input,.bd textarea{font:16px var(--sans,system-ui);padding:10px;border:1px solid var(--hair,#ccc);border-radius:6px;width:100%}"
       ".bd textarea{min-height:90px}.bd button.go{font:700 15px var(--sans,system-ui);padding:10px 16px;border:0;border-radius:6px;background:var(--pri,#111);color:#fff;cursor:pointer;width:auto;justify-self:start}.bd-msg{font-size:14px;min-height:1.2em;color:#0b5d2f}"
       ".bd-c{border-left:2px solid var(--hair,#ddd);padding:6px 0 6px 12px;margin:8px 0}.bd-c .bd-m b{color:var(--ink,#111)}.bd-c p{margin:4px 0}.bd-fold{cursor:pointer;color:var(--mu,#666)}.bd-off{background:var(--bgs,#f3f3f3);border:1px dashed var(--mu,#999);border-radius:8px;padding:10px 14px;font-size:14px;margin:0 0 10px}"
       ".bd-more{display:inline-block;margin:12px 0;font-weight:700;cursor:pointer}@media(max-width:560px){.bd-row{grid-template-columns:26px 26px 1fr}.bd-t{font-size:16px}}\n")

JS = r"""(function(){
var root=document.getElementById("bd");if(!root)return;var BASE="__BASE__",CFG={gravity:1.8,per_page:30,moderation:"before"},up=false,SAMPLE=[];
function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})}
function api(p,o){return fetch(p,o||{}).then(function(r){return r.json()})}
function post(p,b){return api(p,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b)})}
function host(u){try{return new URL(u).hostname.replace(/^www[.]/,"")}catch(e){return ""}}
function ago(h){if(h<1)return Math.max(1,Math.round(h*60))+"분 전";if(h<24)return Math.round(h)+"시간 전";return Math.round(h/24)+"일 전"}
function q(k){var m=location.search.match(new RegExp("[?&]"+k+"=([^&]*)"));return m?decodeURIComponent(m[1]):""}
function rank(L){return L.map(function(p){p.score=p.points/Math.pow(p.hours+2,CFG.gravity);return p}).sort(function(a,b){return b.score-a.score})}
function tabs(cur){var T=[["top","인기"],["new","새 글"],["ask","묻는 글"],["show","보여 주기"],["submit","글 올리기"],["guide","지침"]];
 return '<div class="bd-tabs">'+T.map(function(t){return '<a class="'+(t[0]===cur?"on":"")+'" href="'+(t[0]==="guide"?BASE+"board/guide/":BASE+"board/?v="+t[0])+'">'+t[1]+'</a>'}).join("")+'</div>'}
function offnote(){return up?"":'<p class="bd-off">지금은 서버가 꺼져 있어 예시 글로 화면만 보입니다. 글 올리기·추천·댓글은 서버가 켜져 있을 때 됩니다(python run.py 서버).</p>'}
function row(p,i){var h=p.url?host(p.url):"";return '<div class="bd-row"><span class="bd-n">'+(i+1)+'.</span><button class="bd-v" data-id="'+esc(p.id)+'" title="추천" aria-label="추천">▲</button><div><a class="bd-t" href="'+(p.url?esc(p.url):BASE+"board/?id="+encodeURIComponent(p.id))+'"'+(p.url?' rel="noopener nofollow" target="_blank"':'')+'>'+esc(p.title)+'</a>'+(h?'<span class="bd-h">('+esc(h)+')</span>':'')+
 '<span class="bd-m"><b class="pt">'+p.points+'</b>점 · '+esc(p.name)+' · '+ago(p.hours)+' · <a href="'+BASE+'board/?id='+encodeURIComponent(p.id)+'">댓글 '+p.comments+'</a> · <a class="fl" data-id="'+esc(p.id)+'">신고</a></span></div></div>'}
function bind(){root.querySelectorAll(".bd-v").forEach(function(b){b.onclick=function(){if(!up)return;post("/api/board/vote",{id:b.dataset.id}).then(function(j){if(j.ok){b.classList.add("on");b.parentNode.querySelector(".pt").textContent=j.points}})}});
 root.querySelectorAll("a.fl").forEach(function(a){a.onclick=function(){if(!up)return;post("/api/board/flag",{id:a.dataset.id}).then(function(){a.textContent="신고했습니다"})}})}
function list(v){var kind=(v==="ask"||v==="show")?v:"all",sort=v==="new"?"new":"top",pg=+q("p")||1;
 function draw(L,more){root.innerHTML=tabs(v)+offnote()+(L.length?L.map(function(p,i){return row(p,(pg-1)*CFG.per_page+i)}).join(""):'<p>아직 글이 없습니다. 「글 올리기」에서 첫 글을 올려 보세요.</p>')+(more?'<a class="bd-more" href="'+BASE+'board/?v='+v+'&p='+(pg+1)+'">더 보기</a>':'');bind()}
 if(up)api("/api/board?sort="+sort+"&kind="+kind+"&page="+pg).then(function(j){draw(j.posts||[],j.more)});
 else{var L=SAMPLE.filter(function(p){return kind==="all"||p.kind===kind});L=sort==="new"?L.slice().sort(function(a,b){return a.hours-b.hours}):rank(L.slice());draw(L.slice((pg-1)*CFG.per_page,pg*CFG.per_page),L.length>pg*CFG.per_page)}}
function submit(){root.innerHTML=tabs("submit")+offnote()+'<form id="bdf"><input name="title" maxlength="120" required placeholder="제목 (묻는 글은 「묻습니다:」, 만든 것을 보여 주는 글은 「보여 줍니다:」로 시작)"><input name="url" maxlength="300" placeholder="링크 주소(https://…) — 글만 올릴 때는 비워 둠"><textarea name="text" maxlength="2000" placeholder="글(링크가 있으면 비워도 됨)"></textarea><input name="name" maxlength="30" placeholder="이름(비우면 익명)"><button class="go" type="submit">올리기</button><p class="bd-msg" role="status"></p></form><p class="bd-m">올리기 전에 <a href="'+BASE+'board/guide/">지침</a>을 읽어 주세요.'+(CFG.moderation==="before"?" 올린 글은 운영자가 승인하면 보입니다.":"")+'</p>';
 var f=document.getElementById("bdf");f.onsubmit=function(e){e.preventDefault();var m=f.querySelector(".bd-msg");if(!up){m.textContent="서버가 켜져 있을 때 됩니다.";return}post("/api/board",{title:f.title.value,url:f.url.value,text:f.text.value,name:f.name.value}).then(function(j){m.textContent=j.message||j.error;m.style.color=j.ok?"#0b5d2f":"#a11a12";if(j.ok)f.reset()})}}
function item(id){function draw(p,C){var kids={};C.forEach(function(c){(kids[c.parent||""]=kids[c.parent||""]||[]).push(c)});
 function tree(par){return (kids[par]||[]).map(function(c){return '<div class="bd-c" id="c'+esc(c.id)+'"><span class="bd-m"><b>'+esc(c.name)+'</b> · '+ago(c.hours)+' · <a class="bd-fold">[–]</a> · <a class="re" data-id="'+esc(c.id)+'">답글</a></span><div class="bd-b"><p>'+esc(c.body)+'</p>'+tree(c.id)+'</div></div>'}).join("")}
 root.innerHTML=tabs("")+offnote()+row(p,0)+(p.text?'<p>'+esc(p.text)+'</p>':'')+'<form id="bdc"><input type="hidden" name="parent" value=""><textarea name="body" maxlength="1000" required placeholder="댓글"></textarea><input name="name" maxlength="30" placeholder="이름(비우면 익명)"><button class="go" type="submit">댓글 달기</button><p class="bd-msg" role="status"></p></form><div id="bdt">'+tree("")+'</div>';bind();
 root.querySelectorAll(".bd-fold").forEach(function(a){a.onclick=function(){var b=a.closest(".bd-c").querySelector(".bd-b"),h=b.style.display==="none";b.style.display=h?"":"none";a.textContent=h?"[–]":"[+]"}});
 var f=document.getElementById("bdc");root.querySelectorAll("a.re").forEach(function(a){a.onclick=function(){f.parent.value=a.dataset.id;f.body.placeholder="답글";f.body.focus()}});
 f.onsubmit=function(e){e.preventDefault();var m=f.querySelector(".bd-msg");if(!up){m.textContent="서버가 켜져 있을 때 됩니다.";return}post("/api/board/comment",{id:id,parent:f.parent.value,body:f.body.value,name:f.name.value}).then(function(j){m.textContent=j.message||j.error;if(j.ok){f.body.value="";if(j.shown)item(id)}})}}
 if(up)api("/api/board/item?id="+encodeURIComponent(id)).then(function(j){if(j.post)draw(j.post,j.comments||[]);else root.innerHTML=tabs("")+"<p>글을 찾지 못했습니다.</p>"});
 else{var p=SAMPLE.filter(function(x){return x.id===id})[0];if(p)draw(p,p.sample_comments||[]);else root.innerHTML=tabs("")+"<p>글을 찾지 못했습니다.</p>"}}
function go(){var id=q("id"),v=q("v")||"top";if(id)item(id);else if(v==="submit")submit();else list(v)}
Promise.all([api(BASE+"board.json").catch(function(){return null}),api(BASE+"board_sample.json").catch(function(){return []}),api("/api/health").catch(function(){return {}})]).then(function(r){if(r[0])CFG=r[0];SAMPLE=r[1]||[];up=!!(r[2]&&r[2].ok&&(r[2].features||[]).indexOf("board")>=0);document.documentElement.setAttribute("data-board",up?"server":"sample");go()});
})();"""

GUIDE = ('<h1>지침</h1><p>이 게시판은 한 가지 주제에 관심 있는 사람들이 링크와 글을 올리고, 추천으로 순서를 정하고, 댓글로 이야기하는 곳입니다.</p>'
         '<h2>올릴 것</h2><ul><li>이 게시판의 주제에 맞고, 읽은 사람이 무언가를 알게 되는 글과 링크</li><li>직접 만든 것은 「보여 줍니다:」, 물어볼 것은 「묻습니다:」로 제목을 시작</li></ul>'
         '<h2>올리지 않을 것</h2><ul><li>광고·도배·낚시 제목, 같은 링크를 되풀이해 올리기</li><li>남을 깎아내리는 말, 개인정보</li></ul>'
         '<h2>순서가 정해지는 방식</h2><p>추천을 받은 점수를 올린 뒤 지난 시간으로 나누어 순서를 정합니다. 시간이 지나면 저절로 내려가고 새 글이 올라옵니다. 신고가 쌓이거나 지침에 어긋나면 운영자가 숨길 수 있습니다.</p>'
         '<h2>운영</h2><p>올린 글과 댓글은 운영자가 확인합니다. 숨긴 글은 지우지 않고 보이지 않게만 합니다. 문의는 문의 쪽으로 보내 주세요.</p>')


def config(B):
    K = B.S.get('knobs') or {}
    return {'gravity': float(K.get('gravity', 1.8)), 'per_page': int(K.get('per_page', 30)), 'moderation': 'after' if K.get('moderation') == '바로' else 'before'}


def shell(B):
    return f'<div class="bd" id="bd"><p>불러오는 중…</p></div><script>{JS.replace("__BASE__", B.BASE)}</script>'


def pages(B):
    if not B.part('board', False):
        return []
    json.dump(config(B), open(os.path.join(B.OUT, 'board.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    sp = os.path.join(B.KITS_DIR, 'board', 'data', 'sample.json')
    if not os.path.exists(sp):
        sp = os.path.join(B.HERE, 'kits', 'board', 'data', 'sample.json')
    sample = json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else []
    json.dump(sample, open(os.path.join(B.OUT, 'board_sample.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    u = [B.page('board', f'게시판 — {B.S["name"]}', '링크와 글을 올리고 추천으로 순서를 정하는 게시판', shell(B)),
         B.page('board/guide', f'지침 — {B.S["name"]}', '게시판에 올릴 것과 올리지 않을 것, 순서가 정해지는 방식', f'<div class="page">{GUIDE}</div>')]
    return u


def home_body(B):
    return shell(B)
