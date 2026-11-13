# -*- coding: utf-8 -*-
"""가게 백엔드 스스로 시험: 임시 자료로 서버를 켜고 방문자·운영자 노릇으로 한 바퀴. python shop/smoke.py"""
import json, os, subprocess, sys, tempfile, time, urllib.request, urllib.error
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
import socket


def _free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p   # 빈 포트를 골라 쓴다: 두 벌이 겹쳐 돌아도 서로 깨지 않게


HERE = os.path.dirname(os.path.abspath(__file__)); PORT = _free_port(); B = f'http://127.0.0.1:{PORT}'
REAL = os.path.join(HERE, 'api', 'modules.json')


def call(meth, path, body=None, admin=False, dev='smoke-1'):
    h = {'Content-Type': 'application/json', 'X-Device': dev}
    if admin:
        h['X-Admin-Key'] = 'smoke-key'
    r = urllib.request.Request(B + path, data=json.dumps(body).encode() if body is not None else None, headers=h, method=meth)
    try:
        return json.loads(urllib.request.urlopen(r, timeout=5).read().decode())
    except urllib.error.HTTPError as e:
        return dict(json.loads(e.read().decode()), _code=e.code)


def main():
    # 시험은 모든 기능을 붙인 임시 가게로 돈다: 내 가게의 설정(modules.json)과 자료를 건드리지 않는다
    tmp = tempfile.mkdtemp(); CONF = os.path.join(tmp, 'modules.json')
    ALL = ['catalog', 'cart', 'orders'] + sorted(f[:-3] for f in os.listdir(os.path.join(HERE, 'api', 'modules')) if f.endswith('.py') and f[:-3] not in ('__init__', 'catalog', 'cart', 'orders'))
    keep = json.dumps({'on': ALL}, ensure_ascii=False); open(CONF, 'w', encoding='utf-8').write(keep)
    off = [m for m in ALL if m not in json.load(open(REAL, encoding='utf-8'))['on']]
    env = dict(os.environ, SHOP_DB=os.path.join(tmp, 't.db'), SHOP_ADMIN_KEY='smoke-key', SHOP_CONF=CONF)
    p = subprocess.Popen([sys.executable, '-X', 'utf8', os.path.join(HERE, 'api', 'app.py'), '--port', str(PORT)], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ok = 0; n = 0

    def t(name, cond, show=''):
        nonlocal ok, n
        n += 1; ok += 1 if cond else 0; print(('  ✓ ' if cond else '  ✗ ') + f'{n}. {name}' + (f'  → {show}' if show else ''), flush=True)
    try:
        for _ in range(40):
            try:
                urllib.request.urlopen(B + '/api/features', timeout=1); break
            except Exception:
                time.sleep(0.25)
        f = call('GET', '/api/features'); t('서버가 켜지고 붙은 기능을 말합니다', 'catalog' in f.get('on', []), ', '.join(f.get('on', [])))
        ps = call('GET', '/api/products')['products']; t('상품 목록이 나옵니다', len(ps) > 0, f'{len(ps)}개')
        t('분류로 거릅니다', all(x['cat'] == ps[0]['cat'] for x in call('GET', '/api/products?cat=' + urllib.request.quote(ps[0]['cat']))['products']))
        t('이름으로 찾습니다', len(call('GET', '/api/products?q=' + urllib.request.quote(ps[0]['name'][:3]))['products']) >= 1)
        q0 = min(99, max(2, -(-20000 // max(1, ps[0]['price']))))   # 쿠폰이 먹는 값(2만 원)을 넘게 담는다: 상품 값이 얼마든 같은 시험이 되게
        c = call('POST', '/api/cart', {'id': ps[0]['id'], 'qty': q0}); t('장바구니에 담깁니다', c.get('count') == q0, f'{c.get("total")}원')
        call('POST', '/api/wish', {'id': ps[1]['id']}); t('찜이 됩니다', ps[1]['id'] in call('GET', '/api/wish')['ids'])
        r = call('POST', f'/api/products/{ps[0]["id"]}/reviews', {'stars': 4, 'body': '잘 받았습니다'}); t('상품평이 달립니다', len(r.get('reviews', [])) == 1)
        import sqlite3 as _sq
        _c = _sq.connect(env['SHOP_DB']); _c.execute('update products set stock=0 where id=?', (ps[2]['id'],)); _c.commit(); _c.close()
        _c = _sq.connect(env['SHOP_DB']); _c.execute('update products set stock=99 where id=?', (ps[2]['id'],)); _c.commit(); _c.close(); call('POST', '/api/cart', {'id': ps[2]['id'], 'qty': 1})
        _c = _sq.connect(env['SHOP_DB']); _c.execute('update products set stock=0 where id=?', (ps[2]['id'],)); _c.commit(); _c.close()
        t('담아 둔 뒤에 품절된 상품이 있으면 주문이 거절됩니다', call('POST', '/api/orders', {'name': '시험', 'phone': '000', 'address': '시험 주소'}).get('_code') == 400)
        call('DELETE', f'/api/cart/{ps[2]["id"]}')
        t('품절된 상품은 「품절」로 나오고 장바구니에 담기지 않습니다', call('GET', f'/api/products/{ps[2]["id"]}')['product'].get('soldout') is True and call('POST', '/api/cart', {'id': ps[2]['id'], 'qty': 1}).get('_code') == 400)
        call('POST', '/api/view', {'id': ps[0]['id']}); t('본 횟수로 순위가 섭니다', call('GET', '/api/rank')['products'][0]['id'] == ps[0]['id'])
        o = call('POST', '/api/orders', {'name': '시험', 'phone': '000', 'address': '시험 주소', 'coupon': '첫주문'}); t('무통장 입금으로 주문이 들어가고 쿠폰이 먹습니다', o.get('ok') and o.get('discount') == 3000 and 'bank' in o, f'주문 {o.get("id")}번 {o.get("total")}원')
        t('주문 뒤 장바구니가 비워집니다', call('GET', '/api/cart')['count'] == 0)
        import threading as _th
        _c = _sq.connect(env['SHOP_DB']); _c.execute('update products set stock=1 where id=?', (ps[3]['id'],)); _c.commit(); _c.close()
        for _d in ('smoke-a', 'smoke-b'):
            call('POST', '/api/cart', {'id': ps[3]['id'], 'qty': 1}, dev=_d)
        _res = {}
        def _order(_d):
            _res[_d] = call('POST', '/api/orders', {'name': '시험', 'phone': '000', 'address': '시험 주소'}, dev=_d)
        _ts = [_th.Thread(target=_order, args=(_d,)) for _d in ('smoke-a', 'smoke-b')]
        [x.start() for x in _ts]; [x.join() for x in _ts]
        _ok = [d for d, r in _res.items() if r.get('ok')]; _no = [r for r in _res.values() if r.get('_code') == 400]
        t('하나 남은 상품에 두 사람이 동시에 주문하면 한 사람만 받고, 재고는 0 이 됩니다', len(_ok) == 1 and len(_no) == 1 and call('GET', f'/api/products/{ps[3]["id"]}')['product'].get('soldout') is True, (_no[0].get('error', '') if _no else '')[:40])
        _c = _sq.connect(env['SHOP_DB']); _c.execute('update products set stock=99 where id=?', (ps[3]['id'],)); _c.commit(); _c.close()
        t('운영자 비밀번호 없이는 주문 목록을 못 봅니다', call('GET', '/api/admin/orders').get('_code') == 403)
        call('POST', '/api/admin/bank', {'bank': '시험은행', 'account': '000-00-0000', 'holder': '시험'}, admin=True)
        t('운영자가 넣은 입금 계좌는 주문한 사람에게만 보이고, 비밀번호 없이는 바꿀 수 없습니다', call('GET', '/api/orders').get('bank', {}).get('account') == '000-00-0000' and call('GET', '/api/bank').get('_code') == 404 and call('POST', '/api/admin/bank', {'bank': 'x', 'account': 'y', 'holder': 'z'}).get('_code') == 403)
        t('이미 정해진 운영자 비밀번호는 다시 정할 수 없습니다', call('POST', '/api/admin/setup', {'key': 'another-key-123'}).get('_code') == 400)
        a = call('GET', '/api/admin/orders', admin=True); t('운영자는 입금 대기 주문을 봅니다', a.get('waiting') == 2 and all(x['status'] == '입금 대기' for x in a['orders']))
        _c = _sq.connect(env['SHOP_DB']); _c.execute('update products set stock=5 where id=?', (ps[0]['id'],)); _c.commit(); _c.close()
        call('POST', '/api/cart', {'id': ps[0]['id'], 'qty': 2}, dev='smoke-c'); _o2 = call('POST', '/api/orders', {'name': '시험', 'phone': '000', 'address': '시험 주소'}, dev='smoke-c')
        _st = lambda: call('GET', f'/api/products/{ps[0]["id"]}')['product'].get('stock')
        _a = _st(); call('PUT', f'/api/admin/orders/{_o2["id"]}', {'status': '취소'}, admin=True); _b = _st()
        call('PUT', f'/api/admin/orders/{_o2["id"]}', {'status': '입금 대기'}, admin=True); _d = _st()
        t('주문을 취소하면 재고가 돌아오고, 취소를 풀면 다시 줄어듭니다', (_a, _b, _d) == (3, 5, 3), f'재고 {_a} → 취소 {_b} → 취소 풀기 {_d}')
        _c = _sq.connect(env['SHOP_DB']); _c.execute('update products set stock=99 where id=?', (ps[0]['id'],)); _c.commit(); _c.close()
        a = call('PUT', f'/api/admin/orders/{o["id"]}', {'status': '입금 확인'}, admin=True); t('운영자가 입금을 확인합니다', next(x for x in a['orders'] if x['id'] == o['id'])['status'] == '입금 확인')
        rid = call('GET', '/api/admin/reviews', admin=True)['reviews'][0]['id']; call('PUT', f'/api/admin/reviews/{rid}', {'reply': '고맙습니다'}, admin=True)
        t('운영자가 올린 답글이 상품평 아래에 보이고, 비밀번호 없이는 답글을 달 수 없습니다', call('GET', f'/api/products/{ps[0]["id"]}/reviews')['reviews'][0].get('reply') == '고맙습니다' and call('PUT', f'/api/admin/reviews/{rid}', {'reply': 'x'}).get('_code') == 403)
        d = json.loads(keep); d['on'] = [x for x in d['on'] if x != 'reviews']; open(CONF, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1)); time.sleep(0.05)
        t('상품평을 떼면 서버를 끄지 않아도 그 주소가 사라집니다', call('GET', f'/api/products/{ps[0]["id"]}/reviews').get('_code') == 404 and 'reviews' not in call('GET', '/api/features')['on'])
        open(CONF, 'w', encoding='utf-8').write(keep); time.sleep(0.05)
        t('다시 붙이면 남긴 상품평이 그대로 돌아옵니다', len(call('GET', f'/api/products/{ps[0]["id"]}/reviews').get('reviews', [])) == 1)
    finally:
        open(CONF, 'w', encoding='utf-8').write(keep); p.terminate()
    print(f'  → {n}단계 가운데 {ok}단계 통과')
    if off:
        print('  (시험은 모든 기능을 붙인 임시 가게로 돌렸습니다. 지금 내 가게에서 떼어 놓은 기능: ' + ', '.join(off) + ' — 내 가게의 설정과 자료는 건드리지 않았습니다)')
    return 0 if ok == n else 1


if __name__ == '__main__':
    sys.exit(main())
