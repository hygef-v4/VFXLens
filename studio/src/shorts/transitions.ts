export type Iris = {from: number; mid: number; to: number; cx: number; cy: number};
export type Whip = {at: number; dir: number};

export const irisRadius = (frame: number, iris: Iris, width: number, height: number) => {
  const cover = Math.hypot(width * Math.max(iris.cx, 1 - iris.cx), height * Math.max(iris.cy, 1 - iris.cy));
  const progress = frame < iris.mid ? (iris.mid - frame) / (iris.mid - iris.from) : (frame - iris.mid) / (iris.to - iris.mid);
  return cover * Math.min(1, Math.max(0, progress));
};

export const whipMotion = (frame: number, whip: Whip, width: number) => {
  const delta = frame - whip.at;
  if (Math.abs(delta) >= 3) return {x: 0, blur: 0};
  const strength = 1 - Math.abs(delta) / 3;
  return {x: (delta < 0 ? 1 : -1) * whip.dir * width * 0.12 * strength, blur: width * 0.045 * strength};
};
