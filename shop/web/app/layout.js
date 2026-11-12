import './globals.css';
import site from '../site.json';
import { ShopProvider } from '../lib/shop';
import Header from '../components/Header';
import TabBar from '../components/TabBar';

export const metadata = {
  title: `${site.name} — ${site.tagline}`,
  description: site.tagline,
  manifest: '/manifest.webmanifest',
  appleWebApp: { capable: true, title: site.name, statusBarStyle: 'default' },
};
export const viewport = { themeColor: site.color, width: 'device-width', initialScale: 1 };

export default function RootLayout({ children }) {
  const s = site.seller || {};
  const info = [s.company && `상호 ${s.company}`, s.owner && `대표 ${s.owner}`, s.bizno && `사업자등록번호 ${s.bizno}`, s.address, s.contact].filter(Boolean);
  return (
    <html lang="ko">
      <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
      </head>
      <body style={{ '--pri': site.color }}>
        <ShopProvider>
          <Header />
          <main className="wrap">{children}</main>
          <footer className="foot">
            <div className="wrap">
              <div><b>{site.name}</b>{site.tagline}{info.map((x) => <div key={x}>{x}</div>)}</div>
              <div><h4>주문과 배송</h4><a href="/orders">주문 내역</a><a href="/cart">장바구니</a><span>무통장 입금 · 입금 확인 뒤 보내 드립니다</span></div>
              <div><h4>둘러보기</h4><a href="/search">전체 상품</a><a href="/wish">찜한 상품</a></div>
            </div>
          </footer>
          <TabBar />
        </ShopProvider>
      </body>
    </html>
  );
}
