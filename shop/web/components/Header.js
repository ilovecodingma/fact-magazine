'use client';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import site from '../site.json';
import { api, useShop } from '../lib/shop';

export default function Header() {
  const { count, has } = useShop();
  const [cats, setCats] = useState([]);
  const [q, setQ] = useState('');
  const router = useRouter();
  useEffect(() => { api('/api/categories').then((j) => setCats(j.categories || [])); }, []);
  const go = (e) => { e.preventDefault(); router.push('/search?q=' + encodeURIComponent(q.trim())); };
  return (
    <header className="hd">
      <div className="wrap hd-row">
        <Link href="/" className="logo">{site.name}</Link>
        <form className="find" onSubmit={go} role="search">
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="찾고 싶은 상품을 검색해 보세요" aria-label="상품 찾기" />
          <button aria-label="찾기">🔍</button>
        </form>
        <nav className="hd-my">
          {has('wish') && <Link href="/wish"><span className="ic">♡</span>찜</Link>}
          {has('orders') && <Link href="/orders"><span className="ic">📦</span>주문</Link>}
          {has('cart') && <Link href="/cart" className="cartlink"><span className="ic">🛒</span>장바구니{count > 0 && <em>{count}</em>}</Link>}
        </nav>
      </div>
      <div className="wrap cats">
        <Link href="/search">전체</Link>
        {cats.map((c) => <Link key={c} href={'/search?cat=' + encodeURIComponent(c)}>{c}</Link>)}
        {has('rank') && <Link href="/#rank" className="hot">지금 인기</Link>}
      </div>
    </header>
  );
}
