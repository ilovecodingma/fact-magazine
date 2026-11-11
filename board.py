# -*- coding: utf-8 -*-
"""게시판(링크+추천) 틀 — 레퍼런스: 해커 뉴스(news.ycombinator.com). 2026-11-11 에 첫 화면·새 글·글 쪽·news.css·FAQ·지침 쪽을 직접 받아 읽고 그 짜임을 따랐다(잰 값은 참고/레퍼런스.json 과 참고/조각/해커뉴스.json).
본에서 따른 것: 주황 머리 띠(이름 + new·ask·show·submit) · 옅은 베이지 바탕 · 폭 85% · 한 줄 = 순번(오른쪽 정렬)·▲·제목(사이트) / 아랫줄 = N점 · 이름 · 지난 시간 | 숨기기 | 댓글 N · 줄 사이 5px · 한 쪽 30줄 · 「더 보기」
              글 쪽 = 제목 줄 + 댓글 입력칸(8줄)이 댓글보다 위 + 한 단계에 40px 씩 들여쓴 댓글(휴대폰 12px) · 댓글 머리 「이름 시간 | 다음 [–]」 · 접으면 「[N개 더]」 · 댓글 아래 「답글」 · 맨 아래 지침·문의 링크와 검색칸
본과 다르게 둔 것: 글자는 한글이 읽히게 손잡이 「게시판글자」로 고른다(본 = 제목 10pt·아랫줄 7pt / 크게 = 16px·13px). 로그인·카르마·댓글 내리기(▼)·past·jobs 는 없다. 올린 글은 기본 「승인 뒤 공개」(본은 바로 공개).
방문자가 글을 올리는 종류라 서버(python run.py 서버)가 있어야 돈다. 서버가 꺼져 있으면 예시 글로 화면만 보인다. 파이썬 기본 기능만 쓴다."""
import html, json, os

E = html.escape

CSS = (".bd{--bdt:13.33px;--bds:9.33px;--bdc:12px;--bdh:10.67px;width:85%;min-width:0;margin:8px auto 0;background:#f6f6ef;color:#828282;font:var(--bdt)/1.35 Verdana,Geneva,'Malgun Gothic',sans-serif}"
       ".bd.big{--bdt:16px;--bds:13px;--bdc:15px;--bdh:13px}.bd a{color:#000;text-decoration:none}.bd a:visited{color:#828282}"
       ".bd-top{background:#ff6600;padding:2px 4px;display:flex;gap:4px;align-items:center;line-height:1.5;color:#222;flex-wrap:wrap}.bd-top b{margin-right:5px}.bd-top a{color:#000}.bd-top a.on{color:#fff}.bd-top .sep{color:#222}"
       ".bd-logo{display:inline-block;width:18px;height:18px;border:1px solid #fff;color:#fff;font:700 13px/18px Verdana,sans-serif;text-align:center;margin-right:4px}"
       ".bd-body{padding:10px 0 4px}.bd-row{display:grid;grid-template-columns:34px 18px 1fr;margin:0 0 5px}.bd-n{text-align:right;color:#828282}.bd-v{border:0;background:none;cursor:pointer;width:10px;height:10px;margin:3px 4px 6px;padding:0;position:relative}"
       ".bd-v::before{content:'';position:absolute;left:0;top:0;border-left:5px solid transparent;border-right:5px solid transparent;border-bottom:10px solid #9a9a9a}.bd-v.on::before{border-bottom-color:#ff6600}.bd-v.gone{visibility:hidden}"
       ".bd-t{color:#000}.bd-h{font-size:var(--bdh);color:#828282}.bd-h a{color:#828282}.bd-m{display:block;font-size:var(--bds);color:#828282}.bd-m a{color:#828282;cursor:pointer}.bd-m a:hover{text-decoration:underline}"
       ".bd-more{display:inline-block;margin:8px 0 10px 52px;color:#828282!important;text-decoration:underline!important;cursor:pointer}.bd-text{margin:8px 0 8px 52px;color:#000;max-width:800px}"
       ".bd form{margin:6px 0 14px 52px;display:block}.bd textarea{font:var(--bdt) monospace;width:min(100%,560px);display:block;margin:0 0 6px}.bd input[type=text]{font:var(--bdt) monospace;width:min(100%,420px);display:block;margin:0 0 6px;padding:2px}"
       ".bd button.go{font:var(--bdt) Verdana,Geneva,sans-serif;padding:1px 6px;cursor:pointer;width:auto}.bd-msg{font-size:var(--bds);min-height:1.2em;color:#0b5d2f;margin:4px 0 0}"
       ".bd-c{margin:0 0 10px;display:grid;grid-template-columns:auto 14px 1fr}.bd-ch{font-size:var(--bdh);color:#828282}.bd-ch a{color:#828282;cursor:pointer}.bd-cb{font-size:var(--bdc);color:#000;max-width:1215px;overflow-wrap:anywhere}.bd-cb p{margin:6px 0 0}"
       ".bd-re{font-size:var(--bds);text-decoration:underline!important;color:#000!important;cursor:pointer}.bd-off{border:1px dashed #828282;padding:6px 10px;margin:0 8px 10px 8px;color:#444;font-size:var(--bds)}"
       ".bd-foot{border-top:2px solid #ff6600;margin-top:10px;padding:10px 0 14px;text-align:center;font-size:var(--bdh)}.bd-foot a{color:#828282}.bd-foot input{font:var(--bdt) monospace;width:160px}"
       ".bdfull .mast,.bdfull nav.menu,.bdfull .bnav,.bdfull .notice{display:none!important}.bdfull main.wrap{max-width:none;padding:0}"
       "@media(max-width:750px){.bd{width:100%;--bdt:14.67px;--bds:12px}.bd.big{--bdt:16px;--bds:13px}.bd-row{grid-template-columns:28px 20px 1fr}.bd-v{transform:scale(1.3)}.bd form,.bd-text,.bd-more{margin-left:8px}}\n")

