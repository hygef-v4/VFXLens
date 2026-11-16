export type Iris = {from: number; mid: number; to: number; cx: number; cy: number};

export const irisRadius = (frame: number, iris: Iris, width: number, height: number) => {
  const cover = Math.hypot(width * Math.max(iris.cx, 1 - iris.cx), height * Math.max(iris.cy, 1 - iris.cy));
  const progress = frame < iris.mid ? (iris.mid - frame) / (iris.mid - iris.from) : (frame - iris.mid) / (iris.to - iris.mid);
  return cover * Math.min(1, Math.max(0, progress));
};

