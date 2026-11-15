import {Audio} from '@remotion/media';
import {AbsoluteFill, interpolate, staticFile, useCurrentFrame} from 'remotion';

const stages = ['READ', 'LEARN', 'CREATE', 'RENDER'];

export const SmokeTest = () => {
  const frame = useCurrentFrame();
  const stage = Math.min(stages.length - 1, Math.floor(frame / 75));
  const progress = interpolate(frame, [0, 299], [0, 100]);

  return (
    <AbsoluteFill style={{backgroundColor: '#10171c', color: '#f6f1e7', fontFamily: 'Arial', padding: 90}}>
      <Audio src={staticFile('setup-tone.wav')} />
      <div style={{fontSize: 34, letterSpacing: 8, color: '#91bdb7'}}>VFXLENS</div>
      <div style={{marginTop: 260, fontSize: 112, fontWeight: 700, lineHeight: 1.1}}>One workflow.<br />Two agents.</div>
      <div style={{marginTop: 140, fontSize: 84, color: '#e4b96c'}}>{stages[stage]}</div>
      <div style={{marginTop: 60, height: 10, backgroundColor: '#334148'}}>
        <div style={{height: '100%', width: `${progress}%`, backgroundColor: '#91bdb7'}} />
      </div>
      <div style={{position: 'absolute', bottom: 240, left: 90, right: 90, fontSize: 46}}>
        Local video and audio verification
      </div>
      <div style={{position: 'absolute', bottom: 120, fontSize: 26, color: '#91bdb7'}}>1080 x 1920 / 30 FPS / 10 SECONDS</div>
    </AbsoluteFill>
  );
};
