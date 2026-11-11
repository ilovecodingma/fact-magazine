# -*- coding: utf-8 -*-
"""주문. 결제는 없다 — 장바구니를 주문으로 「접수」하고, 그 뒤(입금 안내·보내기)는 운영자가 처리한다."""
import json


def init(c):
    c.execute("create table if not exists orders(id integer primary key, device text, name text, phone text, address text, memo text, items text, total integer, discount integer default 0, coupon text, status text default '접수', created text default (datetime('now','localtime')))")


def place(c, req):
    d = req['device']; b = req['body']
    for k, label in (('name', '받는 분을'), ('phone', '연락처를'), ('address', '주소를')):
        if not str(b.get(k, '')).strip():
            raise ValueError(label + ' 적어 주세요')
    items = [dict(r) for r in c.execute('select p.id, p.name, p.price, k.qty from cart k join products p on p.id=k.pid where k.device=?', (d,))]
    if not items:
        raise ValueError('장바구니가 비어 있습니다')
    total = sum(i['price'] * i['qty'] for i in items); disc = 0; code = str(b.get('coupon', '')).strip()
    if code and c.execute("select name from sqlite_master where name='coupons'").fetchone():
        cp = c.execute('select * from coupons where code=?', (code,)).fetchone()
        if cp and total >= cp['min_total']:
            disc = min(total, cp['amount'] if cp['kind'] == '원' else total * cp['amount'] // 100)
    cur = c.execute('insert into orders(device,name,phone,address,memo,items,total,discount,coupon) values(?,?,?,?,?,?,?,?,?)', (d, b['name'][:40], b['phone'][:30], b['address'][:200], str(b.get('memo', ''))[:200], json.dumps(items, ensure_ascii=False), total - disc, disc, code if disc else ''))
    c.execute('delete from cart where device=?', (d,))
    return {'ok': True, 'id': cur.lastrowid, 'total': total - disc, 'discount': disc}


def mine(c, req):
    out = [dict(r) for r in c.execute('select id, items, total, discount, status, created from orders where device=? order by id desc', (req['device'],))]
    for o in out:
        o['items'] = json.loads(o['items'])
    return {'orders': out}


ROUTES = [('POST', '/api/orders', place), ('GET', '/api/orders', mine)]
