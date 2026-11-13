# -*- coding: utf-8 -*-
"""자동(3장): 사람이 자리에 없어도 도는 것을 맛본다. 파이썬 기본 기능만 쓴다. 올리기·로그인·메일 발송은 하지 않는다.
python run.py 자동 맛보기 [--뒤 분]   하루 한 바퀴 + 알릴 글·그림·영상을 사람 없이 끝까지 돌리고 넘김/자리비운동안.md 한 장을 남긴다(--뒤 2 면 2분 뒤에 저절로 시작)
python run.py 자동 방송               그날 글을 차례로 띄우고 읽어 주는 방송 화면을 내 PC 에서 연다(송출은 하지 않는다)
python run.py 자동 예약 [07:00] [--예]  날마다 그 시각에 맛보기가 저절로 돌게 예약(--예 가 없으면 걸 명령만 보여 준다) · 자동 예약 끄기 [--예] · 자동 예약 상태"""
import glob, html, json, os, shutil, subprocess, sys, time
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
PY = [sys.executable, '-X', 'utf8']
A = sys.argv[1:]
TASK = 'MyServiceDaily'
REPORT = os.path.join(HERE, '넘김', '자리비운동안.md')


def site():
    S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
    lp = os.path.join(HERE, 'site.local.json')
    if os.path.exists(lp):
        L = json.load(open(lp, encoding='utf-8')); parts = dict(S.get('parts', {}))
        if isinstance(L.get('parts'), dict):
            parts = L['parts'] if L.get('kind') else dict(parts, **L['parts'])
        S.update(L); S['parts'] = parts
    return S


def new_files(folder, t0, pats):
    out = []
    for p in pats:
        out += [f for f in glob.glob(os.path.join(HERE, folder, p), recursive=True) if os.path.getmtime(f) >= t0 - 1]
    return sorted(out)


def step(name, args):
    t = time.time()
    try:
        r = subprocess.run(PY + args, cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=1800)
        rc = r.returncode; tail = ([x for x in (r.stdout or '').strip().splitlines() if x.strip() and x.strip()[0] not in '┌└'] or [''])[-1].lstrip('│ ').strip()[:160]; err = (r.stderr or '').strip()[-300:]
    except Exception as e:
        rc, tail, err = 1, '', repr(e)[:200]
    print(f'  {"✓" if rc == 0 else "✗"} {name} — {time.time() - t:.0f}초  {tail}', flush=True)
    return dict(name=name, ok=rc == 0, secs=time.time() - t, tail=tail, err=err)


