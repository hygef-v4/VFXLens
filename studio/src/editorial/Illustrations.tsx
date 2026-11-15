import React from 'react';

export type IllustrationKind =
  | 'hook'
  | 'timeline'
  | 'handoff'
  | 'context'
  | 'uncertain'
  | 'chip'
  | 'policy'
  | 'route'
  | 'response'
  | 'questions'
  | 'next'
  | 'recap';

type Props = {kind: IllustrationKind; frame: number; accent: string; light?: boolean};

const clamp = (value: number) => Math.max(0, Math.min(1, value));
const fade = (frame: number, start: number, length = 18) => clamp((frame - start) / length);

const Cube = ({x, y, w, h, depth = 22, color, top, side}: {x: number; y: number; w: number; h: number; depth?: number; color: string; top: string; side: string}) => (
  <g>
    <path d={`M${x} ${y} l${depth} -${depth * 0.58} h${w} l-${depth} ${depth * 0.58}z`} fill={top} />
    <path d={`M${x + w} ${y} l${depth} -${depth * 0.58} v${h} l-${depth} ${depth * 0.58}z`} fill={side} />
    <rect x={x} y={y} width={w} height={h} rx="10" fill={color} />
    <path d={`M${x + 10} ${y + 9} h${w - 20}`} stroke="white" strokeOpacity=".23" strokeWidth="3" strokeLinecap="round" />
  </g>
);

const Chip = ({x, y, s = 1, accent, light}: {x: number; y: number; s?: number; accent: string; light: boolean}) => (
  <g transform={`translate(${x} ${y}) scale(${s})`}>
    <ellipse cx="0" cy="85" rx="94" ry="21" fill="#101d1b" opacity=".14" />
    {[-54, -27, 0, 27, 54].map((n) => <g key={n} stroke={light ? '#253631' : '#f8f2e4'} strokeWidth="8" strokeLinecap="round"><path d={`M${n} 10v-24`} /><path d={`M${n} 126v24`} /><path d={`M-79 ${n + 53}h-24`} /><path d={`M79 ${n + 53}h24`} /></g>)}
    <path d="M-72 24 0-6 72 24 0 54z" fill={accent} />
    <path d="M-72 24 0 54v60l-72-30z" fill="#33534b" />
    <path d="M72 24 0 54v60l72-30z" fill="#213a34" />
    <rect x="-36" y="47" width="72" height="41" rx="8" fill="#f4efdF" opacity=".95" />
    <path d="M-22 60h44M-22 71h27" stroke="#32534a" strokeWidth="5" strokeLinecap="round" />
  </g>
);

const Server = ({x, y, scale = 1, accent}: {x: number; y: number; scale?: number; accent: string}) => (
  <g transform={`translate(${x} ${y}) scale(${scale})`}>
    <ellipse cx="0" cy="104" rx="75" ry="17" fill="#10201c" opacity=".14" />
    {[0, 1, 2].map((i) => <g key={i} transform={`translate(0 ${i * 34})`}>
      <path d="M-54 0 0-23 54 0 0 24z" fill="#e4ddc8" />
      <path d="M-54 0 0 24v27l-54-25z" fill="#35534a" />
      <path d="M54 0 0 24v27l54-25z" fill="#203c35" />
      <circle cx="-34" cy="12" r="4" fill={i === 0 ? accent : '#a4b5a1'} />
      <path d="M-20 13h22" stroke="#a4b5a1" strokeWidth="4" strokeLinecap="round" />
    </g>)}
  </g>
);

const Person = ({x, y, scale = 1, accent}: {x: number; y: number; scale?: number; accent: string}) => (
  <g transform={`translate(${x} ${y}) scale(${scale})`}>
    <ellipse cx="0" cy="105" rx="63" ry="14" fill="#10201c" opacity=".14" />
    <path d="M-41 48q41-38 82 0l12 48h-106z" fill="#29463f" />
    <circle cy="15" r="27" fill="#e7b99a" />
    <path d="M-28 11q3-33 31-29 23 4 25 28-20-9-56 1" fill={accent} />
    <path d="M-7 56h14" stroke="#f3eee0" strokeWidth="7" strokeLinecap="round" />
  </g>
);

