import React from "react";
import { useNames } from "../names/useNames.js";

/* P2 — the cascade is a first-class object, not a breadcrumb and not a tooltip. Tidewater
   Georgian resolves through 20 levels; appalachian-log-house reaches 23, and monterey-revival 53. Craftsman resolves
   78 of its 97 slots from ancestors before a line of its own was written, and that fact
   should be visible. Two forms: compact (one line, for a slot row) and full (the ladder). */
const EYE = {
  font: 'var(--type-eyebrow)',
  letterSpacing: 'var(--tr-eyebrow)',
  textTransform: 'uppercase',
  color: 'var(--text-secondary)'
};
/* A LEVEL'S OWN BINDINGS AS A BAR (Phase 17, WP-17.10): specified, extends and forbidden, each its
   binding ink, the length against the busiest level in the cascade, so a thin kit reads thin. */
function LevelBar({ counts, max }) {
  const w = 64, seg = [['specified', 'var(--bind-specified)'], ['extends', 'var(--bind-extends)'],
    ['forbidden', 'var(--bind-forbidden)']];
  let x = 0;
  return /*#__PURE__*/React.createElement("svg", {
    "aria-hidden": "true", width: w, height: 8, style: { flex: 'none', alignSelf: 'center' }
  }, seg.map(function ([k, ink]) {
    const len = (counts[k] || 0) / max * w;
    const r = /*#__PURE__*/React.createElement("rect", { key: k, x: x, y: 1, width: len, height: 6, style: { fill: ink } });
    x += len;
    return r;
  }));
}

function ProvenanceTrace({
  cascade,
  sourceId,
  mode = 'full',
  onSelect,
  collapseFrom = 6,
  style
}) {
  const [all, setAll] = React.useState(false);
  const names = useNames();
  if (mode === 'compact') {
    const hit = cascade.filter(function (l) {
      return l.id === sourceId;
    })[0] || cascade[0];
    return /*#__PURE__*/React.createElement("span", {
      style: {
        display: 'inline-flex',
        alignItems: 'baseline',
        gap: 7,
        ...style
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--text-secondary)'
      }
    }, "\u2191", hit.distance), /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data-s)',
        color: hit.distance === 0 ? 'var(--text-body)' : 'var(--text-secondary)'
      }
    }, hit.id));
  }
  const shown = all ? cascade : cascade.slice(0, collapseFrom);
  const maxB = Math.max(1, ...cascade.map(function (l) { return l.bindings || 0; }));
  const hidden = cascade.length - shown.length;
  const nameOf = function (id) {
    const e = names.status === 'ready' ? names.index.get('style:' + id) : null;
    return (e && e.name) || id;
  };
  return (
    <div style={style} data-cascade="">
      <div className="tdl-section-head" style={{ marginBottom: 6 }}>
        <span style={EYE}>cascade&nbsp;&nbsp;(nearest first)</span>
        <span style={{ font: 'var(--type-data-s)', color: 'var(--text-secondary)' }}>{cascade.length} levels</span>
      </div>
      <div>
        {shown.map(function (l) {
          const isSource = l.id === sourceId;
          return (
            <div key={l.id} className="tdl-cascade-level">
              {/* A LEVEL IS ITS STYLE'S NAME, its bar and its count (WP-18.1). It was the id in
                  Courier with the three counts spelled out beside it and every ban it writes run on
                  beneath: one ladder took a screen of machine text. The counts are the row's title,
                  and the bans fold under a count of their own. */}
              <button type="button" onClick={onSelect ? function () { onSelect(l.id); } : undefined}
                className="tdl-cascade-row" aria-current={isSource ? 'true' : undefined} title={l.detail || undefined}
                style={{ cursor: onSelect ? 'pointer' : 'default' }}>
                <span className="tdl-cascade-n">{l.distance}</span>
                <span className="tdl-cascade-name" data-own={l.distance === 0 ? '' : undefined}>
                  {nameOf(l.id)}<span className="tdl-record-note">{l.id}</span>
                </span>
                {l.counts && <LevelBar counts={l.counts} max={maxB} />}
                <span className="tdl-cascade-n" style={{ width: 22 }}>{l.bindings}</span>
              </button>
              {l.bans && l.bans.length > 0 && (
                <details data-cascade-bans={l.id} className="tdl-cascade-bans">
                  <summary>
                    <span aria-hidden="true" style={{ color: 'var(--refusal-text)', marginRight: 6 }}>{'✕'}</span>
                    {l.bans.length}
                  </summary>
                  <div>
                    {l.bans.map(function (b) { return b.variant ? b.slot + ' · ' + b.variant : b.slot; }).join(', ')}
                  </div>
                </details>
              )}
            </div>
          );
        })}
      </div>
      {hidden > 0 && (
        // a control that navigates takes the link ink through the class (WP-14.33); Phase 17 moved
        // it off the gilt, which removes its row from inks.test's gilt remainder
        <button type="button" className="tdl-link" onClick={function () { setAll(true); }}
          style={{ font: 'var(--fw-reg) 14px/1.4 var(--serif)', marginTop: 10 }}>
          show {hidden} further levels
        </button>
      )}
    </div>
  );
}
export default ProvenanceTrace;
export { ProvenanceTrace };
