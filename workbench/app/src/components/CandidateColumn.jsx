import React from "react";
import { nativityLine } from "../candidateOrder.js";
import { Term } from "./Term.jsx";
import { JudgmentMark } from "./JudgmentMark.jsx";
import { MarkGlyph } from "./MarkGlyph.jsx";

/* P4 — rank them, never crown one. Three rules this component exists to enforce:
   1. trades_away sits adjacent to the score at all times, never behind a disclosure.
   2. score and rightness are DIFFERENT AXES. The native diagram often scores worst; the
      'why' line reads at the same weight as the number so nobody conflates them.
   3. THE NUMBER SHOWS ITS WORKING. It used to be a demerit total — lower is better, no
      ceiling, and the line under it printed the WEIGHTS as a legend ("100/fatal · 8/serious
      · 1/minor − fidelity (7)") which reads as a count of fatal findings and explains
      nothing about the figure above it. It is now a composite out of 100, higher is better,
      and every axis is shown with its own share, its weight and the denominator that share
      was taken over. An axis that could not be evaluated says so and has its weight dropped.
   4. A DISQUALIFIED CANDIDATE IS STILL SCORED, and its number can be the highest on screen.
      A fatal finding is carried in the band below the score, not by withholding the number:
      withholding it was built first and measured, and five briefs of eight came back with
      EVERY candidate disqualified, four dashes and no way to tell them apart. The ordering
      is what keeps a disqualified plan behind a clean one — see candidateOrder.js. */
const EYE = {
  font: 'var(--type-eyebrow)',
  letterSpacing: 'var(--tr-eyebrow)',
  textTransform: 'uppercase',
  color: 'var(--text-secondary)'
};
const SEV = {
  fatal: 'var(--sev-fatal)',
  serious: 'var(--sev-serious)',
  minor: 'var(--sev-minor)'
};
const h = React.createElement;


/* The headline and its whole arithmetic. Rendered from compose.py's `score_axes`, which
   carries one row per axis: its weight out of 100, the share of its own denominator that
   came back clean, and what that denominator was. The bar behind each row is the share, so
   the shape of a candidate is readable before any of the numbers are. */
