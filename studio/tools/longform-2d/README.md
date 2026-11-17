# 2D long-form toolkit

Scripts for the [2D long-form video workflow](../../../workflows/2d-long-form-video.md). The picture is the Remotion
kit in [`studio/src/longform/`](../../src/longform/LongForm.tsx); these scripts make the voice, the timeline and the
manifest it reads.

| Path | What it is |
| --- | --- |
| `scaffold.py <slug>` | Creates `local/productions/<slug>/` from `examples/demo-2d/` and `studio/src/longform/episodes/<slug>/episode.tsx` from the demo episode. Never overwrites |
| `voice_lines.py` | One take per script line with word times → `voice/<id>.wav` + `lines.json`. ElevenLabs CLI per speaker voice, cached in `voice/raw/`; `--silent` for a free draft; `--only l3 l5` to redo lines. Waveform trim, light voice chain, cast pan |
| `build.py` | Places lines in scenes (lead 0.3 s, gap 0.26 s, tail 0.5 s; overridable per scene/line), computes mouth tracks, ducks music and cuts it on cards, resolves SFX anchors, copies media → `studio/public/media/<slug>/longform.json` + `timeline.json` |
| `examples/demo-2d/` | `script.json` and `sfx.json` for the demo episode "The Missing Cent" (fiction, about 30 s) |

Run the demo without any key:

```powershell
python studio/tools/longform-2d/scaffold.py demo-2d
cd local/productions/demo-2d
python ../../../studio/tools/longform-2d/voice_lines.py --silent
python ../../../studio/tools/longform-2d/build.py
cd ../../../studio
npx remotion render src/index.ts LongForm-demo-2d ../local/productions/demo-2d/renders/demo-2d-draft.mp4
```

Requirements: Python 3 with numpy, FFmpeg 4.3+ (`deesser`, `acompressor`), Node for the studio, and the ElevenLabs CLI
(`npm i -g @elevenlabs/cli`, `elevenlabs auth login`) for real voices.
