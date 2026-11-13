"""A sentence end in any script stops the apposed-weekday fold.

A weekday after a day word is an apposition only inside one sentence:
"vou amanhã. segunda-feira trabalho" names tomorrow, and the next sentence
stays in the remainder.  Each script writes its own sentence end: the Arabic
question mark U+061F and full stop U+06D4 (ar, fa), the Devanagari danda
U+0964 and double danda U+0965 (hi), the Armenian full stop U+0589 (hy), the
Greek question mark U+037E (el), the ellipsis U+2026, and the line breaks
CR, U+2028 and U+2029.

Anchor Saturday 2026-10-17 12:00.  Tomorrow is Sunday 2026-10-18, so a fold
of a Monday onto it would refuse the phrase.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

SATURDAY = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("lang,text,offset,rest", [
    ("ar", "غدا\u061f الاثنين", 1, "الاثنين"),
    ("ar", "غدا\u06d4 الاثنين", 1, "الاثنين"),
    ("fa", "فردا\u061f دوشنبه", 1, "دوشنبه"),
    ("hi", "आज\u0964 सोमवार", 0, "सोमवार"),
    ("hi", "आज\u0965 सोमवार", 0, "सोमवार"),
    ("hy", "վաղը\u0589 երկուշաբթի", 1, "երկուշաբթի"),
    ("el", "αύριο\u037e Δευτέρα", 1, "Δευτέρα"),
    ("pt", "amanhã\u2026 segunda-feira", 1, "segunda-feira"),
    ("en", "tomorrow\rmonday", 1, "monday"),
    ("en", "tomorrow\u2028monday", 1, "monday"),
    ("en", "tomorrow\u2029monday", 1, "monday"),
])
def test_a_sentence_end_stops_the_fold(lang, text, offset, rest):
    day = SATURDAY.replace(hour=0) + timedelta(days=offset)
    r = extract_timespan(text, lang, SATURDAY)
    assert r is not None, f"{text!r} was refused"
    assert r[0].start == AstroDate(day.year, day.month, day.day)
    assert r[1] == rest
