# -*- coding: utf-8 -*-
"""db 개념 실험실: 어느 db 를 쓰든 통하는 개념(트랜잭션·롤백·색인·제약·백업)을 눈앞에서 일으켜 본다. 파이썬 기본 기능(sqlite3)만 쓰고, 임시 폴더에서만 돌며 끝나면 지운다.
사용: python run.py 실험 좋아요|롤백|색인|제약|백업   (이 파일을 직접 부르지 않는다)"""
import json, os, random, sqlite3, tempfile, threading, time, shutil


def _db(path):
    c = sqlite3.connect(path, timeout=30, isolation_level=None)   # isolation_level=None: 직접 BEGIN/COMMIT 한다(묶지 않으면 한 줄마다 바로 저장)
    return c


def likes(n=100):
    """동시에 좋아요를 n 번: 읽고(read) 고쳐 쓰는(write) 사이에 다른 사람이 끼어들면 수가 모자란다."""
    d = tempfile.mkdtemp(prefix='lab_'); p = os.path.join(d, 'lab.db')
    c = _db(p); c.execute('CREATE TABLE docs(id TEXT PRIMARY KEY, n INTEGER)'); c.execute("INSERT INTO docs VALUES('post',0)"); c.close()

    def naive():
        c = _db(p)
        try:
            v = c.execute("SELECT n FROM docs WHERE id='post'").fetchone()[0]   # ① 읽고
            time.sleep(random.random() * 0.004)                                    # ② 잠깐 딴 일(다른 사람이 끼어들 틈)
            c.execute("UPDATE docs SET n=? WHERE id='post'", (v + 1,))            # ③ 읽은 값 + 1 을 씀
        finally:
            c.close()

    def safe():
        c = _db(p)
        try:
            for _ in range(200):
                try:
                    c.execute('BEGIN IMMEDIATE')   # 트랜잭션 시작: 끝날 때까지 다른 쓰기는 기다린다
                    v = c.execute("SELECT n FROM docs WHERE id='post'").fetchone()[0]
                    time.sleep(random.random() * 0.004)
                    c.execute("UPDATE docs SET n=? WHERE id='post'", (v + 1,))
                    c.execute('COMMIT'); return
                except sqlite3.OperationalError:
                    try:
                        c.execute('ROLLBACK')
                    except Exception:
                        pass
                    time.sleep(0.002)
        finally:
            c.close()

    def run(fn):
        c = _db(p); c.execute("UPDATE docs SET n=0 WHERE id='post'"); c.close()
        ts = [threading.Thread(target=fn) for _ in range(n)]
        [t.start() for t in ts]; [t.join() for t in ts]
        c = _db(p); v = c.execute("SELECT n FROM docs WHERE id='post'").fetchone()[0]; c.close(); return v
    a = run(naive); b = run(safe); shutil.rmtree(d, ignore_errors=True)
    return {'title': '실험 · 좋아요 동시에 100번(트랜잭션)',
            'say': f'엑셀에서 두 사람이 같은 칸을 동시에 고치면 한 사람의 수정이 사라집니다. 좋아요 {n}번을 동시에 눌러 같은 일을 일으켜 봅니다.',
            'show': [f'묶지 않은 방식(읽고 → 쓰기):   최종 좋아요 = {a}   (기대 {n}, 사라진 것 {n - a}개)', f'트랜잭션으로 묶은 방식:        최종 좋아요 = {b}   (기대 {n})'],
            'ask': '묶지 않았다면 좋아요 수는 왜 모자랐을까요?', 'hint': '읽은 값이 쓰는 순간에는 이미 낡은 값이라서 — 두 사람이 같은 값 7을 읽고 둘 다 8 을 쓰면 하나가 사라집니다. 트랜잭션은 읽고 쓰는 묶음이 끝날 때까지 다른 쓰기를 기다리게 합니다.',
            'ok': a < n and b == n}


