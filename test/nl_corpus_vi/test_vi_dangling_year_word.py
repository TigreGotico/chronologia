"""The year noun ``năm`` must never bind without a year of its own.

``calendar_date`` used to write the noun and the numeral as two independently
optional slots (``year_word? YEAR?``), so a phrase that carries the noun but
no numeral let it bind for nothing while the numeral slot matched empty. The
construction reported a complete, confident date with the noun silently gone
from the remainder. The noun must now either refuse to bind or stay visible
in the remainder.
"""
from ._corpus import parse, start


def test_the_year_word_does_not_bind_without_a_numeral_after_it():
    r = parse("ngày 10 tháng 10 năm")
    assert r is not None, "expected the date without the dangling noun"
    assert "năm" in r[1], (
        f"'năm' must not be silently absorbed; remainder was {r[1]!r}")


def test_the_year_word_does_not_bind_without_a_numeral_after_it_month_only():
    r = parse("tháng 10 năm")
    assert r is not None, "expected the month without the dangling noun"
    assert "năm" in r[1], (
        f"'năm' must not be silently absorbed; remainder was {r[1]!r}")


def test_the_year_word_still_works_with_a_numeral_year_attached():
    s = start("5 tháng 3 năm 2020")
    assert (s.year, s.month, s.day) == (2020, 3, 5)


def test_no_year_at_all_still_resolves_against_the_anchor():
    # anchor is 2017-06-27; a bare month reference with no year at all takes
    # the anchor's own year, 2017, and the first day of that month.
    s = start("tháng tư")
    assert (s.year, s.month, s.day) == (2017, 4, 1)
