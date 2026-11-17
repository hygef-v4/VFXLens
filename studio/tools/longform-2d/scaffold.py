# Start a 2D long-form production in a chosen style: local/productions/<slug>/ (script.json, sfx.json, production.md)
# and studio/src/longform/episodes/<slug>/episode.tsx, both copied from that style's demo. Never overwrites a file.
# Usage (repo root): python studio/tools/longform-2d/scaffold.py <slug> --style ink-puppet-night|argument-board [--title "..."]
# Styles are described in library/styles/<style>.md; the agent asks the user which one before scaffolding.
import argparse, re, shutil, sys
from pathlib import Path

STYLES = {'ink-puppet-night': 'demo-2d', 'argument-board': 'demo-board'}   # style -> demo episode / example folder
TOOL = Path(__file__).resolve().parent; ROOT = TOOL.parents[2]
ap = argparse.ArgumentParser(); ap.add_argument('slug'); ap.add_argument('--style', required=True, choices=STYLES); ap.add_argument('--title')
a = ap.parse_args()
if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', a.slug): sys.exit('slug: lowercase letters, digits and single dashes (it becomes LongForm-<slug>)')
demo = STYLES[a.style]; ex = TOOL / 'examples' / demo
prod = ROOT / 'local/productions' / a.slug; prod.mkdir(parents=True, exist_ok=True)
for f in ex.iterdir():
    if f.is_file() and not (prod / f.name).exists(): shutil.copy(f, prod / f.name); print('created', prod / f.name)
ep = ROOT / 'studio/src/longform/episodes' / a.slug / 'episode.tsx'
if not ep.exists() and a.slug != demo:
    src = (ROOT / 'studio/src/longform/episodes' / demo / 'episode.tsx').read_text(encoding='utf-8')
    src = re.sub(r"slug: '[^']*'", f"slug: '{a.slug}'", src, count=1)
    src = re.sub(r"title: '[^']*'", f"title: {(a.title or a.slug)!r}", src, count=1)
    ep.parent.mkdir(parents=True, exist_ok=True); ep.write_text(src, encoding='utf-8'); print('created', ep)
md = prod / 'production.md'
if not md.exists():
    md.write_text(f'# {a.title or a.slug}\n\nStyle: {a.style} (library/styles/{a.style}.md)\nWorkflow: workflows/2d-long-form-video.md\n\n'
                  '## Decisions\n\n## Facts to check\n\n## Renders\n', encoding='utf-8')
print(f'''
Style {a.style}. Next (in {prod}):
  python ../../../studio/tools/longform-2d/voice_lines.py --silent     # draft timing, no credits (Vietnamese: --wps 4.2)
  python ../../../studio/tools/longform-2d/build.py
  cd ../../../studio && npx remotion studio                            # LongForm-{a.slug}
''')
