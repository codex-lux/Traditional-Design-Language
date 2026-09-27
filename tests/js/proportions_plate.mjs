// The Proportions plate's arithmetic, run for the census (WP-14.1).
//
// Reads a JSON object {case_key: served_data} on stdin -- `data` exactly as
// workbench/server/corpus.py::proportions_with_members serves it -- and writes, per case, what
// workbench/app/src/proportions/plate.js computes: the frame, the datum it states, the pedestal
// die's naked, which members it says state no projection, and every band's extent. It imports the
// module the app imports; it re-derives nothing.
import { plateGeometry } from '../../workbench/app/src/proportions/plate.js';

let raw = '';
process.stdin.setEncoding('utf8');
for await (const chunk of process.stdin) raw += chunk;
const cases = JSON.parse(raw);
const out = {};
for (const [key, data] of Object.entries(cases)) {
  const P = plateGeometry(data);
  if (!P) { out[key] = null; continue; }
  out[key] = {
    H: P.H, maxX: P.maxX, dimX: P.dimX, fromAxis: P.fromAxis, undeclared: P.undeclared,
    nominal: P.nominal, r0: P.r0, dieNaked: P.dieNaked, f: P.f, datumWords: P.datumWords,
    noGeometry: P.noGeometry,
    viewBox: [-P.CAP, -3 * P.U, P.CAP + P.maxX + P.RIGHT, P.H + 6 * P.U],
    unrecorded: [...P.unrecorded].sort(),
    bands: P.bands.map((b) => ({ key: b.key, asm: b.asm, x0: b.x0, x1: b.x1, y0: b.y0, y1: b.y1,
      conf: b.conf || null, side: !!b.side, path: !!(P.segsFor[b.key] && P.segsFor[b.key].path) })),
  };
}
process.stdout.write(JSON.stringify(out));
