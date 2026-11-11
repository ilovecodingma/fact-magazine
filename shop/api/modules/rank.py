# -*- coding: utf-8 -*-
"""지금 많이 보는 상품(지난 이레 동안 본 횟수로 순위)."""


def init(c):
    c.execute('create table if not exists views(pid integer, day text, n integer, primary key(pid, day))')


def hit(c, req):
    c.execute("insert into views values(?, date('now','localtime'), 1) on conflict(pid,day) do update set n=n+1", (int(req['body'].get('id', 0)),)); return {'ok': True}


def top(c, req):
    return {'products': [dict(r) for r in c.execute("select p.*, sum(v.n) as seen from views v join products p on p.id=v.pid where v.day >= date('now','localtime','-7 day') group by p.id order by seen desc limit 10")]}


ROUTES = [('POST', '/api/view', hit), ('GET', '/api/rank', top)]