function ScoreBlock({ candidate: c }) {
  const axes = c.score_axes || [];
  const unscored = typeof c.score !== 'number' || !isFinite(c.score);
  const dq = !!c.disqualified;
  return h(React.Fragment, null,
    h("div", { style: { display: 'flex', alignItems: 'baseline', gap: 9, marginTop: 12 } },
      h("span", { style: { font: 'var(--fw-reg) 26px/1 var(--mono)', color: 'var(--text-body)' } },
        unscored ? '—' : c.score.toFixed(1)),
      h("span", { style: { ...EYE } }, unscored ? "not scored" : "score")),
    /* PHASE 17: the score says its own denominator and how much of it was judged, in mono, from
       the payload: `scoreOf` is the result's `score_model.of` and the two weights are the
       candidate's own. Nothing here types the 100. */
    !unscored && c.scoreOf != null && h("div", { "data-score-of": c.scoreOf,
      style: { font: 'var(--type-data-s)', color: 'var(--text-secondary)', marginTop: 4 } },
      `${c.score.toFixed(1)} of ${c.scoreOf}`,
      c.score_weight_evaluated != null && c.score_weight_unevaluated != null
        ? ` · ${c.score_weight_evaluated} of ${c.score_weight_evaluated + c.score_weight_unevaluated} weight judged`
        : null),
    /* WP-9.3: what the placed revision loop bought here, one line, from revision.js. Absent
       where the compose ran --no-revise; "nothing moved" rather than "was X" against the
       same X. `rank_before` is the server's order before revision, said in words. */
    c.revisedLine && h("div", {
      "data-revised": "",
      style: { ...EYE, color: 'var(--text-secondary)', marginTop: 4, textTransform: 'none', letterSpacing: 0 }
    }, c.revisedLine + (typeof c.rank_before === 'number' ? ` · the server ranked it ${c.rank_before} before revision` : '')),
    /* A disqualified candidate is still scored and its number can be the highest on the
       screen — every ordering puts it last, and this band is why. It is a rule, not a
       ranking: no score is a case for building a plan with a fatal finding in it. */
    dq && h("div", {
      style: { marginTop: 8, borderLeft: '2px solid var(--sev-fatal)', paddingLeft: 9 }
    },
      h("div", { style: { ...EYE, color: 'var(--sev-fatal)' } }, "disqualified"),
      h("p", { style: { font: 'var(--fw-reg) 12.5px/1.5 var(--body)', color: 'var(--text-secondary)',
                        margin: '3px 0 0' } },
        c.disqualified_because || "a fatal finding")),
    c.score_unscored_because && h("p", {
      style: { font: 'var(--fw-reg) 12.5px/1.5 var(--body)', color: 'var(--text-secondary)',
               margin: '6px 0 0' }
    }, c.score_unscored_because),
    axes.length > 0 && h("div", { style: { marginTop: 10 } },
      h("div", { style: EYE }, "how it scores"),
      axes.map(function (a) {
        /* Number() then isFinite: `share` is server data, and a NaN or a string would be
           interpolated straight into a CSS gradient below. A bad share reads as "not
           evaluated", which is the honest fallback and never a silent 0%. */
        const raw = Number(a.share);
        const pct = a.share == null || !isFinite(raw) ? null
          : Math.max(0, Math.min(100, Math.round(raw * 100)));
        const title = [a.what, a.denominator && ('over ' + a.denominator),
                       a.unjudged ? (a.unjudged + ' could not be judged and are not counted as passed') : null,
                       a.note].filter(Boolean).join(' — ');
        return h("div", {
          key: a.axis, title,
          style: { position: 'relative', display: 'grid',
                   gridTemplateColumns: '1fr auto auto', columnGap: 8, alignItems: 'baseline',
                   padding: '2px 4px', marginTop: 1,
                   /* the share, drawn behind the row rather than beside it — four columns
                      of these have no width to spare for a separate bar */
                   backgroundImage: pct == null ? 'none'
                     : `linear-gradient(to right, var(--surface-raised) ${pct}%, transparent ${pct}%)` }
        },
          h("span", { style: { font: 'var(--type-data-s)', color: 'var(--text-secondary)',
                               whiteSpace: 'nowrap', overflow: 'hidden',
                               textOverflow: 'ellipsis' } },
            a.axis,
            /* the mark, not the number — the count would wrap every row it appears on and
               make the eight axes unreadable as a block. It is said once, in full, below. */
            a.unjudged ? h("span", { style: { color: 'var(--text-secondary)' } }, " °") : null),
          h("span", { style: { font: 'var(--type-data-s)',
                               color: 'var(--text-secondary)' } },
            pct == null ? 'not evaluated' : pct + '%'),
          h("span", { style: { font: 'var(--type-data-s)', color: 'var(--text-secondary)' } },
            (a.points == null ? '—' : a.points) + '/' + a.weight));
      })),
    /* Unjudged is not passed, and it is never left to a tooltip: the axes carrying checks
       the corpus could not evaluate are named here in full, under the mark they carry. */
    axes.some(function (a) { return a.unjudged; }) && h("p", {
      style: { font: 'var(--fw-reg) 12px/1.5 var(--body)', color: 'var(--text-secondary)', margin: '7px 0 0' }
    }, "° ", axes.filter(function (a) { return a.unjudged; })
             .map(function (a) { return `${a.unjudged} ${a.axis}`; }).join(", "),
       " could not be evaluated on this plan. They are outside the fraction, not counted as passed."),
    c.score_weight_unevaluated > 0 && h("p", {
      style: { font: 'var(--fw-reg) 12px/1.5 var(--body)', color: 'var(--text-secondary)', margin: '6px 0 0' }
    /* The whole is the two halves the payload states, never a typed 100 (WP-14.31): a figure
       written into the page is true on the day it is typed and silently false after. */
    }, `Scored over ${c.score_weight_evaluated} of `
     + `${c.score_weight_evaluated + c.score_weight_unevaluated} points of evidence — `
     + `${c.score_weight_unevaluated} could not be evaluated on this plan, and are dropped `
     + `rather than passed.`));
}

/* HOW THE TYPE'S OWN FACTS STAND ON THIS CANDIDATE, first and in one of three forms (Phase 17,
   WP-17.4; `candidateStanding.standingOf` decides): refused, a brick band with its sentence;
   placed, a green disc; unjudged, the hatched ring and "may be refused". Every word a record's. */
