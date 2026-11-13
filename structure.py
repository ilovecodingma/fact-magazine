# -*- coding: utf-8 -*-
"""내 서비스의 구조: 독자의 지금 폴더에서 원본·결과물·올라간 곳·돌고 있는 프로그램·최근 한 일을 한 번에 모아 보여 준다. 읽기만 한다. 파이썬 기본 기능만 쓴다.
python run.py 구조            이 폴더의 원본·결과물·올라간 곳 등
python run.py 구조 운영      거기에 더해 「운영 중」: 예약 실행·마지막 일일 배치·가게 프로그램(PID)·터널 주소·마지막 백업
세션은 이 값을 흐름 순서(원본 → 스냅샷 → 빌드 → 결과물 → 배포 → 손님)로 풀어 설명한다(참고/흐름_풀이.md)."""
import glob, json, os, socket, sqlite3, subprocess, sys, time
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))


def jl(p, d=None):
    try:
        return json.load(open(os.path.join(HERE, p), encoding='utf-8'))
    except Exception:
        return d


def up(port):
    s = socket.socket(); s.settimeout(0.5)
    try:
        s.connect(('127.0.0.1', port)); return True
    except Exception:
        return False
    finally:
        s.close()


def size(path):
    t = n = 0
    for r, _, fs in os.walk(path):
        for f in fs:
            try:
                t += os.path.getsize(os.path.join(r, f)); n += 1
            except OSError:
                pass
    return n, t


def pid_alive(pid):
    try:
        r = subprocess.run(['tasklist', '/FI', f'PID eq {int(pid)}', '/NH'], capture_output=True, text=True, errors='replace', timeout=15) if os.name == 'nt' else None
        if r is not None:
            return str(int(pid)) in r.stdout
        os.kill(int(pid), 0); return True
    except Exception:
        return False


