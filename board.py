# -*- coding: utf-8 -*-
"""게시판(링크+추천) 틀 — 레퍼런스: 해커 뉴스(news.ycombinator.com)를 옆에 두고 그대로 옮긴 것(미러). 2026-11-11 에 첫 화면·새 글·글 쪽·news.css·FAQ·지침 쪽을 직접 받아 읽고, 화면을 나란히 찍어 맞췄다(잰 값: 참고/레퍼런스.json, 조각: 참고/조각/해커뉴스.json).
옮긴 것: 주황 머리 띠(이름 + 새 글|지난 글|댓글|묻는 글|보여 주기|구인|글 올리기, 오른쪽에 로그인) · 베이지 바탕 · 폭 85% · 한 줄 = 순번·▲·제목(사이트) / 아랫줄 = 「N점 by 이름 N시간 전 | 숨기기 | 댓글 N개(0 이면 이야기하기)」 · 줄 사이 5px · 한 쪽 30줄 · 「더 보기」
        글 쪽 = 아랫줄에 지난 글|저장 추가 · 댓글 입력칸(8줄)이 댓글보다 위 · 댓글마다 ▲ · 한 단계에 40px 들여쓰기(휴대폰 12px) · 댓글 머리 「이름 시간 | 처음 | 위 | 앞 | 다음 [–]」 · 접으면 「[N개 더]」 · 댓글 아래 「답글」 · 맨 아래 주황 줄과 지침|자주 묻는 것|소개|문의 + 찾기 칸
본과 다른 것(독자가 알고 바꾼다): 로그인·가입이 없어 「로그인」은 운영자 화면으로 가고 이름 칸이 따로 있다. 올린 글은 기본 「승인 뒤 공개」(본은 바로 공개 — 손잡이 공개방식). 글자는 손잡이 게시판글자로(본 = 10pt·7pt).
서버(python run.py 서버)가 있어야 돈다. 꺼져 있으면 예시 글로 화면만 보인다. 파이썬 기본 기능만 쓴다."""
import html, json, os

E = html.escape

