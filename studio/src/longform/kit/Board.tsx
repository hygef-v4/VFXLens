// "argument-board" style pieces (library/styles/argument-board.md). A locked camera on a dark board: meaning builds up,
// the hero of each moment stays bright while older items dim, the question demotes to the board title, a pen line
// carries into the next region, and one "revise" (strike + rewrite) lands each chapter's turn.
// Frame contract: every prop time is in frames relative to the scene (use useLine(id).words[i].from). Fonts come
// from loadFonts() in LongForm (FONT.sans 500/700, FONT.mono). Text ≥ 32 px except titles; weights 500/700 only.
import React, {useMemo} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {useSpeech} from '../context';
import {FONT, clamp01, lerp} from './style';

export const BOARD = {
  paper: '#1C1B19', ink: '#EEE7D8', muted: '#8E887C', accent: '#FF6B2C', core: '#3A3833', faint: '#2A2926',
  sans: `'${FONT.sans}', sans-serif`, mono: `'${FONT.mono}', monospace`,
  margin: 96, railX: 128, col: 300, dim: 0.32,
};
/** Text and data: ease-out, never overshoot. */
export const out3 = (u: number) => 1 - (1 - clamp01(u)) ** 3;
/** Lines and region moves: ease-in-out. */
export const io3 = (u: number) => {const v = clamp01(u); return v < 0.5 ? 4 * v ** 3 : 1 - (-2 * v + 2) ** 3 / 2;};
/** Later items of a group arrive closer together (speed builds up instead of a flat stagger). */
export const accel = (i: number, n: number, spanFrames: number) => spanFrames * Math.sqrt(i / Math.max(1, n));
/** Opacity for focus: 1 while the item is the hero, BOARD.dim after `dimAt`, back to 1 after `undimAt`. */
export const focus = (frame: number, dimAt = Infinity, undimAt = Infinity) =>
  frame < undimAt ? lerp(1, BOARD.dim, out3((frame - dimAt) / 10)) : lerp(BOARD.dim, 1, out3((frame - undimAt) / 10));

let measureCtx: CanvasRenderingContext2D | null = null;
/** Width of a string in the loaded board font (call after loadFonts has resolved). */
export const measure = (s: string, size: number, weight = 700, font = BOARD.sans) => {
  measureCtx ||= document.createElement('canvas').getContext('2d');
  measureCtx!.font = `${weight} ${size}px ${font}`;
  return measureCtx!.measureText(s).width;
};

export const BoardSvg: React.FC<{children: React.ReactNode; opacity?: number}> = ({children, opacity = 1}) => (
  <svg viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', opacity}}>{children}</svg>
);

/** The board: dark paper with a faint 48 px dot grid. */
export const BoardBackground: React.FC = () => {
  const dots = useMemo(() => {
    const out: React.ReactNode[] = [];
    for (let y = 48; y < 1080; y += 48) for (let x = 48; x < 1920; x += 48) out.push(<circle key={`${x}-${y}`} cx={x} cy={y} r={1.6} />);
    return out;
  }, []);
  return (
    <svg viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', background: BOARD.paper}}>
      <g fill={BOARD.ink} opacity={0.07}>{dots}</g>
    </svg>
  );
};

