# Replace TTS word timestamps in timing.json with ElevenLabs forced alignment on the final voice.wav (run after fit.py).
# TTS timestamps start each word ~0.13 s early (leading silence is assigned to the next word; up to 0.35 s after a pause),
# so captions popped before the word was heard. Keeps timing_tts.json; duration is unchanged.
# Usage: python voice/align.py [saved_alignment.json]   (the saved file skips the API call)
import json, shutil, subprocess, sys
from pathlib import Path
if not json.load(open('timing.json', encoding='utf-8')).get('aligned'): shutil.copy('timing.json', 'timing_tts.json')   # fresh fit.py output
T = json.load(open('timing_tts.json', encoding='utf-8')); ws = [w for l in T['lines'] for w in l['words']]
if len(sys.argv) > 1: raw = Path(sys.argv[1]).read_text(encoding='utf-8')
else: raw = subprocess.run([shutil.which('elevenlabs') or 'elevenlabs',   # npm shim (.cmd) on Windows
                            'forced-alignment', 'create', '--file', 'voice.wav', '--text', ' '.join(w['w'] for w in ws), '--format', 'json'],
                           capture_output=True, text=True, encoding='utf-8', check=True).stdout
A = [w for w in json.loads(raw)['words'] if w['text'].strip()]
assert len(A) == len(ws), (len(A), len(ws))
for w, a in zip(ws, A):
    assert a['text'].strip().lower() == w['w'].strip().lower(), (a['text'], w['w'])
    w['t'], w['e'] = round(a['start'], 3), round(max(a['end'], a['start'] + 0.05), 3)
for l in T['lines']: l['start'], l['end'] = l['words'][0]['t'], l['words'][-1]['e']
T['aligned'] = True
json.dump(T, open('timing.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'aligned {len(ws)} words')
