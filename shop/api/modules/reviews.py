# -*- coding: utf-8 -*-
"""상품평(별점과 한마디)."""


def init(c):
    c.execute("create table if not exists reviews(id integer primary key, pid integer, device text, name text, stars integer, body text, created text default (datetime('now','localtime')))")


def view(c, req):
    return {'reviews': [dict(r) for r in c.execute('select id, name, stars, body, created from reviews where pid=? order by id desc limit 50', (req['args'][0],))]}


def add(c, req):
    b = req['body']; stars = max(1, min(5, int(b.get('stars', 5)))); body = str(b.get('body', '')).strip()
    if len(body) < 2:
        raise ValueError('한마디를 적어 주세요')
    c.execute('insert into reviews(pid,device,name,stars,body) values(?,?,?,?,?)', (req['args'][0], req['device'], (str(b.get('name', '')).strip() or '구매자')[:20], stars, body[:500]))
    return view(c, req)


ROUTES = [('GET', r'/api/products/(\d+)/reviews', view), ('POST', r'/api/products/(\d+)/reviews', add)]