CSS = (".bd{--bdt:13.33px;--bds:9.33px;--bdc:12px;--bdh:10.67px;width:85%;min-width:0;margin:8px auto 0;background:#f6f6ef;color:#828282;font:var(--bdt)/1.2 Verdana,Geneva,'Malgun Gothic',sans-serif}"
       ".bd.big{--bdt:16px;--bds:13px;--bdc:15px;--bdh:13px}.bd a{color:#000;text-decoration:none}.bd a:visited{color:#828282}"
       ".bd-top{background:#ff6600;padding:2px;display:flex;align-items:center;line-height:16px;color:#222}.bd-top b{margin:0 5px 0 1px}.bd-top a,.bd-top a:visited{color:#000}.bd-top a.on,.bd-top a.on:visited{color:#fff}.bd-top .nav{flex:1}.bd-top .login{padding-right:4px}"
       ".bd-logo{display:inline-block;width:18px;height:18px;border:1px solid #fff;color:#fff!important;font:700 12px/18px Verdana,sans-serif;text-align:center;margin-right:4px;box-sizing:content-box}"
       ".bd-body{padding:10px 0 0}.bd-row{display:grid;grid-template-columns:26px 14px 1fr;margin:0 0 5px}.bd-n{text-align:right;color:#828282}.bd-v{border:0;background:none;cursor:pointer;width:10px;height:10px;margin:3px 2px 6px;padding:0;position:relative;display:block}"
       ".bd-v::before{content:'';position:absolute;left:0;top:0;border-left:5px solid transparent;border-right:5px solid transparent;border-bottom:10px solid #9a9a9a}.bd-v.on{visibility:hidden}"
       ".bd-t{color:#000}.bd-h{font-size:var(--bdh);color:#828282}.bd-m{display:block;font-size:var(--bds);color:#828282;line-height:1.3}.bd-m a,.bd-m a:visited{color:#828282;cursor:pointer}.bd-m a:hover{text-decoration:underline}"
       ".bd-more{display:inline-block;margin:6px 0 10px 40px;color:#828282!important;cursor:pointer}.bd-text{margin:8px 0 8px 40px;color:#000;max-width:800px;font-size:var(--bdc)}.bd-pad{margin-left:40px}"
       ".bd form{margin:10px 0 26px 40px;display:block}.bd textarea{font:var(--bdt) monospace;display:block;margin:0 0 12px;max-width:calc(100% - 50px)}.bd input[type=text]{font:var(--bdt) monospace;display:block;margin:0 0 8px;padding:1px 2px;max-width:calc(100% - 50px)}"
       ".bd button.go{font:var(--bdt) Verdana,Geneva,sans-serif;padding:1px 6px;cursor:pointer;width:auto;display:inline-block}.bd-msg{font-size:var(--bds);min-height:1.2em;color:#0b5d2f;margin:4px 0 0}.bd-name{font-size:var(--bds)!important;width:150px}"
       ".bd-c{margin:0 0 6px 10px;display:flex;align-items:flex-start}.bd-c .bd-v{flex:none;margin:4px 4px 0 0}.bd-ch{font-size:var(--bdh);color:#828282}.bd-ch a,.bd-ch a:visited{color:#828282;cursor:pointer}.bd-ch a:hover{text-decoration:underline}"
       ".bd-cb{font-size:var(--bdc);color:#000;max-width:1215px;overflow-wrap:anywhere;line-height:1.25}.bd-cb p{margin:6px 0 0}.bd-re{font-size:var(--bds);text-decoration:underline!important;color:#000!important;cursor:pointer}"
       ".bd-foot{border-top:2px solid #ff6600;margin-top:16px;padding:12px 0 16px;text-align:center;font-size:var(--bdh);line-height:1.4}.bd-foot a,.bd-foot a:visited{color:#000}.bd-foot form{margin:14px 0 0;color:#828282;font-size:var(--bdt)}.bd-foot input[type=text]{display:inline-block;width:150px;margin:0}"
       ".bd-off{color:#828282;font-size:var(--bds);margin:10px 0 0}"
       ".bdfull .mast,.bdfull nav.menu,.bdfull .bnav,.bdfull .notice,.bdfull footer,.bdfull .trust,.bdfull .mon{display:none!important}.bdfull main.wrap{max-width:none;padding:0}.bdfull body{background:#fff}"
       "@media(max-width:750px){.bd{width:100%;--bdt:14.67px;--bds:12px;margin-top:0}.bd.big{--bdt:16px;--bds:13px}.bd-top{line-height:1.5;flex-wrap:wrap}.bd-top b{display:block;font-size:15px}.bd-v{transform:scale(1.3);margin-right:6px}.bd form,.bd-text,.bd-more,.bd-pad{margin-left:8px}.bd-row{grid-template-columns:26px 18px 1fr}}\n")

