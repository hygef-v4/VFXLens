# ElevenLabs (CLI, OAuth login) whole-script TTS with character timestamps -> ../voice_raw.mp3 + ../timing_raw.json
# (same shape as the skill's tts.mjs output, so tools/fit.py and captions.py work unchanged).
# Run: python voice/tts_eleven.py [voice_id] [model_id]
import base64, json, subprocess, sys, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent; PROD = ROOT.parent
S = json.loads((PROD / 'script.json').read_text(encoding='utf-8'))
VOICE = sys.argv[1] if len(sys.argv) > 1 else 'uC1r2TVqMMkHyjSAteKk'   # Ian - Deep, Punchy Social Hook Voice
MODEL = sys.argv[2] if len(sys.argv) > 2 else 'eleven_v3'
LEAD = 0.3   # fit.py assumes 0.3 s of silence before the first word
text = ' '.join(l['vo'] for l in S['lines'])   # the CLI drops everything after a newline in --text
raw = ROOT / 'el_full.json'
if not raw.exists():   # never pay twice for the same take
    exe = shutil.which('elevenlabs') or 'elevenlabs'
    r = subprocess.run([exe, 'text-to-speech', 'convert_with_timestamps', '--voice-id', VOICE, '--model-id', MODEL, '--text', text,
                        '--output-format', 'mp3_44100_128', '--format', 'json'], capture_output=True, text=True, encoding='utf-8')
    if r.returncode != 0 or '"audio_base64"' not in r.stdout: sys.exit('TTS failed: ' + (r.stderr or r.stdout)[:800])
    raw.write_text(r.stdout, encoding='utf-8')
d = json.loads(raw.read_text(encoding='utf-8'))
(ROOT / 'el_full.mp3').write_bytes(base64.b64decode(d['audio_base64']))
al = d['alignment']; ch, st, en = al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']
# characters -> words (whitespace separated), then assign words to script lines in order
words, cur = [], None
for c, a, b in zip(ch, st, en):
    if c.isspace():
        if cur: words.append(cur); cur = None
        continue
    if cur is None: cur = {'w': '', 't': a, 'e': b}
    cur['w'] += c; cur['e'] = b
if cur: words.append(cur)
lines, k = [], 0
for l in S['lines']:
    n = len(l['vo'].split()); ws = words[k:k + n]; k += n
    assert [w['w'] for w in ws] == l['vo'].split(), (l['id'], [w['w'] for w in ws])
    ws = [{'w': w['w'], 't': round(w['t'] + LEAD, 3), 'e': round(w['e'] + LEAD, 3)} for w in ws]
    lines.append({'id': l['id'], 'text': l['vo'], 'start': ws[0]['t'], 'end': ws[-1]['e'], 'words': ws})
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-t', str(LEAD), '-i', 'anullsrc=r=44100:cl=mono', '-i', ROOT / 'el_full.mp3',
                '-filter_complex', '[0:a][1:a]concat=n=2:v=0:a=1', '-ar', '44100', '-ac', '1', '-c:a', 'libmp3lame', '-q:a', '2', PROD / 'voice_raw.mp3'], check=True)
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', PROD / 'voice_raw.mp3'], capture_output=True, text=True).stdout)
json.dump({'voice': VOICE, 'model': MODEL, 'duration': round(dur, 3), 'lines': lines}, open(PROD / 'timing_raw.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for l in lines: print(f"{l['id']}: {l['start']:.2f}-{l['end']:.2f} {l['text'][:70]}")
print('duration', round(dur, 2))
