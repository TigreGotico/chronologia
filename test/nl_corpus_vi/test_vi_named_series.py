"""Two overlaps the numbered calendar creates, and where each one lands.

``thứ hai`` is Monday and, read compositionally, "the second".  Georgian faces
the same shape with კვირა (Sunday and week) and settles it with a veto: a
count in front of the word cancels the weekday reading.  Vietnamese needs no
such veto, because the ordinal reading is never reachable -- the locale ships
no ordinal series at all, so ``thứ`` plus a number populates the weekday slot
and nothing else, and no construction puts a count in front of it.  Both
halves of that are pinned here, so the day anyone adds ordinals this file says
what has to be reconsidered.

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
def test_no_ordinal_series_ships(text):
    """thứ nhất is "first" and thứ mười is "tenth", both well formed and
    neither a weekday -- there are only six numbered days.  With no ordinal
    vocabulary they resolve to nothing, which is the honest answer; inventing
    a reading here is what would make the weekday collision real."""
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
