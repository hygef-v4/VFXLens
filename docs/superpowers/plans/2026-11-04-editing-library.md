# Editing Library Implementation Plan

> **For agentic workers:** Execute inline with superpowers:executing-plans; this is a documentation refactor, not an analyzer behavior change.

**Goal:** Turn the existing editing notes into a portable Markdown library with reusable techniques and resources, style entrypoints, and separate source evidence.

**Architecture:** `library/` holds foundations, techniques, styles, resources, tools, case studies and contribution templates. `local/` holds byte-preserved original notes, inventories and machine-specific source mappings and is ignored by Git. Case-specific values stay in case studies; general articles link to them rather than duplicate their tables.

**Tech Stack:** Markdown, Git ignore rules, Python standard library for migration and link verification; no dependency changes.

**Spec:** Conversation-approved hybrid structure: techniques are the foundation, styles are navigation, resources explain asset types independently of the user's local collection. The user explicitly requested execution after reviewing that structure.

## Global Constraints

- Never change original projects, video, presets, installed skills' source evidence, or asset directories.
- Public library pages contain no absolute machine paths, local inventories, private analysis output dependencies, or redistributed media.
- Preserve observed/inferred/unavailable distinctions, source hashes, comp/layer locations and timebase limitations.
- English directory names, Vietnamese content. No website, package dependencies, licensing decision, commit, push or publication in this task.

## Review Focus

- Moved Markdown links and Unicode/duplicate heading fragments must still resolve.
- Private drive paths and inventory counts must not become general instructions.
- Case-study numeric examples must not become default settings or claims of verified renders.
- Readers with a clean checkout must navigate without local source files.
- The personal skill entrypoint and repository README must point to the new library.

### Task 1: Preserve source notes and separate local data

**Files:** `.gitignore`, `local/original-notes/*.md`, `local/source-mappings/notes.json`, `local/inventories/*.md`.

- [x] Copy all ten original notes byte-for-byte and record SHA-256 before changing documentation.
- [x] Keep machine inventories under ignored `local/`; verify Git ignores them.

### Task 2: Build the library and migrate source evidence

**Files:** `library/README.md`, section READMEs, foundation/technique/style/resource/tool articles, six `library/case-studies/*.md`, `library/templates/*.md`, `library/CONTRIBUTING.md`.

- [x] Migrate case studies, replace machine paths with evidence IDs mapped locally, preserve original section anchors.
- [x] Write reusable guides for eight existing technique groups, seven resource types, four styles and tool selection.
- [x] Add contribution templates that distinguish evidence from proposed applications; do not invent verified recipes.

### Task 3: Update entrypoints and verify

**Files:** `README.md`, personal `ae-edit-recipes/SKILL.md`, original `docs/editing*.md` and `docs/adobe-tools-index.md` removed after preservation; `local/verification/check_library.py`.

- [x] Update README and personal skill pointer to `library/README.md`.
- [x] Remove superseded notes only after snapshot hashes match; source media untouched.
- [x] Check every library file/heading link, all articles' reachability, absence of machine paths/output links, source archive hashes and Git ignore status.
- [x] Review the complete documentation change, fix material findings and record results here. Runtime tests are unnecessary because analyzer code is unchanged.

## Execution notes

- Ruling: execute in the current user-visible checkout on branch `docs/editing-library` so untracked notes stay available; no second checkout or runtime code changes are needed.
- Ruling: use local one-off verification rather than adding a permanent documentation framework or tests that mirror file generation.

## Verification and review

- `uv run python local/verification/check_library.py`: 45 public pages, 219 local file/heading links, all pages reachable; 10 original snapshots match SHA-256, 17 evidence IDs map locally, local storage ignored, no machine paths/private output locators in the library.
- Independent read-only review compared all six migrated case studies against archived notes: no Critical/Important findings. One Minor finding restored the Takt Op composition-time versus demo-time warning near the introduction.
- Ruling: external URL freshness, original analysis accuracy, licensing, and AE/render behavior are outside this documentation migration. No runtime tests, source media operations, installation, commit, push or publication were performed.
