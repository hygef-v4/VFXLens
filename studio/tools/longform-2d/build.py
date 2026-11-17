# Timeline + Remotion manifest for a 2D long-form episode. Run in the production folder after voice_lines.py:
#   python <toolkit>/build.py [--lead 0.3] [--gap 0.26] [--tail 0.5] [--hold 1.5]
# Scenes play in script order. Inside a scene the first line starts --lead s in, each next line --gap s after the
# previous one ends (per line "gap" overrides), the scene ends --tail s after its last line (per scene "tail"); a
# scene with no lines lasts "hold" s. Writes studio/public/media/<slug>/longform.json and copies voice, music and SFX.
# Mouth tracks come from each line's loudness (open / mid / closed, held 3 frames); music ducks under the voice and
# goes silent on scenes marked "card": true. SFX anchors (sfx.json "at"): l3, l3.end, l3#2 (word 2), s2, s2.end, or seconds.
import argparse, json, re, shutil, sys, wave
from pathlib import Path
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('--lead', type=float, default=0.3); ap.add_argument('--gap', type=float, default=0.26)
ap.add_argument('--tail', type=float, default=0.5); ap.add_argument('--hold', type=float, default=1.5)
a = ap.parse_args()
P = Path.cwd(); slug = P.name
if not re.fullmatch(r'[a-z0-9-]+', slug): sys.exit(f'Production folder name "{slug}" must be lowercase letters, digits and dashes (it becomes the composition id)')
ROOT = next((p for p in [P, *P.parents] if (p / 'studio/package.json').is_file()), None)
if ROOT is None: sys.exit('Run inside the VFXLens repository (local/productions/<slug>/)')
S = json.loads((P / 'script.json').read_text(encoding='utf-8'))
L = {l['id']: l for l in json.loads((P / 'lines.json').read_text(encoding='utf-8'))}
fps = S.get('fps', 30); OUT = ROOT / 'studio/public/media' / slug
missing = [l['id'] for l in S['lines'] if l['id'] not in L]
if missing: sys.exit(f'No voice for {missing}: run voice_lines.py first')
if not (ROOT / 'studio/src/longform/episodes' / slug / 'episode.tsx').exists():
    print(f'! studio/src/longform/episodes/{slug}/episode.tsx is missing: the composition LongForm-{slug} will not exist', file=sys.stderr)

# ---- timeline (seconds), then frames
F = lambda t: int(round(t * fps))
scenes, lines, t = [], [], 0.0
for sc in S['scenes']:
    own = [l for l in S['lines'] if l['scene'] == sc['id']]
    start = t
    if own:
        cur = start + sc.get('lead', a.lead)
        for i, l in enumerate(own):
            lines.append({**l, 'start': cur, 'dur': L[l['id']]['duration']})
            cur += L[l['id']]['duration'] + (l.get('gap', a.gap) if i < len(own) - 1 else 0)
        end = cur + sc.get('tail', a.tail)
    else:
        end = start + sc.get('hold', a.hold)
    scenes.append({'id': sc['id'], 'kind': sc['kind'], 'card': bool(sc.get('card')), 'props': sc.get('props', {}), 'start': start, 'end': end})
    t = end
total = F(t)
known_scenes = {s['id'] for s in S['scenes']}
bad = [l['id'] for l in S['lines'] if l['scene'] not in known_scenes]
if bad: sys.exit(f'Lines point at unknown scenes: {bad}')

