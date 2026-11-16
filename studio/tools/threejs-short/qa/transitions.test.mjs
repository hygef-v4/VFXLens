import assert from 'node:assert/strict';
import {test} from 'node:test';
import {irisRadius, whipMotion} from '../../../src/shorts/transitions.ts';

test('iris fully covers an off-center frame at both ends and closes at the cut', () => {
  const iris = {from: 10, mid: 16, to: 24, cx: 0.7, cy: 0.3};
  const cover = Math.hypot(1080 * 0.7, 1920 * 0.7);
  for (const f of [0, 10, 24, 30]) assert.ok(irisRadius(f, iris, 1080, 1920) >= cover);
  assert.equal(irisRadius(16, iris, 1080, 1920), 0);
  assert.ok(irisRadius(13, iris, 1080, 1920) > 0);
  assert.ok(irisRadius(20, iris, 1080, 1920) < cover);
});

test('whip is confined to three frames either side and reverses translation across the cut', () => {
  for (const dir of [-1, 1]) {
    const whip = {at: 30, dir};
    for (const f of [0, 27, 33, 50]) assert.deepEqual(whipMotion(f, whip, 1080), {x: 0, blur: 0});
    assert.ok(whipMotion(29, whip, 1080).x * dir > 0);
    assert.ok(whipMotion(30, whip, 1080).x * dir < 0);
    assert.ok(whipMotion(30, whip, 1080).blur > 0);
  }
});
