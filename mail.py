# -*- coding: utf-8 -*-
"""소식지 메일 보내기(SMTP): 오늘의 확인 노트 요약을 메일 한 통으로 만든다. 파이썬 기본 기능(smtplib)만 쓴다.
SMTP 가 뭔가요? 메일을 보내는 길(약속)입니다. 메일 서비스(네이버·구글 등)의 설정에서 「SMTP 사용」을 켜고 서버 주소·포트·(앱) 비밀번호를 받아 아래 설정 파일에 넣습니다 — 이 단계는 사람 몫입니다.
설정(내 컴퓨터에만 둠, git 에 안 올라감): mail.local.json
  {"host": "smtp.예시.com", "port": 587, "security": "starttls", "user": "내아이디", "password": "앱 비밀번호", "from": "내주소@예시.com", "to": ["받는주소@예시.com"]}
  (환경변수 MAIL_HOST·MAIL_PORT·MAIL_SECURITY·MAIL_USER·MAIL_PASSWORD·MAIL_FROM·MAIL_TO 로도 줄 수 있음. security 는 starttls(587) 또는 ssl(465))
사용: python mail.py                  미리보기만(보내지 않음)
      python mail.py --send           실제로 보내기 — 받는 주소를 확인한 뒤에만
      python mail.py --send --to 내주소@예시.com   받는 사람을 바꿔 시험 발송(본인 주소로 먼저 한 통)
      python mail.py 주문알림          가게에 새로 들어온 주문을 운영자 자신에게 알리는 메일 미리보기(받는 사람은 늘 설정의 from — 나 자신뿐)
      python mail.py 주문알림 --send   한 번 보내기 · --auto 는 설정에 "order_notify": true 를 독자가 직접 적어 둔 경우에만 보낸다(하루 한 바퀴가 이것을 부른다)
규칙: 사람이 「보내」 한 뒤에만 --send. 받는 사람 목록은 내가 허락받은 사람만. 비밀번호를 파일·기록에 남기지 않는다."""
import json, os, smtplib, sys, glob, datetime
from email.message import EmailMessage
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))


def config():
    c = {}
    p = os.path.join(HERE, 'mail.local.json')
    if os.path.exists(p):
        c.update(json.load(open(p, encoding='utf-8')))
    for k, env in (('host', 'MAIL_HOST'), ('port', 'MAIL_PORT'), ('security', 'MAIL_SECURITY'), ('user', 'MAIL_USER'), ('password', 'MAIL_PASSWORD'), ('from', 'MAIL_FROM')):
        if os.environ.get(env):
            c[k] = os.environ[env]
    if os.environ.get('MAIL_TO'):
        c['to'] = [x.strip() for x in os.environ['MAIL_TO'].split(',') if x.strip()]
    return c


def site():
    S = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
    lp = os.path.join(HERE, 'site.local.json')
    if os.path.exists(lp):
        S.update(json.load(open(lp, encoding='utf-8')))
    if os.environ.get('SITE_NAME'):
        S['name'] = os.environ['SITE_NAME']
    if os.environ.get('SITE_URL'):
        S['url'] = os.environ['SITE_URL']
    return S


def compose(date=None):
    """가장 최근 날짜(또는 지정 날짜)의 확인 노트로 제목·본문을 만든다."""
    S = site()
    url = S.get('url', '').rstrip('/')
    real = url and '프로젝트이름' not in url and '내계정' not in url
    notes = [json.load(open(p, encoding='utf-8')) for p in sorted(glob.glob(os.path.join(HERE, 'notes', '*.json')))]
    notes = [n for n in notes if not n.get('example')]
    if not notes:
        sys.exit('보낼 확인 노트가 없습니다.')
    date = date or max(n['date'] for n in notes)
    ns = [n for n in notes if n['date'] == date]
    lines = [f'{S["name"]} — {date} 확인 노트 {len(ns)}건', '']
    for n in ns:
        lines += [f'■ {n["title"]}  [{n["verdict"]}]', f'  {n["question"]}', f'  {n["summary"]}']
        lines.append('  전문: ' + (f'{url}/n/{n["id"]}/' if real else '(공개 주소가 정해지면 링크가 들어갑니다)'))
        lines.append('')
    lines += ['공식 자료로 한 번 더 확인합니다.', '이 메일은 수신을 허락한 분께만 보냅니다. 더 받고 싶지 않으면 이 메일에 「중단」이라고 답해 주세요.']
    return f'[{S["name"]}] {date} 확인 노트 {len(ns)}건', '\n'.join(lines)


