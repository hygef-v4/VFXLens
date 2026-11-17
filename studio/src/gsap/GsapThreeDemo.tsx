import gsap from 'gsap';
import {ThreeCanvas} from '@remotion/three';
import {useMemo} from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig} from 'remotion';
import {useGsapTimeline} from './useGsapTimeline';
import {SplitText} from 'gsap/SplitText';

// Scene 1: 2D title, GSAP SplitText.
const Title = ({text}: {text: string}) => {
  const root = useGsapTimeline((tl, el) => {
    const split = SplitText.create(el.querySelector('h1')!, {type: 'chars'});
    tl.from(split.chars, {yPercent: 110, opacity: 0, rotate: 8, duration: 0.6, ease: 'back.out(1.7)', stagger: 0.04});
    tl.to(split.chars, {opacity: 0, y: -30, duration: 0.4, stagger: 0.02}, '+=1.2');
  });
  return (
    <AbsoluteFill ref={root} style={{background: '#10171c', alignItems: 'center', justifyContent: 'center'}}>
      <h1 style={{color: '#f4ead5', fontFamily: 'sans-serif', fontSize: 140, margin: 0, overflow: 'hidden'}}>{text}</h1>
    </AbsoluteFill>
  );
};

// Scene 2: three.js; GSAP tweens a plain object, the frame seeks it, R3F only reads it (no useFrame).
const Cube = () => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const s = useMemo(() => {
    const v = {rot: 0, y: -1.5, scale: 0.2};
    const tl = gsap.timeline({paused: true});
    tl.to(v, {y: 0, scale: 1, duration: 0.9, ease: 'power3.out'}).to(v, {rot: Math.PI * 2, duration: 2.5, ease: 'power1.inOut'}, 0);
    return {v, tl};
  }, []);
  s.tl.seek(frame / fps, false);
  return (
    <ThreeCanvas width={width} height={height}>
      <color attach="background" args={['#10171c']} />
      <ambientLight intensity={0.7} />
      <directionalLight position={[3, 4, 5]} intensity={3} />
      <mesh position-y={s.v.y} scale={s.v.scale} rotation={[0.4, s.v.rot, 0]}>
        <boxGeometry args={[1.5, 1.5, 1.5]} />
        <meshStandardMaterial color="#e4b96c" />
      </mesh>
    </ThreeCanvas>
  );
};

// Long-form pattern: one <Sequence> per scene, each scene owns its own GSAP timeline.
export const GsapThreeDemo = () => (
  <>
    <Sequence durationInFrames={90}><Title text="GSAP + Remotion" /></Sequence>
    <Sequence from={90} durationInFrames={90}><Cube /></Sequence>
  </>
);
