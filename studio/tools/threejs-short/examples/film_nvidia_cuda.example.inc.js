  // ---------- "Nvidia's useless supercomputer" (production nvidia-cuda-bet-20261116), spliced into main.js ----------
  // index.html?viewer=1&film=cuda[&set=home][&t0=s&dur=s]; office load renders l1–l5 + l7 tail–l10, home load renders l6–l7.
  ui.style.display = 'none';
  const { RoundedBoxGeometry } = await import('three/addons/geometries/RoundedBoxGeometry.js');
  const TJ = await getJ('./film/cuda_timing.json'), TL = TJ.lines, END = TJ.duration, T0 = +(Q.get('t0') || 0), HOME = Q.get('set') === 'home';
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
  function drawScreen(mode, t) { const key = mode + (mode === 'math' || mode === 'wait' || mode === 'lab' ? Math.floor(t * 6) : ''); if (key === scrKey) return; scrKey = key; const g = sg;
    if (mode === 'desk') { g.fillStyle = '#2d5fa8'; g.fillRect(0, 0, 640, 400); g.fillStyle = 'rgba(255,255,255,0.85)'; for (let i = 0; i < 4; i++) g.fillRect(30, 30 + i * 80, 56, 56); g.fillStyle = '#1b1f27'; g.fillRect(0, 368, 640, 32); }
    if (mode === 'cuda' || mode === 'math') { g.fillStyle = '#07090b'; g.fillRect(0, 0, 640, 400); }
    if (mode === 'cuda') { g.fillStyle = '#76b900'; g.font = 'bold 150px InterB, sans-serif'; g.textAlign = 'center'; g.fillText('CUDA', 320, 230); g.font = 'bold 26px InterB, sans-serif'; g.fillStyle = '#cfe9a8'; g.fillText('graphics chip → math chip', 320, 300); g.textAlign = 'left'; }
    if (mode === 'math') { const k = Math.floor(t * 6); g.font = 'bold 30px InterB, monospace'; for (let c = 0; c < 5; c++) for (let r = 0; r < 9; r++) { const n = (k + c * 7 + r * 3) % 13; g.fillStyle = r === (k + c * 2) % 9 ? '#eaffc9' : '#76b900'; g.fillText(`${(n * 7 + c) % 10}×${(n + r) % 9 + 1}=${((n * 7 + c) % 10) * ((n + r) % 9 + 1)}`, 18 + c * 126, 40 + r * 42); } }
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
    bigC.forEach((m, i) => { const on = spr(t - o.cubes - i * 0.1), busy = o.run ? (Math.floor(t * (o.slow ? 1.2 : 2.4)) % 4 === i ? 1 : 0.4) : 1; m.scale.setScalar(Math.max(1e-3, on)); m.material.color.copy(OFFC).lerp(BLUE, clamp(on) * busy); });
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
  // ---- v7: diegetic props and physical gags (reference study: text lives in the world; every clause gets a gag) ----
  const canvasTex = (w, h, draw) => { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; };
  // "+50%" price tag that drops onto the GPU card on a string ("cost about fifty percent more")
  const tagTex = canvasTex(256, 160, g => { g.fillStyle = '#ffd400'; g.beginPath(); g.moveTo(44, 0); g.lineTo(256, 0); g.lineTo(256, 160); g.lineTo(44, 160); g.lineTo(0, 80); g.closePath(); g.fill(); g.strokeStyle = '#2a1612'; g.lineWidth = 8; g.stroke(); g.fillStyle = '#2a1612'; g.beginPath(); g.arc(36, 80, 12, 0, 7); g.fill(); g.fillStyle = '#d61f1f'; g.font = 'bold 64px InterB, sans-serif'; g.textAlign = 'center'; g.fillText('+50%', 152, 104); });
  const tag = new THREE.Group(), tagCard = new THREE.Mesh(new THREE.PlaneGeometry(0.17, 0.106), new THREE.MeshStandardMaterial({ map: tagTex, side: THREE.DoubleSide, roughness: 0.6 })), tagStr = new THREE.Mesh(new THREE.CylinderGeometry(0.0018, 0.0018, 1, 4).translate(0, 0.5, 0), new THREE.MeshBasicMaterial({ color: '#2a1612' }));
  tagCard.position.set(0.03, -0.004, 0); tag.add(tagCard); scene.add(tag, tagStr); tag.visible = tagStr.visible = false;
  function tagTick(cd, t, t0) {   // drop on a spring from above, then swing; anchored at the card's right end
    if (t < t0 - 0.05 || !cd.visible) { tag.visible = tagStr.visible = false; return; }
    const A = cd.localToWorld(V(0.08, 0.06, 0.04)), drop = 1 - spr(t - t0), L = 0.14, P = A.clone().add(V(0, -L + 0.55 * drop, 0));
    tag.visible = tagStr.visible = true; tag.position.copy(P); tag.quaternion.copy(cd.quaternion); tag.rotateZ(0.18 * Math.exp(-2.5 * Math.max(0, t - t0 - 0.25)) * Math.sin((t - t0) * 9));
    const top = P.y < A.y ? A : P; tagStr.position.copy(P); tagStr.scale.set(1, Math.max(0.001, top.y - P.y + 0.001), 1); tagStr.visible = P.y < A.y - 0.005; }
  // wall calendar that flips through the years ("For six years")
  const CAL = { x: 4.36, y: FY + 2.55, z: ZB + 0.13 }, calTexs = {};
  const calTex = y => (calTexs[y] ||= canvasTex(256, 330, g => { g.fillStyle = '#fbf8f0'; g.fillRect(0, 0, 256, 330); g.fillStyle = '#d61f1f'; g.fillRect(0, 0, 256, 74); g.fillStyle = '#fff'; g.font = 'bold 46px InterB, sans-serif'; g.textAlign = 'center'; g.fillText('JANUARY', 128, 54); g.fillStyle = '#1b1f27'; g.font = 'bold 84px InterB, sans-serif'; g.fillText(String(y), 128, 190); g.fillStyle = '#9aa3ad'; for (let i = 0; i < 21; i++) g.fillRect(28 + (i % 7) * 30, 222 + ((i / 7) | 0) * 32, 18, 18); }));
  const calBack = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.645), new THREE.MeshStandardMaterial({ map: calTex(2006), roughness: 0.8 })); calBack.position.set(CAL.x, CAL.y, CAL.z); O.add(calBack);
  const calPiv = new THREE.Group(); calPiv.position.set(CAL.x, CAL.y + 0.3225, CAL.z + 0.004); O.add(calPiv);
  const calFront = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.645), new THREE.MeshStandardMaterial({ map: calTex(2006), roughness: 0.8, side: THREE.DoubleSide })); calFront.position.set(0, -0.3225, 0); calPiv.add(calFront);
  { const ring = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.02, 0.02), new THREE.MeshStandardMaterial({ color: '#555b66', metalness: 0.8, roughness: 0.3 })); ring.position.set(CAL.x, CAL.y + 0.33, CAL.z + 0.012); O.add(ring); calBack.visible = calFront.visible = ring.visible = !HOME; }
  function calTick(t, t0, step) {   // years 2006 → 2012, one page per `step` seconds from t0; each page flips up over 0.12 s
    const yr = t < t0 ? 2006 : Math.min(2012, 2006 + Math.floor((t - t0) / step) + 1), local = t < t0 ? 1 : ((t - t0) % step) / 0.12;
    calBack.material.map = calTex(yr); calFront.material.map = calTex(yr - 1 < 2006 ? 2006 : yr - 1); calFront.visible = !HOME && t >= t0 && local < 1 && yr <= 2012 && (t - t0) < step * 6 + 0.12;
    calPiv.rotation.x = -Math.PI * 0.92 * eio(clamp(local)); return yr; }
  // "CUDA USERS" flip counter on the CEO's desk ("outside a few labs, almost nobody used it")
  const CNT = V(ME - 0.6, FY + 0.66, ZD + 0.85), digT = {};
  const digTex = d => (digT[d] ||= canvasTex(128, 160, g => { g.fillStyle = '#121418'; g.fillRect(0, 0, 128, 160); g.fillStyle = '#2a2e36'; g.fillRect(0, 78, 128, 4); g.fillStyle = '#ffffff'; g.font = 'bold 130px InterB, sans-serif'; g.textAlign = 'center'; g.fillText(String(d), 64, 132); }));
  const cnt = new THREE.Group(); cnt.position.copy(CNT); O.add(cnt); cnt.visible = !HOME;
  { const board = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.2, 0.025), new THREE.MeshStandardMaterial({ color: '#1d6b3a', roughness: 0.5 })); board.position.set(0, 0.13, 0); board.rotation.x = -0.18; cnt.add(board);
    const head = new THREE.Mesh(new THREE.PlaneGeometry(0.28, 0.06), new THREE.MeshBasicMaterial({ map: canvasTex(512, 110, g => { g.fillStyle = '#1d6b3a'; g.fillRect(0, 0, 512, 110); g.fillStyle = '#fff'; g.font = 'bold 66px InterB, sans-serif'; g.textAlign = 'center'; g.fillText('CUDA USERS', 256, 80); }) })); head.position.set(0, 0.19, 0.014); head.rotation.x = -0.18; cnt.add(head);
    const dig = new THREE.Mesh(new THREE.PlaneGeometry(0.09, 0.112), new THREE.MeshBasicMaterial({ map: digTex(0) })); dig.position.set(0, 0.1, 0.035); dig.rotation.x = -0.18; cnt.add(dig); cnt.userData.dig = dig; }
  function cntTick(t, flips) {   // flips: [[time, digit], ...] — a quick squash flip at each change
    let d = 0, tf = -9; for (const [ft, fd] of flips) if (t >= ft) { d = fd; tf = ft; }
    const dig = cnt.userData.dig, u = clamp((t - tf) / 0.14); dig.material.map = digTex(d); dig.scale.y = u < 1 ? Math.max(0.05, Math.abs(Math.cos(u * Math.PI))) : 1; }
  // laptop leaderboard (home): ImageNet 2012 top-5 error, the student's net vs the runner-up ("crushed every rival")
  function drawBoard(k) { const g = lg; g.fillStyle = '#0c1220'; g.fillRect(0, 0, 512, 340); g.fillStyle = '#9aa3ad'; g.font = 'bold 26px InterB, sans-serif'; g.fillText('IMAGENET 2012 — ERROR', 22, 44);
    const rows = [['AlexNet', 15.3, '#9cff4a'], ['Next best', 26.2, '#e5483a']];
    rows.forEach(([n, v, col], i) => { const y = 92 + i * 108, w = 300 * (v / 30) * eio(clamp(k * 1.3 - i * 0.15)); g.fillStyle = '#e8ecf3'; g.font = 'bold 28px InterB, sans-serif'; g.fillText(n, 22, y); g.fillStyle = col; g.fillRect(22, y + 14, w, 46); g.fillStyle = '#fff'; g.font = 'bold 34px InterB, sans-serif'; if (k > 0.4) g.fillText(v.toFixed(1) + '%', 34 + w, y + 50); });
    if (k > 0.9) { g.fillStyle = '#ffd400'; g.font = 'bold 44px InterB, sans-serif'; g.fillText('#1  ★', 360, 140); } lapT.needsUpdate = true; lapKey = 'board'; }
  // classroom for the science: 4 big "professor" heads (CPU) vs 512 tiny "student" heads (GPU), exam sheets flying in
  const faceStrip = (glasses) => canvasTex(512, 256, g => { g.fillStyle = '#ffffff'; g.fillRect(0, 0, 512, 256); const cx = 128, cy = 132; g.fillStyle = '#17141a'; for (const s of [-1, 1]) { g.beginPath(); g.ellipse(cx + s * 22, cy - 6, 9, 12, 0, 0, 7); g.fill(); }
    g.strokeStyle = '#17141a'; g.lineWidth = 6; g.beginPath(); g.moveTo(cx - 12, cy + 26); g.quadraticCurveTo(cx, cy + 32, cx + 12, cy + 26); g.stroke();
    if (glasses) { g.lineWidth = 7; for (const s of [-1, 1]) { g.beginPath(); g.arc(cx + s * 24, cy - 6, 19, 0, 7); g.stroke(); } g.beginPath(); g.moveTo(cx - 5, cy - 8); g.lineTo(cx + 5, cy - 8); g.stroke(); } });
  const studTex = faceStrip(false), profTex = faceStrip(true);
  grid.geometry.dispose(); grid.geometry = new THREE.SphereGeometry(0.0128, 14, 10); grid.material = new THREE.MeshBasicMaterial({ map: studTex, toneMapped: false });
  bigC.forEach(m => { m.geometry.dispose(); m.geometry = new THREE.SphereGeometry(0.085, 28, 18); m.material = new THREE.MeshBasicMaterial({ map: profTex, toneMapped: false }); });
  const sheets = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.016, 0.021), new THREE.MeshBasicMaterial({ color: '#ffffff', toneMapped: false, side: THREE.DoubleSide }), 100); sheets.frustumCulled = false; SCI.add(sheets);
  const sciLabel = (txt, col, y) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(0.42, 0.07), new THREE.MeshBasicMaterial({ map: canvasTex(512, 86, g => { g.fillStyle = col; g.font = 'bold 60px InterB, sans-serif'; g.textAlign = 'center'; g.fillText(txt, 256, 64); }), transparent: true, toneMapped: false })); m.position.set(0, y, 0.03); SCI.add(m); return m; };
  const cpuLab = sciLabel('CPU · 4 cores', '#7fc8ff', cpuY + 0.31), gpuLab = sciLabel('GPU · 512 cores', '#9cff4a', gpuY + 0.33);
  function sheetsTick(t, on) {   // GPU: many sheets at once; CPU: one sheet at a time
    for (let k = 0; k < 100; k++) { const gpu = k < 88, rate = gpu ? 1.6 : 0.55, ph = ((t * rate + k * 0.6180339) % 1 + 1) % 1;
      let tx, ty; if (gpu) { const i = (k * 197) % 512; tx = -0.434 + (i % 32) * 0.028; ty = gpuY + 0.21 - ((i / 32) | 0) * 0.028; } else { const i = k % 4; tx = i % 2 ? 0.105 : -0.105; ty = cpuY + (i < 2 ? 0.105 : -0.105); }
      const sx = tx + (gpu ? 0.25 : 0.4) * Math.sin(k * 2.3), sy = ty + 0.55, p = eio(ph), s = on && (gpu || k % 3 === 0) ? Math.max(1e-3, (1 - p) * 1.1) : 1e-3;
      P4.set(lerp(sx, tx, p), lerp(sy, ty, p), 0.07); S4.set(s, s, s); M4.compose(P4, Q4.setFromAxisAngle(V(0, 0, 1), k + t * 3), S4); sheets.setMatrixAt(k, M4); }
    sheets.instanceMatrix.needsUpdate = true; }
  // storm for the doubter's dolly zoom: lightning flashes light the office from the windows
  const boltL = new THREE.DirectionalLight('#cfe0ff', 0); boltL.position.set(-6, 6, -30); scene.add(boltL, boltL.target);
  const flashAt = (t, bolts) => bolts.reduce((m, b) => t >= b ? Math.max(m, Math.exp(-(t - b) * 13) * (1 + 0.6 * Math.sin((t - b) * 90))) : m, 0);
  const officePoints = scene.children.filter(o => o.isPointLight && o !== nightLamp && o !== cardGlow), officePointI = officePoints.map(o => o.intensity);
  // ---- v8 particles: motes in the light for depth (world-fixed volume → parallax; DOF blurs the near ones). Deterministic from t. ----
  const moteTex = canvasTex(64, 64, g => { const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.3, 'rgba(255,255,255,0.6)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); });
  const NM = 1400, motePos = new Float32Array(NM * 3), moteGeo = new THREE.BufferGeometry(); moteGeo.setAttribute('position', new THREE.BufferAttribute(motePos, 3));
  const moteCol = new Float32Array(NM * 3); moteGeo.setAttribute('color', new THREE.BufferAttribute(moteCol, 3));
  const moteMat = new THREE.PointsMaterial({ map: moteTex, size: 0.012, sizeAttenuation: true, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, color: '#ffe2b0', opacity: 0.4, toneMapped: false, vertexColors: true });
  const motes = new THREE.Points(moteGeo, moteMat); motes.frustumCulled = false; motes.renderOrder = 6; scene.add(motes);
  const hsh = i => { const v = Math.sin(i * 12.9898) * 43758.5453; return v - Math.floor(v); };
  const _mp = new THREE.Vector3();
  function motesTick(t, o) {   /* o: center, box [x,y,z] m, color, opacity, size, drift, n (count), lights [V], r (light radius m) */
    motes.visible = o.opacity > 0.01; if (!motes.visible) return; moteMat.color.set(o.color); moteMat.opacity = o.opacity; moteMat.size = o.size; const n = Math.min(NM, o.n || 200); moteGeo.setDrawRange(0, n);
    for (let i = 0; i < NM; i++) { const ph = hsh(i + 19) * 6.283, sp = 0.5 + hsh(i + 29);
      let x = hsh(i + 1) + o.drift[0] * sp * t + 0.012 * Math.sin(t * 0.7 + ph), y = hsh(i + 7) + o.drift[1] * sp * t + 0.01 * Math.sin(t * 0.9 + ph * 1.3), z = hsh(i + 13) + o.drift[2] * sp * t + 0.01 * Math.cos(t * 0.6 + ph);
      x -= Math.floor(x); y -= Math.floor(y); z -= Math.floor(z);
      motePos[i * 3] = o.center.x + (x - 0.5) * o.box[0]; motePos[i * 3 + 1] = o.center.y + (y - 0.5) * o.box[1]; motePos[i * 3 + 2] = o.center.z + (z - 0.5) * o.box[2];
      if (i >= n) continue; _mp.fromArray(motePos, i * 3); let lit = o.lights ? 0 : 1; if (o.lights) for (const L of o.lights) lit = Math.max(lit, o.shaft ? (1 - Math.hypot(_mp.x - L.x, _mp.z - L.z) / o.r) * clamp(1.15 - (L.y - _mp.y) / 4.5) : 1 - _mp.distanceTo(L) / o.r);   /* shaft: dust column under a ceiling lamp */
      const near = clamp((_mp.distanceTo(camera.position) - 0.6) / 0.6); const b = Math.max(0, lit) ** 1.5 * near * (0.55 + 0.45 * Math.sin(t * 2.1 + ph) ** 2); moteCol[i * 3] = moteCol[i * 3 + 1] = moteCol[i * 3 + 2] = b; }
    moteGeo.attributes.color.needsUpdate = true;
    moteGeo.attributes.position.needsUpdate = true; }
  // ---- pose helpers ----
  const stand = (c, x, z, ry = 0, t = 0) => { place(c, x, z, ry, FY); idle(c, t); };
  const type = (c, t) => { const a = 0.03 * Math.sin(t * 28 + c.phase), b = 0.03 * Math.sin(t * 31 + 1 + c.phase); arm(c, 'Left', Lw(c, 0.16, 0.97 + a, 0.52)); arm(c, 'Right', Lw(c, -0.16, 0.97 + b, 0.52)); };
  // v2 motion curves: camera moves start already moving at the cut and settle (no stop-start at every cut); gestures overshoot like a spring
  const cm = u => { u = clamp(u); return 0.75 * u + 0.25 * eio(u); };   /* v8: velocity 0.75 at both ends (no stop-start at cuts), gentle ramp in the middle */
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
    H0: fr(LS(6) - 0.15), H1: fr(WT(7, 'biggest') - 0.1), stu: WT(6, 'student') + 0.3, two: WT(6, 'two') - 0.05, bed: WT(6, 'in', 2) - 0.05, l7: LS(7) - 0.06, crush: WT(7, 'every') - 0.05,
    l8: LS(8) - 0.08, normal: WT(8, 'normal'), four: WT(8, 'four'), that: WT(8, 'that') - 0.1, card8: WT(8, 'card'), five: WT(8, 'five'), l9: LS(9) - 0.1, like: WT(9, 'like'), beat: WT(9, 'beat'), l10: LS(10) - 0.1, all: WT(10, 'all') - 0.06 };
  S.ins = S.math - 0.12; S.qend = TL[2].words[TL[2].words.length - 1].e + 0.2;
  // v7 cues: tag drop, calendar flips, counter flips, leaderboard, lightning, iris into the science
  S.fifty = WT(3, 'fifty'); S.outside = WT(5, 'outside'); S.labs = WT(5, 'labs'); S.nobody5 = WT(5, 'nobody'); S.lapse = S.outside - 0.05; S.rival = WT(7, 'rival'); S.crush = S.rival - 0.05;
  S.bolts = [S.H1 + 0.12, WT(7, 'contest') - 0.05]; S.iris = S.l8 - 0.45; S.calStep = (S.lapse - S.l5 - 0.1) / 6;   // v3: the investor speaks the question himself; laughs start after it
  const officeCast = (t) => { CW.forEach(([c, x], i) => { stand(c, x, CHZ, 0, t); type(c, t + i); face(c, 'calm'); alive(c, t, 0.6); }); };
  let shR = 6;
  function frame(t) {
    resetScene(); nb = 0; bubs.forEach(b => (b.visible = false)); cards.forEach(c => (c.visible = false)); SCI.visible = false; ALL.forEach(c => (c.root.visible = false));
    let dofD = 0, dofA = 0.012, roll = 0, kI = 1.3, rI = 1.5; shR = 6;
    if (HOME) { NIGHT(); const sx = TAB.x, sz = TAB.z - 0.78; motesTick(t, { center: V(TAB.x, 1.45, TAB.z - 0.2), box: [2.4, 1.8, 2.4], color: '#ffc98a', opacity: 1.0, size: 0.018, drift: [0.004, 0.008, 0.003], n: 160, lights: [nightLamp.position], r: 1.3 }); stand(stu, sx, sz, 0, t); face(stu, 'serious'); lean(stu, 0.08); type(stu, t); alive(stu, t, 0.5);
      cards.forEach((cd, i) => { cd.visible = true; cd.position.set(TAB.x + 0.42 + i * 0.05, TAB.y + 0.077, TAB.z + 0.2 - i * 0.2); cd.rotation.set(0, -0.35, 0); cardTick(cd, t + i * 0.3, 0); });
      if (t >= S.l7 - 0.06) drawBoard(btw(t, S.l7 + 0.05, S.rival - 0.1)); else drawLaptop('train', t); const hc = headC(stu), CC = V(TAB.x + 0.44, TAB.y + 0.08, TAB.z + 0.1); kI = 0.9; rI = 1.8;
      if (t < S.stu) { const u = cm(btw(t, S.H0, S.stu)); look(V(lerp(3.0, 4.6, u), lerp(3.4, 1.95, u), lerp(Z + 3.6, Z + 1.3, u)), V(lerp(5.2, sx, u), lerp(0.9, 1.25, u), lerp(Z - 2.4, sz + 0.3, u)), 46); shR = 8; }   // night crane down to the lamp-lit desk
      else if (t < S.two) { const u = cm(btw(t, S.stu, S.two)); look(hc.clone().add(V(0.55, -0.32, lerp(1.6, 1.25, u))), hc.clone().add(V(0, -0.12, 0)), 34); dofD = 1.5; shR = 3; }   // low angle on the student
      else if (t < S.bed) { const u = cm(btw(t, S.two, S.bed)); look(CC.clone().add(V(lerp(0.45, 0.32, u), 0.06 + 0.03 * u, lerp(0.95, 0.7, u))), CC.clone().add(V(0, 0.01, 0)), 38); dofD = lerp(1.05, 0.77, u); dofA = 0.02; shR = 2; }   // ECU: two gaming cards
      else if (t < S.l7) { const u = cm(btw(t, S.bed, S.l7)); look(V(lerp(4.6, 3.3, u), lerp(1.6, 2.2, u), lerp(Z + 1.6, Z + 3.4, u)), V(sx - 0.4, 1.0, sz), 46); shR = 8; }   // pull back: his bedroom
      else if (t < S.crush) { const u = cm(btw(t, S.l7, S.crush)); look(V(sx - 0.28, TAB.y + 0.62, sz - 0.42 + 0.1 * u), lap.position.clone().add(V(0, 0.12, 0.06)), 32); dofD = 0.6; dofA = 0.01; shR = 2; }   // OTS: the laptop recognises everything
      else { const u = cm(btw(t, S.crush, S.H1)), j = spr(t - S.crush); waveArms(stu, t); face(stu, 'laugh'); stu.root.position.y += 0.12 * Math.max(0, Math.sin(Math.min(1, (t - S.crush) * 2.5) * Math.PI)) + Math.abs(Math.sin(t * 7)) * 0.03 * j;
        look(hc.clone().add(V(0.35, -0.2, lerp(1.9, 1.55, u))), hc.clone().add(V(0, -0.15, 0)), 38); bubble(stu, 'YES!', '#2f9e44', t, S.crush); shR = 3; }
    } else {
      LIT(); officeCast(t); const cd = cards[0]; let C = null, xr = 0, scrMode = 'desk', clock = 0;
      let mote = { center: V(1.7, 1.7, ZD + 0.7), box: [6.5, 2.8, 5.5], color: '#ffe0ae', opacity: 1.0, size: 0.02, drift: [0.006, 0.004, 0.002], n: 420, lights: officePoints.map(o => o.position), r: 2.6, shaft: true };
      boltL.intensity = 0; officePoints.forEach((o, i) => (o.intensity = officePointI[i])); post.bloomPass.strength = 0.5; calTick(t, S.l5 + 0.05, S.calStep); cntTick(t, [[S.labs, 1], [S.nobody5, 0]]); cnt.visible = t >= S.l5 && t < S.H0;   /* v11: the board flashed into the hero push for 1–2 frames; it only belongs to the time-lapse */
      stand(ceo, ME, CHZ, 0, t); face(ceo, 'smug'); alive(ceo, t, 0.5);
      if (t < S.nob) { C = hold(ceo, cd, 0, t); xr = Math.min(eio(btw(t, 1.95, 2.6)), 1 - eio(btw(t, 3.75, 4.2))); shR = 3;
        if (t < 1.9) { const u = cm(btw(t, 0, 1.9)); look(C.clone().add(V(C0.w[0] + 0.25 * u, C0.w[1] + 0.12 * u, lerp(C0.w[2], 1.7, u))), vl(C, headC(ceo), 0.45 * u), lerp(C0.f, 38, u)); dofD = lerp(C0.w[2], 1.72, u); }   // open on the card, pull out to the CEO
        else { const u = cm(btw(t, 1.9, S.nob)); look(C.clone().add(V(-0.16 + 0.08 * u, 0.04, lerp(0.8, 0.5, u))), C.clone(), 30); dofD = lerp(0.8, 0.5, u); dofA = 0.016; kI = 0.8; } }   // x-ray push: 512 cores inside
      else if (t < S.cuda - 0.35) { C = hold(ceo, cd, 0.3 * spr(t - S.nob), t); face(ceo, 'grin'); lean(ceo, -0.06); const u = cm(btw(t, S.nob, S.cuda - 0.35));
        [[CW[0][0], 1.3, ZD + 0.8], [CW[2][0], 2.95, ZD + 0.85]].forEach(([c, x, z], i) => { const k = spr(t - S.nob - 0.1 - i * 0.15); stand(c, x, z, yawTo(x, z, ME, CHZ) * Math.min(1, k), t + i); lean(c, 0.12 * k); face(c, 'flat'); headTurn(c, 0, 0.12 * Math.sin(Math.min(1, t - S.nob) * 3)); bubble(c, '?', '#3d7be0', t, S.nob + 0.15 + i * 0.15); });
        look(V(lerp(1.55, 2.6, u), lerp(1.2, 1.42, u), ZD + lerp(3.7, 2.8, u)), V(2.1, 1.3, ZD + 0.1), 46); }   /* v8: more travel (was near-static) */   // nobody asked: blank stares
      else if (t < S.l3) { place(ceo, ME, CHZ, yawTo(ME, CHZ, MX, MZ) * 0.7, FY); idle(ceo, t); type(ceo, t); face(ceo, 'serious'); onDesk(cd, ME - 0.45, ZD - 0.02); scrMode = t < S.cuda ? 'desk' : t < S.math ? 'cuda' : 'math'; shR = 3;
        if (t < S.ins) { const u = cm(btw(t, S.cuda - 0.35, S.ins)); look(V(lerp(ME - 0.42, ME + 0.02, u), lerp(1.74, 1.64, u), CHZ - lerp(0.8, 0.38, u)), V(MX, FY + 0.95, MZ), 30); dofD = lerp(1.35, 0.95, u);   /* v8: arc around his shoulder (was near-static) */ dofA = 0.008; }   // OTS on the monitor: CUDA
        else { const u = cm(btw(t, S.ins, S.l3)), n = V(Math.sin(MR), 0, Math.cos(MR)), P = V(MX, FY + 0.95, MZ).addScaledVector(n, 0.05); ceo.root.visible = false; look(P.clone().addScaledVector(n, lerp(0.98, 0.78, u)).add(V(0.06, 0.03, 0)), P, 34); dofD = lerp(0.98, 0.78, u);   /* v10: a bit wider (was too deep into the screen) */ /* insert: CEO off-camera (his head sat between lens and screen) */ dofA = 0.01; kI = 0.6; } }   // insert: graphics chip → math
      else if (t < S.l5) { // the investor
        C = hold(ceo, cd, t >= S.keep ? 0.1 + 0.3 * spr(t - S.keep) : 0.1, t); scrMode = 'math';
        const walk = btw(t, S.l3, S.inv - 0.15), IP = vl(V(5.3, 0, ZD + 1.5), V(3.15, 0, ZD + 0.75), walk), iry = walk < 1 ? -Math.PI / 2 - 0.3 : yawTo(IP.x, IP.z, ME, CHZ);
        place(inv, IP.x, IP.z, iry, FY); if (walk < 1) SR.clipAt(inv, 'walk', t); else { idle(inv, t); lean(inv, -0.05); } face(inv, flap(t, S.so, S.qend) ? 'smugt' : 'smug'); if (walk >= 1) alive(inv, t, 1.2);
        if (t >= S.inv + 0.15 && t < S.qend) reach(inv, C, Math.min(spr(t - S.inv - 0.15), 1.0 + 0.1 * Math.sin(t * 6)), 'Right');
        if (t >= S.fifty - 0.15 && t < S.inv) { const u = cm(btw(t, S.fifty - 0.15, S.inv)); face(ceo, 'serious'); look(C.clone().add(V(lerp(0.4, 0.12, u), lerp(0.12, 0.03, u), lerp(1.6, 1.0, u))), C.clone().add(V(0.04, -0.04, 0)), 38); dofD = lerp(1.6, 1.0, u); dofA = 0.008; shR = 2; }   // insert: the +50% tag drops on the card
        else if (t < S.inv) { const u = cm(btw(t, S.l3, S.inv)); face(ceo, 'smug'); look(V(lerp(4.6, 4.0, u), 1.45, ZD + 4.6), vl(headC(inv), headC(ceo), 0.2).add(V(0, -0.3, 0)), 40); shR = 6; }   // he walks in
        else if (t < S.so - 0.1) { const u = cm(btw(t, S.inv, S.so - 0.1)); face(ceo, 'serious'); look(V(lerp(1.0, 2.2, u), lerp(1.35, 1.55, u), ZD + lerp(3.9, 2.9, u)), V(2.62, 1.4, ZD + 0.1), 50); dofD = 3.2; dofA = 0.012; shR = 4; }   /* wide two-shot */
        else if (t < S.qend) { const u = cm(btw(t, S.so - 0.1, S.qend)), hi = headC(inv), hcE = headC(ceo); face(ceo, 'serious'); const dI = hcE.clone().sub(hi).setY(0).normalize(), sI = V(-dI.z, 0, dI.x).multiplyScalar(dI.x > 0 ? 1 : -1); if (sI.z < 0) sI.negate(); look(hi.clone().addScaledVector(dI, lerp(1.2, 0.98, u)).addScaledVector(sI, lerp(0.8, 0.65, u)).add(V(0, lerp(0.08, 0.02, u), 0)), hi.clone().add(V(0, -0.08, 0)), lerp(40, 35, u));   /* v8b: investor single from the CEO's side, offset off his head */ const rk = eio(btw(t, S.calc - 0.3, S.calc + 0.15)); dofD = lerp(camera.position.distanceTo(headC(inv)), camera.position.distanceTo(headC(ceo)), rk); dofA = 0.018; shR = 4; }   // two-shot: the question
        else if (t < S.l4) { const w = eio(btw(t, S.qend + 0.05, S.qend + 0.9)),   /* v10: 0.85 s pan (0.22 s read as a jump) */ A = headC(inv), B = headC(CW[1][0]); face(inv, 'laugh'); laughPose(inv, t);
          CW.forEach(([c, x], i) => { stand(c, x, CHZ, yawTo(x, CHZ, ME, CHZ) * 0.8, t); laughPose(c, t + i * 0.4); face(c, 'laugh'); if (i < 2) bubble(c, 'HA', '#e8442a', t, S.qend + 0.07 + i * 0.1); });
          look(V(0.4, 1.55, ZD + 2.4), A.clone().lerp(B, w).add(V(0, -0.1, 0)), 40, (w > 0 && w < 1) ? 0.05 : 0); dofD = 2.6; shR = 5; }   // whip pan: the office laughs
        else { const u = cm(btw(t, S.l4, S.l5)), hc = headC(ceo); face(ceo, flap(t, S.keep, S.keep + 0.7) ? 'serioust' : 'serious'); if (t > S.keep) headTurn(ceo, 0, 0.1 * Math.exp(-4 * (t - S.keep)) * Math.sin((t - S.keep) * 14));
          look(hc.clone().add(V(-0.45, lerp(-0.62, -0.5, u), lerp(1.45, 1.05, u))), hc.clone().add(V(0, -0.08, 0)), 36); dofD = lerp(1.6, 1.2, u); dofA = 0.014; shR = 3; kI = 1.6; rI = 2.0; } }   // low hero push: "keep shipping it"
      else if (t < S.H0) { // time-lapse: six years
        onDesk(cd, ME - 0.45, ZD - 0.02); scrMode = 'wait'; const k = Math.floor((t - S.l5) * 3.2), rnd = n => (Math.sin(k * 12.9898 + n * 78.233) * 43758.5453) % 1;
        SUNDIR.set(Math.cos(k * 0.9) * 0.6, 0.45 + 0.1 * Math.sin(k), -0.75).normalize(); clock = t;
        CW.forEach(([c, x], i) => { if (t > S.lapse + 0.8 && rnd(i) > 0) { c.root.visible = false; return; } stand(c, x + rnd(i + 3) * 0.3, CHZ, rnd(i + 5) * 0.9, t); if (rnd(i + 7) > 0) type(c, t); face(c, rnd(i + 9) > 0.3 ? 'flat' : 'calm'); });
        stand(ceo, ME, CHZ, 0, t); face(ceo, 'flat'); type(ceo, t);
        if (t < S.lapse) { const u = cm(btw(t, S.l5, S.lapse)); look(V(CAL.x + 0.05, CAL.y + 0.02, CAL.z + lerp(2.3, 2.15, u)), V(CAL.x, CAL.y - 0.02, CAL.z), 36); dofD = lerp(2.3, 2.15, u); shR = 4; }   // the wall calendar flips 2006 → 2012
        else { const b = btw(t, S.lapse, S.H0), u = 0.55 * b + 0.45 * (1 - (1 - b) ** 2), cp = CNT.clone().add(V(0, 0.12, 0)); look(cp.clone().add(V(lerp(0.4, 0.04, u), lerp(0.12, 0.03, u), lerp(1.8, 0.85, u))), cp, 38); dofD = lerp(1.8, 0.85, u);   /* v10: enters fast (calendar flicks before) */ dofA = 0.006; shR = lerp(8, 2, u); } }   // push into the counter: 0 → 1 (labs) → 0 (nobody)
      else if (t < S.l8) { // the turn hits the doubter: dolly zoom on the investor
        place(inv, 3.15, ZD + 0.75, 0, FY); idle(inv, t); face(inv, 'pale'); lean(inv, -0.1 * spr(t - S.H1)); onDesk(cd, ME - 0.45, ZD - 0.02); scrMode = 'lab'; face(ceo, 'smug'); CW.forEach(([c, x], i) => { stand(c, x, CHZ, 0, t); face(c, 'wide'); });
        const fl = flashAt(t, S.bolts); renderer.toneMappingExposure = 0.3 + 0.55 * fl; hemi.intensity = 0.22; hemi.color.set('#8090b0'); sun.intensity = 0.6; sun.color.set('#9fb2ff'); U.uSat.value = 0.85; U.uWarm.value = -0.02; boltL.intensity = 7 * fl; boltL.target.position.set(3, 1.5, ZD); officePoints.forEach(o => (o.intensity = 0.4)); face(inv, fl > 0.4 ? 'palet' : 'pale'); mote.color = '#d4e2ff'; mote.opacity = 0.25 + 0.9 * fl; mote.size = 0.02; mote.drift = [0.02, -0.01, 0.006]; mote.lights = null; mote.n = 160;
        const u = cm(btw(t, S.H1, S.l8)), push = eio(btw(t, S.iris, S.l8)), dz = lerp(1.0, 2.9, u) * (1 - 0.7 * push), fov = 2 * Math.atan(0.42 / lerp(1.0, 2.9, u)) * 180 / Math.PI, hc = headC(inv);
        look(V(hc.x + 0.02, hc.y - 0.05 + 0.04 * push, hc.z + dz).add(V(0.012 * Math.sin(t * 80) * fl, 0.012 * Math.cos(t * 70) * fl, 0)), hc.clone().add(V(0, -0.12 * u + 0.05 * push, 0)), fov); roll = -0.09 * u; dofD = dz; dofA = 0.015; bubble(inv, '!', '#e8442a', t, S.H1 + 0.2); shR = 4; kI = 1.6; }
      else if (t < S.l10) { // science: 4 big cores vs 512 small cores
        SCI.visible = true; ALL.forEach(c => (c.root.visible = false)); renderer.toneMappingExposure = 0.24; hemi.intensity = 0.06; sun.intensity = 0.12; U.uVig.value = 0.75; officePoints.forEach(o => (o.intensity = 0)); sheetsTick(t, t >= S.l9); mote = { center: V(SCI.position.x, 1.95, SCI.position.z + 0.3), box: [3.2, 2.6, 3.2], color: '#b4ffc4', opacity: 0.9, size: 0.016, drift: [0.003, 0.01, 0.002], n: 140 };
        post.bloomPass.strength = 0.65 + 1.4 * Math.max(Math.exp(-Math.max(0, t - S.five - 0.25) * 3) * (t >= S.five ? 1 : 0), Math.exp(-Math.max(0, t - S.beat) * 3) * (t >= S.beat ? 1 : 0)); onDesk(cd, ME - 0.45, ZD - 0.02); scrMode = 'lab'; face(ceo, 'smug'); place(inv, 3.15, ZD + 0.75, -0.4, FY); idle(inv, t); face(inv, 'wide'); shR = 4; kI = 1.0; rI = 1.0;
        const run = t >= S.l9 ? 1 : 0; sciTick(t, { cpu: S.normal - 0.1, cubes: S.four - 0.05, gpu: S.card8 - 0.05, grid: S.five - 0.1, run, slow: t >= S.beat - 0.05, cpuProg: run ? 0.06 * btw(t, S.like, S.l10) : 0, gpuProg: run ? eio(btw(t, S.like, S.beat)) : 0 });
        const SP = SCI.position;
        if (t < S.that) { const u = cm(btw(t, S.l8, S.that)); look(V(SP.x + 0.08, cpuY + 0.02, SP.z + lerp(1.9, 1.6, u)), V(SP.x, cpuY - 0.04, SP.z), 34); dofD = lerp(1.9, 1.6, u); }   // CPU: four big cores
        else if (t < S.l9) { const u = cm(btw(t, S.that, S.five + 0.3)); look(V(SP.x + 0.06, lerp(cpuY, gpuY, u), SP.z + lerp(1.6, 1.75, u)), V(SP.x, lerp(cpuY - 0.04, gpuY, u), SP.z), 36); dofD = lerp(1.6, 1.75, u); }   // tilt down: 512 small cores
        else if (t < S.like - 0.1) { const u = cm(btw(t, S.l9, S.like - 0.1)); look(V(SP.x + 0.1, 1.77, SP.z + lerp(2.7, 2.45, u)), V(SP.x, 1.75, SP.z), 46); dofD = lerp(2.7, 2.45, u); }   // both boards: millions of tiny sums
        else if (t < S.beat - 0.05) { const u = cm(btw(t, S.like - 0.1, S.beat - 0.05)); look(V(SP.x - 0.25 + 0.15 * u, gpuY - 0.02, SP.z + lerp(1.5, 1.3, u)), V(SP.x, gpuY - 0.06, SP.z), 38); dofD = lerp(1.5, 1.3, u); }   // GPU: 500 students finish
        else { const u = cm(btw(t, S.beat - 0.05, S.l10)); look(V(SP.x + 0.38 - 0.3 * u, cpuY + 0.02, SP.z + lerp(1.5, 1.05, u)), V(SP.x, cpuY - 0.06, SP.z), 36); dofD = lerp(1.5, 1.05, u);   /* v10: more travel after the GPU beat */ } }   // CPU: four professors still grading
      else { // l10: everyone is in on it; push back into the card (loop to frame 0)
        sun.color.set('#ffc27a'); sun.intensity = 3.6; SUNDIR.set(0.7, 0.28, -0.65).normalize(); U.uWarm.value = 0.13; renderer.toneMappingExposure = 0.46;
        const g = spr(t - S.l10); C = hold(ceo, cd, 0, t); face(ceo, t < S.all ? 'grin' : 'smug'); place(inv, 1.15, ZD + 0.9, 0.35, FY); idle(inv, t); hold(inv, cards[1], 0.25 * g, t + 1); face(inv, 'grin'); scrMode = 'lab';
        [[CW[0][0], 3.15, ZD + 1.0], [CW[1][0], 0.4, ZD + 0.2], [CW[2][0], 3.9, ZD + 0.3]].forEach(([c, x, z], i) => { stand(c, x, z, -0.2 * Math.sign(x - ME), t); waveArms(c, t + i * 0.3); face(c, 'laugh'); c.root.position.y += Math.abs(Math.sin(t * 7 + i)) * 0.04 * g; });
        if (t < S.all) { const u = cm(btw(t, S.l10, S.all)), a = lerp(0.55, -0.15, u), r = lerp(5.0, 4.0, u); look(V(2.15 + Math.sin(a) * r, lerp(2.4, 1.65, u), ZD + 0.2 + Math.cos(a) * r), V(2.15, 1.3, ZD + 0.2), 48); shR = 6; }   /* arc + crane-down */
        else { const u = eio(btw(t, S.all, END - 0.12)), A = headC(ceo).clone().add(V(0.5, -0.1, 2.2)), B = C.clone().add(V(...C0.w)); look(vl(A, B, u), vl(vl(C, headC(ceo), 0.4), C, u), lerp(40, C0.f, u)); dofD = A.distanceTo(B) * (1 - u) + C0.w[2]; shR = 3; } }
      motesTick(t, mote); tagTick(cd, t < S.H0 ? t : -99, S.fifty); cardTick(cd, t, xr); if (cards[1].visible) cardTick(cards[1], t + 0.5, 0); drawScreen(scrMode, t);
      const hands = O.children.filter(o => o.isMesh && Math.abs(o.position.x - 5.6) < 0.01 && Math.abs(o.position.z - (ZB + 0.2)) < 0.01); if (hands.length === 2) { hands[0].rotation.z = -0.6 - clock * 9; hands[1].rotation.z = -2.2 - clock * 60; }
    }
    if (Q.has('dbg')) { const [x, y, z, tx, ty, tz, fv] = Q.get('dbg').split(',').map(Number); look(V(x, y, z), V(tx, ty, tz), fv || 50); dofD = 0; roll = 0; }
    if (dofD === 0 && !Q.has('dbg')) { dofD = camera.position.distanceTo(focus); dofA = 0.007; }
    const loopEdge = t < 0.2 || t > END - 0.25; if (!loopEdge) camera.position.add(hand(t, 0.35));   // light handheld drift (none on the loop frame)
    lightRig(kI, rI);
    ALL.forEach(c => SR.updateLimbs(c)); if (roll) camera.rotateZ(roll);
    post.bokeh.enabled = dofD > 0; if (dofD > 0) { post.bokeh.uniforms.focus.value = dofD; post.bokeh.uniforms.aperture.value = dofA * 1.2; }   /* v10: slightly shallower focus overall */
    const f = HOME ? V(TAB.x, 1, TAB.z) : V(ME, 1, ZD); sun.target.position.copy(f); sun.position.copy(f).addScaledVector(SUNDIR, 60); const sc = sun.shadow.camera; sc.left = sc.bottom = -shR; sc.right = sc.top = shR; sc.near = 1; sc.far = 140; sc.updateProjectionMatrix();
    U.uTime.value = t; post.render(); return canvas.toDataURL('image/jpeg', 0.92); }
  window.frame = t => frame(t + T0); window.DUR = +(Q.get('dur') || END - T0); window.FILM = { END, S }; window.ready = true;
