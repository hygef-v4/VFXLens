# Video reference analysis for directing

Use with VFXLens's [study workflow](../../../../workflows/study-reference.md),
[video analyzer](../../../../src/vfx_engine/video_analyzer/analyzer.py), and
[render and QA gates](rendering-and-qa.md). This adds a director's bounded study
pass; it does not replace the analyzer or its report schemas.

## Bounded study pass

1. Resolve the supplied source and preserve it read-only. Begin with about the
first ten minutes, or the complete clip if shorter. Extend only for a stated
question or requested coverage; record the interval and remaining unexamined
duration.
2. Review sparse overview frames/contact sheet first, then consecutive frames
around a few representative entrances, reveals, cuts, landings, or effect peaks.
Use the evidence frame's actual presentation timestamp (PTS) and frame index.
Do not calculate a supposedly exact VFR locator from nominal fps alone.
3. Describe only what the pixels/audio establish: shot action, composition,
camera change, layers/depth cues, light/color, typography, transitions and sound
cues. Detector output labels candidates. Name possible implementation as an
inference and exact plugin/layer/parameter data as unavailable from a rendered
video unless another source establishes it.
4. Convert findings to a short shot brief: audience takeaway, subject/action,
composition, motion arc, look, timing locator, proposed implementation and
unknowns. Mark production choices as creative decisions.
5. If local ASR is available and requested by the study, bound it to the same
interval. Keep source-language TXT, SRT and structured JSON in the private
production directory; keep any translated summary separate. ASR text/timing is
inferred until listened to and corrected. If unavailable, report the gap.

## Use the existing analyzer as evidence

`vfx analyze-video` writes structured analysis and timeline evidence, exact PTS
per decoded frame, event candidates, and contact/evidence frames. It adapts frame
density to activity and supports `--max-frames`; a cap means partial coverage,
not a complete study. Read the JSON and Markdown, timeline and actual images.
Use sparse evidence for overview and open selected consecutive-frame windows for
motion; a contact sheet cannot establish the full action between samples.

The analyzer's PTS reader is in
[ffprobe_decoder.py](../../../../src/vfx_engine/video_analyzer/decoder/ffprobe_decoder.py);
the result distinguishes measured signals, inferred technique/plugin candidates,
and unavailable exact AE construction. `DataAvailabilityStatus` has
`observed`, `inferred`, `unavailable`, `unsupported`, and `error`; preserve the
reason and locator when summarizing. An output JSON file or a plausible label does
not itself verify an image or establish an exact effect implementation.

## External workflow research

- [rea-video skill at pinned commit](https://github.com/JuneYaoooo/rea-video/blob/ebe853e330d63719a1f91754f789647c515eac19/skills/rea-video/SKILL.md)
  gives a helpful two-stage review pattern: inspect whole-video storyboard/audio,
  then selected shot sheets and uncertain classifications; keep machine and human
  review separate. Its shot records carry frame times/PTS for VFR. The package is
  Apache-2.0, but its CLI, ASR/VLM, model cache and output schema are another
  stack; VFXLens already provides the read-only analyzer. Adopt the evidence
  discipline, not the external package as a dependency.
- [rea-video speech module](https://github.com/JuneYaoooo/rea-video/blob/ebe853e330d63719a1f91754f789647c515eac19/rea_video/speech.py)
  explicitly describes machine transcript limits and first-use model downloads.
  Do not trigger model downloads or external VLM calls during a local study unless
  the user has configured/authorized that processing. Follow VFXLens's local
  transcription setup and current provider policy instead.
- [motion-skills verification guide](https://github.com/iart-ai/motion-skills/blob/9b9ce041932da787cc856d4cdf23afb6cd13d4bf/tools/verify/README.md)
  reinforces freeze-frame, contact-sheet and encoded-contract checks; those are
  production checks and do not substitute for studying the reference evidence.

Keep the source path and detailed locators in the private case study. Promote
only general, reusable writing or visual techniques to the shared library, as
directed by [study-reference](../../../../workflows/study-reference.md).
