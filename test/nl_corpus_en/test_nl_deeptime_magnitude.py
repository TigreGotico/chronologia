"""Indefinite-article deep-time magnitudes ("a billion years ago").

Spoken, colloquial deep time introduced by the *indefinite* article -- "a
million years ago", "a billion years ago", "a hundred thousand years ago" --
is a plain count-from-now offset, not the geological Before-Present
measurement the numeral form carries ("66 million years ago").  So it
resolves to a single-year POINT at ``anchor.year - count*scale``, never a
scale-wide span, and never drops the scale word.

The numeral / spelled-cardinal deep-time path ("66 million", "sixty-six
million", "2 million", "10 thousand", "two thousand") is the geological
Before-Present convention and is deliberately left untouched here -- its
sig-fig span behaviour is pinned in ``test_nl_eras_deep_time.py`` and
``test_nl_spelled_cardinal_fraction.py``.
"""
import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start_end


# -- article magnitude -> single-year POINT at anchor.year - count*scale ---
@pytest.mark.parametrize("text,value", [
    ("a thousand years ago", 1_000),
    ("a million years ago", 1_000_000),
    ("a billion years ago", 1_000_000_000),
    ("a trillion years ago", 1_000_000_000_000),
    ("a hundred thousand years ago", 100_000),
    ("an billion years ago", 1_000_000_000),  # article variant
])
def test_article_magnitude_is_a_point(text, value):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    s, e = r[0].start, r[0].end
    # the scale word is consumed, not stranded
    assert not r[1].strip(), f"{text!r} stranded remainder {r[1]!r}"
    # anchor-relative point, month/day carried from the anchor
    assert s.year == ANCHOR.year - value
    assert (s.month, s.day) == (ANCHOR.month, ANCHOR.day)
    # a POINT: one civil year wide, NOT a scale-wide span
    assert e.year - s.year == 1


def test_article_billion_matches_probe_value():
    # 2017 - 1_000_000_000
    assert span("a billion years ago").start.year == -999_997_983


def test_article_million_matches_probe_value():
    assert span("a million years ago").start.year == -997_983


# -- regression pins: the numeral / geological path stays byte-identical ----
def test_hundred_years_ago_still_civil():
    # "a hundred" composes to 100 and stays a plain civil offset (1917)
    assert span("a hundred years ago").start == AstroDate(1917, 6, 27, 13, 4)


def test_66_million_still_before_present_span():
    s, e = start_end("66 million years ago")
    assert s.year == 1950 - 66_000_000
    assert e.year - s.year == 1_000_000     # sig-fig span, unchanged


def test_two_thousand_still_before_present():
    # spelled numeral routes to the Before-Present convention, unchanged
    assert span("two thousand years ago").start == AstroDate(-50, 1, 1)


def test_10_thousand_still_sigfig_span():
    s, e = start_end("10 thousand years ago")
    assert e.year - s.year == 1_000
