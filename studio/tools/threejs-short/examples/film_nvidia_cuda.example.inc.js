  // ---------- "Nvidia's useless supercomputer" (production nvidia-cuda-bet-20261116), spliced into main.js ----------
  // index.html?viewer=1&film=cuda[&set=home][&t0=s&dur=s]; office load renders l1–l5 + l7 tail–l10, home load renders l6–l7.
  ui.style.display = 'none';
  const { RoundedBoxGeometry } = await import('three/addons/geometries/RoundedBoxGeometry.js');
  const TJ = await getJ('./film/timing.json'), TL = TJ.lines, END = TJ.duration, T0 = +(Q.get('t0') || 0), HOME = Q.get('set') === 'home';
  const LS = i => TL[i - 1].start;
  const WT = (i, w, n = 0) => { const ws = TL[i - 1].words.filter(x => norm(x.w).startsWith(w)); return ws[n] ? ws[n].t : LS(i); };
  const O = OFF_O, ZB = Z - 6, ZD = Z - 2.9, CHZ = ZD - 0.55, ME = 2.1;
  const btw = (t, a, b) => clamp((t - a) / (b - a));
  const flap = (t, a, b) => t >= a && t < b && Math.sin((t - a) * 23) > -0.3;
  // ---- cast: CEO (black jacket), investor (vest, OUTF[1]), student (hoodie, OUTF[0]), three coworkers without hats ----
  let ph = 5; const mk = o => { const c = SR.build({ ...base, ...o }); c.root.scale.setScalar(0.8); c.phase = (ph += 0.37); c.root.rotation.order = 'YXZ'; face(c, 'calm'); c.tint = c.hm.material.uniforms.base.value.clone(); ALL.push(c); return c; };
  const ceo = mk({ jacket: '#2b2b31', jacket2: '#18181c', details: ['collar', 'buttons'], collarCol: '#121215', btn: '#6a6a72' });
  const inv = OUTF[1], stu = OUTF[0], CW = [[ex[1], -2.1], [ex[4], 0.0], [ex[7], 4.2]];
  O.children.filter(o => o.name === 'modern_arm_chair_01' || o.name === 'chair_A_wood').forEach(o => (o.visible = false));
  // pull the desk clusters together (2.1 m apart) so a 9:16 frame holds two desks: -6.2→-2.1, -2.1→0, 6.2→4.2; the CEO's desk stays at 2.1
  if (!HOME) { const moves = [[-2.1, 2.1], [-6.2, 4.1], [6.2, -2.0]].map(([x, dx]) => [O.children.filter(o => Math.abs(o.position.x - x) < 0.9 && Math.abs(o.position.z - ZD) < 1.3), dx]);
    moves.forEach(([objs, dx]) => objs.forEach(o => (o.position.x += dx))); O.children.filter(o => o.name === 'alarm_clock_01').forEach(o => (o.visible = false)); }
  // ---- props ----
  const GLOW = new THREE.Color(0.45, 1.6, 0.12), BLUE = new THREE.Color(0.35, 0.8, 1.8), DIM = new THREE.Color('#23302a'), OFFC = new THREE.Color('#3a3f47');
  function makeCard() {
    const g = new THREE.Group(), shM = new THREE.MeshStandardMaterial({ color: '#2d3038', roughness: 0.32, metalness: 0.55, transparent: true }), fanM = new THREE.MeshStandardMaterial({ color: '#16171b', roughness: 0.5, metalness: 0.2, transparent: true });
    const add = (geo, mat, x, y, z, p = g) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = true; p.add(m); return m; };
    add(new RoundedBoxGeometry(0.44, 0.15, 0.06, 3, 0.012), shM, 0, 0, 0);
    add(new THREE.BoxGeometry(0.43, 0.135, 0.008), new THREE.MeshStandardMaterial({ color: '#0f4a24', roughness: 0.6 }), 0, -0.005, -0.036);
    add(new THREE.BoxGeometry(0.008, 0.17, 0.075), new THREE.MeshStandardMaterial({ color: '#b9bcc4', roughness: 0.3, metalness: 0.9 }), -0.226, 0, 0);
    add(new THREE.BoxGeometry(0.40, 0.012, 0.064), new THREE.MeshBasicMaterial({ color: GLOW, toneMapped: false }), 0.01, 0.068, 0);
    const rotors = [];
    for (const x of [-0.1, 0.11]) { add(new THREE.TorusGeometry(0.06, 0.006, 8, 32), fanM, x, -0.005, 0.031);
      const rot = new THREE.Group(); rot.position.set(x, -0.005, 0.03); g.add(rot); rotors.push(rot);
      for (let b = 0; b < 7; b++) { const bl = add(new THREE.BoxGeometry(0.05, 0.014, 0.003), fanM, 0.03 * Math.cos(b * 0.9), 0.03 * Math.sin(b * 0.9), 0, rot); bl.rotation.z = b * 0.9 + 0.35; }
      const hub = add(new THREE.CylinderGeometry(0.017, 0.017, 0.01, 16), new THREE.MeshStandardMaterial({ color: '#76b900', roughness: 0.4 }), 0, 0, 0.002, rot); hub.rotation.x = Math.PI / 2; }
    const cores = new THREE.InstancedMesh(new THREE.BoxGeometry(0.0065, 0.0065, 0.0065), new THREE.MeshBasicMaterial({ color: '#ffffff', toneMapped: false }), 512), M4 = new THREE.Matrix4();
    for (let i = 0; i < 512; i++) { M4.makeTranslation(-0.17 + (i % 32) * 0.011, -0.06 + ((i / 32) | 0) * 0.008, -0.008); cores.setMatrixAt(i, M4); cores.setColorAt(i, GLOW); }
    g.add(cores); g.userData = { shM, fanM, rotors, cores }; return g; }
  const _c = new THREE.Color();
  function cardTick(cd, t, xray = 0) { const u = cd.userData; u.rotors.forEach((r, i) => (r.rotation.z = -t * (13 + i))); u.shM.opacity = 1 - 0.88 * xray; u.fanM.opacity = 1 - 0.92 * xray; u.cores.visible = xray > 0.01;
    if (xray > 0.01) { for (let i = 0; i < 512; i++) { const b = (0.25 + 0.75 * (0.5 + 0.5 * Math.sin(t * 11 + i * 0.73 + (i % 7)))) * xray; u.cores.setColorAt(i, _c.copy(DIM).lerp(GLOW, b)); } u.cores.instanceColor.needsUpdate = true; } }
  const cards = (HOME ? [0, 1] : [0, 1]).map(() => { const c = makeCard(); scene.add(c); return c; });
  // CEO's monitor beside him, turned to face him; its screen is a canvas we redraw per frame
  const mon = O.children.find(o => o.name === 'computerScreen' && Math.abs(o.position.x - ME) < 0.01); const MX = ME + 0.62, MZ = ZD + 0.05, MR = Math.atan2(ME - MX, CHZ - MZ); if (mon) { mon.position.x = MX; mon.position.z = MZ; mon.rotation.y = MR; }   // monitor at the desk's right end, angled to face him
  const scrC = document.createElement('canvas'); scrC.width = 640; scrC.height = 400; const sg = scrC.getContext('2d'), scrT = new THREE.CanvasTexture(scrC); scrT.colorSpace = THREE.SRGBColorSpace;
  const scr = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.31), new THREE.MeshBasicMaterial({ map: scrT, toneMapped: false })); scr.rotation.y = MR; scr.position.set(MX + Math.sin(MR) * 0.045, FY + 0.95, MZ + Math.cos(MR) * 0.045); scr.visible = !HOME; O.add(scr);
  let scrKey = '';
  function drawScreen(mode, t) { const key = mode + (mode === 'math' || mode === 'wait' || mode === 'lab' ? Math.floor(t * 15) : ''); if (key === scrKey) return; scrKey = key; const g = sg;
    if (mode === 'desk') { g.fillStyle = '#2d5fa8'; g.fillRect(0, 0, 640, 400); g.fillStyle = 'rgba(255,255,255,0.85)'; for (let i = 0; i < 4; i++) g.fillRect(30, 30 + i * 80, 56, 56); g.fillStyle = '#1b1f27'; g.fillRect(0, 368, 640, 32); }
    if (mode === 'cuda' || mode === 'math') { g.fillStyle = '#07090b'; g.fillRect(0, 0, 640, 400); }
    if (mode === 'cuda') { g.fillStyle = '#76b900'; g.font = 'bold 150px InterB, sans-serif'; g.textAlign = 'center'; g.fillText('CUDA', 320, 230); g.font = 'bold 26px InterB, sans-serif'; g.fillStyle = '#cfe9a8'; g.fillText('graphics chip → math chip', 320, 300); g.textAlign = 'left'; }
    if (mode === 'math') { const k = Math.floor(t * 15); g.font = 'bold 30px InterB, monospace'; for (let c = 0; c < 5; c++) for (let r = 0; r < 9; r++) { const n = (k + c * 7 + r * 3) % 13; g.fillStyle = r === (k + c * 2) % 9 ? '#eaffc9' : '#76b900'; g.fillText(`${(n * 7 + c) % 10}×${(n + r) % 9 + 1}=${((n * 7 + c) % 10) * ((n + r) % 9 + 1)}`, 18 + c * 126, 40 + r * 42); } }
    if (mode === 'wait') { g.fillStyle = '#07090b'; g.fillRect(0, 0, 640, 400); g.fillStyle = '#76b900'; g.font = 'bold 54px InterB, sans-serif'; g.textAlign = 'center'; g.fillText('CUDA', 320, 150); g.fillStyle = '#9aa3ad'; g.font = 'bold 34px InterB, sans-serif'; g.fillText('waiting for users' + '.'.repeat(Math.floor(t * 3) % 4), 320, 250); g.textAlign = 'left'; }
    if (mode === 'lab') { g.fillStyle = '#0c1220'; g.fillRect(0, 0, 640, 400); g.fillStyle = '#76b900'; g.font = 'bold 40px InterB, sans-serif'; g.fillText('AI TRAINING', 30, 60); g.fillStyle = '#2b3a55'; g.fillRect(30, 300, 580, 40); g.fillStyle = '#76b900'; g.fillRect(30, 300, 580 * ((t * 0.37) % 1), 40); }
    scrT.needsUpdate = true; }
  // student's laptop (home): own boxes so the screen plane is exactly on the lid
  const lap = new THREE.Group(), lapM = new THREE.MeshStandardMaterial({ color: '#3b3f48', roughness: 0.4, metalness: 0.5 });
  { const b = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.014, 0.25), lapM); b.position.y = 0.007; b.castShadow = true; lap.add(b); const piv = new THREE.Group(); piv.position.set(0, 0.014, 0.12); piv.rotation.x = 0.28; lap.add(piv);
    const lid = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.24, 0.01), lapM); lid.position.set(0, 0.12, 0); lid.castShadow = true; piv.add(lid); lap.userData.piv = piv; }
  const lapC = document.createElement('canvas'); lapC.width = 512; lapC.height = 340; const lg = lapC.getContext('2d'), lapT = new THREE.CanvasTexture(lapC); lapT.colorSpace = THREE.SRGBColorSpace;
  { const s = new THREE.Mesh(new THREE.PlaneGeometry(0.33, 0.21), new THREE.MeshBasicMaterial({ map: lapT, toneMapped: false })); s.rotation.y = Math.PI; s.position.set(0, 0.12, -0.0056); lap.userData.piv.add(s); }
  const ICONS = [['CAT', g => { g.beginPath(); g.moveTo(-40, -10); g.lineTo(-30, -48); g.lineTo(-8, -22); g.lineTo(8, -22); g.lineTo(30, -48); g.lineTo(40, -10); g.arc(0, 0, 40, 0, Math.PI); g.closePath(); g.fill(); }],
    ['CAR', g => { g.fillRect(-46, -10, 92, 26); g.fillRect(-26, -32, 50, 24); g.beginPath(); g.arc(-26, 18, 12, 0, 7); g.arc(26, 18, 12, 0, 7); g.fill(); }],
    ['DOG', g => { g.beginPath(); g.ellipse(0, 0, 36, 32, 0, 0, 7); g.fill(); g.beginPath(); g.ellipse(-36, -6, 12, 26, 0.4, 0, 7); g.ellipse(36, -6, 12, 26, -0.4, 0, 7); g.fill(); }],
    ['SHIP', g => { g.beginPath(); g.moveTo(-50, 0); g.lineTo(50, 0); g.lineTo(34, 24); g.lineTo(-34, 24); g.closePath(); g.fill(); g.fillRect(-6, -40, 8, 40); g.beginPath(); g.moveTo(2, -40); g.lineTo(34, -6); g.lineTo(2, -6); g.fill(); }],
    ['BIRD', g => { g.beginPath(); g.ellipse(0, 4, 30, 20, 0, 0, 7); g.fill(); g.beginPath(); g.arc(26, -14, 14, 0, 7); g.fill(); g.beginPath(); g.moveTo(-4, 0); g.lineTo(-40, -34); g.lineTo(10, -6); g.fill(); }],
    ['FROG', g => { g.beginPath(); g.ellipse(0, 6, 42, 26, 0, 0, 7); g.fill(); g.beginPath(); g.arc(-20, -20, 12, 0, 7); g.arc(20, -20, 12, 0, 7); g.fill(); }]];
  let lapKey = '';
  function drawLaptop(mode, t) { const key = mode + Math.floor(t * 10); if (key === lapKey) return; lapKey = key; const g = lg; g.fillStyle = '#0c1220'; g.fillRect(0, 0, 512, 340);
    const k = Math.floor(t * 10), done = mode === 'win' ? 6 : mode === 'train' ? k % 7 : 0;
    for (let i = 0; i < 6; i++) { const x = 20 + (i % 3) * 164, y = 20 + ((i / 3) | 0) * 160; g.fillStyle = '#1d2a44'; g.fillRect(x, y, 148, 140); g.save(); g.translate(x + 74, y + 62); g.fillStyle = ['#f2a65a', '#e5483a', '#c9874a', '#7da7c9', '#f2cf2c', '#6cc04a'][i]; ICONS[(i + (mode === 'train' ? k : 0)) % 6][1](g); g.restore();
      g.font = 'bold 24px InterB, sans-serif'; g.fillStyle = i < done ? '#9cff4a' : '#7f8aa3'; g.fillText((i < done ? '✓ ' : '? ') + ICONS[(i + (mode === 'train' ? k : 0)) % 6][0], x + 12, y + 130); }
    lapT.needsUpdate = true; }
  // science boards (office): CPU = 4 big blue cores, GPU = 512 small green cores, with progress bars
  const SCI = new THREE.Group(); SCI.position.set(ME - 0.12, 0, ZD + 1.0); scene.add(SCI);
  const plate = (w, h, y) => { const m = new THREE.Mesh(new RoundedBoxGeometry(w, h, 0.03, 2, 0.01), new THREE.MeshStandardMaterial({ color: '#123d24', roughness: 0.5, metalness: 0.2 })); m.position.set(0, y, 0); SCI.add(m); return m; };
  const cpuY = 2.4, gpuY = 1.6, cpuP = plate(0.5, 0.5, cpuY), gpuP = plate(0.98, 0.56, gpuY);
  const bigC = [0, 1, 2, 3].map(i => { const m = new THREE.Mesh(new RoundedBoxGeometry(0.19, 0.19, 0.07, 2, 0.02), new THREE.MeshBasicMaterial({ color: '#ffffff', toneMapped: false })); m.position.set(i % 2 ? 0.105 : -0.105, cpuY + (i < 2 ? 0.105 : -0.105), 0.04); SCI.add(m); return m; });
  const grid = new THREE.InstancedMesh(new THREE.BoxGeometry(0.021, 0.021, 0.02), new THREE.MeshBasicMaterial({ color: '#ffffff', toneMapped: false }), 512); SCI.add(grid);
  const bar = (w, y) => { const bg = new THREE.Mesh(new THREE.BoxGeometry(w, 0.035, 0.02), new THREE.MeshBasicMaterial({ color: '#1b222b' })); bg.position.set(0, y, 0.02); SCI.add(bg);
    const fg = new THREE.Mesh(new THREE.BoxGeometry(1, 0.037, 0.026).translate(0.5, 0, 0), new THREE.MeshBasicMaterial({ color: '#ffffff', toneMapped: false })); fg.position.set(-w / 2, y, 0.02); SCI.add(fg); fg.userData.w = w; return fg; };
  const cpuBar = bar(0.5, cpuY - 0.31), gpuBar = bar(0.98, gpuY - 0.34); cpuBar.material.color.copy(BLUE); gpuBar.material.color.copy(GLOW);
  const M4 = new THREE.Matrix4(), Q4 = new THREE.Quaternion(), S4 = new THREE.Vector3(), P4 = new THREE.Vector3();
  function sciTick(t, o) {   // o: start times of each pop (springs), run = cores busy, slow = only one CPU core lit at a time
    cpuP.scale.setScalar(Math.max(1e-3, spr(t - o.cpu))); gpuP.scale.setScalar(Math.max(1e-3, spr(t - o.gpu)));
    bigC.forEach((m, i) => { const on = spr(t - o.cubes - i * 0.1), busy = o.run ? (Math.floor(t * (o.slow ? 1.2 : 2.4)) % 4 === i ? 1 : 0.15) : 1; m.scale.setScalar(Math.max(1e-3, on)); m.material.color.copy(OFFC).lerp(BLUE, clamp(on) * busy); });
    for (let i = 0; i < 512; i++) { const cx = i % 32, cy = (i / 32) | 0, pop = spr(t - o.grid - (cx + cy) / 47 * 0.55), fl = o.run ? 0.35 + 0.65 * (Math.sin(t * 17 + i * 1.37) > 0.2 ? 1 : 0) : 1;
      P4.set(-0.434 + cx * 0.028, gpuY + 0.21 - cy * 0.028, 0.03); S4.setScalar(Math.max(1e-3, pop)); M4.compose(P4, Q4, S4); grid.setMatrixAt(i, M4); grid.setColorAt(i, _c.copy(DIM).lerp(GLOW, clamp(pop) * fl)); }
    const cpuProg = o.cpuProg, gpuProg = o.gpuProg;
    grid.instanceMatrix.needsUpdate = true; grid.instanceColor.needsUpdate = true;
    cpuBar.scale.x = Math.max(1e-3, cpuBar.userData.w * cpuProg); gpuBar.scale.x = Math.max(1e-3, gpuBar.userData.w * gpuProg); cpuBar.visible = cpuProg > 0.001; gpuBar.visible = gpuProg > 0.001; }
  // speech/reaction bubbles
  const bubT = {}; const bubTex = (txt, col) => (bubT[txt] ||= (() => { const c = document.createElement('canvas'); c.width = 256; c.height = 160; const g = c.getContext('2d'); g.fillStyle = '#fff'; g.strokeStyle = '#2a1612'; g.lineWidth = 8; g.beginPath(); g.ellipse(128, 74, 118, 64, 0, 0, 7); g.fill(); g.stroke(); g.fillStyle = col; g.font = 'bold 82px InterB, sans-serif'; g.textAlign = 'center'; g.fillText(txt, 128, 104); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; })());
  const bubs = [0, 1, 2, 3].map(() => { const b = new THREE.Sprite(new THREE.SpriteMaterial({ transparent: true, depthTest: false })); b.renderOrder = 10; scene.add(b); return b; });
  let nb = 0; const bubble = (c, txt, col, t, t0) => { const b = bubs[nb++]; if (!b) return; const h = headC(c), k = spr(t - t0); b.visible = k > 0; const tx = bubTex(txt, col); if (b.material.map !== tx) { b.material.map = tx; b.material.needsUpdate = true; } b.position.set(h.x + 0.28, h.y + 0.42 + 0.03 * Math.sin(t * 9), h.z); b.scale.set(0.42 * k, 0.26 * k, 1); };
  // home extras
  const nightLamp = new THREE.PointLight('#ffc77a', 0, 7, 1.5), cardGlow = new THREE.PointLight('#8dff4a', 0, 2.2, 2); scene.add(nightLamp, cardGlow);
  let TAB = null;
  if (HOME) { const tb = O.children.find(o => o.name === 'tableRound'); const bb = new THREE.Box3().setFromObject(tb); tb.visible = false; TAB = { x: (bb.min.x + bb.max.x) / 2, z: (bb.min.z + bb.max.z) / 2, y: FY + 0.71 };
    { const wood = new THREE.MeshStandardMaterial({ color: '#8a5a36', roughness: 0.55 }), leg = new THREE.MeshStandardMaterial({ color: '#2a2a2e', roughness: 0.4, metalness: 0.6 }); const top = new THREE.Mesh(new RoundedBoxGeometry(1.5, 0.05, 0.7, 2, 0.01), wood); top.position.set(TAB.x, TAB.y - 0.025, TAB.z); top.castShadow = top.receiveShadow = true; O.add(top);
      for (const [dx, dz] of [[-0.7, -0.3], [0.7, -0.3], [-0.7, 0.3], [0.7, 0.3]]) { const l = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.66, 0.04), leg); l.position.set(TAB.x + dx, FY + 0.33, TAB.z + dz); l.castShadow = true; O.add(l); } }   // his desk (own boxes, desk-height like the office)
    O.add(lap); lap.position.set(TAB.x - 0.12, TAB.y, TAB.z - 0.05);
    O.traverse(o => { if (!o.isMesh || !o.material) return; const m = o.material; if (m.blending === THREE.AdditiveBlending) o.visible = false;
      else if (m.isMeshBasicMaterial && m.color) { if (m.color.r > 1.2) m.color.set('#5a5850'); else if (Math.abs(m.color.r - 0.55) < 0.01 && Math.abs(m.color.b - 0.95) < 0.01) m.color.set('#0b1230'); else if (m.color.getHexString() === '7da7c9') m.color.set('#26324f'); } });
    scene.children.filter(o => o.isPointLight && o !== nightLamp && o !== cardGlow).forEach(o => (o.intensity = 0.0)); scene.background = new THREE.Color('#141a2c'); scene.environmentIntensity = 0.1; }
  // ---- pose helpers ----
  const stand = (c, x, z, ry = 0, t = 0) => { place(c, x, z, ry, FY); idle(c, t); };
  const type = (c, t) => { const a = 0.03 * Math.sin(t * 28 + c.phase), b = 0.03 * Math.sin(t * 31 + 1 + c.phase); arm(c, 'Left', Lw(c, 0.16, 0.97 + a, 0.52)); arm(c, 'Right', Lw(c, -0.16, 0.97 + b, 0.52)); };
  // v2 motion curves: camera moves start already moving at the cut and settle (no stop-start at every cut); gestures overshoot like a spring
  const cm = u => { u = clamp(u); return 0.3 * u + 0.7 * (1 - Math.pow(1 - u, 3)); };
  const spr = s => s <= 0 ? 0 : 1 - Math.exp(-7 * s) * Math.cos(10 * s);   // s = seconds since the gesture started; peaks ≈1.1 at 0.3 s, settles by 0.6 s
  const fr = x => Math.round(x * 30) / 30;
  function hold(c, cd, up = 0, t = 0) { const H = Lw(c, -0.2, 1.36 + 0.18 * up + 0.01 * Math.sin(t * 2), 0.5), Lf = LEFT(c);
    cd.visible = true; cd.position.copy(H); cd.quaternion.copy(c.root.quaternion);
    arm(c, 'Right', H.clone().addScaledVector(Lf, -0.2).add(V(0, -0.02, 0)), dirW(c, -1, -0.6, -0.3)); arm(c, 'Left', H.clone().addScaledVector(Lf, 0.2).add(V(0, -0.02, 0)), dirW(c, 1, -0.6, -0.3)); return H.clone(); }
  // point with a spring: the hand travels from the hip to the pointing pose (k = spring value, may overshoot)
  function reach(c, P, k, s = 'Right') { const sh = SR.wp(c.bone(s + 'Arm')), rest = Lw(c, s === 'Left' ? 0.3 : -0.3, 0.9, 0.15), T = sh.clone().add(P.clone().sub(sh).normalize().multiplyScalar(0.62)); arm(c, s, vl(rest, T, k), dirW(c, s === 'Left' ? 1 : -1, -0.3, 0)); }
  const lean = (c, a) => SR.rotWorld(c.bone('Spine1'), LEFT(c), a);
  const alive = (c, t, a = 1) => headTurn(c, 0.07 * a * Math.sin(t * 1.3 + c.phase * 3), 0.04 * a * Math.sin(t * 1.9 + c.phase));   // secondary motion: the head is never frozen
  const onDesk = (cd, x, z) => { cd.visible = true; cd.position.set(x, FY + 0.66 + 0.085, z); cd.rotation.set(0, 0, 0); };
  // ---- v2 light: brighter grade + a key and a rim that follow every shot (the sun alone left faces flat) ----
  const keyL = new THREE.DirectionalLight('#fff1dc', 0), rimL = new THREE.DirectionalLight('#a9d4ff', 0); scene.add(keyL, keyL.target, rimL, rimL.target);
  post.bloomPass.threshold = 0.82; post.bloomPass.strength = 0.5;
  function lightRig(kI, rI) { const cp = camera.position, f = focus, d = f.clone().sub(cp).setY(0).normalize(), right = V(-d.z, 0, d.x);
    keyL.position.copy(cp).addScaledVector(right, -2.2).add(V(0, 1.8, 0)); keyL.target.position.copy(f); keyL.intensity = kI;
    rimL.position.copy(f).addScaledVector(d, 3).addScaledVector(right, 1.4).add(V(0, 2.0, 0)); rimL.target.position.copy(f); rimL.intensity = rI; }
  const LIT = () => { setLook('day'); hemi.intensity = 0.52; hemi.color.set('#d6e6ff'); hemi.groundColor.set('#b89a78'); sun.intensity = 3.2; sun.color.set('#ffd9a8'); SUNDIR.set(0.35, 0.55, -0.75).normalize();
    U.uSat.value = 1.42; U.uCon.value = 1.17; U.uWarm.value = 0.06; renderer.toneMappingExposure = 0.43; U.uVig.value = 0.4; U.uCA.value = 0.035; U.uDist.value = 0.06; U.uGrain.value = 0.045; scene.environmentIntensity = 0.65; nightLamp.intensity = 0; cardGlow.intensity = 0; };
  const NIGHT = () => { setLook('day'); hemi.intensity = 0.24; hemi.color.set('#8aa0e0'); hemi.groundColor.set('#3a3040'); sun.intensity = 0.5; sun.color.set('#9fb2ff'); SUNDIR.set(-0.3, 0.6, -0.7).normalize();
    U.uSat.value = 1.25; U.uCon.value = 1.12; U.uWarm.value = 0.03; renderer.toneMappingExposure = 0.64; U.uVig.value = 0.5; U.uCA.value = 0.04; U.uDist.value = 0.06; U.uGrain.value = 0.055; scene.environmentIntensity = 0.2;
    nightLamp.position.set(TAB.x - 0.9, FY + 2.0, TAB.z + 0.6); nightLamp.intensity = 14; cardGlow.position.set(TAB.x + 0.45, TAB.y + 0.3, TAB.z + 0.25); cardGlow.intensity = 3.5; };
  // ---- the shots (each 2–3.5 s, cut on the words; see production.md) ----
  const C0 = { w: [0.3, 0.1, 0.6], f: 40 };   // loop frame: the opening and the closing land on this card close-up
  const S = { nob: WT(2, 'nobody') - 0.08, cuda: WT(2, 'cuda'), math: WT(2, 'math'), l3: LS(3) - 0.1, inv: WT(3, 'investors') - 0.06, so: WT(3, 'so'), calc: WT(3, 'calculator'), l4: LS(4) - 0.1, keep: WT(4, 'keep'), l5: LS(5) - 0.1, lapse: WT(5, 'outside') + 0.4,
    H0: fr(LS(6) - 0.15), H1: fr(WT(7, 'worlds') - 0.1), stu: WT(6, 'student') + 0.3, two: WT(6, 'two') - 0.05, bed: WT(6, 'in', 2) - 0.05, l7: LS(7) - 0.06, crush: WT(7, 'every') - 0.05,
    l8: LS(8) - 0.08, normal: WT(8, 'normal'), four: WT(8, 'four'), that: WT(8, 'that') - 0.1, card8: WT(8, 'card'), five: WT(8, 'five'), l9: LS(9) - 0.1, like: WT(9, 'like'), beat: WT(9, 'beat'), l10: LS(10) - 0.1, all: WT(10, 'all') - 0.06 };
  S.ins = S.math - 0.12; S.qend = WT(3, 'open') + 0.45;   // v3: the investor speaks the question himself; laughs start after it
  const officeCast = (t) => { CW.forEach(([c, x], i) => { stand(c, x, CHZ, 0, t); type(c, t + i); face(c, 'calm'); alive(c, t, 0.6); }); };
  let shR = 6;
  function frame(t) {
    resetScene(); nb = 0; bubs.forEach(b => (b.visible = false)); cards.forEach(c => (c.visible = false)); SCI.visible = false; ALL.forEach(c => (c.root.visible = false));
    let dofD = 0, dofA = 0.012, roll = 0, kI = 1.3, rI = 1.5; shR = 6;
    if (HOME) { NIGHT(); const sx = TAB.x, sz = TAB.z - 0.78; stand(stu, sx, sz, 0, t); face(stu, 'serious'); lean(stu, 0.08); type(stu, t); alive(stu, t, 0.5);
      cards.forEach((cd, i) => { cd.visible = true; cd.position.set(TAB.x + 0.42 + i * 0.05, TAB.y + 0.077, TAB.z + 0.2 - i * 0.2); cd.rotation.set(0, -0.35, 0); cardTick(cd, t + i * 0.3, 0); });
      drawLaptop(t >= S.crush ? 'win' : 'train', t); const hc = headC(stu), CC = V(TAB.x + 0.44, TAB.y + 0.08, TAB.z + 0.1); kI = 0.9; rI = 1.8;
      if (t < S.stu) { const u = cm(btw(t, S.H0, S.stu)); look(V(lerp(3.0, 4.6, u), lerp(3.4, 1.95, u), lerp(Z + 3.6, Z + 1.3, u)), V(lerp(5.2, sx, u), lerp(0.9, 1.25, u), lerp(Z - 2.4, sz + 0.3, u)), 46); shR = 8; }   // night crane down to the lamp-lit desk
      else if (t < S.two) { const u = cm(btw(t, S.stu, S.two)); look(hc.clone().add(V(0.55, -0.32, lerp(1.6, 1.25, u))), hc.clone().add(V(0, -0.12, 0)), 34); dofD = 1.5; shR = 3; }   // low angle on the student
      else if (t < S.bed) { const u = cm(btw(t, S.two, S.bed)); look(CC.clone().add(V(lerp(0.45, 0.32, u), 0.06 + 0.03 * u, lerp(0.95, 0.7, u))), CC.clone().add(V(0, 0.01, 0)), 38); dofD = lerp(1.05, 0.77, u); dofA = 0.02; shR = 2; }   // ECU: two gaming cards
      else if (t < S.l7) { const u = cm(btw(t, S.bed, S.l7)); look(V(lerp(4.6, 3.3, u), lerp(1.6, 2.2, u), lerp(Z + 1.6, Z + 3.4, u)), V(sx - 0.4, 1.0, sz), 46); shR = 8; }   // pull back: his bedroom
      else if (t < S.crush) { const u = cm(btw(t, S.l7, S.crush)); look(V(sx - 0.28, TAB.y + 0.62, sz - 0.42 + 0.1 * u), lap.position.clone().add(V(0, 0.12, 0.06)), 32); dofD = 0.6; dofA = 0.01; shR = 2; }   // OTS: the laptop recognises everything
      else { const u = cm(btw(t, S.crush, S.H1)), j = spr(t - S.crush); waveArms(stu, t); face(stu, 'laugh'); stu.root.position.y += 0.12 * Math.max(0, Math.sin(Math.min(1, (t - S.crush) * 2.5) * Math.PI)) + Math.abs(Math.sin(t * 7)) * 0.03 * j;
        look(hc.clone().add(V(0.35, -0.2, lerp(1.9, 1.55, u))), hc.clone().add(V(0, -0.15, 0)), 38); bubble(stu, 'YES!', '#2f9e44', t, S.crush); shR = 3; }
    } else {
      LIT(); officeCast(t); const cd = cards[0]; let C = null, xr = 0, scrMode = 'desk', clock = 0;
      stand(ceo, ME, CHZ, 0, t); face(ceo, 'smug'); alive(ceo, t, 0.5);
      if (t < S.nob) { C = hold(ceo, cd, 0, t); xr = Math.min(eio(btw(t, 1.95, 2.6)), 1 - eio(btw(t, 3.75, 4.2))); shR = 3;
        if (t < 1.9) { const u = cm(btw(t, 0, 1.9)); look(C.clone().add(V(C0.w[0] + 0.25 * u, C0.w[1] + 0.12 * u, lerp(C0.w[2], 1.7, u))), vl(C, headC(ceo), 0.45 * u), lerp(C0.f, 38, u)); dofD = lerp(C0.w[2], 1.72, u); }   // open on the card, pull out to the CEO
        else { const u = cm(btw(t, 1.9, S.nob)); look(C.clone().add(V(-0.16 + 0.08 * u, 0.04, lerp(0.8, 0.5, u))), C.clone(), 30); dofD = lerp(0.8, 0.5, u); dofA = 0.016; kI = 0.8; } }   // x-ray push: 512 cores inside
      else if (t < S.cuda - 0.35) { C = hold(ceo, cd, 0.3 * spr(t - S.nob), t); face(ceo, 'grin'); lean(ceo, -0.06); const u = cm(btw(t, S.nob, S.cuda - 0.35));
        [[CW[0][0], 1.3, ZD + 0.8], [CW[2][0], 2.95, ZD + 0.85]].forEach(([c, x, z], i) => { const k = spr(t - S.nob - 0.1 - i * 0.15); stand(c, x, z, yawTo(x, z, ME, CHZ) * Math.min(1, k), t + i); lean(c, 0.12 * k); face(c, 'flat'); headTurn(c, 0, 0.12 * Math.sin(Math.min(1, t - S.nob) * 3)); bubble(c, '?', '#3d7be0', t, S.nob + 0.15 + i * 0.15); });
        look(V(2.15, lerp(1.25, 1.35, u), ZD + lerp(3.5, 3.1, u)), V(2.1, 1.3, ZD + 0.1), 46); }   // nobody asked: blank stares
      else if (t < S.l3) { place(ceo, ME, CHZ, yawTo(ME, CHZ, MX, MZ) * 0.7, FY); idle(ceo, t); type(ceo, t); face(ceo, 'serious'); onDesk(cd, ME - 0.45, ZD - 0.02); scrMode = t < S.cuda ? 'desk' : t < S.math ? 'cuda' : 'math'; shR = 3;
        if (t < S.ins) { const u = cm(btw(t, S.cuda - 0.35, S.ins)); look(V(ME - 0.12, 1.68, CHZ - 0.6 + 0.16 * u), V(MX, FY + 0.95, MZ), 30); dofD = 1.15; dofA = 0.008; }   // OTS on the monitor: CUDA
        else { const u = cm(btw(t, S.ins, S.l3)), n = V(Math.sin(MR), 0, Math.cos(MR)), P = V(MX, FY + 0.95, MZ).addScaledVector(n, 0.05); ceo.root.visible = false; look(P.clone().addScaledVector(n, lerp(0.7, 0.5, u)).add(V(0.06, 0.03, 0)), P, 34); dofD = lerp(0.7, 0.5, u); /* insert: CEO off-camera (his head sat between lens and screen) */ dofA = 0.01; kI = 0.6; } }   // insert: graphics chip → math
      else if (t < S.l5) { // the investor
        C = hold(ceo, cd, t >= S.keep ? 0.1 + 0.3 * spr(t - S.keep) : 0.1, t); scrMode = 'math';
        const walk = btw(t, S.l3, S.inv - 0.15), IP = vl(V(5.3, 0, ZD + 1.5), V(3.15, 0, ZD + 0.75), walk), iry = walk < 1 ? -Math.PI / 2 - 0.3 : yawTo(IP.x, IP.z, ME, CHZ);
        place(inv, IP.x, IP.z, iry, FY); if (walk < 1) SR.clipAt(inv, 'walk', t); else { idle(inv, t); lean(inv, -0.05); } face(inv, flap(t, S.so, S.qend) ? 'smugt' : 'smug'); if (walk >= 1) alive(inv, t, 1.2);
        if (t >= S.inv + 0.15 && t < S.qend) reach(inv, C, Math.min(spr(t - S.inv - 0.15), 1.0 + 0.1 * Math.sin(t * 6)), 'Right');
        if (t < S.inv) { const u = cm(btw(t, S.l3, S.inv)); face(ceo, 'smug'); look(V(lerp(4.6, 4.0, u), 1.45, ZD + 4.6), vl(headC(inv), headC(ceo), 0.2).add(V(0, -0.3, 0)), 40); shR = 6; }   // he walks in
        else if (t < S.qend) { const u = cm(btw(t, S.inv, S.qend)); face(ceo, 'serious'); look(V(lerp(1.6, 1.8, u), 1.45, ZD + lerp(3.6, 3.2, u)), V(2.62, 1.4, ZD + 0.1), 50); const rk = eio(btw(t, S.calc - 0.3, S.calc + 0.15)); dofD = lerp(camera.position.distanceTo(headC(inv)), camera.position.distanceTo(headC(ceo)), rk); dofA = 0.018; shR = 4; }   // two-shot: the question
        else if (t < S.l4) { const w = eio(btw(t, S.qend + 0.3, S.qend + 0.58)), A = headC(inv), B = headC(CW[1][0]); face(inv, 'laugh'); laughPose(inv, t);
          CW.forEach(([c, x], i) => { stand(c, x, CHZ, yawTo(x, CHZ, ME, CHZ) * 0.8, t); laughPose(c, t + i * 0.4); face(c, 'laugh'); if (i < 2) bubble(c, 'HA', '#e8442a', t, S.qend + 0.35 + i * 0.12); });
          look(V(0.4, 1.55, ZD + 2.4), A.clone().lerp(B, w).add(V(0, -0.1, 0)), 40, (w > 0 && w < 1) ? 0.05 : 0); dofD = 2.6; shR = 5; }   // whip pan: the office laughs
        else { const u = cm(btw(t, S.l4, S.l5)), hc = headC(ceo); face(ceo, flap(t, S.keep, S.keep + 0.7) ? 'serioust' : 'serious'); if (t > S.keep) headTurn(ceo, 0, 0.1 * Math.exp(-4 * (t - S.keep)) * Math.sin((t - S.keep) * 14));
          look(hc.clone().add(V(-0.45, lerp(-0.62, -0.5, u), lerp(1.45, 1.05, u))), hc.clone().add(V(0, -0.08, 0)), 36); dofD = lerp(1.6, 1.2, u); dofA = 0.014; shR = 3; kI = 1.6; rI = 2.0; } }   // low hero push: "keep shipping it"
      else if (t < S.H0) { // time-lapse: six years
        onDesk(cd, ME - 0.45, ZD - 0.02); scrMode = 'wait'; const k = Math.floor((t - S.l5) * 3.2), rnd = n => (Math.sin(k * 12.9898 + n * 78.233) * 43758.5453) % 1;
        SUNDIR.set(Math.cos(k * 0.9) * 0.6, 0.45 + 0.1 * Math.sin(k), -0.75).normalize(); clock = t;
        CW.forEach(([c, x], i) => { if (t > S.lapse + 0.8 && rnd(i) > 0) { c.root.visible = false; return; } stand(c, x + rnd(i + 3) * 0.3, CHZ, rnd(i + 5) * 0.9, t); if (rnd(i + 7) > 0) type(c, t); face(c, rnd(i + 9) > 0.3 ? 'flat' : 'calm'); });
        stand(ceo, ME, CHZ, 0, t); face(ceo, 'flat'); type(ceo, t);
        if (t < S.lapse) { const u = cm(btw(t, S.l5, S.lapse)); look(V(5.3, lerp(3.2, 3.35, u), ZB + lerp(2.8, 2.1, u)), V(5.6, FY + 3.05, ZB + 0.15), 30); shR = 4; }   // the wall clock spins
        else { const u = cm(btw(t, S.lapse, S.H0)); look(V(lerp(-1.4, -0.9, u), lerp(2.7, 2.45, u), Z + lerp(3.0, 2.4, u)), V(1.4, 1.05, ZD), 44); shR = 9; } }   // wide: days blur by
      else if (t < S.l8) { // the turn hits the doubter: dolly zoom on the investor
        place(inv, 3.15, ZD + 0.75, 0, FY); idle(inv, t); face(inv, 'pale'); lean(inv, -0.1 * spr(t - S.H1)); onDesk(cd, ME - 0.45, ZD - 0.02); scrMode = 'lab'; face(ceo, 'smug'); CW.forEach(([c, x], i) => { stand(c, x, CHZ, 0, t); face(c, 'wide'); });
        const u = cm(btw(t, S.H1, S.l8)), dz = lerp(1.0, 2.9, u), fov = 2 * Math.atan(0.42 / dz) * 180 / Math.PI, hc = headC(inv);
        look(V(hc.x + 0.02, hc.y - 0.05, hc.z + dz), hc.clone().add(V(0, -0.12 * u, 0)), fov); roll = -0.09 * u; dofD = dz; dofA = 0.015; bubble(inv, '!', '#e8442a', t, S.H1 + 0.2); shR = 4; kI = 1.6; }
      else if (t < S.l10) { // science: 4 big cores vs 512 small cores
        SCI.visible = true; onDesk(cd, ME - 0.45, ZD - 0.02); scrMode = 'lab'; face(ceo, 'smug'); place(inv, 3.15, ZD + 0.75, -0.4, FY); idle(inv, t); face(inv, 'wide'); shR = 4; kI = 1.0; rI = 1.0;
        const run = t >= S.l9 ? 1 : 0; sciTick(t, { cpu: S.normal - 0.1, cubes: S.four - 0.05, gpu: S.card8 - 0.05, grid: S.five - 0.1, run, slow: t >= S.beat - 0.05, cpuProg: run ? 0.06 * btw(t, S.like, S.l10) : 0, gpuProg: run ? eio(btw(t, S.like, S.beat)) : 0 });
        const SP = SCI.position;
        if (t < S.that) { const u = cm(btw(t, S.l8, S.that)); look(V(SP.x + 0.08, cpuY + 0.02, SP.z + lerp(1.9, 1.6, u)), V(SP.x, cpuY - 0.04, SP.z), 34); dofD = lerp(1.9, 1.6, u); }   // CPU: four big cores
        else if (t < S.l9) { const u = cm(btw(t, S.that, S.five + 0.3)); look(V(SP.x + 0.06, lerp(cpuY, gpuY, u), SP.z + lerp(1.6, 1.75, u)), V(SP.x, lerp(cpuY - 0.04, gpuY, u), SP.z), 36); dofD = lerp(1.6, 1.75, u); }   // tilt down: 512 small cores
        else if (t < S.like - 0.1) { const u = cm(btw(t, S.l9, S.like - 0.1)); look(V(SP.x + 0.1, 1.77, SP.z + lerp(2.7, 2.45, u)), V(SP.x, 1.75, SP.z), 46); dofD = lerp(2.7, 2.45, u); }   // both boards: millions of tiny sums
        else if (t < S.beat - 0.05) { const u = cm(btw(t, S.like - 0.1, S.beat - 0.05)); look(V(SP.x - 0.25 + 0.15 * u, gpuY - 0.02, SP.z + lerp(1.5, 1.3, u)), V(SP.x, gpuY - 0.06, SP.z), 38); dofD = lerp(1.5, 1.3, u); }   // GPU: 500 students finish
        else { const u = cm(btw(t, S.beat - 0.05, S.l10)); look(V(SP.x + 0.2 - 0.1 * u, cpuY + 0.02, SP.z + lerp(1.25, 1.1, u)), V(SP.x, cpuY - 0.06, SP.z), 36); dofD = lerp(1.25, 1.1, u); } }   // CPU: four professors still grading
      else { // l10: everyone is in on it; push back into the card (loop to frame 0)
        const g = spr(t - S.l10); C = hold(ceo, cd, 0, t); face(ceo, t < S.all ? 'grin' : 'smug'); place(inv, 1.15, ZD + 0.9, 0.35, FY); idle(inv, t); hold(inv, cards[1], 0.25 * g, t + 1); face(inv, 'grin'); scrMode = 'lab';
        [[CW[0][0], 3.15, ZD + 1.0], [CW[1][0], 0.4, ZD + 0.2], [CW[2][0], 3.9, ZD + 0.3]].forEach(([c, x, z], i) => { stand(c, x, z, -0.2 * Math.sign(x - ME), t); waveArms(c, t + i * 0.3); face(c, 'laugh'); c.root.position.y += Math.abs(Math.sin(t * 7 + i)) * 0.04 * g; });
        if (t < S.all) { const u = cm(btw(t, S.l10, S.all)); look(V(lerp(2.6, 2.3, u), lerp(1.95, 1.7, u), ZD + lerp(5.0, 4.3, u)), V(2.15, 1.3, ZD + 0.2), 48); shR = 6; }
        else { const u = eio(btw(t, S.all, END - 0.12)), A = headC(ceo).clone().add(V(0.5, -0.1, 2.2)), B = C.clone().add(V(...C0.w)); look(vl(A, B, u), vl(vl(C, headC(ceo), 0.4), C, u), lerp(40, C0.f, u)); dofD = A.distanceTo(B) * (1 - u) + C0.w[2]; shR = 3; } }
      cardTick(cd, t, xr); if (cards[1].visible) cardTick(cards[1], t + 0.5, 0); drawScreen(scrMode, t);
      const hands = O.children.filter(o => o.isMesh && Math.abs(o.position.x - 5.6) < 0.01 && Math.abs(o.position.z - (ZB + 0.2)) < 0.01); if (hands.length === 2) { hands[0].rotation.z = -0.6 - clock * 9; hands[1].rotation.z = -2.2 - clock * 60; }
    }
    if (Q.has('dbg')) { const [x, y, z, tx, ty, tz, fv] = Q.get('dbg').split(',').map(Number); look(V(x, y, z), V(tx, ty, tz), fv || 50); dofD = 0; roll = 0; }
    if (dofD === 0 && !Q.has('dbg')) { dofD = camera.position.distanceTo(focus); dofA = 0.007; }
    const loopEdge = t < 0.2 || t > END - 0.25; if (!loopEdge) camera.position.add(hand(t, 0.35));   // light handheld drift (none on the loop frame)
    lightRig(kI, rI);
    ALL.forEach(c => SR.updateLimbs(c)); if (roll) camera.rotateZ(roll);
    post.bokeh.enabled = dofD > 0; if (dofD > 0) { post.bokeh.uniforms.focus.value = dofD; post.bokeh.uniforms.aperture.value = dofA; }
    const f = HOME ? V(TAB.x, 1, TAB.z) : V(ME, 1, ZD); sun.target.position.copy(f); sun.position.copy(f).addScaledVector(SUNDIR, 60); const sc = sun.shadow.camera; sc.left = sc.bottom = -shR; sc.right = sc.top = shR; sc.near = 1; sc.far = 140; sc.updateProjectionMatrix();
    U.uTime.value = t; post.render(); return canvas.toDataURL('image/jpeg', 0.92); }
  window.frame = t => frame(t + T0); window.DUR = +(Q.get('dur') || END - T0); window.FILM = { END, S }; window.ready = true;