JS = r"""(function(){
var root=document.getElementById("bd");if(!root)return;var BASE="__BASE__",NAME="__NAME__",CFG={gravity:1.8,per_page:30,moderation:"before",font:"ref",full:false},up=false,SAMPLE=[];
function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})}
function api(p,o){return fetch(p,o||{}).then(function(r){return r.json()})}
function post(p,b){return api(p,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b)})}
function host(u){try{return new URL(u).hostname.replace(/^www[.]/,"")}catch(e){return ""}}
function ago(h){if(h<1)return Math.max(1,Math.round(h*60))+"분 전";if(h<24)return Math.round(h)+"시간 전";return Math.round(h/24)+"일 전"}
function q(k){var m=location.search.match(new RegExp("[?&]"+k+"=([^&]*)"));return m?decodeURIComponent(m[1]):""}
function hid(){try{return JSON.parse(localStorage.getItem("fm_bd_hide")||"[]")}catch(e){return[]}}
function rank(L){return L.map(function(p){p.score=p.points/Math.pow(p.hours+2,CFG.gravity);return p}).sort(function(a,b){return b.score-a.score})}
function top(cur){var T=[["new","새 글"],["ask","묻는 글"],["show","보여 주기"],["submit","글 올리기"]];
 return '<div class="bd-top"><span class="bd-logo">'+esc(NAME.charAt(0))+'</span><b><a href="'+BASE+'board/">'+esc(NAME)+'</a></b>'+T.map(function(t){return '<a class="'+(t[0]===cur?"on":"")+'" href="'+BASE+'board/?v='+t[0]+'">'+t[1]+'</a>'}).join('<span class="sep">|</span>')+'</div>'}
function foot(){return '<div class="bd-foot"><a href="'+BASE+'board/guide/">지침</a> | <a href="'+BASE+'about/">소개</a> | <a href="'+BASE+'contact/">문의</a> | <a href="'+BASE+'privacy/">개인정보</a><br><br><form action="'+BASE+'search/" method="get" style="margin:0">찾기: <input type="text" name="q" size="17"></form></div>'}
function offnote(){return up?"":'<p class="bd-off">지금은 서버가 꺼져 있어 예시 글로 화면만 보입니다. 글 올리기·추천·댓글은 서버가 켜져 있을 때 됩니다(python run.py 서버).</p>'}
function row(p,i,single){var h=p.url?host(p.url):"";return '<div class="bd-row" data-id="'+esc(p.id)+'"><span class="bd-n">'+(single?"":(i+1)+".")+'</span><button class="bd-v" data-id="'+esc(p.id)+'" title="추천" aria-label="추천"></button><div><a class="bd-t" href="'+(p.url?esc(p.url):BASE+"board/?id="+encodeURIComponent(p.id))+'"'+(p.url?' rel="noopener nofollow"':'')+'>'+esc(p.title)+'</a>'+(h?' <span class="bd-h">('+esc(h)+')</span>':'')+
 '<span class="bd-m"><span class="pt">'+p.points+'</span>점 · '+esc(p.name)+' · <a href="'+BASE+'board/?id='+encodeURIComponent(p.id)+'">'+ago(p.hours)+'</a> | <a class="hd" data-id="'+esc(p.id)+'">숨기기</a>'+(single?' | <a class="fl" data-id="'+esc(p.id)+'">신고</a>':'')+' | <a href="'+BASE+'board/?id='+encodeURIComponent(p.id)+'">'+(p.comments?"댓글 "+p.comments+"개":"이야기하기")+'</a></span></div></div>'}
function bind(){root.querySelectorAll(".bd-v").forEach(function(b){b.onclick=function(){if(!up)return;post("/api/board/vote",{id:b.dataset.id}).then(function(j){if(j.ok){b.classList.add("on");var r=b.closest(".bd-row");if(r)r.querySelector(".pt").textContent=j.points}})}});
 root.querySelectorAll("a.hd").forEach(function(a){a.onclick=function(){var L=hid();L.push(a.dataset.id);try{localStorage.setItem("fm_bd_hide",JSON.stringify(L.slice(-300)))}catch(e){}var r=a.closest(".bd-row");if(r)r.remove()}});
 root.querySelectorAll("a.fl").forEach(function(a){a.onclick=function(){if(!up)return;post("/api/board/flag",{id:a.dataset.id}).then(function(){a.textContent="신고했습니다"})}})}
function frame(cur,inner){root.className="bd"+(CFG.font==="big"?" big":"");root.innerHTML=top(cur)+'<div class="bd-body">'+offnote()+inner+'</div>'+foot();bind()}
function list(v){var kind=(v==="ask"||v==="show")?v:"all",sort=v==="new"?"new":"top",pg=+q("p")||1,H=hid();
 function draw(L,more){L=L.filter(function(p){return H.indexOf(p.id)<0});frame(v==="top"?"":v,(L.length?L.map(function(p,i){return row(p,(pg-1)*CFG.per_page+i)}).join(""):'<p style="margin-left:52px">아직 글이 없습니다. 「글 올리기」에서 첫 글을 올려 보세요.</p>')+(more?'<a class="bd-more" href="'+BASE+'board/?v='+v+'&p='+(pg+1)+'">더 보기</a>':''))}
 if(up)api("/api/board?sort="+sort+"&kind="+kind+"&page="+pg).then(function(j){draw(j.posts||[],j.more)});
 else{var L=SAMPLE.filter(function(p){return kind==="all"||p.kind===kind});L=sort==="new"?L.slice().sort(function(a,b){return a.hours-b.hours}):rank(L.slice());draw(L.slice((pg-1)*CFG.per_page,pg*CFG.per_page),L.length>pg*CFG.per_page)}}
function submit(){frame("submit",'<form id="bdf"><input type="text" name="title" maxlength="120" required placeholder="제목" aria-label="제목"><input type="text" name="url" maxlength="300" placeholder="링크 주소(https://…)" aria-label="링크 주소"><textarea name="text" rows="4" cols="49" maxlength="2000" placeholder="글(링크가 있으면 비워도 됩니다)" aria-label="글"></textarea><input type="text" name="name" maxlength="30" placeholder="이름(비우면 익명)" aria-label="이름"><button class="go" type="submit">올리기</button><p class="bd-msg" role="status"></p></form><p class="bd-m" style="margin-left:52px">링크를 올릴 때는 글 칸을 비워 둡니다. 물어볼 것은 제목을 「묻습니다:」로, 직접 만든 것을 보여 줄 때는 「보여 줍니다:」로 시작하면 그 목록에 들어갑니다. 올리기 전에 <a href="'+BASE+'board/guide/" style="text-decoration:underline">지침</a>을 읽어 주세요.'+(CFG.moderation==="before"?" 올린 글은 운영자가 승인하면 보입니다.":"")+'</p>');
 var f=document.getElementById("bdf");f.onsubmit=function(e){e.preventDefault();var m=f.querySelector(".bd-msg");if(!up){m.textContent="서버가 켜져 있을 때 됩니다.";return}post("/api/board",{title:f.title.value,url:f.url.value,text:f.text.value,name:f.name.value}).then(function(j){m.textContent=j.message||j.error;m.style.color=j.ok?"#0b5d2f":"#a11a12";if(j.ok)f.reset()})}}
function item(id){function draw(p,C){var kids={};C.forEach(function(c){(kids[c.parent||""]=kids[c.parent||""]||[]).push(c)});var order=[];
 function count(cid){var n=1;(kids[cid]||[]).forEach(function(k){n+=count(k.id)});return n}
 function walk(par,depth){(kids[par]||[]).forEach(function(c){order.push([c,depth]);walk(c.id,depth+1)})}walk("",0);
 var step=window.innerWidth<=750?12:40;
 var cs=order.map(function(x,i){var c=x[0],d=x[1];return '<div class="bd-c" id="c'+esc(c.id)+'" data-d="'+d+'" data-n="'+count(c.id)+'"><span style="width:'+(d*step)+'px"></span><button class="bd-v gone" tabindex="-1" aria-hidden="true"></button><div><span class="bd-ch">'+esc(c.name)+' '+ago(c.hours)+(order[i+1]?' | <a href="#c'+esc(order[i+1][0].id)+'">다음</a>':'')+' <a class="bd-fold">[–]</a></span><div class="bd-cb"><p>'+esc(c.body)+'</p><p><a class="bd-re" data-id="'+esc(c.id)+'">답글</a></p></div></div></div>'}).join("");
 frame("",row(p,0,true)+(p.text?'<div class="bd-text">'+esc(p.text)+'</div>':'')+'<form id="bdc"><input type="hidden" name="parent" value=""><textarea name="body" rows="8" cols="80" maxlength="1000" required aria-label="댓글"></textarea><input type="text" name="name" maxlength="30" placeholder="이름(비우면 익명)" aria-label="이름"><button class="go" type="submit">댓글 달기</button><p class="bd-msg" role="status"></p></form><div id="bdt">'+cs+'</div>');
 root.querySelectorAll(".bd-fold").forEach(function(a){a.onclick=function(){var me=a.closest(".bd-c"),d=+me.dataset.d,shut=a.textContent==="[–]";me.querySelector(".bd-cb").style.display=shut?"none":"";a.textContent=shut?"["+me.dataset.n+"개 더]":"[–]";
  var n=me.nextElementSibling;while(n&&n.classList.contains("bd-c")&&+n.dataset.d>d){n.style.display=shut?"none":"";n=n.nextElementSibling}}});
 var f=document.getElementById("bdc");root.querySelectorAll("a.bd-re").forEach(function(a){a.onclick=function(){f.parent.value=a.dataset.id;f.body.placeholder="답글";f.body.focus();window.scrollTo(0,0)}});
 f.onsubmit=function(e){e.preventDefault();var m=f.querySelector(".bd-msg");if(!up){m.textContent="서버가 켜져 있을 때 됩니다.";return}post("/api/board/comment",{id:id,parent:f.parent.value,body:f.body.value,name:f.name.value}).then(function(j){m.textContent=j.message||j.error;if(j.ok){f.body.value="";if(j.shown)item(id)}})}}
 if(up)api("/api/board/item?id="+encodeURIComponent(id)).then(function(j){if(j.post)draw(j.post,j.comments||[]);else frame("","<p style='margin-left:52px'>글을 찾지 못했습니다.</p>")});
 else{var p=SAMPLE.filter(function(x){return x.id===id})[0];if(p)draw(p,p.sample_comments||[]);else frame("","<p style='margin-left:52px'>글을 찾지 못했습니다.</p>")}}
function go(){var id=q("id"),v=q("v")||"top";if(id)item(id);else if(v==="submit")submit();else list(v)}
Promise.all([api(BASE+"board.json").catch(function(){return null}),api(BASE+"board_sample.json").catch(function(){return []}),api("/api/health").catch(function(){return {}})]).then(function(r){if(r[0])CFG=r[0];SAMPLE=r[1]||[];up=!!(r[2]&&r[2].ok&&(r[2].features||[]).indexOf("board")>=0);
 document.documentElement.setAttribute("data-board",up?"server":"sample");if(CFG.full)document.documentElement.classList.add("bdfull");go()});
})();"""

