import {Composition} from 'remotion';
import {SmokeTest} from './SmokeTest';
import {ThreeCheck} from './ThreeCheck';

export const Root = () => (
  <>
  <Composition
    id="SmokeTest"
    component={SmokeTest}
    durationInFrames={300}
    fps={30}
    width={1080}
    height={1920}
  />
  <Composition id="ThreeCheck" component={ThreeCheck} durationInFrames={30} fps={30} width={640} height={360} />
  </>
);
