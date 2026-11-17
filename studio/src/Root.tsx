import {Composition} from 'remotion';
import {SmokeTest} from './SmokeTest';
import {ThreeCheck} from './ThreeCheck';
import {GsapThreeDemo} from './gsap/GsapThreeDemo';
import {LongForm, calculateLongFormMetadata, longFormDefaults, longFormSchema} from './longform/LongForm';
import {EPISODES} from './longform/registry';
import {DirectorDemo} from './director/DirectorDemo';
import {ShortAssembly, calculateShortMetadata, shortDefaults, shortSchema} from './shorts/ShortAssembly';

export const Root = () => (
  <>
    <Composition id="SmokeTest" component={SmokeTest} durationInFrames={300} fps={30} width={1080} height={1920} />
    <Composition id="ThreeCheck" component={ThreeCheck} durationInFrames={30} fps={30} width={640} height={360} />
    <Composition id="DirectorSkillDemo" component={DirectorDemo} durationInFrames={120} fps={30} width={1280} height={720} />
    <Composition id="GsapThreeDemo" component={GsapThreeDemo} durationInFrames={180} fps={30} width={1280} height={720} />
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
    {/* 2D long-form episodes: one composition per studio/src/longform/episodes/<slug>/episode.tsx (manifest from tools/longform-2d/build.py) */}
    {Object.values(EPISODES).map((e) => (
      <Composition key={e.slug} id={`LongForm-${e.slug}`} component={LongForm} schema={longFormSchema}
        calculateMetadata={calculateLongFormMetadata} durationInFrames={30} fps={30} width={1920} height={1080}
        defaultProps={{...longFormDefaults, slug: e.slug}} />
    ))}
  </>
);
