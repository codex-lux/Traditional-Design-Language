/* Proportions — the packs that reach this style, by how each arrives (WP-14.12, PRD §D.1 row 4).

   The Style Record printed the node's OWN bindings and nothing else, and the Kit printed the same
   list as strings. `/api/styles/{id}/packs` (§H.3) serves every pack that reaches the style in five
   provenances -- bound here, opted into, delivered by an ancestor, withheld by the opt-in gate,
   declined -- and this draws all five, each pack a link to its own page carrying this style
   (`#/proportions/<pack>?style=<id>`, `router.js`'s CONTEXT_KEYS), so the plate there is read
   for the style the reader came from. The five headings are the glossary's `pack-*` records.

   The nearest ancestor's delivered packs are shown and the farther ones FOLD, behind the reader's
   own `delivered` choice in `state/prefs.js` (PRD §I.10): closed until opened, and remembered
   once opened.

   The style's `proportional_system` prose comes first, extracted from the Style Record. Its
   hard-coded list of three "deliberately unbound" styles did not come with it: all three bind
   packs today, so the list had been hiding their real packs behind a note saying there were none. */
import React from 'react';
import { api } from '../api/client.js';
import { prefs } from '../state/prefs.js';
import { Term } from '../components/Term.jsx';
import { RecordLink } from '../components/RecordLink.jsx';
import { Section, prose, quiet, data } from './parts.jsx';
import { packGroups, splitDelivered, deliveredOpen } from './relations.js';

function PackRow({ p, styleId, from, why }) {
  return (
    <div data-pack={p.pack} style={{ display: 'flex', gap: 10, alignItems: 'baseline', padding: '3px 0', flexWrap: 'wrap' }}>
      <span style={{ flex: '1 1 260px', minWidth: 0 }}>
        <RecordLink cite={'pack:' + p.pack} ctx={{ style: styleId }}>{p.name || p.pack}</RecordLink>
      </span>
      <span style={{ ...data, width: 120, flex: 'none' }}>
        {p.kind ? <Term field="pack.kind" value={p.kind} /> : null}
      </span>
      <span style={{ ...data, width: 84, flex: 'none' }}>{p.role || ''}</span>
      {from && (
        <span style={{ ...data, flex: '1 1 100%' }}>
          from <RecordLink cite={'style:' + from}>{p.from_name || from}</RecordLink>
        </span>
      )}
      {why && <span style={{ ...quiet, fontSize: 12.5, flex: '1 1 100%' }}>{why}</span>}
    </div>
  );
}

function Group({ termId, rows, attr, children }) {
  if (!rows.length) return null;
  return (
    <Section eyebrow={<><Term id={termId} /> · {rows.length}</>} data-pack-group={attr}>
      {children}
    </Section>
  );
}

export function ProportionsSection({ rec, styleId }) {
  const [payload, setPayload] = React.useState(null);
  const [failed, setFailed] = React.useState(false);
  const fold = React.useSyncExternalStore(prefs.subscribe, () => prefs.fold('delivered'));
  React.useEffect(() => {
    setPayload(null); setFailed(false);
    api.stylePacks(styleId).then(setPayload).catch(() => setFailed(true));
  }, [styleId]);

  const ps = rec.proportional_system;
  const g = packGroups(payload);
  const { near, far } = splitDelivered(g.delivered);
  const open = deliveredOpen(fold);
  const farCount = far.reduce((n, grp) => n + grp.packs.length, 0);

  return (
    <div data-dossier-section="proportions" data-pack-total={payload ? g.total : undefined}>
      {ps && (
        <Section eyebrow="proportional system">
          <p style={prose}>{ps.governing_logic}</p>
          {(ps.typical_ratios || []).map((r, i) => (
            <p key={i} style={{ ...quiet, fontFamily: 'var(--mono)', fontSize: 12, marginBottom: 5 }}>{r}</p>
          ))}
        </Section>
      )}
      {failed && <p style={quiet}>The packs that reach this style could not be read.</p>}
      {!payload && !failed && <p style={data}>reading the packs…</p>}
      {payload && (
        <>
          <Group termId="pack-own" rows={g.own} attr="own">
            {g.own.map((p) => <PackRow key={p.pack} p={p} styleId={styleId} />)}
          </Group>
          <Group termId="pack-opted-in" rows={g.opted_in} attr="opted_in">
            {g.opted_in.map((p) => <PackRow key={p.pack} p={p} styleId={styleId} from={p.from} />)}
          </Group>
          {near && (
            <Section eyebrow={<><Term id="pack-delivered" /> · {near.packs.length + farCount}</>} data-pack-group="delivered">
              <p style={{ ...data, margin: '0 0 4px' }}>
                from <RecordLink cite={'style:' + near.from}>{near.from_name || near.from}</RecordLink> · ↑{near.distance}
              </p>
              {near.packs.map((p) => <PackRow key={p.pack} p={p} styleId={styleId} />)}
              {far.length > 0 && (
                <div style={{ marginTop: 10 }}>
                  <button type="button" aria-expanded={open} data-fold="delivered"
                    onClick={() => prefs.setFold('delivered', !open)}
                    style={{ font: 'var(--type-data-s)', color: 'var(--gilt-deep)', padding: '2px 0' }}>
                    {open ? '▾' : '▸'} farther ancestors · {far.length} · {farCount}
                  </button>
                  {open && far.map((grp) => (
                    <div key={grp.from} style={{ marginTop: 8 }}>
                      <p style={{ ...data, margin: '0 0 4px' }}>
                        from <RecordLink cite={'style:' + grp.from}>{grp.from_name || grp.from}</RecordLink> · ↑{grp.distance}
                      </p>
                      {grp.packs.map((p) => <PackRow key={p.pack} p={p} styleId={styleId} />)}
                    </div>
                  ))}
                </div>
              )}
            </Section>
          )}
          <Group termId="pack-withheld" rows={g.withheld} attr="withheld">
            {g.withheld.map((p) => <PackRow key={p.pack} p={p} styleId={styleId} from={p.from} why={p.why} />)}
          </Group>
          <Group termId="pack-declined" rows={g.declined} attr="declined">
            {g.declined.map((p) => <PackRow key={p.pack} p={p} styleId={styleId} from={p.from} why={p.reason} />)}
          </Group>
        </>
      )}
    </div>
  );
}
