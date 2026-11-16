import {Composition} from 'remotion';
import {SmokeTest} from './SmokeTest';
import {ThreeCheck} from './ThreeCheck';
import {DirectorDemo} from './director/DirectorDemo';
import {ShortAssembly, calculateShortMetadata, shortDefaults, shortSchema} from './shorts/ShortAssembly';

export const Root = () => (
  <>
    <Composition id="SmokeTest" component={SmokeTest} durationInFrames={300} fps={30} width={1080} height={1920} />
    <Composition id="ThreeCheck" component={ThreeCheck} durationInFrames={30} fps={30} width={640} height={360} />
    <Composition id="DirectorSkillDemo" component={DirectorDemo} durationInFrames={120} fps={30} width={1280} height={720} />
    {/* Any three.js Short: npx remotion render src/index.ts ThreeShort out.mp4 --props='{"manifestFile":"media/<slug>/manifest.json"}' */}
    <Composition
      id="ThreeShort"
      component={ShortAssembly}
      schema={shortSchema}
      calculateMetadata={calculateShortMetadata}
      durationInFrames={30}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{...shortDefaults, manifestFile: 'media/example/manifest.json'}}
    />
  </>
);