def post_promo(S):
    """글 사이트의 하루 일: 가장 새 글 한 편으로 블로그용 글·알림 문구 세 길이·정사각 카드 그림을 promo_out/post_<글 이름>/ 에 만든다. 올리지 않는다."""
    import base64, re
    sys.path.insert(0, HERE)
    import medium as MD
    P = MD.load_posts()
    if not P:
        return dict(name='알릴 글·그림(가장 새 글로)', ok=None, secs=0, tail='건너뜀: posts/ 에 글이 없습니다', err='')
    t = time.time(); p = P[0]; name = S.get('name') or '내 사이트'
    pg = os.path.join(HERE, '진도.json'); dep = (json.load(open(pg, encoding='utf-8')).get('deploy') or {}) if os.path.exists(pg) else {}
    url = dep.get('url', '') + f'/p/{p["slug"]}/' if dep.get('url') and (not dep.get('temp') or dep.get('expires', 0) > time.time()) else ''
    link = url or '(주소 — python run.py 올려 로 받은 주소가 들어갑니다)'
    body = re.sub(r'<[^>]+>', '', p['html']); first = ' '.join(x.strip() for x in body.split('\n') if x.strip())[:400]
    out = os.path.join(HERE, 'promo_out', 'post_' + p['slug']); os.makedirs(out, exist_ok=True)
    open(os.path.join(out, '블로그글.md'), 'w', encoding='utf-8').write(f'# {p["title"]}\n\n{p["sub"]}\n\n{first}…\n\n---\n전문 보기: {link}\n— {name}\n')
    cut = lambda s, n: s if len(s) <= n else s[:n - 1] + '…'
    open(os.path.join(out, '알림_짧게.txt'), 'w', encoding='utf-8').write(cut(p['title'], 40) + '\n')
    open(os.path.join(out, '알림_보통.txt'), 'w', encoding='utf-8').write(cut(f'{p["title"]} — {p["sub"]}', 80) + (f'\n{url}' if url else '') + '\n')
    open(os.path.join(out, '알림_길게.txt'), 'w', encoding='utf-8').write(cut(f'{p["title"]}\n{p["sub"]} {first}', 140) + f'\n{link}\n')
    img = os.path.join(HERE, 'posts', '_cover', p['slug'] + '.jpg')
    src = ('data:image/jpeg;base64,' + base64.b64encode(open(img, 'rb').read()).decode()) if os.path.exists(img) else ''
    ac = S.get('accent') or '#242424'
    card = os.path.join(out, 'card.html')
    open(card, 'w', encoding='utf-8').write('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;width:1080px;height:1080px;font-family:"Pretendard","Malgun Gothic",sans-serif;background:' + html.escape(ac) + '}'
        'img{position:absolute;inset:0;width:1080px;height:1080px;object-fit:cover}.b{position:absolute;left:0;right:0;bottom:0;padding:64px;color:#fff;background:linear-gradient(180deg,transparent,rgba(0,0,0,.8))}'
        '.s{font-size:32px;opacity:.9}.n{font-size:68px;font-weight:800;line-height:1.25;letter-spacing:-2px;margin:12px 0 16px}.d{font-size:32px;opacity:.92;line-height:1.4}</style>'
        + (f'<img src="{src}">' if src else '') + f'<div class="b"><div class="s">{html.escape(name)}</div><div class="n">{html.escape(p["title"])}</div><div class="d">{html.escape(p["sub"])}</div></div>')
    png = os.path.join(out, '카드.png'); made = False
    try:
        import selftest as T
        br = T.find_browser()
        if br:
            subprocess.run([br, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1080,1080', f'--screenshot={png}', 'file:///' + card.replace(os.sep, '/')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
            made = os.path.exists(png)
    except Exception:
        pass
    tail = f'promo_out/post_{p["slug"]}/ — 블로그글.md · 알림 문구 셋' + (' · 카드.png' if made else '')
    print(f'  ✓ 알릴 글·그림(가장 새 글 「{p["title"]}」으로) — {time.time() - t:.0f}초  {tail}', flush=True)
    return dict(name=f'알릴 글·그림(가장 새 글 「{p["title"]}」으로)', ok=True, secs=time.time() - t, tail=tail, err='')


def taste_shop(t0, only):
    """가게의 하루 일: 들어온 것 세기 → 주문표 → 오늘 보낼 것 → 백업 → 상품 하나 홍보물 → 가게 스스로 시험. 입금 확인·발송·채널에 올리기는 사람 몫으로 남긴다."""
    import sqlite3
    db = os.path.join(HERE, 'shop', 'api', 'data', 'shop.db'); pid = 1; nm = ''; cnt = {}
    try:
        c = sqlite3.connect(db)
        r = c.execute('select id, name from products where stock > 0 order by (was - price) desc, id limit 1').fetchone()   # 할인 폭이 가장 큰 상품을 알린다
        if r:
            pid, nm = r
        cnt = dict(c.execute('select status, count(*) from orders group by status').fetchall()); c.close()
    except Exception:
        pass
    print('  이 서비스: 가게 — 주문을 세고, 보낼 것을 뽑고, 백업하고, 상품 하나를 알릴 준비를 합니다', flush=True)
    R = [step('들어온 것 세기(주문·상품평·재고)', ['data.py', '현황']), step('주문을 표로(넘김/주문표.csv)', ['data.py', '주문표']), step('오늘 보낼 것(넘김/오늘_보낼것.md — 입금 확인된 주문만)', ['data.py', '발송목록']), step('새 주문을 나에게 메일로(켜 둔 경우만)', ['mail.py', '주문알림', '--auto']),
         step('운영 자료 백업', ['data.py', '백업']), step(f'상품 하나를 알릴 글·문구·카드(「{nm}」)', ['shop.py', '홍보', str(pid)]), step('가게 스모크 테스트(손님·운영자의 요청을 차례로)', ['shop/smoke.py'])]
    if not only:
        return R
    total = time.time() - t0; wait = cnt.get('입금 대기', 0); paid = cnt.get('입금 확인', 0)
    L = [f'# 자리 비운 동안 — {time.strftime("%Y-%m-%d %H:%M")}', '', f'사람 입력 없이 {total:.0f}초 동안 가게의 일일 배치가 돌았다. 입금 확인·발송·채널에 올리기·메일 발송은 하지 않았다.', '', '## 걸음별 결과(✓ 됨 · ✗ 걸림 · – 건너뜀)']
    for r in R:
        L.append(f'- {"✓" if r["ok"] else ("–" if r["ok"] is None else "✗")} {r["name"]} ({r["secs"]:.0f}초) {r["tail"]}')
    L += ['', '## 지금 가게', f'- 주문: 입금 대기 {wait}건 · 입금 확인(보낼 것) {paid}건 · 보냄 {cnt.get("보냄", 0)}건', '', '## 여기서 사람이 하는 것',
          f'- 입금 확인: 통장에 돈이 들어왔는지 보고 운영자 화면(`http://127.0.0.1:3000/admin`)에서 「입금 확인」을 누른다 — 지금 {wait}건이 기다린다',
          f'- 보내기: `넘김/오늘_보낼것.md` 대로 싸서 보내고 운영자 화면에서 「보냄」을 누른다 — 지금 {paid}건',
          f'- 알리기: `promo_out/shop_{pid}/` 의 글·문구·카드를 로그인된 블로그·SNS 에 올린다(브라우저 확장이 있으면 세션이 채워 넣고 「발행」 앞에서 멈춘다)']
    bad = [r for r in R if r['ok'] is False]
    L += ['', '## 걸린 것'] + ([f'- {r["name"]}: {r["err"] or r["tail"]}' for r in bad] or ['- 없음'])
    os.makedirs(os.path.dirname(REPORT), exist_ok=True); open(REPORT, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print(f'\n끝 — {total:.0f}초. 한 장으로 남겼습니다: 넘김/자리비운동안.md')
    print(f'[사람 없이 된 것] 주문표 · 오늘 보낼 것 · 백업 · 「{nm}」 홍보물 · 스모크 테스트')
    print(f'[여기서 사람이 하는 것] 입금 확인 {wait}건 · 보내기 {paid}건 · 홍보물을 채널에 올리기')
    return 1 if bad else 0


def taste():
    if '--뒤' in A and len(A) > A.index('--뒤') + 1:   # 조금 뒤에 저절로: 떨어진 프로세스로 넘기고 바로 돌아온다
        mins = float(A[A.index('--뒤') + 1]); os.makedirs(os.path.join(HERE, 'logs'), exist_ok=True)
        log = open(os.path.join(HERE, 'logs', '자동.log'), 'a', encoding='utf-8')
        kw = dict(creationflags=0x00000008 | 0x00000200) if os.name == 'nt' else dict(start_new_session=True)
        subprocess.Popen(PY + [os.path.abspath(__file__), '맛보기', '--기다림', str(int(mins * 60))], cwd=HERE, stdout=log, stderr=log, stdin=subprocess.DEVNULL, **kw)
        print(f'{mins:g}분 뒤에 저절로 시작합니다. 이 창을 닫거나 자리를 비워도 됩니다.\n끝나면 넘김/자리비운동안.md 한 장이 생깁니다(돌아와서 「자리 비운 동안 뭐 했어?」 한 줄이면 세션이 읽어 줍니다).'); return 0
    if '--기다림' in A:
        time.sleep(int(A[A.index('--기다림') + 1]))
    t0 = time.time(); S = site(); P = S.get('parts', {}); info = bool(P.get('info')); writing = S.get('frame') == 'medium'
    print('━━ 일일 배치 — 사람 없이 끝까지 ━━', flush=True)
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)   # 도중에 죽어도 지난번의 「성공」 한 장이 남아 거짓말하지 않게, 시작할 때 이번 판을 「아직 끝나지 않음」으로 먼저 적는다
    open(REPORT, 'w', encoding='utf-8').write('# 자리 비운 동안 — ' + time.strftime('%Y-%m-%d %H:%M') + ' 시작' + chr(10)*2 + '이번 일일 배치는 아직 끝나지 않았거나 도중에 멈췄다. 끝났다면 이 줄 아래에 결과가 다시 쓰인다. 멈춘 까닭은 `logs/daily.md` 와 터미널 출력에서 찾는다.' + chr(10))
    pg = os.path.join(HERE, '진도.json'); did = [x.get('what', '') for x in (json.load(open(pg, encoding='utf-8')).get('done', []) if os.path.exists(pg) else [])]
    shop = '본 가게' in did and os.path.exists(os.path.join(HERE, 'shop', 'api', 'data', 'shop.db')); article = '본 글' in did or not shop
    if not article:
        return taste_shop(t0, only=True)
    print('  이 사이트: ' + ('글 사이트 — 뉴스를 모으지 않고, 가장 새 글로 알릴 것을 만듭니다' if writing else '켜진 부품: ' + ', '.join(k for k, v in P.items() if v)), flush=True)
    R = [step('모으기·묶기·대조·빌드(일일 배치)' if info else '빌드(일일 배치 — 뉴스 모으기·대조는 꺼져 있어 건너뜀)', ['run_daily.py'])]
    has_notes = bool(glob.glob(os.path.join(HERE, 'notes', '2*.json')))
    if info and has_notes:
        R.append(step('알릴 글(블로그 글·알림 문구 세 길이)', ['promo.py']))
        R.append(step('알릴 그림(공유 카드·정사각 카드)', ['card.py', '--square']))
        if not (os.environ.get('FFMPEG') or shutil.which('ffmpeg')):   # 이 PC 의 파이썬 꾸러미 안에 들어 있는 것도 찾아본다
            try:
                import imageio_ffmpeg; os.environ['FFMPEG'] = imageio_ffmpeg.get_ffmpeg_exe()
            except Exception:
                pass
        if os.environ.get('FFMPEG') or shutil.which('ffmpeg'):
            R.append(step('알릴 영상(세로 짧은 영상)', ['shorts.py']))
        else:
            R.append(dict(name='알릴 영상(세로 짧은 영상)', ok=None, secs=0, tail='건너뜀: 이 PC 에 ffmpeg 이 없습니다(있으면 저절로 만들어집니다)', err=''))
            print('  – 알릴 영상 — 건너뜀: ffmpeg 없음', flush=True)
    elif writing:
        try:
            R.append(post_promo(S))
        except Exception as e:   # 글 사이트 프로그램(medium.py 등)이 고장 나 불러오지 못해도 배치 전체가 죽지 않고 이 걸음만 ✗ 로 남는다
            print(f'  ✗ 알릴 글·그림(가장 새 글로) — {repr(e)[:120]}', flush=True)
            R.append(dict(name='알릴 글·그림(가장 새 글로)', ok=False, secs=0, tail='', err=repr(e)[:200]))
    else:
        print('  – 알릴 글·그림·영상 — 건너뜀: 이 사이트에는 소식 노트도 글도 없습니다', flush=True)
    if any(P.get(k) for k in ('board', 'market', 'trend')):
        R.append(step('운영자의 하루 일(들어온 것 읽기)', ['ops.py']))
    R.append(step('점검(깨진 주소·빈 페이지)', ['audit.py']))
    if shop:
        R += taste_shop(t0, only=False)
    made = [('새로 빌드한 페이지', new_files('docs', t0, ['**/index.html'])), ('블로그 글', new_files('promo_out', t0, ['*/블로그글.md'])), ('알림 문구', new_files('promo_out', t0, ['*/알림_*.txt'])),
            ('카드 그림', new_files('cards', t0, ['*.png']) + new_files('promo_out', t0, ['*/카드.png'])), ('영상', new_files('shorts', t0, ['*.mp4']))]
    total = time.time() - t0
    L = [f'# 자리 비운 동안 — {time.strftime("%Y-%m-%d %H:%M")}', '', f'사람 입력 없이 {total:.0f}초 동안 돌았다. 올리기·로그인·메일 발송은 하지 않았다.', '', '## 걸음별 결과(✓ 됨 · ✗ 걸림 · – 건너뜀)']
    for r in R:
        L.append(f'- {"✓" if r["ok"] else ("–" if r["ok"] is None else "✗")} {r["name"]} ({r["secs"]:.0f}초) {r["tail"]}')
    L += ['', '## 만들어진 것']
    for what, fs in made:
        if fs:
            L.append(f'- {what} {len(fs)}개 — 예: `{os.path.relpath(fs[-1], HERE).replace(os.sep, "/")}`')
    pp = next((r['tail'].split(' ')[0] for r in R if r['name'].startswith('알릴 글·그림(가장 새 글') and r['ok']), '')   # 글 사이트면 promo_out/post_<글>/
    L += ['', '## 여기서 사람이 로그인하면 이어지는 것']
    if writing and pp:
        L += [f'- 블로그에 올리기: `{pp}블로그글.md` 를 로그인된 블로그 글쓰기 화면에(브라우저 확장이 있으면 세션이 채워 넣고 「발행」 앞에서 멈춘다)',
              f'- SNS 에 올리기: 알림 문구(`{pp}알림_*.txt`)와 카드(`{pp}카드.png`)를 로그인된 채널에']
    elif writing:
        L += ['- 블로그·SNS 에 올리기: 알릴 글이 없어 이번에는 없음']
    else:
        L += ['- 블로그에 올리기: `promo_out/<노트>/블로그글.md` 를 로그인된 블로그 글쓰기 화면에(브라우저 확장이 있으면 세션이 채워 넣고 「발행」 앞에서 멈춘다)',
              '- 영상 올리기: `shorts/<노트>.mp4` 와 제목·설명 `shorts/<노트>.txt` 를 로그인된 영상 채널에', '- 카드 올리기: `cards/<노트>_sq.png` 를 로그인된 사진 채널에']
    L += ['- 사이트 다시 올리기: 「올려」 한마디(이미 한 번 올린 사이트라면 세션이 한다)', '- 방송: `python run.py 자동 방송` 의 화면을 방송 프로그램으로 잡아 로그인된 방송 채널로 송출']
    bad = [r for r in R if r['ok'] is False]
    L += ['', '## 걸린 것'] + ([f'- {r["name"]}: {r["err"] or r["tail"]}' for r in bad] or ['- 없음'])
    os.makedirs(os.path.dirname(REPORT), exist_ok=True); open(REPORT, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print(f'\n끝 — {total:.0f}초. 한 장으로 남겼습니다: 넘김/자리비운동안.md')
    print('[사람 없이 된 것] ' + ' · '.join(f'{w} {len(f)}개' for w, f in made if f))
    print('[여기서 사람이 로그인하면 이어지는 것] 블로그·영상·카드를 채널에 올리기, 방송 송출 — 준비물은 만들어져 있습니다.')
    return 1 if bad else 0


ONAIR = r'''<!doctype html><html lang="ko"><meta charset="utf-8"><title>__NAME__ — 방송</title><style>
html,body{margin:0;height:100%;background:#0d1321;color:#fff;font-family:"Malgun Gothic","Apple SD Gothic Neo",sans-serif;overflow:hidden}
.top{position:fixed;left:0;right:0;top:0;height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 36px;background:#c1121f;font-weight:700;font-size:24px}
.live{background:#fff;color:#c1121f;border-radius:4px;padding:2px 10px;margin-right:14px;font-size:18px}
.main{position:fixed;inset:64px 0 72px 0;display:flex;flex-direction:column;justify-content:center;padding:0 8vw}
.k{font-size:22px;color:#ffd166;margin-bottom:18px}.t{font-size:6vh;line-height:1.25;font-weight:800;margin:0 0 28px}.s{font-size:3.2vh;line-height:1.6;color:#dbe4ff;max-width:60em}
.bar{position:fixed;left:0;right:0;bottom:0;height:72px;background:#1b2845;display:flex;align-items:center;overflow:hidden;font-size:24px;white-space:nowrap}
.bar span{display:inline-block;padding-left:100%;animation:m 40s linear infinite}@keyframes m{to{transform:translateX(-100%)}}
.fade{animation:f .8s}@keyframes f{from{opacity:0;transform:translateY(12px)}}
</style><div class="top"><div><span class="live">ON AIR</span>__NAME__</div><div id="clk"></div></div>
<div class="main" id="m"></div><div class="bar"><span id="tk"></span></div>
<script>var D=__DATA__,i=-1,m=document.getElementById("m");
document.getElementById("tk").textContent=D.map(function(x){return "■ "+x.title}).join("     ");
setInterval(function(){var d=new Date();document.getElementById("clk").textContent=d.toLocaleTimeString("ko-KR")},500);
function show(){i=(i+1)%D.length;var x=D[i];m.innerHTML='<div class="fade"><div class="k">'+(i+1)+" / "+D.length+(x.kind?"  ·  "+x.kind:"")+'</div><h1 class="t"></h1><div class="s"></div></div>';
m.querySelector(".t").textContent=x.title;m.querySelector(".s").textContent=x.text;var done=false,next=function(){if(done)return;done=true;setTimeout(show,2500)};
try{speechSynthesis.cancel();var u=new SpeechSynthesisUtterance(x.title+". "+x.text);u.lang="ko-KR";u.onend=next;speechSynthesis.speak(u)}catch(e){}
setTimeout(next,Math.max(9000,(x.title.length+x.text.length)*230))}
show();document.body.onclick=function(){show()};</script></html>'''


def onair():
    S = site(); items = []
    for f in ([] if S.get('frame') == 'medium' else sorted(glob.glob(os.path.join(HERE, 'notes', '2*.json')), reverse=True)[:12]):   # 글 사이트는 자기 글만
        try:
            d = json.load(open(f, encoding='utf-8')); items.append(dict(title=d.get('title', ''), text=d.get('summary', ''), kind=d.get('verdict', '')))
        except Exception:
            pass
    for f in sorted(glob.glob(os.path.join(HERE, 'posts', '*.md')))[:12]:
        T = open(f, encoding='utf-8').read().splitlines(); body = [x.strip() for x in T if x.strip() and not x.startswith(('#', '---', '|', '>', '!', '-'))  and ':' not in x[:14]]
        title = next((x.lstrip('# ').strip() for x in T if x.startswith('#')), os.path.basename(f)[:-3])
        items.append(dict(title=title, text=' '.join(body[:2])[:260], kind='글'))
    if not items:
        print('띄울 글이 없습니다(notes/ 나 posts/ 에 글이 한 편 있어야 합니다).'); return 1
    out = os.path.join(HERE, 'logs', '방송.html'); os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(ONAIR.replace('__NAME__', html.escape(S.get('name', '내 사이트'))).replace('__DATA__', json.dumps(items, ensure_ascii=False).replace('</', '<\\/')))
    print(f'방송 화면을 만들었습니다: logs/방송.html — 글 {len(items)}편을 차례로 띄우고 소리 내어 읽습니다(브라우저의 읽어 주기 기능, 끝나면 처음부터 다시).')
    if '--headless' not in A:
        try:
            os.startfile(out) if os.name == 'nt' and os.environ.get('HARNESS_NO_OPEN') != '1' else subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', out])
        except Exception:
            pass
    print('[사람 없이 된 것] 그날 글로 방송 화면이 저절로 돌아갑니다(화면을 한 번 눌러야 소리가 나는 브라우저가 있습니다).\n[여기서 사람이 로그인하면 이어지는 것] 이 창을 방송 프로그램(OBS 등)의 화면 잡기로 넣고 로그인된 방송 채널로 송출 — 송출은 사람이 시작합니다.')
    return 0


def schedule():
    rest = [a for a in A[1:] if not a.startswith('--')]
    if os.name != 'nt':
        print(f'이 PC 는 윈도우가 아닙니다. 예약은 crontab 에 한 줄로 겁니다(사람이): 0 7 * * * cd "{HERE}" && python3 auto.py 맛보기'); return 0
    if rest and rest[0] == '상태':
        r = subprocess.run(['powershell', '-NoProfile', '-Command', f"$t=Get-ScheduledTask -TaskName {TASK} -ErrorAction SilentlyContinue; if($t){{$i=$t|Get-ScheduledTaskInfo; '{{0}}|{{1}}|{{2}}' -f $i.NextRunTime.ToString('yyyy-MM-dd HH:mm'),$(if($i.LastRunTime.Year -gt 2000){{$i.LastRunTime.ToString('yyyy-MM-dd HH:mm')}}else{{'-'}}),$i.LastTaskResult}}"], capture_output=True, text=True, errors='replace')
        v = (r.stdout or '').strip().split('|')
        if len(v) == 3:
            print(f'예약이 걸려 있습니다: 다음에 도는 때 {v[0]} · 마지막으로 돈 때 {v[1]}' + ('' if v[1] == '-' else (' (잘 끝남)' if v[2] == '0' else f' (끝난 값 {v[2]} — 넘김/자리비운동안.md 를 봅니다)')))
        else:
            print('걸린 예약이 없습니다.')
        return 0
    if rest and rest[0] == '끄기':
        cmd = ['schtasks', '/Delete', '/TN', TASK, '/F']
    else:
        at = rest[0] if rest else '07:00'
        cmd = ['schtasks', '/Create', '/SC', 'DAILY', '/ST', at, '/TN', TASK, '/F', '/TR', f'"{sys.executable}" -X utf8 "{os.path.join(HERE, "auto.py")}" 맛보기']
    if '--예' not in A:
        print('걸 명령(아직 걸지 않았습니다 — 독자가 「걸어 줘」 하면 --예 를 붙여 다시 부릅니다):\n  ' + subprocess.list2cmdline(cmd) + '\n이 PC 가 켜져 있는 날 그 시각에 저절로 돌고, 결과는 넘김/자리비운동안.md 에 남습니다. 끄기: python run.py 자동 예약 끄기 --예'); return 0
    r = subprocess.run(cmd, capture_output=True, text=True, errors='replace')
    off = '/Delete' in cmd
    if r.returncode == 0:
        print('✓ 예약을 지웠습니다.' if off else f'✓ 예약을 걸었습니다: 날마다 {cmd[cmd.index("/ST") + 1]} 에 저절로 돕니다(이 PC 가 켜져 있을 때). 결과는 넘김/자리비운동안.md')
    else:
        print('✗ 예약을 ' + ('지우지' if off else '걸지') + ' 못했습니다(윈도우 작업 스케줄러가 거절했습니다).')
    return r.returncode


def main():
    c = A[0] if A else ''
    if c == '맛보기':
        return taste()
    if c == '방송':
        return onair()
    if c == '예약':
        return schedule()
    print(__doc__); return 1


if __name__ == '__main__':
    sys.exit(main())
