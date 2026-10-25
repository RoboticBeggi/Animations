import React from 'react';
import {Composition} from 'remotion';
import {KineticCaptions, CaptionsProps} from './KineticCaptions';

const defaults: CaptionsProps = {
  words: [
    {word: 'Hello', start: 0.2, end: 0.6},
    {word: 'studio', start: 0.6, end: 1.2},
    {word: 'world', start: 1.3, end: 1.9},
  ],
  background: '#0b0b12',
  highlight: '#ffe14d',
  fontSize: 120,
};

export const Root: React.FC = () => (
  <Composition
    id="KineticCaptions"
    component={KineticCaptions}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={90}
    defaultProps={defaults}
    // Duration follows the last word, so any transcript just works.
    calculateMetadata={({props}) => ({
      durationInFrames: Math.ceil(((props.words.at(-1)?.end ?? 3) + 0.5) * 30),
    })}
  />
);
