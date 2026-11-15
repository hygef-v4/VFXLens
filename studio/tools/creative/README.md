# Creative skills

The installed canonical skill folders are in `.agents/skills/`, with linked copies in `.claude/skills/` for Claude Code. `skills-lock.json` records managed installs; `manual-skills.json` records the one patched upstream installation. These downloaded folders are ignored, not vendored source.

Installed families: GSAP's eight skills, Blender claymation, painted animation, kinetic-reel, official earshot/real-sound and Lemo-Opuscar. The HyperFrames skills live in the separate `../hyperframes/` project; Remotion and LottieFiles guidance live at the studio root.

Managed entries use GitHub sources; the reviewed earshot, Lemo and painted-animation revisions are pinned in `skills-lock.json`. From this directory, restore those entries for both agents with:

```powershell
$env:DO_NOT_TRACK = '1'
npx skills add https://github.com/Leonxlnx/earshot/tree/4ac3d2ac2b151e1c23376f9ce7f3047a17050013 --skill earshot --skill real-sound -a codex -a claude-code
npx skills add https://github.com/lemomo-ai/lemo-opuscar/tree/3a7132b996be0241c1ea0ab180d519f06e6f10b6 --skill lemo-opuscar -a codex -a claude-code
npx skills add https://github.com/tuzhechen2005/opus-video-skills/tree/59744a69c7b916cfbe4c4ec84006b0c2f5e2fde1 --skill painted-animation -a codex -a claude-code
npx skills add greensock/gsap-skills --skill '*' -a codex -a claude-code
npx skills add angrypenguinpng/blender-claymation-skill --skill blender-claymation -a codex -a claude-code
```

The last two commands fetch upstream's current revision; compare it with the recorded lock hashes and review changes before accepting an update. Preserve custom edits and inspect existing destinations before replacing them. Kinetic-reel needs the manual repair below.

## Kinetic-reel compatibility patch

The inspected upstream `skills/kinetic-reel/SKILL.md` uses an unquoted `: ` inside its one-line YAML description. Skills CLI skips it with a YAML parse error. Its installed copy has only that description value quoted as a YAML string; the body and all supporting files are unchanged. The original repository/revision and patch are recorded in `manual-skills.json`.

To reproduce: copy the trusted `skills/kinetic-reel/` source folder to `.agents/skills/kinetic-reel/`, quote that frontmatter value, validate the YAML, and create the corresponding Claude directory link. Updating upstream can restore the invalid line; validate after updates. Do not count a CLI exit code as proof that every requested skill was installed.

## Windows helpers

The claymation helper accepts `BLENDER` as its executable path. Use the Blender path recorded in `local/setup/status.json`; if a shell helper is needed on Windows, use Git Bash rather than assuming macOS or a WSL installation. Preserve the user's current scene and create a separate production file/process. The repo's shared safety rules take precedence over third-party example defaults.

Keep these skills' runtime dependencies and outputs in their selected production workspace. A skill folder is guidance, not proof that its character rig or output has been rendered successfully.