def running():
    """운영 중: 지금 실행 중인 것과 마지막으로 정상으로 돈 때."""
    print('\n━━ 운영 중 — 지금 무엇이 실행되고 있나 ━━')
    try:
        r = subprocess.run([sys.executable, '-X', 'utf8', os.path.join(HERE, 'auto.py'), '예약', '상태'], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
        print('[예약 실행] ' + ((r.stdout or '').strip().splitlines() or ['확인하지 못함'])[-1])
    except Exception:
        print('[예약 실행] 확인하지 못함')
    rp = os.path.join(HERE, '넘김', '자리비운동안.md')
    if os.path.exists(rp):
        txt = open(rp, encoding='utf-8').read(); bad = '## 걸린 것\n- 없음' not in txt
        print(f'[마지막 일일 배치] {time.strftime("%m-%d %H:%M", time.localtime(os.path.getmtime(rp)))} · ' + ('걸린 것이 있음(넘김/자리비운동안.md 의 「걸린 것」)' if bad else '걸린 것 없음'))
    else:
        print('[마지막 일일 배치] 아직 돈 적 없음')
    run = jl('shop/.run.json', {}) or {}
    names = {'api': '가게 백엔드', 'web': '가게 프런트엔드', 'tunnel': '터널 프로그램'}
    items = [f'{names[k]}(PID {v}) ' + ('실행 중' if pid_alive(v) else '꺼져 있음') for k, v in run.items() if k in names and v]
    print('[가게 프로그램] ' + (' · '.join(items) if items else '켠 기록 없음'))
    ds = (jl('진도.json', {}) or {}).get('deploy_shop') or {}
    if ds.get('url'):
        print('[터널 주소] ' + ds['url'] + ' (이 PC 와 가게가 켜져 있는 동안만 열리고, 다시 열면 새 주소로 바뀝니다)')
    bk = sorted(glob.glob(os.path.join(HERE, '백업', '*.zip')))
    print('[마지막 백업] ' + (os.path.basename(bk[-1]) + f' (모두 {len(bk)}개)' if bk else '없음'))


def main():
    L = jl('site.local.json', {}) or {}; prog = jl('진도.json', {'done': []}) or {'done': []}
    print('━━ 내 서비스의 구조 (이 폴더에서 읽은 값) ━━')
    print(f'작업 폴더: {HERE}')
    posts = [f for f in glob.glob(os.path.join(HERE, 'posts', '*.md'))]; covers = glob.glob(os.path.join(HERE, 'posts', '_cover', '*.jpg'))
    print(f'\n[원본] 사람이 읽는 파일: 글 {len(posts)}편(posts/) · 사진 {len(covers)}장(posts/_cover/) · 이름과 색 등 설정(site.local.json: {", ".join(k for k in L if k in ("name", "tagline", "accent", "slug")) or "없음"})')
    pd = os.path.join(HERE, 'shop', 'api', 'data')
    if os.path.isdir(pd) and any(os.path.exists(os.path.join(pd, f)) for f in ('products.json', 'shop.db')):
        print(f'        가게: 상품 목록(shop/api/data/products.json) · 데이터베이스 파일(shop/api/data/shop.db, {os.path.getsize(os.path.join(pd, "shop.db")) // 1024 if os.path.exists(os.path.join(pd, "shop.db")) else 0}KB) · 화면 shop/web/')
    out = os.path.join(HERE, 'site_local')
    if os.path.isdir(out):
        n, t = size(out); idx = os.path.join(out, 'index.html')
        print(f'[결과물] 브라우저가 읽는 파일 묶음(site_local/): 파일 {n}개 {t // 1024}KB' + (f' · 마지막 빌드 {time.strftime("%m-%d %H:%M", time.localtime(os.path.getmtime(idx)))}' if os.path.exists(idx) else ''))
    snaps = sorted(int(x) for x in os.listdir(os.path.join(HERE, '.간직')) if x.isdigit()) if os.path.isdir(os.path.join(HERE, '.간직')) else []
    print(f'[스냅샷] 구현 전에 뜬 사본(.간직/) {len(snaps)}개' + (f', 가장 최근 {snaps[-1]}번' if snaps else ''))
    rows = [ln for ln in open(os.path.join(HERE, '기록', '흐름.md'), encoding='utf-8').read().splitlines() if ln.startswith('| ') and not ln.startswith('| 때')] if os.path.exists(os.path.join(HERE, '기록', '흐름.md')) else []
    print('[변경 이력] 기록/흐름.md 의 최근 줄:')
    for r in rows[-3:]:
        c = [x.strip() for x in r.strip('|').split('|')]
        print(f'   {c[0]} · 말: {c[1][:40]} · 확인: {c[4]} · {c[5]}')
    if not rows:
        print('   아직 없음')
    dep = prog.get('deploy') or {}; ds = prog.get('deploy_shop') or {}
    print('[올라간 곳]' + (f' 글 사이트 {dep["url"]} ({"임시 배포, 60분" if dep.get("temp") else "고정 주소"}, {dep.get("t", "")})' if dep.get('url') else ' 글 사이트: 아직 배포 전') + (f' · 가게 터널 주소 {ds["url"]}' if ds.get('url') else ''))
    prev = [p for p in range(8000, 8010) if up(p)]
    print('[돌고 있는 프로그램] ' + ', '.join(filter(None, [f'글 사이트 미리 보기 127.0.0.1:{p}' for p in prev] + (['가게 프런트엔드 3000'] if up(3000) else []) + (['가게 백엔드 8787'] if up(8787) else []))) if (prev or up(3000) or up(8787)) else '[돌고 있는 프로그램] 지금 이 폴더의 서버는 꺼져 있음')
    db = os.path.join(pd, 'shop.db')
    if os.path.exists(db):
        try:
            c = sqlite3.connect(db); o = c.execute('select count(*) from orders').fetchone()[0]; p = c.execute('select count(*) from products').fetchone()[0]; c.close()
            on = (jl('shop/api/modules.json', {}) or {}).get('on', [])
            print(f'[가게] 상품 {p}개 · 주문 {o}건 · 켜진 기능 모듈 {len(on)}개({", ".join(on)})')
        except Exception:
            pass
    av = jl('android_app/version.json')
    if av:
        print(f'[앱] {av.get("package")} · 버전 {av.get("name")}({av.get("code")}) · {av.get("bytes", 0) // 1024}KB · 서명 키는 android_app/ 에 있고 읽지 않음')
    print(f'[백업] 운영 자료 묶음(백업/) {len(glob.glob(os.path.join(HERE, "백업", "*.zip")))}개')
    if '--운영' in sys.argv or '운영' in sys.argv[1:]:
        running()
    return 0


if __name__ == '__main__':
    sys.exit(main())
