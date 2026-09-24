/* THE SEVEN SCHEMA FIELDS A GLOSSARY RECORD MAY BIND A WORD TO (WP-14.6, PRD §A.4).

   A glossary record's `binds` ties a word to one real member of a schema enum — `binding-open` to
   `kit.binding = open` — so a surface can ask "what is this value called?" through
   `lookup.termFor(field, value)` instead of printing the machine value. The server serves the
   resolved map as `by_field`; this table is the app's statement of WHICH fields that map may carry
   and where each one's enum lives, so a reader can check a field before asking for it.

   It is spelled twice by design: here, and as `FIELDS` in `build/check_glossary.py` (WP-14.1).
   `src/glossary.test.mjs` (WP-14.8) holds this table to the records both ways, and
   `src/lookup.test.mjs` holds each pointer to the schema file it names, so neither copy can name a
   field whose enum is not where it says. The id of the record binding a value is NOT derived
   here: that is `by_field`'s, read off the records' own `binds`, and a second rule for it would
   be a second answer.

   Pure data. */

const field = (family, schema, pointer) => Object.freeze({ family, schema, pointer });

export const FIELDS = Object.freeze({
  'style.rank': field('rank', 'schema/style-node.schema.json', '/properties/rank'),
  'lineage.type': field('edge', 'schema/style-node.schema.json',
    '/properties/lineage/items/properties/type'),
  'kit.binding': field('binding', 'schema/kit.schema.json',
    '/properties/slots/additionalProperties/properties/binding'),
  'kit.variant_status': field('variant-status', 'schema/kit.schema.json',
    '/properties/slots/additionalProperties/properties/variants/items/properties/status'),
  'kit.parameter_kind': field('param-kind', 'schema/kit.schema.json',
    '/$defs/parameter/properties/kind'),
  'pack.kind': field('pack-kind', 'schema/proportion-pack.schema.json', '/properties/kind'),
  'fault.severity': field('severity', 'schema/fault.schema.json', '/properties/severity'),
});
