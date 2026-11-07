# Fonts: Selecting Typefaces and Verifying Language Support

## Identifying by Letterform Style

| Classification | Suggested Editorial Role | Watch Out For |
| --- | --- | --- |
| Clean neutral sans-serif | Captions, lyrics, and secondary labels | Character width, tracking, and export legibility |
| Tall narrow condensed | Short punchy titles | Diacritic collisions and tight uppercase kerning |
| Heavy display / ultra-bold | Impact keywords and sticker callouts | Counter spaces closing up under glow or motion blur |
| Serif | Editorial or nostalgic moods | Thin hairlines and serifs disappearing at small sizes |
| Script / brush | Accent words and decorative overlays | Connecting strokes, breathing room, and glyph mapping |
| Pixel / block | Retro, arcade, or HUD motifs | Preserving crisp pixel grids when scaling |

These are art-direction guidelines rather than rigid stylistic rules. A font filename containing "Glitch" does not automatically mean its outlines carry digital distortion.

## Selection Workflow

1. Render the **exact target phrase**, including diacritics, numerals, punctuation, and required casing.
2. Check for missing glyphs, `.notdef` tofu boxes, misplaced diacritics, or silent system-font fallbacks that break the visual style.
3. Inspect at final export resolution, over the actual background, and during motion.
4. Check line breaks, tracking, stroke weights, drop shadows, and legibility at peak motion blur.
5. Verify font licensing before embedding or redistributing font files in a project package.

Checking a Unicode `cmap` table is only an initial filter; it does not confirm OpenType shaping, combining diacritic placement, or rendering inside After Effects. Never assume all weights/styles in a family share identical glyph coverage, and watch out for novelty fonts that map logos or demo icons onto standard letter/number codepoints.

**Related:** [Staggered Text Typography](../techniques/typography/staggered-text.md), [Collage Style](../styles/collage.md), [Easing and Typography Tools](../tools/easing-and-typography.md).
