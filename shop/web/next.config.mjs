/** @type {import('next').NextConfig} */
// 화면과 백엔드를 한 주소로: /api/* 로 온 것은 이 PC 의 파이썬 백엔드(8787)로 넘긴다.
// 그래서 휴대폰이나 바깥에서 화면 주소 하나만 열어도 상품·장바구니·주문이 된다.
const BACKEND = process.env.SHOP_BACKEND || 'http://127.0.0.1:8787';
const nextConfig = {
  reactStrictMode: true,
  devIndicators: false,
  async rewrites() {
    return [{ source: '/api/:path*', destination: `${BACKEND}/api/:path*` }];
  },
};
export default nextConfig;
