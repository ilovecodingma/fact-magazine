# -*- coding: utf-8 -*-
"""다듬기 10: 레퍼런스(미디엄)에 있고 우리에 없던 글 머리 정보와 글에 붙는 단추 — 읽는 시간·주제 태그·글쓴이·저장(이 기기에 저장한 글 목록)·듣기(브라우저 읽어 주기)·공유. 서버 없이 된다.
박수(좋아요)·응답(댓글)은 방식 백엔드 (나)를 골랐을 때 댓글 키트가 맡는다. 파이썬 기본 기능만 쓴다."""
import html, json, re

E = html.escape


def css(opt):
    return ("body.pl10 .mh{display:flex;gap:10px 14px;align-items:center;flex-wrap:wrap;font:15px/1.4 var(--sans,system-ui);color:var(--mu,#555);border-top:1px solid var(--hair,#ddd);border-bottom:1px solid var(--hair,#ddd);padding:10px 0;margin:0 0 20px}\n"
            "body.pl10 .mh .au{font-weight:700;color:var(--ink,#111)}body.pl10 .tg a{display:inline-block;padding:4px 10px;border-radius:999px;background:var(--bgs,#eee);color:var(--ink,#111);font:600 13px/1.2 var(--sans,system-ui);margin-right:6px}\n"
            "body.pl10 .ma{display:flex;gap:8px;flex-wrap:wrap;margin:26px 0 0;padding-top:14px;border-top:1px solid var(--hair,#ddd)}body.pl10 .ma button,body.pl10 .ma a{font:700 14px/1 var(--sans,system-ui);padding:10px 14px;border:1px solid var(--hair,#ccc);border-radius:999px;background:#fff;color:var(--ink,#111);cursor:pointer;width:auto}\n"
            "body.pl10 .ma button[aria-pressed=true]{background:var(--pri,#111);border-color:var(--pri,#111);color:#fff}body.pl10 .sv-list a{display:block;padding:12px 0;border-bottom:1px solid var(--hair,#ddd);font:700 17px/1.5 var(--sans,system-ui)}\n"
            "@media print{body.pl10 .ma{display:none}}\n")


def minutes(n):
    txt = ' '.join([n.get('summary', '')] + [f.get('text', '') for f in n.get('facts', [])] + list(n.get('differs', [])) + list(n.get('unconfirmed', [])))
    return max(1, round(len(re.sub(r'\s+', '', txt)) / 500))   # 한글은 1분에 약 500자를 읽는다고 잡는다


def head_html(B, n, cats):
    tags = ''.join(f'<a href="{B.BASE}{("?cat=" + E(t)) if t in cats else ""}">{E(t)}</a>' for t in (n.get('tags') or [])[:4])
    return (f'<div class="mh"><span class="tg">{tags}</span><a class="au" href="{B.BASE}about/">{E(B.S["name"])}</a><span class="rt">읽는 데 {minutes(n)}분</span><span>{E(n["date"])}</span><span>확인 시각 {E(n["checked_at"])}</span></div>')


def actions_html(B, n, opt):
    if opt == 'B':   # 가볍게: 공유만
        return '<div class="ma"><button type="button" data-act="share">링크 복사</button><button type="button" onclick="window.print()">인쇄</button></div>' + JS
    return (f'<div class="ma" data-id="{E(n["id"])}" data-title="{E(n["title"])}"><button type="button" data-act="save" aria-pressed="false">저장</button><button type="button" data-act="listen" aria-pressed="false">듣기</button>'
            f'<button type="button" data-act="share">링크 복사</button><button type="button" onclick="window.print()">인쇄</button><a href="{B.BASE}saved/">저장한 글 보기</a></div>' + JS)


JS = ('<script>(function(){var box=document.querySelector(".ma");if(!box)return;var K="fm_saved";function get(){try{return JSON.parse(localStorage.getItem(K)||"[]")}catch(e){return[]}}'
      'var sv=box.querySelector("[data-act=save]"),ls=box.querySelector("[data-act=listen]"),sh=box.querySelector("[data-act=share]"),u=location.pathname;'
      'function has(){return get().some(function(x){return x.u===u})}function paint(){if(sv){sv.setAttribute("aria-pressed",has());sv.textContent=has()?"저장됨":"저장"}}paint();'
      'if(sv)sv.onclick=function(){var L=get();if(has())L=L.filter(function(x){return x.u!==u});else L.unshift({u:u,t:box.dataset.title,d:new Date().toISOString().slice(0,10)});try{localStorage.setItem(K,JSON.stringify(L.slice(0,200)))}catch(e){}paint()};'
      'if(ls){if(!("speechSynthesis" in window)){ls.disabled=true;ls.textContent="듣기(이 브라우저는 안 됨)"}else ls.onclick=function(){var s=window.speechSynthesis;if(s.speaking){s.cancel();ls.setAttribute("aria-pressed",false);ls.textContent="듣기";return}'
      'var a=document.querySelector(".art"),t=[];["h1",".dek",".sum",".src-card p","ol.fn li"].forEach(function(q){a.querySelectorAll(q).forEach(function(e){t.push(e.innerText)})});var m=new SpeechSynthesisUtterance(t.join(". "));m.lang="ko-KR";m.onend=function(){ls.setAttribute("aria-pressed",false);ls.textContent="듣기"};s.speak(m);ls.setAttribute("aria-pressed",true);ls.textContent="멈추기"}}'
      'if(sh)sh.onclick=function(){if(navigator.clipboard)navigator.clipboard.writeText(location.href).then(function(){sh.textContent="복사했습니다"})}})()</script>')


def extra_pages(B):
    """저장한 글 쪽(/saved/): 이 기기의 브라우저에만 남는 목록."""
    if 10 not in B.POLISH or B.POLISH[10] == 'B' or not B.part('info'):
        return []
    js = ('<script>(function(){var L=[];try{L=JSON.parse(localStorage.getItem("fm_saved")||"[]")}catch(e){}var o=document.getElementById("svl");function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;"}[c]})}'
          'o.innerHTML=L.length?L.map(function(x){return "<a href=\\""+esc(x.u)+"\\">"+esc(x.t)+" <small>"+esc(x.d||"")+"</small></a>"}).join(""):"<p>아직 저장한 글이 없습니다. 글 아래의 「저장」을 누르면 여기에 모입니다.</p>"})()</script>')
    return [B.page('saved', f'저장한 글 — {B.S["name"]}', '이 기기에 저장해 둔 글 목록', f'<div class="page"><span class="lb">저장</span><h1>저장한 글</h1><p>이 목록은 이 기기의 브라우저에만 남습니다(서버로 가지 않습니다).</p><div id="svl" class="sv-list"></div></div>{js}', noindex=True)]
