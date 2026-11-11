# -*- coding: utf-8 -*-
"""쿠폰. 주문할 때 코드를 넣으면 깎인다(주문 기능이 붙어 있을 때)."""


def init(c):
    c.execute('create table if not exists coupons(code text primary key, title text, kind text, amount integer, min_total integer default 0)')
    if c.execute('select count(*) from coupons').fetchone()[0] == 0:
        c.execute("insert into coupons values('첫주문', '첫 주문 3,000원 할인', '원', 3000, 20000)")


def view(c, req):
    return {'coupons': [dict(r) for r in c.execute('select * from coupons')]}


ROUTES = [('GET', '/api/coupons', view)]
