/* Where the region names in `geography.regions` are, on the earth.

   THIS IS INTERFACE FURNITURE, NOT CORPUS DATA, AND THE DISTINCTION IS LOAD-BEARING.
   The corpus holds no coordinates. It says "Tidewater Virginia" and "the James, York,
   Rappahannock and Potomac river plantations", which is how a building tradition is
   actually located — by the country it was built in, not by a decimal pair. These numbers
   exist so that prose can be drawn on a map. Not one of them may migrate into styles/*.json
   as a measured fact: that is exactly the laundering CLAUDE.md forbids, and it would turn
   a drawing aid into a claim the sources never made.

   Every point is a rough centre of the named region, taken from common geographic
   knowledge. They are accurate to about the size of the thing named and no better, which
   is why `precision` is recorded beside each one and drawn differently:

     locality — a town, a valley, a stretch of coast. The mark is a point because the
                record named something you could walk across.
     region   — a state, a province, a named country-side. The mark is a point, but the
                thing is a hundred miles wide.
     country  — a nation, or "United States nationwide". The record names no hearth at
                all; the mark is drawn hollow and hatched so the map never implies one.

   A style is placed by the FINEST region it names, not the first: a record reading
   ["United States", "New England"] is placed in New England, because that is the better
   information the record already carried. A style naming nothing this file knows is not
   placed, not guessed — see UNLOCATED handling in MapView. */

export const REGIONS_ONLY = 'regions-only';

/* "This style has no hearth", said by the record itself.

   A family or a tradition is an abstraction over styles and has no birthplace, and a few
   styles say as much in prose: `neo-eclectic` reads "No design hearth; the style was generated
   inside production builders' plan departments", `craftsman-bungalow` "Streetcar suburbs
   nationwide". Those are records telling the truth, and a country-wide mark for them is
   correct rather than a failure of the drawing.

   ONE COPY, because there were three and two already disagreed. `check_gazetteer.py` matched
   "no single hearth" and MapView did not, so `american-farmhouse-vernacular` was classified
   differently by the check and the map it checks — inert only because that style happens to
   place at region precision. Found by an adversarial audit. */
export const statesNoHearth = (hearth) =>
  /no (single |design )?hearth|nationwide/i.test(hearth || '');

const PRECISION = { locality: 0, region: 1, country: 2 };

