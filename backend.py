# -*- coding: utf-8 -*-
"""백엔드(독자 PC 의 도커 서버, server/app.py)와 이어지는 사이트 쪽 조각: api.js·댓글/좋아요·문의 양식·소식 받기·방문 통계 신호. 파이썬 기본 기능만 쓴다.
서버가 꺼져 있어도 찍어 둔 화면은 그대로 열리고, 기능 칸에는 「서버가 켜져 있을 때 됩니다」만 보인다."""
import html, os

E = html.escape

API_JS = r"""(function(){
var OFF="서버가 켜져 있을 때 됩니다(python run.py 서버)";
function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})}
function api(p,o){o=o||{};return fetch(p,o).then(function(r){return r.json()})}
function post(p,b){return api(p,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b)})}
var up=false;
api("/api/health").then(function(j){up=!!j.ok}).catch(function(){up=false}).then(init);
function msg(el,t,ok){var m=el.querySelector(".be-msg");if(m){m.textContent=t;m.style.color=ok?"#0b5d2f":"#a11a12"}}
function init(){
 document.documentElement.setAttribute("data-server",up?"on":"off");
 if(!up){document.querySelectorAll("[data-widget]").forEach(function(e){var m=e.querySelector(".be-off");if(m)m.hidden=false;e.querySelectorAll("form,button.be-like").forEach(function(f){f.hidden=true})});return}
 document.querySelectorAll("[data-widget] .be-off").forEach(function(m){m.hidden=true});
 document.querySelectorAll("[data-widget] form,[data-widget] button.be-like").forEach(function(e){e.hidden=false});
 api("/api/visit",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({path:location.pathname})}).catch(function(){});
 document.querySelectorAll('[data-widget="comments"]').forEach(function(w){var slug=w.dataset.slug,L=w.querySelector(".cm-list");
  function load(){api("/api/comments?slug="+encodeURIComponent(slug)).then(function(j){L.innerHTML=(j.comments||[]).map(function(c){return '<div class="cm"><b>'+esc(c.name)+'</b> <span>'+esc(c.created.slice(0,10))+'</span><p>'+esc(c.body)+'</p></div>'}).join("")||'<p class="be-mu">아직 공개된 댓글이 없습니다.</p>'})}
  load();var f=w.querySelector("form");if(f)f.onsubmit=function(e){e.preventDefault();post("/api/comments",{slug:slug,name:f.name.value,body:f.body.value}).then(function(j){msg(w,j.message||j.error,!!j.ok);if(j.ok)f.body.value=""})};
  var lb=w.querySelector("button.be-like");if(lb){api("/api/likes?slug="+encodeURIComponent(slug)).then(function(j){lb.querySelector("b").textContent=j.likes||0});lb.onclick=function(){post("/api/like",{slug:slug}).then(function(j){if(j.ok)lb.querySelector("b").textContent=j.likes})}}});
 document.querySelectorAll('[data-widget="contact"] form').forEach(function(f){var w=f.closest("[data-widget]");f.onsubmit=function(e){e.preventDefault();post("/api/contact",{name:f.name.value,email:f.email.value,message:f.message.value}).then(function(j){msg(w,j.message||j.error,!!j.ok);if(j.ok)f.reset()})}});
 document.querySelectorAll('[data-widget="subscribe"] form').forEach(function(f){var w=f.closest("[data-widget]");f.onsubmit=function(e){e.preventDefault();post("/api/subscribe",{email:f.email.value}).then(function(j){msg(w,j.message||j.error,!!j.ok);if(j.ok)f.reset()})}});
}
})();"""

