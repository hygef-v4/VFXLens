# Create a new three.js character-short production from the claude-3d-animated-shorts engine, with this toolkit's
# fixes applied. Usage (from the repo root):
#   python studio/tools/threejs-short/scaffold.py <slug> [--skill-dir <claude-3d-animated-shorts dir>]
# Result: local/productions/<slug>/ (ignored) with engine/ (copied files; node_modules + assets linked to the skill,
# never modified), voice/, audio/, qa/, render_fast.sh and a film.inc.js to write the shots in.
import argparse, os, shutil, subprocess, sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
REPO = KIT.parents[2]
ap = argparse.ArgumentParser(); ap.add_argument('slug'); ap.add_argument('--skill-dir', default=str(Path.home() / '.claude' / 'skills' / 'claude-3d-animated-shorts'))
a = ap.parse_args()
SK = Path(a.skill_dir) / 'engine'
if not (SK / 'main.js').exists(): sys.exit(f'engine not found: {SK} (install the claude-3d-animated-shorts skill, run its fetch-assets/npm install)')
if not (SK / 'node_modules').exists() or not (SK / 'assets' / 'rigs').exists(): sys.exit('skill engine is missing node_modules or assets: run `npm install` and `bash scripts/fetch-assets.sh` in the skill')
P = REPO / 'local' / 'productions' / a.slug
if P.exists(): sys.exit(f'{P} already exists; continue that production instead of overwriting it')
E = P / 'engine'; (E / 'film').mkdir(parents=True); (E / 'out').mkdir()
for f in ['main.js', 'stickrig.js', 'world.js', 'index.html', 'viewer.html', 'package.json']: shutil.copy(SK / f, E / f)
for f in ['Anton.ttf', 'Inter-Black.otf', 'ph_words.json', 'ph_lines.json']: shutil.copy(SK / 'film' / f, E / 'film' / f)
for f in ['render.cjs', 'post.js']: shutil.copy(KIT / 'engine' / f, E / f)   # resilient renderer, lens CA/distortion/grain uniforms
# film hook: ?viewer=1&film=1 runs film.inc.js (inlined by build.py) instead of the skill's demo skit
m = (E / 'main.js').read_text(encoding='utf-8')
a1 = "if (Q.has('viewer')) { if (Q.has('skit')) window.ready = false;"; a2 = "  if (!Q.has('skit')) loop(); else {"
if m.count(a1) != 1 or m.count(a2) != 1: sys.exit('main.js changed upstream: add the film hook by hand (see README.md)')
m = m.replace(a1, "if (Q.has('viewer')) { if (Q.has('skit') || Q.has('film')) window.ready = false;").replace(a2, "  if (Q.has('film')) {\n// @@FILM@@\n  } else if (!Q.has('skit')) loop(); else {")
(E / 'main.js').write_text(m, encoding='utf-8')
(E / 'build.py').write_text("""# Inline film.inc.js into main.js at the @@FILM@@ marker -> main.film.js (served by film.html). Run after each edit.
from pathlib import Path
d = Path(__file__).parent
m = (d / 'main.js').read_text(encoding='utf-8')
assert m.count('// @@FILM@@') == 1
(d / 'main.film.js').write_text(m.replace('// @@FILM@@', (d / 'film.inc.js').read_text(encoding='utf-8')), encoding='utf-8')
(d / 'film.html').write_text((d / 'index.html').read_text(encoding='utf-8').replace('./main.js', './main.film.js'), encoding='utf-8')
print('built main.film.js')
""", encoding='utf-8')
shutil.copy(KIT / 'examples' / 'starter.film.inc.js', E / 'film.inc.js')   # minimal starter film; rewrite cast/props/shots
for name in ['node_modules', 'assets']:   # link, never copy or modify the skill's dependencies and CC0 assets
    src, dst = SK / name, E / name
    if os.name == 'nt': subprocess.run(['cmd', '/c', 'mklink', '/J', str(dst), str(src)], check=True, capture_output=True)
    else: os.symlink(src, dst, target_is_directory=True)
for sub, files in {'voice': ['voice/tts_eleven.py', 'voice/tighten.py', 'voice/evenpace.py', 'voice/fit.py', 'voice/align.py', 'voice/silent_timing.py', 'examples/voice_quote_splice.example.py'], 'audio': ['audio/cues.example.py', 'audio/build_manifest.example.py', 'audio/music_fallback.py'], 'qa': ['qa/grid.py', 'qa/luma.py', 'qa/audit.py']}.items():
    (P / sub).mkdir(exist_ok=True)
    for f in files: shutil.copy(KIT / f, P / sub / Path(f).name.replace('.example', ''))
shutil.copy(KIT / 'render_fast.example.sh', P / 'render_fast.sh')
(P / 'assets' / 'sfx' / 'lib').mkdir(parents=True)
(P / 'script.json').write_text('{\n  "title": "",\n  "voice": "",\n  "lines": [\n    { "id": "l1", "vo": "" }\n  ]\n}\n', encoding='utf-8')
(P / 'production.md').write_text(f"# {a.slug}\n\nFollow workflows/threejs-character-short.md. Record here: contract, sources/fact-check, creative decisions, voice ids, resource-library path (VFX_RESOURCES), commands run, QA results, open issues, next action.\n", encoding='utf-8')
print('created', P)
