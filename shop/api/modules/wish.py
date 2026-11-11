# -*- coding: utf-8 -*-
"""찜."""


def init(c):
    c.execute('create table if not exists wish(device text, pid integer, primary key(device, pid))')


def view(c, req):
    d = req['device']
    return {'ids': [r[0] for r in c.execute('select pid from wish where device=?', (d,))], 'products': [dict(r) for r in c.execute('select p.* from wish w join products p on p.id=w.pid where w.device=?', (d,))]}


def toggle(c, req):
    d = req['device']; pid = int(req['body'].get('id', 0))
    if c.execute('select 1 from wish where device=? and pid=?', (d, pid)).fetchone():
        c.execute('delete from wish where device=? and pid=?', (d, pid))
    else:
        c.execute('insert into wish values(?,?)', (d, pid))
    return view(c, req)


ROUTES = [('GET', '/api/wish', view), ('POST', '/api/wish', toggle)]
