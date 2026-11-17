// Stage + camera for a long-form scene. Everything inside <Stage> is drawn in 1920×1080 SVG units and scaled to the
// composition. The camera never stops: every shot pushes in (default 5–7 %), optionally rotates, shakes on hits and
// whips out/in with a horizontal blur. Grade is a mild CSS colour filter; Vignette sits outside the camera.
import React, {useId} from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {useScene} from '../context';
import {easeInOut, lerp, rand} from './style';

export const STAGE_W = 1920;
export const STAGE_H = 1080;

export const Stage: React.FC<{children: React.ReactNode; background?: string}> = ({children, background}) => (
  <svg viewBox={`0 0 ${STAGE_W} ${STAGE_H}`} width="100%" height="100%" style={{position: 'absolute', inset: 0, background, overflow: 'visible'}}>
    {children}
  </svg>
);

export type Shake = {at: number; dur?: number; amp?: number}; // seconds from scene start, stage units
export type CameraProps = {
  children: React.ReactNode;
  zoom?: [number, number]; focus?: [number, number]; rotate?: [number, number];
  whipIn?: boolean; whipOut?: boolean; shakes?: Shake[]; grade?: boolean;
};

export const Camera: React.FC<CameraProps> = ({children, zoom = [1, 1.06], focus = [960, 540], rotate = [0, 0], whipIn, whipOut, shakes = [], grade = true}) => {
  const frame = useCurrentFrame(); const {fps, width, height} = useVideoConfig();
  const {scene} = useScene(); const n = scene.durationInFrames;
  const id = useId().replace(/:/g, '');
  const e = easeInOut(frame / Math.max(1, n - 1));
  const k = width / STAGE_W;
  let wx = 0; let blur = 0;
  if (whipOut && n - frame <= 5) {const i = 6 - (n - frame); wx = -i * i * 34; blur = i * 16;}
  if (whipIn && frame < 4) {const i = 4 - frame; wx = i * i * 52; blur = i * 18;}
  let sx = 0; let sy = 0;
  for (const [i, s] of shakes.entries()) {
    const u = (frame / fps - s.at) / (s.dur ?? 0.35);
    if (u >= 0 && u < 1) {const a = (s.amp ?? 14) * (1 - u); sx += a * Math.sin(frame * 2.3 + rand(i) * 6); sy += a * Math.cos(frame * 3.1 + rand(i + 9) * 6);}
  }
  const z = lerp(zoom[0], zoom[1], e); const r = lerp(rotate[0], rotate[1], e);
  const transform = `translate(${width / 2 + (wx + sx) * k}px, ${height / 2 + sy * k}px) scale(${z}) rotate(${r}deg) translate(${-focus[0] * k}px, ${-focus[1] * k}px)`;
  const filters = [grade ? 'saturate(0.94) contrast(0.97) brightness(1.01)' : '', blur ? `url(#${id})` : ''].filter(Boolean).join(' ');
  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      <svg width={0} height={0} style={{position: 'absolute'}}><filter id={id} x="-10%" width="120%"><feGaussianBlur stdDeviation={`${blur} 0.01`} /></filter></svg>
      <div style={{position: 'absolute', left: 0, top: 0, width, height, transformOrigin: '0 0', transform, filter: filters || undefined}}>{children}</div>
    </AbsoluteFill>
  );
};

export const Vignette: React.FC<{strength?: number}> = ({strength = 0.62}) => (
  <AbsoluteFill style={{pointerEvents: 'none', background: `radial-gradient(ellipse 74% 74% at 50% 50%, rgba(0,0,0,0) 42%, rgba(2,3,12,${strength}) 100%)`}} />
);
