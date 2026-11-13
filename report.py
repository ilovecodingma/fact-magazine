# -*- coding: utf-8 -*-
"""내 기록 한 장: 설치와 첫 결과물까지 걸린 시간, 막힌 곳의 종류, 한 일의 횟수를 한 장으로 모은다. 파이썬 기본 기능만 쓴다.
python run.py 내기록        한 장을 보여 주고 넘김/내기록.md 에 적는다(저장소 이력에 올라가지 않는다)
이 한 장은 내 컴퓨터에만 있고 어디로도 저절로 보내지 않는다. 시험에 참여할 때 독자가 직접 내밀 때만 남에게 간다.
들어가지 않는 것: 이름, 사이트·가게의 이름과 주소, 파일 경로, 독자가 한 말, 주문 내용."""
import collections, datetime, json, os, platform, shutil, subprocess, sys, time
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '넘김', '내기록.md')


def _t(s):
    try:
        return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M')
    except Exception:
        return None


def _ver(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15, shell=(os.name == 'nt'), errors='replace')
        if r.returncode != 0:
            return None   # 없거나 실행되지 않음(운영체제의 오류 글은 담지 않는다)
        out = (r.stdout or r.stderr).strip()
        return out.splitlines()[0][:60] if out else '있음'
    except Exception:
        return None


def main():
    pg = os.path.join(HERE, '진도.json'); d = json.load(open(pg, encoding='utf-8')) if os.path.exists(pg) else {'done': []}
    done = [(x.get('what', ''), _t(x.get('t', ''))) for x in d.get('done', [])]
    times = [t for _, t in done if t]
    made = [w[2:].strip() for w, _ in done if w.startswith('본 ')]
    ups = [t for w, t in done if w.startswith('올림: ') and t]
    # 시작: 저장소를 받은 때(윈도우는 폴더 생성 시각). 다른 운영체제는 알 수 없어 진도의 첫 줄만 쓴다
    got = None
    if os.name == 'nt':
        try:
            got = datetime.datetime.fromtimestamp(os.path.getctime(os.path.join(HERE, '.git'))).replace(second=0, microsecond=0)
        except Exception:
            got = None
    first_step = min(times) if times else None
    first_result = min(ups) if ups else None
    cnt = lambda p: sum(1 for w, _ in done if w.startswith(p))
    stuck = collections.Counter(x.get('code', '') for x in (d.get('stuck') or []))
    days = sorted({t.strftime('%Y-%m-%d') for t in times})
    L = ['# 내 기록 한 장', '', f'정리한 때: {time.strftime("%Y-%m-%d %H:%M")}', '', '## 환경',
         f'- 운영체제: {platform.system()} {platform.release()}', f'- 파이썬: {platform.python_version()}',
         f'- Claude Code: {_ver(["claude", "--version"]) or "확인되지 않음"}']
    for name, cmds in (('git', ['git', '--version']), ('node', ['node', '--version']), ('ffmpeg', ['ffmpeg', '-version'])):
        L.append(f'- {name}: {_ver(cmds) or "없음"}')
    L += ['', '## 시작에서 첫 결과물까지', f'- 만든 것: {", ".join(dict.fromkeys(made)) or "아직 없음"}',
          f'- 저장소를 받은 때: {got.strftime("%Y-%m-%d %H:%M") if got else "알 수 없음"}',
          f'- 뼈대를 띄운 때(첫 기록): {first_step.strftime("%Y-%m-%d %H:%M") if first_step else "아직 없음"}',
          f'- 첫 결과물(첫 배포 주소)이 나온 때: {first_result.strftime("%Y-%m-%d %H:%M") if first_result else "아직 없음"}']
    if first_result and (got or first_step):
        base = got or first_step
        L.append(f'- 받은 때부터 첫 결과물까지: {max(0, int((first_result - base).total_seconds() // 60))}분' + ('' if got else '(뼈대를 띄운 때부터)'))
    L += ['', '## 한 일의 횟수', f'- 구현 요청(말 한 줄로 바꾼 것): {cnt("바꿈: ")}', f'- 롤백(되돌린 것): {cnt("되돌리기")}', f'- 배포: {cnt("올림: ")}',
          f'- 일일 배치(사람 없이 돈 것): {cnt("자동 ")}']
    L += ['', '## 막힌 곳(종류만)']
    L += [f'- {k}: {v}번' for k, v in stuck.most_common()] or ['- 기록된 것 없음']
    L += ['', '## 이어서 한 날', f'- 기록이 있는 날: {", ".join(days) if days else "없음"}' + (f' (첫 날 뒤로 {len(days) - 1}일 더)' if len(days) > 1 else ''), '',
          '이 한 장은 내 컴퓨터의 `넘김/내기록.md` 에만 있습니다. 시험에 참여한다면 이 파일을 직접 건네 주세요.']
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L))
    return 0


if __name__ == '__main__':
    sys.exit(main())
