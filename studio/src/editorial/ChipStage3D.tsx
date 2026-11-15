import React, {useLayoutEffect, useMemo, useRef} from 'react';
import {ThreeCanvas} from '@remotion/three';
import {Matrix4, Object3D} from 'three';
import type {InstancedMesh} from 'three';

const ink = '#0B191D';
const lime = '#B9ED69';
const cream = '#F2F0E6';
const metal = '#D7B76D';

const settle = (frame: number) => {
  const t = Math.max(0, Math.min(1, frame / 60));
  return 1 - Math.pow(1 - t, 3);
};

const CircuitBoard = () => (
  <group>
    <mesh position={[0, -0.22, 0]} receiveShadow>
      <boxGeometry args={[5.15, 0.3, 4.25]} />
      <meshStandardMaterial color="#173035" metalness={0.52} roughness={0.38} />
    </mesh>
    <mesh position={[0, -0.045, 0]}>
      <boxGeometry args={[5.02, 0.06, 4.12]} />
      <meshStandardMaterial color="#243F3B" metalness={0.4} roughness={0.32} />
    </mesh>
    {[[-2.25, -1.74], [2.25, -1.74], [-2.25, 1.74], [2.25, 1.74]].map(([x, z], i) => (
      <mesh key={i} position={[x, -0.04, z]} rotation={[Math.PI / 2, 0, 0]} castShadow>
        <cylinderGeometry args={[0.13, 0.16, 0.12, 8]} />
        <meshStandardMaterial color={metal} metalness={0.8} roughness={0.24} />
      </mesh>
    ))}
    {[-1, 1].flatMap((side) => [0, 1, 2, 3].map((i) => (
      <group key={`${side}-${i}`}>
        <mesh position={[side * (1.67 + (i % 2) * 0.28), 0.0, -1.5 + i * 0.95]}>
          <boxGeometry args={[0.58, 0.025, 0.045]} />
          <meshStandardMaterial color={i % 2 ? '#64805C' : lime} emissive={lime} emissiveIntensity={0.16} metalness={0.3} roughness={0.5} />
        </mesh>
        <mesh position={[side * 2.1, 0.0, -1.43 + i * 0.94]}>
          <boxGeometry args={[0.16, 0.028, 0.07]} />
          <meshStandardMaterial color={metal} metalness={0.75} roughness={0.25} />
        </mesh>
      </group>
    )))}
    {[-1, 1].flatMap((side) => [0, 1, 2].map((i) => (
      <mesh key={`${side}-${i}`} position={[-1.02 + i * 1.02, 0.0, side * 1.77]}>
        <boxGeometry args={[0.045, 0.025, 0.46]} />
        <meshStandardMaterial color="#9AAF74" emissive="#5D713F" emissiveIntensity={0.16} roughness={0.44} />
      </mesh>
    )))}
    <mesh position={[0, 0.005, -1.86]}>
      <boxGeometry args={[3.12, 0.025, 0.045]} />
      <meshStandardMaterial color="#6C8462" metalness={0.3} roughness={0.43} />
    </mesh>
    <mesh position={[0, 0.005, 1.86]}>
      <boxGeometry args={[3.12, 0.025, 0.045]} />
      <meshStandardMaterial color="#6C8462" metalness={0.3} roughness={0.43} />
    </mesh>
  </group>
);

const Pins = () => {
  const ref = useRef<InstancedMesh>(null);
  const matrices = useMemo(() => {
    const object = new Object3D();
    const result: Matrix4[] = [];
    const steps = 12;
    for (let edge = 0; edge < 4; edge++) {
      for (let i = 0; i < steps; i++) {
        const along = (i - (steps - 1) / 2) * 0.19;
        const x = edge < 2 ? (edge === 0 ? -1.48 : 1.48) : along;
        const z = edge < 2 ? along : (edge === 2 ? -1.48 : 1.48);
        object.position.set(x, 0.23, z);
        object.rotation.set(0, edge < 2 ? 0 : Math.PI / 2, 0);
        object.updateMatrix();
        result.push(object.matrix.clone());
      }
    }
    return result;
  }, []);

  useLayoutEffect(() => {
    if (!ref.current) return;
    matrices.forEach((matrix, index) => ref.current?.setMatrixAt(index, matrix));
    ref.current.instanceMatrix.needsUpdate = true;
  }, [matrices]);

  return (
    <instancedMesh ref={ref} args={[undefined, undefined, matrices.length]} castShadow receiveShadow>
      <boxGeometry args={[0.16, 0.075, 0.055]} />
      <meshStandardMaterial color={metal} metalness={0.84} roughness={0.2} />
    </instancedMesh>
  );
};