/** Signature: the argument rail. `steps[i]` is the frame chapter i opens; its name runs down the rail beside the node. */
export const ArgumentRail: React.FC<{chapters: string[]; steps: number[]}> = ({chapters, steps}) => {
  const frame = useCurrentFrame();
  const y0 = 220; const gap = Math.min(180, 640 / Math.max(1, chapters.length - 1)); const x = BOARD.railX;
  const cur = Math.max(0, steps.filter((f) => frame >= f).length - 1);
  const fill = steps.reduce((acc, f, i) => (i === 0 ? acc : acc + io3((frame - f) / 14)), 0);
  const k = out3((frame - steps[cur]) / 8);
  return (
    <BoardSvg>
      <line x1={x} y1={y0} x2={x} y2={y0 + gap * (chapters.length - 1)} stroke={BOARD.muted} strokeOpacity={0.3} strokeWidth={3} />
      <line x1={x} y1={y0} x2={x} y2={y0 + gap * fill} stroke={BOARD.ink} strokeWidth={3} />
      {chapters.map((_, i) => {
        const on = i <= cur; const active = i === cur && frame >= steps[0];
        return <circle key={i} cx={x} cy={y0 + gap * i} r={active ? 11 + 3 * k : 8} fill={active ? BOARD.accent : on ? BOARD.ink : BOARD.paper} stroke={on ? 'none' : BOARD.muted} strokeWidth={3} />;
      })}
      {frame >= steps[0] && (
        <text transform={`translate(${x + 30} ${y0 + gap * cur + 18}) rotate(90)`} fontFamily={BOARD.mono} fontSize={30} letterSpacing={6} fill={BOARD.ink} opacity={k}>
          {String(cur + 1).padStart(2, '0')} {chapters[cur].toUpperCase()}
        </text>
      )}
    </BoardSvg>
  );
};

/** Verb "place": chunks land on the frames that say them (6 frames, 10 px rise, no blur, no pop). */
export const Placed: React.FC<{chunks: string[]; at: number[]; style: React.CSSProperties}> = ({chunks, at, style}) => {
  const frame = useCurrentFrame();
  return (
    <div style={{position: 'absolute', whiteSpace: 'nowrap', ...style}}>
      {chunks.map((c, i) => {const u = out3((frame - at[i]) / 6); return <span key={i} style={{display: 'inline-block', marginRight: '0.26em', opacity: u, transform: `translateY(${(1 - u) * 10}px)`}}>{c}</span>;})}
    </div>
  );
};

/** Signature: the chapter question lands big in the centre, holds, then demotes to the board title (top-left, muted). */
export const QuestionTitle: React.FC<{chunks: string[]; at: number[]; demoteAt: number; size?: number}> = ({chunks, at, demoteAt, size = 72}) => {
  const frame = useCurrentFrame();
  const small = 34; const w = measure(chunks.join(' '), size);
  const k = io3((frame - demoteAt) / 22);
  return (
    <Placed chunks={chunks} at={at} style={{
      left: lerp(960 - w / 2, BOARD.col, k), top: lerp(470, 112, k), transform: `scale(${lerp(1, small / size, k)})`, transformOrigin: '0 0',
      fontFamily: BOARD.sans, fontWeight: 700, fontSize: size, color: BOARD.ink, opacity: lerp(1, 0.62, k),
    }} />
  );
};