def rollback():
    d = tempfile.mkdtemp(prefix='lab_'); p = os.path.join(d, 'lab.db'); c = _db(p)
    c.execute('CREATE TABLE docs(id TEXT PRIMARY KEY, data TEXT NOT NULL)')
    batch = [('c1', '댓글 A'), ('c2', '댓글 B'), ('c3', None), ('c4', '댓글 D')]   # 세 번째 줄은 일부러 오류(빈 값)

    def put_all(use_tx):
        c.execute('DELETE FROM docs')
        if use_tx:
            c.execute('BEGIN')
        try:
            for i, v in batch:
                c.execute('INSERT INTO docs VALUES(?,?)', (i, v))
            if use_tx:
                c.execute('COMMIT')
        except sqlite3.Error as e:
            if use_tx:
                c.execute('ROLLBACK')
            return type(e).__name__
        return None
    e1 = put_all(False); n1 = c.execute('SELECT COUNT(*) FROM docs').fetchone()[0]
    e2 = put_all(True); n2 = c.execute('SELECT COUNT(*) FROM docs').fetchone()[0]
    c.close(); shutil.rmtree(d, ignore_errors=True)
    return {'title': '실험 · 되돌리기(롤백)', 'say': '댓글 4건을 한꺼번에 저장하는데 세 번째에서 일부러 오류를 냅니다. 반쯤 들어간 채로 남는지 봅니다.',
            'show': [f'묶지 않았을 때: 오류({e1}) 뒤에 남은 문서 = {n1}건 (앞의 2건만 들어간 반쯤 저장된 상태)', f'트랜잭션으로 묶었을 때: 오류({e2}) → ROLLBACK 뒤에 남은 문서 = {n2}건 (아무것도 안 들어간 처음 상태)'],
            'ask': '반쯤 저장된 상태가 왜 위험할까요?', 'hint': '합계가 안 맞거나 다음 저장이 중복 오류를 냅니다. 트랜잭션은 「전부 되거나 전부 안 되거나」를 보장합니다.', 'ok': n1 == 2 and n2 == 0}


def index(rows=200000):
    d = tempfile.mkdtemp(prefix='lab_'); p = os.path.join(d, 'lab.db'); c = _db(p)
    c.execute('CREATE TABLE visits(day TEXT, path TEXT, n INTEGER)')
    c.execute('BEGIN'); days = [time.strftime('%Y-%m-%d', time.localtime(time.time() - i * 86400)) for i in range(400)]
    c.executemany('INSERT INTO visits VALUES(?,?,1)', ((random.choice(days), f'/n/{random.randint(1, 300)}/') for _ in range(rows))); c.execute('COMMIT')
    today = days[0]

    def timed():
        t = time.perf_counter()
        for _ in range(20):
            v = c.execute('SELECT COUNT(*) FROM visits WHERE day=?', (today,)).fetchone()[0]
        return (time.perf_counter() - t) / 20 * 1000, v
    t1, v = timed(); c.execute('CREATE INDEX ix_day ON visits(day)'); t2, v2 = timed()
    c.close(); shutil.rmtree(d, ignore_errors=True)
    return {'title': f'실험 · 색인({rows:,}건 가운데 오늘 것만 세기)', 'say': f'방문 기록 {rows:,}건을 실험용으로 채우고 「오늘 방문 수」를 셉니다. 책의 색인(찾아보기)처럼 db 에도 색인이 있습니다.',
            'show': [f'색인 없이: {t1:.1f} ms   (결과 {v}건, 처음부터 끝까지 훑음)', f'색인 만든 뒤: {t2:.2f} ms   (결과 {v2}건, 색인으로 바로 찾음)', f'→ 약 {t1 / max(t2, 0.001):.0f}배 빨라졌습니다'],
            'ask': '색인을 모든 칸에 만들면 안 될까요?', 'hint': '색인은 읽기를 빠르게 하는 대신 저장할 때마다 색인도 고쳐야 해서 쓰기가 느려지고 공간을 씁니다. 자주 찾는 칸에만 만듭니다.', 'ok': t2 < t1}


