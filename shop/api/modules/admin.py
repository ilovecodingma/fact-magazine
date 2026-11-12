# -*- coding: utf-8 -*-
"""운영자: 들어온 주문 보기·상태 바꾸기, 상품 올리기·내리기. 환경변수 SHOP_ADMIN_KEY 로 정한 열쇠가 맞아야 한다."""
import json


def need(req):
    if not req['admin']:
        raise PermissionError()


def orders(c, req):
    need(req)
    out = [dict(r) for r in c.execute('select * from orders order by id desc limit 200')] if c.execute("select name from sqlite_master where name='orders'").fetchone() else []
    for o in out:
        o['items'] = json.loads(o['items'])
    return {'orders': out, 'waiting': sum(1 for o in out if o['status'] in ('입금 대기', '접수'))}


def status(c, req):
    need(req); s = str(req['body'].get('status', ''))
    if s not in ('입금 대기', '입금 확인', '보냄', '취소'):
        raise ValueError('상태는 입금 대기·입금 확인·보냄·취소 가운데 하나입니다')
    c.execute('update orders set status=? where id=?', (s, req['args'][0])); return orders(c, req)


def add_product(c, req):
    need(req); b = req['body']
    if not str(b.get('name', '')).strip() or int(b.get('price', 0) or 0) <= 0:
        raise ValueError('이름과 값을 적어 주세요')
    cur = c.execute('insert into products(name,cat,price,was,emoji,color,desc,badge) values(?,?,?,?,?,?,?,?)', (b['name'][:80], str(b.get('cat', '기타'))[:20], int(b['price']), int(b.get('was') or b['price']), str(b.get('emoji', '📦'))[:4], str(b.get('color', '#eef2ff'))[:9], str(b.get('desc', ''))[:1000], str(b.get('badge', ''))[:12]))
    return {'ok': True, 'id': cur.lastrowid}


def del_product(c, req):
    need(req); c.execute('delete from products where id=?', (req['args'][0],)); return {'ok': True}


def setup(c, req):
    """운영자 열쇠를 처음 한 번 정한다. 이 PC 에서 연 화면에서만 되고(바깥 주소로는 안 됨), 이미 정해져 있으면 안 된다."""
    import app
    if app.has_key():
        raise ValueError('운영자 열쇠가 이미 정해져 있습니다')
    if req.get('outside'):
        raise ValueError('운영자 열쇠는 가게를 켠 PC 에서만 정할 수 있습니다')
    k = str(req['body'].get('key', ''))
    if len(k) < 8:
        raise ValueError('여덟 글자 이상으로 정해 주세요')
    json.dump({'hash': app.key_hash(k)}, open(app.KEYFILE, 'w', encoding='utf-8'))
    return {'ok': True}


def set_bank(c, req):
    need(req); b = req['body']
    import os
    from modules.orders import BANK as fp
    d = {k: str(b.get(k, '')).strip()[:60] for k in ('bank', 'account', 'holder')}
    json.dump(d, open(fp, 'w', encoding='utf-8'), ensure_ascii=False)
    return {'ok': True, 'set': bool(d['account'])}


def has_bank(c, req):
    need(req)
    import os
    from modules.orders import BANK as fp
    try:
        return {'set': bool(json.load(open(fp, encoding='utf-8')).get('account'))}
    except Exception:
        return {'set': False}


ROUTES = [('POST', '/api/admin/setup', setup), ('POST', '/api/admin/bank', set_bank), ('GET', '/api/admin/bank', has_bank), ('GET', '/api/admin/orders', orders), ('PUT', r'/api/admin/orders/(\d+)', status), ('POST', '/api/admin/products', add_product), ('DELETE', r'/api/admin/products/(\d+)', del_product)]
