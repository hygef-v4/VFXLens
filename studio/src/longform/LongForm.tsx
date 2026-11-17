// Manifest-driven assembly for 2D long-form episodes. tools/longform-2d/build.py writes public/media/<slug>/longform.json
// (scenes, voice lines with word times and mouth tracks, ducked music, SFX); the episode file supplies one React component
// per scene kind. Picture = Remotion SVG/HTML (+ optional @remotion/three shots); text motion = GSAP seeked by frame.
import {Audio} from '@remotion/media';
import React, {useEffect, useState} from 'react';
import {z} from 'zod';
import {
  AbsoluteFill, CalculateMetadataFunction, cancelRender, continueRender, delayRender, Sequence, staticFile,
} from 'remotion';
import {loadFonts} from './kit/style';
import {EPISODES} from './registry';
import {SceneContext, type LongFormManifest} from './context';
export * from './context';

export const longFormSchema = z.object({
  slug: z.string(),
  music: z.boolean(),
  musicDb: z.number().min(-24).max(18),
  voiceDb: z.number().min(-24).max(12),
  sfxDb: z.number().min(-24).max(12),
});
export type LongFormProps = z.infer<typeof longFormSchema>;
export const longFormDefaults = {music: true, musicDb: 0, voiceDb: 0, sfxDb: 0};
const dB = (x: number) => Math.pow(10, x / 20);

const manifestPath = (slug: string) => {
  if (!/^[a-z0-9-]+$/.test(slug)) throw new Error(`Bad episode slug: ${slug}`);
  return `media/${slug}/longform.json`;
};
const loadManifest = async (slug: string): Promise<LongFormManifest> => {
  const file = manifestPath(slug);
  const r = await fetch(staticFile(file));
  if (!r.ok) throw new Error(`${file}: HTTP ${r.status}. Run studio/tools/longform-2d/build.py in the production folder first.`);
  return r.json();
};
export const calculateLongFormMetadata: CalculateMetadataFunction<LongFormProps> = async ({props}) => {
  const m = await loadManifest(props.slug);
  return {durationInFrames: m.durationInFrames, fps: m.fps, width: m.width, height: m.height};
};

export const LongForm: React.FC<LongFormProps> = ({slug, music = true, musicDb = 0, voiceDb = 0, sfxDb = 0}) => {
  const [m, setM] = useState<LongFormManifest | null>(null);
  const [handle] = useState(() => delayRender('Loading long-form manifest'));
  useEffect(() => {
    let off = false;
    Promise.all([loadManifest(slug), loadFonts()])
      .then(([mm]) => {if (!off) {setM(mm); continueRender(handle);}})
      .catch((e) => cancelRender(e));
    return () => {off = true;};
  }, [slug, handle]);
  if (!m) return null;
  const episode = EPISODES[slug];
  if (!episode) throw new Error(`No episode registered for ${slug} (studio/src/longform/episodes/${slug}/episode.tsx)`);
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {m.scenes.map((s) => {
        const Comp = episode.scenes[s.kind];
        if (!Comp) throw new Error(`Episode ${slug} has no scene component "${s.kind}" (scene ${s.id})`);
        const lines = m.lines.filter((l) => l.scene === s.id).map((l) => ({
          ...l, from: l.from - s.from, words: l.words.map((w) => ({...w, from: w.from - s.from, to: w.to - s.from})),
        }));
        return (
          <Sequence key={s.id} name={`${s.id} · ${s.kind}`} from={s.from} durationInFrames={s.durationInFrames}>
            <SceneContext.Provider value={{scene: s, lines}}><Comp scene={s} lines={lines} /></SceneContext.Provider>
          </Sequence>
        );
      })}
      {m.lines.map((l) => (
        <Sequence key={`v${l.id}`} name={`${l.speaker}: ${l.text.slice(0, 40)}`} from={l.from} durationInFrames={l.durationInFrames} layout="none">
          <Audio src={staticFile(l.src)} volume={Math.min(1, l.volume * dB(voiceDb))} />
        </Sequence>
      ))}
      {music && m.music && (
        <Audio name="Music (ducked)" src={staticFile(m.music.src)}
          volume={(f) => Math.min(1, (m.music!.volumes[Math.min(f, m.music!.volumes.length - 1)] ?? 0) * dB(musicDb))} />
      )}
      {m.sfx.map((s, i) => (
        <Sequence key={`sfx${i}`} name={`SFX: ${s.note}`} from={s.from} layout="none">
          <Audio src={staticFile(s.src)} volume={Math.min(1, s.volume * dB(sfxDb))} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