JS = r"""(function(){
var root=document.getElementById("bd");if(!root)return;var BASE="__BASE__",NAME="__NAME__",CFG={gravity:1.8,per_page:30,moderation:"before",font:"ref",full:false},up=false,SAMPLE=[];
function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})}
function api(p,o){return fetch(p,o||{}).then(function(r){return r.json()})}
function post(p,b){return api(p,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b)})}
function host(u){try{return new URL(u).hostname.replace(/^www[.]/,"")}catch(e){return ""}}
function ago(h){if(h<1)return Math.max(1,Math.round(h*60))+"분 전";if(h<24)return Math.round(h)+"시간 전";return Math.round(h/24)+"일 전"}
function q(k){var m=location.search.match(new RegExp("[?&]"+k+"=([^&]*)"));return m?decodeURIComponent(m[1]):""}
function ls(k){try{return JSON.parse(localStorage.getItem(k)||"[]")}catch(e){return[]}}
function lsput(k,L){try{localStorage.setItem(k,JSON.stringify(L.slice(-300)))}catch(e){}}
function rank(L){return L.map(function(p){p.score=p.points/Math.pow(p.hours+2,CFG.gravity);return p}).sort(function(a,b){return b.score-a.score})}
function B(v){return BASE+"board/"+(v?"?v="+v:"")}
function top(cur){var T=[["new","새 글"],["past","지난 글"],["comments","댓글"],["ask","묻는 글"],["show","보여 주기"],["jobs","구인"],["submit","글 올리기"]];
 return '<div class="bd-top"><a class="bd-logo" href="'+B("")+'">'+esc(NAME.charAt(0))+'</a><span class="nav"><b><a href="'+B("")+'">'+esc(NAME)+'</a></b>'+T.map(function(t){return '<a class="'+(t[0]===cur?"on":"")+'" href="'+B(t[0])+'">'+t[1]+'</a>'}).join(' | ')+'</span><span class="login"><a href="'+(up?"/admin/":BASE+"board/guide/")+'">'+(up?"로그인":"지침")+'</a></span></div>'}
function foot(){return '<div class="bd-foot"><a href="'+BASE+'board/guide/">지침</a> | <a href="'+BASE+'board/guide/#faq">자주 묻는 것</a> | <a href="'+B("saved")+'">저장한 글</a> | <a href="'+BASE+'about/">소개</a> | <a href="'+BASE+'privacy/">개인정보</a> | <a href="'+BASE+'contact/">문의</a><form action="'+BASE+'search/" method="get">찾기: <input type="text" name="q" size="17"></form>'+(up?"":'<p class="bd-off">지금은 서버가 꺼져 있어 예시 글로 화면만 보입니다(python run.py 서버 를 켜면 글 올리기·추천·댓글이 됩니다).</p>')+'</div>'}
function sub(p,single){var u=B("")+"?id="+encodeURIComponent(p.id);return '<span class="bd-m"><span class="pt">'+p.points+'</span>점 by '+esc(p.name)+' <a href="'+u+'">'+ago(p.hours)+'</a> | <a class="hd" data-id="'+esc(p.id)+'">숨기기</a>'+(single?' | <a href="'+B("past")+'">지난 글</a> | <a class="fv" data-id="'+esc(p.id)+'" data-t="'+esc(p.title)+'">저장</a> | <a class="fl" data-id="'+esc(p.id)+'">신고</a>':'')+' | <a href="'+u+'">'+(p.comments?"댓글 "+p.comments+"개":"이야기하기")+'</a></span>'}
function row(p,i,single){var h=p.url?host(p.url):"",voted=ls("fm_bd_voted").indexOf(p.id)>=0;return '<div class="bd-row" data-id="'+esc(p.id)+'"><span class="bd-n">'+(single?"":(i+1)+".")+'</span><button class="bd-v'+(voted?" on":"")+'" data-id="'+esc(p.id)+'" title="추천" aria-label="추천"></button><div><a class="bd-t" href="'+(p.url?esc(p.url):B("")+"?id="+encodeURIComponent(p.id))+'"'+(p.url?' rel="noopener nofollow"':'')+'>'+esc(p.title)+'</a>'+(h?' <span class="bd-h">('+esc(h)+')</span>':'')+sub(p,single)+'</div></div>'}
function bind(){root.querySelectorAll(".bd-row .bd-v").forEach(function(b){b.onclick=function(){if(!up)return;post("/api/board/vote",{id:b.dataset.id}).then(function(j){if(j.ok){b.classList.add("on");var L=ls("fm_bd_voted");L.push(b.dataset.id);lsput("fm_bd_voted",L);var r=b.closest(".bd-row");if(r)r.querySelector(".pt").textContent=j.points}})}});
 root.querySelectorAll(".bd-c .bd-v").forEach(function(b){b.onclick=function(){b.classList.add("on")}});
 root.querySelectorAll("a.hd").forEach(function(a){a.onclick=function(){var L=ls("fm_bd_hide");L.push(a.dataset.id);lsput("fm_bd_hide",L);var r=a.closest(".bd-row");if(r)r.remove()}});
 root.querySelectorAll("a.fv").forEach(function(a){a.onclick=function(){var L=ls("fm_bd_fav");if(!L.some(function(x){return x.id===a.dataset.id}))L.push({id:a.dataset.id,t:a.dataset.t});lsput("fm_bd_fav",L);a.textContent="저장했습니다"}});
 root.querySelectorAll("a.fl").forEach(function(a){a.onclick=function(){if(!up)return;post("/api/board/flag",{id:a.dataset.id}).then(function(){a.textContent="신고했습니다"})}})}
function frame(cur,inner){root.className="bd"+(CFG.font==="big"?" big":"");root.innerHTML=top(cur)+'<div class="bd-body">'+inner+'</div>'+foot();bind()}
function list(v){var kind=(v==="ask"||v==="show"||v==="jobs")?(v==="jobs"?"job":v):"all",sort=v==="new"?"new":(v==="past"?"past":"top"),pg=+q("p")||1,H=ls("fm_bd_hide");
 function draw(L,more){L=L.filter(function(p){return H.indexOf(p.id)<0});frame(v==="top"?"":v,(L.length?L.map(function(p,i){return row(p,(pg-1)*CFG.per_page+i)}).join(""):'<p class="bd-pad">아직 글이 없습니다.</p>')+(more?'<a class="bd-more" href="'+B(v)+'&p='+(pg+1)+'">더 보기</a>':''))}
 if(up)api("/api/board?sort="+sort+"&kind="+kind+"&page="+pg).then(function(j){draw(j.posts||[],j.more)});
 else{var L=SAMPLE.filter(function(p){return kind==="all"?p.kind!=="job":p.kind===kind});if(sort==="past")L=L.filter(function(p){return p.hours>=24});L=sort==="new"?L.slice().sort(function(a,b){return a.hours-b.hours}):(sort==="past"?L.slice().sort(function(a,b){return b.points-a.points}):rank(L.slice()));draw(L.slice((pg-1)*CFG.per_page,pg*CFG.per_page),L.length>pg*CFG.per_page)}}
function newcomments(){function draw(C){frame("comments",C.length?C.map(function(c){return '<div class="bd-c"><button class="bd-v" aria-label="추천"></button><div><span class="bd-ch">'+esc(c.name)+' '+ago(c.hours)+' | on: <a href="'+B("")+'?id='+encodeURIComponent(c.pid)+'">'+esc(c.title||"")+'</a></span><div class="bd-cb"><p>'+esc(c.body)+'</p></div></div></div>'}).join(""):'<p class="bd-pad">아직 댓글이 없습니다.</p>')}
 if(up)api("/api/board/comments").then(function(j){draw(j.comments||[])});
 else{var C=[];SAMPLE.forEach(function(p){(p.sample_comments||[]).forEach(function(c){C.push({name:c.name,hours:c.hours,body:c.body,pid:p.id,title:p.title})})});C.sort(function(a,b){return a.hours-b.hours});draw(C)}}
function saved(){var L=ls("fm_bd_fav");frame("",'<p class="bd-pad">이 기기에 저장한 글입니다.</p>'+(L.length?L.map(function(x,i){return '<div class="bd-row"><span class="bd-n">'+(i+1)+'.</span><span></span><div><a class="bd-t" href="'+B("")+'?id='+encodeURIComponent(x.id)+'">'+esc(x.t)+'</a></div></div>'}).join(""):'<p class="bd-pad">아직 없습니다. 글 쪽의 「저장」을 누르면 여기에 모입니다.</p>'))}
function submit(){frame("submit",'<form id="bdf"><input type="text" name="title" size="50" maxlength="120" required placeholder="제목" aria-label="제목"><input type="text" name="url" size="50" maxlength="300" placeholder="링크 주소(https://…)" aria-label="링크 주소"><textarea name="text" rows="4" cols="49" maxlength="2000" placeholder="글" aria-label="글"></textarea><input type="text" class="bd-name" name="name" maxlength="30" placeholder="이름(비우면 익명)" aria-label="이름"><button class="go" type="submit">올리기</button><p class="bd-msg" role="status"></p></form><p class="bd-m bd-pad">링크를 올릴 때는 글 칸을 비워 둡니다. 링크가 없으면 글이 묻는 글이 됩니다. 제목을 「묻습니다:」로 시작하면 묻는 글, 「보여 줍니다:」는 보여 주기, 「구인:」은 구인 목록에 들어갑니다. 올리기 전에 <a href="'+BASE+'board/guide/" style="text-decoration:underline">지침</a>을 읽어 주세요.'+(CFG.moderation==="before"?" 올린 글은 운영자가 승인하면 보입니다.":"")+'</p>');
 var f=document.getElementById("bdf");f.onsubmit=function(e){e.preventDefault();var m=f.querySelector(".bd-msg");if(!up){m.textContent="서버가 켜져 있을 때 됩니다.";return}post("/api/board",{title:f.title.value,url:f.url.value,text:f.text.value,name:f.name.value}).then(function(j){m.textContent=j.message||j.error;m.style.color=j.ok?"#0b5d2f":"#a11a12";if(j.ok)f.reset()})}}
function item(id){function draw(p,C){var kids={},byid={};C.forEach(function(c){byid[c.id]=c;(kids[c.parent||""]=kids[c.parent||""]||[]).push(c)});var order=[];
 function count(cid){var n=1;(kids[cid]||[]).forEach(function(k){n+=count(k.id)});return n}
 function walk(par,depth,rootid){(kids[par]||[]).forEach(function(c,i,arr){order.push({c:c,d:depth,root:rootid||c.id,prev:i>0?arr[i-1].id:"",next:i<arr.length-1?arr[i+1].id:""});walk(c.id,depth+1,rootid||c.id)})}walk("",0,"");
 var step=window.innerWidth<=750?12:40;
 var cs=order.map(function(x){var c=x.c,d=x.d,nav=[];if(d>1)nav.push('<a href="#c'+esc(x.root)+'">처음</a>');if(d>0)nav.push('<a href="#c'+esc(c.parent)+'">위</a>');if(x.prev)nav.push('<a href="#c'+esc(x.prev)+'">앞</a>');if(x.next)nav.push('<a href="#c'+esc(x.next)+'">다음</a>');
  return '<div class="bd-c" id="c'+esc(c.id)+'" data-d="'+d+'" data-n="'+count(c.id)+'" style="padding-left:'+(d*step)+'px"><button class="bd-v" aria-label="추천"></button><div><span class="bd-ch">'+esc(c.name)+' '+ago(c.hours)+(nav.length?' | '+nav.join(' | '):'')+' <a class="bd-fold">[–]</a></span><div class="bd-cb"><p>'+esc(c.body)+'</p><p><a class="bd-re" data-id="'+esc(c.id)+'">답글</a></p></div></div></div>'}).join("");
 frame("",row(p,0,true)+(p.text?'<div class="bd-text">'+esc(p.text)+'</div>':'')+'<form id="bdc"><input type="hidden" name="parent" value=""><textarea name="body" rows="8" cols="80" maxlength="1000" required aria-label="댓글"></textarea><input type="text" class="bd-name" name="name" maxlength="30" placeholder="이름(비우면 익명)" aria-label="이름"><button class="go" type="submit">댓글 달기</button><p class="bd-msg" role="status"></p></form><div id="bdt">'+cs+'</div>');
 root.querySelectorAll(".bd-fold").forEach(function(a){a.onclick=function(){var me=a.closest(".bd-c"),d=+me.dataset.d,shut=a.textContent==="[–]";me.querySelector(".bd-cb").style.display=shut?"none":"";a.textContent=shut?"["+me.dataset.n+"개 더]":"[–]";
  var n=me.nextElementSibling;while(n&&n.classList.contains("bd-c")&&+n.dataset.d>d){n.style.display=shut?"none":"";n=n.nextElementSibling}}});
 var f=document.getElementById("bdc");root.querySelectorAll("a.bd-re").forEach(function(a){a.onclick=function(){f.parent.value=a.dataset.id;f.body.placeholder="답글";f.body.focus();window.scrollTo(0,0)}});
 f.onsubmit=function(e){e.preventDefault();var m=f.querySelector(".bd-msg");if(!up){m.textContent="서버가 켜져 있을 때 됩니다.";return}post("/api/board/comment",{id:id,parent:f.parent.value,body:f.body.value,name:f.name.value}).then(function(j){m.textContent=j.message||j.error;if(j.ok){f.body.value="";if(j.shown)item(id)}})}}
 if(up)api("/api/board/item?id="+encodeURIComponent(id)).then(function(j){if(j.post)draw(j.post,j.comments||[]);else frame("","<p class='bd-pad'>글을 찾지 못했습니다.</p>")});
 else{var p=SAMPLE.filter(function(x){return x.id===id})[0];if(p)draw(p,p.sample_comments||[]);else frame("","<p class='bd-pad'>글을 찾지 못했습니다.</p>")}}
function go(){var id=q("id"),v=q("v")||"top";if(id)item(id);else if(v==="submit")submit();else if(v==="comments")newcomments();else if(v==="saved")saved();else list(v)}
Promise.all([api(BASE+"board.json").catch(function(){return null}),api(BASE+"board_sample.json").catch(function(){return []}),api("/api/health").catch(function(){return {}})]).then(function(r){if(r[0])CFG=r[0];SAMPLE=r[1]||[];up=!!(r[2]&&r[2].ok&&(r[2].features||[]).indexOf("board")>=0);
 document.documentElement.setAttribute("data-board",up?"server":"sample");if(CFG.full)document.documentElement.classList.add("bdfull");go()});
})();"""

