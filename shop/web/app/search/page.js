'use client';
import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { api } from '../../lib/shop';
import ProductCard from '../../components/ProductCard';

function List() {
  const sp = useSearchParams();
  const cat = sp.get('cat') || '';
  const q = sp.get('q') || '';
  const [sort, setSort] = useState('');
  const [ps, setPs] = useState(null);
  useEffect(() => {
    const u = new URLSearchParams();
    if (cat) u.set('cat', cat);
    if (q) u.set('q', q);
    if (sort) u.set('sort', sort);
    api('/api/products?' + u.toString()).then((j) => setPs(j.products || []));
  }, [cat, q, sort]);
  return (
    <section className="sec">
      <div className="listhead">
        <h2>{q ? `「${q}」 찾은 결과` : cat || '전체 상품'} {ps && <small>{ps.length}개</small>}</h2>
        <div className="sorts">
          {[['', '추천순'], ['low', '낮은 값순'], ['high', '높은 값순'], ['new', '새로 온 순']].map(([k, t]) => (
            <button key={k} className={sort === k ? 'on' : ''} onClick={() => setSort(k)}>{t}</button>
          ))}
        </div>
      </div>
      {ps && ps.length === 0 && <p className="empty">찾는 상품이 없습니다.</p>}
      <div className="grid five">{(ps || []).map((p) => <ProductCard key={p.id} p={p} />)}</div>
    </section>
  );
}

export default function Search() {
  return <Suspense><List /></Suspense>;
}
