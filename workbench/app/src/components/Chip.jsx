/* A CHIP ON ONE OF THE FOUR LADDERS (Phase 17, WP-17.1): a source, a binding, a variant's rank,
   a severity. The forms are `chips.js`'s; this draws them. The word is the caller's -- a status
   word read from the record or its glossary term -- and a value the ladder does not know is drawn
   as the bare word, never as another rung.

   <LadderChip ladder="source" value="measured" /> · <SourceChip kind="invented" />
   <BindingChip binding="forbidden" /> · <SeverityChip severity="serious">2</SeverityChip> */
import React from 'react';
import { chipOf, chipStyle } from '../chips.js';

export function LadderChip({ ladder, value, children, style, ...rest }) {
  const look = chipOf(ladder, value);
  const word = children ?? value;
  if (!look) return <span data-chip={ladder} data-value={value} style={{ font: 'var(--type-data-s)', ...style }} {...rest}>{word}</span>;
  const s = chipStyle(look);
  return (
    <span data-chip={ladder} data-value={value} style={{ ...s.box, ...style }} {...rest}>
      {s.swatch && <span aria-hidden="true" style={s.swatch} />}
      <span style={s.word}>{word}</span>
    </span>
  );
}

export const SourceChip = ({ kind, ...p }) => <LadderChip ladder="source" value={kind} {...p} />;
export const BindingChip = ({ binding, ...p }) => <LadderChip ladder="binding" value={binding} {...p} />;
export const SeverityChip = ({ severity, ...p }) => <LadderChip ladder="severity" value={severity} {...p} />;