function StandingBand({ c }) {
  if (c.standing === 'refused' && c.refused) {
    return h("div", { "data-candidate-standing": "refused",
      style: { margin: '10px -15px 0', padding: '7px 15px', borderLeft: '5px solid var(--refusal)',
        background: 'var(--sev-fatal-field)', font: 'var(--type-data-s)', color: 'var(--text-body)' } },
      h(MarkGlyph, { token: "--mark-refused", size: 11, style: { display: 'inline-block', verticalAlign: 'middle', marginRight: 7 } }),
      h(Term, { id: "judgment-refused" }),
      c.refused.facts && c.refused.facts.length ? ` · ${c.refused.facts.join(', ')}` : null);
  }
  const placed = c.standing === 'placed';
  return h("div", { "data-candidate-standing": placed ? "placed" : "unjudged",
    style: { display: 'flex', alignItems: 'center', gap: 7, marginTop: 10, font: 'var(--type-data-s)',
      color: 'var(--text-secondary)' } },
    h(MarkGlyph, { token: placed ? "--mark-passed" : "--mark-unjudged", size: 11 }),
    placed ? h(Term, { id: "candidate-placed" })
      : h(React.Fragment, null, h(Term, { id: "judgment-unjudged" }), " · ",
        h("i", { style: { font: 'italic var(--fw-reg) 13px/1.3 var(--body)' } }, h(Term, { id: "candidate-may-be-refused" }))));
}

