# -*- coding: utf-8 -*-
"""상품·분류·찾기. 상품은 data/products.json(보기 자료)에서 처음 한 번 들어간다 — 독자의 상품으로 바꾸려면 그 파일을 고치고 python run.py 가게 상품다시."""
import json, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = os.path.join(HERE, 'data', 'products.json')


def init(c):
    c.execute('create table if not exists products(id integer primary key, name text, cat text, price integer, was integer, emoji text, color text, desc text, badge text, stock integer default 99, created text default current_timestamp)')
    if c.execute('select count(*) from products').fetchone()[0] == 0 and os.path.exists(SEED):
        for p in json.load(open(SEED, encoding='utf-8'))['products']:
            c.execute('insert into products(name,cat,price,was,emoji,color,desc,badge,stock) values(?,?,?,?,?,?,?,?,?)', (p['name'], p['cat'], p['price'], p.get('was') or p['price'], p.get('emoji', '📦'), p.get('color', '#eef2ff'), p.get('desc', ''), p.get('badge', ''), int(p.get('stock', 99))))


def stats(c, ps):
    has = c.execute("select name from sqlite_master where name='reviews'").fetchone()
    for p in ps:
        r = c.execute('select count(*), avg(stars) from reviews where pid=?', (p['id'],)).fetchone() if has else (0, None)
        p['reviews'] = r[0]; p['stars'] = round(r[1], 1) if r[1] else 0
        p['soldout'] = (p.get('stock') or 0) <= 0
        p['off'] = round((p['was'] - p['price']) * 100 / p['was']) if p['was'] > p['price'] else 0
    return ps


def cats(c, req):
    return {'categories': [r[0] for r in c.execute('select cat from products group by cat order by min(id)')]}


def plist(c, req):
    q = req['q']; sql = 'select * from products where 1=1'; a = []
    if q.get('cat'):
        sql += ' and cat=?'; a.append(q['cat'])
    if q.get('q'):
        sql += ' and (name like ? or desc like ?)'; a += ['%' + q['q'] + '%'] * 2
    sql += {'low': ' order by price', 'high': ' order by price desc', 'new': ' order by id desc'}.get(q.get('sort'), ' order by id')
    return {'products': stats(c, [dict(r) for r in c.execute(sql, a)])}


def pone(c, req):
    r = c.execute('select * from products where id=?', (req['args'][0],)).fetchone()
    if not r:
        raise ValueError('없는 상품입니다')
    return {'product': stats(c, [dict(r)])[0]}


ROUTES = [('GET', '/api/categories', cats), ('GET', '/api/products', plist), ('GET', r'/api/products/(\d+)', pone)]
