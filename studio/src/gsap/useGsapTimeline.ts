import gsap from 'gsap';
import {SplitText} from 'gsap/SplitText';
import {useLayoutEffect, useRef, useState} from 'react';
import {cancelRender, continueRender, delayRender, useCurrentFrame, useVideoConfig} from 'remotion';

gsap.registerPlugin(SplitText);
gsap.ticker.lagSmoothing(0);

// Remotion owns time: the timeline is built paused, seeked to frame/fps, never played.
// Wait for fonts first because SplitText measures glyphs.
export const useGsapTimeline = <T extends Element = HTMLDivElement>(build: (tl: gsap.core.Timeline, root: T) => void) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const root = useRef<T>(null);
  const tl = useRef<gsap.core.Timeline | null>(null);
  const [handle] = useState(() => delayRender('gsap fonts'));

  useLayoutEffect(() => {
    let ctx: gsap.Context | undefined;
    document.fonts.ready
      .then(() => {
        ctx = gsap.context(() => {
          tl.current = gsap.timeline({paused: true});
          build(tl.current, root.current!);
        }, root);
        tl.current?.seek(frame / fps, false);
        continueRender(handle);
      })
      .catch(cancelRender);
    return () => ctx?.revert();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useLayoutEffect(() => {
    tl.current?.seek(frame / fps, false);
  }, [frame, fps]);

  return root;
};
