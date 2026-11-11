# -*- coding: utf-8 -*-
"""가게 백엔드 스스로 시험: 임시 자료로 서버를 켜고 방문자·운영자 노릇으로 한 바퀴. python shop/smoke.py"""
import json, os, subprocess, sys, tempfile, time, urllib.request, urllib.error
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__)); PORT = 8799; B = f'http://127.0.0.1:{PORT}'
CONF = os.path.join(HERE, 'api', 'modules.json')


def call(meth, path, body=None, admin=False):
    h = {'Content-Type': 'application/json', 'X-Device': 'smoke-1'}
    if admin:
        h['X-Admin-Key'] = 'smoke-key'
    r = urllib.request.Request(B + path, data=json.dumps(body).encode() if body is not None else None, headers=h, method=meth)
    try:
        return json.loads(urllib.request.urlopen(r, timeout=5).read().decode())
    except urllib.error.HTTPError as e:
        return dict(json.loads(e.read().decode()), _code=e.code)


def main():
    tmp = tempfile.mkdtemp(); keep = open(CONF, encoding='utf-8').read()
    env = dict(os.environ, SHOP_DB=os.path.join(tmp, 't.db'), SHOP_ADMIN_KEY='smoke-key')
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
        c = call('POST', '/api/cart', {'id': ps[0]['id'], 'qty': 2}); t('장바구니에 담깁니다', c.get('count') == 2, f'{c.get("total")}원')
        call('POST', '/api/wish', {'id': ps[1]['id']}); t('찜이 됩니다', ps[1]['id'] in call('GET', '/api/wish')['ids'])
        r = call('POST', f'/api/products/{ps[0]["id"]}/reviews', {'stars': 4, 'body': '잘 받았습니다'}); t('상품평이 달립니다', len(r.get('reviews', [])) == 1)
        call('POST', '/api/view', {'id': ps[0]['id']}); t('본 횟수로 순위가 섭니다', call('GET', '/api/rank')['products'][0]['id'] == ps[0]['id'])
        o = call('POST', '/api/orders', {'name': '시험', 'phone': '000', 'address': '시험 주소', 'coupon': '첫주문'}); t('주문이 접수되고 쿠폰이 먹습니다(결제 없음)', o.get('ok') and o.get('discount') == 3000, f'주문 {o.get("id")}번 {o.get("total")}원')
        t('주문 뒤 장바구니가 비워집니다', call('GET', '/api/cart')['count'] == 0)
        t('운영자 열쇠 없이는 주문 목록을 못 봅니다', call('GET', '/api/admin/orders').get('_code') == 403)
        a = call('GET', '/api/admin/orders', admin=True); t('운영자는 들어온 주문을 봅니다', a.get('waiting') == 1)
        a = call('PUT', f'/api/admin/orders/{o["id"]}', {'status': '보냄'}, admin=True); t('운영자가 상태를 바꿉니다', a['orders'][0]['status'] == '보냄')
        d = json.loads(keep); d['on'] = [x for x in d['on'] if x != 'reviews']; open(CONF, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1)); time.sleep(0.05)
        t('상품평을 떼면 서버를 끄지 않아도 그 주소가 사라집니다', call('GET', f'/api/products/{ps[0]["id"]}/reviews').get('_code') == 404 and 'reviews' not in call('GET', '/api/features')['on'])
        open(CONF, 'w', encoding='utf-8').write(keep); time.sleep(0.05)
        t('다시 붙이면 남긴 상품평이 그대로 돌아옵니다', len(call('GET', f'/api/products/{ps[0]["id"]}/reviews').get('reviews', [])) == 1)
    finally:
        open(CONF, 'w', encoding='utf-8').write(keep); p.terminate()
    print(f'  → {n}단계 가운데 {ok}단계 통과'); return 0 if ok == n else 1


if __name__ == '__main__':
    sys.exit(main())