function CandidateColumn({
  candidate,
  rank,
  selected,
  onSelect,
  children,
  style
}) {
  const c = candidate;
  const native = !!c.native;
  // WP-14.27: the served nativity, worded by its record -- see `nativityLine`
  const line = nativityLine(c);
  return /*#__PURE__*/React.createElement("section", {
    "data-candidate": c.parti,
    "data-candidate-n": c.n,
    "data-selected": selected ? "" : undefined,
    // Phase 17: a candidate is a vellum column on the dark instrument
    "data-ground": "vellum",
    className: "tdl-vellum",
    onClick: onSelect ? function () {
      onSelect(c);
    } : undefined,
    style: {
      flex: 1,
      minWidth: 0,
      // the picked column takes the instrument's one struck highlight, outside the paper
      border: selected ? '1px solid var(--gilt)' : '1px solid var(--surface-panel)',
      outline: selected ? '2px solid var(--gilt)' : 'none',
      background: 'var(--surface-panel)',
      padding: '14px 15px 16px',
      cursor: onSelect ? 'pointer' : 'default',
      transition: 'var(--t-hover)',
      ...style
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 9
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--text-secondary)'
    }
  }, rank), /*#__PURE__*/React.createElement("h3", {
    style: {
      font: 'var(--fw-reg) var(--fs-d4)/1.16 var(--display)',
      fontVariationSettings: '"opsz" 30',
      letterSpacing: 'var(--tr-display)',
      color: 'var(--text-body)',
      margin: 0,
      flex: 1
    }
  }, onSelect
    /* A COLUMN CAN BE SELECTED FROM A KEYBOARD (audit follow-up, 16 Oct 2026). The click handler
       sits on the <section>, which no key reaches, so the strip's "select a candidate" was an
       instruction a keyboard reader could not follow. The name is the control: a real button, in
       the tab order, announcing whether the column is the one picked. A click on it selects once
       (it does not also reach the section's own handler); a click anywhere else on the column
       selects as it always did. */
    ? /*#__PURE__*/React.createElement("button", {
      type: "button",
      "data-candidate-select": c.n,
      "aria-pressed": selected ? "true" : "false",
      onClick: function (e) {
        e.stopPropagation();
        onSelect(c);
      },
      style: {
        font: 'inherit',
        fontVariationSettings: 'inherit',
        letterSpacing: 'inherit',
        color: 'inherit',
        background: 'none',
        border: 0,
        padding: 0,
        margin: 0,
        textAlign: 'left',
        cursor: 'pointer'
      }
    }, c.parti_name) : c.parti_name)), /*#__PURE__*/React.createElement(StandingBand, { c: c }), /*#__PURE__*/React.createElement(ScoreBlock, {
    candidate: c
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 12,
      marginTop: 10,
      flexWrap: 'wrap'
    }
  }, ['fatal', 'serious', 'minor'].map(function (s) {
    const n = c.counts && c.counts[s] != null ? c.counts[s] : 0;
    return /*#__PURE__*/React.createElement("span", {
      key: s,
      style: {
        font: 'var(--type-data-s)',
        color: n === 0 ? 'var(--text-secondary)' : SEV[s]
      }
    }, s, " ", n);
  }),
  /* A refusal is a different measure from the three counts beside it and is not among them: a
     column can read `fatal 0` and be one the type's own facts turned down, which is the reading
     that sent a reader to a screen that would not draw their pick. Said on the counts' own line,
     in the refusal's ink, by the glossary's word for it. */
  c.refused && /*#__PURE__*/React.createElement("span", {
    "data-candidate-refused-mark": c.refused.kind,
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--refusal-text)'
    }
  }, /*#__PURE__*/React.createElement(Term, {
    id: "judgment-refused"
  }))), c.unjudged_fatal_n > 0 && /*#__PURE__*/React.createElement("div", {
    /* R13 (29 Sep 2026): the fatal faults the corpus could not judge on this candidate, in the
       unjudged mark and its glossary word, never in the fatal ink -- they break a tie against
       the candidate and do not disqualify it. The names are the payload's. */
    "data-unjudged-fatal": c.unjudged_fatal_n,
    style: {
      marginTop: 6
    }
  }, /*#__PURE__*/React.createElement(JudgmentMark, {
    state: "unjudged",
    label: "fatal " + c.unjudged_fatal_n,
    reason: (c.unjudged_fatal || []).map(function (x) {
      return x.name || x.fault;
    }).join('; ')
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 13,
      paddingTop: 12,
      borderTop: '1px solid var(--border-soft)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: EYE
  }, "why"), /*#__PURE__*/React.createElement("p", {
    "data-nativity": line.nativity || "",
    style: {
      font: 'var(--fw-reg) 13px/1.55 var(--body)',
      margin: '5px 0 0',
      color: native ? 'var(--sev-cleared)' : 'var(--text-secondary)'
    }
  }, line.term ? /*#__PURE__*/React.createElement("span", {
    style: {
      color: line.nativity === 'borrowed' ? 'var(--text-accent)' : 'inherit'
    }
  }, /*#__PURE__*/React.createElement(Term, {
    id: line.term
  })) : null, line.term && line.prose ? ' \u2014 ' : null, line.prose)), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 12
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      ...EYE,
      color: 'var(--text-accent)'
    }
  }, "trades away"), /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 13px/1.6 var(--body)',
      color: 'var(--text-body)',
      margin: '5px 0 0',
      textWrap: 'pretty'
    }
  }, c.trades_away)), /*#__PURE__*/React.createElement("dl", {
    style: {
      margin: '14px 0 0',
      display: 'grid',
      gridTemplateColumns: 'auto 1fr',
      columnGap: 12,
      rowGap: 4
    }
  }, [['area', c.area], ['footprint', c.footprint], ['bays', c.bays], ['massing', c.massing]].filter(function (r) {
    return r[1];
  }).map(function (r) {
    return /*#__PURE__*/React.createElement(React.Fragment, {
      key: r[0]
    }, /*#__PURE__*/React.createElement("dt", {
      style: {
        ...EYE
      }
    }, r[0]), /*#__PURE__*/React.createElement("dd", {
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--text-secondary)',
        margin: 0
      }
    }, r[1]));
  })), c.warnings && c.warnings.length > 0 && /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 13,
      paddingTop: 12,
      borderTop: '1px solid var(--border-soft)'
    }
  }, c.warnings.map(function (w, i) {
    return /*#__PURE__*/React.createElement("p", {
      key: i,
      style: {
        display: 'flex',
        gap: 8,
        font: 'var(--fw-reg) 12.5px/1.55 var(--body)',
        color: 'var(--text-secondary)',
        margin: i ? '7px 0 0' : 0
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--fw-semi) 12.5px/1.55 var(--mono)',
        color: 'var(--sev-serious)'
      }
    }, "!"), w);
  })), children);
}
export default CandidateColumn;
export { CandidateColumn };
