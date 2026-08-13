# -*- coding: utf-8 -*-
"""R163 (en) -- a BARE "every <N> last <weekday>" (no "of ... month/year"
scope tail) misread as a day-of-month rule, stranding "last <weekday>".

``_recur_every``'s ellipsis for "every last <weekday>" (-> the -1st weekday
of the month, ``FREQ=MONTHLY;BYDAY=-1<WD>``) only fired when ``num_val is
None`` -- i.e. no leading interval count. With a count present ("every 2nd
last friday") that guard failed, the next branch ("every <ordinal>
<weekday>") also failed because ``t[j]`` was the "last" marker rather than a
weekday, and the phrase fell through to the day-of-month ellipsis ("every
<ordinal> [of the month]" -> ``BYMONTHDAY``), which DOES accept an ordinal
surface with no tail at all -- "2nd" folded to ``BYMONTHDAY=2`` and "last
friday" was left stranded as unmatched remainder: silently wrong (a day-of-
month rule, not the last-friday-of-the-month rule the phrase names) AND
stranded.

DECIDED SEMANTICS: mirrors the month-scope decision from R154 -- the bare
"every <N> last <weekday>" ellipsis reads as the SAME monthly last-weekday
rule the explicit "of the month" tail already produces, with the interval
prefix DROPPED exactly as "every 2nd last friday of the month" already drops
it (the base MONTHLY cadence already IS the elliptical reading, so an
explicit interval would be degenerate). Root: the day-of-month ellipsis
claimed the ordinal before the last-weekday ellipsis got a chance to see the
"last <weekday>" tail behind the count -- fixed by adding a "every <N> last
<weekday>" branch to ``_recur_every`` ahead of the day-of-month one, mirroring
the existing bare "every last <weekday>" branch but keyed off ``num_val is
not None`` instead of ``is None``.

de/es siblings: R154 (the interval-fold decision this defect mirrors)
documented NO de/es surface at all for the "every other"/"every Nth"
interval-prefix vocabulary this defect also depends on -- so this defect's
de/es siblings are unattested for the same reason and are skipped, en only.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "en"

_CASES = [
    # -- the defect: bare interval + last-weekday must read elliptically,
    # not as a day-of-month rule ------------------------------------------
    ("every 2nd last friday", "FREQ=MONTHLY;BYDAY=-1FR", ""),
    ("every 3rd last monday", "FREQ=MONTHLY;BYDAY=-1MO", ""),
    # -- controls: established readings this fix must not regress ----------
    ("every last friday", "FREQ=MONTHLY;BYDAY=-1FR", ""),
    ("every 2nd last friday of the month", "FREQ=MONTHLY;BYDAY=-1FR", ""),
    ("every 2nd last friday of the year",
     "FREQ=YEARLY;INTERVAL=2;BYDAY=-1FR", ""),
    ("every 2nd friday", "FREQ=WEEKLY;INTERVAL=2;BYDAY=FR", ""),
    ("every 2nd of the month", "FREQ=MONTHLY;BYMONTHDAY=2", ""),
    ("every 1st of the month", "FREQ=MONTHLY;BYMONTHDAY=1", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bare_interval_last_weekday_reads_elliptically(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
