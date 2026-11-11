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
        rc = r.returncode; tail = ((r.stdout or '').strip().splitlines() or [''])[-1][:160]; err = (r.stderr or '').strip()[-300:]
    except Exception as e:
        rc, tail, err = 1, '', repr(e)[:200]
    print(f'  {"✓" if rc == 0 else "✗"} {name} — {time.time() - t:.0f}초  {tail}', flush=True)
    return dict(name=name, ok=rc == 0, secs=time.time() - t, tail=tail, err=err)


def taste():
    if '--뒤' in A and len(A) > A.index('--뒤') + 1:   # 조금 뒤에 저절로: 떨어진 프로세스로 넘기고 바로 돌아온다
        mins = float(A[A.index('--뒤') + 1]); os.makedirs(os.path.join(HERE, 'logs'), exist_ok=True)
        log = open(os.path.join(HERE, 'logs', '자동.log'), 'a', encoding='utf-8')
        kw = dict(creationflags=0x00000008 | 0x00000200) if os.name == 'nt' else dict(start_new_session=True)
        subprocess.Popen(PY + [os.path.abspath(__file__), '맛보기', '--기다림', str(int(mins * 60))], cwd=HERE, stdout=log, stderr=log, stdin=subprocess.DEVNULL, **kw)
        print(f'{mins:g}분 뒤에 저절로 시작합니다. 이 창을 닫거나 자리를 비워도 됩니다.\n끝나면 넘김/자리비운동안.md 한 장이 생깁니다(돌아와서 「자리 비운 동안 뭐 했어?」 한 줄이면 세션이 읽어 줍니다).'); return 0
    if '--기다림' in A:
        time.sleep(int(A[A.index('--기다림') + 1]))
    t0 = time.time(); S = site(); P = S.get('parts', {}); info = bool(P.get('info'))
    print('━━ 자동 — 사람 없이 끝까지 ━━', flush=True)
    R = [step('모으기·묶기·대조·화면(하루 한 바퀴)', ['run_daily.py'])]
    has_notes = bool(glob.glob(os.path.join(HERE, 'notes', '2*.json')))
    if info and has_notes:
        R.append(step('알릴 글(블로그 글·알림 문구 세 길이)', ['promo.py']))
        R.append(step('알릴 그림(공유 카드·정사각 카드)', ['card.py', '--square']))
        if os.environ.get('FFMPEG') or shutil.which('ffmpeg'):
            R.append(step('알릴 영상(세로 짧은 영상)', ['shorts.py']))
        else:
            R.append(dict(name='알릴 영상(세로 짧은 영상)', ok=None, secs=0, tail='건너뜀: 이 PC 에 ffmpeg 이 없습니다(있으면 저절로 만들어집니다)', err=''))
            print('  – 알릴 영상 — 건너뜀: ffmpeg 없음', flush=True)
    else:
        print('  – 알릴 글·그림·영상 — 건너뜀: 이 사이트에는 소식 노트가 없습니다(글 사이트·게시판·장터·순위는 화면과 운영자 일만 돕니다)', flush=True)
    if any(P.get(k) for k in ('board', 'market', 'trend')):
        R.append(step('운영자의 하루 일(들어온 것 읽기)', ['ops.py']))
    R.append(step('점검(깨진 주소·빈 쪽)', ['audit.py']))
    made = [('새로 찍은 쪽', new_files('docs', t0, ['**/index.html'])), ('블로그 글', new_files('promo_out', t0, ['*/블로그글.md'])), ('알림 문구', new_files('promo_out', t0, ['*/알림_*.txt'])),
            ('카드 그림', new_files('cards', t0, ['*.png'])), ('영상', new_files('shorts', t0, ['*.mp4']))]
    total = time.time() - t0
    L = [f'# 자리 비운 동안 — {time.strftime("%Y-%m-%d %H:%M")}', '', f'사람 입력 없이 {total:.0f}초 동안 돌았다. 올리기·로그인·메일 발송은 하지 않았다.', '', '## 사람 없이 된 것']
    for r in R:
        L.append(f'- {"✓" if r["ok"] else ("–" if r["ok"] is None else "✗")} {r["name"]} ({r["secs"]:.0f}초) {r["tail"]}')
    L += ['', '## 만들어진 것']
    for what, fs in made:
        if fs:
            L.append(f'- {what} {len(fs)}개 — 예: `{os.path.relpath(fs[-1], HERE).replace(os.sep, "/")}`')
    L += ['', '## 여기서 사람이 로그인하면 이어지는 것', '- 블로그에 올리기: `promo_out/<글>/블로그글.md` 를 로그인된 블로그 글쓰기 화면에(브라우저 확장이 있으면 세션이 채워 넣고 「발행」 앞에서 멈춘다)',
          '- 영상 올리기: `shorts/<글>.mp4` 와 제목·설명 `shorts/<글>.txt` 를 로그인된 영상 채널에', '- 카드 올리기: `cards/<글>_sq.png` 를 로그인된 사진 채널에', '- 사이트 다시 올리기: 「올려」 한마디(이미 한 번 올린 사이트라면 세션이 한다)',
          '- 방송: `python run.py 자동 방송` 의 화면을 방송 프로그램으로 잡아 로그인된 방송 채널로 송출']
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
try{speechSynthesis.cancel();var u=new SpeechSynthesisUtterance(x.title+". "+x.text);u.lang="ko-KR";u.onend=next;u.onerror=next;speechSynthesis.speak(u)}catch(e){}
setTimeout(next,Math.max(9000,(x.title.length+x.text.length)*230))}
show();document.body.onclick=function(){show()};</script></html>'''


def onair():
    S = site(); items = []
    for f in sorted(glob.glob(os.path.join(HERE, 'notes', '2*.json')), reverse=True)[:12]:
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
            os.startfile(out) if os.name == 'nt' else subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', out])
        except Exception:
            pass
    print('[사람 없이 된 것] 그날 글로 방송 화면이 저절로 돌아갑니다(화면을 한 번 눌러야 소리가 나는 브라우저가 있습니다).\n[여기서 사람이 로그인하면 이어지는 것] 이 창을 방송 프로그램(OBS 등)의 화면 잡기로 넣고 로그인된 방송 채널로 송출 — 송출은 사람이 시작합니다.')
    return 0


def schedule():
    rest = [a for a in A[1:] if not a.startswith('--')]
    if os.name != 'nt':
        print(f'이 PC 는 윈도우가 아닙니다. 예약은 crontab 에 한 줄로 겁니다(사람이): 0 7 * * * cd "{HERE}" && python3 auto.py 맛보기'); return 0
    if rest and rest[0] == '상태':
        r = subprocess.run(['schtasks', '/Query', '/TN', TASK], capture_output=True, text=True, errors='replace')
        print('예약이 걸려 있습니다:\n' + r.stdout.strip() if r.returncode == 0 else '걸린 예약이 없습니다.'); return 0
    if rest and rest[0] == '끄기':
        cmd = ['schtasks', '/Delete', '/TN', TASK, '/F']
    else:
        at = rest[0] if rest else '07:00'
        cmd = ['schtasks', '/Create', '/SC', 'DAILY', '/ST', at, '/TN', TASK, '/F', '/TR', f'"{sys.executable}" -X utf8 "{os.path.join(HERE, "auto.py")}" 맛보기']
    if '--예' not in A:
        print('걸 명령(아직 걸지 않았습니다 — 독자가 「걸어 줘」 하면 --예 를 붙여 다시 부릅니다):\n  ' + subprocess.list2cmdline(cmd) + '\n이 PC 가 켜져 있는 날 그 시각에 저절로 돌고, 결과는 넘김/자리비운동안.md 에 남습니다. 끄기: python run.py 자동 예약 끄기 --예'); return 0
    r = subprocess.run(cmd, capture_output=True, text=True, errors='replace')
    print(('✓ ' if r.returncode == 0 else '✗ ') + (r.stdout or r.stderr).strip()); return r.returncode


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
