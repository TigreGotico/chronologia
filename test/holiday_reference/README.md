# Frozen reference snapshots

`national.json` holds a frozen snapshot of an independent reference calendar's
national (jurisdiction-wide, observed) holiday dates, as
`{jurisdiction: {year: [[month, day], ...]}}`, captured from vacanza/holidays
0.101.

The snapshot is a fixture, not a live oracle. The per-country differential tests
compare chronologia's own national public set against these frozen dates and
require every disagreement to be listed and justified in the calling module. A
frozen snapshot keeps that differential reproducible: the suite asserts the same
thing on every machine and in every year, and no third-party release can turn it
red without a deliberate refresh of this file.

Regenerate only when a refresh against a newer reference release is the intended
change, and re-justify every disagreement that moves.
