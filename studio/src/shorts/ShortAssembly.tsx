// Manifest-driven assembly for shorts whose picture is rendered elsewhere (e.g. a three.js engine): the 3D render is
// one <Video>; Remotion adds light leaks (screen blend), title cards, word-pop captions, voice, ducked music,
// ambience beds and peak-aligned SFX. The manifest lives in the ignored public/media/<slug>/ (private production data).
import {Audio, Video} from '@remotion/media';
import React, {useEffect, useState} from 'react';
import {z} from 'zod';
import {Iris, irisRadius, Whip, whipMotion} from './transitions';
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
  words: Word[]; cards: Card[]; irises?: Iris[]; whips?: Whip[];
};
// Studio controls: per-layer trims in dB on top of the manifest's levels (0 = as built). Drag in the Props panel, listen, render.
export const shortSchema = z.object({
  manifestFile: z.string(),
  music: z.boolean(),
  musicDb: z.number().min(-24).max(18),
  voiceDb: z.number().min(-24).max(12),
  sfxDb: z.number().min(-24).max(12),
  ambienceDb: z.number().min(-24).max(18),
});
export type ShortAssemblyProps = z.infer<typeof shortSchema>;
export const shortDefaults = {music: true, musicDb: 0, voiceDb: 0, sfxDb: 0, ambienceDb: 0};
const dB = (x: number) => Math.pow(10, x / 20);

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

export const ShortAssembly: React.FC<ShortAssemblyProps> = ({manifestFile, music = true, musicDb = 0, voiceDb = 0, sfxDb = 0, ambienceDb = 0}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
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
  const iris = m.irises?.find((i) => frame >= i.from && frame <= i.to);
  const whip = m.whips?.find((w) => Math.abs(frame - w.at) < 3);
  const motion = whip ? whipMotion(frame, whip, width) : {x: 0, blur: 0};
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <svg width="0" height="0" style={{position: 'absolute'}}><defs><filter id="short-whip" x="-30%" y="-5%" width="160%" height="110%"><feGaussianBlur stdDeviation={`${motion.blur} 0`} /></filter></defs></svg>
      <AbsoluteFill style={{clipPath: iris ? `circle(${irisRadius(frame, iris, width, height)}px at ${iris.cx * 100}% ${iris.cy * 100}%)` : undefined}}>
        <AbsoluteFill style={{transform: `translateX(${motion.x}px) scale(${whip ? 1.3 : 1})`, filter: whip ? 'url(#short-whip)' : undefined}}>
          <Video name="three.js render" src={staticFile(m.video)} muted style={{width: '100%', height: '100%'}} />
          {m.leaks.map((l, i) => <Sequence key={`leak${i}`} name={`Light leak ${i + 1}`} from={l.from} durationInFrames={l.durationInFrames}><LeakLayer leak={l} /></Sequence>)}
          <Cards cards={m.cards} />
        </AbsoluteFill>
        <Captions words={m.words} y={m.captionY} />
      </AbsoluteFill>
      <Audio name="Voice" src={staticFile(m.voice.src)} volume={m.voice.volume * dB(voiceDb)} />
      {music && <Audio name="Music (ducked)" src={staticFile(m.music.src)} volume={(f) => Math.min(1, (m.music.volumes[Math.min(f, m.music.volumes.length - 1)] ?? 0) * dB(musicDb))} />}
      {m.beds.map((b, i) => <Sequence key={`bed${i}`} name={`Ambience ${i + 1}`} from={b.from} durationInFrames={b.durationInFrames}><Audio src={staticFile(b.src)} volume={Math.min(1, b.volume * dB(ambienceDb))} loop /></Sequence>)}
      {m.sfx.map((s, i) => (
        <Sequence key={`sfx${i}`} name={`SFX: ${s.note}`} from={s.from} durationInFrames={s.durationInFrames ?? undefined}>
          <Audio src={staticFile(s.src)} volume={Math.min(1, s.volume * dB(sfxDb))} trimBefore={s.trimBefore || undefined} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
