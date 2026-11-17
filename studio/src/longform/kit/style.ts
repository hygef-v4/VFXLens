// Shared look for 2D long-form episodes: ink, palette, fonts and the easing curves every kit piece uses.
import {continueRender, delayRender, staticFile} from 'remotion';

export const INK = '#18161B';
export const LW = 6; // outline width at 1920×1080
export const PALETTE = {
  gold: '#F2C14E', red: '#C8242C', lime: '#B8F04A', cream: '#FFF6DC', paper: '#F3E7C9',
  navy: '#1B2340', night: '#4C5CA0', lamp: '#FFD27A', window: '#FFC25A',
};
// hand/label/marker: ink-puppet-night (Latin only: they miss most Vietnamese letters).
// sans/mono: argument-board and any Vietnamese text (Be Vietnam Pro 500/700, JetBrains Mono; full Vietnamese coverage).
export const FONT = {hand: 'LF Hand', label: 'LF Label', marker: 'LF Marker', sans: 'LF Sans', mono: 'LF Mono'};

const FILES: [string, string, string?][] = [
  [FONT.hand, 'fonts/CaveatBrush-Regular.ttf'],
  [FONT.label, 'fonts/Kalam-Bold.ttf'],
  [FONT.marker, 'fonts/PermanentMarker-Regular.ttf'],
  [FONT.sans, 'fonts/BeVietnamPro-Medium.ttf', '500'],
  [FONT.sans, 'fonts/BeVietnamPro-Bold.ttf', '700'],
  [FONT.mono, 'fonts/JetBrainsMono.ttf', '100 800'],
];
let fontsLoaded: Promise<void> | null = null;
// Call once at the top of a composition; blocks rendering until every face is in document.fonts.
export const loadFonts = () => {
  if (!fontsLoaded) {
    const handle = delayRender('long-form fonts');
    fontsLoaded = Promise.all(FILES.map(async ([family, file, weight]) => {
      const face = new FontFace(family, `url(${staticFile(file)})`, weight ? {weight} : undefined);
      await face.load();
      (document.fonts as unknown as {add: (f: FontFace) => void}).add(face);
    })).then(() => continueRender(handle));
  }
  return fontsLoaded;
};

export const clamp01 = (u: number) => Math.min(1, Math.max(0, u));
export const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
/** Progress 0..1 of a window starting at t0 lasting d (any units, usually seconds). */
export const K = (t: number, t0: number, d: number) => clamp01((t - t0) / d);
export const easeInOut = (u: number) => 0.5 - 0.5 * Math.cos(Math.PI * clamp01(u));
export const easeOut = (u: number) => 1 - (1 - clamp01(u)) ** 3;
/** Snappy overshoot for pose changes: passes 1, peaks slightly above, settles at 1. */
export const back = (u: number, k = 1.9) => {
  const v = clamp01(u) - 1;
  return 1 + (k + 1) * v ** 3 + k * v ** 2;
};
/** Pop-in scale 0 → ~1.15 → 1. */
export const pop = (u: number) => (u <= 0 ? 0 : u >= 1 ? 1 : u < 0.6 ? 1.15 * easeOut(u / 0.6) : 1.15 - 0.15 * easeInOut((u - 0.6) / 0.4));
/** Deterministic pseudo-random in [0,1) for a seed (never Math.random in a render). */
export const rand = (seed: number) => {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
