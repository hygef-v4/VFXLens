import React, {useEffect, useLayoutEffect, useMemo, useRef} from 'react';
import {ThreeCanvas} from '@remotion/three';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {useThree} from '@react-three/fiber';
import {
  Color,
  Group,
  IcosahedronGeometry,
  InstancedMesh,
  MeshStandardMaterial,
  Object3D,
  PerspectiveCamera,
  ShaderMaterial,
} from 'three';

const CAMERA = {position: [4.1, 2.5, 7.6] as [number, number, number], fov: 34, near: 0.1, far: 60};
const QUALITY = {dpr: 1, shadows: 'percentage' as const};
const PARTICLE_COUNT = 96;
const COLORS = {
  background: '#0b1117',
  ceramic: '#d9e0df',
  metal: '#82949a',
  ink: '#11191d',
  cyan: '#77ead8',
  warm: '#ffbf73',
};

const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
const smoothstep = (x: number) => {
  const t = clamp01(x);
  return t * t * (3 - 2 * t);
};

// A stateless integer hash gives each particle stable attributes without render-order state.
const remotionRandom = (seed: number, index: number, lane: number) => {
  let x = (seed ^ Math.imul(index + 1, 0x9e3779b1) ^ Math.imul(lane + 1, 0x85ebca6b)) >>> 0;
  x = Math.imul(x ^ (x >>> 16), 0x7feb352d);
  x = Math.imul(x ^ (x >>> 15), 0x846ca68b);
  return ((x ^ (x >>> 16)) >>> 0) / 4294967296;
};

const CameraTrack = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const camera = useThree((state) => state.camera as PerspectiveCamera);

  useLayoutEffect(() => {
    const p = smoothstep(frame / Math.max(1, durationInFrames - 1));
    camera.position.set(4.1 - 0.8 * p, 2.5 - 0.32 * p, 7.6 - 0.95 * p);
    camera.lookAt(0, 0.96 + 0.08 * p, 0);
    camera.updateMatrixWorld();
  }, [camera, durationInFrames, frame]);

  return null;
};

const ProductMotion = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const group = useRef<Group>(null);

  useLayoutEffect(() => {
    if (!group.current) return;
    const seconds = frame / fps;
    group.current.rotation.y = -0.3 + seconds * 0.1;
    group.current.position.y = -0.2 * (1 - smoothstep(frame / 16));
  }, [fps, frame]);

  return (
    <group ref={group}>
      <mesh position={[0, 1.02, 0]} castShadow receiveShadow>
        <cylinderGeometry args={[0.72, 0.78, 2.05, 64, 1, false]} />
        <meshStandardMaterial color={COLORS.ceramic} metalness={0.18} roughness={0.26} />
      </mesh>
      <mesh position={[0, 0.12, 0]} castShadow>
        <cylinderGeometry args={[0.79, 0.79, 0.19, 64]} />
        <meshStandardMaterial color={COLORS.metal} metalness={0.86} roughness={0.2} />
      </mesh>
      <mesh position={[0, 2.05, 0]} castShadow>
        <cylinderGeometry args={[0.72, 0.7, 0.12, 64]} />
        <meshStandardMaterial color={COLORS.metal} metalness={0.82} roughness={0.2} />
      </mesh>
      <mesh position={[0, 1.02, 0.82]}>
        <torusGeometry args={[0.42, 0.045, 12, 64]} />
        <meshStandardMaterial color={COLORS.metal} metalness={0.9} roughness={0.19} />
      </mesh>
      <mesh position={[0, 1.02, 0.825]}>
        <circleGeometry args={[0.375, 64]} />
        <meshStandardMaterial color={COLORS.ink} metalness={0.3} roughness={0.48} />
      </mesh>
      <mesh position={[0, 1.02, 0.84]}>
        <torusGeometry args={[0.23, 0.018, 8, 48]} />
        <meshStandardMaterial color={COLORS.cyan} emissive={COLORS.cyan} emissiveIntensity={0.42} metalness={0.45} roughness={0.24} />
      </mesh>
      <mesh position={[0, 1.02, 0.845]}>
        <circleGeometry args={[0.205, 48]} />
        <meshStandardMaterial color="#26363a" metalness={0.35} roughness={0.36} />
      </mesh>
      <mesh position={[0, 2.12, 0]}>
        <sphereGeometry args={[0.09, 24, 16]} />
        <meshStandardMaterial color={COLORS.warm} emissive={COLORS.warm} emissiveIntensity={1.25} />
      </mesh>
      <mesh position={[0, 0.32, 0.739]}>
        <boxGeometry args={[0.24, 0.035, 0.018]} />
        <meshStandardMaterial color={COLORS.cyan} emissive={COLORS.cyan} emissiveIntensity={0.55} />
      </mesh>
    </group>
  );
};

const makeParticleSeeds = () => Array.from({length: PARTICLE_COUNT}, (_, i) => ({
  angle: remotionRandom(503, i, 0) * Math.PI * 2,
  radius: 2.6 + remotionRandom(503, i, 1) * 1.8,
  height: (remotionRandom(503, i, 2) - 0.5) * 3.3,
  depth: (remotionRandom(503, i, 3) - 0.5) * 2.6,
  phase: remotionRandom(503, i, 4) * Math.PI * 2,
  speed: 0.16 + remotionRandom(503, i, 5) * 0.2,
  size: 0.55 + remotionRandom(503, i, 6) * 0.75,
}));

