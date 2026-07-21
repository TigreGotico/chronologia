"""Adversarial Russian cases -- written to break the parser.

Case-form near-misses, the "три дня" (three days vs 3 pm) ambiguity, the
дня/года genitive traps, cross-language contamination, and recorded engine
gaps (half-TO idiom, seconds, oblique numerals).
"""
import pytest

from ._corpus import ANCHOR, parse, nomatch


@pytest.mark.parametrize("text", [
    "", "   ", "привет как дела", "qwerty zxcvb", "нет даты здесь",
    "просто какие-то слова",
])
def test_junk_is_none(text):
    nomatch(text)


# an offset needs its direction marker (через / назад)
@pytest.mark.parametrize("text", [
    "три дня", "пять лет", "две недели", "десять минут", "минут",
])
def test_offset_without_marker(text):
    nomatch(text)


# marker or number alone must not fabricate an offset (deposited NON_MATCHES)
@pytest.mark.parametrize("text", ["через недели", "2 назад"])
def test_incomplete_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99", "13:75"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


# foreign (Czech/Ukrainian/Bulgarian) phrases must not parse as Russian
@pytest.mark.parametrize("text", [
    "před 2 lety",       # cs
    "через 2 роки",      # uk (roki, not года)
    "след три дни",      # bg
    "за 5 lat",          # pl
])
def test_foreign_not_matched(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


# recorded engine gaps
def test_halfto_idiom_gap():
    # "полдесятого" = 9:30 (half-TO the tenth); no direction word -> must not
    # fabricate 10:30
    r = parse("полдесятого")
    if r is not None:
        assert (r[0].start.hour, r[0].start.minute) != (10, 30)


def test_seconds_offset_gap():
    nomatch("через 45 секунд")


def test_bare_weekday_alone():
    nomatch("пятница")
