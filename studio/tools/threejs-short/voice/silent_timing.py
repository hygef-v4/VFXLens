# Draft timing without a voice: script.json -> timing.json (+ engine/film/timing.json) and a silent voice.wav, at a
# fixed reading pace. Use it to block shots and render a captions-only cut before paying for TTS; replace it with the
# real voice chain (tts_eleven -> tighten -> evenpace -> fit -> align) once the script is final.
# Usage (production folder): python voice/silent_timing.py [--wps 2.8] [--gap 0.35] [--lead 0.4]
import argparse, json, re, shutil, wave
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument('--wps', type=float, default=2.8); ap.add_argument('--gap', type=float, default=0.35); ap.add_argument('--lead', type=float, default=0.4)
a = ap.parse_args(); S = json.loads(Path('script.json').read_text(encoding='utf-8'))
spoken = lambda w: 3 if re.fullmatch(r'\d{4}', re.sub(r'\D', '', w)) else 1   # a year is read as ~3 words (same rule as evenpace)
t, lines = a.lead, []
for l in S['lines']:
    ws = []
    for w in l['vo'].split():
        d = spoken(w) / a.wps; ws.append({'w': w, 't': round(t, 3), 'e': round(t + d * 0.85, 3)}); t += d
    assert ws, f"{l['id']}: empty line"
    lines.append({'id': l['id'], 'text': l['vo'], 'start': ws[0]['t'], 'end': ws[-1]['e'], 'words': ws}); t += a.gap
T = {'voice': 'silent draft', 'duration': round(t + a.lead, 3), 'lines': lines}
Path('timing.json').write_text(json.dumps(T, ensure_ascii=False, indent=1), encoding='utf-8')
shutil.copy('timing.json', Path('engine/film/timing.json'))
with wave.open('voice.wav', 'wb') as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(48000); f.writeframes(b'\0\0' * int(T['duration'] * 48000))
print(f"{len(lines)} lines, {sum(len(l['words']) for l in lines)} words, {T['duration']} s")
