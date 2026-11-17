// Flat ink-line puppet: round head without a neck, pill body, stick legs, thin noodle arms, one uniform outline.
// Drawn in SVG user units with the origin at the feet; place it inside an <svg viewBox="0 0 1920 1080">.
// s = 1 gives a 100-unit head radius (close-up ≈ 2, wide shot ≈ 0.5–0.8). Invent a new Look for every cast member.
import React, {useId} from 'react';
import {INK, LW, back, lerp} from './style';

export type Look = {
  skin: string; skinDark: string; suit: string; suitDark: string; shirt: string; tie?: string;
  bowtie?: boolean; hair?: 'none' | 'slick' | 'bald' | 'bob' | 'curly'; hairColor?: string;
  glasses?: boolean; moustache?: boolean; hat?: 'none' | 'bowler' | 'cap'; hatColor?: string; pocket?: string;
};
export type Eyes = 'dot' | 'half' | 'wide' | 'closed';
export type Mouth = 'smile' | 'smirk' | 'flat' | 'o' | 'mid' | 'open' | 'frown';
export type ArmPose = 'down' | 'pocket' | 'hip' | 'present' | 'gesture' | 'chin' | 'hold' | 'point' | 'shrug';
/** A pose name, or a blend {from, to, k} that snaps with a small overshoot as k goes 0 → 1. */
export type Arm = ArmPose | {from: ArmPose; to: ArmPose; k: number};
/** [hipX, footOffsetX, lift] for each leg. */
export type Legs = [[number, number, number], [number, number, number]];

// Left-arm (screen-left) elbow and hand points relative to the feet; the right arm mirrors them.
const POSES: Record<ArmPose, {elbow: [number, number]; hand: [number, number]; showHand: boolean}> = {
  down: {elbow: [-94, -232], hand: [-100, -168], showHand: true},
  pocket: {elbow: [-98, -230], hand: [-72, -180], showHand: false},
  hip: {elbow: [-132, -236], hand: [-86, -192], showHand: true},
  present: {elbow: [-132, -300], hand: [-212, -334], showHand: true},
  gesture: {elbow: [-138, -266], hand: [-156, -350], showHand: true},
  chin: {elbow: [-126, -262], hand: [-60, -318], showHand: true},
  hold: {elbow: [-98, -238], hand: [-42, -212], showHand: true},
  point: {elbow: [-150, -296], hand: [-246, -312], showHand: true},
  shrug: {elbow: [-142, -250], hand: [-170, -300], showHand: true},
};
const BODY = {top: -342, bottom: -118, halfW: 82, r: 68};
const HEAD = {cy: -424, r: 100};
const SHOULDER: [number, number] = [-54, -290];

const resolveArm = (a: Arm) => {
  if (typeof a === 'string') return POSES[a];
  const k = back(a.k, 1.6); const p = POSES[a.from]; const q = POSES[a.to];
  return {
    elbow: [lerp(p.elbow[0], q.elbow[0], k), lerp(p.elbow[1], q.elbow[1], k)] as [number, number],
    hand: [lerp(p.hand[0], q.hand[0], k), lerp(p.hand[1], q.hand[1], k)] as [number, number],
    showHand: k > 0.5 ? q.showHand : p.showHand,
  };
};

/** Crossing stick legs for a walk; use with bob = 6 * |sin(phase)|. phase ≈ seconds × 11. */
export const walkLegs = (phase: number, stride = 44, lift = 18): Legs => {
  const a = Math.sin(phase);
  return [[-10, a * stride, Math.max(0, Math.cos(phase)) * lift], [10, -a * stride, Math.max(0, -Math.cos(phase)) * lift]];
};
/** True for ~3 frames every period seconds; give each character its own phase. */
export const blinking = (frame: number, fps: number, period = 2.6, phase = 0) => ((frame / fps + phase) % period) < 0.1;

export type PuppetProps = {
  x: number; y: number; s?: number; look: Look;
  /** -1..1 three-quarter turn: features slide toward the facing side, the far eye narrows. */
  face?: number; eyes?: Eyes; mouth?: Mouth; brow?: number; browTilt?: number; pupil?: number;
  arms?: [Arm, Arm]; tilt?: number; bob?: number; squash?: number; legs?: Legs;
  /** Key light side: -1 = from screen-left, 1 = from screen-right. Shadow crescent falls on the other side. */
  light?: number; rim?: string; sweat?: number; flip?: boolean;
};

