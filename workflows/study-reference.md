# Study a reference

Read this from the repo root resolved by `skills/vfxlens/SKILL.md`, even when the
user's working directory is elsewhere. Keep the original source read-only.

## Find and inspect the source

Identify the actual supplied file/URL and its version. If the referenced PDF or
media is missing, locate it in user-provided context or connected sources before
asking for the missing locator. An existing survey or another document's summary
does not establish what the requested source contains. Continue independent work
while a required input is missing; label the source-dependent work as pending.

Reuse `<repo>/library/README.md` and relevant canonical articles before writing
new ones. Put the source-specific study in
`<repo>/local/productions/<slug>/reference.md` (or the existing equivalent). Record
source identity, date, page/figure or comp/layer/property or timestamp/frame,
claims, measured values with units, proposed application and limitations.

## PDF, article or documentation

For a local PDF, use installed PyMuPDF (`pymupdf`) to inspect page count, text and
page renders. `pypdf` is a text/metadata fallback; neither text extraction alone
nor a table of contents substitutes for inspecting relevant diagrams. For a
scanned PDF, use available local OCR and record any unreadable pages. Save page
images/extracted text in the private production directory, leaving the PDF intact.
The root document environment is documented in `docs/ai-video-requirements.md`.

Read the passages and page images supporting the proposed technique. Cite PDF
page numbers and distinguish printed page labels from file page indices where
they differ. For a URL, retrieve the referenced primary source, record its URL
and access date, and inspect relevant figures. If retrieval fails, record the
failure rather than presenting a cached summary as a fresh reading.

For a 2.5D source, extract what it actually establishes about flat artwork,
spatial depth, cameras, light/shadows, expression changes and compositing. Convert
that into a small shot experiment for this brief, retaining its stated limits.
Do not inherit the source's duration, fps, asset rights or software assumptions.

## Video or AE project

For learning a long video's style, scene design, lighting and audio, begin with
about the first ten minutes (or the whole source when shorter). Inspect sparse
overview samples, then a few representative consecutive-frame windows. Bound
audio/ASR work to the same study interval. Extend coverage when the user requests
it or a specific unanswered question needs another segment; record what remains
unexamined. This learning pass does not require an uncapped full-source VFX run.

Extract a timestamped transcript for the studied interval when local ASR is
available. Save readable TXT, SRT and structured JSON privately, preserving the
original language; keep Vietnamese summaries separate. Use it to study the hook,
questions, metaphors, explanation order, evidence and narrative transitions as
well as images. Label ASR text/times as inferred and record missing coverage,
recognition errors and listening checks; a source's factual claims remain claims
until independently verified. If transcription is unavailable, state that limit.

For reusable writing lessons, use [Content Writing](../library/content-writing/README.md).
Keep exact source examples/locators in the case study and private transcript;
promote the writing method to the matching guide instead of duplicating the script.

Use the existing `analyze-video` / `analyze-project` commands in the shared skill;
do not invent a PDF or production command under `vfx`. Read JSON and Markdown
reports, timeline and actual contact sheets/frames. If analysis was capped with
`--max-frames`, report partial coverage and the unexamined interval.

For video, begin with overview frames and then consecutive frames around the
specific entrance, landing, cut or effect being studied. Use exact presentation
timestamps (PTS) from source evidence; on variable frame rate footage, nominal
fps multiplied by time is not an exact frame locator. Record any timestamp
fallback. Detector labels are candidates, not proof of a plugin or technique.

For AE, trace the composition, layer, source precomp, effect order/matchNames,
keyframes, interpolation and dependencies before giving a numerical recipe.
Map nested timing, start/stretch and time remapping before aligning with a demo.
Saved parameter values are reference values, not universally correct settings.
Offline expression text does not reveal evaluated runtime values. Apply the
repo's temporary-copy rules if the read-only AE bridge is needed.

## Record what is known

Use the repo's availability states precisely:

| State | What the study may claim |
| --- | --- |
| `observed` | Directly read from the source or measured; cite its locator. |
| `inferred` | A conclusion backed by identified observations; state the reasoning. |
| `unavailable` | The source does not expose the requested information. |
| `unsupported` | The parser/tool does not support the format or field. |
| `error` | Reading or extraction failed; identify the failed operation. |

A creative choice for the new film is a decision, not an observed reference fact.
An effect present in an AE stack is not proof that it contributes to the image;
an MP4 cannot establish exact plugin settings. Claim visual verification only for
the rendered contribution actually inspected on a safe working copy.

Finish a study with source-backed findings, a proposed application and specific
unknowns. Add reusable lessons to the existing library article or matching
template only when warranted; keep raw reports/private locators in `local/`.
If the user asked for a video, continue into `workflows/create-video.md` rather
than stopping at the notes.
