"""A range reading carries one reading per bound, with the exact words the
bound reads.

The expected words are the ones that name each bound in the phrase, and the
expected characters are found in the text with ``str.find``.  A word between
the bound's words that the bound does not read is not claimed: the German
endpoint "jeden Montag von Juni" reads "Montag" and "Juni", not "von".  An
open range has one bound.

Anchor 2026-11-22 09:00, a Sunday: June is June 2027, August is August 2027
and the next Friday is 2026-11-27.
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate
from chronologia.extract.reading import read
from chronologia.extract.timespan import extract_timespan

ANCHOR = datetime(2026, 11, 22, 9, 0)


def words(text, bound):
    return [text[t.char_start:t.char_end] for t in bound.tokens
            if t.index in bound.claimed]


def chars(text, first, last):
    return text.find(first), text.find(last) + len(last)


@pytest.mark.parametrize("lang, text, left, right", [
    ("en", "from june until august", ["june"], ["august"]),
    ("en", "every friday until june", ["friday"], ["june"]),
    ("en", "between monday and friday", ["monday"], ["friday"]),
    ("en", "from 9am to 5pm", ["9", "am"], ["5", "pm"]),
    ("pt", "de 3 de junho até 5 de agosto", ["3", "de", "junho"],
     ["5", "de", "agosto"]),
    # the bare day borrows the month of the right bound and reads only "5"
    ("es", "del 5 al 12 de junio", ["5"], ["12", "de", "junio"]),
    ("de", "jeden Montag von Juni bis August", ["Montag", "Juni"],
     ["August"]),
    # the left bound does not claim the am/pm word that it borrows
    ("en", "between eleven and one pm", ["eleven"], ["one", "pm"]),
])
def test_a_closed_range_carries_both_bounds(lang, text, left, right):
    span = read(text, lang, ANCHOR, first=True)[0]
    assert span.kind == "span"
    assert (words(text, span.left), words(text, span.right)) == (left, right)
    assert span.left.chars == chars(text, left[0], left[-1])
    assert span.right.chars == chars(text, right[0], right[-1])


def test_a_bound_reads_its_own_words():
    span = read("every friday until june", "en", ANCHOR, first=True)[0]
    assert (span.left.span.start, span.left.span.end) == (
        AstroDate(2026, 11, 27), AstroDate(2026, 11, 28))
    assert (span.right.span.start, span.right.span.end) == (
        AstroDate(2027, 6, 1), AstroDate(2027, 7, 1))


@pytest.mark.parametrize("text, left, right", [
    ("until june", None, ["june"]),
    ("since 2019", ["2019"], None),
])
def test_an_open_range_carries_one_bound(text, left, right):
    span = read(text, "en", ANCHOR, first=True)[0]
    assert span.construction == "open_range"
    got = [None if b is None else words(text, b)
           for b in (span.left, span.right)]
    assert got == [left, right]


def test_a_point_and_a_bare_now_carry_no_bound():
    for text in ("next friday", "now"):
        got = read(text, "en", ANCHOR, first=True)[0]
        assert (got.left, got.right) == (None, None)


def test_the_bare_day_claims_its_own_words_only():
    text = "from the 5th to the 12th of june"
    span = read(text, "en", ANCHOR, first=True)[0]
    assert words(text, span.left) == ["the", "5", "th"]
    assert words(text, span.right) == ["the", "12", "th", "of", "june"]
    assert span.left.chars == (text.find("the 5th"), text.find("5th") + 3)
    assert span.right.chars == (text.find("the 12th"), len(text))


def test_an_affix_bound_claims_its_whole_word_and_reads_its_stem():
    text = "péntekig"
    span = read(text, "hu", ANCHOR, first=True)[0]
    assert span.left is None
    assert words(text, span.right) == ["péntekig"]
    assert span.right.chars == (0, len("péntek"))


def test_the_borrowed_meridiem_leaves_the_span_unchanged():
    text = "between eleven and one pm"
    span = read(text, "en", ANCHOR, first=True)[0]
    assert span.left.chars == (8, 14)
    assert span.chars == (0, len(text))


def alone(text, lang, anchor=ANCHOR):
    return extract_timespan(text, lang, anchor).span


def test_a_bound_span_is_the_endpoint_read_alone():
    # "dia 3" rolls back to 3 November in the range; alone it is 3 December
    span = read("do dia 3 até hoje", "pt", ANCHOR, first=True)[0]
    assert span.left.span == alone("dia 3", "pt")
    assert span.right.span == alone("hoje", "pt")


@pytest.mark.parametrize("text", [
    "since monday until friday",
    "since noon until today saturday",
])
def test_a_since_until_right_bound_ends_the_range(text):
    span = read(text, "en", ANCHOR, first=True)[0]
    assert span.right.span.end == span.span.end