export const Puppet: React.FC<PuppetProps> = ({
  x, y, s = 1, look, face = 0, eyes = 'dot', mouth = 'smile', brow = 0, browTilt = 0, pupil = 0,
  arms = ['down', 'down'], tilt = 0, bob = 0, squash = 0, legs, light = -1, rim, sweat = -1, flip = false,
}) => {
  const id = useId().replace(/:/g, '');
  const lw = Math.max(LW * 0.9, 4.6 / s); // keep the outline about LW on screen at any scale
  const ink = (w = lw) => ({stroke: INK, strokeWidth: w, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const, fill: 'none'});
  const outline = (w = lw) => ({stroke: INK, strokeWidth: w, strokeLinejoin: 'round' as const});
  const L: Legs = legs ?? [[-24, 0, 0], [24, 0, 0]];
  const bodyPath = `M ${-BODY.halfW} ${BODY.top + BODY.r} a ${BODY.r} ${BODY.r} 0 0 1 ${BODY.r} ${-BODY.r} h ${2 * BODY.halfW - 2 * BODY.r} a ${BODY.r} ${BODY.r} 0 0 1 ${BODY.r} ${BODY.r} V ${BODY.bottom - 40} a 40 40 0 0 1 -40 40 H ${-BODY.halfW + 40} a 40 40 0 0 1 -40 -40 Z`;
  const fx = face * 38; const eyeY = -8; const mx = face * 32; const my = 40;

  const eye = (ex0: number) => {
    const ex = ex0 + fx;
    const far = (face > 0 && ex0 > 0) || (face < 0 && ex0 < 0);
    const sq = far ? 1 - 0.3 * Math.abs(face) : 1;
    const inner = ex0 < 0 ? 1 : -1;
    const by = eyeY - 30 - brow * 9;
    const browEl = <line x1={ex - 13 * sq} y1={by + inner * browTilt * 7 * -1} x2={ex + 13 * sq} y2={by + inner * browTilt * 7} {...ink(lw * 0.78)} />;
    let e: React.ReactNode;
    if (eyes === 'wide') {
      e = <><ellipse cx={ex} cy={eyeY} rx={17 * sq} ry={17} fill="#FBFBF7" {...outline(lw * 0.7)} /><ellipse cx={ex + pupil * 6} cy={eyeY} rx={5.5 * sq} ry={5.5} fill={INK} /></>;
    } else if (eyes === 'closed') {
      e = <path d={`M ${ex - 11 * sq} ${eyeY} Q ${ex} ${eyeY + 9} ${ex + 11 * sq} ${eyeY}`} {...ink(lw * 0.8)} />;
    } else if (eyes === 'half') {
      e = <><path d={`M ${ex - 6.5 * sq} ${eyeY - 3} A ${6.5 * sq} 9 0 0 0 ${ex + 6.5 * sq} ${eyeY - 3} Z`} fill={INK} /><line x1={ex - 13 * sq} y1={eyeY - 4} x2={ex + 13 * sq} y2={eyeY - 4} {...ink(lw * 0.8)} /></>;
    } else {
      e = <><ellipse cx={ex} cy={eyeY} rx={5.5 * sq} ry={8} fill={INK} /><circle cx={ex + 1.5} cy={eyeY - 3} r={1.8} fill="#fff" opacity={0.85} /></>;
    }
    return <g key={ex0}>{e}{browEl}</g>;
  };

  const mouthEl = (() => {
    switch (mouth) {
      case 'smile': return <path d={`M ${mx - 17} ${my - 2} Q ${mx} ${my + 13} ${mx + 17} ${my - 2}`} {...ink(lw * 0.8)} />;
      case 'frown': return <path d={`M ${mx - 15} ${my + 6} Q ${mx} ${my - 6} ${mx + 15} ${my + 6}`} {...ink(lw * 0.8)} />;
      case 'smirk': {const d = face >= 0 ? 1 : -1; return <path d={`M ${mx - 15 * d} ${my + 3} Q ${mx + 4 * d} ${my + 12} ${mx + 20 * d} ${my - 6}`} {...ink(lw * 0.8)} />;}
      case 'flat': return <line x1={mx - 12} y1={my + 2} x2={mx + 12} y2={my + 2} {...ink(lw * 0.8)} />;
      case 'o': return <ellipse cx={mx} cy={my + 1} rx={8} ry={10} fill="#5A1A1E" {...outline(lw * 0.7)} />;
      case 'mid': return <ellipse cx={mx} cy={my + 3} rx={12} ry={7} fill="#5A1A1E" {...outline(lw * 0.7)} />;
      case 'open': return (
        <g>
          <clipPath id={`${id}m`}><path d={`M ${mx - 19} ${my - 4} H ${mx + 19} Q ${mx + 18} ${my + 22} ${mx} ${my + 22} Q ${mx - 18} ${my + 22} ${mx - 19} ${my - 4} Z`} /></clipPath>
          <path d={`M ${mx - 19} ${my - 4} H ${mx + 19} Q ${mx + 18} ${my + 22} ${mx} ${my + 22} Q ${mx - 18} ${my + 22} ${mx - 19} ${my - 4} Z`} fill="#5A1A1E" />
          <g clipPath={`url(#${id}m)`}><rect x={mx - 22} y={my - 6} width={44} height={8} fill="#FAFAF4" /><ellipse cx={mx} cy={my + 17} rx={11} ry={8} fill="#D05860" /></g>
          <path d={`M ${mx - 19} ${my - 4} H ${mx + 19} Q ${mx + 18} ${my + 22} ${mx} ${my + 22} Q ${mx - 18} ${my + 22} ${mx - 19} ${my - 4} Z`} {...ink(lw * 0.7)} />
        </g>
      );
    }
  })();

  const hairColor = look.hairColor ?? '#1C1B22';
  const R = HEAD.r;
  const hairBack = look.hair === 'bob'
    ? <path d={`M ${-R - 14} 10 C ${-R - 18} ${-R - 30} ${R + 18} ${-R - 30} ${R + 14} 10 L ${R + 10} 62 L ${-R - 10} 62 Z`} fill={hairColor} {...outline()} />
    : look.hair === 'bald'
      ? [-1, 1].map((sx) => <path key={sx} d={`M ${sx * 86} -48 Q ${sx * 122} -40 ${sx * 106} -16 Q ${sx * 126} 0 ${sx * 104} 18 Q ${sx * 112} 34 ${sx * 86} 34 Z`} fill={look.hairColor ?? '#8A8A92'} {...outline(lw * 0.8)} />)
      : null;
  const hairFront = look.hair === 'slick'
    ? <path d={`M ${-R - 4} -2 A ${R + 4} ${R + 4} 0 0 1 ${R + 4} -2 Q ${R - 18} -60 ${24 + face * 16} -58 Q ${-46 + face * 16} -66 ${-R - 4} -2 Z`} fill={hairColor} {...outline()} />
    : look.hair === 'bob'
      ? <path d={`M ${-R - 6} 0 C ${-R - 4} ${-R - 20} ${R + 4} ${-R - 20} ${R + 6} 0 C ${R - 10} -50 ${30 + face * 20} -60 ${face * 20} -40 C ${-30 + face * 20} -64 ${-R + 10} -50 ${-R - 6} 0 Z`} fill={hairColor} {...outline()} />
      : look.hair === 'curly'
        ? <g>{[-80, -48, -14, 20, 54, 84].map((cx, i) => <circle key={i} cx={cx} cy={-78 - (i % 2) * 12} r={30} fill={hairColor} {...outline(lw * 0.8)} />)}</g>
        : null;
  const hat = look.hat === 'bowler'
    ? <g><path d={`M ${-R + 6} -56 C ${-R - 2} ${-R - 82} ${R + 2} ${-R - 82} ${R - 6} -56 Z`} fill={look.hatColor ?? '#2E2E38'} {...outline()} /><ellipse cx={0} cy={-55} rx={R + 40} ry={15} fill={look.hatColor ?? '#2E2E38'} {...outline()} /></g>
    : look.hat === 'cap'
      ? <g><path d={`M ${-R + 2} -40 C ${-R} ${-R - 50} ${R} ${-R - 50} ${R - 2} -40 Z`} fill={look.hatColor ?? '#2F6B4E'} {...outline()} /><path d={`M ${face >= 0 ? 0 : -R - 50} -44 h ${R + 50} q 10 14 -6 18 h ${-R - 40} z`} fill={look.hatColor ?? '#2F6B4E'} {...outline(lw * 0.8)} /></g>
      : null;

  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
      {L.map(([hx, dx, lift], i) => <line key={i} x1={hx} y1={BODY.bottom - 8} x2={hx + dx} y2={-lift} {...ink()} />)}
      <g transform={`translate(0 ${-bob}) scale(${1 + squash * 0.6} ${1 - squash})`}>
        {/* body with a hard shadow crescent on the side away from the key light */}
        <clipPath id={`${id}b`}><path d={bodyPath} /></clipPath>
        <g clipPath={`url(#${id}b)`}>
          <rect x={-200} y={-400} width={400} height={400} fill={look.suitDark} />
          <path d={bodyPath} transform={`translate(${light * 16} -5)`} fill={look.suit} />
          <path d={`M -34 ${BODY.top - 4} L 0 ${BODY.top + 96} L 34 ${BODY.top - 4} Z`} fill={look.shirt} />
          {look.bowtie
            ? <g><path d={`M 0 ${BODY.top + 40} l -24 -14 v 28 z M 0 ${BODY.top + 40} l 24 -14 v 28 z`} fill={look.tie ?? '#A8232B'} {...outline(lw * 0.75)} /><circle cx={0} cy={BODY.top + 40} r={5} fill={look.tie ?? '#A8232B'} {...outline(lw * 0.7)} /></g>
            : look.tie && <path d={`M -9 ${BODY.top + 24} H 9 L 13 ${BODY.top + 82} L 0 ${BODY.top + 98} L -13 ${BODY.top + 82} Z`} fill={look.tie} {...outline(lw * 0.75)} />}
          {[-1, 1].map((sx) => <path key={sx} d={`M ${sx * 36} ${BODY.top - 2} L ${sx * 2} ${BODY.top + 98} L ${sx * 2} ${BODY.bottom}`} {...ink(lw * 0.75)} />)}
          {look.pocket && <path d={`M 30 ${BODY.top + 96} L 52 ${BODY.top + 92} L 48 ${BODY.top + 76} L 40 ${BODY.top + 86} L 33 ${BODY.top + 76} Z`} fill={look.pocket} {...outline(lw * 0.55)} />}
        </g>
        <path d={bodyPath} {...ink()} />
        {/* arms over the body */}
        {arms.map((a, i) => {
          const m = i === 0 ? 1 : -1; const p = resolveArm(a);
          const [sx, sy] = [SHOULDER[0] * m, SHOULDER[1]]; const [ex, ey] = [p.elbow[0] * m, p.elbow[1]]; const [hx, hy] = [p.hand[0] * m, p.hand[1]];
          const cx = 2 * ex - (sx + hx) / 2; const cy = 2 * ey - (sy + hy) / 2; // the curve passes through the elbow
          return <g key={i}><path d={`M ${sx} ${sy} Q ${cx} ${cy} ${hx} ${hy}`} {...ink()} />{p.showHand && <circle cx={hx} cy={hy} r={13} fill={look.skin} {...outline(lw * 0.8)} />}</g>;
        })}
        {/* head */}
        <g transform={`translate(0 ${HEAD.cy}) rotate(${tilt})`}>
          {hairBack}
          <clipPath id={`${id}h`}><circle r={R} /></clipPath>
          <g clipPath={`url(#${id}h)`}>
            <rect x={-R} y={-R} width={2 * R} height={2 * R} fill={look.skinDark} />
            <circle cx={light * 7} cy={-17} r={R} fill={look.skin} />
            {rim && <circle cx={-light * 11} cy={4} r={R} fill="none" stroke={rim} strokeOpacity={0.85} strokeWidth={14} />}
          </g>
          <circle r={R} {...ink()} />
          {hairFront}
          {hat}
          {eye(-30)}{eye(30)}
          {look.glasses && <g>{[-30, 30].map((ex0) => <ellipse key={ex0} cx={ex0 + fx} cy={eyeY} rx={24} ry={24} fill="#E1F0FF" fillOpacity={0.22} {...outline(lw * 0.7)} />)}<line x1={fx - 6} y1={eyeY - 3} x2={fx + 6} y2={eyeY - 3} {...ink(lw * 0.7)} /></g>}
          {look.moustache && <path d={`M ${mx} ${my - 17} Q ${mx - 22} ${my - 31} ${mx - 38} ${my - 18} Q ${mx - 20} ${my - 7} ${mx} ${my - 12} Q ${mx + 20} ${my - 7} ${mx + 38} ${my - 18} Q ${mx + 22} ${my - 31} ${mx} ${my - 17} Z`} fill={hairColor} />}
          {mouthEl}
          {sweat >= 0 && (() => {const sx = (face > 0 ? -1 : 1) * 62; const sy = -66 + 30 * (sweat % 1); return <path d={`M ${sx} ${sy - 18} Q ${sx + 14} ${sy + 2} ${sx} ${sy + 9} Q ${sx - 14} ${sy + 2} ${sx} ${sy - 18} Z`} fill="#8FC8EE" {...outline(lw * 0.7)} />;})()}
        </g>
      </g>
    </g>
  );
};
