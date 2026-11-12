# -*- coding: utf-8 -*-
"""데이터 관리(운영): 내 사이트에 쌓인 것을 한눈에 보고, 통째로 백업하고, 복구하고, 주문을 표로 뽑는다. 파이썬 기본 기능만 쓴다.
python run.py 데이터 현황            글·상품·주문·상품평·올린 주소·마지막 백업을 한 장으로
python run.py 데이터 백업            백업/<날짜_시각>.zip 한 파일로(설정·글·사진·가게 자료·넘김·기록) — 최근 14개만 남긴다
python run.py 데이터 목록            백업해 둔 파일들
python run.py 데이터 복구 [파일] --예  그 백업(없으면 가장 최근)으로 되돌린다. 되돌리기 직전 상태도 먼저 백업해 둔다
python run.py 데이터 주문표          가게 주문을 넘김/주문표.csv 로(엑셀로 열림) — 입금 대기·입금 확인·보냄
운영에서 이 일은 「데이터」 담당 세션(또는 서브에이전트)이 맡는다: 아침마다 현황 → 백업, 주문이 있으면 주문표."""
import csv, json, os, sqlite3, sys, time, zipfile
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
BK = os.path.join(HERE, '백업'); DB = os.path.join(HERE, 'shop', 'api', 'data', 'shop.db')
A = sys.argv[1:]
WHAT = ['site.local.json', '내_서비스.md', '진도.json', 'posts', 'notes', '넘김', '기록', 'shop/api/data', 'shop/api/modules.json', 'shop/web/site.json', 'shop/web/public/p', 'shop/web/public/hero.jpg']


def q(sql, default=0):
    if not os.path.exists(DB):
        return default
    try:
        c = sqlite3.connect(DB); r = c.execute(sql).fetchall(); c.close(); return r
    except Exception:
        return default


def backups():
    return sorted(f for f in os.listdir(BK) if f.endswith('.zip')) if os.path.isdir(BK) else []


def status():
    n_posts = len([f for f in os.listdir(os.path.join(HERE, 'posts')) if f.endswith('.md')]) if os.path.isdir(os.path.join(HERE, 'posts')) else 0
    n_notes = len([f for f in os.listdir(os.path.join(HERE, 'notes')) if f.endswith('.json') and f[:1].isdigit()]) if os.path.isdir(os.path.join(HERE, 'notes')) else 0
    prog = json.load(open(os.path.join(HERE, '진도.json'), encoding='utf-8')) if os.path.exists(os.path.join(HERE, '진도.json')) else {}
    dep = prog.get('deploy') or {}
    print('┌─ 데이터 현황 ' + '─' * 40)
    print(f'│ 글 {n_posts}편 · 확인 노트 {n_notes}건')
    if os.path.exists(DB):
        one = lambda s: (q(s) or [[0]])[0][0]
        by = dict(q('select status, count(*) from orders group by status') or [])
        print(f'│ 가게: 상품 {one("select count(*) from products")}개 · 상품평 {one("select count(*) from reviews")}개 · 주문 {sum(by.values())}건' + (' (' + ' · '.join(f'{k} {v}' for k, v in by.items()) + ')' if by else ''))
        wait = by.get('입금 대기', 0)
        if wait:
            print(f'│ ▶ 사람이 볼 것: 입금 대기 {wait}건 — 입금을 확인하고 운영자 화면(/admin)에서 「입금 확인」으로')
    else:
        print('│ 가게: 아직 켠 적이 없습니다')
    print('│ 올린 주소: ' + (dep.get('url', '') + (' (임시)' if dep.get('temp') else '') if dep else '아직'))
    B = backups()
    print('│ 마지막 백업: ' + (B[-1] + f' · 모두 {len(B)}개' if B else '없음 — python run.py 데이터 백업'))
    print('└' + '─' * 52)
    return 0


def backup(tag=''):
    os.makedirs(BK, exist_ok=True); name = time.strftime('%Y-%m-%d_%H%M%S') + (('_' + tag) if tag else '') + '.zip'; fp = os.path.join(BK, name); n = 0
    with zipfile.ZipFile(fp, 'w', zipfile.ZIP_DEFLATED) as z:
        for w in WHAT:
            p = os.path.join(HERE, w)
            if os.path.isfile(p):
                z.write(p, w); n += 1
            elif os.path.isdir(p):
                for root, _, fs in os.walk(p):
                    for f in fs:
                        full = os.path.join(root, f); z.write(full, os.path.relpath(full, HERE).replace(os.sep, '/')); n += 1
    for old in backups()[:-14]:
        os.remove(os.path.join(BK, old))
    print(f'백업했습니다: 백업/{name}  (파일 {n}개, {os.path.getsize(fp) // 1024}KB) — 최근 14개만 남깁니다')
    return fp


def restore():
    B = backups(); rest = [a for a in A[1:] if not a.startswith('--')]
    if not B:
        print('백업해 둔 것이 없습니다.'); return 1
    name = rest[0] if rest else B[-1]
    name = os.path.basename(name)
    if name not in B:
        print('그런 백업이 없습니다. python run.py 데이터 목록'); return 1
    if '--예' not in A:
        print(f'복구하면 지금의 글·설정·가게 자료가 백업/{name} 때의 것으로 바뀝니다(지금 상태는 먼저 백업해 둡니다).\n독자가 「복구해 줘」 하면 --예 를 붙여 다시 부릅니다: python run.py 데이터 복구 {name} --예'); return 0
    backup('복구직전')
    with zipfile.ZipFile(os.path.join(BK, name)) as z:
        for m in z.namelist():
            dst = os.path.normpath(os.path.join(HERE, m))
            if not dst.startswith(HERE + os.sep):
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True); open(dst, 'wb').write(z.read(m))
    print(f'복구했습니다: 백업/{name}. 복구 직전 상태도 백업/ 에 남겨 두었습니다. 올려 둔 사이트에 반영하려면 python run.py 올려.')
    return 0


def orders_csv():
    R = q('select id, created, status, name, phone, address, memo, total, discount, items from orders order by id desc', [])
    if not R:
        print('주문이 없습니다.'); return 0
    out = os.path.join(HERE, '넘김', '주문표.csv'); os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f); w.writerow(['주문 번호', '때', '상태', '받는 분', '연락처', '주소', '남긴 말', '값', '할인', '상품'])
        for r in R:
            items = ' / '.join(f'{i["name"]} {i["qty"]}개' for i in json.loads(r[9]))
            w.writerow(list(r[:9]) + [items])
    print(f'주문 {len(R)}건을 표로 뽑았습니다: 넘김/주문표.csv (받는 분의 연락처·주소가 들어 있으니 바깥에 올리지 않습니다)')
    return 0


def main():
    c = A[0] if A else '현황'
    if c == '현황':
        return status()
    if c == '백업':
        backup(); return 0
    if c == '목록':
        B = backups(); print('\n'.join(f'  {b}  {os.path.getsize(os.path.join(BK, b)) // 1024}KB' for b in B) or '백업해 둔 것이 없습니다.'); return 0
    if c == '복구':
        return restore()
    if c == '주문표':
        return orders_csv()
    print(__doc__); return 1


if __name__ == '__main__':
    sys.exit(main())
