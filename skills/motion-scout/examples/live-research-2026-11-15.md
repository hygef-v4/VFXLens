# Live research example — sci-fi product commercial

**Mode:** research only. **Snapshot:** 2026-11-15, approximately 10:34 UTC.
This is a dated example of the research process, not a repository catalog to reuse
instead of live discovery. No candidate was installed or executed in VFXLens.

Brief tested: find exceptional and recently trending open-source Three.js,
WebGPU and Remotion technology for a cinematic sci-fi product commercial; inspect
GitHub and accessible X evidence and propose integration without installation.
Dimensions/duration were not supplied: those remain production decisions, not
measured properties of the candidates.

## Access, windows and metric honesty

GitHub MCP repository search was present but its read-only test returned
`ReadTimeout`. Public GitHub REST and native web discovery worked. Local `git`,
Python, Codex and Claude executables were detected; their presence does not prove
authenticated model/tool sessions. X indexed searches returned no relevant posts;
opening `https://x.com/mrdoob` returned HTTP 403. No X metrics were verified.

The 7/30/90-day pushed-at cutoffs were 2026-11-08, 2026-10-16 and 2026-08-17.
These measure repo activity, not star growth. Established work was also considered.
No historical star baseline was available: **recent growth is unknown for every
candidate** and no `Verified Viral` label was assigned. Conflicting displayed
snapcn totals (625 on a page, 626 on its homepage, 627 in the REST snapshot) were
kept distinct rather than averaged or used to invent a velocity.

## Shortlist and eligibility

The rubric uses 30% visual quality/innovation, 25% demonstrated implementation,
20% reuse/video compatibility, 15% engineering and 10% verified recent momentum.
Overall numeric scores are withheld because dimensions are unverified. Tiers are
provisional task-fit judgments. An API license indicator is preliminary; only
the first two received selected source/license inspection. No S-tier certification
or complete source/asset clearance is claimed.