GUIDE = ('<h1>지침</h1><p>이 게시판은 한 가지 주제에 관심 있는 사람들이 링크와 글을 올리고, 추천으로 순서를 정하고, 댓글로 이야기하는 곳입니다.</p>'
         '<h2>올릴 것</h2><ul><li>이 게시판의 주제에 맞고, 읽은 사람의 궁금증을 채워 주는 글과 링크</li><li>직접 만든 것은 「보여 줍니다:」, 물어볼 것은 「묻습니다:」로 제목을 시작</li><li>다른 곳에서 본 것을 올릴 때는 처음 나온 곳의 주소</li></ul>'
         '<h2>올릴 때</h2><ul><li>제목을 눈에 띄게 하려고 느낌표를 붙이거나 「대단한」 같은 말을 넣지 않기</li><li>제목에 사이트 이름을 넣지 않기(링크 뒤에 사이트가 따로 보입니다)</li><li>이 게시판을 홍보에만 쓰지 않기. 자기 것을 올려도 되지만 가끔만</li></ul>'
         '<h2>올리지 않을 것</h2><ul><li>광고·도배·낚시 제목, 같은 링크를 되풀이해 올리기</li><li>남을 깎아내리는 말, 개인정보</li></ul>'
         '<h2>순서가 정해지는 방식</h2><p>추천 점수를 올린 뒤 지난 시간의 거듭제곱으로 나누어 순서를 정합니다. 시간이 지나면 저절로 내려가고 새 글이 올라옵니다. 신고가 쌓이거나 지침에 어긋나면 운영자가 숨길 수 있습니다. 글에는 내리기(▼)가 없습니다.</p>'
         '<h2>운영</h2><p>올린 글과 댓글은 운영자가 확인합니다. 숨긴 글은 지우지 않고 보이지 않게만 합니다. 문의는 문의 쪽으로 보내 주세요.</p>')


