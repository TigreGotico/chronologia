# -*- coding: utf-8 -*-
"""Second-pass sweep: relative-period marker SYNONYMS not yet exercised.

``chronologia/locale/eu/marker_next.voc`` lists three next-markers
(``datorren``, ``hurrengo``, ``ondorengo``), ``marker_last.voc`` lists three
past-markers (``aurreko``, ``joan den``, ``pasa den``), and ``marker_this.voc``
lists two this-markers (``honetako``, ``oraingo``).  The first-pass
``test_rel_period.py`` only ever used ``datorren``/``aurreko``/``aste
honetako`` -- this sweep exercises the remaining synonyms across week, month
and year so every voc surface is proven, not just one representative per
polarity.  Gold is independent calendar arithmetic against the Tuesday
2017-06-27 anchor, matching the reckoning already established in
``test_rel_period``.  Week start index 0 (Monday).
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, span

_MID = dict(hour=0, minute=0, second=0, microsecond=0)
_SIDX = 0


def _expected(rel, unit):
    if unit == "week":
        base = ANCHOR.replace(**_MID)
        s = base - timedelta(days=(base.weekday() - _SIDX) % 7) + timedelta(weeks=rel)
        e = s + timedelta(days=7)
    elif unit == "month":
        s = ANCHOR.replace(day=1, **_MID) + relativedelta(months=rel)
        e = s + relativedelta(months=1)
    elif unit == "year":
        s = ANCHOR.replace(month=1, day=1, **_MID) + relativedelta(years=rel)
        e = s + relativedelta(years=1)
    else:
        raise AssertionError(unit)
    return AstroDate(s.year, s.month, s.day), AstroDate(e.year, e.month, e.day)


# next-marker synonyms: hurrengo, ondorengo (datorren already covered)
NEXT_CASES = [
    ("hurrengo astea", 1, "week"),
    ("hurrengo hilabetea", 1, "month"),
    ("hurrengo urtea", 1, "year"),
    ("ondorengo astea", 1, "week"),
    ("ondorengo hilabetea", 1, "month"),
    ("ondorengo urtea", 1, "year"),
]

# last-marker synonyms: joan den, pasa den (aurreko already covered)
LAST_CASES = [
    ("joan den astea", -1, "week"),
    ("joan den hilabetea", -1, "month"),
    ("joan den urtea", -1, "year"),
    ("pasa den astea", -1, "week"),
    ("pasa den hilabetea", -1, "month"),
    ("pasa den urtea", -1, "year"),
]

# this-marker synonym: oraingo (aste honetako already covered)
THIS_CASES = [
    ("oraingo astea", 0, "week"),
    ("oraingo hilabetea", 0, "month"),
    ("oraingo urtea", 0, "year"),
    ("honetako hilabetea", 0, "month"),
    ("honetako urtea", 0, "year"),
]


@pytest.mark.parametrize("text,rel,unit", NEXT_CASES + LAST_CASES + THIS_CASES)
def test_marker_synonym_rel_period(text, rel, unit):
    sp = span(text)
    assert (sp.start, sp.end) == _expected(rel, unit)