| Tier / confidence | Candidate | Snapshot / activity | Evidence and proposed use |
| --- | --- | --- | --- |
| A, provisional / medium | [snapcn](https://github.com/shadcn-labs/snapcn) | MIT indicator; 627 stars / 34 forks; pushed 2026-11-12, within 7 days | Frame-driven Remotion text/logo components inspected; live catalog viewed. Best small-code reuse candidate, conditional on selected-file/font/dependency review and local seek/render tests. |
| B / Experimental / medium | [Threejs-Punk](https://github.com/ektogamat/threejs-conference) | MIT; 162 / 34; pushed 2026-09-23, within 90 days | Viewed a limited neon/rain intro; inspected TSL rain and GPU collision code. Useful visual/shader study; real-time/random simulation requires an original analytical or baked adaptation. |
| C / low | [video-motion-pro](https://github.com/huige-opc/video-motion-pro) | Apache-2.0 indicator; 2 / 0; pushed 2026-08-15, outside 90 days | README/metadata lead for shot cards; no local execution or verified visual output. |
| C / low | [remotion-cinematic](https://github.com/codeverbojan/remotion-cinematic) | MIT indicator; 26 / 7; pushed 2026-11-04, within 30 days | Product-demo template lead; app/screen focus is less relevant to a 3D hero. README/metadata only. |
| C / Experimental / low | [Lithosphere](https://github.com/neurabytelabs/lithosphere) | MIT indicator; 3 / 0; pushed 2026-10-08, within 90 days and outside 30 | WebGPU/TSL glowing-orb prototype lead; demo not viewed and shader unit not locally tested. |
| C / low | [promo-video-skill](https://github.com/aariz51/promo-video-skill) | MIT indicator; 3 / 1; pushed 2026-10-21, within 30 days | Reference-to-promo workflow lead; source skill was not activated. README/metadata only. |

Low-star candidates were retained for relevant techniques instead of discarded
for lack of popularity. [visions-recipes](https://github.com/jqaisystems/visions-recipes)
and [video-talkcraft](https://github.com/Vincentwei1021/video-talkcraft) were screened
as conditional/reference-only because their API license metadata was `NOASSERTION`;
that does not establish their actual license or clear source reuse.

## Inspected source and visual limits

- snapcn at [`18b973d7592adf2099a4d5cc2d8970862a4e1172`](https://github.com/shadcn-labs/snapcn/tree/18b973d7592adf2099a4d5cc2d8970862a4e1172):
  README/LICENSE, [`text-reveal`](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/registry/snap-cn/text-reveal/index.tsx)
  and [`sky-lockup`](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/registry/snap-cn/sky-lockup/index.tsx).
  They use Remotion frame evaluation. `@/lib/...` aliases and
  `@remotion/google-fonts` require adaptation; font/measurement readiness and
  backward seeks still need local testing.
  Its [pinned manifest](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/package.json)
  declares Remotion packages `4.0.542` and React `19.2.4`; local versions are
  `4.0.543` and `19.3.1`. Adapt a selected component to the local versions;
  importing the Next.js catalog and its server dependencies is unnecessary.
- Threejs-Punk at [`8cc20593b2270e2ce832e7b7b44356705daddec4`](https://github.com/ektogamat/threejs-conference/tree/8cc20593b2270e2ce832e7b7b44356705daddec4):
  README/LICENSE, [`surfaceRain.js`](https://github.com/ektogamat/threejs-conference/blob/8cc20593b2270e2ce832e7b7b44356705daddec4/src/tsl/surfaceRain.js)
  and [`createCollisionRain.js`](https://github.com/ektogamat/threejs-conference/blob/8cc20593b2270e2ce832e7b7b44356705daddec4/src/world/weather/createCollisionRain.js).
  The latter uses random initialization and history-dependent compute; its live
  update loop is not an arbitrary-frame Remotion export path.
  Its [pinned manifest](https://github.com/ektogamat/threejs-conference/blob/8cc20593b2270e2ce832e7b7b44356705daddec4/package.json)
  declares Three `^0.185.1`, GSAP `^3.15.0` and BVH `^0.9.13`. Local Three
  `0.187.0` is outside that Three range; TSL APIs must be checked before adapting.
- [`threejspunk.vercel.app`](https://threejspunk.vercel.app/): a screenshot showed
  a limited dark neon magenta/cyan rain/orb intro after a loading state. This is
  mood evidence, not a complete scene, asset review or GPU benchmark.
- [`snapcn.dev`](https://snapcn.dev/): the viewed homepage/gallery showed launch
  cards and title/logo presentation; no selected component was rendered locally.
- Other inspected repository heads: video-motion-pro
  `bdfecf89476a83370dcfa74e2f0e99cddd74ac49`, remotion-cinematic
  `b86df2d8e8e3aee7dc942b7db46ce04ab64766cd`, Lithosphere
  `5fee6e0fcc4241de48978ec70b47aaacc2dceb2f`, promo-video-skill
  `124414a011f891353a2f32546487d8c1248c7400`.

## Proposed Director handoff — not executed

Reuse the existing VFXLens R3F scene/camera/analytical instancing patterns first.
Prototype one dark product reveal with meaningful material/reflection changes,
then add only a small text reveal if it earns its place. Use Threejs-Punk's
rain/neon treatment as visual study; implement frame-pure rain or bake it rather
than importing the app. Consider snapcn's selected component only after reviewing
its exact imports/license. Keep native WebGPU optional until backend/capture/seek
checks succeed; the local WebGL path is a potential fallback.

Acceptance plan: installed-version/typecheck, representative still and short
moving shot, fresh/reverse-frame comparison, concurrent export, encoded-frame
inspection and sound review when audio is supplied. These are proposed tests,
not completed results. No runtime dependency, video source, lockfile, paid service
or model download changed during this research.

An additional live run of the bundled REST helper found 39 matches for
`webgpu particles archived:false pushed:2026-10-16..2026-11-15`, returning new leads
including [tidemote](https://github.com/thallada/tidemote),
[NexaCore](https://github.com/cokovali10-sketch/NexaCore) and
[particle-lab-alpha](https://github.com/Artsrun/particle-lab-alpha).
They were discovery hits only, not inspected/approved selections. The helper ran
successfully with Windows CP1252 console encoding; a single real snapshot produced
`growth: unknown`. A before/after hash check found no changes to the 12 inspected
video-source/dependency files.

Skill verification passed: 16 helper unit tests, Ruff, all 47 existing VFXLens
tests, frontmatter validation at all three locations, and 15 relative Markdown
links. Both client discovery junctions exposed the same 17 canonical files;
setup/check also worked from an unrelated Windows working directory. Interactive
Codex/Claude session selection was not tested. No upstream video was built or
rendered as part of this research-only run.
