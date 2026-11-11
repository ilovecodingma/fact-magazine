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
  return (
    <html lang="ko">
      <body style={{ '--pri': site.color }}>
        <ShopProvider>
          <Header />
          <main className="wrap">{children}</main>
          <footer className="foot">
            <div className="wrap">
              <b>{site.name}</b>
              <span>주문하면 판매자가 연락드립니다</span>
              <a href="/orders">주문 내역</a>
            </div>
          </footer>
          <TabBar />
        </ShopProvider>
      </body>
    </html>
  );
}
