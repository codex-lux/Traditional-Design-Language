# oq/a-slug-in-a-code-span-is-not-checked — the citation guard cannot see 65% of the namespace it guards, and removing the exemption would convict five honest illustrations

*Status: OPEN · Raised in: the WP-9.2 adversarial audit (1 Sep 2026)*

**`check_citations.py` validates named open-question citations, and 113 of the 169 in this tree
are invisible to it** — measured at `84314fa`, and **the number moves as documents discuss the
problem**: it was 100 of 153 two commits earlier, and this entry added five more illustrative
slugs of its own. Any figure here is quoted with the commit it was taken at or not at all. Mutation-tested both ways:

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

Measured across the tree at `84314fa`: **113 slug mentions inside code spans (unchecked), 56 in
plain prose (checked)**; at `025329c`, two commits earlier, it was 100 and 53. The corpus froze its numbers at 99 and made slugs the primary mechanism
(`099-how-an-open-question-id-is-issued.md`), so the guard covers the legacy namespace and misses
most of the live one.

## Nothing is currently wrong, and that is the whole difficulty

Of the 113 unchecked mentions at `84314fa`, **103 resolve and 10 do not — and every one of the 10
is deliberate.** Five were there before this audit; **the other five were added by this entry and
by CLAUDE.md quoting it**, which is the clearest possible statement of the problem: a document
cannot describe the ambiguity without producing more of it.

| mention | where | what it is |
|---|---|---|
| `oq/no-such-question` | `tests/test_citations.py:276` | this checker's own test fixture |
| `oq/span-partial-bearing-wall` ×4 | `099-…`:7, `oq-two-id-namespaces.md`:8 and :14, `wp-8.1-the-citation-guard.md`:142 | a hypothetical slug used to explain the naming scheme — `oq-two-id-namespaces` uses it precisely as its example of a slug that would duplicate OQ 98 |

So **the exemption is doing its job for five real uses, and simply deleting it would produce five
false accusations including one against the checker's own test.** This is not a dead guard to be
switched on; it is a guard whose blind spot is load-bearing.

## The question

**How does a document cite a named question distinguishably from illustrating one?** Four shapes:

1. **Check slugs inside code spans, and give illustrations a form that is not a slug.** Rewrite the
   five as `oq/<slug>` or `oq/example-only`, neither of which matches the id pattern. Cheapest and
   closes the gap completely; costs one edit to a test fixture and three documents, and commits the
   corpus to never writing a plausible-looking example slug again.
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
slug" is a rule nobody will remember, which is how the five got written in the first place.

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
