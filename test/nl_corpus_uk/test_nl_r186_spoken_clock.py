"""R186 (uk): the spoken Ukrainian clock -- a locative "at <hour>" ("о
другій") and the toward-hour half/quarter ("пів на другу", "чверть на
одинадцяту").  Both were dead: the locative ordinal never folded to a digit,
so even the plain hour returned no match at all.

Direction is a fact of the language, not a guess: "пів на другу" ("half
onto the second") NAMES THE COMING HOUR, 01:30 -- not 02:30.  Two
independent worked examples confirm this:
  - promovu.in.ua, "Час англійською": "13:30 - пів на другу" and
    "10:15 - чверть на одинадцяту, чверть по десятій".
    https://promovu.in.ua/time/
  - miyklas.com.ua, 6th-grade Ukrainian-language lesson: "10:30 ...
    десята година тридцять хвилин ... пів на одинадцяту".
    https://www.miyklas.com.ua/p/ukrainska-mova/6-klas/chislivnik-14257/vikoristannia-chislivnikiv-na-poznachennia-dat-i-chasu-37756/

Golds below are computed by hand from the 2017-06-27 13:04 Tuesday anchor
with ``prefer_future``: any wall time already passed today rolls to the next
day, 2017-06-28.
"""
from datetime import timedelta

from ._corpus import ANCHOR, ad, parse


def test_locative_bare_hour():
    # "о другій" == at two o'clock == 02:00, the LITERAL named hour.
    r = parse("о другій")
    assert r is not None
    assert r.span.start == ad(ANCHOR.replace(day=28, hour=2, minute=0,
                                             second=0, microsecond=0))
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""


def test_toward_hour_half_names_the_coming_hour():
    # "пів на другу" == half onto the second == 01:30, NOT 02:30 -- a
    # reversed reading would silently land here.  Pinned side-by-side with
    # the plain "о другій" == 02:00 above: the two must differ by a full
    # 30 minutes AND a full hour of "which hour is named", so a swapped
    # direction fails loudly rather than by a rounding coincidence.
    r = parse("пів на другу")
    assert r is not None
    assert r.span.start == ad(ANCHOR.replace(day=28, hour=1, minute=30,
                                             second=0, microsecond=0))
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""


def test_toward_hour_quarter_names_the_coming_hour():
    # "чверть на одинадцяту" == a quarter onto the eleventh == 10:15, the
    # differ-by-a-full-hour adversarial case: naively read as "quarter PAST
    # ten" it would be 10:15 too by coincidence for :15, so pair it against
    # the bare locative hour it is built from.
    r = parse("чверть на одинадцяту")
    assert r is not None
    assert r.span.start == ad(ANCHOR.replace(day=28, hour=10, minute=15,
                                             second=0, microsecond=0))
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""


def test_locative_bare_hour_eleven_pairs_with_toward_quarter():
    # "о одинадцятій" == at eleven o'clock == 11:00, sitting a full hour
    # after the toward-quarter reading above (10:15) -- if the toward-hour
    # construction were reversed to name the PAST hour instead of the
    # coming one, this pair would collapse toward the same hour instead of
    # standing a full 45 minutes apart.
    r = parse("о одинадцятій")
    assert r is not None
    assert r.span.start == ad(ANCHOR.replace(day=28, hour=11, minute=0,
                                             second=0, microsecond=0))
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""
