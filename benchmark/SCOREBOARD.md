# Differential benchmark scoreboard

Generated: 2026-07-22 14:06 UTC

Gold cases: 1002 hand-derived `(text, expected_date)` pairs across 21 languages, pulled live from the repo's own `test/nl_corpus_*` corpora (see `benchmark/adapter.py`) -- independent of all three engines under test.

Generation command: `python benchmark/run.py`

House rule: **benchmark, don't assert.** This is a snapshot, not a gate; nothing here fails CI. Competitors emit plain `datetime`s, so every engine is scored against the gold case's exact expected *date* (chronologia's result is reduced to `span.start.date()`).

Outcome key: **exact** = parsed date matches gold; **no-parse** = engine returned nothing; **wrong** = engine returned a date that does not match.

## Per-language accuracy (exact-match %)

| lang | n | chronologia | dateparser | dateutil |
|---|---|---|---|---|
| ar | 40 | 100% (40/40) | 20% (8/40) | 0% (0/40) |
| ast | 59 | 100% (59/59) | 41% (24/59) | 0% (0/59) |
| bg | 4 | 100% (4/4) | 0% (0/4) | 0% (0/4) |
| ca | 80 | 100% (80/80) | 30% (24/80) | 0% (0/80) |
| cs | 7 | 100% (7/7) | 0% (0/7) | 0% (0/7) |
| de | 27 | 78% (21/27) | 0% (0/27) | 0% (0/27) |
| en | 132 | 95% (126/132) | 50% (66/132) | 9% (12/132) |
| es | 106 | 95% (101/106) | 57% (60/106) | 0% (0/106) |
| fr | 106 | 95% (101/106) | 59% (63/106) | 0% (0/106) |
| gl | 80 | 100% (80/80) | 50% (40/80) | 0% (0/80) |
| he | 32 | 100% (32/32) | 100% (32/32) | 0% (0/32) |
| hr | 4 | 100% (4/4) | 0% (0/4) | 0% (0/4) |
| it | 74 | 100% (74/74) | 64% (47/74) | 0% (0/74) |
| oc | 52 | 100% (52/52) | 2% (1/52) | 0% (0/52) |
| pl | 4 | 100% (4/4) | 0% (0/4) | 0% (0/4) |
| pt | 108 | 94% (102/108) | 56% (60/108) | 0% (0/108) |
| ro | 69 | 100% (69/69) | 54% (37/69) | 0% (0/69) |
| ru | 5 | 100% (5/5) | 0% (0/5) | 0% (0/5) |
| sk | 5 | 100% (5/5) | 0% (0/5) | 0% (0/5) |
| sl | 4 | 100% (4/4) | 0% (0/4) | 0% (0/4) |
| uk | 4 | 100% (4/4) | 0% (0/4) | 0% (0/4) |

## Overall (all languages combined)

| engine | exact | no-parse | wrong | accuracy |
|---|---|---|---|---|
| chronologia | 974 | 0 | 28 | 97.2% |
| dateparser | 462 | 540 | 0 | 46.1% |
| dateutil | 12 | 240 | 750 | 1.2% |

## Honest notes

chronologia leads (or ties) exact-match accuracy on every language in this run.

Caveats: dateparser/dateutil are general-purpose date parsers, not span-native (they collapse a phrase to its left edge datetime, never a width); this benchmark only credits the start-of-span comparison chronologia's own spec calls for, so it necessarily understates what chronologia additionally returns (the end of the span, resolution, calendar metadata) that the competitors cannot represent at all.

