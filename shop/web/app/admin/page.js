'use client';
import { useEffect, useState } from 'react';
import { api, won } from '../../lib/shop';

export default function Admin() {
  const [key, setKey] = useState('');
  const [hasKey, setHasKey] = useState(null);
  const [key2, setKey2] = useState('');
  useEffect(() => { api('/api/features').then((f) => setHasKey(!!f.admin)); }, []);
  const setup = async (e) => {
    e.preventDefault();
    if (key !== key2) return setMsg('두 칸이 서로 다릅니다');
    const j = await api('/api/admin/setup', { method: 'POST', body: { key } });
    if (!j.ok) return setMsg(j.error);
    setHasKey(true); setKey2(''); setMsg('열쇠를 정했습니다. 그 열쇠로 들어가세요.');
  };
  const [data, setData] = useState(null);
  const [msg, setMsg] = useState('');
  const [bank, setBank] = useState({ bank: '', account: '', holder: '' });
  const [bankSet, setBankSet] = useState(null);
  const saveBank = async (e) => {
    e.preventDefault();
    const j = await api('/api/admin/bank', { method: 'POST', body: bank, admin: key });
    setMsg(j.ok ? '입금 계좌를 넣었습니다' : j.error); if (j.ok) { setBankSet(j.set); setBank({ bank: '', account: '', holder: '' }); }
  };
  const [np, setNp] = useState({ name: '', cat: '', price: '', was: '', emoji: '📦', desc: '' });
  const load = async (e) => {
    e && e.preventDefault();
    const j = await api('/api/admin/orders', { admin: key });
    if (j.failed !== undefined) { setData(null); return setMsg(j.error); }
    setMsg(''); setData(j);
    api('/api/admin/bank', { admin: key }).then((b) => setBankSet(!!b.set));
  };
  const setStatus = async (id, status) => setData(await api('/api/admin/orders/' + id, { method: 'PUT', body: { status }, admin: key }));
  const addProduct = async (e) => {
    e.preventDefault();
    const j = await api('/api/admin/products', { method: 'POST', body: { ...np, price: Number(np.price), was: Number(np.was) || Number(np.price) }, admin: key });
    setMsg(j.ok ? `상품을 올렸습니다(${j.id}번)` : j.error);
    if (j.ok) setNp({ name: '', cat: '', price: '', was: '', emoji: '📦', desc: '' });
  };
  if (!data && hasKey === false) return (
    <form className="orderbox narrow" onSubmit={setup}>
      <h2>운영자 열쇠 정하기</h2>
      <input type="password" placeholder="운영자 열쇠(여덟 글자 이상)" value={key} onChange={(e) => setKey(e.target.value)} required minLength={8} autoComplete="new-password" />
      <input type="password" placeholder="한 번 더" value={key2} onChange={(e) => setKey2(e.target.value)} required autoComplete="new-password" />
      <button className="btn wide">정하기</button>
      <p className="msg" role="alert">{msg}</p>
    </form>
  );
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
      <form className="orderbox" onSubmit={saveBank}>
        <h2>입금 계좌 <small style={{ fontWeight: 400, fontSize: 13 }}>{bankSet ? '넣어 둠' : '아직 없음'}</small></h2>
        <input placeholder="은행" value={bank.bank} onChange={(e) => setBank({ ...bank, bank: e.target.value })} required autoComplete="off" />
        <input placeholder="계좌 번호" value={bank.account} onChange={(e) => setBank({ ...bank, account: e.target.value })} required autoComplete="off" />
        <input placeholder="예금주" value={bank.holder} onChange={(e) => setBank({ ...bank, holder: e.target.value })} required autoComplete="off" />
        <button className="btn wide">계좌 넣기</button>
      </form>
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
