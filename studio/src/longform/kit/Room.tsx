// Starter interior set (stage units, flat colours, one ink outline): striped wall, wainscot, floor, a window onto a
// night city, curtains, a ticking wall clock, a framed picture, a desk with drawers and a banker's lamp, a rug.
// Sets read as rich when they are dense with props; copy this into an episode and add the story's own objects.
// ROOM_LIGHTS are the matching <Night> holes (lamp pool, window, floor spill).
import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import type {Hole} from './Light';
import {INK, LW, PALETTE, rand} from './style';

const o = (w = LW) => ({stroke: INK, strokeWidth: w, strokeLinejoin: 'round' as const, strokeLinecap: 'round' as const});

export const ROOM_LIGHTS: Hole[] = [
  {x: 1430, y: 640, r: 470, ry: 330, a: 0.95}, // lamp pool on the desk
  {kind: 'path', d: 'M 270 180 H 690 V 560 H 270 Z', a: 0.55}, // window
  {kind: 'path', d: 'M 250 860 L 720 860 L 900 1080 L 120 1080 Z', a: 0.35}, // moonlight spill on the floor
  {x: 960, y: 820, r: 420, ry: 180, a: 0.45}, // where the characters stand
];

const City: React.FC = () => (
  <g>
    {Array.from({length: 9}, (_, i) => {
      const x = 270 + i * 48; const h = 90 + rand(i) * 200; const top = 560 - h;
      return (
        <g key={i}>
          <rect x={x} y={top} width={46} height={h} fill="#151a33" />
          {Array.from({length: Math.floor(h / 28)}, (_, j) => rand(i * 31 + j) > 0.55 && <rect key={j} x={x + 8 + (j % 2) * 18} y={top + 10 + j * 26} width={10} height={12} fill={PALETTE.window} opacity={0.85} />)}
        </g>
      );
    })}
  </g>
);

export const Room: React.FC<{wall?: string; stripe?: string; floor?: string}> = ({wall = '#6F7E9C', stripe = '#667592', floor = '#5B4636'}) => {
  const t = useCurrentFrame() / useVideoConfig().fps;
  const minute = (t / 60) * 360; const second = t * 6;
  return (
    <g>
      {/* wall with stripes, wainscot and floor */}
      <rect x={-200} y={-200} width={2320} height={1100} fill={wall} />
      {Array.from({length: 26}, (_, i) => <rect key={i} x={-200 + i * 96} y={-200} width={44} height={1100} fill={stripe} />)}
      <rect x={-200} y={640} width={2320} height={240} fill="#4E5A73" {...o()} />
      {Array.from({length: 12}, (_, i) => <rect key={i} x={-160 + i * 190} y={672} width={150} height={176} rx={6} fill="none" {...o(LW * 0.6)} />)}
      <rect x={-200} y={880} width={2320} height={400} fill={floor} {...o()} />
      {Array.from({length: 14}, (_, i) => <line key={i} x1={-200 + i * 180} y1={880} x2={-420 + i * 220} y2={1280} {...o(LW * 0.45)} />)}
      {/* window with night city and two reflections */}
      <rect x={270} y={180} width={420} height={380} fill="#0F1430" {...o()} />
      <circle cx={600} cy={250} r={34} fill="#F6F0D2" />
      <City />
      <path d="M 300 200 L 360 200 L 290 300 Z" fill="#fff" opacity={0.12} />
      <line x1={480} y1={180} x2={480} y2={560} {...o()} /><line x1={270} y1={370} x2={690} y2={370} {...o()} />
      <rect x={250} y={560} width={460} height={26} fill="#E9DFC8" {...o()} />
      {/* curtains */}
      <path d="M 210 150 Q 260 360 220 600 L 300 600 Q 330 360 300 150 Z" fill="#8E2C34" {...o()} />
      <path d="M 750 150 Q 700 360 740 600 L 660 600 Q 630 360 660 150 Z" fill="#8E2C34" {...o()} />
      <rect x={190} y={136} width={580} height={22} rx={10} fill="#3A2C22" {...o()} />
      {/* framed picture and clock */}
      <rect x={1050} y={200} width={240} height={170} fill="#C9A86A" {...o()} />
      <rect x={1074} y={222} width={192} height={126} fill="#8FA7B8" {...o(LW * 0.6)} />
      <path d="M 1074 348 L 1140 270 L 1190 320 L 1220 290 L 1266 348 Z" fill="#5E7F5A" />
      <circle cx={1640} cy={250} r={78} fill="#F4EFE2" {...o()} />
      {Array.from({length: 12}, (_, i) => {const a = (i * Math.PI) / 6; return <line key={i} x1={1640 + Math.sin(a) * 60} y1={250 - Math.cos(a) * 60} x2={1640 + Math.sin(a) * 68} y2={250 - Math.cos(a) * 68} {...o(LW * 0.5)} />;})}
      <line x1={1640} y1={250} x2={1640 + Math.sin((minute * Math.PI) / 180) * 50} y2={250 - Math.cos((minute * Math.PI) / 180) * 50} {...o()} />
      <line x1={1640} y1={250} x2={1640 + Math.sin((second * Math.PI) / 180) * 60} y2={250 - Math.cos((second * Math.PI) / 180) * 60} stroke={PALETTE.red} strokeWidth={3} />
      {/* rug */}
      <ellipse cx={960} cy={980} rx={620} ry={90} fill="#7B3A3F" {...o()} />
      <ellipse cx={960} cy={980} rx={540} ry={64} fill="none" stroke="#D9B66A" strokeWidth={6} />
      {/* desk with drawers, papers and lamp */}
      <rect x={1240} y={600} width={520} height={44} rx={8} fill="#6B4A32" {...o()} />
      <rect x={1270} y={644} width={460} height={236} fill="#5A3D29" {...o()} />
      {[0, 1, 2].map((i) => <g key={i}><rect x={1530} y={664 + i * 72} width={180} height={58} rx={6} fill="#6B4A32" {...o(LW * 0.7)} /><circle cx={1620} cy={693 + i * 72} r={7} fill={PALETTE.gold} {...o(LW * 0.4)} /></g>)}
      <rect x={1300} y={584} width={150} height={18} fill="#F4EFE2" transform="rotate(-4 1375 593)" {...o(LW * 0.6)} />
      <rect x={1600} y={586} width={34} height={16} fill="#2E2E38" {...o(LW * 0.6)} />
      <line x1={1618} y1={586} x2={1618} y2={470} {...o()} />
      <path d="M 1540 470 Q 1618 410 1696 470 Z" fill="#2F6B4E" {...o()} />
      <ellipse cx={1618} cy={474} rx={30} ry={9} fill={PALETTE.lamp} />
    </g>
  );
};
