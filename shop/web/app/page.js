'use client';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import site from '../site.json';
import { api, useShop } from '../lib/shop';
import ProductCard from '../components/ProductCard';

export default function Home() {
  const { has } = useShop();
  const [ps, setPs] = useState([]);
  const [rank, setRank] = useState([]);
  const [coupons, setCoupons] = useState([]);
  useEffect(() => { api('/api/products').then((j) => setPs(j.products || [])); }, []);
  useEffect(() => { has('rank') ? api('/api/rank').then((j) => setRank(j.products || [])) : setRank([]); }, [has('rank')]);
  useEffect(() => { has('coupons') ? api('/api/coupons').then((j) => setCoupons(j.coupons || [])) : setCoupons([]); }, [has('coupons')]);
  const deals = [...ps].sort((a, b) => b.off - a.off).slice(0, 6);
  const cats = [...new Set(ps.map((p) => p.cat))];
  return (
    <>
      <section className="hero">
        <div>
          <h1>{site.banner.title}</h1>
          <p>{site.banner.sub}</p>
          <Link href="/search" className="btn">둘러보기</Link>
        </div>
        {coupons[0] && <div className="coupon"><small>쿠폰</small><b>{coupons[0].title}</b><code>{coupons[0].code}</code></div>}
      </section>

      <section className="sec">
        <h2>오늘의 특가</h2>
        <div className="grid six">{deals.map((p) => <ProductCard key={p.id} p={p} />)}</div>
      </section>

      {has('rank') && rank.length > 0 && (
        <section className="sec" id="rank">
          <h2>지금 많이 보는 상품</h2>
          <div className="grid six">{rank.slice(0, 6).map((p, i) => <ProductCard key={p.id} p={{ ...p, off: p.was > p.price ? Math.round((p.was - p.price) * 100 / p.was) : 0 }} rank={i + 1} />)}</div>
        </section>
      )}

      {cats.map((c) => (
        <section className="sec" key={c}>
          <h2>{c} <Link href={'/search?cat=' + encodeURIComponent(c)}>더 보기 ›</Link></h2>
          <div className="grid six">{ps.filter((p) => p.cat === c).slice(0, 6).map((p) => <ProductCard key={p.id} p={p} />)}</div>
        </section>
      ))}
    </>
  );
}
