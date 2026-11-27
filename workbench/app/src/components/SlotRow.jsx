import React from "react";
import { LadderChip } from "./Chip.jsx";

/* 97 of these per kit, most of them 'open'. Collapsed it is one 26px line: slot, binding,
   source, and the fault count filed against it. Open it carries the rule sentence, the
   authoring note, the variants ladder, the parameters with their kind, and the pack
   precedence. Prose stays beside the test: the rule sentence is never replaced by the number. */
/* The binding, the variant ranks and the parameter kinds are drawn as chips since Phase 17, one
   form per rung from `chips.js` (`components/Chip.jsx`); this file keeps no map of its own. */
const FAULT_LINK = {
  display: 'block',
  font: 'var(--fw-reg) 16px/1.45 var(--serif)',
  marginTop: 5,
  textAlign: 'left'
};
const FAULT_TEXT = {
  ...FAULT_LINK,
  color: 'var(--text-secondary)'
};
const EYE = {
  font: 'var(--type-eyebrow)',
  letterSpacing: 'var(--tr-eyebrow)',
  textTransform: 'uppercase',
  color: 'var(--text-secondary)'
};

/* REDRAWN FOR A READER (WP-18.1, 27 Nov 2026). The row was five Courier columns: the group's id,
   the slot's id, a binding chip, `↑1 georgian-colonial-ameri…` cut off at 190 px, and a fault
   count. It leads with the slot's NAME now, then what the style answers (its canonical variants,
   in the reading face), then where the answer comes from as a style's name. The slot's group is
   the heading its rows stand under (`KitSurface`), and each id is a margin note, shown on demand.
   Nothing the row can say was removed: the binding chip, the source and its distance, and the
   fault count are all still on the line. */
/* A variant has an id and no name. On the reading line its hyphens are set as spaces; opened, the
   chip prints the id exactly as the record writes it. */
function spaced(id) { return String(id == null ? '' : id).replace(/[-_]+/g, ' '); }

function SlotRow({ slot, expanded, onToggle, onSource, onFault, style }) {
  const [openInner, setOpenInner] = React.useState(false);
  const open = expanded != null ? expanded : openInner;
  const bind = slot.binding;
  const answer = (slot.variants || []).filter(function (v) { return v.status === 'canonical'; })
    .map(function (v) { return spaced(v.name); });
  const src = slot.source;
  return (
    <div className="tdl-slot" data-kit-slot={slot.id} data-open={open ? '' : undefined} style={style}>
      <button type="button" onClick={function () { onToggle ? onToggle(slot) : setOpenInner(!open); }}
        aria-expanded={open} className="tdl-slot-row">
        <span className="tdl-slot-name" data-binding={bind}>
          {slot.name || slot.id}<span className="tdl-record-note">{slot.id}</span>
        </span>
        <span className="tdl-slot-answer">{answer.join(' · ')}</span>
        <LadderChip ladder="binding" value={bind} style={{ flex: 'none', justifyContent: 'flex-start' }} />
        <span className="tdl-slot-source" title={src ? src.id : undefined}>
          {src ? (
            <>
              <span className="tdl-slot-up" aria-hidden="true">{src.distance === 0 ? '' : '↑' + src.distance}</span>
              {slot.sourceName || src.id}
            </>
          ) : '—'}
        </span>
        <span className="tdl-slot-faults" style={{ color: slot.faults ? 'var(--sev-serious)' : 'var(--text-secondary)' }}>
          {slot.faults ? slot.faults.length + ' fault' + (slot.faults.length === 1 ? '' : 's') : '—'}
        </span>
      </button>
      {open && (
        <div className="tdl-slot-body tdl-rise">
          {slot.rule && (
            <div className="tdl-slot-part">
              <div style={EYE}>rule</div>
              <p className="tdl-slot-rule">{slot.rule}</p>
            </div>
          )}
          {slot.variants && slot.variants.length > 0 && (
            <div className="tdl-slot-part">
              <div style={EYE}>variants</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 8 }}>
                {slot.variants.map(function (v) {
                  return <LadderChip key={v.name} title={v.note} ladder="variant" value={v.status}>{v.name}</LadderChip>;
                })}
              </div>
              {slot.variants.filter(function (v) { return v.note; }).map(function (v) {
                return (
                  <p key={v.name} className="tdl-slot-note">
                    <span style={{ font: 'var(--type-data-s)', color: 'var(--text-body)', marginRight: 8 }}>{v.name}</span>
                    {v.note}
                  </p>
                );
              })}
            </div>
          )}
          {slot.parameters && slot.parameters.length > 0 && (
            <div className="tdl-slot-part">
              <div style={EYE}>parameters</div>
              <table className="tdl-table" style={{ marginTop: 6, width: 'auto', minWidth: '60%' }}>
                <tbody>
                  {slot.parameters.map(function (p) {
                    return (
                      <tr key={p.name}>
                        <td className="tdl-num">{p.name}</td>
                        <td style={{ font: 'var(--type-data)', color: 'var(--text-body)' }}>{p.value}</td>
                        <td className="tdl-num">{p.unit}</td>
                        <td><LadderChip ladder="source" value={p.kind} /></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
          {slot.note && (
            <div className="tdl-slot-part">
              <div style={EYE}>note</div>
              <p className="tdl-slot-note" style={{ marginTop: 6 }}>{slot.note}</p>
            </div>
          )}
          <div style={{ display: 'flex', gap: 34, flexWrap: 'wrap', alignItems: 'flex-start' }}>
            {slot.packs && slot.packs.length > 0 && (
              <span>
                <span style={EYE}>pack precedence</span>
                {slot.packs.map(function (p) {
                  return <span key={p} style={{ display: 'block', font: 'var(--type-data-s)', color: 'var(--text-secondary)', marginTop: 5 }}>{p}</span>;
                })}
              </span>
            )}
            {slot.faults && slot.faults.length > 0 && (
              <span>
                <span style={EYE}>faults filed here</span>
                {slot.faults.map(function (fl) {
                  // A fault name navigates to its record, so it is a link and takes `.tdl-link` whole; with no
                  // handler it is plain text in the working grey (WP-14.33's audit).
                  return onFault
                    ? <button key={fl.id} type="button" onClick={function () { onFault(fl.id); }} className="tdl-link" style={FAULT_LINK}>{fl.name}</button>
                    : <span key={fl.id} style={FAULT_TEXT}>{fl.name}</span>;
                })}
              </span>
            )}
            {slot.source && onSource && (
              <button type="button" onClick={function () { onSource(slot.source.id); }} className="tdl-action"
                style={{ ...EYE, color: 'var(--text-accent)', alignSelf: 'flex-end', padding: '3px 6px', border: '1px solid transparent' }}>
                trace to origin
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
export default SlotRow;
export { SlotRow };
