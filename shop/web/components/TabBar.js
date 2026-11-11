'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useShop } from '../lib/shop';

// 휴대폰에서 앱처럼 보이는 아래 메뉴.
export default function TabBar() {
  const p = usePathname();
  const { count, has } = useShop();
  const tabs = [['/', '🏠', '홈', true], ['/search', '🔍', '찾기', true], ['/wish', '♡', '찜', has('wish')], ['/cart', '🛒', '장바구니', has('cart')], ['/orders', '📦', '주문', has('orders')]];
  return (
    <nav className="tabbar">
      {tabs.filter((t) => t[3]).map(([href, ic, label]) => (
        <Link key={href} href={href} className={p === href ? 'on' : ''}>
          <span>{ic}{href === '/cart' && count > 0 && <em>{count}</em>}</span>{label}
        </Link>
      ))}
    </nav>
  );
}
