import {Composition} from 'remotion';
import {SmokeTest} from './SmokeTest';
import {ThreeCheck} from './ThreeCheck';
import {EditorialExplainer} from './editorial/EditorialExplainer';
import {DirectorDemo} from './director/DirectorDemo';

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
  </>
);
