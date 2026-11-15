import {ThreeCanvas} from '@remotion/three';
import {useCurrentFrame, useVideoConfig} from 'remotion';

export const ThreeCheck = () => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  return (
    <ThreeCanvas width={width} height={height}>
      <color attach="background" args={['#10171c']} />
      <ambientLight intensity={0.7} />
      <directionalLight position={[3, 4, 5]} intensity={3} />
      <mesh rotation={[frame / 60, frame / 40, 0]}>
        <boxGeometry args={[1.5, 1.5, 1.5]} />
        <meshStandardMaterial color="#e4b96c" />
      </mesh>
    </ThreeCanvas>
  );
};
