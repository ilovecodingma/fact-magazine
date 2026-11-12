// 본을 받아 보는 도구: 로그인 없는 새 브라우저(Edge·Chrome, 창 없이)로 주소를 열어 화면을 위에서 아래까지 찍고, 화면 요소의 자리·크기·글자·색을 잰다.
// 사용: node refshot.js <주소> <받을 폴더> <이름> [가로=1440] [세로=900] [mobile] [--steps 차례.json]
// 결과: <폴더>/<이름>_1.png … (한 화면씩) · <폴더>/<이름>.json (잰 값). 남의 사이트 화면은 저장소에 넣지 않는다(내 PC 임시 폴더에만).
const { spawn } = require('child_process'); const fs = require('fs'); const path = require('path');
const [url, outdir0, name] = process.argv.slice(2, 5); const outdir = outdir0 ? path.resolve(outdir0) : outdir0; /* 받을 폴더는 어떻게 적어도 절대 경로로 바꿔 쓴다(상대 경로면 브라우저가 연결되지 않는다) */ const vw = +(process.argv[5] || 1440), vh = +(process.argv[6] || 900), mobile = process.argv[7] === 'mobile';
if (!url || !outdir || !name) { console.log('사용: node refshot.js <주소> <받을 폴더> <이름> [가로] [세로] [mobile]'); process.exit(1); }
const CANDS = [process.env.BROWSER, 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', 'C:/Program Files/Microsoft/Edge/Application/msedge.exe', 'C:/Program Files/Google/Chrome/Application/chrome.exe', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/usr/bin/google-chrome', '/usr/bin/chromium'].filter(Boolean);
const BR = CANDS.find((p) => fs.existsSync(p)); if (!BR) { console.log('브라우저(Edge·Chrome)를 찾지 못했습니다'); process.exit(1); }
fs.mkdirSync(outdir, { recursive: true });
const prof = path.join(outdir, '_p_' + name + '_' + Date.now()); const port = 9300 + Math.floor(Math.random() * 600);
const p = spawn(BR, ['--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--remote-debugging-port=' + port, '--user-data-dir=' + prof, `--window-size=${vw},${vh}`, 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const JPG = process.argv.includes('jpg'); const EXT = JPG ? 'jpg' : 'png'; const SHOTFMT = JPG ? { format: 'jpeg', quality: 86 } : { format: 'png' };   // 끝에 jpg 를 붙이면 jpg 로(책에 넣을 때 가볍게)

// 화면에서 재는 것: 글자가 든 잎 요소와 그림·단추·칸의 자리(x,y,w,h)와 글자 크기·굵기·줄 높이·색·바탕·글꼴·둥글기.
const MEASURE = `(() => {
  const out = []; const seen = new Set();
  const push = (el, kind) => { const r = el.getBoundingClientRect(); if (r.width < 2 || r.height < 2) return; const s = getComputedStyle(el); if (s.visibility === 'hidden' || s.display === 'none' || +s.opacity === 0) return;
    const k = [kind, Math.round(r.x), Math.round(r.y + scrollY), Math.round(r.width), Math.round(r.height)].join(','); if (seen.has(k)) return; seen.add(k);
    out.push({ k: kind, tag: el.tagName.toLowerCase(), t: kind === 'text' ? el.textContent.trim().replace(/\\s+/g, ' ').slice(0, 40) : (el.getAttribute('alt') || el.getAttribute('aria-label') || '').slice(0, 30), x: Math.round(r.x), y: Math.round(r.y + scrollY), w: Math.round(r.width), h: Math.round(r.height), fs: parseFloat(s.fontSize), fw: s.fontWeight, lh: s.lineHeight, c: s.color, bg: s.backgroundColor, ff: s.fontFamily.split(',')[0].replace(/"/g, ''), ls: s.letterSpacing, br: s.borderRadius, bd: s.borderTopWidth !== '0px' ? s.borderTopWidth + ' ' + s.borderTopColor : '', bb: s.borderBottomWidth !== '0px' ? s.borderBottomWidth + ' ' + s.borderBottomColor : '', pad: s.padding }); };
  for (const el of document.querySelectorAll('body *')) {
    if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'PATH', 'G'].includes(el.tagName.toUpperCase())) continue;
    const own = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim().length > 0);
    if (own) push(el, 'text'); else if (['IMG', 'SVG', 'PICTURE', 'VIDEO'].includes(el.tagName.toUpperCase())) push(el, 'img'); else if (['BUTTON', 'INPUT', 'TEXTAREA', 'SELECT'].includes(el.tagName.toUpperCase())) push(el, 'ctl');
    else { const s = getComputedStyle(el); if ((s.backgroundColor !== 'rgba(0, 0, 0, 0)' && s.backgroundColor !== 'rgb(255, 255, 255)') || s.borderTopWidth !== '0px' || s.borderBottomWidth !== '0px' || s.boxShadow !== 'none') push(el, 'box'); }
  }
  return JSON.stringify({ url: location.href, title: document.title, vw: innerWidth, vh: innerHeight, docH: document.documentElement.scrollHeight, bodyBg: getComputedStyle(document.body).backgroundColor, bodyFont: getComputedStyle(document.body).fontFamily, items: out.slice(0, 1500) });
})()`;

(async () => {
  let list; for (let i = 0; i < 60; i++) { try { list = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); if (list.length) break; } catch (e) {} await sleep(250); }
  const ws = new WebSocket(list.find((x) => x.type === 'page').webSocketDebuggerUrl); await new Promise((r) => (ws.onopen = r));
  let id = 0; const pend = {}; ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pend[d.id]) { pend[d.id](d.result || d.error); delete pend[d.id]; } };
  const send = (method, params = {}) => new Promise((r) => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
  await send('Page.enable'); await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: vw, height: vh, deviceScaleFactor: 1, mobile });
  if (mobile) await send('Emulation.setUserAgentOverride', { userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' });
  await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: process.argv.includes('dark') ? 'dark' : 'light' }] });
  if (process.argv.includes('nojs')) await send('Emulation.setScriptExecutionDisabled', { value: true });   // 받아 둔 원문(file://)을 그릴 때: 화면의 스크립트가 주소를 보고 딴 쪽으로 바꾸지 않게
  await send('Page.navigate', { url }); await sleep(6000);
  const ev = async (expression) => (await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true })).result?.value;
  // --steps <파일.json>: 칸에 넣고 → 누르고 → 찍는 차례. 입력이 있어야 나오는 화면(주문 완료·운영자 화면)을 찍을 때 쓴다.
  // 차례 한 칸: {"shot":"이름"} {"fill":"고르는 말","value":"넣을 값"} {"click":"고르는 말"} {"clickText":"단추 글자"} {"wait":1000} {"goto":"주소"} {"scroll":600}
  const si = process.argv.indexOf('--steps');
  if (si > 0) {
    const steps = JSON.parse(fs.readFileSync(process.argv[si + 1], 'utf8')); const made = [];
    for (const st of steps) {
      if (st.goto) { await send('Page.navigate', { url: st.goto }); await sleep(st.wait || 3500); }
      else if (st.fill) { await ev(`(() => { const el = document.querySelector(${JSON.stringify(st.fill)}); if (!el) return false; const set = Object.getOwnPropertyDescriptor(el.tagName === 'SELECT' ? HTMLSelectElement.prototype : el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype, 'value').set; set.call(el, ${JSON.stringify(String(st.value))}); el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); return true; })()`); await sleep(250); }
      else if (st.click) { await ev(`(() => { const el = document.querySelector(${JSON.stringify(st.click)}); if (el) el.click(); return !!el; })()`); await sleep(st.wait || 1500); }
      else if (st.clickText) { await ev(`(() => { const el = [...document.querySelectorAll('main button'), ...document.querySelectorAll('button'), ...document.querySelectorAll('main a'), ...document.querySelectorAll('a')].find((e) => e.textContent.trim() === ${JSON.stringify(st.clickText)}); if (el) el.click(); return !!el; })()`); await sleep(st.wait || 1500); }
      else if (st.scroll !== undefined) { await ev(`scrollTo(0, ${+st.scroll})`); await sleep(500); }
      else if (st.shot) { const shot = await send('Page.captureScreenshot', SHOTFMT); const f = path.join(outdir, `${name}_${st.shot}.${EXT}`); fs.writeFileSync(f, Buffer.from(shot.data, 'base64')); made.push(path.basename(f)); }
      else if (st.wait) { await sleep(st.wait); }
    }
    console.log(JSON.stringify({ url, shots: made }));
    ws.close(); p.kill(); setTimeout(() => { try { fs.rmSync(prof, { recursive: true, force: true }); } catch (e) {} process.exit(0); }, 800);
    return;
  }
  // 끝까지 한 번 내려갔다 올라와 늦게 뜨는 그림을 불러 둔다
  const docH0 = await ev('document.documentElement.scrollHeight'); for (let y = 0; y < Math.min(docH0, 20000); y += vh) { await ev(`scrollTo(0, ${y})`); await sleep(350); } await ev('scrollTo(0,0)'); await sleep(600);
  const data = JSON.parse(await ev(MEASURE)); fs.writeFileSync(path.join(outdir, name + '.json'), JSON.stringify(data));
  const pages = Math.min(Math.ceil(data.docH / vh), 14);
  for (let i = 0; i < pages; i++) { await ev(`scrollTo(0, ${i * vh})`); await sleep(500); const shot = await send('Page.captureScreenshot', SHOTFMT); fs.writeFileSync(path.join(outdir, `${name}_${i + 1}.${EXT}`), Buffer.from(shot.data, 'base64')); }
  console.log(JSON.stringify({ title: data.title, url: data.url, docH: data.docH, items: data.items.length, shots: pages }));
  ws.close(); p.kill(); setTimeout(() => { try { fs.rmSync(prof, { recursive: true, force: true }); } catch (e) {} process.exit(0); }, 800);
})().catch((e) => { console.log('실패: ' + e.message); try { p.kill(); } catch (x) {} process.exit(1); });
