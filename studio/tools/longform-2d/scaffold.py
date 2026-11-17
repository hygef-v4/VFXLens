# Start a 2D long-form production: local/productions/<slug>/ (script.json, sfx.json, production.md) and the episode code
# studio/src/longform/episodes/<slug>/episode.tsx copied from the demo. Never overwrites an existing file.
# Usage (repo root): python studio/tools/longform-2d/scaffold.py <slug> [--title "My Episode"] [--example demo-2d]
import argparse, re, shutil, sys
from pathlib import Path

TOOL = Path(__file__).resolve().parent; ROOT = TOOL.parents[2]
ap = argparse.ArgumentParser(); ap.add_argument('slug'); ap.add_argument('--title'); ap.add_argument('--example', default='demo-2d')
a = ap.parse_args()
if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', a.slug): sys.exit('slug: lowercase letters, digits and single dashes (it becomes LongForm-<slug>)')
ex = TOOL / 'examples' / a.example
if not ex.is_dir(): sys.exit(f'no example {ex}')
prod = ROOT / 'local/productions' / a.slug; prod.mkdir(parents=True, exist_ok=True)
for f in ex.iterdir():
    if f.is_file() and not (prod / f.name).exists(): shutil.copy(f, prod / f.name); print('created', prod / f.name)
ep = ROOT / 'studio/src/longform/episodes' / a.slug / 'episode.tsx'
if not ep.exists():
    src = (ROOT / 'studio/src/longform/episodes/demo-2d/episode.tsx').read_text(encoding='utf-8')
    src = src.replace("slug: 'demo-2d'", f"slug: '{a.slug}'").replace("title: 'The Missing Cent'", f"title: {(a.title or a.slug)!r}")
    ep.parent.mkdir(parents=True, exist_ok=True); ep.write_text(src, encoding='utf-8'); print('created', ep)
md = prod / 'production.md'
if not md.exists():
    md.write_text(f'# {a.title or a.slug}\n\nWorkflow: workflows/2d-long-form-video.md\n\n## Decisions\n\n## Facts to check\n\n## Renders\n', encoding='utf-8')
print(f'''
Next (in {prod}):
  python ../../../studio/tools/longform-2d/voice_lines.py --silent     # draft timing, no credits
  python ../../../studio/tools/longform-2d/build.py
  cd ../../../studio && npx remotion studio                            # LongForm-{a.slug}
''')