/** A hand-drawn wobbly line from (x0, y) to (x1, y), drawn on over `frames`. */
export const PenLine: React.FC<{x0: number; x1: number; y: number; at: number; frames?: number; color?: string; width?: number; seed?: number}> = ({x0, x1, y, at, frames = 10, color = BOARD.accent, width = 7, seed = 1}) => {
  const frame = useCurrentFrame(); const k = out3((frame - at) / frames);
  if (k <= 0) return null;
  const n = 10; const pts = Array.from({length: n + 1}, (_, i) => [x0 + ((x1 - x0) * i) / n, y + Math.sin(i * 1.3 + seed) * 4]);
  const d = pts.map((p, i) => `${i ? 'L' : 'M'} ${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ');
  const len = Math.abs(x1 - x0) * 1.05;
  return <BoardSvg><path d={d} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={len} strokeDashoffset={len * (1 - k)} /></BoardSvg>;
};

/**
 * Signature "revise": a claim `lead + wrong` (e.g. "GPU " + "mạnh hơn.") is placed on `showAt`, gets a pen underline
 * (which LineCarry can continue), then `wrong` is struck at `strikeAt` and `right` is written above it at `rewriteAt`.
 */
export const Revise: React.FC<{
  label?: string; lead: string; wrong: string; right: string; x?: number; baseline: number; size?: number;
  showAt: [number, number, number]; strikeAt: number; rewriteAt: number; dimAt?: number; undimAt?: number;
}> = ({label, lead, wrong, right, x = BOARD.col, baseline, size = 96, showAt, strikeAt, rewriteAt, dimAt, undimAt}) => {
  const frame = useCurrentFrame();
  const leadW = measure(lead + ' ', size); const wrongW = measure(wrong, size);
  const dim = focus(frame, dimAt, undimAt);
  const [la, a, b] = showAt.map((f) => out3((frame - f) / 6));
  const ks = out3((frame - strikeAt) / 8); const kr = out3((frame - rewriteAt) / 10);
  const sx0 = x + leadW - 6; const sx1 = x + leadW + wrongW * 0.94; const sy = baseline - size * 0.32; const len = sx1 - sx0 + 20;
  const under = out3((frame - (showAt[2] + 14)) / 10);
  return (
    <>
      {label && <div style={{position: 'absolute', left: x, top: baseline - size - 82, fontFamily: BOARD.mono, fontSize: 32, letterSpacing: 4, color: BOARD.muted, opacity: la * dim * (1 - kr)}}>{label.toUpperCase()}</div>}
      <div style={{position: 'absolute', left: x, top: baseline - size, fontFamily: BOARD.sans, fontWeight: 700, fontSize: size, lineHeight: 1.2, whiteSpace: 'nowrap', opacity: dim}}>
        <span style={{display: 'inline-block', opacity: a, transform: `translateY(${(1 - a) * 10}px)`, color: BOARD.ink}}>{lead}&nbsp;</span>
        <span style={{display: 'inline-block', opacity: b, transform: `translateY(${(1 - b) * 10}px)`, color: ks > 0 ? BOARD.muted : BOARD.ink}}>{wrong}</span>
      </div>
      <BoardSvg opacity={dim}>
        {under > 0 && <line x1={x} y1={baseline + 30} x2={x + (leadW + wrongW) * under} y2={baseline + 30} stroke={BOARD.ink} strokeWidth={4} strokeLinecap="round" opacity={0.85} />}
        {ks > 0 && <path d={`M ${sx0} ${sy + 6} C ${sx0 + 120} ${sy - 4} ${sx1 - 160} ${sy + 10} ${sx1} ${sy - 4}`} fill="none" stroke={BOARD.accent} strokeWidth={10} strokeLinecap="round" strokeDasharray={len} strokeDashoffset={len * (1 - ks)} />}
      </BoardSvg>
      {kr > 0 && (
        <div style={{position: 'absolute', left: x + leadW, top: baseline - size - 104, fontFamily: BOARD.sans, fontWeight: 700, fontSize: size * 0.96, color: BOARD.accent,
          whiteSpace: 'nowrap', clipPath: `inset(-20px ${(1 - kr) * 100}% -20px 0)`, transform: 'rotate(-2deg)', transformOrigin: '0 100%'}}>{right}</div>
      )}
      <PenLine x0={x + leadW} x1={x + leadW + measure(right, size * 0.96)} y={baseline - size - 22} at={rewriteAt + 12} seed={9} />
    </>
  );
};

/** Signature "line-carry": the pen line leaves a point, runs right and draws the frame of the next region. No cut. */
export const LineCarry: React.FC<{at: number; from: [number, number]; box: {x: number; y: number; w: number; h: number}; frames?: number}> = ({at, from, box, frames = 34}) => {
  const frame = useCurrentFrame(); const k = io3((frame - at) / frames);
  if (k <= 0) return null;
  const {x, y, w, h} = box; const [fx, fy] = from;
  const pts: [number, number][] = [[fx, fy], [x, fy], [x, y], [x + w, y], [x + w, y + h], [x, y + h], [x, fy]];
  const total = pts.slice(1).reduce((acc, p, i) => acc + Math.hypot(p[0] - pts[i][0], p[1] - pts[i][1]), 0);
  return (
    <BoardSvg>
      <polyline points={pts.map((p) => p.join(',')).join(' ')} fill="none" stroke={BOARD.ink} strokeWidth={4} strokeLinejoin="round" strokeLinecap="round"
        strokeDasharray={total} strokeDashoffset={total * (1 - k)} />
    </BoardSvg>
  );
};

/** Signature: the skeptic, an index card with a folded corner, peeking in from the bottom margin (4 % overshoot cap). */
export const Skeptic: React.FC<{speaker: string; inAt: number; convincedAt?: number; x?: number}> = ({speaker, inAt, convincedAt = Infinity, x = 940}) => {
  const frame = useCurrentFrame(); const {fps} = useVideoConfig();
  const talk = useSpeech(speaker);
  if (frame < inAt) return null;
  const u = clamp01((frame - inAt) / 12); const rise = u < 0.7 ? 1.04 * out3(u / 0.7) : 1.04 - 0.04 * out3((u - 0.7) / 0.3);
  const conv = out3((frame - convincedAt) / 8);
  const blink = ((frame / fps + 0.7) % 2.8) < 0.1;
  const y = 1080 - 250 * rise + 40; const tilt = talk ? -7 : -3 * (1 - conv); const brow = 6 + 8 * conv;
  const ink = {stroke: BOARD.paper, strokeWidth: 5, strokeLinecap: 'round' as const};
  const mouth = talk === 'open' ? <ellipse cx={0} cy={58} rx={14} ry={11} fill={BOARD.paper} /> : talk === 'mid' ? <ellipse cx={0} cy={58} rx={11} ry={6} fill={BOARD.paper} />
    : conv > 0 ? <path d="M -16 54 Q 0 66 16 54" fill="none" {...ink} /> : <line x1={-12} y1={58} x2={12} y2={56} {...ink} />;
  return (
    <BoardSvg>
      <g transform={`translate(${x} ${y}) rotate(${tilt})`}>
        <path d="M -85 -110 H 55 L 85 -80 V 200 H -85 Z" fill={BOARD.ink} />
        <path d="M 55 -110 V -80 H 85" fill="#D8CFBC" stroke="#BDB39E" strokeWidth={2} />
        <line x1={-85} y1={-70} x2={85} y2={-70} stroke="#E5382F" strokeWidth={3} opacity={0.8} />
        {[0, 1, 2, 3, 4].map((i) => <line key={i} x1={-85} y1={-30 + i * 40} x2={85} y2={-30 + i * 40} stroke="#7FA6C9" strokeWidth={2} opacity={0.45} />)}
        {[-28, 28].map((ex) => (blink ? <line key={ex} x1={ex - 9} y1={10} x2={ex + 9} y2={10} {...ink} /> : <circle key={ex} cx={ex} cy={10} r={8} fill={BOARD.paper} />))}
        <line x1={-40} y1={-14 - brow * (talk ? 1.6 : 1)} x2={-16} y2={-18 - brow} {...ink} />
        <line x1={16} y1={-18 - brow} x2={40} y2={-14 - brow * (conv > 0 ? 1 : 0.4)} {...ink} />
        {mouth}
      </g>
    </BoardSvg>
  );
};

/** A short boxed note so a spoken objection still reads with the sound off. */
export const BoardNote: React.FC<{text: string; at: number; out: number; left?: number; bottom?: number}> = ({text, at, out, left = 620, bottom = 300}) => {
  const frame = useCurrentFrame(); const k = out3((frame - at) / 8) * (1 - out3((frame - out) / 8));
  if (k <= 0) return null;
  return (
    <div style={{position: 'absolute', left, bottom, opacity: k, transform: `translateY(${(1 - k) * 12}px)`, border: `3px solid ${BOARD.ink}`, borderRadius: 14,
      padding: '12px 22px', fontFamily: BOARD.sans, fontWeight: 500, fontSize: 40, color: BOARD.ink, background: BOARD.paper, whiteSpace: 'nowrap'}}>{text}</div>
  );
};