GUIDE = ('<h1>지침</h1><p>이 게시판은 한 가지 주제에 관심 있는 사람들이 링크와 글을 올리고, 추천으로 순서를 정하고, 댓글로 이야기하는 곳입니다.</p>'
         '<h2>올릴 것</h2><ul><li>이 게시판의 주제에 맞고, 읽은 사람의 궁금증을 채워 주는 글과 링크</li><li>직접 만든 것은 「보여 줍니다:」, 물어볼 것은 「묻습니다:」로 제목을 시작</li><li>다른 곳에서 본 것을 올릴 때는 처음 나온 곳의 주소</li></ul>'
         '<h2>올릴 때</h2><ul><li>제목을 눈에 띄게 하려고 느낌표를 붙이거나 「대단한」 같은 말을 넣지 않기</li><li>제목에 사이트 이름을 넣지 않기(링크 뒤에 사이트가 따로 보입니다)</li><li>이 게시판을 홍보에만 쓰지 않기. 자기 것을 올려도 되지만 가끔만</li></ul>'
         '<h2>올리지 않을 것</h2><ul><li>광고·도배·낚시 제목, 같은 링크를 되풀이해 올리기</li><li>남을 깎아내리는 말, 개인정보</li></ul>'
         '<h2 id="faq">자주 묻는 것</h2><p><b>순서는 어떻게 정해지나요?</b> 추천 점수를 올린 뒤 지난 시간의 거듭제곱으로 나누어 정합니다. 시간이 지나면 저절로 내려가고 새 글이 올라옵니다. 신고가 쌓이거나 지침에 어긋나면 운영자가 숨길 수 있습니다.</p>'
         '<p><b>왜 내리기 화살표가 없나요?</b> 글에는 내리기가 없습니다. 어긋난 글은 신고해 주세요.</p><p><b>묻는 글·보여 주기는 무엇인가요?</b> 묻는 글은 질문과 글만 있는 글, 보여 주기는 직접 만든 것을 내보이는 글입니다.</p>'
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
