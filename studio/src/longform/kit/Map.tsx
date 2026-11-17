// In-world map pieces for the stage: a navy grid, glowing city dots and a dotted route that draws itself with a
// small marker riding its head. Land shapes are drawn per episode (simple ink-outlined paths read best).
import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {Glow} from './Light';
import {FONT, INK, K, PALETTE, easeInOut} from './style';

export const MapGrid: React.FC<{color?: string}> = ({color = PALETTE.navy}) => (
  <g>
    <rect x={-400} y={-400} width={2720} height={1880} fill={color} />
    {Array.from({length: 30}, (_, i) => <line key={`v${i}`} x1={-400 + i * 96} y1={-400} x2={-400 + i * 96} y2={1480} stroke="#fff" strokeOpacity={0.06} strokeWidth={2} />)}
    {Array.from({length: 20}, (_, i) => <line key={`h${i}`} x1={-400} y1={-400 + i * 96} x2={2320} y2={-400 + i * 96} stroke="#fff" strokeOpacity={0.06} strokeWidth={2} />)}
  </g>
);

export const City: React.FC<{x: number; y: number; label?: string; at?: number}> = ({x, y, label, at = 0}) => {
  const t = useCurrentFrame() / useVideoConfig().fps; const k = K(t, at, 0.3);
  if (k <= 0) return null;
  return (
    <g opacity={k}>
      <Glow x={x} y={y} r={60} color={PALETTE.window} a={0.7} />
      <circle cx={x} cy={y} r={11} fill={PALETTE.window} stroke={INK} strokeWidth={5} />
      {label && <text x={x} y={y - 34} textAnchor="middle" fontFamily={FONT.label} fontSize={44} fill={PALETTE.cream} stroke={INK} strokeWidth={9} paintOrder="stroke fill">{label}</text>}
    </g>
  );
};

/** Dotted route through `points` (stage units) revealed between at and at + dur seconds. */
export const Route: React.FC<{points: [number, number][]; at: number; dur: number; color?: string; marker?: boolean}> = ({points, at, dur, color = PALETTE.cream, marker = true}) => {
  const t = useCurrentFrame() / useVideoConfig().fps;
  const seg = points.slice(1).map((p, i) => Math.hypot(p[0] - points[i][0], p[1] - points[i][1]));
  const total = seg.reduce((a, b) => a + b, 0);
  let left = easeInOut(K(t, at, dur)) * total;
  const shown: [number, number][] = [points[0]];
  for (let i = 0; i < seg.length && left > 0; i++) {
    const u = Math.min(1, left / seg[i]); const [a, b] = [points[i], points[i + 1]];
    shown.push([a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u]); left -= seg[i];
  }
  const head = shown[shown.length - 1];
  return (
    <g>
      <polyline points={shown.map((p) => p.join(',')).join(' ')} fill="none" stroke={color} strokeWidth={11} strokeLinecap="round" strokeDasharray="0.1 26" />
      {marker && shown.length > 1 && <circle cx={head[0]} cy={head[1]} r={17} fill={PALETTE.red} stroke={INK} strokeWidth={6} />}
    </g>
  );
};
