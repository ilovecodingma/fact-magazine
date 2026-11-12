'use client';
import Link from 'next/link';
import { useState } from 'react';
import { won } from '../lib/shop';

// 상품 사진: public/p/<번호>.jpg 가 있으면 그 사진, 없으면 바탕색에 그림 글자.
export function Thumb({ p, big }) {
  const [ok, setOk] = useState(true);
  return (
    <div className={'thumb' + (big ? ' big' : '')} style={{ background: p.color }}>
      {ok ? <img src={`/p/${p.id}.jpg`} alt={p.name} loading="lazy" onError={() => setOk(false)} /> : <span aria-hidden="true">{p.emoji}</span>}
    </div>
  );
}

export function Stars({ n, count }) {
  if (!count) return null;
  const full = Math.round(n);
  return <span className="stars">{'★'.repeat(full)}<i>{'★'.repeat(5 - full)}</i> <small>{count}</small></span>;
}

export default function ProductCard({ p, rank }) {
  return (
    <Link href={'/p/' + p.id} className="card">
      {rank && <b className="rankno">{rank}</b>}
      {p.badge && <span className="badge">{p.badge}</span>}
      <Thumb p={p} />
      <div className="card-b">
        <div className="nm">{p.name}</div>
        <div className="ds">{p.desc}</div>
        <div className="pr">
          {p.off > 0 && <b className="off">{p.off}%</b>}
          <span className="price">{won(p.price)}원</span>
          {p.off > 0 && <s>{won(p.was)}원</s>}
        </div>
        <Stars n={p.stars} count={p.reviews} />
      </div>
    </Link>
  );
}
