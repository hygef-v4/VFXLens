import {Composition} from 'remotion';
import {SmokeTest} from './SmokeTest';
import {ThreeCheck} from './ThreeCheck';
import {EditorialExplainer} from './editorial/EditorialExplainer';
import {DirectorDemo} from './director/DirectorDemo';
import {ShortAssembly, calculateShortMetadata} from './shorts/ShortAssembly';

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
  <Composition id="DirectorSkillDemo" component={DirectorDemo} durationInFrames={120} fps={30} width={1280} height={720} />
  <Composition
    id="EditorialExplainer"
    component={EditorialExplainer}
    durationInFrames={3600}
    fps={30}
    width={1920}
    height={1080}
    defaultProps={{manifestFile: 'media/nvidia-ceo-20261115/manifest.json'}}
  />
  <Composition
    id="NvidiaCudaShort"
    component={ShortAssembly}
    calculateMetadata={calculateShortMetadata}
    durationInFrames={30}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={{manifestFile: 'media/nvidia-cuda-bet/manifest.json', music: true}}
  />
  {/* Any three.js short: npx remotion render src/index.ts ThreeShort out.mp4 --props='{"manifestFile":"media/<slug>/manifest.json"}' */}
  <Composition
    id="ThreeShort"
    component={ShortAssembly}
    calculateMetadata={calculateShortMetadata}
    durationInFrames={30}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={{manifestFile: 'media/nvidia-cuda-bet/manifest.json', music: true}}
  />
  </>
);
