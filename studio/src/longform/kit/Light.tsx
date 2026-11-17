// Night lighting inside a <Stage>: draw the set flat, then <Night> multiplies a navy darkness over everything drawn
// before it with soft holes where lamps, windows and spill fall; <Glow> adds light (screen blend) on bulbs and cones.
import React, {useId} from 'react';
import {PALETTE} from './style';

export type Hole =
  | {kind?: 'pool'; x: number; y: number; r: number; ry?: number; a?: number} // soft round/oval pool, a = 0..1 strength
  | {kind: 'path'; d: string; a?: number; blur?: number}; // any shape: window, lamp cone, floor spill

export const Night: React.FC<{lights: Hole[]; ambient?: string}> = ({lights, ambient = PALETTE.night}) => {
  const id = useId().replace(/:/g, '');
  return (
    <g style={{mixBlendMode: 'multiply'}}>
      <defs>
        <radialGradient id={`${id}g`}>
          <stop offset="0" stopColor="#000" stopOpacity={1} />
          <stop offset="0.5" stopColor="#000" stopOpacity={0.75} />
          <stop offset="1" stopColor="#000" stopOpacity={0} />
        </radialGradient>
        <filter id={`${id}f`} x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation={24} /></filter>
        <mask id={`${id}m`} maskUnits="userSpaceOnUse" x={-2000} y={-2000} width={6000} height={6000}>
          <rect x={-2000} y={-2000} width={6000} height={6000} fill="#fff" />
          {lights.map((l, i) => l.kind === 'path'
            ? <path key={i} d={l.d} fill="#000" fillOpacity={l.a ?? 0.8} filter={l.blur === 0 ? undefined : `url(#${id}f)`} />
            : <ellipse key={i} cx={l.x} cy={l.y} rx={l.r} ry={l.ry ?? l.r} fill={`url(#${id}g)`} opacity={l.a ?? 0.9} />)}
        </mask>
      </defs>
      <rect x={-2000} y={-2000} width={6000} height={6000} fill={ambient} mask={`url(#${id}m)`} />
    </g>
  );
};

export const Glow: React.FC<{x: number; y: number; r: number; color?: string; a?: number}> = ({x, y, r, color = PALETTE.lamp, a = 0.8}) => {
  const id = useId().replace(/:/g, '');
  return (
    <g style={{mixBlendMode: 'screen'}}>
      <radialGradient id={id}><stop offset="0" stopColor={color} stopOpacity={a} /><stop offset="0.5" stopColor={color} stopOpacity={a * 0.4} /><stop offset="1" stopColor={color} stopOpacity={0} /></radialGradient>
      <circle cx={x} cy={y} r={r} fill={`url(#${id})`} />
    </g>
  );
};

/** Soft contact shadow under a character's feet. */
export const GroundShadow: React.FC<{x: number; y: number; w: number}> = ({x, y, w}) => (
  <ellipse cx={x} cy={y + 4} rx={w / 2} ry={w * 0.09} fill="#000" opacity={0.28} />
);
