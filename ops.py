# -*- coding: utf-8 -*-
"""운영자의 하루 일(ops): 방문자가 남긴 것을 받는 사이트(게시판·장터·순위)에서 오늘 사람이 볼 것만 뽑아 준다. 파이썬 기본 기능만 쓴다.
서버가 쌓아 둔 문서를 읽기만 한다: 도커로 켠 서버(python run.py 서버)가 떠 있으면 거기서 꺼내고, 아니면 파일 저장소(--data 폴더의 app.db)에서. 승인·숨김은 하지 않는다(그것은 운영자 화면 /admin/ 에서 사람이).
쓰는 법: python ops.py [--data 폴더]   ·   python run.py 운영"""
import json, os, sqlite3, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


def settings():
    S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
    loc = os.path.join(HERE, 'site.local.json')
    if os.path.exists(loc):
        S.update(json.load(open(loc, encoding='utf-8')))
    return S


def _hours(created):
    try:
        return max(0.0, (time.time() - time.mktime(time.strptime(str(created)[:19].replace('T', ' '), '%Y-%m-%d %H:%M:%S'))) / 3600)
    except Exception:
        return 0.0


def docker_up():
    """도커로 켠 서버(app)가 떠 있나. 도커가 없거나 꺼져 있으면 False."""
    try:
        r = subprocess.run(['docker', 'compose', 'ps', '--status', 'running', '-q', 'app'], cwd=HERE, capture_output=True, text=True, timeout=15)
        return r.returncode == 0 and bool(r.stdout.strip())
    except Exception:
        return False


def rows(db, col):
    """그 모음의 문서들(없으면 빈 목록). 지난 시간(시간 단위)을 _h 로 붙인다. db 가 'docker' 면 떠 있는 서버에서 꺼내 읽는다(python run.py 자료 와 같은 길)."""
    out = []
    if db == 'docker':
        try:
            r = subprocess.run(['docker', 'compose', 'exec', '-T', 'app', 'python', '/app/app.py', '--dump', col], cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
            out = json.loads(r.stdout) if r.returncode == 0 else []
        except Exception:
            out = []
        for d in out:
            d['_h'] = _hours(d.get('_created', ''))
        return out
    try:
        for i, data, created in db.execute('SELECT id, data, created FROM docs WHERE collection=?', (col,)):
            d = json.loads(data); d['_id'] = i
            d['_h'] = _hours(created)
            out.append(d)
    except sqlite3.Error:
        pass
    return out


def lines(S, db):
    P = S.get('parts') or {}; out = []; todo = 0
    if P.get('board'):
        posts = rows(db, 'posts'); cm = rows(db, 'pcomments'); pend = [p for p in posts if p.get('status') == 'pending']; pc = [c for c in cm if c.get('status') == 'pending']; fl = rows(db, 'flags')
        todo += len(pend) + len(pc) + len(fl)
        out.append(f'[게시판] 승인 기다리는 글 {len(pend)}건 · 댓글 {len(pc)}건 · 신고 {len(fl)}건 / 지난 하루 새 글 {sum(1 for p in posts if p["_h"] < 24)}건 · 새 댓글 {sum(1 for c in cm if c["_h"] < 24)}건 (보이는 글 모두 {sum(1 for p in posts if p.get("status") == "approved")}건)')
        out += [f'   - 승인할 글: {p.get("title", "")[:50]} ({p.get("name", "")})' for p in pend[:5]]
    if P.get('market'):
        ct = [c for c in rows(db, 'contacts') if c.get('status') == 'new']; od = [c for c in ct if '주문' in (c.get('message', '') + c.get('subject', ''))]
        todo += len(ct)
        out.append(f'[장터] 새 문의 {len(ct)}건 (그 가운데 주문 문의로 보이는 것 {len(od)}건) / 지난 하루 {sum(1 for c in ct if c["_h"] < 24)}건')
        out += [f'   - {c.get("name", "")} · {c.get("message", "")[:60]}' for c in ct[:5]]
    if P.get('trend'):
        its = rows(db, 'trend_items'); pend = [p for p in its if p.get('status') == 'pending']; st = [s for s in rows(db, 'trend_stars') if s.get('on') is not False]
        todo += len(pend); day = {}
        for s in st:
            if s['_h'] < 24:
                day[s.get('iid')] = day.get(s.get('iid'), 0) + 1
        top = sorted(day.items(), key=lambda x: -x[1])[:3]
        out.append(f'[순위] 승인 기다리는 항목 {len(pend)}건 / 지난 하루 받은 별 {sum(day.values())}개 · 지금까지 {len(st)}개' + (' / 오늘 별을 많이 받은 것: ' + ', '.join(f'{k}({v})' for k, v in top) if top else ''))
        out += [f'   - 승인할 항목: {p.get("name", "")} — {p.get("desc", "")[:40]} ({p.get("owner", "")})' for p in pend[:5]]
    if P.get('comments') or P.get('backend'):
        pc = [c for c in rows(db, 'comments') if c.get('status') == 'pending']
        if pc:
            todo += len(pc); out.append(f'[댓글] 승인 기다리는 댓글 {len(pc)}건')
    return out, todo


def main():
    S = settings(); P = S.get('parts') or {}
    data = sys.argv[sys.argv.index('--data') + 1] if '--data' in sys.argv else os.path.join(HERE, 'data', 'app')
    if not any(P.get(k) for k in ('board', 'market', 'trend')):
        print('운영자의 하루 일: 이 사이트는 방문자가 남기는 것을 받는 틀(게시판·장터·순위)이 꺼져 있어 볼 것이 없습니다.'); return 0
    dbp = os.path.join(data, 'app.db'); src = ''
    if '--data' not in sys.argv and docker_up():
        out, todo = lines(S, 'docker'); src = '도커로 켠 서버'
    elif os.path.exists(dbp):
        db = sqlite3.connect(f'file:{dbp}?mode=ro', uri=True, timeout=5)
        out, todo = lines(S, db); db.close(); src = '파일 저장소'
    else:
        print('운영자의 하루 일: 서버가 꺼져 있어 읽을 것이 없습니다. python run.py 서버 로 켜 두면 방문자가 남긴 것이 쌓이고, 켜져 있는 동안 이 명령이 그것을 읽습니다.'); return 0
    print(f'운영자의 하루 일 — {time.strftime("%Y-%m-%d %H:%M")} (읽기만 함 · {src})')
    print('\n'.join(out))
    print(f'→ 오늘 사람이 정할 것 {todo}건' + (' — 승인·숨김은 운영자 화면 /admin/ 에서(python run.py 서버 뒤 로그인).' if todo else ' — 없습니다.'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
