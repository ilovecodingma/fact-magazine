'use client';
import Link from 'next/link';
import { won } from '../lib/shop';

export function Thumb({ p, big }) {
  return <div className={'thumb' + (big ? ' big' : '')} style={{ background: p.color }} aria-hidden="true">{p.emoji}</div>;
}

export function Stars({ n, count }) {
  if (!count) return null;
  const full = Math.round(n);
  return <span className="stars">{'★'.repeat(full)}<i>{'★'.repeat(5 - full)}</i> <small>({count})</small></span>;
}

export default function ProductCard({ p, rank }) {
  return (
    <Link href={'/p/' + p.id} className="card">
      {rank && <b className="rankno">{rank}</b>}
      <Thumb p={p} />
      <div className="card-b">
        <div className="nm">{p.name}</div>
        {p.off > 0 && <div className="was"><b>{p.off}%</b> <s>{won(p.was)}원</s></div>}
        <div className="price">{won(p.price)}<small>원</small></div>
        {p.badge && <div className="badge">{p.badge}</div>}
        <Stars n={p.stars} count={p.reviews} />
      </div>
    </Link>
  );
}
