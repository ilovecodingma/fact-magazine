'use client';
import { useState } from 'react';
import { api, won } from '../../lib/shop';

export default function Admin() {
  const [key, setKey] = useState('');
  const [data, setData] = useState(null);
  const [msg, setMsg] = useState('');
  const [np, setNp] = useState({ name: '', cat: '', price: '', was: '', emoji: '📦', desc: '' });
  const load = async (e) => {
    e && e.preventDefault();
    const j = await api('/api/admin/orders', { admin: key });
    if (j.failed !== undefined) { setData(null); return setMsg(j.error); }
    setMsg(''); setData(j);
  };
  const setStatus = async (id, status) => setData(await api('/api/admin/orders/' + id, { method: 'PUT', body: { status }, admin: key }));
  const addProduct = async (e) => {
    e.preventDefault();
    const j = await api('/api/admin/products', { method: 'POST', body: { ...np, price: Number(np.price), was: Number(np.was) || Number(np.price) }, admin: key });
    setMsg(j.ok ? `상품을 올렸습니다(${j.id}번)` : j.error);
    if (j.ok) setNp({ name: '', cat: '', price: '', was: '', emoji: '📦', desc: '' });
  };
  if (!data) return (
    <form className="orderbox narrow" onSubmit={load}>
      <h2>운영자</h2>
      <input type="password" placeholder="운영자 열쇠" value={key} onChange={(e) => setKey(e.target.value)} required />
      <button className="btn wide">들어가기</button>
      <p className="msg" role="alert">{msg}</p>
    </form>
  );
  return (
    <>
      <section className="sec">
        <h2>들어온 주문 <small>처리 기다림 {data.waiting}건</small></h2>
        {data.orders.length === 0 && <p className="empty">아직 주문이 없습니다.</p>}
        <ul className="orders">
          {data.orders.map((o) => (
            <li key={o.id}>
              <div><b>주문 {o.id}번</b> <small>{o.created}</small> <span className={'st st-' + o.status.replace(' ', '')}>{o.status}</span></div>
              <p>{o.items.map((i) => `${i.name} ${i.qty}개`).join(' · ')}</p>
              <p><b>{won(o.total)}원</b> · {o.name} · {o.phone} · {o.address}{o.memo && ` · ${o.memo}`}</p>
              <div className="sorts">{['입금 대기', '입금 확인', '보냄', '취소'].map((s) => <button key={s} className={o.status === s ? 'on' : ''} onClick={() => setStatus(o.id, s)}>{s}</button>)}</div>
            </li>
          ))}
        </ul>
      </section>
      <form className="orderbox" onSubmit={addProduct}>
        <h2>상품 올리기</h2>
        <input placeholder="상품 이름" value={np.name} onChange={(e) => setNp({ ...np, name: e.target.value })} required />
        <input placeholder="분류" value={np.cat} onChange={(e) => setNp({ ...np, cat: e.target.value })} required />
        <input placeholder="값(원)" value={np.price} onChange={(e) => setNp({ ...np, price: e.target.value })} required inputMode="numeric" />
        <input placeholder="원래 값(선택)" value={np.was} onChange={(e) => setNp({ ...np, was: e.target.value })} inputMode="numeric" />
        <input placeholder="그림 글자" value={np.emoji} onChange={(e) => setNp({ ...np, emoji: e.target.value })} />
        <input placeholder="한 줄 설명" value={np.desc} onChange={(e) => setNp({ ...np, desc: e.target.value })} />
        <button className="btn wide">올리기</button>
        <p className="msg" role="status">{msg}</p>
      </form>
    </>
  );
}