export const EditorialIllustration = ({kind, frame, accent, light = false}: Props) => {
  const paper = light ? '#fffdf5' : '#f2eddf';
  const ink = light ? '#24342f' : '#f5f0e2';
  const muted = light ? '#73827a' : '#87968d';
  const id = `ill-${kind}-${React.useId().replace(/:/g, '')}`;
  const p = (start: number, len = 22) => fade(frame, start, len);
  let art: React.ReactNode;

  switch (kind) {
    case 'hook':
    case 'chip': {
      const pulse = (frame % 72) / 72;
      art = <>
        <path d="M178 285h190q38 0 60-28l55-66q20-24 53-24h120" fill="none" stroke={muted} strokeWidth="7" strokeLinecap="round" strokeDasharray="12 14" opacity=".46" />
        <circle cx={178 + pulse * 480} cy={285 - Math.sin(pulse * Math.PI) * 100} r="10" fill={accent} />
        <Server x={162} y={337} scale={.75} accent={accent} />
        <Server x={740} y={335} scale={.7} accent={accent} />
        <Chip x={450} y={219} s={1.12} accent={accent} light={light} />
        <path d="M352 430h190" stroke={ink} strokeWidth="2" opacity=".2" />
        <rect x="376" y="436" width="148" height="34" rx="17" fill={light ? '#e6ead9' : '#293e37'} />
        <text x="450" y="459" textAnchor="middle" fontSize="15" fontWeight="800" letterSpacing="2" fill={ink}>AI · GPU</text>
      </>;
      break;
    }
    case 'timeline':
      art = <>
        <ellipse cx="451" cy="482" rx="300" ry="27" fill="#10201c" opacity=".12" />
        <g transform="rotate(-7 350 300)">
          <rect x="205" y="154" width="270" height="310" rx="18" fill="#d7d0bd" />
          <rect x="190" y="138" width="270" height="310" rx="18" fill={paper} />
          <path d="M224 188h190M224 216h130M224 254h190M224 276h155" stroke={muted} strokeWidth="9" strokeLinecap="round" opacity=".54" />
          <rect x="224" y="310" width="204" height="91" rx="12" fill="#e7eadb" />
          <path d="M240 334h148M240 357h112M240 379h87" stroke="#718177" strokeWidth="8" strokeLinecap="round" />
          <rect x="323" y="127" width="73" height="15" rx="7" fill={accent} />
        </g>
        {[0, 1].map((i) => {
          const x = i ? 535 : 555;
          const y = i ? 271 : 364;
          return <g key={i} transform={`translate(${x} ${y})`}>
            <rect x="0" y="0" width="192" height="143" rx="18" fill={i ? '#ced5c5' : '#dde2d1'} />
            <rect x="0" y="0" width="192" height="42" rx="18" fill={i ? '#405d51' : accent} />
            <rect x="0" y="22" width="192" height="20" fill={i ? '#405d51' : accent} />
            {[0, 1, 2, 3].map((n) => <circle key={n} cx={30 + n * 42} cy="69" r="8" fill={i ? '#667b6e' : '#a7bc9c'} opacity={n === Math.floor((frame / 16) % 4) ? 1 : .47} />)}
            <path d="M25 102h138M25 120h92" stroke="#718177" strokeWidth="7" strokeLinecap="round" opacity=".65" />
          </g>;
        })}
        <path d="M475 328h60" stroke={ink} strokeWidth="4" strokeDasharray="7 8" opacity=".7" />
        <path d="m526 317 14 11-14 11" fill="none" stroke={accent} strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" />
      </>;
      break;
    case 'handoff':
      art = <>
        <path d="M158 435 451 300l291 135-292 131z" fill={light ? '#e4e7d9' : '#293e37'} />
        <path d="M188 420 451 300l261 120-261 120z" fill={paper} />
        <Person x={284} y={224} scale={1.12} accent={accent} />
        <Person x={620} y={224} scale={1.12} accent="#577266" />
        <path d="M345 308q95-80 186 0" fill="none" stroke={accent} strokeWidth="8" strokeDasharray="10 12" strokeLinecap="round" />
        <path d="M480 297l20 13-21 12" fill="none" stroke={accent} strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" />
        <g transform={`translate(${447 + Math.sin(frame / 13) * 5} ${311 + Math.cos(frame / 13) * 5})`}>
          <path d="M-29 4 0-9 29 4 0 18z" fill={accent} />
          <path d="M-29 4 0 18v26l-29-13z" fill="#547360" />
          <path d="M29 4 0 18v26l29-13z" fill="#315348" />
        </g>
        <path d="M220 480h144M536 480h144" stroke={muted} strokeWidth="4" strokeLinecap="round" opacity=".5" />
      </>;
      break;
    case 'context':
      art = <>
        <ellipse cx="450" cy="489" rx="260" ry="27" fill="#10201c" opacity=".12" />
        <path d="M225 195q0-22 22-22h187l72 68v216H247q-22 0-22-22z" fill="#d4cebc" />
        <path d="M247 173h181l61 61h-45q-17 0-17-17v-44" fill="#fffdf5" />
        <path d="M270 281h163M270 308h121M270 336h157" stroke={muted} strokeWidth="10" strokeLinecap="round" opacity=".58" />
        <path d="M421 299q0-88 88-88t88 88v119H421z" fill="#527064" />
        <path d="M444 298q0-63 65-63t65 63v98H444z" fill="#e5e9d9" />
        <Person x={509} y={278} scale={.62} accent={accent} />
        <path d="M586 306h109q22 0 22 22v102q0 19-19 19H582q-18 0-18-18V329q0-23 22-23z" fill={accent} />
        <path d="m625 351 24-12 24 12v25q0 24-24 36-24-12-24-36z" fill="#f7f0df" />
        <path d="m637 374 9 9 16-19" fill="none" stroke="#4d6859" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" />
      </>;
      break;
    case 'uncertain':
      art = <>
        <path d="M268 170h214q17 0 17 17v190q0 17-17 17H268q-17 0-17-17V187q0-17 17-17z" fill={paper} />
        <path d="M289 213h153M289 241h118M289 271h136" stroke={muted} strokeWidth="9" strokeLinecap="round" opacity=".5" />
        <circle cx="465" cy="339" r="96" fill={light ? '#e9eddd' : '#344a42'} stroke={accent} strokeWidth="13" />
        <circle cx="465" cy="339" r="62" fill="none" stroke={accent} strokeWidth="4" opacity=".35" />
        <path d="M533 408 650 526" stroke="#35564b" strokeWidth="32" strokeLinecap="round" />
        <path d="M450 311q3-25 28-25 28 0 28 26 0 17-20 29-15 10-15 25" fill="none" stroke={ink} strokeWidth="13" strokeLinecap="round" />
        <circle cx="471" cy="391" r="7" fill={accent} />
        <path d="M615 200q0-34 39-34 37 0 37 32 0 24-25 33-20 8-20 28" fill="none" stroke={accent} strokeWidth="7" strokeLinecap="round" />
        <circle cx="646" cy="279" r="5" fill={accent} />
        <path d="m658 353 24-12 24 12v27q0 23-24 35-24-12-24-35z" fill={accent} />
        <path d="m670 377 9 9 15-18" fill="none" stroke="#f7f0df" strokeWidth="4" strokeLinecap="round" />
      </>;
      break;
    case 'policy':
      art = <>
        <ellipse cx="433" cy="495" rx="284" ry="26" fill="#10201c" opacity=".12" />
        <path d="m228 260 208-89 208 89z" fill="#d6d0bd" />
        <path d="M247 259h378v22H247z" fill="#71847a" />
        {[0, 1, 2, 3, 4].map((i) => <g key={i} transform={`translate(${275 + i * 78} 290)`}>
          <rect width="30" height="143" rx="8" fill="#e8e1cf" />
          <path d="M-8 0h46M-8 132h46" stroke="#71847a" strokeWidth="9" strokeLinecap="round" />
        </g>)}
        <path d="M230 431h412v28H230z" fill="#405c51" />
        <path d="M197 459h478v26H197z" fill="#243d35" />
        <g transform="translate(567 340)">
          <path d="M0 0v116M65 0v116" stroke={accent} strokeWidth="10" strokeLinecap="round" />
          <path d="M-15 35h95" stroke={accent} strokeWidth="8" strokeLinecap="round" />
          <rect x="16" y="43" width="35" height="37" rx="5" fill={accent} />
          <path d="m24 62 8 8 14-17" fill="none" stroke="#f6f0df" strokeWidth="4" strokeLinecap="round" />
        </g>
        <path d="M226 532h418" stroke={muted} strokeWidth="4" strokeDasharray="8 12" opacity=".5" />
      </>;
      break;
    case 'route': {
      const points = [{x: 142, y: 397}, {x: 318, y: 281}, {x: 482, y: 398}, {x: 652, y: 277}, {x: 774, y: 397}];
      const d = points.map((pt, i) => `${i ? 'L' : 'M'}${pt.x} ${pt.y}`).join(' ');
      const q = (frame % 100) / 100;
      const idx = Math.floor(q * 4);
      const local = q * 4 - idx;
      const from = points[idx]; const to = points[idx + 1];
      art = <>
        <path d={d} fill="none" stroke={muted} strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="4 15" opacity=".6" />
        <path d={d} fill="none" stroke={accent} strokeWidth="3" strokeLinecap="round" strokeDasharray="2 16" opacity=".7" />
        {points.map((pt, i) => <g key={i} transform={`translate(${pt.x} ${pt.y})`}>
          <ellipse cy="36" rx="55" ry="14" fill="#10201c" opacity=".12" />
          {i === 0 || i === 4 ? <g><path d="M-32-18 0-33 33-18 0-2z" fill="#e6dfcb"/><path d="M-32-18 0-2v35l-32-17z" fill="#416154"/><path d="M33-18 0-2v35l33-17z" fill="#29483d"/><rect x="-8" y="-14" width="16" height="15" rx="3" fill={accent}/></g> : i === 1 || i === 3 ? <g><path d="M-32-7 0-23 32-7 0 9z" fill="#e5ddc8"/><path d="M-32-7 0 9v27l-32-16z" fill="#3e5b50"/><path d="M32-7 0 9v27l32-16z" fill="#29473c"/><rect x="-10" y="-13" width="20" height="21" rx="3" fill={i === 1 ? accent : '#9baa91'}/></g> : <g><circle cy="-5" r="27" fill="#e7b99a"/><path d="M-30 31q30-31 60 0" fill="#315146"/><path d="M-27-9q5-26 28-24 20 2 26 25-25-8-54-1" fill={accent}/></g>}
          <circle cx="0" cy="-52" r={i === 2 ? 8 : 5} fill={i === 2 ? accent : ink} opacity={p(5 + i * 4)} />
        </g>)}
        <g transform={`translate(${from.x + (to.x - from.x) * local} ${from.y + (to.y - from.y) * local - 25})`}>
          <path d="M-14 0 0-8 14 0 0 8z" fill={accent}/><path d="M-14 0 0 8v14l-14-7z" fill="#577360"/><path d="M14 0 0 8v14l14-7z" fill="#345649"/>
        </g>
      </>;
      break;
    }
    case 'response':
      art = <>
        <path d="M191 447 450 326l258 121-258 121z" fill={light ? '#e2e6d8' : '#2a4038'} />
        <path d="M229 434 450 332l220 102-220 102z" fill={paper} />
        <Server x={451} y={208} scale={1.5} accent={accent} />
        {[0, 1, 2].map((i) => <g key={i} transform={`translate(${274 + i * 158} ${373 + (i % 2) * 31})`}>
          <circle r="30" fill={accent} opacity={.16 + .18 * Math.sin(frame / 10 + i)} />
          <circle r="18" fill={accent} />
          <path d="m-8 0 6 7 12-15" fill="none" stroke="#f7f0df" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        </g>)}
        <path d="M281 482q169 77 339 0" fill="none" stroke={accent} strokeWidth="5" strokeDasharray="4 13" strokeLinecap="round" />
      </>;
      break;
    case 'questions':
      art = <>
        <path d="M165 445h565" stroke={muted} strokeWidth="5" strokeDasharray="6 14" opacity=".45" />
        <g transform={`translate(267 ${264 + Math.sin(frame / 14) * 7})`}>
          <Person x={0} y={0} scale={1.02} accent={accent} />
          <circle cx="0" cy="-28" r="53" fill="none" stroke={accent} strokeWidth="4" opacity=".5" />
          <path d="M-21 84h42" stroke={accent} strokeWidth="7" strokeLinecap="round" />
        </g>
        <g transform={`translate(462 ${301 + Math.sin(frame / 14 + 2) * 7})`}>
          <circle r="57" fill={paper} stroke="#8b9b8f" strokeWidth="4" />
          <circle cy="-6" r="28" fill="none" stroke={ink} strokeWidth="9" />
          <path d="m19 16 31 32" stroke={accent} strokeWidth="12" strokeLinecap="round" />
          <path d="M-14 99h28" stroke={muted} strokeWidth="7" strokeLinecap="round" />
        </g>
        <g transform={`translate(654 ${265 + Math.sin(frame / 14 + 4) * 7})`}>
          <Server x={0} y={0} scale={.76} accent={accent} />
          <path d="M-27 143h54" stroke={accent} strokeWidth="7" strokeLinecap="round" />
        </g>
      </>;
      break;
    case 'next':
      art = <>
        <ellipse cx="451" cy="478" rx="238" ry="25" fill="#10201c" opacity=".12" />
        <g transform="rotate(-8 435 325)">
          <rect x="269" y="159" width="343" height="308" rx="23" fill="#d4cebb" />
          <rect x="253" y="143" width="343" height="308" rx="23" fill={paper} />
          <rect x="253" y="143" width="343" height="76" rx="23" fill={accent} />
          <path d="M253 194h343" stroke={accent} strokeWidth="49" />
          {[0, 1, 2, 3, 4, 5, 6].map((i) => <g key={i} transform={`translate(${290 + (i % 4) * 72} ${253 + Math.floor(i / 4) * 75})`}>
            <rect width="48" height="48" rx="9" fill={i === (Math.floor(frame / 20) % 7) ? accent : '#e1e5d6'} />
            {i === (Math.floor(frame / 20) % 7) && <path d="m12 24 8 8 17-19" fill="none" stroke="#f7f0df" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />}
          </g>)}
          <path d="M321 139v34M528 139v34" stroke="#f4efdf" strokeWidth="12" strokeLinecap="round" />
        </g>
        <path d="M618 334h93" stroke={muted} strokeWidth="8" strokeLinecap="round" />
        <path d="m690 314 25 20-25 20" fill="none" stroke={accent} strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" />
      </>;
      break;
    case 'recap':
      art = <>
        <path d="M230 297q114-143 220 0t220 0" fill="none" stroke={muted} strokeWidth="7" strokeDasharray="8 13" opacity=".6" />
        <path d="M230 297q114 143 220 0t220 0" fill="none" stroke={muted} strokeWidth="7" strokeDasharray="8 13" opacity=".6" />
        <g transform={`translate(${450 + Math.cos(frame / 27) * 5} ${298 + Math.sin(frame / 27) * 5})`}>
          <circle r="91" fill={accent} opacity=".13" />
          <Chip x={0} y={-45} s={.65} accent={accent} light={light} />
        </g>
        {[[230, 297], [670, 297], [450, 473]].map(([x, y], i) => <g key={i} transform={`translate(${x} ${y})`}>
          <ellipse cy="41" rx="71" ry="17" fill="#10201c" opacity=".13" />
          <circle r="52" fill={i === 1 ? '#e8e1cf' : '#38584c'} />
          {i === 0 ? <path d="M-25 5 0-8 25 5 0 18zM-25 5 0 18v21l-25-13zM25 5 0 18v21l25-13z" fill="#a4b299" /> : i === 1 ? <path d="M-21-12h42v40h-42zM-13-24h26v12h-26z" fill={accent} /> : <path d="M-23-15h46v36h-46zM-30-22h60v11h-60z" fill={accent} />}
        </g>)}
        <circle cx="450" cy="182" r="8" fill={accent} opacity={p(0)} />
        <circle cx="784" cy="297" r="8" fill={accent} opacity={p(12)} />
      </>;
      break;
  }

  return (
    <svg viewBox="0 0 900 620" width="100%" height="100%" role="img" aria-label={`${kind} editorial illustration`} preserveAspectRatio="xMidYMid meet">
      <defs>
        <linearGradient id={`${id}-shine`} x1="0" x2="1" y1="0" y2="1">
          <stop offset="0" stopColor={accent} stopOpacity=".2" />
          <stop offset="1" stopColor={accent} stopOpacity="0" />
        </linearGradient>
      </defs>
      <ellipse cx="450" cy="520" rx="360" ry="48" fill={`url(#${id}-shine)`} />
      {art}
    </svg>
  );
};
