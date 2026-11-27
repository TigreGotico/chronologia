"""Lone day-part words with no reading yet, pinned as strict xfails.

Anchor: Tuesday 2023-06-27 13:04.  Bands: CLDR 47, de morgen [05:00, 10:00),
it mattina [06:00, 12:00) and sera [18:00, 24:00).
"""
from datetime import datetime, timedelta

import pytest

from chronologia.extract import extract_timespan

ANCHOR = datetime(2023, 6, 27, 13, 4)
TODAY = ANCHOR.replace(hour=0, minute=0)


def _start(text, lang):
    r = extract_timespan(text, lang, anchor=ANCHOR)
    assert r is not None
    s = r.span.start
    return datetime(s.year, s.month, s.day, s.hour, s.minute)


@pytest.mark.xfail(strict=True, reason="chronologia#1465: de 'am Morgen' reads as tomorrow")
def test_de_am_morgen_is_the_morning():
    assert _start("Am Morgen hat mich meine Schwester angerufen", "de") == TODAY + timedelta(hours=5)


@pytest.mark.xfail(strict=True, reason="chronologia#1465: de 'in der Früh' gives no reading")
def test_de_in_der_frueh_is_the_morning():
    assert _start("Ausgerechnet in der Früh ist mir das Wechselgeld unter die Theke gerollt", "de") == TODAY + timedelta(hours=5)


@pytest.mark.xfail(strict=True, reason="chronologia#1103: it fused 'stasera'/'stamattina' give no reading")
@pytest.mark.parametrize("text, hours", [
    ("Stasera passo da mia sorella.", 18),
    ("Stamattina ho incontrato Lucia al mercato.", 6),
])
def test_it_fused_daypart(text, hours):
    assert _start(text, "it") == TODAY + timedelta(hours=hours)
