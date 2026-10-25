import React from 'react';
import {AbsoluteFill, spring, useCurrentFrame, useVideoConfig} from 'remotion';

export type Word = {word: string; start: number; end: number};
export type CaptionsProps = {
  words: Word[];
  background: string;
  highlight: string;
  fontSize: number;
};

// Show the word being spoken (plus context) with a spring pop on entry.
export const KineticCaptions: React.FC<CaptionsProps> = ({words, background, highlight, fontSize}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const active = words.findIndex((w) => t >= w.start && t < w.end + 0.15);
  const first = Math.max(0, active - 2);
  const visible = active < 0 ? [] : words.slice(first, active + 3);

  return (
    <AbsoluteFill style={{background, justifyContent: 'center', alignItems: 'center'}}>
      <div style={{display: 'flex', flexWrap: 'wrap', gap: 24, justifyContent: 'center', padding: 60}}>
        {visible.map((w, i) => {
          const idx = first + i;
          const pop = spring({frame: frame - Math.round(w.start * fps), fps, config: {damping: 12, stiffness: 180}});
          const isActive = idx === active;
          return (
            <span
              key={idx}
              style={{
                fontFamily: 'Impact, Arial Black, sans-serif',
                fontSize,
                textTransform: 'uppercase',
                color: isActive ? highlight : '#fff',
                transform: `scale(${0.6 + 0.4 * pop})`,
                opacity: Math.min(1, pop),
              }}
            >
              {w.word}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
