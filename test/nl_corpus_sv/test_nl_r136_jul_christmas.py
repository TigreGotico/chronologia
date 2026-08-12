"""R136 regression (sv): bare "jul" is Christmas, not the month of July.

Swedish spells the month "juli"; "jul" alone is the everyday word for
Christmas ("jul", "juldagen", "god jul"). The MONTH vocab also lists "jul"
as an abbreviation so in-context abbreviated dates ("15. jul. 2026", "jul
2026") still read as July -- those two shapes bind a DAY or YEAR slot and
must be untouched by the fix. Anchor 2017-06-27 (from ``_corpus``):
Christmas 2017 = 25 Dec."""
from datetime import timedelta
from chronologia.extract import extract_recurrence
from ._corpus import ANCHOR, AstroDate, span, start


def test_bare_jul_is_christmas():
    assert start('jul') == AstroDate(2017, 12, 25)
    assert span('jul').width == timedelta(days=1)


def test_juldagen_unchanged():
    assert start('juldagen') == AstroDate(2017, 12, 25)


def test_juli_month_unchanged():
    s = span('juli')
    assert s.start == AstroDate(2017, 7, 1)
    assert s.end == AstroDate(2017, 8, 1)


def test_abbreviated_month_date_still_july():
    assert start('15. jul. 2026') == AstroDate(2026, 7, 15)


def test_jul_with_year_is_still_july():
    s = span('jul 2026')
    assert s.start == AstroDate(2026, 7, 1)
    assert s.end == AstroDate(2026, 8, 1)


def test_recurrence_until_jul_is_christmas():
    got = extract_recurrence('varje måndag till jul', 'sv', anchor=ANCHOR)
    assert got is not None
    assert got[0].until == AstroDate(2017, 12, 25)


def test_recurrence_until_december_unchanged():
    got = extract_recurrence('varje måndag till december', 'sv',
                              anchor=ANCHOR)
    assert got is not None
    assert got[0].until == AstroDate(2017, 12, 1)
