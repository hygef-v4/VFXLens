// Types shared by the long-form assembly, the kit and episodes, plus the scene context hooks.
import React, {createContext, useContext} from 'react';
import {useCurrentFrame} from 'remotion';
import type {Mouth} from './kit/Puppet';

export type Word = {w: string; from: number; to: number}; // frames, absolute in the episode
export type Line = {id: string; scene: string; speaker: string; text: string; src: string; from: number; durationInFrames: number; volume: number; words: Word[]; mouth: string};
export type Scene = {id: string; kind: string; from: number; durationInFrames: number; card: boolean; props: Record<string, unknown>};
export type Sfx = {src: string; from: number; volume: number; note: string};
export type LongFormManifest = {
  slug: string; title: string; fps: number; width: number; height: number; durationInFrames: number;
  scenes: Scene[]; lines: Line[]; music: {src: string; volumes: number[]} | null; sfx: Sfx[];
};
/** What a scene component receives: its own spec, and its lines with frames relative to the scene start. */
export type SceneProps = {scene: Scene; lines: Line[]};
export type Episode = {slug: string; title: string; scenes: Record<string, React.FC<SceneProps>>};

export const SceneContext = createContext<SceneProps | null>(null);
/** The current scene and its lines (frames relative to the scene). */
export const useScene = () => {
  const s = useContext(SceneContext);
  if (!s) throw new Error('useScene() outside a long-form scene');
  return s;
};
const MOUTH: Record<string, Mouth> = {c: 'flat', m: 'mid', o: 'open'};
/** Mouth shape for a speaker at this frame from the precomputed loudness track, or null when they are not talking. */
export const useSpeech = (speaker: string): Mouth | null => {
  const frame = useCurrentFrame(); const {lines} = useScene();
  const l = lines.find((x) => x.speaker === speaker && frame >= x.from && frame < x.from + x.durationInFrames);
  if (!l) return null;
  return MOUTH[l.mouth[frame - l.from] ?? 'c'] ?? 'flat';
};
/** A line of this scene by id (frames relative to the scene). Throws on a typo so a missing cue fails loudly. */
export const useLine = (id: string) => {
  const l = useScene().lines.find((x) => x.id === id);
  if (!l) throw new Error(`No line ${id} in this scene`);
  return l;
};

