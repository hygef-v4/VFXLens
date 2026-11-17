// Demo episode for the "argument-board" style (library/styles/argument-board.md): "Vì sao GPU chạy AI nhanh hơn CPU?",
// about 22 s, one board scene. Facts in the script are illustrative and unverified; the race bars are labelled "minh họa".
// Copy with `scaffold.py <slug> --style argument-board`, then replace the question, claim, evidence and revise.
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {
  ArgumentRail, BOARD, BoardBackground, BoardNote, BoardSvg, LineCarry, QuestionTitle, Revise, Skeptic, accel, focus, io3, measure, out3,
  useLine, type Episode, type Line, type SceneProps,
} from '../../kit';

const W = (l: Line, i: number) => l.words[Math.min(i, l.words.length - 1)].from;
const PANEL = {x: 1090, y: 236, w: 734, h: 664};

/** Evidence region: cores as squares, the same work as two racing bars (illustrative). */
const Mechanism: React.FC<{l4: Line; l5: Line; dimAt: number}> = ({l4, l5, dimAt}) => {
  const frame = useCurrentFrame(); const P = PANEL;
  const cpuAt = W(l4, 2); const gpuAt = W(l4, 8); const workAt = W(l5, 3); const doneAt = W(l5, 10);
  if (frame < cpuAt - 10) return null;
  const span = Math.max(1, doneAt - workAt);
  const gpuP = io3((frame - workAt) / span); const cpuP = 0.12 * Math.min(1, Math.max(0, (frame - workAt) / (span + 60)));
  const pulse = frame >= workAt && gpuP < 1;
  const label = (t: string, y: number, at: number) => <text x={P.x + 56} y={y} fontFamily={BOARD.mono} fontSize={32} letterSpacing={3} fill={BOARD.muted} opacity={out3((frame - at) / 6)}>{t}</text>;
  const bar = (y: number, p: number, name: string) => (
    <g opacity={out3((frame - workAt) / 6)}>
      <rect x={P.x + 56} y={y} width={420} height={18} rx={9} fill={BOARD.faint} />
      <rect x={P.x + 56} y={y} width={420 * p} height={18} rx={9} fill={p >= 1 ? BOARD.accent : BOARD.ink} />
      <text x={P.x + 500} y={y + 17} fontFamily={BOARD.sans} fontWeight={700} fontSize={36} fill={p >= 1 ? BOARD.accent : BOARD.ink} style={{fontVariantNumeric: 'tabular-nums'}}>{name} {Math.round(p * 100)}%</text>
    </g>
  );
  const cols = 46; const rows = 8; const cell = 13.4;
  return (
    <BoardSvg opacity={focus(frame, dimAt)}>
      {label('CPU · vài chục lõi mạnh', P.y + 108, cpuAt)}
      {Array.from({length: 16}, (_, i) => {
        const k = out3((frame - cpuAt - accel(i, 16, 14)) / 6); const lit = frame >= workAt && Math.floor((frame - workAt) / 10) % 2 === 0;
        return <rect key={i} x={P.x + 56 + (i % 8) * 74} y={P.y + 150 + Math.floor(i / 8) * 74 + (1 - k) * 12} width={60} height={60} rx={8} fill={lit ? BOARD.ink : BOARD.core} stroke={BOARD.ink} strokeWidth={2} opacity={k} />;
      })}
      {label('GPU · hàng nghìn lõi nhỏ', P.y + 392, gpuAt)}
      {Array.from({length: cols * rows}, (_, i) => {
        const cx = i % cols; const cy = Math.floor(i / cols); const k = out3((frame - gpuAt - accel(cx + cy, cols + rows, 18)) / 5);
        const lit = (pulse && Math.floor((frame - workAt) / 6) % 2 === 0) || gpuP >= 1;
        return <rect key={i} x={P.x + 56 + cx * cell} y={P.y + 432 + cy * cell} width={cell - 3} height={cell - 3} rx={2} fill={lit ? BOARD.ink : BOARD.core} opacity={k} />;
      })}
      {bar(P.y + 560, cpuP, 'CPU')}
      {bar(P.y + 610, gpuP, 'GPU')}
      <text x={P.x + P.w - 24} y={P.y + 52} textAnchor="end" fontFamily={BOARD.mono} fontSize={28} fill={BOARD.muted} opacity={out3((frame - workAt) / 6)}>minh họa</text>
    </BoardSvg>
  );
};

const Board: React.FC<SceneProps> = () => {
  const l1 = useLine('l1'); const l2 = useLine('l2'); const l3 = useLine('l3'); const l4 = useLine('l4'); const l5 = useLine('l5'); const l6 = useLine('l6');
  const end = (l: Line) => l.from + l.durationInFrames;
  const carryAt = W(l4, 0) - 6; const size = 96; const baseline = 470;
  return (
    <AbsoluteFill>
      <BoardBackground />
      <ArgumentRail chapters={['Câu hỏi', 'Hiểu lầm', 'Bằng chứng', 'Kết luận']} steps={[l1.from, l2.from, l4.from, l6.from]} />
      <QuestionTitle chunks={['Vì sao', 'GPU', 'chạy AI', 'nhanh hơn CPU?']} at={[W(l1, 0), W(l1, 2), W(l1, 5), W(l1, 7)]} demoteAt={end(l1) + 22} />
      <Revise label="Nhiều người nghĩ" lead="GPU" wrong="mạnh hơn." right="đông hơn." baseline={baseline} size={size}
        showAt={[W(l2, 0), W(l2, 4), W(l2, 5)]} strikeAt={W(l6, 2) - 2} rewriteAt={W(l6, 6) - 4} dimAt={carryAt + 20} undimAt={l6.from - 8} />
      <LineCarry at={carryAt} from={[BOARD.col + measure('GPU mạnh hơn.', size), baseline + 30]} box={PANEL} />
      <Mechanism l4={l4} l5={l5} dimAt={l6.from - 8} />
      <Skeptic speaker="skeptic" inAt={l3.from - 10} convincedAt={W(l6, 6)} />
      <BoardNote text="Từng lõi GPU yếu hơn mà?" at={W(l3, 1)} out={end(l3) + 8} />
    </AbsoluteFill>
  );
};

export const episode: Episode = {slug: 'demo-board', title: 'Vì sao GPU chạy AI nhanh hơn CPU?', scenes: {board: Board}};