def deliver(c, subj, body, to):
    msg = EmailMessage()
    msg['Subject'] = subj; msg['From'] = c['from']; msg['To'] = ', '.join(to); msg['Date'] = datetime.datetime.now().astimezone().strftime('%a, %d %b %Y %H:%M:%S %z')
    msg.set_content(body)
    port = int(c['port']); sec = c.get('security', 'starttls')
    if sec == 'ssl':
        s = smtplib.SMTP_SSL(c['host'], port, timeout=30)
    else:
        s = smtplib.SMTP(c['host'], port, timeout=30)
        if sec != 'none':   # none 은 내 컴퓨터 안의 시험용 받는 곳에만 쓴다
            s.starttls()
    try:
        if sec != 'none':
            s.login(c['user'], c['password'])
        s.send_message(msg)
    finally:
        s.quit()


def order_notify():
    """가게에 새로 들어온 주문을 운영자 자신에게만 알린다. 손님의 연락처·주소는 메일에 싣지 않는다(운영자 화면에서 본다)."""
    import sqlite3
    auto = '--auto' in sys.argv; send = '--send' in sys.argv or auto
    db = os.path.join(HERE, 'shop', 'api', 'data', 'shop.db'); st = os.path.join(HERE, '넘김', '.주문알림.json')
    if not os.path.exists(db):
        print('건너뜀: 가게를 아직 켠 적이 없습니다.'); return 0
    c = config()
    if auto and c.get('order_notify') is not True:
        print('건너뜀: 주문 알림 메일이 꺼져 있습니다(켜려면 mail.local.json 에 "order_notify": true 를 직접 적습니다).'); return 0
    last = json.load(open(st, encoding='utf-8')).get('last', 0) if os.path.exists(st) else 0
    q = sqlite3.connect(db); rows = q.execute("select id, name, items, total, status, created from orders where id > ? and status != '취소' order by id", (last,)).fetchall(); q.close()
    if not rows:
        print('새로 들어온 주문이 없습니다. 메일을 보내지 않았습니다.'); return 0
    try:
        shop = json.load(open(os.path.join(HERE, 'shop', 'web', 'site.json'), encoding='utf-8')).get('name') or '내 가게'
    except Exception:
        shop = '내 가게'
    lines = [f'{shop} — 새 주문 {len(rows)}건', '']
    for oid, name, items, total, status, created in rows:
        its = ', '.join(f'{i["name"]} {i["qty"]}개' for i in json.loads(items))
        lines += [f'■ 주문 {oid}번 · {created} · {status}', f'  {its}', f'  {total:,}원 · 받는 분 {name[:1]}○○', '']
    lines += ['받는 분의 연락처와 주소는 이 메일에 싣지 않았습니다. 이 PC 에서 운영자 화면(http://127.0.0.1:3000/admin)을 열어 확인하고, 입금이 들어왔으면 「입금 확인」을 눌러 주세요.']
    subj = f'[{shop}] 새 주문 {len(rows)}건'; body = '\n'.join(lines); to = [c['from']] if c.get('from') else []
    print('제목:', subj); print('받는 사람(나 자신):', ', '.join(to) or '(설정에 from 이 없습니다)'); print('-' * 40); print(body)
    if not send:
        print('-' * 40); print('미리보기입니다. 보내지 않았습니다.'); return 0
    need = ('host', 'port', 'from') if c.get('security') == 'none' else ('host', 'port', 'user', 'password', 'from')
    missing = [k for k in need if not c.get(k)]
    if missing:
        print('설정이 모자랍니다: ' + ', '.join(missing) + ' (mail.local.json 에 직접 넣으세요)'); return 1
    deliver(c, subj, body, to)
    os.makedirs(os.path.dirname(st), exist_ok=True); json.dump({'last': rows[-1][0], 't': datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}, open(st, 'w', encoding='utf-8'))
    print(f'보냈습니다: 나 자신에게 새 주문 {len(rows)}건(주문 {rows[0][0]}~{rows[-1][0]}번). 같은 주문은 다시 알리지 않습니다.'); return 0


def main():
    if '주문알림' in sys.argv:
        sys.exit(order_notify())
    send = '--send' in sys.argv
    to_override = sys.argv[sys.argv.index('--to') + 1].split(',') if '--to' in sys.argv else None
    subj, body = compose()
    c = config()
    to = to_override or c.get('to', [])
    print('제목:', subj); print('받는 사람:', ', '.join(to) or '(없음)'); print('-' * 40); print(body)
    if not send:
        print('-' * 40); print('미리보기입니다. 보내지 않았습니다. 실제로 보내려면 받는 주소를 확인한 뒤 --send 를 붙이세요.'); return
    missing = [k for k in ('host', 'port', 'user', 'password', 'from') if not c.get(k)]
    if missing or not to:
        sys.exit('설정이 모자랍니다: ' + ', '.join(missing + ([] if to else ['to'])) + ' (mail.local.json 에 넣으세요)')
    deliver(c, subj, body, to)
    print('보냈습니다:', ', '.join(to))


if __name__ == '__main__':
    main()
