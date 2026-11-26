"""French "la nuit de samedi à dimanche": a part of the day named by a range
of days refuses.

"la nuit de samedi à dimanche" is the night that runs from Saturday into
Sunday.  TLFi (CNRTL) s.v. "nuit", II.A, gives the night as the time "depuis
la disparition de la lumière qui suit le coucher du soleil jusqu'à
l'apparition du jour qui precède le lever du soleil", which depends on the
place and the season, and a fixed clock band only in law ("DR. Espace de temps
qui s'étend de 21 heures à 6 heures").  The locale's "nuit" band is the small
hours of one day (Unicode CLDR 47, fr), so it cannot hold a night that starts
the evening before.  "le soir du 3 au 5 mai" names three evenings, no single
span.  So these phrases return nothing.

Before this fix "dans la nuit de samedi à dimanche" said on Thursday
26 November 2026 read 00:00 to 04:00 of that Thursday: a wrong span.
"""
from datetime import datetime

import pytest

from ._corpus import ad, nomatch, parse

THU = datetime(2026, 11, 26, 10, 0)   # a Thursday


@pytest.mark.parametrize("text", [
    "dans la nuit de samedi à dimanche",
    "la nuit de samedi à dimanche",
    "la nuit du samedi au dimanche",
    "nuit de samedi à dimanche",
    "les nuits de samedi à dimanche",
    "la nuit du 28 au 29 novembre",
    "dans la nuit du 28 au 29",
    "la nuit d'hier à aujourd'hui",
    "le soir du 3 au 5 mai",
])
def test_daypart_over_a_range_of_days_refuses(text):
    nomatch(text, THU)


@pytest.mark.parametrize("text,start,end", [
    # one day named: the locale's own band of that day still reads
    ("la nuit de samedi", datetime(2026, 11, 28, 0, 0),
     datetime(2026, 11, 28, 4, 0)),
    ("samedi soir", datetime(2026, 11, 28, 18, 0),
     datetime(2026, 11, 29, 0, 0)),
    # a range of days with no part of the day is unchanged
    ("de samedi à dimanche", datetime(2026, 11, 28, 0, 0),
     datetime(2026, 11, 30, 0, 0)),
])
def test_one_day_or_no_daypart_still_reads(text, start, end):
    r = parse(text, THU)
    assert r is not None
    assert (r[0].start, r[0].end) == (ad(start), ad(end))
    assert r.remainder == ""
