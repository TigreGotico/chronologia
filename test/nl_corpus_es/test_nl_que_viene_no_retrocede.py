# -*- coding: utf-8 -*-
""""la semana que viene" names one week counted from now.

On Thursday 2026-12-31, "la semana que viene" is Monday 4 January to Monday
11 January 2027.  It lies after "el 31 de diciembre", so the range is
reversed: no range is read, and the words stay in the remainder.  The left
end is never moved back a year.
"""
from datetime import datetime

from ._corpus import ad, parse


def test_semana_que_viene_no_retrocede_un_ano():
    r = parse("desde la semana que viene hasta el 31 de diciembre",
              datetime(2026, 12, 31, 12, 0))
    assert r is not None
    assert (r.span.start, r.span.end) == (ad(datetime(2027, 1, 4)),
                                          ad(datetime(2027, 1, 11)))
    assert r.remainder != ""
