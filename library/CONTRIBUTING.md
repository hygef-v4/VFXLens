# Contributing Knowledge

## Placing Articles in the Right Section

- `foundations`: Core principles reused across multiple techniques.
- `techniques`: A single actionable task; link to source evidence rather than duplicating raw tables.
- `styles`: Visual/rhythmic traits and how to combine technique and resource articles.
- `resources`: How to identify, select, and composite an asset type independently of personal packs.
- `tools`: What task a tool solves, its dependencies, versions, and limitations.
- `case-studies`: Source parameters/locations and what has been verified.

Each topic has one canonical article; use links when referencing it from different styles. Create directories only when they have content. Use `kebab-case` English filenames and write content in English.

## What a Useful Article Should Contain

Purpose, visual/audio indicators or inputs, step-by-step execution, controls and units, dependencies, common pitfalls, verification level, and sources. Start from the matching [template](templates/README.md). If no side-by-side render comparison has been performed, state that the workflow is a proposed guide.

## Public vs. Private Data

Keep machine-specific paths, personal asset inventories, raw analysis reports, and private media inside the Git-ignored `local/` directory. In public articles, use meaningful source identifiers and comp/layer/property locators; never create links that require private local files to read. Keep SHA-256 hashes to identify sources where appropriate, noting that a hash does not grant redistribution rights.

Do not commit third-party plugins, fonts, presets, projects, or media into the library without verified redistribution rights. The library does not grant licenses for referenced third-party sources; documentation licensing must be decided before any public release.

## Pre-Submission Checklist

- New articles are reachable from section indexes, and all file/heading links resolve.
- No local machine paths, personal inventories, or private report links appear in public pages.
- Numeric examples cite their source, unit/timebase, and limitations rather than masquerading as universal defaults.
- `observed`, `inferred`, `unavailable`, `unsupported`, and `error` states are clearly distinguished.
- No duplicate topic pages; style, tool, and resource pages link to the canonical article.

You do not need to run the analyzer or open After Effects solely to edit documentation. When updating a recipe, record the exact verification steps actually performed, including what remains unverified.

[Back to Library](README.md)
