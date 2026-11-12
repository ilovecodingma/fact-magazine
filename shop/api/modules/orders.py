# -*- coding: utf-8 -*-
"""주문. 무통장 입금 방식 — 주문하면 「입금 대기」가 되고 입금할 계좌를 알려 준다. 운영자가 입금을 확인하면 「입금 확인」, 보내면 「보냄」.
입금 계좌는 운영자가 운영자 화면(/admin)에서 직접 넣는다 — data/bank.local.json 에만 남고(git 에 올라가지 않는다) 세션은 이 파일을 읽지 않는다. 카드 결제는 없다."""
import json, os

BANK = os.path.join(os.path.dirname(os.environ.get('SHOP_DB') or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'shop.db')), 'bank.local.json')


def bank():
    try:
        return json.load(open(BANK, encoding='utf-8'))
    except Exception:
        return {'bank': '', 'account': '', 'holder': ''}


def init(c):
    c.execute("create table if not exists orders(id integer primary key, device text, name text, phone text, address text, memo text, items text, total integer, discount integer default 0, coupon text, status text default '입금 대기', created text default (datetime('now','localtime')))")


def place(c, req):
    d = req['device']; b = req['body']
    for k, label in (('name', '받는 분을'), ('phone', '연락처를'), ('address', '주소를')):
        if not str(b.get(k, '')).strip():
            raise ValueError(label + ' 적어 주세요')
    items = [dict(r) for r in c.execute('select p.id, p.name, p.price, k.qty, p.stock from cart k join products p on p.id=k.pid where k.device=?', (d,))]
    if not items:
        raise ValueError('장바구니가 비어 있습니다')
    out = [i['name'] for i in items if (i.pop('stock') or 0) <= 0]
    if out:
        raise ValueError('품절된 상품이 담겨 있습니다: ' + ', '.join(out) + ' — 장바구니에서 빼고 다시 주문해 주세요')
    total = sum(i['price'] * i['qty'] for i in items); disc = 0; code = str(b.get('coupon', '')).strip()
    if code and c.execute("select name from sqlite_master where name='coupons'").fetchone():
        cp = c.execute('select * from coupons where code=?', (code,)).fetchone()
        if cp and total >= cp['min_total']:
            disc = min(total, cp['amount'] if cp['kind'] == '원' else total * cp['amount'] // 100)
    for i in items:   # 재고를 줄인다 — 남아 있을 때만 줄어드는 한 줄이라, 동시에 온 주문 가운데 먼저 온 것만 받는다(늦은 쪽은 여기서 거절되고 아무것도 바뀌지 않는다)
        if c.execute('update products set stock = stock - ? where id = ? and stock >= ?', (i['qty'], i['id'], i['qty'])).rowcount == 0:
            left = (c.execute('select stock from products where id=?', (i['id'],)).fetchone() or [0])[0]
            c.rollback()
            raise ValueError(f'「{i["name"]}」은(는) 지금 {max(left, 0)}개 남았습니다 — 수량을 줄이거나 장바구니에서 빼고 다시 주문해 주세요')
    payer = (str(b.get('payer', '')).strip() or b['name'])[:40]
    cur = c.execute('insert into orders(device,name,phone,address,memo,items,total,discount,coupon) values(?,?,?,?,?,?,?,?,?)', (d, b['name'][:40], b['phone'][:30], b['address'][:200], ('입금자 ' + payer + ' · ' + str(b.get('memo', '')))[:200], json.dumps(items, ensure_ascii=False), total - disc, disc, code if disc else ''))
    c.execute('delete from cart where device=?', (d,))
    return {'ok': True, 'id': cur.lastrowid, 'total': total - disc, 'discount': disc, 'payer': payer, 'bank': bank()}


def mine(c, req):
    out = [dict(r) for r in c.execute('select id, items, total, discount, status, created from orders where device=? order by id desc', (req['device'],))]
    for o in out:
        o['items'] = json.loads(o['items'])
    return {'orders': out, 'bank': bank() if out else {}}


ROUTES = [('POST', '/api/orders', place), ('GET', '/api/orders', mine)]
