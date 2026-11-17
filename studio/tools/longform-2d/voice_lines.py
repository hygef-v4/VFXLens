# One voice file per script line (narrator + characters), each with word times -> voice/<id>.wav + lines.json.
# Run in the production folder: python <toolkit>/voice_lines.py [--silent] [--model eleven_v3] [--speed 1.0] [--only l3 l5]
#   ElevenLabs (CLI, `elevenlabs auth login`): each speaker uses cast.<speaker>.voice from script.json; every raw take is
#   cached in voice/raw/ by text+voice+model+speed, so a rerun never pays twice. --only regenerates just those lines.
#   --silent: no API call; silent audio and evenly spaced word times at --wps, to block shots and render a draft cut.
# Takes are trimmed on the waveform (speech onset / tail above -45 dB), never on alignment times, so word endings are not
# clipped; then a light voice chain (high-pass, de-ess, compressor; a small room on characters) and the cast pan.
import argparse, base64, hashlib, json, re, shutil, subprocess, sys, wave
from pathlib import Path
import numpy as np

sys.stdout.reconfigure(encoding='utf-8', errors='replace')   # Vietnamese lines on a cp1252 Windows console

SR = 48000
ap = argparse.ArgumentParser()
ap.add_argument('--silent', action='store_true'); ap.add_argument('--wps', type=float, default=2.6)
ap.add_argument('--model', default='eleven_v3'); ap.add_argument('--speed', default='1.0')
ap.add_argument('--only', nargs='*', default=[])
a = ap.parse_args()
S = json.loads(Path('script.json').read_text(encoding='utf-8'))
cast = S['cast']; VOICE = Path('voice'); RAW = VOICE / 'raw'; RAW.mkdir(parents=True, exist_ok=True)
old = {l['id']: l for l in json.loads(Path('lines.json').read_text(encoding='utf-8'))} if Path('lines.json').exists() else {}
spoken = lambda w: 3 if re.fullmatch(r'\d{4}', re.sub(r'\D', '', w)) else 1   # a year is read as ~3 words

CHAIN = {
    'narrator': 'highpass=f=70,equalizer=f=300:t=q:w=1.2:g=-1.5,equalizer=f=3500:t=q:w=1:g=2,deesser=i=0.35,'
                'acompressor=threshold=-22dB:ratio=3:attack=5:release=120:makeup=3dB',
    'character': 'highpass=f=80,equalizer=f=3200:t=q:w=1:g=2,deesser=i=0.35,'
                 'acompressor=threshold=-22dB:ratio=3:attack=5:release=120:makeup=3dB,aecho=0.8:0.6:28|47:0.10|0.06',
}

def decode(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, '<i2').astype(np.float64) / 32768

def write_wav(path, x, channels=1):
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(channels); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())

def chars_to_words(al):
    words, cur = [], None
    for c, s, e in zip(al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']):
        if c.isspace():
            if cur: words.append(cur); cur = None
            continue
        if cur is None: cur = {'w': '', 't': s, 'e': e}
        cur['w'] += c; cur['e'] = e
    if cur: words.append(cur)
    return words

def tts(line, voice):
    key = hashlib.sha1(json.dumps([line['vo'], voice, a.model, a.speed]).encode()).hexdigest()[:10]
    cached = RAW / f"{line['id']}-{key}.json"
    if not cached.exists():
        exe = shutil.which('elevenlabs') or 'elevenlabs'
        r = subprocess.run([exe, 'text-to-speech', 'convert_with_timestamps', '--voice-id', voice, '--model-id', a.model, '--text', line['vo'],
                            '--voice-settings.speed', a.speed, '--output-format', 'mp3_44100_128', '--format', 'json'],
                           capture_output=True, text=True, encoding='utf-8')
        if r.returncode != 0 or '"audio_base64"' not in r.stdout: sys.exit(f"TTS failed on {line['id']}: " + (r.stderr or r.stdout)[:600])
        cached.write_text(r.stdout, encoding='utf-8')
    d = json.loads(cached.read_text(encoding='utf-8'))
    mp3 = RAW / f"{line['id']}-{key}.mp3"; mp3.write_bytes(base64.b64decode(d['audio_base64']))
    x = decode(mp3); words = chars_to_words(d['alignment'])
    expect = line['vo'].split()
    if [w['w'] for w in words] != expect: print(f"  ! {line['id']}: alignment words differ from the script; check the take", file=sys.stderr)
    # trim on the waveform: onset - 30 ms, tail (last sample above -45 dB of the peak) + 60 ms
    thr = np.abs(x).max() * 10 ** (-45 / 20); idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0: sys.exit(f"{line['id']}: the take is silent")
    i0 = max(0, idx[0] - int(0.03 * SR)); i1 = min(len(x), idx[-1] + int(0.06 * SR))
    x = x[i0:i1]; off = i0 / SR; dur = len(x) / SR
    words = [{'w': w['w'], 't': round(min(dur, max(0, w['t'] - off)), 3), 'e': round(min(dur, max(0, w['e'] - off)), 3)} for w in words]
    return x, words

out = []
for line in S['lines']:
    sp = line['speaker']
    if sp not in cast: sys.exit(f"{line['id']}: speaker '{sp}' is not in script.json cast")
    if a.only and line['id'] not in a.only and line['id'] in old:
        out.append(old[line['id']]); continue
    if a.silent:
        t, ws = 0.05, []
        for w in line['vo'].split():
            d = spoken(w) / a.wps; ws.append({'w': w, 't': round(t, 3), 'e': round(t + d * 0.85, 3)}); t += d
        x = np.zeros(int((t + 0.1) * SR)); words = ws
    else:
        voice = cast[sp].get('voice')
        if not voice: sys.exit(f"cast.{sp}.voice is empty: pick a voice id (ElevenLabs voice list) or use --silent")
        x, words = tts(line, voice)
    role = cast[sp].get('role', 'character'); pan = float(cast[sp].get('pan', 0))
    mono = VOICE / f"{line['id']}_dry.wav"; write_wav(mono, x)
    gl, gr = np.sqrt(0.5 * (1 - pan)) * 1.414, np.sqrt(0.5 * (1 + pan)) * 1.414   # centre = unity on both sides
    chain = ('' if a.silent else CHAIN['narrator' if role == 'narrator' else 'character'] + ',') + f'pan=stereo|c0={gl:.3f}*c0|c1={gr:.3f}*c0'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(mono), '-af', chain, '-ar', str(SR), str(VOICE / f"{line['id']}.wav")], check=True)
    mono.unlink()
    dur = round(len(x) / SR, 3)
    out.append({'id': line['id'], 'scene': line['scene'], 'speaker': sp, 'text': line['vo'], 'duration': dur, 'silent': a.silent, 'words': words})
    print(f"{line['id']:>5} {sp:<10} {dur:5.2f}s  {line['vo'][:70]}")
Path('lines.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
print(f"{len(out)} lines, {sum(l['duration'] for l in out):.1f} s of speech")
