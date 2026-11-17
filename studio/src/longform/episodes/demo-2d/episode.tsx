// Demo episode "The Missing Cent" (fiction, ~30 s): one component per scene kind of script.json.
// Copy this file to episodes/<slug>/episode.tsx (scaffold.py does it) and replace cast, sets and shots with the story's own.
import {useThree} from '@react-three/fiber';
import {ThreeCanvas} from '@remotion/three';
import React from 'react';
import * as THREE from 'three';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {
  Camera, City, Glow, GroundShadow, K, LocationTag, LowerThird, MapGrid, Night, PALETTE, PolaroidEnding, PopLabel, Puppet,
  ROOM_LIGHTS, Room, Route, Stage, Stamp, TextCard, Vignette, blinking, useLine, useScene, useSpeech,
  type Episode, type Look, type SceneProps,
} from '../../kit';

// Original cast: invent new looks for every episode.
const MIRA: Look = {skin: '#E9C39A', skinDark: '#C99F72', suit: '#3F6E6A', suitDark: '#2D504D', shirt: '#F4EFE2', tie: '#E0A43A', hair: 'bob', hairColor: '#2B1E1A', glasses: true};
const BOSS: Look = {skin: '#D9A77E', skinDark: '#B5835C', suit: '#4A3B5C', suitDark: '#352A43', shirt: '#F4EFE2', bowtie: true, tie: '#B8322F', hair: 'bald', moustache: true, hairColor: '#6E6A70', pocket: '#F4EFE2'};

/** Office two-shot: Mira at the desk side, the boss by the door. Shared by the opening and the polaroid ending. */
const Office: React.FC = () => {
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const t = frame / fps;
  const mira = useSpeech('mira'); const boss = useSpeech('boss');
  const {lines} = useScene();
  const bossLine = lines.find((l) => l.speaker === 'boss');
  const bossK = bossLine ? K(frame - bossLine.from, 0, 8) : 0; // snap into the gesture as he starts talking
  const squash = 0.07 * (1 - K(t, 0, 0.25)); // every shot starts with a small squash
  return (
    <Stage>
      <Room />
      <GroundShadow x={1180} y={900} w={210} /><GroundShadow x={640} y={900} w={210} />
      <Puppet x={1180} y={900} s={1.25} look={MIRA} face={-0.55} light={1} squash={squash}
        eyes={blinking(frame, fps, 2.6, 0.3) ? 'closed' : 'dot'} mouth={mira ?? 'flat'} brow={mira ? 0.4 : 0}
        arms={['hold', 'chin']} bob={2 * Math.sin(t * 2.4)} rim="#FFE2A8" />
      <Puppet x={640} y={900} s={1.25} look={BOSS} face={0.5} light={1} squash={squash}
        eyes={blinking(frame, fps, 2.9, 1.1) ? 'closed' : boss ? 'dot' : 'half'} mouth={boss ?? 'smirk'}
        arms={[{from: 'hip', to: 'gesture', k: bossK}, 'pocket']} bob={2 * Math.sin(t * 2.1 + 1)} />
      <Night lights={ROOM_LIGHTS} />
      <Glow x={1618} y={478} r={150} />
    </Stage>
  );
};

const OfficeScene: React.FC<SceneProps> = () => {
  const {fps} = useVideoConfig(); const l2 = useLine('l2');
  const centAt = (l2.words[1]?.from ?? l2.from) / fps; // the pop lands on "cent"
  return (
    <AbsoluteFill>
      <Camera zoom={[1.0, 1.07]} focus={[930, 560]} whipOut>
        <Office />
        <Stage><PopLabel text="$0.01" x={1420} y={300} at={centAt} out={centAt + 1.6} color={PALETTE.lime} /></Stage>
      </Camera>
      <Vignette />
      <LocationTag text="City Savings Bank, 9:04 pm" />
      <LowerThird name="Mira Holt" role="Night accountant" at={l2.from / fps} out={l2.from / fps + 2.6} />
    </AbsoluteFill>
  );
};

const CardScene: React.FC<SceneProps> = ({lines}) => <TextCard words={lines[0]?.words} />;

const MapScene: React.FC<SceneProps> = ({lines}) => {
  const {fps} = useVideoConfig(); const start = (lines[0]?.from ?? 0) / fps; const dur = (lines[0]?.durationInFrames ?? 90) / fps;
  return (
    <AbsoluteFill>
      <Camera zoom={[1.02, 1.1]} focus={[1000, 560]} rotate={[-1.5, 0.5]} whipIn>
        <Stage>
          <MapGrid />
          <path d="M 140 260 C 420 160 760 220 980 330 C 1180 420 1240 600 1120 760 C 960 960 520 980 300 860 C 120 760 40 420 140 260 Z" fill="#3E5A4A" stroke="#18161B" strokeWidth={7} />
          <path d="M 1300 520 C 1420 440 1640 460 1760 560 C 1860 660 1800 860 1620 900 C 1460 930 1300 820 1280 700 Z" fill="#3E5A4A" stroke="#18161B" strokeWidth={7} />
          <City x={520} y={480} label="City" at={start} />
          <City x={1600} y={720} label="Harbor" at={start + dur * 0.6} />
          <Route points={[[520, 480], [820, 560], [1180, 520], [1420, 640], [1600, 720]]} at={start + 0.2} dur={dur * 0.8} />
        </Stage>
      </Camera>
      <Vignette />
    </AbsoluteFill>
  );
};

