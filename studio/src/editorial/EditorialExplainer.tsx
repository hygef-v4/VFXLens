import {Audio} from '@remotion/media';
import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill, cancelRender, continueRender, delayRender, Easing,
  Interactive, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig,
} from 'remotion';
import {EditorialIllustration, type IllustrationKind} from './Illustrations';
import {ChipStage3D} from './ChipStage3D';

type Point = {label: string; value: string};
type Scene = {
  id: string;
  kind: IllustrationKind;
  chapter: string;
  title: string;
  subtitle: string;
  badge: string;
  source: string;
  from: number;
  durationInFrames: number;
  theme: 'ink' | 'paper' | 'lime';
  points: Point[];
};
type Caption = {startMs: number; endMs: number; text: string};
type Manifest = {
  title: string;
  asOf: string;
  fps: number;
  durationFrames: number;
  audioFile: string;
  scenes: Scene[];
  captions: Caption[];
};
export type EditorialExplainerProps = {manifestFile: string};

const kinds = new Set(['hook', 'timeline', 'handoff', 'context', 'uncertain', 'chip',
  'policy', 'route', 'response', 'questions', 'next', 'recap']);
const safeAsset = (path: string) => /^media\/[\w./-]+$/.test(path) && !path.includes('..');

// A manifest is private production data; reject broken timing before rendering.
const validateManifest = (input: Manifest, fps: number, duration: number): Manifest => {
  if (input.fps !== fps || input.durationFrames !== duration || !safeAsset(input.audioFile)) {
    throw new Error('Manifest must match composition timing and use a local media audio file.');
  }
  if (!Array.isArray(input.scenes) || input.scenes.length === 0 || !Array.isArray(input.captions)) {
    throw new Error('Manifest needs scenes and captions.');
  }
  let end = 0;
  for (const scene of input.scenes) {
    if (scene.from !== end || !Number.isInteger(scene.durationInFrames) ||
      scene.durationInFrames < 30 || !kinds.has(scene.kind) ||
      !['ink', 'paper', 'lime'].includes(scene.theme) ||
      !Array.isArray(scene.points) || scene.points.length > 3 ||
      ['title', 'subtitle', 'chapter', 'badge', 'source'].some((key) =>
        typeof scene[key as keyof Scene] !== 'string')) {
      throw new Error(`Invalid scene or gap in timeline: ${scene.id}`);
    }
    end += scene.durationInFrames;
  }
  if (end !== duration) throw new Error('Scene timeline does not fill the film.');
  let previousEnd = 0;
  for (const caption of input.captions) {
    if (!Number.isFinite(caption.startMs) || !Number.isFinite(caption.endMs) ||
      caption.startMs < previousEnd - 1 || caption.endMs <= caption.startMs ||
      caption.endMs > duration / fps * 1000 + 1 || typeof caption.text !== 'string') {
      throw new Error('Caption times are invalid, overlapping or outside the film.');
    }
    previousEnd = caption.endMs;
  }
  return input;
};

const palette = {
  ink: {bg: '#0B191D', fg: '#F2F0E6', muted: '#A7BAB6', accent: '#B9ED69', card: '#173035', border: '#39514D'},
  paper: {bg: '#F3F0E5', fg: '#122A2C', muted: '#526B65', accent: '#236B55', card: '#E5E8DC', border: '#B9C6B8'},
  lime: {bg: '#CCEE8B', fg: '#112B27', muted: '#365E46', accent: '#1B5B43', card: '#DDF2B7', border: '#8BAB6C'},
};

const PaperGrid = ({color}: {color: string}) => (
  <svg width="1920" height="1080" style={{position: 'absolute', inset: 0, opacity: 0.09}}>
    <defs><pattern id="editorial-grid" width="48" height="48" patternUnits="userSpaceOnUse">
      <path d="M 48 0 L 0 0 0 48" fill="none" stroke={color} strokeWidth="1" />
    </pattern></defs>
    <rect width="1920" height="1080" fill="url(#editorial-grid)" />
  </svg>
);