/* name → [lat, lon, precision] */
export const GAZETTEER = {
  // ── Britain and Ireland ────────────────────────────────────────────────────
  'England': [52.4, -1.5, 'country'],
  'Scotland': [56.8, -4.2, 'country'],
  'Wales': [52.3, -3.7, 'country'],
  'Ireland': [53.2, -8.0, 'country'],
  'Northern Ireland': [54.7, -6.6, 'region'],
  'Ulster': [54.7, -6.9, 'region'],
  'London': [51.5, -0.13, 'locality'],
  'the Cotswolds': [51.8, -2.0, 'region'],
  'Cotswolds': [51.8, -2.0, 'region'],
  'East Anglia': [52.4, 1.0, 'region'],
  'Kent': [51.2, 0.7, 'region'],
  'Sussex': [50.9, -0.3, 'region'],
  'Yorkshire': [54.0, -1.3, 'region'],
  'the Home Counties': [51.6, -0.5, 'region'],
  'Bath': [51.38, -2.36, 'locality'],
  'Edinburgh': [55.95, -3.19, 'locality'],
  'Brighton': [50.82, -0.14, 'locality'],
  'Cheltenham': [51.9, -2.08, 'locality'],
  'Devon': [50.7, -3.7, 'region'],
  'Cornwall': [50.4, -4.8, 'region'],

  // ── Continental Europe ─────────────────────────────────────────────────────
  'France': [46.6, 2.4, 'country'],
  'Paris': [48.86, 2.35, 'locality'],
  'Ile-de-France': [48.8, 2.4, 'region'],
  'Île-de-France': [48.8, 2.4, 'region'],
  'Normandy': [49.1, 0.2, 'region'],
  'Brittany': [48.2, -2.9, 'region'],
  'Loire Valley': [47.4, 0.7, 'region'],
  'Provence': [43.9, 5.8, 'region'],
  'Italy': [42.8, 12.6, 'country'],
  'Tuscany': [43.4, 11.2, 'region'],
  'Rome and Lazio': [41.9, 12.6, 'region'],
  'Rome': [41.9, 12.5, 'locality'],
  'Veneto': [45.5, 11.9, 'region'],
  'Vicenza': [45.55, 11.55, 'locality'],
  'Venice': [45.44, 12.34, 'locality'],
  'Florence': [43.77, 11.26, 'locality'],
  'Lombardy': [45.6, 9.7, 'region'],
  'Spain': [40.2, -3.7, 'country'],
  'Andalusia': [37.5, -4.8, 'region'],
  'Al-Andalus': [37.4, -4.5, 'region'],
  'Castile': [41.3, -4.5, 'region'],
  'Catalonia': [41.8, 1.6, 'region'],
  'Seville': [37.39, -5.98, 'locality'],
  'Granada': [37.18, -3.6, 'locality'],
  'Portugal': [39.5, -8.2, 'country'],
  'Netherlands': [52.2, 5.4, 'country'],
  'Amsterdam': [52.37, 4.9, 'locality'],
  'Belgium': [50.6, 4.6, 'country'],
  'Flanders': [51.0, 3.7, 'region'],
  'Germany': [51.1, 10.4, 'country'],
  'Bavaria': [48.8, 11.4, 'region'],
  'the Rhineland': [50.5, 7.2, 'region'],
  'Rhineland': [50.5, 7.2, 'region'],
  'Switzerland': [46.8, 8.2, 'country'],
  'Austria': [47.6, 14.1, 'country'],
  'Scandinavia': [60.5, 14.0, 'region'],
  'Norway': [61.0, 8.5, 'country'],
  'Sweden': [61.0, 15.0, 'country'],
  'Denmark': [56.1, 9.5, 'country'],
  'Finland': [63.5, 26.0, 'country'],
  'Greece': [39.0, 22.0, 'country'],
  'Athens': [37.98, 23.73, 'locality'],
  'Mediterranean basin': [38.5, 12.0, 'region'],
  'North Africa': [31.5, 6.0, 'region'],
  'Morocco': [31.8, -6.5, 'country'],
  'Turkey': [39.0, 35.0, 'country'],
  'Russia': [56.0, 38.0, 'country'],
  'Poland': [52.0, 19.4, 'country'],
  'Bohemia': [49.8, 14.5, 'region'],

  // ── The United States, coarse to fine ──────────────────────────────────────
  'United States': [39.5, -98.0, 'country'],
  'United States nationwide': [39.5, -98.0, 'country'],
  'United States Northeast': [42.5, -73.5, 'region'],
  'New England': [43.5, -71.5, 'region'],
  'Coastal New England': [42.6, -70.6, 'region'],
  'Mid-Atlantic': [39.9, -75.6, 'region'],
  'the South': [33.5, -85.0, 'region'],
  'Deep South': [32.4, -87.0, 'region'],
  'Upper South': [36.3, -80.0, 'region'],
  'Upland South': [36.0, -84.0, 'region'],
  'Lowcountry South': [32.6, -80.3, 'region'],
  'Gulf South': [30.3, -89.5, 'region'],
  'Gulf Coast': [30.2, -88.5, 'region'],
  'Midwest': [41.6, -89.0, 'region'],
  'Great Lakes': [44.0, -85.0, 'region'],
  'Ohio Valley': [39.2, -84.5, 'region'],
  'Appalachia': [37.5, -81.5, 'region'],
  'Ozarks': [36.6, -92.8, 'region'],
  'Great Plains': [41.0, -100.0, 'region'],
  'Pacific Northwest': [46.5, -122.5, 'region'],
  'Southwest': [34.0, -108.0, 'region'],
  'Chesapeake': [38.6, -76.3, 'region'],
  'Tidewater Virginia': [37.3, -76.7, 'region'],
  'Spanish Americas': [19.0, -99.0, 'region'],

  'Massachusetts': [42.3, -71.8, 'region'],
  'eastern Massachusetts': [42.4, -71.1, 'region'],
  'Cape Cod and the Islands': [41.68, -70.2, 'locality'],
  'Rhode Island': [41.7, -71.5, 'region'],
  'Connecticut': [41.6, -72.7, 'region'],
  'New Hampshire': [43.7, -71.6, 'region'],
  'Vermont': [44.0, -72.7, 'region'],
  'Maine': [45.3, -69.2, 'region'],
  'New York': [42.9, -75.5, 'region'],
  'New York City': [40.71, -74.0, 'locality'],
  'Upstate New York': [42.9, -75.5, 'region'],
  'Hudson Valley': [41.7, -73.9, 'region'],
  'Hudson Valley, New York': [41.7, -73.9, 'region'],
  'Ulster County, New York': [41.9, -74.2, 'locality'],
  'New Jersey': [40.2, -74.6, 'region'],
  'Bergen County, New Jersey': [40.96, -74.07, 'locality'],
  'Pennsylvania': [40.9, -77.8, 'region'],
  'southeastern Pennsylvania': [40.2, -75.8, 'region'],
  'Philadelphia': [39.95, -75.17, 'locality'],
  'Lancaster, Berks, Lebanon and Montgomery counties, Pennsylvania': [40.35, -76.0, 'locality'],
  'Delaware': [39.0, -75.5, 'region'],
  'Maryland': [39.0, -76.8, 'region'],
  'Baltimore': [39.29, -76.61, 'locality'],
  'Virginia': [37.6, -78.7, 'region'],
  'North Carolina': [35.6, -79.4, 'region'],
  'South Carolina': [33.9, -80.9, 'region'],
  'South Carolina Lowcountry': [32.9, -80.2, 'region'],
  'Charleston': [32.78, -79.93, 'locality'],
  'Georgia': [32.7, -83.4, 'region'],
  'Savannah': [32.08, -81.09, 'locality'],
  'Florida': [28.4, -81.8, 'region'],
  'Alabama': [32.8, -86.8, 'region'],
  'Mississippi': [32.7, -89.7, 'region'],
  'Louisiana': [31.0, -92.0, 'region'],
  'New Orleans (Vieux Carré, Faubourg Marigny, Tremé)': [29.96, -90.06, 'locality'],
  'New Orleans': [29.95, -90.07, 'locality'],
  'the Mississippi River parishes above and below New Orleans': [30.05, -90.7, 'locality'],
  'Tennessee': [35.8, -86.4, 'region'],
  'Kentucky': [37.5, -85.3, 'region'],
  'Texas': [31.3, -99.3, 'region'],
  'Ohio': [40.3, -82.8, 'region'],
  'Indiana': [39.9, -86.3, 'region'],
  'Illinois': [40.0, -89.2, 'region'],
  'Chicago': [41.88, -87.63, 'locality'],
  'Michigan': [44.3, -85.4, 'region'],
  'Wisconsin': [44.5, -89.5, 'region'],
  'Minnesota': [46.3, -94.3, 'region'],
  'Iowa': [42.0, -93.5, 'region'],
  'Missouri': [38.4, -92.5, 'region'],
  'Kansas': [38.5, -98.4, 'region'],
  'Nebraska': [41.5, -99.8, 'region'],
  'Colorado': [39.0, -105.5, 'region'],
  'New Mexico': [34.4, -106.1, 'region'],
  'upper Rio Grande valley, New Mexico': [36.0, -105.9, 'locality'],
  'Santa Fe': [35.69, -105.94, 'locality'],
  'Arizona': [34.3, -111.7, 'region'],
  'Utah': [39.3, -111.7, 'region'],
  'California': [37.2, -119.7, 'region'],
  'Northern California': [39.3, -121.5, 'region'],
  'Southern California': [34.0, -117.6, 'region'],
  'coastal California from San Diego to Sonoma': [35.4, -120.6, 'region'],
  'Monterey and the Salinas Valley, California': [36.6, -121.6, 'locality'],
  'Los Angeles': [34.05, -118.24, 'locality'],
  'San Francisco': [37.77, -122.42, 'locality'],
  'Pasadena': [34.15, -118.14, 'locality'],
  'Oregon': [44.0, -120.6, 'region'],
  // AMBIGUOUS IN PROSE, so it is flagged regions-only: a style whose `regions` list says
  // "Washington" means the state, but a hearth sentence saying "standardized in Washington by
  // the Federal Housing Administration" means D.C. The 45 degree anchor cannot separate them
  // because both readings are inside the United States — that rule was built for the Boston in
  // Lincolnshire, and is blind to ambiguity within one country. Before this flag,
  // `minimal-traditional` was drawn 3,700 km from where its record puts it.
  'Washington': [47.4, -120.5, 'region', REGIONS_ONLY],
  'Hawaii': [20.8, -156.3, 'region'],

  // ── Canada, and the wider Atlantic ─────────────────────────────────────────
  'Canada': [56.0, -96.0, 'country'],
  'Ontario': [49.3, -84.5, 'region'],
  'Quebec': [52.0, -71.5, 'region'],
  'Maritime Canada': [45.8, -63.5, 'region'],
  'Nova Scotia': [45.0, -63.0, 'region'],
  'New Brunswick': [46.5, -66.2, 'region'],
  'Newfoundland': [48.7, -56.0, 'region'],
  'British Columbia': [53.7, -124.0, 'region'],
  'Mexico': [23.6, -102.5, 'country'],
  'Mexico City': [19.43, -99.13, 'locality'],
  'the Caribbean': [17.5, -72.0, 'region'],
  'Caribbean': [17.5, -72.0, 'region'],
  'Cuba': [21.8, -79.5, 'country'],
  'Brazil': [-10.0, -52.0, 'country'],
  'South Africa': [-29.5, 24.5, 'country'],
  'Cape Town': [-33.92, 18.42, 'locality'],
  'Australia': [-25.5, 134.0, 'country'],
  'New Zealand': [-41.5, 172.5, 'country'],
  'India': [22.0, 79.0, 'country'],

  /* ── Places the HEARTH sentences name (OQ 65) ──────────────────────────────
     Everything below was added by reading the 132 hearth sentences and listing
     what they name that this file could not place. They are here to be matched
     in prose, not in `regions`, which is why several are towns.

     Ambiguity is real and handled by the anchor check in placeByHearth rather
     than by leaving names out: there is a Boston in Lincolnshire and a Salem in
     Oregon, and an English style anchored to England rejects the Massachusetts
     reading at 70° before it is ever drawn. */

  // New England, which most of the American hearths point at
  'Boston': [42.36, -71.06, 'locality'],
  'Salem': [42.52, -70.90, 'locality'],
  'Marblehead': [42.50, -70.86, 'locality'],
  'Ipswich': [42.68, -70.84, 'locality'],
  'Newport': [41.49, -71.31, 'locality'],
  'Portsmouth': [43.07, -70.76, 'locality'],
  'Essex County': [42.64, -70.94, 'locality'],
  'Massachusetts Bay': [42.4, -70.9, 'region'],
  'Connecticut River': [41.8, -72.6, 'region'],
  'Connecticut Valley': [41.9, -72.6, 'region'],

  // the mid-Atlantic and the Hudson
  'Delaware Valley': [40.0, -75.2, 'region'],
  'Fishkill': [41.54, -73.90, 'locality'],
  'Albany': [42.65, -73.76, 'locality'],
  'Washington, D.C.': [38.90, -77.04, 'locality'],
  'Erie Canal': [43.1, -76.1, 'region'],
  'Western Reserve': [41.4, -81.3, 'region'],

  // the South and the interior
  'Albemarle County': [38.02, -78.53, 'locality'],
  'Great Valley of Virginia': [38.4, -78.9, 'region'],
  'Blue Ridge': [36.6, -81.5, 'region'],
  'Virginia Piedmont': [37.9, -78.3, 'region'],
  'Carolina Piedmont': [35.5, -80.5, 'region'],
  'Lower Mississippi Valley': [31.5, -91.4, 'region'],
  'Black Belt': [32.4, -87.2, 'region'],
  'East Tennessee': [35.9, -84.0, 'region'],
  'Bluegrass': [38.0, -84.5, 'region'],
  'Tennessee Valley': [34.8, -87.0, 'region'],
  'St. Augustine': [29.90, -81.31, 'locality'],
  'Rio Grande': [35.5, -106.0, 'region'],

  // the West
  'Santa Barbara': [34.42, -119.70, 'locality'],
  'Montecito': [34.44, -119.63, 'locality'],
  'Oak Park': [41.89, -87.79, 'locality'],
  'San Diego': [32.72, -117.16, 'locality'],
  'Sonoma': [38.29, -122.46, 'locality'],
  'Seaside': [30.38, -86.15, 'locality'],

  // England, beyond the counties already listed
  'Derbyshire': [53.1, -1.6, 'region'],
  'Nottinghamshire': [53.1, -1.0, 'region'],
  'Gloucestershire': [51.8, -2.2, 'region'],
  'Oxfordshire': [51.8, -1.3, 'region'],
  'Wiltshire': [51.3, -1.9, 'region'],
  'Norfolk': [52.6, 1.0, 'region'],
  'the Thames valley': [51.5, -0.9, 'region'],
  'Thames valley': [51.5, -0.9, 'region'],
  'the Midlands': [52.5, -1.5, 'region'],
  'Twickenham': [51.45, -0.33, 'locality'],
  'Ramsgate': [51.34, 1.42, 'locality'],
  'Westminster': [51.50, -0.13, 'locality'],
  'Chiswick': [51.49, -0.26, 'locality'],

  // Scotland
  'Aberdeenshire': [57.2, -2.5, 'region'],
  'Aberdeen': [57.15, -2.09, 'locality'],
  'Abbotsford': [55.60, -2.78, 'locality'],
  'the Borders': [55.5, -2.8, 'region'],

  // France
  'the Rhone valley': [44.9, 4.8, 'region'],
  'Rhone valley': [44.9, 4.8, 'region'],
  'Amboise': [47.41, 0.98, 'locality'],
  'Blois': [47.59, 1.33, 'locality'],
  "Pays d'Auge": [49.1, 0.1, 'region'],
  'Calvados': [49.1, -0.4, 'region'],
  'the Perche': [48.5, 0.7, 'region'],
  'Burgundy': [47.1, 4.5, 'region'],

  // Iberia
  'Salamanca': [40.97, -5.66, 'locality'],
  'Toledo': [39.86, -4.03, 'locality'],
  'Valladolid': [41.65, -4.72, 'locality'],
  'Madrid': [40.42, -3.70, 'locality'],
  'Aragon': [41.6, -0.9, 'region'],
  'Zaragoza': [41.65, -0.89, 'locality'],
  'Teruel': [40.34, -1.11, 'locality'],

  // the German lands and the north
  'Hesse': [50.6, 9.0, 'region'],
  'Franconia': [49.8, 10.9, 'region'],
  'Lower Saxony': [52.8, 9.4, 'region'],
  'Westphalia': [51.7, 7.9, 'region'],
  'Luneburg Heath': [53.1, 10.1, 'region'],
  'Middle Rhine': [50.2, 7.7, 'region'],
  'Bernese Oberland': [46.6, 7.9, 'region'],
  'Telemark': [59.4, 8.6, 'region'],
  'Numedal': [60.3, 9.1, 'region'],
  'Dalarna': [60.9, 14.5, 'region'],
  'Savo': [62.6, 27.5, 'region'],

  // Italy and Greece
  'Siena': [43.32, 11.33, 'locality'],
  'Chianti': [43.5, 11.3, 'region'],
  "Val d'Orcia": [43.05, 11.6, 'region'],
  'Peloponnese': [37.5, 22.3, 'region'],
  'Attica': [38.0, 23.7, 'region'],

  // the last five the hearths named and this file could not read
  'Manhattan': [40.78, -73.97, 'locality'],
  'Brooklyn': [40.68, -73.94, 'locality'],
  'Bergen County': [40.96, -74.07, 'locality'],
  'Hackensack': [40.89, -74.04, 'locality'],
  'Atlantic seaboard': [39.5, -75.5, 'region'],
  // adjectives are how a hearth names a place: "the Florentine and Sienese hill country"
  'Florentine': [43.77, 11.26, 'region'],
  'Sienese': [43.32, 11.33, 'region'],
  // the four rivers of the Tidewater, named in tidewater-georgian's hearth
  'Rappahannock': [38.0, -76.9, 'region'],
  'Potomac': [38.4, -77.1, 'region'],

  // New Spain
  'Bajio': [20.7, -101.3, 'region'],
  'Hidalgo': [20.5, -98.8, 'region'],
  'Puebla': [19.05, -98.2, 'locality'],
  'Yucatan': [20.7, -89.1, 'region'],
};

