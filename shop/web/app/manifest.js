import site from '../site.json';

// 휴대폰에서 「홈 화면에 추가」 하면 앱처럼 뜨게 하는 설정.
export default function manifest() {
  return {
    name: site.name,
    short_name: site.name,
    description: site.tagline,
    start_url: '/',
    display: 'standalone',
    background_color: '#ffffff',
    theme_color: site.color,
    icons: [
      { src: '/icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' },
      { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
      { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
    ],
  };
}