def mouth_track(wav, n, words, start_f):
    with wave.open(str(wav)) as f:
        sr, ch = f.getframerate(), f.getnchannels(); x = np.frombuffer(f.readframes(f.getnframes()), '<i2').astype(np.float64) / 32768
    x = x.reshape(-1, ch).mean(1); hop = sr / fps
    rms = np.array([np.sqrt(np.mean(x[int(i * hop):int((i + 1) * hop)] ** 2) + 1e-12) for i in range(n)])
    if rms.max() < 1e-4:   # silent draft: flap during each word so the blocking still reads
        out = ['c'] * n
        for w in words:
            for i in range(F(w['t']), min(n, F(w['e']))): out[i] = 'om'[((i - F(w['t'])) // 3) % 2]
        return ''.join(out)
    m = rms.max(); out, cur, held = [], 'c', 3
    for v in rms:
        tgt = 'o' if v > 0.45 * m else 'm' if v > 0.14 * m else 'c'
        if tgt != cur and held >= 3: cur, held = tgt, 0
        held += 1; out.append(cur)
    out[-1] = 'c'; return ''.join(out)

(OUT / 'voice').mkdir(parents=True, exist_ok=True)
vol = S.get('voice_volume', 1.0)
m_lines = []
for l in lines:
    rec = L[l['id']]; f0 = F(l['start']); n = max(1, F(l['start'] + l['dur']) - f0)
    src = P / 'voice' / f"{l['id']}.wav"; shutil.copy(src, OUT / 'voice' / src.name)
    m_lines.append({'id': l['id'], 'scene': l['scene'], 'speaker': l['speaker'], 'text': l['vo'], 'src': f'media/{slug}/voice/{src.name}',
                    'from': f0, 'durationInFrames': n, 'volume': vol,
                    'words': [{'w': w['w'], 'from': f0 + F(w['t']), 'to': f0 + max(F(w['t']) + 1, F(w['e']))} for w in rec['words']],
                    'mouth': mouth_track(src, n, rec['words'], f0)})
m_scenes = [{'id': s['id'], 'kind': s['kind'], 'card': s['card'], 'props': s['props'], 'from': F(s['start']), 'durationInFrames': F(s['end']) - F(s['start'])} for s in scenes]

# ---- music: base volume, ducked by the voice envelope, silent on cards (8-frame fades)
music = None
if S.get('music'):
    mu = S['music']; src = (P / mu['src']).resolve()
    if not src.exists(): sys.exit(f'music file not found: {src}')
    shutil.copy(src, OUT / f'music{src.suffix}')
    act = np.zeros(total)
    for ml in m_lines: act[ml['from']:ml['from'] + ml['durationInFrames']] = 1
    env = np.zeros(total); e = 0.0
    for i in range(total): e += (act[i] - e) * (0.25 if act[i] > e else 0.1); env[i] = e   # fast attack, slow release
    gate = np.ones(total)
    for s in m_scenes:
        if s['card']:
            a0, a1 = s['from'], s['from'] + s['durationInFrames']
            gate[a0:a1] = 0
            gate[max(0, a0 - 8):a0] = np.minimum(gate[max(0, a0 - 8):a0], np.linspace(1, 0, a0 - max(0, a0 - 8)))
            gate[a1:min(total, a1 + 8)] = np.minimum(gate[a1:min(total, a1 + 8)], np.linspace(0, 1, min(total, a1 + 8) - a1))
    v = mu.get('volume', 0.36) * (1 - mu.get('duck', 0.6) * env) * gate
    music = {'src': f'media/{slug}/music{src.suffix}', 'volumes': [round(float(x), 4) for x in v]}

# ---- SFX
def anchor(at):
    if isinstance(at, (int, float)): return float(at)
    mm = re.fullmatch(r'([A-Za-z0-9_-]+?)(?:#(\d+)|\.(end))?', str(at))
    if not mm: sys.exit(f'bad SFX anchor {at!r}')
    key, word, end = mm.groups()
    for l in lines:
        if l['id'] == key:
            if word is not None: return l['start'] + L[key]['words'][int(word)]['t']
            return l['start'] + (l['dur'] if end else 0)
    for s in scenes:
        if s['id'] == key: return s['end'] if end else s['start']
    sys.exit(f'SFX anchor {at!r} matches no line or scene')
sfx = []
if (P / 'sfx.json').exists():
    (OUT / 'sfx').mkdir(exist_ok=True)
    for i, e in enumerate(json.loads((P / 'sfx.json').read_text(encoding='utf-8'))):
        src = Path(e['src']) if Path(e['src']).is_absolute() else P / e['src']
        if not src.exists(): sys.exit(f'SFX file not found: {src}')
        name = f'{i:03d}-{src.name}'; shutil.copy(src, OUT / 'sfx' / name)
        sfx.append({'src': f'media/{slug}/sfx/{name}', 'from': max(0, F(anchor(e['at']) + e.get('offset', 0))), 'volume': e.get('volume', 0.5), 'note': e.get('note', src.stem)})

M = {'slug': slug, 'title': S.get('title', slug), 'fps': fps, 'width': S.get('width', 1920), 'height': S.get('height', 1080),
     'durationInFrames': total, 'scenes': m_scenes, 'lines': m_lines, 'music': music, 'sfx': sfx}
(OUT / 'longform.json').write_text(json.dumps(M, ensure_ascii=False), encoding='utf-8')
(P / 'timeline.json').write_text(json.dumps({'scenes': [{k: s[k] for k in ('id', 'kind', 'start', 'end')} for s in scenes],
                                             'lines': [{'id': l['id'], 'start': round(l['start'], 3), 'dur': l['dur']} for l in lines]}, indent=1), encoding='utf-8')
for s in scenes: print(f"{s['id']:>5} {s['kind']:<12} {s['start']:7.2f} - {s['end']:7.2f}")
print(f'{total} frames ({total / fps:.1f} s), {len(m_lines)} lines, {len(sfx)} SFX, music: {"yes" if music else "none"} -> {OUT / "longform.json"}')