/* → {lat, lon, precision, region} for the FINEST region a style names, or null.

   Null means the gazetteer has never heard of any region this style claims. That is
   reported as unlocated, never rounded to a continent: a mark placed where no record put
   one is worse than an absence, because an absence can be seen. */
export function placeByRegions(regions) {
  let best = null;
  for (const r of regions || []) {
    const hit = GAZETTEER[r] || GAZETTEER[String(r).trim()];
    if (!hit) continue;
    const rank = PRECISION[hit[2]];
    if (best === null || rank < best.rank) {
      best = { lat: hit[0], lon: hit[1], precision: hit[2], region: r, rank, via: 'regions' };
      if (rank === 0) break;              // nothing beats a locality
    }
  }
  return best;
}

/* The `regions` list is the coarse answer, and often the corpus knows better in prose.
   `craftsman` lists "United States" and its hearth says "Pasadena and Los Angeles,
   California"; `prairie-school` lists "United States" and says "Oak Park and Chicago".
   Placing those in the middle of Kansas threw away the best geography the record holds —
   59 of the 81 country-level placements had a hearth naming somewhere finer.

   So the hearth sentence is read for place names it shares with this gazetteer. The names
   are sorted longest-first so "Newport, Rhode Island" is tried before "Newport", and each
   is matched on word boundaries so "Bath" does not match "Bathurst".

   THE HEARTH MAY SHARPEN A REGION, NEVER CONTRADICT ONE. A hearth match is rejected when it
   is more than 45° from EVERY region the style names — not merely from the finest one, which
   was the first version of this rule and was wrong. `churrigueresque` lists Spain, Mexico and
   the Spanish Americas and its hearth reads "Madrid, Salamanca and Andalusia"; anchored only
   to the finest region (the Spanish Americas, in Mexico) Madrid looked like a contradiction
   and was thrown away, when Spain is sitting right there in the style's own regions.

   Against every region it still does the work it was written for: `dutch-colonial-american`
   names six regions, all of them American, and its hearth says "the Hudson corridor from
   Nieuw Amsterdam to Beverwijck (Albany)". Amsterdam is far from all six, so it is refused —
   and the sentence resolves to Albany, which is what it meant. That is the difference between
   reading the corpus and guessing at it. Rejections are returned so a caller can report them
   rather than have them vanish. */
