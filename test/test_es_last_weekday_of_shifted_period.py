"""The last weekday of a period named after its noun, in Spanish.

"el mes que viene", "el mes pasado" and "el año 2027" put the relative word
or the year after the period noun, and "el mes de noviembre" puts the month
noun before the month name.  The anchor is Saturday 17 October 2026.  The
golds are calendar arithmetic: 30 November 2026 is a Monday, so the last
Friday of November is the 27th; 30 September 2026 is a Wednesday (25th);
31 December 2027 is a Friday; 31 December 2025 is a Wednesday (26th);
31 October 2027 is a Sunday (29th).  1 November 2026 is a Sunday, so the
first Monday of November is the 2nd, the first Friday the 6th and the second
Tuesday the 10th; 31 October 2026 is a Saturday, so the last Friday of
October is the 30th.
"""
from datetime import datetime

import pytest

from chronologia import AstroDate, extract_timespan

ANCHOR = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("text, lang, day", [
    ("el último viernes del mes que viene", "es", (2026, 11, 27)),
    ("el último viernes del mes siguiente", "es", (2026, 11, 27)),
    ("el último viernes del mes pasado", "es", (2026, 9, 25)),
    ("el último viernes del año que viene", "es", (2027, 12, 31)),
    ("el último viernes del año siguiente", "es", (2027, 12, 31)),
    ("el último viernes del año pasado", "es", (2025, 12, 26)),
    ("el último viernes de octubre del año 2027", "es", (2027, 10, 29)),
    ("el último viernes del mes de noviembre", "es", (2026, 11, 27)),
    ("el último viernes del próximo mes", "es", (2026, 11, 27)),
    ("el último viernes de noviembre", "es", (2026, 11, 27)),
    ("the last friday of next month", "en", (2026, 11, 27)),
    ("el último viernes del mes que viene a las 3", "es", (2026, 11, 27, 3)),
    ("le dernier vendredi du mois prochain", "fr", (2026, 11, 27)),
    ("le dernier vendredi du mois dernier", "fr", (2026, 9, 25)),
    ("il ultimo venerdì del mese prossimo", "it", (2026, 11, 27)),
    ("il ultimo venerdì del mese scorso", "it", (2026, 9, 25)),
    ("l ultim divendres del mes que ve", "ca", (2026, 11, 27)),
    ("o ultimo venres do mes que vén", "gl", (2026, 11, 27)),
])
def test_last_weekday_of_the_period(text, lang, day):
    r = extract_timespan(text, lang, ANCHOR)
    assert (r.span.start, r.remainder) == (AstroDate(*day), "")


@pytest.mark.parametrize("text, lang, day, rest", [
    ("the first monday of the month this year", "en", (2026, 11, 2),
     "this year"),
    ("pay rent the first friday of the month this time", "en",
     (2026, 11, 6), "pay rent this time"),
    ("the second tuesday of the month this time", "en", (2026, 11, 10),
     "this time"),
    ("the last friday of the month last year", "en", (2026, 10, 30),
     "last year"),
    ("the last friday of the month next year", "en", (2026, 10, 30),
     "next year"),
    ("el primer lunes del mes este año", "es", (2026, 11, 2), "este año"),
    ("der erste Montag des Monats nächstes Jahr", "de", (2026, 11, 2),
     "nächstes Jahr"),
    ("de eerste maandag van de maand volgend jaar", "nl", (2026, 11, 2),
     "volgend jaar"),
])
def test_a_period_noun_after_the_month_stays_out_of_its_scope(text, lang, day,
                                                              rest):
    r = extract_timespan(text, lang, ANCHOR)
    assert (r.span.start, r.remainder) == (AstroDate(*day), rest)
