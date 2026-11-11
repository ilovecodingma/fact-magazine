/* 뜬소문 막기 — 몰려오는 「뜬소문」을 「확인 도장」으로 막으며 버티는 게임 (뱀서류).
   정적 파일 하나(canvas, 바깥 라이브러리·이미지·소리 없음). 최고 기록은 이 브라우저(localStorage)에만 저장된다.
   조작: 화면 끌기(터치·마우스) 또는 방향키·WASD. 도장은 가까운 뜬소문에게 저절로 날아간다.
   시험용 주소 매개변수: ?bot=1 (스스로 플레이) ?stop=levelup|over|win|play&t=60 (그 장면까지 빨리 감아 멈춤) */
(function () {
  'use strict';
  var cv = document.getElementById('g'), ctx = cv.getContext('2d');
  var W = 360, H = 540, SC = 2;           // 화면 논리 크기, 그림 배율
  cv.width = W * SC; cv.height = H * SC; ctx.scale(SC, SC);
  var Q = new URLSearchParams(location.search), BOT = Q.get('bot') === '1', STOP = Q.get('stop') || '';
  var SERIF = "'Noto Serif KR','Nanum Myeongjo','Batang',serif", SANS = "system-ui,'Malgun Gothic',sans-serif";
  var INK = '#111', RED = '#a11a12', BLUE = '#0b3d91', PAPER = '#f7f5ee', LINE = '#e4e0d2';
  var WIN_AT = 300;                        // 5분을 버티면 끝

  var best = 0;
  try { best = +localStorage.getItem('rumor_best') || 0; } catch (e) {}

  /* ---------- 강화 목록 ---------- */
  var UPS = [
    { id: 'rate', name: '연사', desc: '도장이 15% 더 빨리 나갑니다', max: 6 },
    { id: 'multi', name: '도장 +1', desc: '한 번에 도장이 하나 더 나갑니다', max: 4 },
    { id: 'big', name: '큰 도장', desc: '도장이 커지고 한 개 더 뚫습니다', max: 5 },
    { id: 'speed', name: '빠른 걸음', desc: '이동이 12% 빨라집니다', max: 4 },
    { id: 'magnet', name: '자석', desc: '증거 조각을 더 멀리서 모읍니다', max: 4 },
    { id: 'hp', name: '튼튼한 몸', desc: '최대 체력 +20, 체력 25 회복', max: 5 },
    { id: 'orb', name: '회전 각주', desc: '몸 둘레를 도는 각주가 하나 늘어납니다', max: 5 },
    { id: 'nova', name: '정정 보도', desc: '일정 시간마다 둘레의 뜬소문을 한꺼번에 정정합니다', max: 4 }   // 판 2 에서 추가
  ];

  /* ---------- 상태 ---------- */
  var mode, t, px, py, hp, maxhp, lv, xp, need, kills, inv, cd, spin, fl, shake;
  var nt, ring, E, P, G, FX, up, offer, keys = {}, joy = null, camx, camy, acc = 0, last = 0, started = false, doneStop = false;

  function reset() {
    mode = 'play'; t = 0; px = 0; py = 0; hp = maxhp = 100; lv = 1; xp = 0; need = need_for(1); kills = 0; inv = 0; cd = 0.3; spin = 0; shake = 0;
    E = []; P = []; G = []; FX = []; offer = null; camx = 0; camy = 0; fl = { spawn: 1, boss1: false, boss2: false, boss3: false };
    nt = 10; ring = 0;
    up = {}; UPS.forEach(function (u) { up[u.id] = 0; });
  }
  function need_for(l) { return 4 + l * 3; }
  mode = 'title'; reset(); mode = 'title';

  /* ---------- 입력 ---------- */
  function pos(e) { var r = cv.getBoundingClientRect(); return { x: (e.clientX - r.left) / r.width * W, y: (e.clientY - r.top) / r.height * H }; }
  cv.addEventListener('pointerdown', function (e) {
    var p = pos(e); try { cv.setPointerCapture(e.pointerId); } catch (x) {}
    if (mode === 'title') { reset(); return; }
    if (mode === 'over' || mode === 'win') { if (p.y > H * 0.66) reset(); return; }
    if (mode === 'levelup') { pick(Math.floor((p.y - 100) / 134)); return; }
    joy = { id: e.pointerId, x0: p.x, y0: p.y, x: p.x, y: p.y };
  });
  cv.addEventListener('pointermove', function (e) { if (joy && joy.id === e.pointerId) { var p = pos(e); joy.x = p.x; joy.y = p.y; } });
  function endp(e) { if (joy && joy.id === e.pointerId) joy = null; }
  cv.addEventListener('pointerup', endp); cv.addEventListener('pointercancel', endp);
  window.addEventListener('keydown', function (e) {
    var k = e.key.toLowerCase(); keys[k] = true;
    if (['arrowup', 'arrowdown', 'arrowleft', 'arrowright', ' '].indexOf(k) >= 0) e.preventDefault();
    if (mode === 'title' && (k === ' ' || k === 'enter')) reset();
    else if ((mode === 'over' || mode === 'win') && (k === ' ' || k === 'enter')) reset();
    else if (mode === 'levelup' && '123'.indexOf(k) >= 0 && k) pick(+k - 1);
  });
  window.addEventListener('keyup', function (e) { keys[e.key.toLowerCase()] = false; });

  /* ---------- 강화 고르기 ---------- */
  function openLevelUp() {
    var pool = UPS.filter(function (u) { return up[u.id] < u.max; }), out = [];
    while (out.length < 3 && pool.length) out.push(pool.splice(Math.floor(Math.random() * pool.length), 1)[0]);
    if (!out.length) { hp = Math.min(maxhp, hp + 30); return; }   // 모두 최대면 체력만 회복
    offer = out; mode = 'levelup';
  }
  function pick(i) {
    if (!offer || i < 0 || i >= offer.length) return;
    var u = offer[i]; up[u.id]++;
    if (u.id === 'hp') { maxhp += 20; hp = Math.min(maxhp, hp + 25); }
    offer = null; mode = 'play'; joy = null;
  }

  /* ---------- 적 ---------- */
  var TYPES = {
    a: { txt: '카더라', r: 12, hp: 3, sp: 42, dmg: 8, xp: 1 },
    b: { txt: '속보?', r: 10, hp: 2, sp: 78, dmg: 6, xp: 1 },
    c: { txt: '충격', r: 17, hp: 14, sp: 28, dmg: 14, xp: 4 },
    d: { txt: '대형 오보', r: 32, hp: 160, sp: 26, dmg: 24, xp: 30 }
  };
  function spawn(k) {
    var T = TYPES[k], a = Math.random() * 6.283, d = 330, s = 1 + t / 140;
    E.push({ k: k, x: px + Math.cos(a) * d, y: py + Math.sin(a) * d, hp: T.hp * s * (k === 'd' ? 1 + t / 100 : 1), T: T, hit: 0, orb: 0 });
  }
  function dist2(ax, ay, bx, by) { var dx = ax - bx, dy = ay - by; return dx * dx + dy * dy; }

  /* ---------- 갱신 ---------- */
  function inputVec() {
    var x = 0, y = 0;
    if (BOT) return botVec();
    if (keys.arrowleft || keys.a) x -= 1; if (keys.arrowright || keys.d) x += 1;
    if (keys.arrowup || keys.w) y -= 1; if (keys.arrowdown || keys.s) y += 1;
    if (joy) { var dx = joy.x - joy.x0, dy = joy.y - joy.y0, m = Math.hypot(dx, dy); if (m > 6) { x = dx / Math.max(m, 40); y = dy / Math.max(m, 40); } }
    var l = Math.hypot(x, y); if (l > 1) { x /= l; y /= l; }
    return { x: x, y: y };
  }
  function botVec() {                       // 시험용: 가까운 적에게서 멀어지고 증거 조각 쪽으로
    var x = 0, y = 0, i, e, d, w;
    for (i = 0; i < E.length; i++) { e = E[i]; d = Math.sqrt(dist2(px, py, e.x, e.y)); if (d < 140 && d > 0.1) { w = (140 - d) / 140; w *= w * 3; x += (px - e.x) / d * w; y += (py - e.y) / d * w; } }
    var bd = 160, bg = null; for (i = 0; i < G.length; i++) { d = Math.sqrt(dist2(px, py, G[i].x, G[i].y)); if (d < bd) { bd = d; bg = G[i]; } }
    if (bg && (x * x + y * y) < 0.5) { x += (bg.x - px) / bd * 0.8; y += (bg.y - py) / bd * 0.8; }
    var l = Math.hypot(x, y); if (l > 1) { x /= l; y /= l; }
    return { x: x, y: y };
  }

  function step(dt) {
    if (mode !== 'play') return;
    t += dt; spin += dt * 2.2; if (inv > 0) inv -= dt; if (shake > 0) shake -= dt;
    var v = inputVec(), sp = 120 * (1 + 0.12 * up.speed);
    px += v.x * sp * dt; py += v.y * sp * dt;
    // 적 등장: 시간이 갈수록 빨라지고 한 번에 더 나온다
    fl.spawn -= dt;
    if (fl.spawn <= 0 && E.length < 260) {
      fl.spawn = Math.max(0.12, 0.9 - t / 260); var n = 1 + Math.floor(t / 40), i;
      for (i = 0; i < n; i++) spawn(t > 60 && Math.random() < 0.18 ? 'c' : (t > 25 && Math.random() < 0.35 ? 'b' : 'a'));
    }
    if (t > 90 && !fl.boss1) { fl.boss1 = true; spawn('d'); }
    if (t > 190 && !fl.boss2) { fl.boss2 = true; spawn('d'); spawn('d'); }
    if (t > 270 && !fl.boss3) { fl.boss3 = true; spawn('d'); spawn('d'); spawn('d'); }
    // 도장 발사
    cd -= dt;
    if (cd <= 0) {
      var tg = null, bd = 420 * 420, j, e2;
      for (j = 0; j < E.length; j++) { e2 = E[j]; var dd = dist2(px, py, e2.x, e2.y); if (dd < bd) { bd = dd; tg = e2; } }
      if (tg) {
        var base = Math.atan2(tg.y - py, tg.x - px), n2 = 1 + up.multi, k;
        for (k = 0; k < n2; k++) {
          var ang = base + (n2 > 1 ? (k - (n2 - 1) / 2) * 0.2 : 0);
          P.push({ x: px, y: py, vx: Math.cos(ang) * 300, vy: Math.sin(ang) * 300, r: 6 + up.big * 1.6, pierce: 1 + up.big, life: 1.5, dmg: 2, hit: [] });
        }
        cd = 0.8 * Math.pow(0.85, up.rate);
      } else cd = 0.1;
    }
    var i2, p, e;
    for (i2 = P.length - 1; i2 >= 0; i2--) {
      p = P[i2]; p.x += p.vx * dt; p.y += p.vy * dt; p.life -= dt;
      for (var q = 0; q < E.length && p.life > 0; q++) {
        e = E[q]; if (p.hit.indexOf(e) >= 0) continue;
        if (dist2(p.x, p.y, e.x, e.y) < (p.r + e.T.r) * (p.r + e.T.r)) { hurt(e, p.dmg); p.hit.push(e); if (--p.pierce <= 0) p.life = 0; }
      }
      if (p.life <= 0) P.splice(i2, 1);
    }
    // 정정 보도: 레벨이 높을수록 더 자주, 둘레의 뜬소문에 한꺼번에 피해
    if (up.nova) {
      nt -= dt; if (ring > 0) ring -= dt;
      if (nt <= 0) { nt = Math.max(8, 24 - 4 * up.nova); ring = 0.45; for (var nz = E.length - 1; nz >= 0; nz--) { if (dist2(px, py, E[nz].x, E[nz].y) < 150 * 150) hurt(E[nz], 8); } }
    }
    // 회전 각주
    var no = up.orb;
    for (var o = 0; o < no; o++) {
      var oa = spin + o * 6.283 / no, ox = px + Math.cos(oa) * 52, oy = py + Math.sin(oa) * 52;
      for (var r = 0; r < E.length; r++) { e = E[r]; if (e.orb <= 0 && dist2(ox, oy, e.x, e.y) < (9 + e.T.r) * (9 + e.T.r)) { hurt(e, 1.6); e.orb = 0.35; } }
    }
    // 적 이동·접촉
    for (var m = E.length - 1; m >= 0; m--) {
      e = E[m]; if (e.hit > 0) e.hit -= dt; if (e.orb > 0) e.orb -= dt;
      var dx = px - e.x, dy = py - e.y, dl = Math.hypot(dx, dy) || 1;
      var sm = 1 + t / 330; e.x += dx / dl * e.T.sp * sm * dt; e.y += dy / dl * e.T.sp * sm * dt;
      for (var z = m + 1; z < E.length && z < m + 6; z++) { var f = E[z], ex = e.x - f.x, ey = e.y - f.y, el = Math.hypot(ex, ey), rr = e.T.r + f.T.r; if (el > 0 && el < rr) { var push = (rr - el) * 0.3; e.x += ex / el * push; e.y += ey / el * push; f.x -= ex / el * push; f.y -= ey / el * push; } }
      if (dl < e.T.r + 11 && inv <= 0) { hp -= Math.round(e.T.dmg * (1 + t / 260)); inv = 0.6; shake = 0.15; if (hp <= 0) { finish(false); return; } }
    }
    // 증거 조각
    var mg = 50 * (1 + 0.4 * up.magnet);
    for (var g = G.length - 1; g >= 0; g--) {
      var ge = G[g], gd = Math.sqrt(dist2(px, py, ge.x, ge.y));
      if (gd < mg || ge.pull) { ge.pull = true; ge.x += (px - ge.x) / (gd || 1) * 230 * dt; ge.y += (py - ge.y) / (gd || 1) * 230 * dt; }
      if (gd < 12) { xp += ge.v; G.splice(g, 1); while (xp >= need) { xp -= need; lv++; need = need_for(lv); openLevelUp(); if (mode === 'levelup') break; } }
    }
    for (var s = FX.length - 1; s >= 0; s--) { FX[s].life -= dt; FX[s].x += FX[s].vx * dt; FX[s].y += FX[s].vy * dt; if (FX[s].life <= 0) FX.splice(s, 1); }
    if (t >= WIN_AT) finish(true);
  }
  function hurt(e, d) {
    e.hp -= d; e.hit = 0.08;
    if (e.hp <= 0) {
      var i = E.indexOf(e); if (i >= 0) E.splice(i, 1); kills++;
      G.push({ x: e.x, y: e.y, v: e.T.xp, pull: false });
      for (var k = 0; k < 4; k++) FX.push({ x: e.x, y: e.y, vx: (Math.random() - 0.5) * 120, vy: (Math.random() - 0.5) * 120, life: 0.35 });
    }
  }
  function finish(win) {
    mode = win ? 'win' : 'over';
    var sc = Math.floor(t); if (sc > best) { best = sc; try { localStorage.setItem('rumor_best', String(best)); } catch (e) {} }
  }

  /* ---------- 그리기 ---------- */
  function mmss(s) { s = Math.floor(s); return Math.floor(s / 60) + ':' + ('0' + (s % 60)).slice(-2); }
  function text(s, x, y, size, color, align, font, weight) { ctx.font = (weight || 700) + ' ' + size + 'px ' + (font || SERIF); ctx.fillStyle = color; ctx.textAlign = align || 'center'; ctx.textBaseline = 'middle'; ctx.fillText(s, x, y); }
  function draw() {
    camx += (px - camx) * 0.2; camy += (py - camy) * 0.2;
    var sx = shake > 0 ? (Math.random() - 0.5) * 5 : 0, sy = shake > 0 ? (Math.random() - 0.5) * 5 : 0;
    var ox = W / 2 - camx + sx, oy = H / 2 - camy + sy;
    ctx.fillStyle = PAPER; ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = LINE; ctx.lineWidth = 1; ctx.beginPath();           // 신문지 괘선 모양 바닥
    var gx = -(((ox % 40) + 40) % 40), gy = -(((oy % 40) + 40) % 40), i;
    for (i = gx; i < W; i += 40) { ctx.moveTo(i, 0); ctx.lineTo(i, H); }
    for (i = gy; i < H; i += 40) { ctx.moveTo(0, i); ctx.lineTo(W, i); }
    ctx.stroke();
    var j;
    for (j = 0; j < G.length; j++) { var g = G[j]; ctx.save(); ctx.translate(g.x + ox, g.y + oy); ctx.rotate(0.785); ctx.fillStyle = BLUE; ctx.fillRect(-3.5, -3.5, 7, 7); ctx.restore(); }
    for (j = 0; j < E.length; j++) {
      var e = E[j], r = e.T.r, X = e.x + ox, Y = e.y + oy; if (X < -50 || X > W + 50 || Y < -50 || Y > H + 50) continue;
      ctx.fillStyle = e.hit > 0 ? '#f6d6d2' : '#fff'; ctx.strokeStyle = RED; ctx.lineWidth = e.k === 'd' ? 3 : 1.6;
      ctx.beginPath(); ctx.rect(X - r * 1.5, Y - r * 0.75, r * 3, r * 1.5); ctx.fill(); ctx.stroke();
      text(e.T.txt, X, Y + 1, e.k === 'd' ? 14 : Math.max(9, r * 0.72), RED, 'center', SERIF, 800);
    }
    for (j = 0; j < P.length; j++) { var p = P[j]; ctx.strokeStyle = RED; ctx.fillStyle = 'rgba(161,26,18,.16)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(p.x + ox, p.y + oy, p.r, 0, 6.283); ctx.fill(); ctx.stroke(); text('확', p.x + ox, p.y + oy + 1, p.r * 1.25, RED, 'center', SERIF, 900); }
    for (j = 0; j < up.orb; j++) { var oa = spin + j * 6.283 / up.orb; ctx.fillStyle = INK; ctx.beginPath(); ctx.arc(px + Math.cos(oa) * 52 + ox, py + Math.sin(oa) * 52 + oy, 8, 0, 6.283); ctx.fill(); text('*', px + Math.cos(oa) * 52 + ox, py + Math.sin(oa) * 52 + oy + 3, 14, '#fff', 'center', SERIF, 900); }
    for (j = 0; j < FX.length; j++) { ctx.fillStyle = 'rgba(17,17,17,' + (FX[j].life * 2) + ')'; ctx.fillRect(FX[j].x + ox - 1.5, FX[j].y + oy - 1.5, 3, 3); }
    if (ring > 0) { ctx.strokeStyle = 'rgba(161,26,18,' + Math.min(1, ring * 2.2) + ')'; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(px + ox, py + oy, 150 * (1 - ring / 0.45) + 10, 0, 6.283); ctx.stroke(); text('정정', px + ox, py + oy - 150 * (1 - ring / 0.45) - 14, 16, RED, 'center', SERIF, 900); }
    // 플레이어(확인 도장)
    ctx.globalAlpha = inv > 0 && Math.floor(inv * 20) % 2 ? 0.45 : 1;
    ctx.fillStyle = INK; ctx.beginPath(); ctx.arc(px + ox, py + oy, 12, 0, 6.283); ctx.fill(); text('확', px + ox, py + oy + 1, 14, '#fff', 'center', SERIF, 900); ctx.globalAlpha = 1;
    // 조이스틱
    if (joy && mode === 'play') { ctx.strokeStyle = 'rgba(17,17,17,.35)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(joy.x0, joy.y0, 36, 0, 6.283); ctx.stroke(); var jl = Math.min(36, Math.hypot(joy.x - joy.x0, joy.y - joy.y0)), ja = Math.atan2(joy.y - joy.y0, joy.x - joy.x0); ctx.fillStyle = 'rgba(17,17,17,.5)'; ctx.beginPath(); ctx.arc(joy.x0 + Math.cos(ja) * jl, joy.y0 + Math.sin(ja) * jl, 14, 0, 6.283); ctx.fill(); }
    hud();
    if (mode === 'title') title(); else if (mode === 'levelup') levelup(); else if (mode === 'over' || mode === 'win') over();
  }
  function hud() {
    ctx.fillStyle = INK; ctx.fillRect(0, 0, W, 5); ctx.fillStyle = '#d9d4c4'; ctx.fillRect(0, 0, W, 5);
    ctx.fillStyle = BLUE; ctx.fillRect(0, 0, W * Math.min(1, xp / need), 5);
    text(mmss(t) + ' / 5:00', W / 2, 22, 15, INK, 'center', SANS, 700);
    text('레벨 ' + lv, 10, 22, 13, INK, 'left', SANS, 700);
    text('막은 소문 ' + kills, W - 10, 22, 13, INK, 'right', SANS, 700);
    ctx.fillStyle = '#d9d4c4'; ctx.fillRect(10, 34, 110, 7); ctx.fillStyle = hp / maxhp > 0.3 ? '#0b5d2f' : RED; ctx.fillRect(10, 34, 110 * Math.max(0, hp) / maxhp, 7);
  }
  function panel(h) { ctx.fillStyle = 'rgba(247,245,238,.93)'; ctx.fillRect(0, 0, W, H); ctx.strokeStyle = INK; ctx.lineWidth = 3; ctx.strokeRect(14, 14, W - 28, H - 28); ctx.lineWidth = 1; ctx.strokeRect(19, 19, W - 38, H - 38); }
  function title() {
    panel(); text('뜬소문 막기', W / 2, 120, 40, INK, 'center', SERIF, 900);
    text('몰려오는 뜬소문을 「확인 도장」으로 막으세요', W / 2, 168, 14, INK, 'center', SANS, 600);
    var L = ['도장은 가까운 소문에게 저절로 날아갑니다', '화면을 끌어서 움직이세요 (PC: 방향키·WASD)', '파란 증거 조각을 모으면 강화를 고를 수 있습니다', '5분을 버티면 오늘의 정정 보도가 나갑니다'];
    for (var i = 0; i < L.length; i++) text(L[i], W / 2, 220 + i * 26, 13, '#333', 'center', SANS, 500);
    text(best ? '최고 기록 ' + mmss(best) : '아직 기록이 없습니다', W / 2, 345, 15, RED, 'center', SANS, 700);
    ctx.fillStyle = INK; ctx.fillRect(W / 2 - 80, 400, 160, 48); text('시작', W / 2, 425, 18, '#fff', 'center', SANS, 800);
    text('화면을 누르거나 스페이스', W / 2, 475, 12, '#666', 'center', SANS, 500);
  }
  function levelup() {
    ctx.fillStyle = 'rgba(247,245,238,.9)'; ctx.fillRect(0, 0, W, H);
    text('강화를 고르세요', W / 2, 52, 22, INK, 'center', SERIF, 900); text('레벨 ' + lv, W / 2, 80, 13, '#666', 'center', SANS, 600);
    for (var i = 0; i < offer.length; i++) {
      var y = 100 + i * 134, u = offer[i];   // 카드 세 장: 위에서 100, 높이 120, 간격 14 (눌림 판정도 같은 값)
      ctx.fillStyle = '#fff'; ctx.strokeStyle = INK; ctx.lineWidth = 2; ctx.fillRect(20, y, W - 40, 120); ctx.strokeRect(20, y, W - 40, 120);
      text((i + 1) + '. ' + u.name + (up[u.id] ? '  (' + up[u.id] + '→' + (up[u.id] + 1) + ')' : ''), W / 2, y + 40, 21, INK, 'center', SERIF, 800);
      text(u.desc, W / 2, y + 82, 13, '#444', 'center', SANS, 500);
    }
  }
  function over() {
    var win = mode === 'win'; panel();
    text(win ? '정정 보도가 나갔습니다' : '뜬소문에 묻혔습니다', W / 2, 120, 28, win ? '#0b5d2f' : RED, 'center', SERIF, 900);
    text('버틴 시간 ' + mmss(t), W / 2, 200, 24, INK, 'center', SERIF, 800);
    text('막은 소문 ' + kills + '개 · 레벨 ' + lv, W / 2, 240, 15, '#333', 'center', SANS, 600);
    text('최고 기록 ' + mmss(best), W / 2, 290, 15, RED, 'center', SANS, 700);
    text(win ? '5분을 끝까지 버텼습니다' : '5분을 버티면 정정 보도가 나갑니다', W / 2, 335, 12.5, '#555', 'center', SANS, 500);
    ctx.fillStyle = INK; ctx.fillRect(W / 2 - 80, 400, 160, 48); text('다시 하기', W / 2, 425, 18, '#fff', 'center', SANS, 800);
  }

  /* ---------- 반복 ---------- */
  function frame(now) {
    var dt = Math.min(0.05, (now - last) / 1000 || 0.016); last = now;
    acc += dt; while (acc >= 1 / 60) { step(1 / 60); acc -= 1 / 60; }
    draw(); requestAnimationFrame(frame);
  }
  if (STOP) {                            // 시험용: 그 장면까지 빨리 감는다(봇이 대신 플레이)
    BOT = true; reset();
    var guard = 0, target = STOP;
    while (guard++ < 60 * 60 * 6 && !doneStop) {
      if (target === 'play' && t >= (+Q.get('t') || 60) && mode === 'play') { doneStop = true; break; }
      if (mode === 'levelup' && target === 'levelup' && lv >= 3) { doneStop = true; break; }
      if (mode === 'levelup') { pick(Math.floor(Math.random() * offer.length)); }
      if (mode === 'over' || mode === 'win') { doneStop = (target === 'over' || target === 'win'); break; }
      step(1 / 60);
    }
    camx = px; camy = py; draw();   // 감아 둔 장면을 그릴 때는 카메라가 바로 플레이어를 따라가게
  } else { requestAnimationFrame(frame); }
  window.__rumor = function () { return { mode: mode, t: Math.round(t * 10) / 10, lv: lv, kills: kills, hp: hp, enemies: E.length, x: Math.round(px), y: Math.round(py) }; };
})();
