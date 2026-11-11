'use client';
import { useEffect, useState } from 'react';
import { api, won } from '../../lib/shop';

export default function Orders() {
  const [os, setOs] = useState(null);
  useEffect(() => { api('/api/orders').then((j) => setOs(j.orders || [])); }, []);
  return (
    <section className="sec">
      <h2>주문 내역</h2>
      {os && os.length === 0 && <p className="empty">아직 주문이 없습니다.</p>}
      <ul className="orders">
        {(os || []).map((o) => (
          <li key={o.id}>
            <div><b>주문 {o.id}번</b> <small>{o.created}</small> <span className={'st st-' + o.status.replace(' ', '')}>{o.status}</span></div>
            <p>{o.items.map((i) => `${i.name} ${i.qty}개`).join(' · ')}</p>
            <b>{won(o.total)}원</b>
          </li>
        ))}
      </ul>
    </section>
  );
}
