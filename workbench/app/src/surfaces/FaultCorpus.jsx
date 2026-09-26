/* Surface ⑨ — the Fault Corpus, live. Element-first: faults hang off slots, not styles.
   The list filters on the corpus's own axes; the reading pane fetches the full record
   (find_faults cards are summaries) and style exceptions render above the general rule. */
import React from 'react';
import { api } from '../api/client.js';
import { FaultCard } from '../components/FaultCard.jsx';
import { UnsourcedImageRecord } from '../components/UnsourcedImageRecord.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { FilterStrip, Chip, ChipGroup, FilterGroup } from '../Chrome.jsx';
import { FilterInput } from '../components/FilterInput.jsx';
import { StylePicker } from '../components/StylePicker.jsx';
import { useSurfaceFilters } from '../filters/useFilters.js';
import { matches } from '../search/match.js';
import { PullPane } from '../components/PullPane.jsx';
import { Term } from '../components/Term.jsx';
import { NoRecordChosen } from '../components/NoRecordChosen.jsx';
import { faultGroups, groupRows, styleFaultIds } from '../faults/groups.js';

/* The limit the style's fault list and the dossier's partition are both taken at
   (`corpus.dossier_faults` asks `core.find_faults` for 300), so the two answer the same question. */
const STYLE_LIST_LIMIT = 300;

const SEV_C = { fatal: 'var(--sev-fatal)', serious: 'var(--sev-serious)', minor: 'var(--sev-minor)' };
const SPEC = { sev: {}, driver: {}, q: { type: 'text' }, style: {} };

