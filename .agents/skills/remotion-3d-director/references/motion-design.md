# Motion direction and layered graphics

## A beat changes understanding

For each narration beat, write the intended takeaway and the exact cue that earns
the visual change. Match proof to evidence, relationships to diagrams, mechanisms
to moving objects, and emotion/action to character staging. Give one element the
lead; supporting and decorative motion should not compete with it.

Compare a representative frame with the chosen reference: silhouette, subject
size, environment, depth, contrast, character/prop continuity and text amount.
When the reference uses a recurring prop in changing locations, carry that object
between shots. A heading plus unrelated icon does not reproduce that language.
Use the VFXLens style/case pages to recover the relevant locators, not a claimed
universal style. Reuse principles rather than a creator's assets/signature look.

## Timing grammar

- Separate entrance, landing, readable hold, action and exit. Tune the readable
  hold after the text/pose is complete; an entrance duration is not reading time.
- Use anticipation/overshoot/settle only when they support the object and tone.
  A spring's `frame` is event-local and `fps` comes from the composition.
- Overlap actions to show continuity, sequence them to show cause, and allow rest
  when the sentence carries the meaning. Continuous camera drift is not required.
- Use shared cue IDs for speech, motion and SFX. An onset detector is a candidate
  cue, not proof of a beat or correct editorial timing.

## GSAP as an evaluator

Adapt facecammaxxing's paused/seekable pattern, not a live playback loop:

```tsx
useLayoutEffect(() => {
  const ctx = gsap.context(() => {
    timeline.current = gsap.timeline({paused: true})
      .fromTo(ref.current, {opacity: 0, y: 24},
        {opacity: 1, y: 0, duration: 0.4, immediateRender: false});
  }, ref);
  return () => {timeline.current = null; ctx.revert();};
}, []);
useLayoutEffect(() => {
  timeline.current?.totalTime(Math.max(0, frame / fps), true);
}, [frame, fps]);
```

Supply React refs, Remotion frame/fps and the installed GSAP import. Seek total
time for authored repeats; use explicit initial values so reverse seeks restore
state. Infinite repeats need a bounded film interval and seek tests. Do not let
ticker callbacks, delayed calls or callbacks that mutate external state become
hidden animation clocks. Kill/revert owned timelines on teardown.

## Typography, captions and compositing

Use delivery-specific safe areas and actual font metrics/diacritics. Reserve word
layout before revealing words so captions do not recenter every frame. Keep
contrast and reading size at the intended phone/desktop viewing scale. Maintain
one authoritative narration draft and original measured word/caption times;
estimated timings are labelled estimates, including TTS metadata that has not
been listening-checked. Deliberate pre-cue timing is an explicit offset, not an
assumed feature of the caption component.

Separate world/background, behind-subject effects, subject, front accents and
screen text when needed. Different depth layers can have different camera
response. Matte quality, face occlusion and collisions need frame inspection;
an oval mask cannot guarantee semantic subject protection. Finish with sound
levels and an audible review when tools permit; visual cleanliness alone does
not establish a good mix.

Sources: [facecammaxxing](source-attribution.md#facecammaxxing),
[motion-tools-and-skills](source-attribution.md#motion-tools-and-skills),
[VFXLens writing](../../../../library/content-writing/README.md).
