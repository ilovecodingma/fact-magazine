# -*- coding: utf-8 -*-
"""장바구니. 가입이 없으므로 기기마다(X-Device) 하나씩 가진다."""


def init(c):
    c.execute('create table if not exists cart(device text, pid integer, qty integer, primary key(device, pid))')


def need(req):
    if not req['device']:
        raise ValueError('기기 표시가 없습니다')
    return req['device']


def view(c, req):
    d = need(req)
    items = [dict(r) for r in c.execute('select p.id, p.name, p.price, p.was, p.emoji, p.color, k.qty from cart k join products p on p.id=k.pid where k.device=? order by k.rowid', (d,))]
    return {'items': items, 'count': sum(i['qty'] for i in items), 'total': sum(i['qty'] * i['price'] for i in items)}


def add(c, req):
    d = need(req); pid = int(req['body'].get('id', 0)); qty = max(1, min(99, int(req['body'].get('qty', 1))))
    r = c.execute('select stock from products where id=?', (pid,)).fetchone()
    if not r:
        raise ValueError('없는 상품입니다')
    if (r[0] or 0) <= 0:
        raise ValueError('품절된 상품입니다')
    c.execute('insert into cart(device,pid,qty) values(?,?,?) on conflict(device,pid) do update set qty=min(99, qty+excluded.qty)', (d, pid, qty))
    return view(c, req)


def setqty(c, req):
    d = need(req); qty = int(req['body'].get('qty', 1))
    if qty <= 0:
        c.execute('delete from cart where device=? and pid=?', (d, req['args'][0]))
    else:
        c.execute('update cart set qty=? where device=? and pid=?', (min(99, qty), d, req['args'][0]))
    return view(c, req)


def remove(c, req):
    c.execute('delete from cart where device=? and pid=?', (need(req), req['args'][0])); return view(c, req)


ROUTES = [('GET', '/api/cart', view), ('POST', '/api/cart', add), ('PUT', r'/api/cart/(\d+)', setqty), ('DELETE', r'/api/cart/(\d+)', remove)]
