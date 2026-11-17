// Every studio/src/longform/episodes/<slug>/episode.tsx exporting `episode` becomes a LongForm-<slug> composition.
// Episodes other than the tracked demo are git-ignored (private productions); webpack picks them up at bundle time.
import type {Episode} from './context';

type WebpackContext = {keys: () => string[]; (key: string): {episode?: Episode}};
const ctx = (require as unknown as {context: (dir: string, deep: boolean, re: RegExp) => WebpackContext})
  .context('./episodes', true, /episode\.tsx$/);

export const EPISODES: Record<string, Episode> = Object.fromEntries(
  ctx.keys().map((k) => ctx(k).episode).filter((e): e is Episode => Boolean(e)).map((e) => [e.slug, e]),
);
