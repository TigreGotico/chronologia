"""Two overlaps the numbered calendar creates, and where each one lands.

``thứ hai`` is Monday and, read compositionally, "the second".  Georgian faces
the same shape with კვირა (Sunday and week) and settles it with a veto: a
count in front of the word cancels the weekday reading.  Vietnamese settles it
by LENGTH instead, because ``thứ`` is equally the ordinal marker: a weekday
name is ``thứ`` plus exactly one numeral word, so a numeral that runs longer
is an ordinal and never a day.  ``thứ hai`` is Monday, ``thứ hai mươi`` is the
twentieth, and a count in front of either still needs no veto -- ``thứ hai``
names no unit, so the count simply stays in the remainder.

``hôm kia`` and ``ngày kia`` are the sharper problem: a minimal pair, both
closing on ``kia``, pointing two days in OPPOSITE directions.  Only the head
noun separates them, and matching on ``kia`` alone would be four days wrong.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, remainder, start


@pytest.mark.parametrize("text,y,m,d", [
    ("thứ hai", 2017, 7, 3),
    ("thứ ba", 2017, 7, 4),
    ("thứ tư", 2017, 6, 28),
])
def test_thu_plus_number_is_a_weekday(text, y, m, d):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, m, d)
    assert remainder(text) == ""


@pytest.mark.parametrize("text", [
    "thứ hai", "thứ ba", "thứ tư", "thứ năm", "thứ sáu", "thứ bảy",
])
def test_a_weekday_span_is_one_whole_day(text):
    s = parse(text)[0]
    assert s.end - s.start == timedelta(days=1)


@pytest.mark.parametrize("text", ["thứ nhất", "thứ mười", "thứ mười hai"])
def test_a_bare_ordinal_names_no_date(text):
    """thứ nhất is "first" and thứ mười is "tenth", both well formed and
    neither a weekday -- there are only six numbered days.  A bare ordinal
    names no period on its own, so it resolves to nothing; it takes a scope
    noun beside it ("thế kỷ thứ hai mươi") to name one."""
    assert parse(text) is None


@pytest.mark.parametrize("text", [
    "thứ hai mươi", "thứ hai mươi mốt", "thứ ba mươi", "thứ hai mươi lăm",
])
def test_a_longer_numeral_after_thu_is_an_ordinal_not_a_weekday(text):
    """The collision the length rule settles.  Every one of these opens with
    the two words that spell Monday, and reading Monday out of them would
    answer a specific day for "the twentieth" and leave the rest of the
    numeral in the remainder.  None of them is a date on its own."""
    assert parse(text) is None


@pytest.mark.parametrize("text", ["hai thứ hai", "ba thứ ba", "2 thứ hai"])
def test_a_count_before_a_weekday_needs_no_veto(text):
    """Georgian vetoes the weekday reading when an unconsumed number precedes
    it, because there the same word is also a duration unit.  thứ hai is not
    a unit of anything, so the count simply stays in the remainder and the
    weekday still resolves -- the collision Georgian guards against does not
    arise, and no veto is wired."""
    r = parse(text)
    assert r is not None
    assert r[1] != ""


@pytest.mark.parametrize("text,offset", [
    ("hôm kia", -2),
    ("ngày kia", 2),
    ("ngày mốt", 2),
])
def test_the_kia_pair_points_in_opposite_directions(text, offset):
    assert start(text) == ad(ANCHOR.replace(hour=0, minute=0)
                             + timedelta(days=offset))


def test_the_kia_pair_is_four_days_apart():
    """The whole point of the pair: a fold keying on kia alone would collapse
    these two onto one date instead of separating them by four days."""
    before = start("hôm kia")
    after = start("ngày kia")
    assert (after.day - before.day) == 4


@pytest.mark.parametrize("text,offset", [
    ("hôm qua", -1),
    ("hôm nay", 0),
    ("ngày mai", 1),
])
def test_the_hom_and_ngay_heads_across_the_whole_series(text, offset):
    assert start(text) == ad(ANCHOR.replace(hour=0, minute=0)
                             + timedelta(days=offset))


@pytest.mark.parametrize("text", ["kia", "hôm", "ngày"])
def test_the_bare_pieces_name_no_day(text):
    assert parse(text) is None


@pytest.mark.parametrize("text,month", [
    ("tháng tư", 4),
    ("tháng 4", 4),
])
def test_april_uses_the_positional_four(text, month):
    """Month four is tháng tư, never tháng bốn -- the same substitution the
    ordinal series uses, reaching into the calendar."""
    assert start(text).month == month


def test_thang_bon_is_not_a_month():
    assert parse("tháng bốn") is None


@pytest.mark.parametrize("text,month", [
    ("tháng mười hai", 12),
    ("tháng 12", 12),
    ("tháng mười một", 11),
])
def test_a_longer_numeral_after_thang_still_names_its_month(text, month):
    """The same length rule runs over the month head, where the long numeral
    IS the name: CLDR spells every month in digits too, so December reads the
    same written out as it does as "tháng 12"."""
    assert start(text).month == month