CSS = (".be{margin:30px 0 0;padding:18px 20px;border:1px solid var(--hair,#ddd);border-radius:12px;background:#fff;font:16px/1.7 var(--sans,system-ui)}.be h2{font:800 17px/1.4 var(--sans,system-ui);margin:0 0 10px;border:0;padding:0}"
       ".be form{display:grid;gap:8px;margin:12px 0 0}.be input,.be textarea{font:16px var(--sans,system-ui);padding:10px;border:1px solid var(--hair,#ccc);border-radius:6px;width:100%}.be textarea{min-height:90px}"
       ".be button{font:700 15px var(--sans,system-ui);padding:10px 16px;border:1px solid var(--pri,#111);background:var(--pri,#111);color:#fff;border-radius:6px;cursor:pointer;width:auto;justify-self:start}"
       ".be button.be-like{background:#fff;color:var(--pri,#111);margin:0 0 8px}.be button.be-like b{margin-left:6px}.be .cm{border-top:1px solid var(--hair,#ddd);padding:8px 0}.be .cm span,.be-mu,.be-off{color:#555;font-size:14px}.be .cm p{margin:4px 0 0}.be-msg{font-size:14px;min-height:1em}")


def write(B):
    open(os.path.join(B.OUT, 'api.js'), 'w', encoding='utf-8').write(API_JS)


def script_tag(B):
    return f'<script src="{B.BASE}api.js" defer></script>' if B.part('backend', False) else ''


def comments_html(B, slug):
    if not (B.part('backend', False) and B.part('comments', False)):
        return ''
    return (f'<section class="be" data-widget="comments" data-slug="{E(slug)}"><h2>의견과 댓글</h2><button type="button" class="be-like" hidden>👍 도움이 됐어요 <b>0</b></button><div class="cm-list"></div>'
            '<form hidden><input name="name" maxlength="30" placeholder="이름(비워 두면 익명)" aria-label="이름"><textarea name="body" maxlength="600" required placeholder="댓글을 남겨 주세요(운영자가 승인하면 보입니다)" aria-label="댓글"></textarea><button type="submit">댓글 남기기</button></form>'
            '<p class="be-msg" role="status"></p><p class="be-off" hidden>댓글·좋아요는 서버가 켜져 있을 때 됩니다.</p></section>')


def contact_html(B):
    if not (B.part('backend', False) and B.part('contact', False)):
        return ''
    return ('<section class="be" data-widget="contact"><h2>문의 보내기</h2><form hidden><input name="name" maxlength="40" placeholder="이름" aria-label="이름"><input name="email" type="email" required maxlength="120" placeholder="답을 받을 메일 주소" aria-label="메일 주소">'
            '<textarea name="message" required minlength="5" maxlength="1500" placeholder="문의·정정 요청 내용(어느 노트의 어느 문장인지 적어 주세요)" aria-label="문의 내용"></textarea><button type="submit">보내기</button></form>'
            '<p class="be-msg" role="status"></p><p class="be-off" hidden>문의 양식은 서버가 켜져 있을 때 됩니다. 그때까지는 위의 메일 주소로 보내 주세요.</p></section>')


def subscribe_html(B):
    return ('<section class="be" data-widget="subscribe"><h2>소식 받기</h2><p>새 확인 노트를 올리면 알려 드립니다. 메일 주소는 이 사이트의 서버에만 저장하고 다른 곳에 주지 않습니다.</p><form hidden><input name="email" type="email" required maxlength="120" placeholder="메일 주소" aria-label="메일 주소"><button type="submit">신청하기</button></form>'
            '<p class="be-msg" role="status"></p><p class="be-off" hidden>소식 받기 신청은 서버가 켜져 있을 때 됩니다.</p></section>')


def pages(B):
    """소식 받기 쪽(/subscribe/). 서버가 없으면 안내만 보인다."""
    if not (B.part('backend', False) and B.part('subscribe', False)):
        return []
    return [B.page('subscribe', f'소식 받기 — {B.S["name"]}', '새 확인 노트 소식을 메일로 받는 신청', f'<div class="page"><span class="lb">소식</span><h1>소식 받기</h1>{subscribe_html(B)}</div>')]
