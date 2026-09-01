"""The year noun ``taong`` must never bind without a year of its own.

``calendar_date`` used to write the noun and the numeral as two independently
optional slots (``year_word? YEAR?``), so a phrase that carries the noun but
no numeral -- an utterance cut off mid-sentence, or a caller who forgot the
number -- let the noun bind for nothing while the numeral slot matched empty.
The construction reported a complete, confident date with the noun silently
gone from the remainder, and the caller had no way to know a year had been
asked for but never supplied.  The noun must now either refuse to bind or
stay visible in the remainder.
"""
from ._corpus import parse, remainder, start


def test_the_year_word_does_not_bind_without_a_numeral_after_it():
    r = parse("ika-10 ng Oktubre taong")
    assert r is not None, "expected the date without the dangling noun"
    assert "taong" in r[1], (
        f"'taong' must not be silently absorbed; remainder was {r[1]!r}")


def test_the_year_word_does_not_bind_without_a_numeral_after_it_month_only():
    r = parse("Oktubre taong")
    assert r is not None, "expected the month without the dangling noun"
    assert "taong" in r[1], (
        f"'taong' must not be silently absorbed; remainder was {r[1]!r}")


def test_the_year_word_still_works_with_a_spelled_year_attached():
    s = start("ika-isa ng Abril taong dalawang libo't dalawampu't dalawa")
    assert (s.year, s.month, s.day) == (2022, 4, 1)


def test_a_bare_numeral_year_still_works_without_the_noun():
    s = start("ika-24 ng Agosto 2026")
    assert (s.year, s.month, s.day) == (2026, 8, 24)


def test_the_dangling_linker_ng_does_not_bind_without_a_meridiem():
    r = parse("alas-3 ng")
    assert r is not None, "expected the hour without the dangling linker"
    assert r[0].start.hour == 3
    assert "ng" in r[1], (
        f"'ng' must not be silently absorbed; remainder was {r[1]!r}")


def test_the_linker_and_meridiem_still_work_together():
    s = start("alas-3 ng hapon")
    assert s.hour == 15

    remainder_ = remainder("alas-3 ng hapon")
    assert remainder_ == "", f"expected an empty remainder, got {remainder_!r}"


def test_the_ika_form_already_refused_the_dangling_linker():
    r = parse("ika-3 ng")
    assert r is None, (
        f"a dangling 'ng' linker must not silently resolve; got {r!r}")
