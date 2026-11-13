# -*- coding: utf-8 -*-
"""내 서비스의 구조: 독자의 지금 폴더에서 원본·결과물·올라간 곳·돌고 있는 프로그램·최근 한 일을 한 번에 모아 보여 준다. 읽기만 한다. 파이썬 기본 기능만 쓴다.
python run.py 구조
세션은 이 값을 흐름 순서(원본 → 스냅샷 → 빌드 → 결과물 → 배포 → 손님)로 풀어 설명한다(참고/흐름_풀이.md)."""
import glob, json, os, socket, sqlite3, sys, time
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
    return 0


if __name__ == '__main__':
    sys.exit(main())
