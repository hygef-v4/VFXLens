# Evidence and Validation

This library records both directly extracted data and proposed recreation workflows. Because the two carry different epistemic weight, they must be labeled explicitly.

| Status | Meaning | Example |
| --- | --- | --- |
| `observed` | Directly read or measured | Keyframe Amplitude stored in `.aep`; alpha channel measured from an image |
| `inferred` | Evidence-backed inference | Proposing a decaying envelope to accent a beat |
| `unavailable` | Not provided by the static source | Runtime expression value when reading offline only |
| `unsupported` | Not yet decoded by the tool | Unparsed proprietary binary channel/payload |
| `error` | Read or extraction failure | `ffprobe` timeout; fallback timestamp rather than native PTS |

## What a Source-Backed Recipe Must Record

Source identifier and analysis date; comp/layer/property or timestamp/frame; effect stack order; units; keyframes/expressions/dependencies; enabled status; what was directly observed; the proposed application workflow; and any remaining unverified steps. A cryptographic hash identifies an exact source file but does not prove visual quality or redistribution rights.

In case studies, `evidence:` tokens identify private sources retained locally by the analyst. The library does not redistribute those payloads, and citing an identifier does not imply the reader has access to the private source. When reproducing a technique, record the locator and evidence of your new test rather than claiming the original source was re-verified.

## When to Upgrade the Verification Level

1. Inspect the full source and dependency chain, confirming the active timebase and actual render path.
2. Work on a disposable working copy, leaving the original source untouched.
3. Solo/toggle or isolate the specific step under test and compare rendered previews.
4. Record the outcome, conditions, artifacts, and failure modes, attaching shareable evidence.

Watching a rendered video never proves an exact plugin name or numeric parameter. A layer carrying an effect does not prove that effect contributes to the final render: the layer may be disabled, trimmed outside its `in`/`out` range, masked by a matte, or superseded by a prerender. Reading a static expression string does not guarantee it evaluates without error in the host.

**Further Reading:** [Technique Template](../templates/technique.md), [Case Study Template](../templates/case-study.md).
