"""The Finnish clock separator is the PERIOD, not the colon.

Kielikello's rule on writing clock times prescribes it -- "kellonajan tunnit
ja minuutit erotetaan toisistaan pisteellä", with "klo 9.15" as the worked
example -- and CLDR 47's fi short time pattern is "H.mm".  The locale used to
read only "15:30"; "15.30" split into two bare numbers and nothing matched.

The period is also Finnish's date separator and ordinal marker, so the pins
below check that "3.6.2020" is still a date, "15. elokuuta" still an ordinal
day, and a thousands group is still a number.

Anchor: Tuesday 2017-06-27 13:04.  prefer_future rolls a wall time already
past today to tomorrow.
"""
import pytest

from ._corpus import ANCHOR, ad, parse


def _consumed(text):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r[1] == "", f"{text!r} stranded {r[1]!r}"
    return r[0]


@pytest.mark.parametrize("text,y,mo,d,h,mi", [
    ("klo 9.15", 2017, 6, 28, 9, 15),      # 09:15 < 13:04 -> tomorrow
    ("kello 15.30", 2017, 6, 27, 15, 30),  # 15:30 > 13:04 -> today
    ("15.30", 2017, 6, 27, 15, 30),
    ("9.15", 2017, 6, 28, 9, 15),
    ("23.59", 2017, 6, 27, 23, 59),
    ("0.05", 2017, 6, 28, 0, 5),
])
def test_dotted_clock(text, y, mo, d, h, mi):
    s = _consumed(text)
    assert s.start == ad(ANCHOR.replace(year=y, month=mo, day=d, hour=h,
                                        minute=mi, second=0, microsecond=0))


def test_hour_word_is_consumed():
    """"kello"/"klo" belongs to the clock it introduces, colon form included."""
    for text in ("kello 15:30", "klo 15:30", "kello 15.30"):
        s = _consumed(text)
        assert (s.start.hour, s.start.minute) == (15, 30), text


@pytest.mark.parametrize("text,h,mi", [
    ("15:30", 15, 30),
    ("09:15", 9, 15),
])
def test_colon_clock_unchanged(text, h, mi):
    s = _consumed(text)
    assert (s.start.hour, s.start.minute) == (h, mi)


def test_dotted_date_still_a_date():
    s = _consumed("3.6.2020")
    assert (s.start.year, s.start.month, s.start.day) == (2020, 6, 3)
    assert (s.start.hour, s.start.minute) == (0, 0)


def test_spaced_dotted_date_still_a_date():
    s = _consumed("15. 6. 2020")
    assert (s.start.year, s.start.month, s.start.day) == (2020, 6, 15)


def test_ordinal_day_still_an_ordinal():
    s = _consumed("15. elokuuta 2020")
    assert (s.start.year, s.start.month, s.start.day) == (2020, 8, 15)


@pytest.mark.parametrize("text", ["15.70", "25.30", "99.99"])
def test_out_of_range_is_no_clock(text):
    assert parse(text) is None, text


def test_thousands_group_is_still_a_number():
    """"1.000" is a thousands group in a comma-decimal locale, and three
    digits after the dot are not a minute -- it must not become a time."""
    assert parse("1.000") is None


@pytest.mark.xfail(reason="a trailing dot makes the run a truncated dotted "
                          "date ('15.06.'), which the date rules refuse; the "
                          "sentence-final clock is refused with it",
                   strict=True)
def test_sentence_final_dotted_clock():
    assert parse("kello 15.30.") is not None
