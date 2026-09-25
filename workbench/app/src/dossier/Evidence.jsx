/* Evidence — what the record rests on (WP-14.12, PRD §D.1 row 8).

   The exemplars and sources blocks of `surfaces/StyleRecord.jsx`, extracted, and the style's IMAGE
   RECORDS beside them, which no surface of the style showed: `/api/assets?style=` answers with
   every record filed against it, and almost all of them are WANTED -- a shot specified and not yet
   taken. Each carries its status in the record's own word, because an image record with no file
   is a stated state and must not read as a picture that failed to load. The dossier's evidence
   count is these three together; the image list states how many of its records it shows, from the
   payload, rather than implying it shows them all. */
import React from 'react';
import { api } from '../api/client.js';
import { Term } from '../components/Term.jsx';
import { Section, quiet, data } from './parts.jsx';

const ASSET_PAGE = 200;

export function Evidence({ rec, styleId }) {
  const [assets, setAssets] = React.useState(null);
  const [failed, setFailed] = React.useState(false);
  React.useEffect(() => {
    setAssets(null); setFailed(false);
    api.assets({ style: styleId, limit: ASSET_PAGE }).then(setAssets).catch(() => setFailed(true));
  }, [styleId]);
  const exemplars = rec.exemplars || [];
  const sources = rec.sources || [];
  const records = assets ? assets.assets || [] : [];

  return (
    <div data-dossier-section="evidence" style={{ display: 'flex', gap: 34, alignItems: 'flex-start', flexWrap: 'wrap' }}>
      <div style={{ flex: '1 1 420px', minWidth: 340, maxWidth: 680 }}>
        {exemplars.length > 0 && (
          <Section eyebrow={<><Term id="exemplar" /> · {exemplars.length}</>}>
            {exemplars.map((e, i) => (
              <p key={i} data-exemplar="" style={{ ...quiet, marginBottom: 8 }}>
                <span style={{ color: 'var(--ink)' }}>{e.name}</span>
                {e.location ? ` — ${e.location}` : ''}{e.year ? `, ${e.year}` : ''}
                {/* WP-11.1: standing is an editorial call and `why` says whose; the record's refs
                    are what a reader can check. An exemplar with no record says so rather than
                    looking like one that has. */}
                {e.standing ? (
                  <span style={{ marginLeft: 8, fontSize: 11, letterSpacing: '0.04em', textTransform: 'uppercase', color: 'var(--ink-3)', border: '1px solid var(--line)', borderRadius: 3, padding: '0 5px' }}>{e.standing}</span>
                ) : null}
                {e.note ? <span style={{ display: 'block', color: 'var(--ink-3)' }}>{e.note}</span> : null}
                {e.why ? <span style={{ display: 'block', color: 'var(--ink-3)', fontStyle: 'italic' }}>{e.why}</span> : null}
                {e.precedent_record && e.precedent_record.refs ? (
                  <span style={{ display: 'block', fontSize: 12 }}>
                    {e.precedent_record.refs.filter((r) => r.url).map((r, j) => (
                      <a key={j} href={r.url} target="_blank" rel="noreferrer" style={{ marginRight: 10, color: 'var(--accent, var(--ink-2))' }}>
                        {r.kind}{r.id ? ` ${r.id}` : ''}
                      </a>
                    ))}
                    {e.precedent_record.has_survey ? <span style={{ color: 'var(--ink-3)' }}>· HABS written data on the record</span> : null}
                  </span>
                ) : (
                  <span style={{ display: 'block', fontSize: 12, color: 'var(--ink-3)' }}>no precedent record yet — a name a reader can find and a checker cannot resolve</span>
                )}
              </p>
            ))}
          </Section>
        )}

        {sources.length > 0 && (
          <Section eyebrow={<><Term id="bibliographic-source" /> · {sources.length}</>}>
            {sources.map((src, i) => (
              <p key={i} data-source="" style={{ ...quiet, fontSize: 12.5, marginBottom: 5 }}>{src}</p>
            ))}
          </Section>
        )}
      </div>

      <div style={{ flex: '1 1 320px', minWidth: 280, maxWidth: 520 }}>
        {failed && <p style={quiet}>The image records could not be read.</p>}
        {assets && assets.matches > 0 && (
          <Section eyebrow={<>image records · {assets.returned} of {assets.matches}</>}
            data-assets-returned={assets.returned} data-assets-matches={assets.matches}>
            {records.map((a) => (
              <div key={a.id} data-asset={a.id} data-asset-status={a.status}
                style={{ padding: '6px 0', borderBottom: '1px solid var(--rule-soft)' }}>
                <p style={{ ...quiet, fontSize: 12.5 }}>{a.caption || a.id}</p>
                <span style={data}>{a.status}{a.kind ? ` · ${a.kind}` : ''}{a.role ? ` · ${a.role}` : ''}{a.file ? '' : ' · no file'}</span>
              </div>
            ))}
          </Section>
        )}
      </div>
    </div>
  );
}