const ParticleFlow = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const ref = useRef<InstancedMesh>(null);
  const seeds = useMemo(makeParticleSeeds, []);
  const geometry = useMemo(() => new IcosahedronGeometry(1, 0), []);
  const material = useMemo(() => new MeshStandardMaterial({
    color: new Color(COLORS.cyan),
    emissive: new Color(COLORS.cyan),
    emissiveIntensity: 0.48,
    roughness: 0.28,
    metalness: 0.3,
  }), []);
  const dummy = useMemo(() => new Object3D(), []);

  useEffect(() => () => {
    geometry.dispose();
    material.dispose();
  }, [geometry, material]);

  useLayoutEffect(() => {
    const mesh = ref.current;
    if (!mesh) return;
    const seconds = frame / fps;
    const gather = smoothstep((seconds - 0.3) / 1.25);
    seeds.forEach((seed, i) => {
      const angle = seed.angle + seconds * seed.speed;
      const radius = seed.radius * (1 - gather) + (1.5 + seed.size * 0.48) * gather;
      dummy.position.set(
        Math.cos(angle) * radius,
        seed.height * (1 - gather) + (0.38 + Math.sin(angle * 2 + seed.phase) * 0.24) * gather,
        seed.depth * (1 - gather) + Math.sin(angle) * radius * 0.44 * gather,
      );
      const pulse = 0.76 + 0.24 * Math.sin(seconds * 2.4 + seed.phase);
      dummy.scale.setScalar(0.025 * seed.size * pulse);
      dummy.rotation.set(seed.phase + seconds * 0.2, angle, seed.phase * 0.4);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);
    });
    mesh.instanceMatrix.needsUpdate = true;
  }, [dummy, fps, frame, seeds]);

  return <instancedMesh ref={ref} args={[geometry, material, PARTICLE_COUNT]} dispose={null} frustumCulled={false} />;
};

const ContactShadow = () => {
  const material = useMemo(() => new ShaderMaterial({
    transparent: true,
    depthWrite: false,
    vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
    fragmentShader: 'varying vec2 vUv; void main(){ float d = length((vUv - 0.5) * 2.0); float a = (1.0 - smoothstep(0.18, 1.0, d)) * 0.28; gl_FragColor = vec4(0.01, 0.04, 0.05, a); }',
  }), []);
  useEffect(() => () => material.dispose(), [material]);
  return (
    <mesh position={[0, 0.012, 0]} rotation={[-Math.PI / 2, 0, 0]} material={material}>
      <planeGeometry args={[3.5, 2.5]} />
    </mesh>
  );
};

const StaticSet = () => (
  <>
    <color attach="background" args={[COLORS.background]} />
    <fog attach="fog" args={[COLORS.background, 9, 20]} />
    <hemisphereLight args={['#d8f4f3', '#101b20', 1.1]} />
    <directionalLight
      position={[4, 7, 5]}
      intensity={3.2}
      color="#fff0dc"
      castShadow
      shadow-mapSize-width={1024}
      shadow-mapSize-height={1024}
      shadow-camera-near={0.1}
      shadow-camera-far={18}
      shadow-camera-left={-5}
      shadow-camera-right={5}
      shadow-camera-top={5}
      shadow-camera-bottom={-5}
      shadow-bias={-0.0003}
    />
    <directionalLight position={[-4, 2.5, 4]} intensity={0.85} color="#83d8dc" />
    <directionalLight position={[0, 4.5, -5]} intensity={2.1} color="#77ead8" />
    <mesh position={[0, -0.04, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
      <planeGeometry args={[200, 200]} />
      <meshStandardMaterial color="#111c21" metalness={0.22} roughness={0.72} />
    </mesh>
    <ContactShadow />
  </>
);

const Labels = () => {
  const frame = useCurrentFrame();
  const enter = smoothstep((frame - 3) / 14);
  const style: React.CSSProperties = {
    position: 'absolute',
    left: 72,
    top: 52,
    color: '#e8f0ee',
    opacity: enter,
    transform: `translateY(${12 * (1 - enter)}px)`,
    fontFamily: 'Inter, Segoe UI, sans-serif',
    pointerEvents: 'none',
  };
  return (
    <div style={style}>
      <div style={{fontSize: 13, letterSpacing: 4, color: COLORS.cyan, fontWeight: 700}}>STUDIO / PRODUCT STUDY 01</div>
      <div style={{fontSize: 40, lineHeight: 1.05, letterSpacing: -1.3, fontWeight: 600, marginTop: 11}}>A quieter kind of power.</div>
      <div style={{fontSize: 15, color: '#9eafb2', letterSpacing: 1.1, marginTop: 11}}>NOVA  /  ROOM SPEAKER</div>
      <div style={{position: 'absolute', left: 0, top: 542, width: 260, borderTop: '1px solid #34474c', paddingTop: 13, color: '#aab9bb', fontSize: 12, letterSpacing: 1.6}}>
        CERAMIC SHELL <span style={{color: COLORS.cyan}}>·</span> BRUSHED ALLOY <span style={{color: COLORS.cyan}}>·</span> SPATIAL SOUND
      </div>
    </div>
  );
};

export const DirectorDemo: React.FC = () => (
  <AbsoluteFill style={{background: COLORS.background, overflow: 'hidden'}}>
    <ThreeCanvas
      width={1280}
      height={720}
      camera={CAMERA}
      dpr={QUALITY.dpr}
      shadows={QUALITY.shadows}
      gl={{antialias: true, powerPreference: 'high-performance'}}
      style={{position: 'absolute', inset: 0}}
    >
      <CameraTrack />
      <StaticSet />
      <ProductMotion />
      <ParticleFlow />
    </ThreeCanvas>
    <Labels />
  </AbsoluteFill>
);
