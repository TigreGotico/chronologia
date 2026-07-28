# -*- coding: utf-8 -*-
"""Month + explicit year spans the whole calendar month. Greek names the month
either in the nominative ("Μάρτιος 2019") or the bare genitive ("Μαρτίου 2019");
both bind the same civil month. The span runs [first-of-month, first-of-next),
computed independently by rolling the month number.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start_end

NOM = {
    1: "ιανουάριος", 2: "φεβρουάριος", 3: "μάρτιος", 4: "απρίλιος",
    5: "μάιος", 6: "ιούνιος", 7: "ιούλιος", 8: "αύγουστος",
    9: "σεπτέμβριος", 10: "οκτώβριος", 11: "νοέμβριος", 12: "δεκέμβριος",
}
GEN = {
    1: "ιανουαρίου", 2: "φεβρουαρίου", 3: "μαρτίου", 4: "απριλίου",
    5: "μαΐου", 6: "ιουνίου", 7: "ιουλίου", 8: "αυγούστου",
    9: "σεπτεμβρίου", 10: "οκτωβρίου", 11: "νοεμβρίου", 12: "δεκεμβρίου",
}

_YEARS = [1999, 2008, 2019, 2020, 2026]


def _month_span(y, mo):
    s = datetime(y, mo, 1)
    e = datetime(y + 1, 1, 1) if mo == 12 else datetime(y, mo + 1, 1)
    return ad(s), ad(e)


_NOM_CASES = [(f"{NOM[mo]} {y}", y, mo) for y in _YEARS for mo in range(1, 13)]
_GEN_CASES = [(f"{GEN[mo]} {y}", y, mo) for y in _YEARS for mo in range(1, 13)]


@pytest.mark.parametrize("text,y,mo", _NOM_CASES)
def test_month_year_nominative(text, y, mo):
    assert start_end(text) == _month_span(y, mo)


@pytest.mark.parametrize("text,y,mo", _GEN_CASES)
def test_month_year_genitive(text, y, mo):
    assert start_end(text) == _month_span(y, mo)
