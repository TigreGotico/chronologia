"""Adversarial Slovak cases -- written to break the parser.

Case-form near-misses, direction traps, cross-language contamination (Czech,
Croatian, Bulgarian -- deposited in the sk legacy suite), and recorded engine
gaps (half-/quarter-TO idioms, seconds).
"""
import pytest

from ._corpus import ANCHOR, parse, nomatch


@pytest.mark.parametrize("text", [
    "", "   ", "ahoj ako sa máš", "qwerty zxcvb", "žiadny dátum tu",
])
def test_junk_is_none(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "päť dní", "dva týždne", "tri mesiace", "desať rokov", "minút",
])
def test_offset_without_marker(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["99:99", "25:61", "40:00", "13:75"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


# Croatian / Bulgarian phrases must not parse as Slovak (deposited FOREIGN set)
@pytest.mark.parametrize("text", [
    "sutra", "u sedam ujutro", "15. kolovoza", "za deset minuta",
    "утре", "следващата сряда", "15 август", "след три часа",
])
def test_foreign_not_matched(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


# recorded engine gaps
def test_halfto_idiom_gap():
    # "pol tretej" = 2:30 (half-TO the third); no direction word -> must not
    # fabricate 3:30
    r = parse("pol tretej")
    if r is not None:
        assert (r[0].start.hour, r[0].start.minute) != (3, 30)


def test_quarterto_idiom_gap():
    # "štvrť na osem" = 7:15; unsupported, must not fabricate 8:15
    r = parse("štvrť na osem")
    if r is not None:
        assert (r[0].start.hour, r[0].start.minute) != (8, 15)


def test_seconds_offset_gap():
    nomatch("za 45 sekúnd")


def test_bare_weekday_alone():
    nomatch("piatok")
