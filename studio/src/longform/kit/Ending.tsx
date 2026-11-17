// Polaroid ending: at `at` seconds the shot freezes with a camera flash, shrinks into a tilted instant photo on a dark
// table, a red marker ring draws around the hero and the handwritten payoff line appears word by word.
import React from 'react';
import {AbsoluteFill, Freeze, useCurrentFrame, useVideoConfig} from 'remotion';
import {FONT, K, PALETTE, back, easeOut, lerp} from './style';

export const PolaroidEnding: React.FC<{at: number; caption: string; ring?: {x: number; y: number; r: number} /* screen position in 1920×1080 units, after the shot's camera */; children: React.ReactNode}> = ({at, caption, ring, children}) => {
  const frame = useCurrentFrame(); const {fps, width, height} = useVideoConfig();
  const atF = Math.round(at * fps); const t = frame / fps;
  if (frame < atF) return <>{children}</>;
  const k = back(K(t, at, 0.45), 1.4);
  const scale = lerp(1, 0.67, k); const rot = lerp(0, -4, k);
  const flash = 1 - K(t, at, 0.22);
  const ringK = easeOut(K(t, at + 0.5, 0.6));
  const circ = ring ? 2 * Math.PI * ring.r : 0;
  return (
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, #2a2420 0%, #0d0b0a 80%)'}}>
      <div style={{position: 'absolute', left: 0, top: 0, width, height, transform: `translate(${width * 0.02 * k}px, ${-height * 0.08 * k}px) scale(${scale}) rotate(${rot}deg)`, transformOrigin: '50% 50%'}}>
        <div style={{position: 'absolute', inset: -0.035 * width, bottom: -0.2 * height, background: PALETTE.cream, boxShadow: '0 30px 80px rgba(0,0,0,0.6)', borderRadius: 6}} />
        <AbsoluteFill style={{overflow: 'hidden'}}><Freeze frame={atF}>{children}</Freeze></AbsoluteFill>
        {ring && (
          <svg viewBox="0 0 1920 1080" width="100%" height="100%" style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
            <circle cx={ring.x} cy={ring.y} r={ring.r} fill="none" stroke={PALETTE.red} strokeWidth={12} strokeLinecap="round"
              strokeDasharray={circ} strokeDashoffset={circ * (1 - ringK)} transform={`rotate(-80 ${ring.x} ${ring.y})`} />
          </svg>
        )}
        <div style={{position: 'absolute', left: 0, right: 0, top: height * 1.03, textAlign: 'center', fontFamily: FONT.hand, fontSize: 124, color: '#2a2018', opacity: k > 0.5 ? 1 : 0}}>
          {caption.split(' ').map((w, i) => {
            const u = K(t, at + 0.9 + i * 0.12, 0.25); // words land one by one after the ring starts
            return <span key={i} style={{display: 'inline-block', marginRight: '0.25em', opacity: u, transform: `translateY(${(1 - back(u, 2)) * 20}px)`}}>{w}</span>;
          })}
        </div>
      </div>
      <AbsoluteFill style={{background: '#fff', opacity: flash}} />
    </AbsoluteFill>
  );
};