const LightPass = ({frame, accent, visible}: {frame: number; accent: string; visible: boolean}) => {
  if (!visible) return null;
  const sweep = interpolate(frame, [12, 82], [-620, 2050], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const strength = interpolate(frame, [10, 30, 66, 84], [0, .16, .12, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <>
    <div style={{position: 'absolute', left: sweep, top: -250, width: 340, height: 1600, rotate: '23deg', background: `linear-gradient(90deg, transparent, ${accent}, transparent)`, opacity: strength, mixBlendMode: 'screen', pointerEvents: 'none'}} />
    <svg viewBox="0 0 1920 1080" width="1920" height="1080" style={{position: 'absolute', inset: 0, opacity: .5, pointerEvents: 'none'}}>
      {Array.from({length: 14}, (_, i) => <circle key={i} cx={1020 + (i * 149 % 770) + Math.sin(frame / 70 + i) * 12} cy={700 - (frame * (.38 + i % 3 * .12) + i * 71) % 540} r={i % 3 === 0 ? 2.5 : 1.5} fill={accent} opacity={.16 + (i % 4) * .07} />)}
    </svg>
  </>;
};

const SceneFrame = ({scene, index, count, asOf}: {scene: Scene; index: number; count: number; asOf: string}) => {
  const frame = useCurrentFrame();
  const colors = palette[scene.theme];
  const enter = interpolate(frame, [0, 22], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.16, 1, 0.3, 1)});
  const exit = interpolate(frame, [scene.durationInFrames - 9, scene.durationInFrames - 1], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const longestLine = Math.max(...scene.title.split('\n').map((line) => line.length));
  const headlineSize = longestLine > 22 ? 72 : longestLine > 18 ? 80 : 92;

  return (
    <AbsoluteFill style={{backgroundColor: colors.bg, color: colors.fg, fontFamily: 'VFXEditorial, sans-serif', overflow: 'hidden'}}>
      <PaperGrid color={colors.fg} />
      <LightPass frame={frame} accent={colors.accent} visible={scene.theme === 'ink'} />
      <div style={{position: 'absolute', left: 100, top: 64, right: 100, display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 23, fontWeight: 700, letterSpacing: 2}}>
        <div style={{display: 'flex', gap: 18, alignItems: 'center'}}><span style={{width: 12, height: 12, background: colors.accent, borderRadius: '50%'}} />ĐIỂM TIN CÔNG NGHỆ</div>
        <div style={{color: colors.muted, fontSize: 21, letterSpacing: 1}}>CẬP NHẬT {asOf} <span style={{marginLeft: 42, color: colors.fg}}>{String(index + 1).padStart(2, '0')} / {count}</span></div>
      </div>
      <div style={{position: 'absolute', top: 114, left: 100, right: 100, height: 1, background: colors.border}} />

      <div style={{position: 'absolute', left: 100, top: 167, width: 850, opacity: enter * exit, translate: `0 ${(1 - enter) * 42}px`}}>
        <Interactive.Div name="Chapter label" style={{fontFamily: 'VFXEditorial, sans-serif', color: colors.accent, fontWeight: 700, letterSpacing: 3, fontSize: 25}}>{scene.chapter}</Interactive.Div>
        <Interactive.Div name="Main headline" style={{fontFamily: 'VFXEditorial, sans-serif', fontSize: headlineSize, fontWeight: 900, letterSpacing: -3.5, lineHeight: 1.08, marginTop: 40, whiteSpace: 'pre-line', maxWidth: 880}}>{scene.title}</Interactive.Div>
        <Interactive.Div name="Explanation" style={{fontFamily: 'VFXEditorial, sans-serif', fontSize: 34, lineHeight: 1.4, marginTop: 34, maxWidth: 790, color: colors.muted}}>{scene.subtitle}</Interactive.Div>
        <Interactive.Div name="Evidence status" style={{fontFamily: 'VFXEditorial, sans-serif', marginTop: 36, display: 'inline-block', maxWidth: 810, padding: '13px 18px', border: `1px solid ${colors.border}`, borderRadius: 8, fontSize: 19, fontWeight: 700, lineHeight: 1.4, letterSpacing: 1, backgroundColor: colors.card}}>{scene.badge}</Interactive.Div>
      </div>

      <div style={{position: 'absolute', right: 60, top: 155, width: 900, height: 620, opacity: enter * exit, translate: `${(1 - enter) * 70}px 0`, scale: interpolate(frame, [0, scene.durationInFrames - 1], [1, 1.045], {extrapolateRight: 'clamp'})}}>
        {scene.kind === 'hook' || scene.kind === 'chip'
          ? <ChipStage3D frame={frame} />
          : <EditorialIllustration kind={scene.kind} frame={frame} accent={colors.accent} light={scene.theme !== 'ink'} />}
      </div>

      <div style={{position: 'absolute', left: 100, right: 100, bottom: 233, display: 'flex', gap: 22, opacity: exit}}>
        {scene.points.map((point, i) => {
          const onset = 18 + i * Math.min(60, scene.durationInFrames / 6);
          const reveal = interpolate(frame, [onset, onset + 20], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          return <div key={point.label} style={{flex: 1, minWidth: 0, padding: '17px 24px', borderTop: `3px solid ${colors.accent}`, background: colors.card, opacity: reveal, translate: `0 ${(1 - reveal) * 22}px`}}>
            <div style={{color: colors.muted, fontSize: 21, marginBottom: 9, fontWeight: 700, letterSpacing: 1}}>{point.label}</div>
            <div style={{fontSize: point.value.length > 30 ? 29 : 35, fontWeight: 700, lineHeight: 1.2}}>{point.value}</div>
          </div>;
        })}
      </div>

      <div style={{position: 'absolute', left: 100, right: 100, bottom: 35, color: colors.muted, fontSize: 22, display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <span>{scene.source}</span><span style={{fontSize: 17, letterSpacing: 1}}>ĐỒ HỌA MINH HỌA</span>
      </div>
    </AbsoluteFill>
  );
};

const CaptionLayer = ({captions}: {captions: Caption[]}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const now = frame / fps * 1000;
  const current = captions.find((caption) => caption.startMs <= now && caption.endMs > now);
  if (!current) return null;
  return <div style={{position: 'absolute', bottom: 90, left: 120, right: 120, display: 'flex', justifyContent: 'center', pointerEvents: 'none'}}>
    <div style={{fontFamily: 'VFXEditorial, sans-serif', background: '#071417F2', color: '#FFFFFF', border: '1px solid #60736B', borderRadius: 12, padding: '17px 32px', fontSize: 38, fontWeight: 400, lineHeight: 1.32, textAlign: 'center', maxWidth: 1550, whiteSpace: 'pre-line'}}>{current.text}</div>
  </div>;
};

const Progress = ({duration}: {duration: number}) => {
  const frame = useCurrentFrame();
  return <div style={{position: 'absolute', bottom: 0, left: 0, height: 6, background: '#76B844', width: `${(frame + 1) / duration * 100}%`}} />;
};

export const EditorialExplainer = ({manifestFile}: EditorialExplainerProps) => {
  const {fps, durationInFrames} = useVideoConfig();
  const [manifest, setManifest] = useState<Manifest | null>(null);
  const [handle] = useState(() => delayRender('Loading private editorial manifest'));

  useEffect(() => {
    let disposed = false;
    if (!safeAsset(manifestFile)) {cancelRender(new Error('Use a manifest under public/media/.')); return;}
    const loadedFonts = Promise.all(['400', '700'].map(async (weight) => {
      const loaded = await document.fonts.load(`${weight} 40px VFXEditorial`, 'Tiếng Việt');
      if (loaded.length === 0) throw new Error('Editorial font did not load.');
    }));
    const data = fetch(staticFile(manifestFile))
      .then((response) => {if (!response.ok) throw new Error(`Cannot read manifest: HTTP ${response.status}`); return response.json();});
    Promise.all([data, loadedFonts])
      .then(([input]) => {
        const checked = validateManifest(input, fps, durationInFrames);
        if (!disposed) {setManifest(checked); continueRender(handle);}
      })
      .catch((error: unknown) => {if (!disposed) cancelRender(error instanceof Error ? error : new Error(String(error)));});
    return () => {disposed = true;};
  }, [manifestFile, fps, durationInFrames, handle]);

  const fontStyles = <style>{`
    @font-face {font-family:VFXEditorial;src:url("${staticFile('media/editorial-fonts/regular.ttf')}") format("truetype");font-weight:400;font-display:block;}
    @font-face {font-family:VFXEditorial;src:url("${staticFile('media/editorial-fonts/bold.ttf')}") format("truetype");font-weight:700;font-display:block;}
  `}</style>;
  if (!manifest) return fontStyles;
  return <AbsoluteFill>
    {fontStyles}
    {manifest.scenes.map((scene, index) => <Sequence key={scene.id} name={scene.chapter} from={scene.from} durationInFrames={scene.durationInFrames}>
      <SceneFrame scene={scene} index={index} count={manifest.scenes.length} asOf={manifest.asOf} />
    </Sequence>)}
    <Audio name="Narration and sound design" src={staticFile(manifest.audioFile)} />
    <CaptionLayer captions={manifest.captions} />
    <Progress duration={durationInFrames} />
  </AbsoluteFill>;
};
