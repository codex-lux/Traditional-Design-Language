# oq/a-slug-in-a-code-span-is-not-checked — the citation guard cannot see two thirds of the namespace it guards, and removing the exemption would convict fourteen honest illustrations

*Status: OPEN · Raised in: the WP-9.2 adversarial audit (1 Sep 2026)*

**`check_citations.py` validates named open-question citations, and 122 of the 178 in this tree
were invisible to it at `5572866`** — and **the number moves as documents discuss the problem**:
100 of 153 at `025329c`, 113 of 169 at `84314fa`, 122 of 178 at `5572866`. **Correcting this entry
took it to 126 of 182**, because the corrections below name the illustrative slugs one more time
each. Every figure here is quoted with the commit it was taken at, or as a stated delta from one.
Mutation-tested both ways:

```
fake slug in plain prose          ->  DANGLING  ...:127: OQ-SLUG-THAT-NAMES-NO-ENTRY names no entry
the same fake slug in `backticks` ->  0 dangling, silently accepted
```

*(The fake slug is written in capitals above because the first draft of this entry used a real-
looking one and **`check_citations.py` convicted this file for it** — see "the entry convicted
itself" below.)*

The cause is one line, and it is deliberate:

```python
# An inline code span is a QUOTATION, not a citation. Documents that discuss this
# bug have to be able to write `OQ 82 and 84` to show what it looks like ...
line = CODE.sub(lambda c: " " * len(c.group(0)), line)
```

**That exemption was written for the NUMBERED namespace, where prose is the citation form and a
code span is the exception. For slugs the convention is inverted**: `` `oq/the-raw-kit-read` `` in
backticks *is* how this corpus cites a named question — CLAUDE.md does it, every report does it,
and this file does it in the sentence you are reading. So for slugs, citation and illustration are
typographically identical and the checker cannot tell them apart.

Measured across the tree at `5572866`: **122 slug mentions inside code spans (unchecked), 56 in
plain prose (checked)** — 68.5%, and 126/56 (69.2%) after this correction; at `84314fa` it was 113
and 56, at `025329c` 100 and 53. **The checked count has not moved in three commits while the
unchecked count has risen by 26**, which is the trend the question is about. The corpus froze its numbers at 99 and made slugs the primary mechanism
(`099-how-an-open-question-id-is-issued.md`), so the guard covers the legacy namespace and misses
most of the live one.

## Nothing is currently wrong, and that is the whole difficulty

Of the 122 unchecked mentions at `5572866`, **112 resolved and 10 did not — and every one of the
10 was deliberate.** Five were there before this audit; **the other five were added by this entry
and by CLAUDE.md quoting it**, which is the clearest possible statement of the problem: a document
cannot describe the ambiguity without producing more of it. **Correcting this entry made it 14**,
for the same reason and in the paragraph reporting it. Three distinct slugs across those 14:
`oq/span-partial-bearing-wall` 7, `oq/no-such-question` 4, and the placeholder discussed under (1)
3.

| mention | where | what it is |
|---|---|---|
| `oq/no-such-question` ×4 | `tests/test_citations.py`, `CLAUDE.md`, this file ×2 | this checker's own test fixture, and the documents quoting it |
| `oq/span-partial-bearing-wall` ×7 | `099-…`, `oq-two-id-namespaces` ×2, `wp-8.1-the-citation-guard.md`, `CLAUDE.md`, this file ×2 | a hypothetical slug used to explain the naming scheme — `oq-two-id-namespaces` uses it precisely as its example of a slug that would duplicate OQ 98 |
| `oq/example-only` ×3 | this file only | proposed below as a safe illustration form — **and it is not one**; see the correction under (1). Line numbers are omitted from this table on purpose: they moved three times while it was being written |

So **the exemption is doing its job for three distinct illustrative slugs across fourteen mentions,
and simply deleting it would produce fourteen false accusations including one against the checker's
own test.** This is not a dead guard to be switched on; it is a guard whose blind spot is
load-bearing.

## The question

**How does a document cite a named question distinguishably from illustrating one?** Four shapes:

1. **Check slugs inside code spans, and give illustrations a form that is not a slug.** Rewrite the
   fourteen as something the id pattern cannot match. **The first draft of this entry proposed
   `oq/<slug>` or `oq/example-only` and one of the two is wrong**: `SLUG_CITE` is
   `\boq/[a-z0-9][a-z0-9-]*`, so `oq/example-only` matches it exactly and adopting it would create
   the eleventh dangling citation this shape is meant to prevent — the entry proposing the fix
   demonstrating the bug for the second time. `oq/<slug>` is safe because `<` is outside the
   character class. Cheapest and closes the gap completely; costs one edit to a test fixture and
   four documents, and commits the corpus to never writing a plausible-looking example slug again.
2. **Check slugs inside code spans, with a declared exemption marker** — a trailing comment or an
   `<!-- illustration -->` on the line. Honest and explicit; adds a second thing to remember.
3. **Change the citation convention: cite slugs in plain prose, reserve backticks for
   illustration**, mirroring the numbered namespace exactly. Most consistent, and it means
   rewriting 100 mentions and retraining every future agent against what currently reads as
   idiomatic.
4. **Leave it, and record that named citations are checked only in prose.** Defensible only if
   somebody states it — an unstated blind spot in a guard is the WP-8.6 pattern, and this register
   already carries `oq/two-id-namespaces` about the cost of the split.

**(1) looks right and is not obviously right**, because "never write an example that looks like a
slug" is a rule nobody will remember — which is how the fourteen got written in the first place,
and how this entry's own proposed replacement broke it in the sentence proposing it.

## The entry convicted itself, which is the finding in one line

The first draft of this file wrote the mutation output with a plausible fake slug inside a
**fenced** code block. `check_citations.py` exempts only **inline** code spans — a fenced block is
scanned like prose — so the run came back `1 dangling`, naming this file, for an illustration of
the very ambiguity the file is about.

That is worth keeping rather than quietly fixing, because it sharpens the question. The corpus has
**three** contexts, not two, and only one of them is exempt:

| context | scanned? |
|---|---|
| plain prose | yes — and this is the numbered namespace's citation form |
| ``inline `code span` `` | **no** — and this is the slug namespace's citation form |
| fenced ``` block ``` | yes |

So an author illustrating a slug has exactly one place to do it safely (an inline span) and that
is the same place a citation lives. Any fix in shape (1) above must say what an illustration looks
like, or the next person writing about this problem will trip the same wire.

## Provenance

Found by mutation-testing `check_citations.py` during the WP-9.2 audit rather than by reading it:
the plain-prose mutation failed as expected, the backticked one passed, and the difference is what
exposed the exemption. **Pre-existing — not introduced by WP-9.2** — though that package added six
named entries and dozens of backticked citations to a namespace it did not know was unguarded.
Nothing in the tree is dangling today; the guard simply would not notice if it were.
