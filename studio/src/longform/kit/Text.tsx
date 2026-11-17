// Text pieces animated with GSAP timelines (built paused, seeked by frame through useGsapTimeline).
// In-stage pieces (PopLabel, Stamp) are SVG and move with the camera; overlays (TextCard, ChapterTitle, LowerThird,
// LocationTag) are HTML in composition pixels and sit outside the camera.
import gsap from 'gsap';
import {SplitText} from 'gsap/SplitText';
import React from 'react';
import {AbsoluteFill, useVideoConfig} from 'remotion';
import {useGsapTimeline} from '../../gsap/useGsapTimeline';
import type {Word} from '../context';
import {FONT, INK, PALETTE, rand} from './style';

const strokeText = (w: number, color = INK): React.CSSProperties => ({WebkitTextStroke: `${w}px ${color}`, paintOrder: 'stroke fill'});

type Pose = {s: number; r: number; o: number};
/**
 * Tween an SVG group's scale/rotation/opacity about a stage point. GSAP's own SVG origin math goes wrong inside the
 * CSS-scaled camera, so GSAP tweens a plain object and onUpdate writes the attributes (a pure function of the tween).
 */
const svgTween = (tl: gsap.core.Timeline, g: Element, x: number, y: number, from: Pose, to: Pose, vars: gsap.TweenVars, at: number) => {
  const p = {...from};
  const apply = () => {
    g.setAttribute('transform', `translate(${x} ${y}) rotate(${p.r}) scale(${p.s}) translate(${-x} ${-y})`);
    g.setAttribute('opacity', String(p.o));
  };
  apply();
  tl.fromTo(p, from, {...to, ...vars, onUpdate: apply}, at);
  return {p, apply};
};

/**
 * Black card with white handwriting; each word lands when the voice says it (words from the scene's line) or,
 * without words, evenly across `seconds`. Use for chapter cards and punchlines.
 */
export const TextCard: React.FC<{text?: string; words?: Word[]; seconds?: number; size?: number; color?: string}> = ({text, words, seconds = 1.2, size = 132, color = '#fff'}) => {
  const {fps} = useVideoConfig();
  const list = words ? words.map((w) => w.w) : (text ?? '').split(/\s+/).filter(Boolean);
  const times = words ? words.map((w) => Math.max(0, w.from / fps)) : list.map((_, i) => (i / Math.max(1, list.length)) * seconds);
  const root = useGsapTimeline((tl, el) => {
    el.querySelectorAll<HTMLElement>('[data-w]').forEach((node, i) => {
      tl.fromTo(node, {opacity: 0, y: 26, rotate: (rand(i) - 0.5) * 8}, {opacity: 1, y: 0, rotate: (rand(i + 5) - 0.5) * 3, duration: 0.22, ease: 'back.out(2.4)'}, times[i]);
    });
  });
  return (
    <AbsoluteFill ref={root} style={{background: '#000', alignItems: 'center', justifyContent: 'center', padding: '0 8%'}}>
      <div style={{fontFamily: FONT.hand, fontSize: size, color, lineHeight: 1.12, textAlign: 'center'}}>
        {list.map((w, i) => <span key={i} data-w style={{display: 'inline-block', marginRight: '0.28em', opacity: 0}}>{w}</span>)}
      </div>
    </AbsoluteFill>
  );
};

/** Chapter title: characters rise out of a mask one by one (SplitText), then hold. */
export const ChapterTitle: React.FC<{kicker?: string; title: string; at?: number}> = ({kicker, title, at = 0.15}) => {
  const root = useGsapTimeline((tl, el) => {
    const split = SplitText.create(el.querySelector('[data-title]')!, {type: 'chars', mask: 'chars'});
    tl.from(split.chars, {yPercent: 115, duration: 0.5, ease: 'back.out(1.8)', stagger: 0.035}, at);
    const k = el.querySelector('[data-kicker]');
    if (k) tl.from(k, {opacity: 0, letterSpacing: '0.6em', duration: 0.5, ease: 'power2.out'}, at);
  });
  return (
    <AbsoluteFill ref={root} style={{background: '#000', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 18}}>
      {kicker && <div data-kicker style={{fontFamily: FONT.label, fontSize: 44, color: PALETTE.gold, letterSpacing: '0.3em', textTransform: 'uppercase'}}>{kicker}</div>}
      <div data-title style={{fontFamily: FONT.hand, fontSize: 168, color: '#fff', lineHeight: 1}}>{title}</div>
    </AbsoluteFill>
  );
};

