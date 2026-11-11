'use client';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api, useShop, won } from '../../lib/shop';
import { Thumb } from '../../components/ProductCard';

export default function Cart() {
  const { has, refresh } = useShop();
  const router = useRouter();
  const [cart, setCart] = useState(null);
  const [f, setF] = useState({ name: '', phone: '', address: '', memo: '', coupon: '' });
  const [msg, setMsg] = useState('');
  const [done, setDone] = useState(null);
  const load = () => api('/api/cart').then((j) => setCart(j.items ? j : { items: [], total: 0, count: 0 }));
  useEffect(() => { load(); }, []);
  const setQty = async (id, qty) => { setCart(await api('/api/cart/' + id, { method: 'PUT', body: { qty } })); refresh(); };
  const order = async (e) => {
    e.preventDefault();
    const j = await api('/api/orders', { method: 'POST', body: f });
    if (!j.ok) return setMsg(j.error || '주문하지 못했습니다');
    setDone(j); refresh();
  };

  if (done) return (
    <section className="done">
      <div className="check">✓</div>
      <h1>주문이 접수되었습니다</h1>
      <p>주문 번호 {done.id}번 · {won(done.total)}원{done.discount > 0 && ` (쿠폰 ${won(done.discount)}원 할인)`}</p>
      <p>판매자가 적어 주신 연락처로 안내드립니다.</p>
      <div className="buy"><Link href="/orders" className="btn line">주문 내역</Link><Link href="/" className="btn">계속 둘러보기</Link></div>
    </section>
  );
  if (!cart) return <p className="empty">불러오는 중…</p>;
  if (cart.items.length === 0) return <section className="done"><h1>장바구니가 비어 있습니다</h1><div className="buy"><Link href="/" className="btn">둘러보기</Link></div></section>;

  return (
    <div className="cartpage">
      <section className="sec">
        <h2>장바구니 <small>{cart.count}개</small></h2>
        <ul className="cartlist">
          {cart.items.map((i) => (
            <li key={i.id}>
              <Thumb p={i} />
              <div className="grow"><Link href={'/p/' + i.id}>{i.name}</Link><div className="price">{won(i.price)}<small>원</small></div></div>
              <div className="qty">
                <button onClick={() => setQty(i.id, i.qty - 1)} aria-label="하나 빼기">−</button><span>{i.qty}</span><button onClick={() => setQty(i.id, i.qty + 1)} aria-label="하나 더">＋</button>
              </div>
              <b className="sum">{won(i.price * i.qty)}원</b>
              <button className="x" onClick={() => setQty(i.id, 0)} aria-label="빼기">✕</button>
            </li>
          ))}
        </ul>
      </section>
      {has('orders') && (
        <form className="orderbox" onSubmit={order}>
          <h2>주문서</h2>
          <input placeholder="받는 분" value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} required />
          <input placeholder="연락처" value={f.phone} onChange={(e) => setF({ ...f, phone: e.target.value })} required inputMode="tel" />
          <input placeholder="주소" value={f.address} onChange={(e) => setF({ ...f, address: e.target.value })} required />
          <input placeholder="남길 말(선택)" value={f.memo} onChange={(e) => setF({ ...f, memo: e.target.value })} />
          {has('coupons') && <input placeholder="쿠폰 코드(선택)" value={f.coupon} onChange={(e) => setF({ ...f, coupon: e.target.value })} />}
          <div className="total"><span>상품 값</span><b>{won(cart.total)}원</b></div>
          <button className="btn wide">주문하기</button>
          <p className="msg" role="alert">{msg}</p>
        </form>
      )}
    </div>
  );
}