const NAMES_BY_LENGTH = Object.keys(GAZETTEER).sort((a, b) => b.length - a.length);
const ESC = /[.*+?^${}()|[\]\\]/g;

/* One RegExp per name for the life of the page, not one per name PER STYLE. Building them
   inside the scan compiled 17,587 of them for a single 164-style pass — 17.9 ms measured,
   and the Phylogeny re-ran it on every keystroke of its filter box. 275 compiles now, once. */
const WORD_RE = new Map();
const wordRe = (name) => {
  let re = WORD_RE.get(name);
  if (!re) {
    re = new RegExp('(^|[^a-z])' + name.toLowerCase().replace(ESC, '\\$&') + '($|[^a-z])');
    WORD_RE.set(name, re);
  }
  return re;
};
const CONTRADICTION_DEGREES = 45;

function degreesApart(a, b) {
  const dLat = a.lat - b.lat;
  // longitude degrees narrow with latitude; at 45° a degree of longitude is ~0.7 of one
  // of latitude, and this only needs to separate "same country" from "other continent"
  const dLon = (a.lon - b.lon) * Math.cos((a.lat + b.lat) / 2 * Math.PI / 180);
  return Math.hypot(dLat, dLon);
}

/* Every point the style's own regions vouch for — the set a hearth match is held against. */
export function regionAnchors(regions) {
  const out = [];
  for (const r of regions || []) {
    const hit = GAZETTEER[r] || GAZETTEER[String(r).trim()];
    if (hit) out.push({ lat: hit[0], lon: hit[1] });
  }
  return out;
}

