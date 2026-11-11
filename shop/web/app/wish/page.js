'use client';
import { useEffect, useState } from 'react';
import { api } from '../../lib/shop';
import ProductCard from '../../components/ProductCard';

export default function Wish() {
  const [ps, setPs] = useState(null);
  useEffect(() => { api('/api/wish').then((j) => setPs((j.products || []).map((p) => ({ ...p, off: p.was > p.price ? Math.round((p.was - p.price) * 100 / p.was) : 0 })))); }, []);
  return (
    <section className="sec">
      <h2>찜한 상품</h2>
      {ps && ps.length === 0 && <p className="empty">상품의 ♡ 를 누르면 여기에 모입니다.</p>}
      <div className="grid five">{(ps || []).map((p) => <ProductCard key={p.id} p={p} />)}</div>
    </section>
  );
}