// three.js shot: a low-angle lighthouse with a sweeping beam. Ink look = toon shading + inverted-hull outline.
const INK3 = new THREE.MeshBasicMaterial({color: '#18161B', side: THREE.BackSide});
const Inked: React.FC<{geo: THREE.BufferGeometry; color: string; y: number; emissive?: string}> = ({geo, color, y, emissive}) => (
  <group position-y={y}>
    <mesh geometry={geo}><meshToonMaterial color={color} emissive={emissive ?? '#000'} /></mesh>
    <mesh geometry={geo} material={INK3} scale={1.045} />
  </group>
);
// Geometry is built once per bundle, never per frame.
const STRIPES = [0, 1, 2, 3].map((i) => new THREE.CylinderGeometry(0.62 - (i + 1) * 0.06, 0.62 - i * 0.06, 1, 32));
const ROCK = new THREE.CylinderGeometry(2.2, 2.8, 0.8, 9);
const LAMP = new THREE.CylinderGeometry(0.5, 0.5, 0.7, 24);
const ROOF = new THREE.ConeGeometry(0.6, 0.6, 24);
/** Low-angle orbit driven by the frame (R3F's camera prop only applies once). */
const Orbit: React.FC<{angle: number}> = ({angle}) => {
  const camera = useThree((s) => s.camera);
  camera.position.set(Math.sin(angle) * 12, 0.8, Math.cos(angle) * 12);
  camera.lookAt(0, 2.6, 0);
  return null;
};
const Lighthouse: React.FC = () => {
  const frame = useCurrentFrame(); const {fps, width, height} = useVideoConfig(); const t = frame / fps;
  const orbit = 0.35 + t * 0.06;
  return (
    <ThreeCanvas width={width} height={height} camera={{fov: 40}}>
      <Orbit angle={orbit} />
      <color attach="background" args={['#141A36']} />
      <ambientLight intensity={0.35} color="#7C8CC8" />
      <directionalLight position={[-4, 6, 3]} intensity={1.3} color="#B9C6FF" />
      <pointLight position={[0, 4.6, 0]} intensity={6} distance={6} color={PALETTE.lamp} />
      <Inked geo={ROCK} color="#5B5560" y={-0.4} />
      {STRIPES.map((g, i) => <Inked key={i} geo={g} color={i % 2 ? '#F4EFE2' : '#C8242C'} y={0.5 + i} />)}
      <Inked geo={LAMP} color="#FFE7A8" emissive="#8A6A20" y={4.35} />
      <Inked geo={ROOF} color="#2E2E38" y={5.0} />
      <mesh position={[0, 4.35, 0]} rotation={[0, t * 1.4, Math.PI / 2]}>
        <coneGeometry args={[1.2, 9, 24, 1, true]} />
        <meshBasicMaterial color={PALETTE.lamp} transparent opacity={0.16} blending={THREE.AdditiveBlending} depthWrite={false} side={THREE.DoubleSide} />
      </mesh>
    </ThreeCanvas>
  );
};
const LandmarkScene: React.FC<SceneProps> = () => {
  const {fps} = useVideoConfig(); const l6 = useLine('l6');
  const hit = (l6.words[l6.words.length - 1]?.from ?? l6.from) / fps; // stamp on the last word
  return (
    <AbsoluteFill>
      <Camera zoom={[1, 1.05]} shakes={[{at: hit, dur: 0.35, amp: 16}]} grade={false}>
        <Lighthouse />
        <Stage><Stamp text="SOLD" x={1340} y={760} at={hit} /></Stage>
      </Camera>
      <Vignette strength={0.7} />
      <LocationTag text="Gull Harbor" />
    </AbsoluteFill>
  );
};

const EndingScene: React.FC<SceneProps> = ({lines}) => {
  const {fps} = useVideoConfig(); const last = lines[lines.length - 1];
  const at = last ? (last.from + last.durationInFrames) / fps + 0.25 : 1;
  return (
    // Mira's head is at stage (1180, 370); with zoom 1.1 around (1100, 560) it lands at (1048, 331) on screen.
    <PolaroidEnding at={at} caption="Every cent leaves a trail." ring={{x: 1048, y: 331, r: 165}}>
      <AbsoluteFill><Camera zoom={[1.1, 1.1]} focus={[1100, 560]}><Office /></Camera><Vignette /></AbsoluteFill>
    </PolaroidEnding>
  );
};

export const episode: Episode = {
  slug: 'demo-2d',
  title: 'The Missing Cent',
  scenes: {office: OfficeScene, card: CardScene, map: MapScene, landmark3d: LandmarkScene, ending: EndingScene},
};