def constraint():
    d = tempfile.mkdtemp(prefix='lab_'); p = os.path.join(d, 'lab.db'); c = _db(p)
    c.execute("CREATE TABLE subscribers(email TEXT PRIMARY KEY CHECK(length(email)>3 AND instr(email,'@')>1), status TEXT NOT NULL DEFAULT 'on')")
    res = []
    for em in ('reader@example.com', 'reader@example.com', '', 'not-an-email'):
        try:
            c.execute('INSERT INTO subscribers(email) VALUES(?)', (em,)); res.append(f'「{em}」 → 저장됨')
        except sqlite3.IntegrityError as e:
            res.append(f'「{em}」 → 거절({"같은 주소가 이미 있음(중복 금지)" if "UNIQUE" in str(e) else "형식·빈 값 검사 실패"})')
    n = c.execute('SELECT COUNT(*) FROM subscribers').fetchone()[0]; c.close(); shutil.rmtree(d, ignore_errors=True)
    return {'title': '실험 · 제약(중복 금지·빈 값 거절)', 'say': '같은 메일 주소로 두 번 신청하고, 빈 값과 이상한 값도 넣어 봅니다. db 가 스스로 막아 주는 규칙이 제약입니다.',
            'show': res + [f'최종 남은 신청 = {n}건'], 'ask': '프로그램에서 검사하면 되는데 db 에도 제약을 두는 까닭은?', 'hint': '프로그램이 여러 개이거나 실수가 있어도 db 가 마지막 방어선이 되어 잘못된 자료가 쌓이지 않습니다.', 'ok': n == 1}


def backup():
    d = tempfile.mkdtemp(prefix='lab_'); p = os.path.join(d, 'lab.db'); c = _db(p)
    c.execute('CREATE TABLE docs(collection TEXT, id TEXT, data TEXT, PRIMARY KEY(collection,id))')
    for i in range(5):
        c.execute('INSERT INTO docs VALUES(?,?,?)', ('comments', f'c{i}', json.dumps({'name': f'독자{i}', 'body': f'댓글 {i}'}, ensure_ascii=False)))
    before = c.execute('SELECT COUNT(*) FROM docs').fetchone()[0]
    dump = [{'collection': a, 'id': b, 'data': json.loads(x)} for a, b, x in c.execute('SELECT * FROM docs')]   # 내보내기: JSON 파일 한 개
    bf = os.path.join(d, 'backup.json'); open(bf, 'w', encoding='utf-8').write(json.dumps(dump, ensure_ascii=False, indent=1))
    c.execute('DELETE FROM docs'); gone = c.execute('SELECT COUNT(*) FROM docs').fetchone()[0]          # 지우기(사고)
    for r in json.load(open(bf, encoding='utf-8')):                                                       # 되살리기
        c.execute('INSERT INTO docs VALUES(?,?,?)', (r['collection'], r['id'], json.dumps(r['data'], ensure_ascii=False)))
    after = c.execute('SELECT COUNT(*) FROM docs').fetchone()[0]; size = os.path.getsize(bf); c.close(); shutil.rmtree(d, ignore_errors=True)
    return {'title': '실험 · 백업과 복구', 'say': '문서 5건을 JSON 파일 하나로 내보내고, db 를 비운 뒤(사고), 그 파일로 되살립니다.',
            'show': [f'내보내기: backup.json {size}바이트 (문서 {before}건)', f'사고(전부 지움) 뒤: {gone}건', f'복구 뒤: {after}건 → 처음과 같음'], 'ask': '백업 파일을 db 와 같은 PC 에만 두면 어떤 위험이 있을까요?', 'hint': 'PC 가 고장 나거나 도둑맞으면 db 와 백업이 함께 사라집니다. 다른 곳(외장 디스크·클라우드)에도 사본을 둡니다. 클라우드 db 로 옮길 때도 이 파일이 그대로 쓰입니다.', 'ok': before == after == 5 and gone == 0}


EXPS = {'좋아요': likes, '롤백': rollback, '색인': index, '제약': constraint, '백업': backup}
