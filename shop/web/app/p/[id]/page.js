'use client';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api, useShop, won } from '../../../lib/shop';
import { Stars, Thumb } from '../../../components/ProductCard';

export default function Product() {
  const { id } = useParams();
  const router = useRouter();
  const { has, refresh } = useShop();
  const [p, setP] = useState(null);
  const [qty, setQty] = useState(1);
  const [wished, setWished] = useState(false);
  const [reviews, setReviews] = useState([]);
  const [msg, setMsg] = useState('');
  const [form, setForm] = useState({ stars: 5, body: '', name: '' });

  useEffect(() => { api('/api/products/' + id).then((j) => setP(j.product || false)); }, [id]);
  useEffect(() => { if (has('rank')) api('/api/view', { method: 'POST', body: { id: Number(id) } }); }, [id, has('rank')]);
  useEffect(() => { if (has('wish')) api('/api/wish').then((j) => setWished((j.ids || []).includes(Number(id)))); }, [id, has('wish')]);
  useEffect(() => { has('reviews') ? api(`/api/products/${id}/reviews`).then((j) => setReviews(j.reviews || [])) : setReviews([]); }, [id, has('reviews')]);

  if (p === null) return <p className="empty">불러오는 중…</p>;
  if (p === false) return <p className="empty">없는 상품입니다.</p>;

  const add = async (thenGo) => {
    const j = await api('/api/cart', { method: 'POST', body: { id: p.id, qty } });
    if (j.failed !== undefined) return setMsg(j.error);
    await refresh();
    if (thenGo) router.push('/cart'); else setMsg('장바구니에 담았습니다');
  };
  const wish = async () => { const j = await api('/api/wish', { method: 'POST', body: { id: p.id } }); setWished((j.ids || []).includes(p.id)); };
  const post = async (e) => {
    e.preventDefault();
    const j = await api(`/api/products/${id}/reviews`, { method: 'POST', body: form });
    if (j.reviews) { setReviews(j.reviews); setForm({ stars: 5, body: '', name: '' }); api('/api/products/' + id).then((x) => x.product && setP(x.product)); }
  };

  return (
    <>
      <section className="pd">
        <Thumb p={p} big />
        <div className="pd-info">
          <div className="crumb">{p.cat}</div>
          <h1>{p.name}</h1>
          <Stars n={p.stars} count={p.reviews} />
          <hr />
          {p.off > 0 && <div className="was"><b>{p.off}%</b> <s>{won(p.was)}원</s></div>}
          <div className="price big">{won(p.price)}<small>원</small></div>
          {p.badge && <div className="badge">{p.badge}</div>}
          <p className="desc">{p.desc}</p>
          {has('cart') && (
            <>
              <div className="qty">
                <button onClick={() => setQty(Math.max(1, qty - 1))} aria-label="하나 빼기">−</button>
                <span>{qty}</span>
                <button onClick={() => setQty(Math.min(99, qty + 1))} aria-label="하나 더">＋</button>
                <b>{won(p.price * qty)}원</b>
              </div>
              <div className="buy">
                {has('wish') && <button className={'wishbtn' + (wished ? ' on' : '')} onClick={wish} aria-label="찜">{wished ? '♥' : '♡'}</button>}
                <button className="btn line" onClick={() => add(false)}>장바구니 담기</button>
                {has('orders') && <button className="btn" onClick={() => add(true)}>바로 주문</button>}
              </div>
              <p className="msg" role="status">{msg}</p>
            </>
          )}
        </div>
      </section>

      {has('reviews') && (
        <section className="sec">
          <h2>상품평 <small>{reviews.length}개</small></h2>
          <form className="rvform" onSubmit={post}>
            <select value={form.stars} onChange={(e) => setForm({ ...form, stars: Number(e.target.value) })} aria-label="별점">
              {[5, 4, 3, 2, 1].map((n) => <option key={n} value={n}>{'★'.repeat(n)}</option>)}
            </select>
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="이름(비우면 구매자)" maxLength={20} />
            <input className="grow" value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} placeholder="써 보니 어땠나요?" maxLength={500} required />
            <button className="btn">남기기</button>
          </form>
          {reviews.length === 0 && <p className="empty">첫 상품평을 남겨 주세요.</p>}
          <ul className="rvs">
            {reviews.map((r) => <li key={r.id}><span className="stars">{'★'.repeat(r.stars)}</span> <b>{r.name}</b> <small>{r.created}</small><p>{r.body}</p></li>)}
          </ul>
        </section>
      )}
    </>
  );
}