const Processor = ({frame}: {frame: number}) => {
  const assembled = settle(frame);
  const orbit = frame * 0.00145;
  const bob = Math.sin(frame * 0.055) * 0.025 * assembled;
  return (
    <group rotation={[0, orbit, 0]} position={[0, bob, 0]}>
      <CircuitBoard />
      <group position={[0, 0.32 + (1 - assembled) * 0.62, 0]}>
        <mesh castShadow receiveShadow>
          <boxGeometry args={[3.14, 0.22, 3.14]} />
          <meshStandardMaterial color="#293E3D" metalness={0.65} roughness={0.3} />
        </mesh>
        <mesh position={[0, 0.13, 0]}>
          <boxGeometry args={[2.96, 0.055, 2.96]} />
          <meshStandardMaterial color={metal} metalness={0.85} roughness={0.24} />
        </mesh>
        <mesh position={[0, 0.18, 0]} castShadow receiveShadow>
          <boxGeometry args={[2.78, 0.16, 2.78]} />
          <meshStandardMaterial color="#D9D6C7" metalness={0.42} roughness={0.27} />
        </mesh>
        <mesh position={[0, 0.265, 0]}>
          <boxGeometry args={[2.54, 0.025, 2.54]} />
          <meshStandardMaterial color="#EEEBDD" metalness={0.3} roughness={0.24} />
        </mesh>
        <Pins />
      </group>

      <group position={[0, 0.55 + (1 - assembled) * 0.92, 0]}>
        <mesh castShadow receiveShadow>
          <boxGeometry args={[2.13, 0.28, 2.13]} />
          <meshStandardMaterial color="#82958A" metalness={0.72} roughness={0.24} />
        </mesh>
        <mesh position={[0, 0.17, 0]} castShadow receiveShadow>
          <boxGeometry args={[1.88, 0.16, 1.88]} />
          <meshStandardMaterial color={cream} metalness={0.34} roughness={0.2} />
        </mesh>
        <mesh position={[0, 0.26, 0]}>
          <boxGeometry args={[1.62, 0.035, 1.62]} />
          <meshStandardMaterial color="#C5D19B" metalness={0.5} roughness={0.24} />
        </mesh>
        {[-0.52, -0.26, 0, 0.26, 0.52].map((offset) => (
          <group key={offset}>
            <mesh position={[offset, 0.286, 0]}>
              <boxGeometry args={[0.018, 0.012, 1.3]} />
              <meshStandardMaterial color="#55715A" metalness={0.45} roughness={0.32} />
            </mesh>
            <mesh position={[0, 0.287, offset]}>
              <boxGeometry args={[1.3, 0.012, 0.018]} />
              <meshStandardMaterial color="#55715A" metalness={0.45} roughness={0.32} />
            </mesh>
          </group>
        ))}
        <mesh position={[0, 0.33, 0]} castShadow>
          <boxGeometry args={[0.7, 0.075, 0.7]} />
          <meshStandardMaterial color={ink} metalness={0.62} roughness={0.22} emissive="#18352E" emissiveIntensity={0.18} />
        </mesh>
        <mesh position={[0, 0.372, 0]}>
          <boxGeometry args={[0.34, 0.012, 0.34]} />
          <meshStandardMaterial color={lime} emissive={lime} emissiveIntensity={0.62} metalness={0.25} roughness={0.25} />
        </mesh>
        {[-0.49, 0.49].flatMap((x) => [-0.49, 0.49].map((z) => (
          <mesh key={`${x}-${z}`} position={[x, 0.31, z]}>
            <boxGeometry args={[0.2, 0.025, 0.2]} />
            <meshStandardMaterial color="#779076" emissive="#5C8052" emissiveIntensity={0.22} metalness={0.36} roughness={0.3} />
          </mesh>
        )))}
      </group>
    </group>
  );
};

const DataCubes = ({frame}: {frame: number}) => (
  <group>
    {[0, 1, 2, 3, 4].map((i) => {
      const angle = frame * 0.013 + (i * Math.PI * 2) / 5;
      const radius = i % 2 ? 2.48 : 2.8;
      const scale = i === 2 ? 0.2 : 0.13;
      return (
        <mesh key={i} position={[Math.cos(angle) * radius, 0.9 + Math.sin(frame * 0.045 + i) * 0.12, Math.sin(angle) * radius]} rotation={[0.35, angle, 0.35]} castShadow>
          <boxGeometry args={[scale, scale, scale]} />
          <meshStandardMaterial color={i === 2 ? lime : cream} emissive={i === 2 ? lime : '#C5D19B'} emissiveIntensity={i === 2 ? 0.42 : 0.12} metalness={0.55} roughness={0.22} />
        </mesh>
      );
    })}
  </group>
);

export const ChipStage3D = ({frame}: {frame: number}) => {
  const push = 0.35 * (1 - settle(frame));
  const camera = useMemo(() => ({position: [6 + push, 6.2 + push, 8 + push] as [number, number, number], fov: 31}), [push]);
  return (
    <ThreeCanvas
      width={900}
      height={620}
      camera={camera}
      gl={{alpha: true, antialias: true, powerPreference: 'high-performance'}}
      shadows
      style={{width: '100%', height: '100%', background: 'transparent'}}
    >
      <hemisphereLight args={['#EDF7DD', '#172827', 1.05]} />
      <ambientLight intensity={0.4} />
      <directionalLight position={[5, 8, 6]} intensity={2.7} castShadow shadow-mapSize-width={1024} shadow-mapSize-height={1024} shadow-camera-near={0.1} shadow-camera-far={25} shadow-bias={-0.00025} />
      <directionalLight position={[-6, 4, 3]} intensity={1.15} color="#D7E8C5" />
      <directionalLight position={[0, 5, -7]} intensity={1.8} color={lime} />
      <pointLight position={[0, 2.3, 0]} intensity={0.48} color={lime} distance={5} />
      <group position={[0, -0.08, 0]}>
        <Processor frame={frame} />
        <DataCubes frame={frame} />
        <mesh position={[0, -0.49, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
          <planeGeometry args={[200, 200]} />
          <shadowMaterial transparent opacity={0.25} />
        </mesh>
      </group>
    </ThreeCanvas>
  );
};
