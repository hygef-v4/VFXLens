import assert from 'node:assert/strict';
import {mkdir, writeFile} from 'node:fs/promises';

// A quiet tone verifies audio delivery without requiring private or licensed media.
const rate = 24000;
const seconds = 10;
const wav = Buffer.alloc(44 + rate * seconds * 2);
wav.write('RIFF', 0);
wav.writeUInt32LE(wav.length - 8, 4);
wav.write('WAVEfmt ', 8);
wav.writeUInt32LE(16, 16);
wav.writeUInt16LE(1, 20);
wav.writeUInt16LE(1, 22);
wav.writeUInt32LE(rate, 24);
wav.writeUInt32LE(rate * 2, 28);
wav.writeUInt16LE(2, 32);
wav.writeUInt16LE(16, 34);
wav.write('data', 36);
wav.writeUInt32LE(wav.length - 44, 40);
for (let i = 0; i < rate * seconds; i++) {
  const phase = (i / rate) % 2.5;
  const envelope = phase < 0.16 ? Math.sin(Math.PI * phase / 0.16) : 0;
  wav.writeInt16LE(Math.round(2200 * envelope * Math.sin(2 * Math.PI * 440 * i / rate)), 44 + i * 2);
}
assert.equal(wav.readUInt32LE(40) / (wav.readUInt32LE(24) * wav.readUInt16LE(32)), seconds);
await mkdir(new URL('../public/', import.meta.url), {recursive: true});
await mkdir(new URL('../../local/setup/', import.meta.url), {recursive: true});
await writeFile(new URL('../public/setup-tone.wav', import.meta.url), wav);
console.log('Prepared 10-second local audio verification asset.');
