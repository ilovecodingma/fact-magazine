# -*- coding: utf-8 -*-
"""확인 노트 → 세로 쇼츠(1080x1920) 자동 제작. 사람 입력 없이 한 편이 나온다.
장면 3개: ① 질문과 판정 ② 확인한 사실(출처 이름) ③ 아직 확인 안 된 것 + 사이트 이름.
그림은 글자와 도형뿐(이미지 모델 없음). 글 장면은 브라우저로 찍고, ffmpeg 으로 묶는다. 목소리는 윈도우 기본 음성이 있으면 쓰고 없으면 무음.
필요한 것: ① 파이썬(기본 기능만) ② Edge·Chrome 중 하나 ③ ffmpeg (없으면 안내 문구가 나옵니다 — 런북 10절)
사용: python shorts.py                 notes/ 의 모든 노트(예시 제외)로 만들기
      python shorts.py notes/2026-11-11-export.json   한 편만
결과: shorts/<노트 id>.mp4 + shorts/<노트 id>.txt (제목·설명 글)"""
import glob, html, json, os, re, shutil, subprocess, sys, tempfile, wave
try:
    sys.stdout.reconfigure(encoding='utf-8')   # 윈도우에서 한글 출력이 깨지지 않게
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'shorts')
E = html.escape
VCOL = {'확인됨': '#0b5d2f', '일부만 확인됨': '#8a4b00', '아직 확인 안 됨': '#a11a12'}


def site():
    """사이트 이름·공개 주소를 site.json(+site.local.json, 환경변수)에서 읽는다. 주소가 안내용 기본값이면 빈 글자."""
    S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
    lp = os.path.join(HERE, 'site.local.json')
    if os.path.exists(lp):
        S.update(json.load(open(lp, encoding='utf-8')))
    for k, env in (('name', 'SITE_NAME'), ('url', 'SITE_URL')):
        if os.environ.get(env):
            S[k] = os.environ[env]
    url = S.get('url', '').rstrip('/')
    if (not url) or '프로젝트이름' in url or '내계정' in url:
        url = ''
    return S['name'], url