/** Hand-lettered label in the stage (SVG) that pops in with an overshoot at `at` seconds and optionally out. */
export const PopLabel: React.FC<{text: string; x: number; y: number; at: number; out?: number; size?: number; color?: string; rotate?: number; font?: string}> = ({text, x, y, at, out, size = 84, color = PALETTE.lime, rotate = -4, font = FONT.label}) => {
  const root = useGsapTimeline<SVGGElement>((tl, el) => {
    const g = el.firstElementChild!;
    const {p, apply} = svgTween(tl, g, x, y, {s: 0.05, r: rotate - 10, o: 0}, {s: 1, r: rotate, o: 1}, {duration: 0.32, ease: 'back.out(2.6)'}, at);
    if (out !== undefined) tl.to(p, {s: 0.05, o: 0, duration: 0.18, ease: 'power2.in', onUpdate: apply}, out);
  });
  return (
    <g ref={root}>
      <g opacity={0}>
        <text x={x} y={y} textAnchor="middle" dominantBaseline="middle" fontFamily={font} fontSize={size} fill={color} stroke={INK} strokeWidth={size * 0.17} strokeLinejoin="round" paintOrder="stroke fill" transform={`skewX(-8) translate(${Math.tan(8 * Math.PI / 180) * y} 0)`}>{text}</text>
      </g>
    </g>
  );
};

/** Rubber stamp that slams down (scale 2.6 → 1 in 0.2 s). Pair it with a Camera shake and a thud SFX at the same time. */
export const Stamp: React.FC<{text: string; x: number; y: number; at: number; size?: number; color?: string; rotate?: number}> = ({text, x, y, at, size = 96, color = PALETTE.red, rotate = -8}) => {
  const w = text.length * size * 0.72 + size; const h = size * 1.6;
  const root = useGsapTimeline<SVGGElement>((tl, el) => {
    svgTween(tl, el.firstElementChild!, x, y, {s: 2.6, r: rotate - 6, o: 0}, {s: 1, r: rotate, o: 1}, {duration: 0.2, ease: 'power4.in'}, at);
  });
  return (
    <g ref={root}>
      <g opacity={0}>
        <rect x={x - w / 2} y={y - h / 2} width={w} height={h} rx={18} fill="none" stroke={color} strokeWidth={10} />
        <rect x={x - w / 2 + 14} y={y - h / 2 + 14} width={w - 28} height={h - 28} rx={10} fill="none" stroke={color} strokeWidth={5} />
        <text x={x} y={y + size * 0.05} textAnchor="middle" dominantBaseline="middle" fontFamily={FONT.marker} fontSize={size} fill={color} letterSpacing={4}>{text}</text>
      </g>
    </g>
  );
};

/** Name lower-third: dark box, gold bar, name and role; scales in with an overshoot. */
export const LowerThird: React.FC<{name: string; role?: string; at?: number; out?: number}> = ({name, role, at = 0.3, out}) => {
  const root = useGsapTimeline((tl, el) => {
    const box = el.querySelector('[data-box]');
    tl.fromTo(box, {scale: 0.6, opacity: 0, transformOrigin: '0% 50%'}, {scale: 1, opacity: 1, duration: 0.35, ease: 'back.out(2)'}, at);
    tl.from(el.querySelectorAll('[data-line]'), {x: -30, opacity: 0, duration: 0.3, stagger: 0.08, ease: 'power3.out'}, at + 0.1);
    if (out !== undefined) tl.to(box, {opacity: 0, x: -40, duration: 0.25, ease: 'power2.in'}, out);
  });
  return (
    <AbsoluteFill ref={root} style={{pointerEvents: 'none'}}>
      <div data-box style={{position: 'absolute', left: '6%', bottom: '11%', display: 'flex', background: 'rgba(16,15,22,0.92)', border: `5px solid ${INK}`, borderRadius: 14, padding: '16px 36px 18px 24px', gap: 22, opacity: 0}}>
        <div style={{width: 12, borderRadius: 6, background: PALETTE.gold}} />
        <div>
          <div data-line style={{fontFamily: FONT.label, fontSize: 70, color: PALETTE.cream, lineHeight: 1.05}}>{name}</div>
          {role && <div data-line style={{fontFamily: FONT.label, fontSize: 38, color: PALETTE.gold}}>{role}</div>}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** Small location / date tag in the lower left. */
export const LocationTag: React.FC<{text: string; at?: number}> = ({text, at = 0.2}) => {
  const root = useGsapTimeline((tl, el) => {
    tl.from(el.querySelector('[data-tag]'), {y: 30, opacity: 0, duration: 0.4, ease: 'power3.out'}, at);
  });
  return (
    <AbsoluteFill ref={root} style={{pointerEvents: 'none'}}>
      <div data-tag style={{position: 'absolute', left: '4.5%', bottom: '6%', fontFamily: FONT.label, fontSize: 46, color: PALETTE.cream, ...strokeText(10)}}>{text}</div>
    </AbsoluteFill>
  );
};
