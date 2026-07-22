"""Adversarial Czech cases -- written to break the parser, not to pass it.

Case-form near-misses, direction traps, cross-language contamination, and
the recorded engine gaps (half-TO idiom, oblique-numeral folding, seconds).
"""
import pytest

from ._corpus import ANCHOR, parse, nomatch, start


# -- pure junk never fabricates a date -----------------------------------

@pytest.mark.parametrize("text", [
    "", "   ", "ahoj jak se máš", "qwerty zxcvb", "žádné datum tady",
    "jenom nějaká slova",
])
def test_junk_is_none(text):
    nomatch(text)


# -- an offset needs its direction marker --------------------------------

@pytest.mark.parametrize("text", [
    "pět dní", "dva týdny", "tři měsíce", "deset let", "minut",
])
def test_offset_without_marker(text):
    nomatch(text)


# -- "letos" (this year) must NOT fold into "rok"/"lety" -----------------

def test_letos_is_not_lety():
    # a loose prefix fold would turn "letos" into a year offset -- it must not
    r = parse("letos jedeme na dovolenou")
    assert r is None or r[0].start.year not in (2015, 2019)


# -- impossible clocks never fabricate an out-of-range hour --------------

@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99", "13:75"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


# -- foreign (Slovak/Polish/Russian) phrases must not parse as Czech ------

@pytest.mark.parametrize("text", [
    "za desať minút",        # sk (Czech would be "minut")
    "pojutrze",              # pl (day after tomorrow)
    "через 3 дня",           # ru
    "sutra",                 # hr
])
def test_foreign_not_matched(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


# -- recorded engine gaps: assert the boundary, not a wrong span ---------

def test_halfto_idiom_gap():
    # "půl desáté" = 9:30 (half-TO the tenth); no explicit direction word,
    # so the engine cannot express it -- must not fabricate 10:30 either.
    r = parse("půl desáté")
    if r is not None:
        assert (r[0].start.hour, r[0].start.minute) != (10, 30)


def test_seconds_offset_gap():
    # the engine has no sub-minute offset unit; "za 45 sekund" does not resolve
    nomatch("za 45 sekund")


# -- a bare weekday alone names its next strictly-future occurrence -------

def test_bare_weekday_resolves_next():
    # a bare weekday names its next strictly-future occurrence, a day-wide span
    from datetime import timedelta
    from ._corpus import span
    ahead = (4 - ANCHOR.weekday()) % 7 or 7          # 4 == Friday (pátek)
    s = (ANCHOR + timedelta(days=ahead)).date()
    e = s + timedelta(days=1)
    sp = span("pátek")
    assert (sp.start.year, sp.start.month, sp.start.day) == (s.year, s.month, s.day)
    assert (sp.end.year, sp.end.month, sp.end.day) == (e.year, e.month, e.day)