export function placeByHearth(hearth, anchors) {
  if (!hearth || typeof hearth !== 'string') return null;
  const text = hearth.toLowerCase();
  const vouchers = anchors || [];
  let bestRank = 99;
  let cands = [];
  const rejected = [];

  for (const name of NAMES_BY_LENGTH) {
    const hit = GAZETTEER[name];
    if (hit[3] === REGIONS_ONLY) continue;        // ambiguous in prose — see 'Washington'
    const rank = PRECISION[hit[2]];
    if (rank > bestRank) continue;                // cannot improve on what we have
    const m = text.match(wordRe(name));
    if (!m) continue;
    const found = { lat: hit[0], lon: hit[1], precision: hit[2], region: name, rank, via: 'hearth' };
    const vouched = vouchers.length === 0
      || vouchers.some((a) => degreesApart(found, a) <= CONTRADICTION_DEGREES);
    if (!vouched) { rejected.push(name); continue; }
    if (rank < bestRank) { bestRank = rank; cands = []; }
    cands.push({ ...found, at: m.index });
  }
  if (!cands.length) return null;

  /* THE EARLIEST-MENTIONED PLACE WINS, and the order of these two steps is the whole rule.
     These sentences are written primary-first — "Pasadena and Los Angeles", "San Diego and
     Santa Barbara", "Twickenham for the Gothick phase; Ramsgate, Westminster ... for the
     archaeological one" — and several mark the later ones as secondary in so many words
     ("with a second core", "and after them"). Scanning the gazetteer longest-name-first and
     taking the first hit picked by an accident of key length instead: 25 of 93 hearth
     placements landed on a place the sentence names second or later, `craftsman` among them,
     which put it in Los Angeles while the record said Pasadena — the very word this whole
     reading was justified by.

     Earliest-wins runs AFTER the anchor filter, never before. Sorting first and anchoring
     second would hand `dutch-colonial-american` to Amsterdam, which is the first place its
     hearth names and the exact bug the anchor rule exists to catch. Filtered first, the same
     sentence resolves to Albany. */
  cands.sort((a, b) => a.at - b.at);
  const best = cands[0];
  best.rejected = rejected;
  return best;
}

/* The placement a style actually gets: the finest of what its regions say and what its
   hearth says, with the hearth held to the account of every region the style names. */
export function placeStyle(regions, hearth) {
  const byRegion = placeByRegions(regions);
  const byHearth = placeByHearth(hearth, regionAnchors(regions));
  if (byHearth && (!byRegion || byHearth.rank < byRegion.rank)) {
    return { ...byHearth, coarser: byRegion ? byRegion.region : null };
  }
  return byRegion;
}

export const GAZETTEER_SIZE = Object.keys(GAZETTEER).length;
