'use client';
// 가게 화면이 함께 쓰는 것: 백엔드 부르기, 기기 표시, 붙어 있는 기능, 장바구니 수.
import { createContext, useCallback, useContext, useEffect, useState } from 'react';

export const API = process.env.NEXT_PUBLIC_API || '';   // 비어 있으면 같은 주소의 /api 로(화면이 백엔드로 넘겨 준다)

function device() {
  if (typeof window === 'undefined') return '';
  let d = localStorage.getItem('shop_device');
  if (!d) { d = 'd' + Math.random().toString(36).slice(2) + Date.now().toString(36); localStorage.setItem('shop_device', d); }
  return d;
}

export async function api(path, { method = 'GET', body, admin } = {}) {
  const headers = { 'Content-Type': 'application/json', 'X-Device': device() };
  if (admin) headers['X-Admin-Key'] = admin;
  try {
    const r = await fetch(API + path, { method, headers, body: body ? JSON.stringify(body) : undefined, cache: 'no-store' });
    const j = await r.json();
    return r.ok ? j : { ...j, failed: r.status };
  } catch (e) {
    return { failed: 0, error: '지금은 연결할 수 없습니다. 잠시 뒤 다시 해 주세요.' };
  }
}

export const won = (n) => (n || 0).toLocaleString('ko-KR');

const Ctx = createContext({ on: [], count: 0, refresh: () => {}, has: () => false });
export const useShop = () => useContext(Ctx);

export function ShopProvider({ children }) {
  const [on, setOn] = useState([]);
  const [count, setCount] = useState(0);
  const refresh = useCallback(async () => {
    const f = await api('/api/features');
    const list = f.on || [];
    setOn(list);
    if (list.includes('cart')) { const c = await api('/api/cart'); setCount(c.count || 0); } else setCount(0);
  }, []);
  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 5000); // 기능을 붙였다 떼면 몇 초 안에 화면이 따라간다
    if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => {});
    return () => clearInterval(t);
  }, [refresh]);
  return <Ctx.Provider value={{ on, count, refresh, has: (k) => on.includes(k) }}>{children}</Ctx.Provider>;
}
