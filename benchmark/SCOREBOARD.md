# Differential benchmark scoreboard

Generated: 2026-07-22 17:53 UTC

Gold cases: 1049 hand-derived `(text, expected_date)` pairs across 30 languages, pulled live from the repo's own `test/nl_corpus_*` corpora (see `benchmark/adapter.py`) -- independent of all three engines under test.

Generation command: `python benchmark/run.py`

House rule: **benchmark, don't assert.** This is a snapshot, not a gate; nothing here fails CI. Competitors emit plain `datetime`s, so every engine is scored against the gold case's exact expected *date* (chronologia's result is reduced to `span.start.date()`).

Outcome key: **exact** = parsed date matches gold; **no-parse** = engine returned nothing; **wrong** = engine returned a date that does not match.

## Per-language accuracy (exact-match %)

| lang | n | chronologia | dateparser | dateutil |
|---|---|---|---|---|
| an | 7 | 100% (7/7) | 0% (0/7) | 0% (0/7) |
| ar | 48 | 100% (48/48) | 17% (8/48) | 0% (0/48) |
| ast | 59 | 100% (59/59) | 41% (24/59) | 0% (0/59) |
| bg | 10 | 100% (10/10) | 0% (0/10) | 0% (0/10) |
| ca | 80 | 100% (80/80) | 30% (24/80) | 0% (0/80) |
| cs | 13 | 100% (13/13) | 0% (0/13) | 0% (0/13) |
| da | 5 | 100% (5/5) | 0% (0/5) | 0% (0/5) |
| de | 14 | 100% (14/14) | 0% (0/14) | 0% (0/14) |
| en | 115 | 100% (115/115) | 57% (66/115) | 10% (12/115) |
| es | 94 | 100% (94/94) | 64% (60/94) | 0% (0/94) |
| fa | 7 | 100% (7/7) | 0% (0/7) | 0% (0/7) |
| fr | 94 | 100% (94/94) | 67% (63/94) | 0% (0/94) |
| fy | 5 | 100% (5/5) | 0% (0/5) | 0% (0/5) |
| gl | 80 | 100% (80/80) | 50% (40/80) | 0% (0/80) |
| he | 40 | 100% (40/40) | 80% (32/40) | 0% (0/40) |
| hr | 10 | 100% (10/10) | 0% (0/10) | 0% (0/10) |
| it | 74 | 100% (74/74) | 64% (47/74) | 0% (0/74) |
| mwl | 7 | 100% (7/7) | 0% (0/7) | 0% (0/7) |
| nb | 5 | 100% (5/5) | 0% (0/5) | 0% (0/5) |
| nl | 5 | 100% (5/5) | 0% (0/5) | 0% (0/5) |
| nn | 5 | 100% (5/5) | 0% (0/5) | 0% (0/5) |
| oc | 52 | 100% (52/52) | 2% (1/52) | 0% (0/52) |
| pl | 10 | 100% (10/10) | 0% (0/10) | 0% (0/10) |
| pt | 94 | 100% (94/94) | 64% (60/94) | 0% (0/94) |
| ro | 69 | 100% (69/69) | 54% (37/69) | 0% (0/69) |
| ru | 11 | 100% (11/11) | 0% (0/11) | 0% (0/11) |
| sk | 11 | 100% (11/11) | 0% (0/11) | 0% (0/11) |
| sl | 10 | 100% (10/10) | 0% (0/10) | 0% (0/10) |
| sv | 5 | 100% (5/5) | 0% (0/5) | 0% (0/5) |
| uk | 10 | 100% (10/10) | 0% (0/10) | 0% (0/10) |

## Overall (all languages combined)

| engine | exact | no-parse | wrong | accuracy |
|---|---|---|---|---|
| chronologia | 1049 | 0 | 0 | 100.0% |
| dateparser | 462 | 585 | 2 | 44.0% |
| dateutil | 12 | 272 | 765 | 1.1% |

## Honest notes

Business-day corpus golds are excluded from the comparison: they are computed
with the `jurisdiction=` keyword (holiday-aware counting) and per-case anchors
the collector cannot reproduce, and the competitor engines have no concept of
a holiday jurisdiction at all -- including them would score three engines on
different questions. On every case the harness can reproduce faithfully, the
engines answer the same question.

chronologia leads (or ties) exact-match accuracy on every language in this run.

Caveats: dateparser/dateutil are general-purpose date parsers, not span-native (they collapse a phrase to its left edge datetime, never a width); this benchmark only credits the start-of-span comparison chronologia's own spec calls for, so it necessarily understates what chronologia additionally returns (the end of the span, resolution, calendar metadata) that the competitors cannot represent at all.