export function FaultCorpus({ onCite, selection, setSelection }) {
  const [all, setAll] = React.useState([]);
  const [id, setId] = React.useState(selection?.fault || null);
  const [fault, setFault] = React.useState(null);
  const [assets, setAssets] = React.useState([]);

  const filters = useSurfaceFilters(SPEC);
  const { sev, driver, q } = filters.values;
  const styleInView = filters.values.style || '';

  React.useEffect(() => {
    api.faults({ limit: 250 }).then((r) => setAll(r.faults || []));
  }, []);

  React.useEffect(() => {
/* The URL owns this, so an ABSENT selection must reset rather than leave the last one showing.
   Guarding the sync with `if (selection?.x)` meant pressing Back to a bare #/faults left the
   panel displaying the record you had just left — the address bar and the screen disagreeing,
   which is the one thing the router exists to prevent. Found by an adversarial audit.
   AND ABSENT MEANS NONE (WP-14.27). It reset to a typed `porch-too-shallow-to-inhabit`, so a bare
   #/faults read one fault's card under an address naming no fault. A bare address lists the
   corpus and says no record is chosen, in its glossary record's words. */
    setId(selection?.fault || null);
  }, [selection?.fault]);

  /* THE STYLE'S FAULTS IN THE DOSSIER'S THREE GROUPS (WP-14.27, PRD §C.12). The partition is
     `corpus.dossier_faults`, served on the dossier route; the list it partitions is the style's
     own `find_faults`. Both at one limit, and `faults/groups.js` holds the one to the other. */
  const [grouping, setGrouping] = React.useState(null);
  React.useEffect(() => {
    if (!styleInView) { setGrouping(null); return undefined; }
    let current = true;
    setGrouping(null);
    Promise.all([api.styleDossier(styleInView), api.faults({ style: styleInView, limit: STYLE_LIST_LIMIT })])
      .then(([d, r]) => {
        if (current) setGrouping(faultGroups(d && d.faults, (r.faults || []).map((f) => f.id)));
      })
      .catch(() => { if (current) setGrouping({ state: 'unjudged', reason: 'the style could not be read' }); });
    return () => { current = false; };
  }, [styleInView]);

  /* ONLY THE ANSWER TO THE LATEST QUESTION IS SHOWN (WP-14.11). A move to a new address changes
     the fault and the style in one navigation, and this effect runs once for the style (with the
     OLD fault still in `id`) and again for the fault -- two requests in flight, and whichever
     resolved LAST was drawn. Forced by delaying the stale one, the card read "The Newel That
     Cannot Be Leaned On" under an address naming `surround-that-lies-about-the-wall`, on this
     tree and on a `git archive` of the base commit alike; unforced it won 2 runs in 5 here (the
     walk's among them) and 0 in 3 on the base. A card of another fault under this address would also carry
     another fault's licence verdict, which is the thing the card may not get wrong. A superseded
     request is discarded, its assets with it. */
  React.useEffect(() => {
    // No fault named: nothing is fetched, and the card of the fault the reader just left goes.
    if (!id) { setFault(null); setAssets([]); return undefined; }
    let current = true;
    api.fault(id, styleInView || undefined)
      .then((f) => current && setFault({
        ...f,
        fix: f.fixes,   // the card reads `fix`; the record says `fixes`
        // the card reads exception.statement + a printable bounds; the record says
        // why + a {measurement: [lo, hi]} dict
        exceptions: (f.exceptions || []).map((e) => ({
          ...e,
          statement: e.why,
          bounds: e.bounds && typeof e.bounds === 'object'
            ? Object.entries(e.bounds).map(([k, v]) =>
                `${k} ${Array.isArray(v) ? v.join('–') : v}`).join(' · ')
            : e.bounds,
        })),
        // the card typesets `test` as prose beside the statement; the record's is a
        // structured rule — render it as the sentence it encodes, note included
        /* `between` carries BOTH edges — 40 of 210 faults, measured 25 Sep 2026 — and only
           `threshold` was printed, so a two-sided band rendered as "between 7.0 ratio"
           and a reader could not tell whether 12.0 passed. */
        test: f.test
          ? `${f.test.expression} ${f.test.direction} ${f.test.threshold}`
            + (f.test.upper != null ? ` to ${f.test.upper}` : '')
            + ` ${f.test.units}`
            + ` · measurable from a ${f.test.measurable_from}` +
            (f.test.note ? ` — ${f.test.note}` : '')
          : null,
      }))
      .catch(() => { if (current) setFault(null); });
    api.assets({ fault: id, limit: 4 })
      .then((r) => { if (current) setAssets(r.assets || []); })
      .catch(() => { if (current) setAssets([]); });
    return () => { current = false; };
  }, [id, styleInView]);

  const sevCounts = all.reduce((a, f) => { a[f.severity] = (a[f.severity] || 0) + 1; return a; }, {});
  const driverCounts = all.reduce((a, f) => {
    if (f.driver) a[f.driver] = (a[f.driver] || 0) + 1;
    return a;
  }, {});
  // With a style in view the list is that style's faults, which is what `style` narrows to.
  const inStyle = styleFaultIds(grouping);
  const list = all.filter((f) =>
    (!inStyle || inStyle.has(f.id))
    && (!sev || f.severity === sev)
    && (!driver || f.driver === driver)
    && matches(f, q, ['name', 'id', 'severity', 'driver', 'frequency', 'aka',
                      (r) => (r.slots || []).join(' ')]));

  const drivers = Object.entries(driverCounts).sort((a, b) => b[1] - a[1]);
  const grouped = groupRows(list, grouping);

  const row = (f) => {
    const on = f.id === id;
    return (
      /* Selecting writes the URL, so a fault you are reading is a link you can
         send — and the citation the rail would use for it is the same string. */
      <button key={f.id} type="button" data-fault-row={f.id} aria-current={on ? 'true' : undefined}
        onClick={() => { setId(f.id); setSelection && setSelection({ fault: f.id }); }}
        style={{ display: 'block', width: '100%', textAlign: 'left', padding: '9px 12px 11px',
          borderBottom: '1px solid var(--rule-soft)',
          borderLeft: '2px solid ' + (on ? 'var(--gilt-deep)' : 'transparent'),
          background: on ? 'var(--paper-deep)' : 'transparent', transition: 'var(--t-hover)' }}>
        <div style={{ font: 'var(--fw-reg) 15px/1.25 var(--display)', fontVariationSettings: '"opsz" 24',
          color: on ? 'var(--ink)' : 'var(--ink-2)' }}>{f.name}</div>
        <div style={{ display: 'flex', gap: 10, marginTop: 5 }}>
          <span style={{ font: 'var(--type-data-s)', color: SEV_C[f.severity] }}>{f.severity}</span>
          <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>{f.frequency}</span>
          <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>{f.slots && f.slots[0]}</span>
        </div>
      </button>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip filters={filters} right={
        <span style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Eyebrow as="span" style={{ whiteSpace: 'nowrap' }}>exceptions</Eyebrow>
          <StylePicker value={styleInView} onChange={(v) => filters.set('style', v)}
            label="Read the corpus with one style's exceptions in view" allowNone width={160}
            noneLabel="no style" />
        </span>
      }>
        {/* The corpus's own count, from the list the API answered — it said "209" against a
            corpus of 210 (WP-14.13). While the list is still loading it names no figure. */}
        <FilterInput value={q} onChange={(v) => filters.set('q', v)} count={list.length}
          label={all.length ? `Filter the ${all.length} faults by name, slot, severity or driver`
            : 'Filter the faults by name, slot, severity or driver'}
          placeholder={all.length ? `filter ${all.length} faults` : 'filter the faults'} width={180} />
        <span style={{ width: 1, height: 18, background: 'var(--rule)' }} />
        <ChipGroup label="severity">
          <Eyebrow as="span">severity</Eyebrow>
          {['fatal', 'serious', 'minor'].map((s) => (
            <Chip key={s} radio on={sev === s} tone={SEV_C[s]}
              onClick={() => filters.toggle('sev', s)}>{s} {sevCounts[s] || 0}</Chip>
          ))}
        </ChipGroup>
        {/* The nine cause drivers are a long tail nobody steers by daily — they fold, and
            the fold says which one is on so nothing hides behind it. */}
        <FilterGroup label="cause driver" active={driver ? 1 : 0} summary={driver || ''}>
          <ChipGroup label="cause driver">
            {drivers.map(([d, n]) => (
              <Chip key={d} radio on={driver === d}
                onClick={() => filters.toggle('driver', d)}>{d} {n}</Chip>
            ))}
          </ChipGroup>
        </FilterGroup>
      </FilterStrip>

      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        <PullPane pane="faults" side="left"
          style={{ borderRight: '1px solid var(--rule)', overflow: 'auto' }}>
          <div style={{ padding: '11px 12px', borderBottom: '1px solid var(--rule)' }}>
            <Eyebrow>
              {all.length} solecisms · {list.length} shown here
              {list.length !== all.length && filters.activeCount > 0 ? ' · filtered' : ''}
            </Eyebrow>
            <p style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-2)', margin: '7px 0 0' }}>
              {/* `all` is the FAULT list, and it is capped at the query's own limit — the
                   denominator was labelled "cause drivers" and would silently truncate. */}
              Of the {all.length} solecisms listed, exactly {driverCounts.ignorance || 0} name{driverCounts.ignorance === 1 ? 's' : ''}{' '}
              <span style={{ color: 'var(--ink-2)' }}>ignorance</span>.
              This is a system explaining an economy, not scolding a builder.
            </p>
          </div>
          {list.length === 0 && all.length > 0 && (
            <p style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-2)',
              margin: 0, padding: '14px 12px' }}>
              No fault matches. The corpus holds {all.length}; the filters above are hiding
              all of them.
            </p>
          )}
          {grouping && grouping.state === 'unjudged' && (
            <p data-fault-groups-unjudged="" style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)',
              margin: 0, padding: '10px 12px', borderBottom: '1px solid var(--rule-soft)' }}>
              {grouping.reason}
            </p>
          )}
          {grouped
            ? grouped.map((g) => (
                <div key={g.id} data-fault-group={g.id} data-fault-group-count={g.rows.length}>
                  <div style={{ padding: '10px 12px 6px', borderBottom: '1px solid var(--rule-soft)',
                    background: 'var(--paper-deep)' }}>
                    <Eyebrow><Term id={g.term} /> · {g.rows.length}</Eyebrow>
                  </div>
                  {g.rows.map(row)}
                </div>
              ))
            : list.map(row)}
        </PullPane>

        <div style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '18px 22px 34px' }}>
          {!id && <NoRecordChosen surface="faults" />}
          {id && fault && (
            <div style={{ display: 'flex', gap: 22, alignItems: 'flex-start', flexWrap: 'wrap' }}>
              <div style={{ flex: '1 1 520px', minWidth: 460, maxWidth: 760 }}>
                <FaultCard fault={fault} styleInView={styleInView || undefined}
                  onSlot={(s) => onCite && onCite('slot:' + s)} />
              </div>
              <div style={{ flex: '0 1 268px', minWidth: 240 }}>
                {/* The eyebrow and the empty-state used to be written as facts about the whole
                    corpus, hardcoded: "specified, not yet sourced" and "the corpus holds 322
                    specified records and none has a photograph". Both were shown to the reader
                    and both went stale the day anything was sourced -- 1,850 records and 73
                    files later they were still saying it. Neither states a corpus-wide number
                    now; the eyebrow describes THESE records and the empty state describes this
                    fault. */}
                <Eyebrow style={{ marginBottom: 9 }}>
                  {assets.some((a) => a.file) ? 'evidence' : 'evidence · specified, not yet sourced'}
                </Eyebrow>
                {assets.length === 0 && (
                  <p style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-2)', margin: 0 }}>
                    No image records are filed against this fault yet — the record is the
                    object until one is.
                  </p>
                )}
                {assets.map((a, i) => (
                  <UnsourcedImageRecord key={a.id || i} style={i ? { marginTop: 14 } : undefined}
                    record={{
                      id: a.id,
                      subject: a.caption || a.subject,
                      shot_spec: typeof a.shot_spec === 'string' ? a.shot_spec : JSON.stringify(a.shot_spec),
                      alt: a.alt_text || a.alt,
                      // file, rights and generated_from were dropped here, so an image could
                      // not have been shown even once one existed. `provenance_required` used
                      // to fall back to the literal 'photographer credit + permission' -- a
                      // licensing claim that came from nowhere in the data.
                      file: a.file,
                      status: a.status,
                      rights: a.rights,
                      generated_from: a.generated_from,
                      provenance_required: typeof a.provenance === 'string' ? a.provenance
                        : a.provenance_required || undefined,
                    }} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
