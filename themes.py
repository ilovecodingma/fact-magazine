# -*- coding: utf-8 -*-
"""겉모습 틀(테마) 여섯 가지. build.py 가 style.css 맨 끝에 붙이고 <body class="th-이름"> 으로 켠다.
site.json 의 "theme"(+ 선택 "accent" 색) 또는 환경변수 SITE_THEME·SITE_ACCENT 로 고른다. 파이썬 기본 기능만 쓴다.
 paper  신문형(기본)      card  카드 잡지형      shop  가게형      doc  문서형      play  놀이터형      one  한 장짜리"""

NAMES = {'paper': '신문형', 'card': '카드 잡지형', 'shop': '가게형', 'doc': '문서형', 'play': '놀이터형', 'one': '한 장짜리'}
DEFAULT_ACCENT = {'paper': '#111111', 'card': '#e4572e', 'shop': '#b5532a', 'doc': '#2f6fed', 'play': '#ff4f8b', 'one': '#7a5cff'}

CSS = r"""
/* ===== 카드 잡지형: 밝은 회색 바탕에 흰 카드, 왼쪽 정렬 제호, 알약 모양 메뉴 ===== */
body.th-card{--bg:#f2f0ec;--hair:#e4e0d8;--link:var(--ac);font-family:var(--sans)}
body.th-card .dateline{color:rgba(255,255,255,.85);border:0;text-align:left;padding:22px 0 0;font-size:14px}
body.th-card .mast{background:linear-gradient(135deg,var(--ac),color-mix(in srgb,var(--ac) 55%,#000));border:0;box-shadow:0 6px 18px rgba(0,0,0,.12);padding-bottom:18px}
body.th-card .logo{text-align:left;font:900 44px/1.1 var(--sans);color:#fff;margin:8px 0 4px;text-shadow:0 2px 0 rgba(0,0,0,.15)}
body.th-card nav.menu{justify-content:flex-start;border:0;padding:16px 0 4px;gap:8px}
body.th-card nav.menu a,body.th-card details.mn summary{background:#fff;border-radius:999px;padding:9px 16px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
body.th-card nav.menu a:hover{background:var(--ac);color:#fff;text-decoration:none}
body.th-card .gl a,body.th-card .tp,body.th-card .side .it,body.th-card .lead,body.th-card .ex-grid>div,body.th-card .cr{background:#fff;border:0;border-radius:16px;box-shadow:0 2px 10px rgba(0,0,0,.06);padding:18px 20px}
body.th-card .gl{gap:16px}body.th-card .cols{column-count:auto;display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
body.th-card .side{border:0;padding-left:0}body.th-card .front{gap:20px}
body.th-card .sec{border-top:0;margin-top:34px}body.th-card .sec h2{display:inline-block;background:var(--ac);color:#fff;padding:7px 14px;border-radius:999px;font-size:14px}
body.th-card h1,body.th-card h2,body.th-card h3,body.th-card .lead h2{font-family:var(--sans)}
body.th-card .page{max-width:1000px}body.th-card .page>h2{display:none}body.th-card .page>p{font-size:20px;margin:6px 0 20px}
body.th-card footer{border-top:0}
@media(max-width:900px){body.th-card .cols{grid-template-columns:repeat(2,1fr)}}@media(max-width:640px){body.th-card .logo{font-size:32px}body.th-card .cols{grid-template-columns:1fr}body.th-card nav.menu{flex-wrap:wrap}}

/* ===== 가게형: 크림 바탕, 큰 색 띠 머리, 둥근 버튼 메뉴, 점선 카드 ===== */
body.th-shop{--bg:#fbf3e6;--hair:#e8d6bd;--mu:#7a6551;--link:var(--ac);font-family:var(--sans)}
body.th-shop .mast{background:var(--ac);border:0;color:#fff;padding:26px 0 30px;text-align:center}
body.th-shop .dateline{color:#ffe9cf;border:0;font-size:15px;letter-spacing:.04em;padding:0 0 4px;order:2}
body.th-shop .logo{color:#fff;font:900 56px/1.1 var(--serif);margin:8px 0 6px;text-shadow:0 3px 0 rgba(0,0,0,.18)}
body.th-shop .mast .wrap{display:flex;flex-direction:column}
body.th-shop nav.menu{border:0;justify-content:center;padding:18px 0 6px;gap:10px}
body.th-shop nav.menu a,body.th-shop details.mn summary{background:#fff;border:2px solid var(--ac);color:var(--ac);border-radius:12px;padding:9px 18px;font-weight:800}
body.th-shop nav.menu a:hover{background:var(--ac);color:#fff;text-decoration:none}
body.th-shop .gl a,body.th-shop .tp,body.th-shop .side .it,body.th-shop .ex-grid>div{background:#fffaf2;border:2px dashed #d9b98f;border-radius:12px;padding:16px 18px}
body.th-shop .gl{gap:16px}body.th-shop .sec{border-top:0;text-align:center}body.th-shop .sec h2{display:inline-block;font-size:18px;color:var(--ac);border-bottom:3px solid var(--ac);padding-bottom:6px;margin-bottom:14px}
body.th-shop .sec .sub{text-align:center}body.th-shop .tp{text-align:left}
body.th-shop .page{text-align:center;max-width:900px}body.th-shop .page>h2{font-size:30px;color:var(--ac)}body.th-shop .gl{text-align:left}
body.th-shop footer{background:#f3e3c9;border:0;text-align:center}
body.th-shop .cols{column-rule:0}
@media(max-width:640px){body.th-shop .logo{font-size:38px}body.th-shop nav.menu{flex-wrap:wrap;justify-content:center}}

/* ===== 문서형: 흰 바탕, 작은 왼쪽 제호, 한 칸 읽기 폭, 파란 포인트, 목록은 줄로 ===== */
body.th-doc{--hair:#e3e7ee;--mu:#5f6b7a;--link:var(--ac);font-family:var(--sans);background:#fff}
body.th-doc .dateline{display:none}
body.th-doc .mast{border:0;border-bottom:1px solid #e3e7ee;background:#f7f9fc}
body.th-doc .logo{text-align:left;font:800 19px/1 var(--sans);margin:15px 0;color:var(--ink)}body.th-doc .logo::before{content:"▍";color:var(--ac)}
body.th-doc nav.menu{justify-content:flex-start;border:0;padding:10px 0;gap:20px;border-bottom:1px solid #e3e7ee}
body.th-doc nav.menu a{color:var(--mu)}body.th-doc nav.menu a:hover{color:var(--ac);text-decoration:none}
body.th-doc main.wrap{max-width:760px}
body.th-doc h1,body.th-doc h2,body.th-doc h3{font-family:var(--sans)}
body.th-doc .gl{display:block}body.th-doc .gl a{border-bottom:1px solid #e3e7ee;padding:14px 4px}body.th-doc .gl h3{font-size:18px;color:var(--ac);margin:2px 0}
body.th-doc .gl .lb{display:none}
body.th-doc .sec{border-top:0;margin-top:30px}body.th-doc .sec h2{font-size:22px;letter-spacing:0;border-left:4px solid var(--ac);padding-left:10px;margin-bottom:10px}
body.th-doc .front{display:block}body.th-doc .side{border:0;padding:0;margin-top:12px}
body.th-doc .cols{column-count:1;column-rule:0}
body.th-doc .page>h2{font-size:32px;margin-bottom:4px}
body.th-doc .notice{background:#eef4ff;border-color:#c9dbff}
body.th-doc footer{border-top:1px solid #e3e7ee}

/* ===== 놀이터형: 어두운 남색 바탕, 보라→분홍 머리, 굵은 테두리·그림자 카드, 알록달록 ===== */
body.th-play{--ink:#fff;--bg:#14123a;--mu:#b9b6e8;--hair:#3a3678;--link:#ffd23f;font-family:var(--sans)}
body.th-play .mast{border:0;background:linear-gradient(120deg,#5b2bd9,var(--ac));padding:14px 0 10px;box-shadow:0 5px 0 #ffd23f}
body.th-play .dateline{color:#fff;border:0;opacity:.9;padding-bottom:0}
body.th-play .logo{font:900 52px/1.1 var(--sans);color:#fff;text-shadow:3px 3px 0 #14123a;margin:10px 0 12px}
body.th-play nav.menu{border:0;gap:10px;padding:18px 0 4px}
body.th-play nav.menu a,body.th-play details.mn summary{background:#ffd23f;color:#14123a;border:3px solid #fff;border-radius:14px;padding:9px 16px;font-weight:900;box-shadow:3px 3px 0 #000}
body.th-play nav.menu a:hover{background:#4de3c1;text-decoration:none}
body.th-play .mnp{background:#2b2766;border-color:#ffd23f}
body.th-play .gl a,body.th-play .tp,body.th-play .side .it,body.th-play .ex-grid>div,body.th-play .cr{background:#25216a;border:3px solid #fff;border-radius:18px;box-shadow:5px 5px 0 #000;padding:16px 18px}
body.th-play .gl a:nth-child(3n+1){background:#3a2bb0}body.th-play .gl a:nth-child(3n+2){background:#a3238e}body.th-play .gl a:nth-child(3n){background:#0b7a75}
body.th-play .gl{gap:20px}body.th-play .gl p,body.th-play .lead p,body.th-play .dek,body.th-play .gm .how,body.th-play details.fq p{color:#e8e6ff}
body.th-play .sec{border-top:0}body.th-play .sec h2{display:inline-block;background:#ffd23f;color:#14123a;padding:6px 14px;border-radius:10px;font-size:15px;box-shadow:3px 3px 0 #000}
body.th-play h1,body.th-play h2,body.th-play h3{font-family:var(--sans)}body.th-play .page>h2{font-size:34px;color:#ffd23f}
body.th-play .calc input,body.th-play .lf input{background:#fff;color:#111}
body.th-play button,body.th-play .gm button,body.th-play main button{background:#ffd23f!important;color:#14123a!important;border:3px solid #fff!important;border-radius:12px!important;box-shadow:3px 3px 0 #000}
body.th-play .gm canvas{background:#fff}
body.th-play footer{border-top:3px solid #ffd23f;color:#b9b6e8}body.th-play footer a{color:#fff}
body.th-play .notice{background:#2b2766;border-color:#ffd23f;color:#fff}
body.th-play .mdt td,body.th-play .mdt th{border-color:#5a55a8}
body.th-play a.logo{color:#fff}
@media(max-width:640px){body.th-play .logo{font-size:36px}}

/* ===== 한 장짜리: 엷은 그라데이션, 가운데 큰 제호, 작은 메뉴, 좁은 한 줄 읽기 ===== */
body.th-one{--hair:#e6e2fb;--link:var(--ac);font-family:var(--sans);background:linear-gradient(180deg,#f3f0ff 0%,#fff 420px)}
body.th-one .mast{border:0;padding:46px 0 6px;text-align:center}
body.th-one .dateline{order:2;border:0;font-size:17px;color:var(--mu);padding:0 0 4px;letter-spacing:.02em}
body.th-one .mast .wrap{display:flex;flex-direction:column}
body.th-one .logo{font:900 68px/1.08 var(--sans);color:var(--ac);letter-spacing:-.03em;margin:0 0 10px}
body.th-one nav.menu{border:0;gap:18px;font-size:13px;padding:14px 0 0;color:var(--mu)}body.th-one nav.menu a{color:var(--mu)}
body.th-one main.wrap{max-width:680px}body.th-one .page>p,body.th-one .sec h2,body.th-one .sec .sub{text-align:center}
body.th-one h1,body.th-one h2,body.th-one h3{font-family:var(--sans)}
body.th-one .gl{display:flex;flex-direction:column;gap:12px;text-align:center}
body.th-one .gl a{background:#fff;border:2px solid var(--ac);border-radius:16px;padding:16px;box-shadow:0 6px 0 rgba(122,92,255,.18)}body.th-one .gl a:hover{background:var(--ac);color:#fff}body.th-one .gl a:hover p,body.th-one .gl a:hover .lb{color:#fff}
body.th-one .gl .lb{display:none}
body.th-one .sec{border-top:0;margin-top:36px}body.th-one .sec h2{font-size:20px;letter-spacing:0;color:var(--ac)}
body.th-one .tp,body.th-one .it{text-align:left}body.th-one .cols{column-count:1;column-rule:0}
body.th-one .page>h2{display:none}body.th-one .page>p{font-size:22px;line-height:1.6;margin:10px 0 24px}
body.th-one footer{border:0;text-align:center}
@media(max-width:640px){body.th-one .logo{font-size:44px}body.th-one .mast{padding-top:28px}}
"""
