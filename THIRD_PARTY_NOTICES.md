# Third-party notices

VFXLens is MIT-licensed (see `LICENSE`). It adapts or depends on the following third-party work.

## Adapted code

### claude-3d-animated-shorts (MIT)

`studio/tools/threejs-short/engine/render.cjs` and `engine/post.js` are modified copies of files from
[thuann-vn/claude-3d-animated-shorts](https://github.com/thuann-vn/claude-3d-animated-shorts). The toolkit's scaffold
copies the rest of that engine from a local install of the skill; the engine itself is not redistributed here.

```text
MIT License

Copyright (c) 2026 thuann-vn (3D engine, characters, sets, skill)
Copyright (c) mromidev (original claude-animated-shorts workflow, see upstream-2d/LICENSE-upstream)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Third-party assets keep their own licenses: Kenney Furniture Kit and KayKit
Furniture Bits are CC0 (see engine/assets/props/*/LICENSE-*.txt). Files fetched
by scripts/fetch-assets.sh (Xbot.glb, Horse.glb, Anton, Inter) are not included.
```

## Dependencies with licence terms to note

| Project | Licence | Note |
| --- | --- | --- |
| [Remotion](https://www.remotion.dev/license) | Remotion License | Free for individuals and companies of up to 3 people; larger companies need a company licence |
| [py-aep](https://github.com/forticheprod/py-aep) | MIT | Reads `.aep` files in the analyzer |
| [pmndrs/postprocessing](https://github.com/pmndrs/postprocessing) | Zlib | Post effects for three.js scenes |
| [three.js](https://github.com/mrdoob/three.js) | MIT | 3D rendering |
| [OpenAI Whisper](https://github.com/openai/whisper) | MIT | Optional local transcription (`studio/voice`) |

Other Python and npm dependencies are listed with their versions in `uv.lock`, `studio/voice/uv.lock` and
`studio/package-lock.json`; their licences apply as published by each project.

Studies in `library/case-studies/` describe and measure third-party videos and After Effects projects for education
and commentary. They do not include those works' media, and the analysed source files are not redistributed.
