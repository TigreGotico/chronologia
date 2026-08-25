"""The two unit words a Russian-shaped locale would get wrong.

Belarusian names the minute **хвіліна** and the hour **гадзіна**.  The Russian
cognates мінута and час are not the Belarusian words for them -- час in
particular means "time" in general, and in the hour sense is a documented
Russianism.  CLDR's ``dateFields`` displayName for be is literally "хвіліна"
and "гадзіна".

Every case is pinned in both directions: the Belarusian word reads, and the
Russian cognate does not silently read as the same unit.  A locale copied from
ru and lightly edited would pass the first half of this file and fail the
second.
"""
import pytest

from ._corpus import ANCHOR, parse, start, start_end


@pytest.mark.parametrize("text,minutes", [
    ("праз 1 хвіліну", 1), ("праз 3 хвіліны", 3), ("праз 5 хвілін", 5),
    ("праз 15 хвілін", 15), ("праз 30 хвілін", 30), ("праз 45 хвілін", 45),
])
def test_minute_is_hvilina(text, minutes):
    s = start(text)
    assert (s.hour * 60 + s.minute) - (ANCHOR.hour * 60 + ANCHOR.minute) == minutes


@pytest.mark.parametrize("text,hours", [
    ("праз 1 гадзіну", 1), ("праз 2 гадзіны", 2), ("праз 3 гадзіны", 3),
    ("праз 5 гадзін", 5), ("праз 10 гадзін", 10),
])
def test_hour_is_hadzina(text, hours):
    s = start(text)
    assert s.hour == (ANCHOR.hour + hours) % 24


@pytest.mark.parametrize("text", [
    "праз 5 мінут", "5 мінут таму", "праз 3 мінуты",
])
def test_the_russian_minute_is_not_a_belarusian_minute(text):
    """мінута is the Russian word.  It must not read as a minute offset --
    if it did, the locale was bootstrapped by translating ru."""
    r = parse(text)
    assert r is None or "мінут" in r[1]


@pytest.mark.parametrize("text", [
    "праз 5 часоў", "5 часоў таму", "праз тры часы",
])
def test_the_russian_hour_is_not_a_belarusian_hour(text):
    """час in the hour sense is a dialectal Russianism; it is not shipped, so
    a count of them names no offset."""
    r = parse(text)
    assert r is None or "час" in r[1]


@pytest.mark.parametrize("text,days", [
    ("праз 1 дзень", 1), ("праз 2 дні", 2), ("праз 5 дзён", 5),
    ("праз 21 дзень", 21),
])
def test_day_paucal_forms(text, days):
    """CLDR's four plural forms for дзень: дзень / дні / дзён / дня.  A
    count ending in 1 takes the singular, 2-4 the paucal дні, the rest the
    genitive plural дзён."""
    s, _ = start_end(text)
    assert (s.date() - ANCHOR.date()).days == days


@pytest.mark.parametrize("text,weeks", [
    ("праз 1 тыдзень", 1), ("праз 2 тыдні", 2), ("праз 5 тыдняў", 5),
])
def test_week_paucal_forms(text, weeks):
    s = start(text)
    assert (s.date() - ANCHOR.date()).days == weeks * 7


@pytest.mark.parametrize("text,months", [
    ("праз 1 месяц", 1), ("праз 3 месяцы", 3), ("праз 7 месяцаў", 7),
])
def test_month_paucal_forms(text, months):
    s = start(text)
    assert (s.year - ANCHOR.year) * 12 + s.month - ANCHOR.month == months


@pytest.mark.parametrize("text,years", [
    ("праз 1 год", 1), ("праз 2 гады", 2), ("праз 5 гадоў", 5),
    ("2 гады таму", -2), ("11 гадоў таму", -11), ("21 год таму", -21),
])
def test_year_paucal_forms(text, years):
    assert start(text).year == ANCHOR.year + years


@pytest.mark.parametrize("text,minutes", [
    ("5 хвілін таму", -5), ("20 хвілін таму", -20), ("1 хвіліну таму", -1),
])
def test_the_past_marker_is_tamu(text, minutes):
    """CLDR relativeTime-type-past is "{0} X таму"."""
    s = start(text)
    assert (s.hour * 60 + s.minute) - (ANCHOR.hour * 60 + ANCHOR.minute) == minutes


@pytest.mark.parametrize("text", ["5 хвілін назад", "5 хвілін тому"])
def test_the_russian_and_ukrainian_ago_markers_do_not_ship(text):
    r = parse(text)
    assert r is None or "хвілін" in r[1]
