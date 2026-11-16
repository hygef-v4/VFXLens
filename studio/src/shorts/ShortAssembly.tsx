// Manifest-driven assembly for shorts whose picture is rendered elsewhere (e.g. a three.js engine): the 3D render is
// one <Video>; Remotion adds light leaks (screen blend), title cards, word-pop captions, voice, ducked music,
// ambience beds and peak-aligned SFX. The manifest lives in the ignored public/media/<slug>/ (private production data).
import {Audio, Video} from '@remotion/media';
import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill, CalculateMetadataFunction, cancelRender, continueRender, delayRender, interpolate, Sequence, spring,
  staticFile, useCurrentFrame, useVideoConfig,
} from 'remotion';

type Span = {from: number; to: number};
type Word = Span & {text: string; color: string; speaker: string};
type Card = Span & {text: string; color: string};
type Sfx = {src: string; from: number; trimBefore: number; durationInFrames: number | null; volume: number; note: string};
type Bed = {src: string; from: number; durationInFrames: number; volume: number};
type Leak = {src: string; from: number; durationInFrames: number; opacity: number};
export type ShortManifest = {
  fps: number; durationInFrames: number; width: number; height: number; video: string; font: string; captionY: number;
  voice: {src: string; volume: number}; music: {src: string; volumes: number[]}; beds: Bed[]; sfx: Sfx[]; leaks: Leak[];
  words: Word[]; cards: Card[];
};
export type ShortAssemblyProps = {manifestFile: string; music?: boolean};

const safe = (p: string) => p.startsWith('media/') && !p.includes('..');
const loadManifest = async (file: string): Promise<ShortManifest> => {
  if (!safe(file)) throw new Error('Use a manifest under public/media/.');
  const r = await fetch(staticFile(file)); if (!r.ok) throw new Error(`Manifest ${file}: HTTP ${r.status}`);
  return r.json();
};
export const calculateShortMetadata: CalculateMetadataFunction<ShortAssemblyProps> = async ({props}) => {
  const m = await loadManifest(props.manifestFile);
  return {durationInFrames: m.durationInFrames, fps: m.fps, width: m.width, height: m.height};
};

const STROKE: React.CSSProperties = {WebkitTextStroke: '12px #000', paintOrder: 'stroke fill', textShadow: '0 6px 18px rgba(0,0,0,0.45)'};

// one word at a time, popping in with a spring (≈115% → 100% in a few frames)
const Captions: React.FC<{words: Word[]; y: number}> = ({words, y}) => {
  const frame = useCurrentFrame(); const {fps, height} = useVideoConfig();
  const w = words.find((x) => frame >= x.from && frame < x.to); if (!w) return null;
  const s = spring({frame: frame - w.from, fps, config: {damping: 12, stiffness: 260, mass: 0.6}});
  const scale = interpolate(s, [0, 1], [1.18, 1]); const opacity = interpolate(frame - w.from, [0, 2], [0.4, 1], {extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: height * y, transform: `translateY(-50%) scale(${scale})`, textAlign: 'center', opacity}}>
      <span style={{fontFamily: 'ShortFont', fontSize: 96, color: w.color, letterSpacing: 1, ...STROKE}}>{w.text}</span>
    </div>
  );
};
const Cards: React.FC<{cards: Card[]}> = ({cards}) => {
  const frame = useCurrentFrame(); const {fps, height} = useVideoConfig();
  const c = cards.find((x) => frame >= x.from && frame < x.to); if (!c) return null;
  const s = spring({frame: frame - c.from, fps, config: {damping: 14, stiffness: 220}});
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: height * 0.12, textAlign: 'center', transform: `translateY(${interpolate(s, [0, 1], [-30, 0])}px)`, opacity: s}}>
      <span style={{fontFamily: 'ShortFont', fontSize: 124, color: c.color, ...STROKE}}>{c.text}</span>
    </div>
  );
};
const LeakLayer: React.FC<{leak: Leak}> = ({leak}) => {
  const frame = useCurrentFrame(); const d = leak.durationInFrames;
  const o = leak.opacity * interpolate(frame, [0, 6, d - 10, d], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <Video src={staticFile(leak.src)} muted style={{position: 'absolute', inset: 0, width: '100%', height: '100%', mixBlendMode: 'screen', opacity: o}} />;
};

export const ShortAssembly: React.FC<ShortAssemblyProps> = ({manifestFile, music = true}) => {
  const [m, setM] = useState<ShortManifest | null>(null);
  const [handle] = useState(() => delayRender('Loading short manifest'));
  useEffect(() => {
    let off = false;
    loadManifest(manifestFile).then(async (mm) => {
      const face = new FontFace('ShortFont', `url(${staticFile(mm.font)})`); await face.load(); (document.fonts as unknown as {add: (f: FontFace) => void}).add(face);
      if (!off) {setM(mm); continueRender(handle);}
    }).catch((e) => cancelRender(e));
    return () => {off = true;};
  }, [manifestFile, handle]);
  if (!m) return null;
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <Video name="three.js render" src={staticFile(m.video)} muted style={{width: '100%', height: '100%'}} />
      {m.leaks.map((l, i) => <Sequence key={`leak${i}`} name={`Light leak ${i + 1}`} from={l.from} durationInFrames={l.durationInFrames}><LeakLayer leak={l} /></Sequence>)}
      <Cards cards={m.cards} />
      <Captions words={m.words} y={m.captionY} />
      <Audio name="Voice" src={staticFile(m.voice.src)} volume={m.voice.volume} />
      {music && <Audio name="Music (ducked)" src={staticFile(m.music.src)} volume={(f) => m.music.volumes[Math.min(f, m.music.volumes.length - 1)] ?? 0} />}
      {m.beds.map((b, i) => <Sequence key={`bed${i}`} name={`Ambience ${i + 1}`} from={b.from} durationInFrames={b.durationInFrames}><Audio src={staticFile(b.src)} volume={b.volume} loop /></Sequence>)}
      {m.sfx.map((s, i) => (
        <Sequence key={`sfx${i}`} name={`SFX: ${s.note}`} from={s.from} durationInFrames={s.durationInFrames ?? undefined}>
          <Audio src={staticFile(s.src)} volume={s.volume} trimBefore={s.trimBefore || undefined} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
