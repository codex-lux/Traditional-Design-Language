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

export const PRECISION = { locality: 0, region: 1, country: 2 };

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
  'Washington': [47.4, -120.5, 'region'],
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
};

/* → {lat, lon, precision, region} for the FINEST region a style names, or null.

   Null means the gazetteer has never heard of any region this style claims. That is
   reported as unlocated, never rounded to a continent: a mark placed where no record put
   one is worse than an absence, because an absence can be seen. */
export function placeStyle(regions) {
  let best = null;
  for (const r of regions || []) {
    const hit = GAZETTEER[r] || GAZETTEER[String(r).trim()];
    if (!hit) continue;
    const rank = PRECISION[hit[2]];
    if (best === null || rank < best.rank) {
      best = { lat: hit[0], lon: hit[1], precision: hit[2], region: r, rank };
      if (rank === 0) break;              // nothing beats a locality
    }
  }
  return best;
}

export const GAZETTEER_SIZE = Object.keys(GAZETTEER).length;
