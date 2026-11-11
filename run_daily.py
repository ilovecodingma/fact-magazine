# -*- coding: utf-8 -*-
"""하루 한 바퀴를 한 번에: 수집 → 묶기 → 대조 → 화면 → 호 발행 → 쇼츠 → 올리기 → 메일 한 통 → 기록.
사용: python run_daily.py                 올리기·메일 없이 만들기까지(안전한 기본)
      python run_daily.py --deploy        끝에 git 커밋·푸시까지(저장소가 호스팅에 연결돼 있을 때)
      python run_daily.py --mail          끝에 소식지 미리보기(보내지는 않음). 실제 발송은 --mail --send (받는 주소 확인 뒤에만)
      python run_daily.py --dry           하는 일만 보여 주고 실행하지 않음(기록도 남기지 않음)
      python run_daily.py --skip 수집,쇼츠   그 이름의 단계를 건너뜀(단계 이름은 --dry 로 확인)
부품은 site.json 의 parts 로 켜고 끕니다(info·games·issue·shorts·mail). 한 단계가 실패하면 거기서 멈추고 logs/ 에 남깁니다(같은 실패가 두 번 이어지면 사람이 봅니다).
윈도우 작업 스케줄러에 걸어 컴퓨터가 알아서 돌리는 방법은 런북 12절."""
import datetime, json, os, subprocess, sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
LOGS = os.path.join(HERE, 'logs')
ARGS = sys.argv[1:]


def parts():
    P = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8')).get('parts', {})
    return P


def run(name, cmd, env=None):
    """한 단계를 실행하고 (성공 여부, 출력 끝 3줄)을 돌려준다."""
    print(f'▶ {name}: {" ".join(os.path.basename(c) if os.path.exists(c) else c for c in cmd)}')
    if '--dry' in ARGS:
        return True, ''
    r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace', env={**os.environ, **(env or {})})
    tail = '\n'.join((r.stdout + r.stderr).strip().splitlines()[-3:])
    print('   ' + tail.replace('\n', '\n   '))
    return r.returncode == 0, tail


def main():
    P = parts()
    on = lambda k: P.get(k, True)
    os.makedirs(LOGS, exist_ok=True)
    start = datetime.datetime.now()
    steps, done = [], []
    clean = {'SITE_EXTRAS': '{}'}   # 저장소에 올라가는 docs/ 는 내 값(쿠팡 등) 없이 만든다
    if not on('info'):
        print('▷ 수집·묶기·대조 — 건너뜀: 이 사이트는 뉴스 기능이 꺼져 있어 이 단계는 건너뜁니다')
    if on('info'):
        steps += [('수집', [PY, '-X', 'utf8', 'collect.py'], None), ('묶기', [PY, '-X', 'utf8', 'group.py'], None), ('대조', [PY, '-X', 'utf8', 'check.py'], None)]
    steps.append(('화면(빌드)', [PY, '-X', 'utf8', 'build.py'], clean))
    if on('issue'):
        steps += [('호 발행(PDF)', [PY, '-X', 'utf8', 'issue.py'], None), ('화면 다시(PDF 링크)', [PY, '-X', 'utf8', 'build.py'], clean)]
    if on('shorts'):
        import shutil
        if os.environ.get('FFMPEG') or shutil.which('ffmpeg'):
            steps.append(('쇼츠', [PY, '-X', 'utf8', 'shorts.py'], None))
        else:
            print('▷ 쇼츠 — 건너뜀: ffmpeg 가 없습니다(설치: 윈도우 `winget install Gyan.FFmpeg`, 맥 `brew install ffmpeg`, 리눅스 `sudo apt install ffmpeg`. 깔면 다음 한 바퀴부터 만들어집니다)')
    if '--deploy' in ARGS:
        steps += [('올리기: 커밋', ['git', 'add', '-A'], None), ('올리기: 푸시', ['git', 'commit', '-m', f'자동 갱신 {datetime.date.today()}'], None), ('올리기: 푸시', ['git', 'push'], None)]
    if '--mail' in ARGS and on('mail'):
        steps.append(('메일', [PY, '-X', 'utf8', 'mail.py'] + (['--send'] if '--send' in ARGS else []), None))
    if '--skip' in ARGS:
        skip = [x.strip() for x in ARGS[ARGS.index('--skip') + 1].split(',')]
        steps = [s for s in steps if s[0] not in skip]
    if '--dry' in ARGS:
        for name, cmd, env in steps:
            print(f'▶ {name}: ' + ' '.join(os.path.basename(c) if os.path.exists(c) else c for c in cmd))
        print(f'시험 실행: 할 일 {len(steps)}단계(실행하지 않았고 기록도 남기지 않았습니다)')
        sys.exit(0)
    ok_all = True
    for name, cmd, env in steps:
        ok, tail = run(name, cmd, env)
        done.append((name, ok, tail))
        if not ok and not (name == '올리기: 푸시' and 'nothing to commit' in tail):   # 바뀐 것이 없어 커밋이 안 되는 것은 실패가 아님
            ok_all = False
            print(f'✖ {name} 에서 멈춥니다.'); break
    line = f'{start:%Y-%m-%d %H:%M} 하루 한 바퀴 {"성공" if ok_all else "중단"} — ' + ', '.join(f'{n}{"✓" if o else "✗"}' for n, o, _ in done)
    open(os.path.join(LOGS, 'daily.md'), 'a', encoding='utf-8').write('- ' + line + '\n')
    print(line)
    sys.exit(0 if ok_all else 1)


if __name__ == '__main__':
    main()
