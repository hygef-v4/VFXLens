  // ---------- Starter film: one presenter at the office desk, one shot per narration line ----------
  // Spliced into main.js at // @@FILM@@ by build.py. Serve film.html?viewer=1&film=1[&t0=s&dur=s].
  // Reads ./film/timing.json (voice/fit.py + voice/align.py). Replace the cast, props and shots with your story;
  // keep the frame contract at the bottom (window.frame returns a JPEG data URL for render.cjs).
  ui.style.display = 'none';
  const TJ = await getJ('./film/timing.json'), TL = TJ.lines, END = TJ.duration, T0 = +(Q.get('t0') || 0);
  const ZD = Z - 2.9, ME = 2.1, CHZ = ZD - 0.55;
  const btw = (t, a, b) => clamp((t - a) / (b - a));
  const cm = u => { u = clamp(u); return 0.75 * u + 0.25 * eio(u); };   // keeps velocity through every cut (ease-in-out reads as stop-start)
  const speaking = t => TL.some(l => l.words.some(w => t >= w.t && t < w.e));
  const hero = OUTF[1];
  // Shots: [wide, medium push, low close-up] cycled per line; each starts already moving and ends moving.
  const SHOTS = [
    (u, h) => { const a = lerp(-0.7, 0.25, u), r = lerp(4.6, 3.2, u); look(V(ME + Math.sin(a) * r, lerp(2.1, 1.6, u), CHZ + Math.cos(a) * r), V(ME, 1.25, CHZ), 46); },   // arc + push
    (u, h) => look(h.clone().add(V(lerp(-1.3, -0.45, u), lerp(0.05, -0.12, u), lerp(2.3, 1.35, u))), h.clone().add(V(0, -0.15, 0)), 38),
    (u, h) => { const a = lerp(-0.6, 0.15, u), r = lerp(1.7, 1.0, u); look(h.clone().add(V(Math.sin(a) * r, lerp(-0.5, -0.35, u), Math.cos(a) * r)), h.clone().add(V(0, -0.08, 0)), 34); }];   // arcs move the background: a straight push on flat walls reads as static
  const frame = t => {
    resetScene(); setLook('day'); hemi.intensity = 0.32; sun.intensity = 2.6; SUNDIR.set(0.35, 0.5, -0.75).normalize();
    place(hero, ME, CHZ, 0, FY); idle(hero, t); face(hero, speaking(t) && Math.sin(t * 23) > -0.3 ? 'smugt' : 'smug');
    ALL.forEach(c => SR.updateLimbs(c));
    const i = Math.max(0, TL.findIndex((l, k) => t < (TL[k + 1] ? TL[k + 1].start : END))), a = TL[i].start, b = TL[i + 1] ? TL[i + 1].start : END;
    const h = headC(hero); SHOTS[i % SHOTS.length](cm(btw(t, i ? a : 0, b)), h);
    if (t > 0.2 && t < END - 0.25) camera.position.add(hand(t, 0.35));   // light handheld drift, none on the loop frames
    const dofD = camera.position.distanceTo(h); post.bokeh.enabled = true; post.bokeh.uniforms.focus.value = dofD; post.bokeh.uniforms.aperture.value = 0.012;
    const f = V(ME, 1, ZD); sun.target.position.copy(f); sun.position.copy(f).addScaledVector(SUNDIR, 60); const sc = sun.shadow.camera; sc.left = sc.bottom = -6; sc.right = sc.top = 6; sc.near = 1; sc.far = 140; sc.updateProjectionMatrix();
    U.uTime.value = t; post.render(); return canvas.toDataURL('image/jpeg', 0.92); };
  window.frame = t => frame(t + T0); window.DUR = +(Q.get('dur') || END - T0); window.FILM = { END }; window.ready = true;
