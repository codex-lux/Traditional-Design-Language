// The Transcription canvas's geometry, run for the census (WP-14.4): reads {case: {rooms, backdrop}}
// on stdin and writes each traced room's rect and the backdrop's box, as `traceCanvas.js` computes them.
import { backdropBox, roomRect } from '../../workbench/app/src/traceCanvas.js';

let raw = '';
process.stdin.setEncoding('utf8');
for await (const chunk of process.stdin) raw += chunk;
const out = {};
for (const [k, c] of Object.entries(JSON.parse(raw))) {
  out[k] = { rooms: c.rooms.map((r) => ({ key: r.key, rect: roomRect(r) })),
             backdrop: c.backdrop ? backdropBox(c.backdrop) : null };
}
process.stdout.write(JSON.stringify(out));