def config(B):
    K = B.S.get('knobs') or {}
    return {'gravity': float(K.get('gravity', 1.8)), 'per_page': int(K.get('per_page', 30)), 'moderation': 'after' if K.get('moderation') == '바로' else 'before',
            'font': 'big' if K.get('board_font') == '크게' else 'ref', 'full': B.S.get('kind', '').startswith('커뮤니티')}


def shell(B):
    return f'<div class="bd" id="bd"><p>불러오는 중…</p></div><script>{JS.replace("__BASE__", B.BASE).replace("__NAME__", B.S["name"].replace(chr(34), ""))}</script>'


def pages(B):
    if not B.part('board', False):
        return []
    json.dump(config(B), open(os.path.join(B.OUT, 'board.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    sp = os.path.join(B.KITS_DIR, 'board', 'data', 'sample.json')
    if not os.path.exists(sp):
        sp = os.path.join(B.HERE, 'kits', 'board', 'data', 'sample.json')
    sample = json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else []
    json.dump(sample, open(os.path.join(B.OUT, 'board_sample.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    return [B.page('board', f'게시판 — {B.S["name"]}', '링크와 글을 올리고 추천으로 순서를 정하는 게시판', shell(B)),
            B.page('board/guide', f'지침 — {B.S["name"]}', '게시판에 올릴 것과 올리지 않을 것, 순서가 정해지는 방식', f'<div class="page">{GUIDE}</div>')]


def home_body(B):
    return shell(B)
