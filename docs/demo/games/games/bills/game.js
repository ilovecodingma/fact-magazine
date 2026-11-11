/* 청구서 피하기 — 세 줄로 떨어지는 「청구서」를 피하고 「절약」 동전을 모으는 한 손 게임.
   조작: 화면 왼쪽 누르기 = 왼쪽 줄로, 오른쪽 누르기 = 오른쪽 줄로 (PC: ← → 또는 A D). 목숨 3개, 시간이 갈수록 빨라진다.
   정적 파일 하나, 바깥 라이브러리·이미지·소리 없음. 최고 기록은 이 브라우저에만 저장. 시험용 주소 매개변수: ?bot=1 */
(function () {
  'use strict';
  var cv = document.getElementById('g'), ctx = cv.getContext('2d'), W = 360, H = 540, SC = 2;
  cv.width = W * SC; cv.height = H * SC; ctx.scale(SC, SC);
  var BOT = new URLSearchParams(location.search).get('bot') === '1';
  var SERIF = "'Noto Serif KR','Nanum Myeongjo','Batang',serif", SANS = "system-ui,'Malgun Gothic',sans-serif";
  var INK = '#111', RED = '#a11a12', GREEN = '#0b5d2f', PAPER = '#f7f5ee';
  var LANES = [W * 0.2, W * 0.5, W * 0.8], PY = 450;
  var best = 0; try { best = +localStorage.getItem('bills_best') || 0; } catch (e) {}
  var endAt = 0, mode = 'title', t = 0, score = 0, lives = 3, lane = 1, tx = LANES[1], px = LANES[1], items = [], spawn = 0, inv = 0, combo = 0, botT = 0;
  var BILLS = ['세금', '이자', '관리비', '통신비', '카드값'];

  function start() { mode = 'play'; t = 0; score = 0; lives = 3; lane = 1; px = tx = LANES[1]; items = []; spawn = 0.4; inv = 0; combo = 0; }
  function go(d) { if (mode === 'title') { start(); return; } if (mode === 'over') { if (performance.now() - endAt > 700) start(); return; }   // 끝난 직후 연타로 바로 다시 시작되지 않게
    lane = Math.max(0, Math.min(2, lane + d)); tx = LANES[lane]; }
  cv.addEventListener('pointerdown', function (e) { var r = cv.getBoundingClientRect(); go((e.clientX - r.left) / r.width < 0.5 ? -1 : 1); });
  window.addEventListener('keydown', function (e) {
    var k = e.key.toLowerCase();
    if (k === 'arrowleft' || k === 'a') { go(-1); e.preventDefault(); } else if (k === 'arrowright' || k === 'd') { go(1); e.preventDefault(); } else if (k === ' ' || k === 'enter') { if (mode === 'title' || (mode === 'over' && performance.now() - endAt > 700)) start(); e.preventDefault(); }
  });

  function step(dt) {
    t += dt; if (inv > 0) inv -= dt;
    px += (tx - px) * Math.min(1, dt * 14);
    var speed = 150 + t * 5;                                   // 초당 떨어지는 속도(px) — 갈수록 빨라진다
    spawn -= dt;
    if (spawn <= 0) {
      spawn = Math.max(0.28, 0.85 - t / 90);
      var n = t > 20 && Math.random() < 0.4 ? 2 : 1, used = [], i;   // 20초가 지나면 가끔 두 줄에 동시에
      for (i = 0; i < n; i++) { var l; do { l = Math.floor(Math.random() * 3); } while (used.indexOf(l) >= 0); used.push(l);
        items.push({ l: l, y: -30, coin: Math.random() < 0.38, txt: BILLS[Math.floor(Math.random() * BILLS.length)] }); }
      if (used.length === 3) used.pop();
    }
    for (var j = items.length - 1; j >= 0; j--) {
      var it = items[j]; it.y += speed * dt;
      if (Math.abs(it.y - PY) < 28 && Math.abs(LANES[it.l] - px) < 30) {
        if (it.coin) { combo++; score += 10 + Math.min(20, combo); items.splice(j, 1); continue; }
        else if (inv <= 0) { lives--; inv = 1.0; combo = 0; items.splice(j, 1); if (lives <= 0) return end(); continue; }
      }
      if (it.y > H + 30) { if (it.coin) combo = 0; items.splice(j, 1); }
    }
    score += 0;   // 점수는 동전으로만 오른다(버틴 시간은 화면에 따로 보인다)
  }
  function end() { mode = 'over'; endAt = performance.now(); if (score > best) { best = score; try { localStorage.setItem('bills_best', String(best)); } catch (e) {} } }

  function text(s, x, y, size, color, align, font, weight) { ctx.font = (weight || 700) + ' ' + size + 'px ' + (font || SERIF); ctx.fillStyle = color; ctx.textAlign = align || 'center'; ctx.textBaseline = 'middle'; ctx.fillText(s, x, y); }
  function draw() {
    ctx.fillStyle = PAPER; ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = '#d8d3c4'; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(W / 3, 0); ctx.lineTo(W / 3, H); ctx.moveTo(W * 2 / 3, 0); ctx.lineTo(W * 2 / 3, H); ctx.stroke();
    if (mode === 'title') return title();
    var i;
    for (i = 0; i < items.length; i++) {
      var it = items[i], x = LANES[it.l];
      if (it.coin) { ctx.fillStyle = '#f2c94c'; ctx.strokeStyle = INK; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, it.y, 17, 0, 6.283); ctx.fill(); ctx.stroke(); text('절약', x, it.y + 1, 12, INK, 'center', SERIF, 900); }
      else { ctx.fillStyle = '#fff'; ctx.strokeStyle = RED; ctx.lineWidth = 2.5; ctx.fillRect(x - 28, it.y - 18, 56, 36); ctx.strokeRect(x - 28, it.y - 18, 56, 36); text(it.txt, x, it.y + 1, 13, RED, 'center', SERIF, 900); }
    }
    ctx.globalAlpha = inv > 0 && Math.floor(inv * 14) % 2 ? 0.4 : 1;
    ctx.fillStyle = INK; ctx.beginPath(); ctx.arc(px, PY, 20, 0, 6.283); ctx.fill(); text('나', px, PY + 1, 17, '#fff', 'center', SERIF, 900); ctx.globalAlpha = 1;
    ctx.fillStyle = 'rgba(247,245,238,.9)'; ctx.fillRect(0, 0, W, 38);
    text('절약 ' + score, 12, 19, 16, INK, 'left', SANS, 800); text(Math.floor(t) + '초', W / 2, 19, 14, '#555', 'center', SANS, 700); text('♥'.repeat(Math.max(0, lives)) + '♡'.repeat(3 - Math.max(0, lives)), W - 12, 19, 16, RED, 'right', SANS, 700);
    if (mode === 'over') over();
  }
  function title() {
    ctx.strokeStyle = INK; ctx.lineWidth = 3; ctx.strokeRect(14, 14, W - 28, H - 28); ctx.lineWidth = 1; ctx.strokeRect(19, 19, W - 38, H - 38);
    text('청구서 피하기', W / 2, 110, 34, INK, 'center', SERIF, 900);
    text('떨어지는 청구서를 피하고 절약 동전을 모으세요', W / 2, 160, 13.5, INK, 'center', SANS, 600);
    var L = ['화면 왼쪽을 누르면 한 줄 왼쪽으로', '오른쪽을 누르면 한 줄 오른쪽으로 (PC: ← →)', '청구서에 닿으면 목숨이 하나 줄어듭니다', '목숨 3개, 갈수록 빨라집니다'];
    for (var i = 0; i < L.length; i++) text(L[i], W / 2, 215 + i * 26, 13, '#333', 'center', SANS, 600);
    text(best ? '최고 기록 ' + best + '점' : '아직 기록이 없습니다', W / 2, 345, 15, RED, 'center', SANS, 700);
    ctx.fillStyle = INK; ctx.fillRect(W / 2 - 80, 400, 160, 48); text('시작', W / 2, 425, 18, '#fff', 'center', SANS, 800);
    text('화면을 누르거나 스페이스', W / 2, 476, 12, '#666', 'center', SANS, 500);
  }
  function over() {
    ctx.fillStyle = 'rgba(247,245,238,.94)'; ctx.fillRect(0, 38, W, H); ctx.strokeStyle = INK; ctx.lineWidth = 3; ctx.strokeRect(14, 60, W - 28, H - 90);
    text('청구서에 묻혔습니다', W / 2, 130, 26, RED, 'center', SERIF, 900);
    text('절약 ' + score + '점', W / 2, 205, 36, INK, 'center', SERIF, 900); text('버틴 시간 ' + Math.floor(t) + '초', W / 2, 250, 15, '#333', 'center', SANS, 600);
    text('최고 기록 ' + best + '점', W / 2, 285, 15, RED, 'center', SANS, 700);
    ctx.fillStyle = INK; ctx.fillRect(W / 2 - 80, 340, 160, 48); text('다시 하기', W / 2, 365, 18, '#fff', 'center', SANS, 800);
    text('화면을 누르거나 스페이스', W / 2, 415, 12, '#666', 'center', SANS, 500);
  }

  function bot() {                                             // 시험용: 가장 가까운 청구서를 피하고 동전 쪽으로
    var danger = [0, 0, 0], want = [0, 0, 0], i;
    for (i = 0; i < items.length; i++) { var it = items[i]; if (it.y > PY - 190 && it.y < PY + 30) { if (it.coin) want[it.l] += 1; else danger[it.l] += 1; } }
    var best = lane, bs = -9; for (var l = 0; l < 3; l++) { var s = want[l] * 2 - danger[l] * 6 - Math.abs(l - lane) * 0.7; if (s > bs) { bs = s; best = l; } }
    if (best < lane) go(-1); else if (best > lane) go(1);
  }
  var last = 0;
  function frame(now) {
    var dt = Math.min(0.05, (now - last) / 1000 || 0.016); last = now;
    if (mode === 'play') { if (BOT) { botT -= dt; if (botT <= 0) { botT = 0.12; bot(); } } step(dt); }
    else if (BOT) { botT -= dt; if (botT <= -1.2) { botT = 0; start(); } }
    draw(); requestAnimationFrame(frame);
  }
  window.__bills = function () { return { mode: mode, t: Math.round(t * 10) / 10, score: score, lives: lives, lane: lane }; };
  requestAnimationFrame(frame);
})();
