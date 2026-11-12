# -*- coding: utf-8 -*-
"""준비: 튜토리얼에 필요한 프로그램을 점검하고, 빠진 것은 운영체제의 설치 도구로 깐다. 파이썬 기본 기능만 쓴다.
python run.py 준비            점검하고 무엇을 어떻게 깔지 보여 준다(아직 깔지 않는다)
python run.py 준비 --예       빠진 것을 깐다 — 세션은 독자에게 「빠진 것 n개를 깔까요?」를 한 번 묻고 「예」를 들은 뒤에만 부른다
python run.py 준비 --시늉 node,git   (시험용) 그 프로그램이 없는 것처럼 보고 계획만 보여 준다
깔 때 쓰는 것: 윈도우 winget · 맥 brew · 리눅스 apt. 깔면 그 프로그램의 사용 약관에 동의하는 것이고, 윈도우는 관리자 승인 창이 뜰 수 있다(승인은 독자가 누른다).
파이썬은 이 파일을 돌리는 데 필요하므로, 파이썬이 없으면 세션이 시작.md 의 차례대로 먼저 깐다."""
import json, os, platform, shutil, subprocess, sys, urllib.request
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
A = sys.argv[1:]
FAKE = set(A[A.index('--시늉') + 1].split(',')) if '--시늉' in A and len(A) > A.index('--시늉') + 1 else set()
OS = 'win' if os.name == 'nt' else 'mac' if sys.platform == 'darwin' else 'linux'

# 이름: (무엇에 쓰나, 꼭 필요한가, 설치 꾸러미 {win, mac, linux})
NEED = {
    'git': ('저장소 받기', True, {'win': 'Git.Git', 'mac': 'git', 'linux': 'git'}),
    'node': ('2장 가게 화면(Next.js)·글 사이트 올리기', True, {'win': 'OpenJS.NodeJS.LTS', 'mac': 'node', 'linux': 'nodejs npm'}),
    'browser': ('화면 찍기·카드 그림·자동 확인', True, {'win': 'Microsoft.Edge', 'mac': 'google-chrome', 'linux': 'chromium'}),
    'ffmpeg': ('3장 짧은 영상(없으면 영상만 건너뜀)', False, {'win': 'Gyan.FFmpeg', 'mac': 'ffmpeg', 'linux': 'ffmpeg'}),
}
WIN_DIRS = {'git': [r'C:\Program Files\Git\cmd\git.exe'], 'node': [r'C:\Program Files\nodejs\node.exe'],
            'browser': [r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Google\Chrome\Application\chrome.exe']}


def find(name):
    if name in FAKE:
        return None
    if name == 'browser':
        for c in (os.environ.get('BROWSER'), shutil.which('msedge'), shutil.which('chrome'), shutil.which('google-chrome'), shutil.which('chromium'), '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'):
            if c and os.path.exists(c):
                return c
    elif name == 'ffmpeg':
        c = os.environ.get('FFMPEG') or shutil.which('ffmpeg')
        if c:
            return c
        try:
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass
    else:
        c = shutil.which(name)
        if c:
            return c
    for c in WIN_DIRS.get(name, []) if OS == 'win' else []:   # 막 깔아서 아직 PATH 에 안 잡힌 것
        if os.path.exists(c):
            return c
    return None


def version(name, path):
    if name in ('browser', 'ffmpeg'):
        return os.path.basename(path)
    try:
        return subprocess.run([path, '--version'], capture_output=True, text=True, timeout=15).stdout.strip().splitlines()[0][:40]
    except Exception:
        return '있음'


def installer():
    if OS == 'win':
        return shutil.which('winget')
    if OS == 'mac':
        return shutil.which('brew')
    return shutil.which('apt-get')


def cmd_for(name):
    pkg = NEED[name][2][OS]
    if OS == 'win':
        return ['winget', 'install', '-e', '--id', pkg, '--silent', '--accept-package-agreements', '--accept-source-agreements']
    if OS == 'mac':
        return ['brew', 'install'] + (['--cask'] if name == 'browser' else []) + pkg.split()
    return ['sudo', 'apt-get', 'install', '-y'] + pkg.split()


def main():
    print('━━ 준비 — 필요한 프로그램 점검 ━━')
    print(f'  ✔ 파이썬     {platform.python_version()}  (이 점검을 돌리는 것)')
    missing = []
    for name, (why, must, _) in NEED.items():
        p = find(name)
        if p:
            print(f'  ✔ {name:<9} {version(name, p)}')
        else:
            missing.append(name); print(f'  ✘ {name:<9} 없음 — {why}' + ('' if must else ' · 없어도 튜토리얼은 간다'))
    try:
        urllib.request.urlopen('https://www.google.com', timeout=8); net = True
    except Exception:
        net = False
    print(f'  {"✔" if net else "✘"} 인터넷     {"됨" if net else "안 됨 — 사진 받기·올리기에 필요합니다"}')
    if not missing:
        print('\n다 갖춰져 있습니다. 바로 시작합니다.'); return 0
    inst = installer()
    if not inst:
        how = {'win': 'winget(앱 설치 관리자)', 'mac': 'Homebrew(brew.sh)', 'linux': 'apt'}[OS]
        print(f'\n이 컴퓨터에는 설치 도구 {how} 가 없어 저절로 깔 수 없습니다. 아래를 깔아 주세요(공식 사이트):')
        for n in missing:
            print(f'  - {n}: ' + {'git': 'git-scm.com', 'node': 'nodejs.org (LTS)', 'browser': 'microsoft.com/edge 또는 google.com/chrome', 'ffmpeg': 'ffmpeg.org'}[n])
        return 1
    print(f'\n빠진 것 {len(missing)}개를 이렇게 깝니다:')
    for n in missing:
        print('  ' + ' '.join(cmd_for(n)))
    print('깔면 각 프로그램의 사용 약관에 동의하게 됩니다.' + (' 윈도우는 관리자 승인 창이 뜰 수 있습니다(독자가 「예」를 누릅니다).' if OS == 'win' else ' 컴퓨터 비밀번호를 물을 수 있습니다(독자가 칩니다).' if OS != 'mac' else ''))
    if '--예' not in A:
        print('\n[세션] 독자에게 한 번 묻습니다: 「빠진 것 ' + ', '.join(missing) + ' 을(를) 깔까요? 몇 분 걸립니다.」 → 「예」면 python run.py 준비 --예'); return 0
    if FAKE:
        print('\n(시늉이라 깔지 않았습니다)'); return 0
    bad = []
    for n in missing:
        print(f'\n▶ {n} 까는 중…', flush=True)
        r = subprocess.run(cmd_for(n))
        if r.returncode != 0 or not find(n):
            bad.append(n)
    print('\n' + ('✓ 다 깔았습니다.' if not bad else '✗ 깔지 못한 것: ' + ', '.join(bad) + ' — 위 출력의 마지막 줄을 그대로 알려 주세요.'))
    if OS == 'win' and not bad:
        print('막 깐 프로그램은 이 창에서 바로 안 잡힐 수 있어 설치된 자리에서 찾아 씁니다. 그래도 안 되면 터미널을 한 번 닫았다 엽니다.')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
