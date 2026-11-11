/* 확인 도장 판정 — 소식과 출처를 보고 「확인됨」 / 「아직 확인 안 됨」 도장을 빨리 찍는 반응 게임.
   규칙(화면에도 적혀 있음): 출처가 공식 기관 자료이고 소식의 숫자·날짜가 그 자료에 있다고 하면 확인됨, 출처가 지인·익명·캡처·「카더라」면 아직 확인 안 됨.
   소식은 전부 지어낸 예시(가상의 시·기관)라 실제 사실과 무관하다. 정적 파일 하나, 바깥 라이브러리·이미지·소리 없음. 최고 기록은 이 브라우저에만 저장.
   조작: 화면 왼쪽 누르기 = 확인됨, 오른쪽 누르기 = 아직 확인 안 됨 (PC: ← → 또는 A D). 시험용 주소 매개변수: ?bot=1 */
(function () {
  'use strict';
  var cv = document.getElementById('g'), ctx = cv.getContext('2d'), W = 360, H = 540, SC = 2;
  cv.width = W * SC; cv.height = H * SC; ctx.scale(SC, SC);
  var BOT = new URLSearchParams(location.search).get('bot') === '1';
  var SERIF = "'Noto Serif KR','Nanum Myeongjo','Batang',serif", SANS = "system-ui,'Malgun Gothic',sans-serif";
  var INK = '#111', RED = '#a11a12', GREEN = '#0b5d2f', PAPER = '#f7f5ee';
  var GOOD = ['시청 공고문', '교육청 보도자료', '구청 홈페이지 공지', '고용센터 안내문', '시 의회 회의록', '공단 누리집 안내'];
  var BAD = ['지인에게 들은 말', '익명 커뮤니티 글', '캡처 이미지(출처 없음)', '「카더라」 단체방 전달', '출처를 밝히지 않은 영상', '친구의 친구 이야기'];
  var CLAIMS = [
    'A시 청년 월세 지원, 월 20만 원 한도', 'B구 출산 축하금 100만 원 지급', 'C시 버스 환승 할인 12월 1일부터', 'D교육청 방과후 신청 기간 3월 4일까지',
    'E시 소상공인 대출 이자 지원 1.5%p', 'F구 노인 일자리 5백 명 모집', 'G시 전기요금 지원 가구당 3만 원', 'H공단 연금 안내문 발송 10월 말',
    'I시 주차요금 인하 시간당 600원', 'J구 도서관 연장 운영 밤 10시까지', 'K시 학원비 세액공제 한도 상향', 'L구 이사비 지원 최대 50만 원'];
  var best = 0; try { best = +localStorage.getItem('verdict_best') || 0; } catch (e) {}
  var endAt = 0, mode = 'title', t = 0, score = 0, streak = 0, lives = 3, card = null, flash = 0, flashOk = true, pending = 0, botT = 0;
  var LIMIT = 45;

  function next() {
    var ok = Math.random() < 0.5;
    card = { ok: ok, claim: CLAIMS[Math.floor(Math.random() * CLAIMS.length)], src: (ok ? GOOD : BAD)[Math.floor(Math.random() * 6)], age: 0 };
  }
  function start() { mode = 'play'; t = 0; score = 0; streak = 0; lives = 3; flash = 0; next(); }
  function answer(sayOk) {
    if (mode === 'title') { start(); return; }
    if (mode === 'over') { if (performance.now() - endAt > 700) start(); return; }   // 끝난 직후 연타로 바로 다시 시작되지 않게
    if (!card) return;
    var right = sayOk === card.ok;
    if (right) { streak++; score += 1 + Math.floor(streak / 5); } else { streak = 0; lives--; }
    flash = 0.25; flashOk = right;
    if (lives <= 0) return end();
    next();
  }
  function end() { mode = 'over'; endAt = performance.now(); if (score > best) { best = score; try { localStorage.setItem('verdict_best', String(best)); } catch (e) {} } }
  cv.addEventListener('pointerdown', function (e) { var r = cv.getBoundingClientRect(); answer((e.clientX - r.left) / r.width < 0.5); });
  window.addEventListener('keydown', function (e) {
    var k = e.key.toLowerCase();
    if (k === 'arrowleft' || k === 'a') { answer(true); e.preventDefault(); }
    else if (k === 'arrowright' || k === 'd') { answer(false); e.preventDefault(); }
    else if (k === ' ' || k === 'enter') { if (mode === 'title' || (mode === 'over' && performance.now() - endAt > 700)) start(); e.preventDefault(); }
  });

  function text(s, x, y, size, color, align, font, weight) { ctx.font = (weight || 700) + ' ' + size + 'px ' + (font || SERIF); ctx.fillStyle = color; ctx.textAlign = align || 'center'; ctx.textBaseline = 'middle'; ctx.fillText(s, x, y); }
  function wrap(s, x, y, maxw, size, lh, color) {   // 글자 단위 줄바꿈(한글)
    ctx.font = '800 ' + size + 'px ' + SERIF; var line = '', ly = y;
    for (var i = 0; i < s.length; i++) { var test = line + s[i]; if (ctx.measureText(test).width > maxw && line) { text(line, x, ly, size, color, 'center', SERIF, 800); line = s[i]; ly += lh; } else line = test; }
    text(line, x, ly, size, color, 'center', SERIF, 800); return ly;
  }
  function draw() {
    ctx.fillStyle = PAPER; ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = '#e4e0d2'; ctx.lineWidth = 1; ctx.beginPath(); for (var i = 40; i < H; i += 40) { ctx.moveTo(0, i); ctx.lineTo(W, i); } ctx.stroke();
    if (mode === 'title') return title();
    // 머리 줄
    ctx.fillStyle = '#d9d4c4'; ctx.fillRect(0, 0, W, 6); ctx.fillStyle = INK; ctx.fillRect(0, 0, W * Math.max(0, (LIMIT - t)) / LIMIT, 6);
    text('점수 ' + score, 12, 24, 15, INK, 'left', SANS, 800); text('연속 ' + streak, W / 2, 24, 13, '#555', 'center', SANS, 700); text('♥'.repeat(Math.max(0, lives)) + '♡'.repeat(3 - Math.max(0, lives)), W - 12, 24, 16, RED, 'right', SANS, 700);
    if (mode === 'over') return over();
    // 기사 카드
    var y0 = 90; ctx.fillStyle = '#fff'; ctx.strokeStyle = flash > 0 ? (flashOk ? GREEN : RED) : INK; ctx.lineWidth = flash > 0 ? 4 : 2; ctx.fillRect(24, y0, W - 48, 210); ctx.strokeRect(24, y0, W - 48, 210);
    text('소식', 40, y0 + 22, 12, '#777', 'left', SANS, 700);
    var ly = wrap(card.claim, W / 2, y0 + 80, W - 100, 21, 30, INK);
    ctx.strokeStyle = '#ddd'; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(40, y0 + 150); ctx.lineTo(W - 40, y0 + 150); ctx.stroke();
    text('출처', 40, y0 + 172, 12, '#777', 'left', SANS, 700); text(card.src, W / 2, y0 + 190, 16, card.ok ? '#1d3d6b' : '#7a3a12', 'center', SANS, 700);
    // 도장 버튼
    ctx.fillStyle = '#fff'; ctx.strokeStyle = GREEN; ctx.lineWidth = 3; ctx.fillRect(18, 330, 156, 110); ctx.strokeRect(18, 330, 156, 110);
    text('확인됨', 96, 372, 24, GREEN, 'center', SERIF, 900); text('◀ 왼쪽', 96, 410, 12, '#555', 'center', SANS, 600);
    ctx.fillStyle = '#fff'; ctx.strokeStyle = RED; ctx.fillRect(186, 330, 156, 110); ctx.strokeRect(186, 330, 156, 110);
    text('아직 확인 안 됨', 264, 372, 17, RED, 'center', SERIF, 900); text('오른쪽 ▶', 264, 410, 12, '#555', 'center', SANS, 600);
    text('출처가 공식 기관이면 확인됨 · 지인·익명·캡처면 아직 확인 안 됨', W / 2, 470, 11.5, '#555', 'center', SANS, 600);
    text('소식은 모두 지어낸 예시입니다', W / 2, 492, 11, '#888', 'center', SANS, 500);
  }
  function title() {
    ctx.strokeStyle = INK; ctx.lineWidth = 3; ctx.strokeRect(14, 14, W - 28, H - 28); ctx.lineWidth = 1; ctx.strokeRect(19, 19, W - 38, H - 38);
    text('확인 도장 판정', W / 2, 110, 34, INK, 'center', SERIF, 900);
    text('소식과 출처를 보고 도장을 찍으세요', W / 2, 160, 14, INK, 'center', SANS, 600);
    var L = ['출처가 공식 기관(시청·교육청·공단)이면', '「확인됨」 — 화면 왼쪽을 누르세요', '출처가 지인·익명·캡처·「카더라」면', '「아직 확인 안 됨」 — 오른쪽을 누르세요', '45초 동안 최대한 많이, 3번 틀리면 끝납니다'];
    for (var i = 0; i < L.length; i++) text(L[i], W / 2, 215 + i * 26, 13, i === 1 ? GREEN : i === 3 ? RED : '#333', 'center', SANS, 600);
    text(best ? '최고 기록 ' + best + '점' : '아직 기록이 없습니다', W / 2, 365, 15, RED, 'center', SANS, 700);
    ctx.fillStyle = INK; ctx.fillRect(W / 2 - 80, 405, 160, 48); text('시작', W / 2, 430, 18, '#fff', 'center', SANS, 800);
    text('화면을 누르거나 스페이스', W / 2, 480, 12, '#666', 'center', SANS, 500);
  }
  function over() {
    ctx.fillStyle = 'rgba(247,245,238,.94)'; ctx.fillRect(0, 40, W, H); ctx.strokeStyle = INK; ctx.lineWidth = 3; ctx.strokeRect(14, 60, W - 28, H - 90);
    text(lives <= 0 ? '도장이 세 번 틀렸습니다' : '시간이 끝났습니다', W / 2, 130, 26, lives <= 0 ? RED : GREEN, 'center', SERIF, 900);
    text(score + '점', W / 2, 205, 44, INK, 'center', SERIF, 900);
    text('최고 기록 ' + best + '점', W / 2, 265, 15, RED, 'center', SANS, 700);
    ctx.fillStyle = INK; ctx.fillRect(W / 2 - 80, 340, 160, 48); text('다시 하기', W / 2, 365, 18, '#fff', 'center', SANS, 800);
    text('화면을 누르거나 스페이스', W / 2, 415, 12, '#666', 'center', SANS, 500);
  }

  var last = 0;
  function frame(now) {
    var dt = Math.min(0.05, (now - last) / 1000 || 0.016); last = now;
    if (mode === 'play') {
      t += dt; if (flash > 0) flash -= dt;
      if (BOT) { botT -= dt; if (botT <= 0) { botT = 0.7; answer(Math.random() < 0.9 ? card.ok : !card.ok); } }   // 시험용: 90% 맞히는 봇
      if (t >= LIMIT) end();
    } else if (BOT && mode !== 'play') { botT -= dt; if (botT <= -1.5) { botT = 0; start(); } }
    draw(); requestAnimationFrame(frame);
  }
  window.__verdict = function () { return { mode: mode, t: Math.round(t * 10) / 10, score: score, lives: lives, streak: streak, ok: card && card.ok }; };
  requestAnimationFrame(frame);
})();
