# Per-Character Staggered Text

**Purpose:** Drive individual characters, words, or lines through a shared motion curve at staggered time offsets rather than keyframing every glyph manually. This guide explains the underlying mechanism and proposed workflow; source expressions extracted offline have not been executed in the host to verify all runtime dependencies.

## Proposed Recreation Workflow

1. Choose the grouping unit (`Characters`, `Words`, or `Lines`), traversal direction, and ordering.
2. Keyframe the master motion curve on the text animator or controller property.
3. Have each text unit sample the master animation at an index-dependent time delay (`time - offset`). Keep fixed-second delays distinct from frame-duration delays (`thisComp.frameDuration`).
4. When adding damped cosine/sine overshoot, tune amplitude, frequency, exponential decay, and trigger time.
5. Inspect the first, middle, and last characters, whitespace handling, multi-line wraps, and diacritics on the actual display string.

## Three Implementation Approaches to Distinguish

- **Built-in Text Animator / Expression Selector:** Keeps the text layer live and editable while evaluating per-glyph selector weights.
- **TextEvo:** Relies on a companion pseudo-effect controller and linked expressions; never copy a single expression line in isolation and call it a self-contained recipe.
- **TextExploder or Raster Cutouts:** Splits glyphs/words into independent layers or image cutouts for collage-style parenting and drop shadows; no longer uses a single text layer's `textIndex` selector.

## Dependencies and Verification

Preserve controller names, property indices, delay units (seconds vs. frames), vector dimensions (`2D` vs. `3D`), and animator properties (`Position`, `Scale`, `Rotation`). A fixed-amplitude damped cosine selector behaves differently from velocity-driven keyframe overshoot. Applying Ease and Wizz can overwrite an existing property expression; select [Easing and Typography Tools](../../tools/easing-and-typography.md) according to the specific task.

**Sources:** [Takt Op, Section 5](../../case-studies/takt-op.md#5-per-character-staggered-text), [Standard](../../case-studies/standard.md), [Chal7z](../../case-studies/chal7z-presets.md), [AE Notes](../../case-studies/ae-notes.md). **Resources:** [Fonts](../../resources/fonts.md), [Cutouts and Frames](../../resources/cutouts-and-frames.md).