def find_tools():
    """ffmpeg 와 브라우저 실행 파일을 찾는다. 없으면 안내를 내고 멈춘다."""
    ff = os.environ.get('FFMPEG') or shutil.which('ffmpeg')
    cands = [os.environ.get('BROWSER', ''), shutil.which('msedge') or '', shutil.which('chrome') or '', shutil.which('google-chrome') or '', shutil.which('chromium') or '',
             r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
             r'C:\Program Files\Google\Chrome\Application\chrome.exe', r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
             '/usr/bin/google-chrome', '/usr/bin/chromium', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    br = next((c for c in cands if c and os.path.exists(c)), None)
    if not ff:
        sys.exit('ffmpeg 가 없습니다. 설치: 윈도우 `winget install Gyan.FFmpeg`, 맥 `brew install ffmpeg`, 리눅스 `sudo apt install ffmpeg`. 이미 있으면 환경변수 FFMPEG 에 실행 파일 경로를 주세요. (런북 10절)')
    if not br:
        sys.exit('Edge 또는 Chrome 을 찾지 못했습니다. 환경변수 BROWSER 에 실행 파일 경로를 주세요. (런북 10절)')
    return ff, br


def clip(text, n):
    """한 줄 자막으로 쓸 만큼 자른다(문장 끝에서). 숫자 한가운데서 자르지 않는다."""
    text = re.sub(r'\s+', ' ', text).strip()
    return text if len(text) <= n else None


def scenes(note, name, url):
    """노트 → 장면 3개: (제목 줄, 본문 html, 읽을 글)."""
    v = note['verdict']; col = VCOL[v]
    facts = [f for f in note.get('facts', []) if clip(f['text'], 100)][:3]
    unc = [x for x in note.get('unconfirmed', []) if clip(x, 90)][:3]
    s1 = (f'<div class="lb">확인 노트 · {E(note["date"])}</div><h1>{E(note["question"])}</h1><div class="stamp" style="color:{col};border-color:{col}">{E(v)}</div>',
          f'{note["question"]} 판정은 {v}입니다.')
    if facts:
        body = ''.join(f'<p class="fact">{E(f["text"])}<span class="src">출처 · {E(f["source"])}</span></p>' for f in facts)
        say = '확인한 사실입니다. ' + ' '.join(f['text'] + ' 출처, ' + f['source'] + '.' for f in facts)
    else:
        body = '<p class="fact">공식 자료에서 같은 내용을 아직 찾지 못했습니다.</p>'
        say = '공식 자료에서 같은 내용을 아직 찾지 못했습니다.'
    s2 = (f'<div class="lb">확인한 사실</div>{body}', say)
    ub = ''.join(f'<p class="fact">{E(x)}</p>' for x in unc) or '<p class="fact">남은 확인 사항은 없습니다.</p>'
    foot = f'<div class="foot"><b>{E(name)}</b><br>{E(url) if url else "공식 자료로 한 번 더 확인합니다"}</div>'
    s3 = (f'<div class="lb">아직 확인 안 된 것</div>{ub}</div>{foot}<div>', ('아직 확인 안 된 것입니다. ' + ' '.join(unc) if unc else '남은 확인 사항은 없습니다.') + f' {name}에서 공식 자료로 한 번 더 확인합니다.')
    return [s1, s2, s3]


PAGE = """<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
*{box-sizing:border-box}html,body{margin:0;width:1080px;height:1920px;background:#fff;color:#111;overflow:hidden}
body{font-family:'Noto Serif KR','Nanum Myeongjo','Batang',serif;padding:120px 90px 330px;position:relative}
.top{position:absolute;left:0;right:0;top:0;text-align:center;border-bottom:6px double #111;padding:36px 0 22px}
.top b{font-size:64px;font-weight:900;letter-spacing:-1px}.top div{font:600 26px system-ui,'Malgun Gothic',sans-serif;color:#555;margin-bottom:8px}
.main{position:absolute;left:90px;right:90px;top:280px;bottom:360px;display:flex;flex-direction:column;justify-content:center}
.lb{font:800 34px system-ui,'Malgun Gothic',sans-serif;letter-spacing:2px;color:#555;border-top:4px solid #111;padding-top:18px;margin:0 0 40px}
h1{font-size:84px;line-height:1.35;font-weight:800;margin:0 0 60px;letter-spacing:-2px}
.stamp{display:inline-block;font:900 64px system-ui,'Malgun Gothic',sans-serif;border:6px solid;padding:14px 34px}
.fact{font-size:50px;line-height:1.55;margin:0 0 44px;font-weight:600}.src{display:block;font:600 32px system-ui,'Malgun Gothic',sans-serif;color:#0b3d91;margin-top:8px}
.foot{position:absolute;left:90px;right:90px;bottom:330px;border-top:4px solid #111;padding-top:24px;font:600 34px/1.5 system-ui,'Malgun Gothic',sans-serif;color:#333}.foot b{font:900 54px 'Noto Serif KR','Nanum Myeongjo','Batang',serif;color:#111}
</style></head><body><div class="top"><div>%s</div><b>%s</b></div><div class="main">%s</div></body></html>"""


def screenshot(browser, html_path, png):
    subprocess.run([browser, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1080,1920', '--screenshot=' + png, 'file:///' + html_path.replace('\\', '/')],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    return os.path.exists(png)


def speak(text, wav):
    """윈도우 기본 한국어 음성으로 읽기. 음성이 없거나 윈도우가 아니면 False(무음으로 진행)."""
    if os.name != 'nt':
        return False
    txt = wav + '.txt'
    open(txt, 'w', encoding='utf-8').write(text)
    ps = ("Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
          "$v=$s.GetInstalledVoices() | Where-Object {$_.VoiceInfo.Culture.Name -eq 'ko-KR'} | Select-Object -First 1; if(-not $v){exit 3}; "
          "$s.SelectVoice($v.VoiceInfo.Name); $s.Rate=1; $s.SetOutputToWaveFile('%s'); $s.Speak((Get-Content -Raw -Encoding UTF8 '%s')); $s.Dispose()" % (wav, txt))
    r = subprocess.run(['powershell', '-NoProfile', '-Command', ps], capture_output=True, timeout=120)
    return r.returncode == 0 and os.path.exists(wav) and os.path.getsize(wav) > 1000


def wav_len(wav):
    with wave.open(wav) as w:
        return w.getnframes() / float(w.getframerate())


def make(note_path, ff, br):
    note = json.load(open(note_path, encoding='utf-8'))
    name, url = site()
    sc = scenes(note, name, url)
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='shorts_')
    parts = []
    date = note['date']
    try:
        for i, (body, say) in enumerate(sc, 1):
            hp = os.path.join(tmp, f's{i}.html'); png = os.path.join(tmp, f's{i}.png'); wav = os.path.join(tmp, f's{i}.wav')
            open(hp, 'w', encoding='utf-8').write(PAGE % (E(date), E(name), body))
            if not screenshot(br, hp, png):
                sys.exit('장면 그림을 만들지 못했습니다(브라우저 실행 실패): ' + br)
            voiced = speak(say, wav)
            dur = (wav_len(wav) + 1.0) if voiced else max(6.0, len(say) / 7.0)
            dur = min(max(dur, 5.0), 16.0)
            seg = os.path.join(tmp, f'seg{i}.mp4')
            vf = "zoompan=z='min(zoom+0.0004,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,format=yuv420p"
            cmd = [ff, '-y', '-loglevel', 'error', '-loop', '1', '-t', f'{dur:.2f}', '-i', png]
            cmd += (['-i', wav] if voiced else ['-f', 'lavfi', '-t', f'{dur:.2f}', '-i', 'anullsrc=r=44100:cl=mono'])
            cmd += ['-vf', vf, '-c:v', 'libx264', '-r', '30', '-c:a', 'aac', '-ar', '44100', '-ac', '1', '-t', f'{dur:.2f}', seg]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                sys.exit('ffmpeg 실패: ' + r.stderr[-300:])
            parts.append(seg)
        lst = os.path.join(tmp, 'list.txt')
        open(lst, 'w', encoding='utf-8').write(''.join("file '" + p.replace('\\', '/') + "'\n" for p in parts))
        out = os.path.join(OUT, note['id'] + '.mp4')
        r = subprocess.run([ff, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', out], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit('ffmpeg 이어 붙이기 실패: ' + r.stderr[-300:])
        for i in range(1, 4):   # 장면 그림도 같이 남긴다(확인·책 캡처용)
            shutil.copy(os.path.join(tmp, f's{i}.png'), os.path.join(OUT, f'{note["id"]}_장면{i}.png'))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    title = f'{note["title"]} | {name}'
    if len(title) > 95:
        title = f'{note["title"][:80]}… | {name}'
    desc = f'{note["question"]}\n판정: {note["verdict"]}\n{note["summary"]}\n\n공식 자료로 한 번 더 확인합니다.' + (f'\n노트 전문: {url}/n/{note["id"]}/' if url else '\n(공개 주소가 정해지면 노트 주소를 여기에 넣습니다)')
    open(os.path.join(OUT, note['id'] + '.txt'), 'w', encoding='utf-8').write(f'제목\n{title}\n\n설명\n{desc}\n')
    return out


def main():
    ff, br = find_tools()
    paths = [a for a in sys.argv[1:] if not a.startswith('-')]
    if not paths:
        for p in sorted(glob.glob(os.path.join(HERE, 'notes', '*.json'))):
            if not json.load(open(p, encoding='utf-8')).get('example'):
                paths.append(p)
    if not paths:
        sys.exit('만들 노트가 없습니다(notes/ 에 노트를 넣으세요).')
    for p in paths:
        print('만드는 중:', os.path.basename(p))
        print('  ->', make(p, ff, br))


if __name__ == '__main__':
    main()
