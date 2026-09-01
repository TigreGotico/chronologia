# -*- coding: utf-8 -*-
"""The year noun ``ปี`` must never bind without a year of its own.

``calendar_date`` used to write the noun and the numeral as two independently
optional slots (``year_word? YEAR?``), so a phrase that carries the noun but
no numeral let it bind for nothing while the numeral slot matched empty. The
construction reported a complete, confident date with the noun silently gone
from the remainder. The noun must now either refuse to bind or stay visible
in the remainder.
"""
from ._corpus import parse, start


def test_the_year_word_does_not_bind_without_a_numeral_after_it():
    r = parse("วันที่ 10 ตุลาคม ปี")
    assert r is not None, "expected the date without the dangling noun"
    assert "ปี" in r[1], (
        f"'ปี' must not be silently absorbed; remainder was {r[1]!r}")


def test_a_bare_numeral_year_still_works_without_the_noun():
    s = start("20 มกราคม 2026")
    assert (s.year, s.month, s.day) == (2026, 1, 20)


def test_the_month_only_order_resolves_the_year_word_variant():
    span, remainder_ = parse("ตุลาคม ปี 2020")
    assert (span.start.year, span.start.month) == (2020, 10)
    assert remainder_ == "", f"expected an empty remainder, got {remainder_!r}"


def test_the_month_only_order_still_dangles_the_noun_without_a_numeral():
    r = parse("วันที่ 10 ตุลาคม ปี")
    assert r is not None
    assert "ปี" in r[1]
    r2 = parse("ตุลาคม ปี")
    assert r2 is not None, "expected the month without the dangling noun"
    assert "ปี" in r2[1], (
        f"'ปี' must not be silently absorbed; remainder was {r2[1]!r}")
