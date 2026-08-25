"""The date line, the months and weekdays, the seasons, and ranges.

The date runs day, month, year -- little-endian, and written in digits it is
period-separated with the abbreviation "г." trailing the year, which is what
CLDR states for every one of its date formats.  Month names are borrowed Latin
and take no ending; weekday names are Slavic.
"""
import pytest

from ._corpus import ANCHOR, day, nomatch, parse, remainder, span, start_end

MONTHS = ["јануари", "февруари", "март", "април", "мај", "јуни", "јули",
          "август", "септември", "октомври", "ноември", "декември"]


@pytest.mark.parametrize("n,name", list(enumerate(MONTHS, 1)))
def test_every_month_name(n, name):
    s = span(f"5 {name} 2028")
    assert (s.start.year, s.start.month, s.start.day) == (2028, n, 5)


@pytest.mark.parametrize("n,name", list(enumerate(
    ["јан", "фев", "мар", "апр", "мај", "јун", "јул", "авг", "сеп", "окт",
     "ное", "дек"], 1)))
def test_every_month_abbreviation(n, name):
    s = span(f"5 {name} 2028")
    assert (s.start.year, s.start.month, s.start.day) == (2028, n, 5)


@pytest.mark.parametrize("text,expect", [
    ("5 јуни 2027", (2027, 6, 5)),
    ("5 јуни", (2027, 6, 5)),
    ("1 јануари 2030", (2030, 1, 1)),
    ("25 декември 2020", (2020, 12, 25)),
    ("15 август 2027", (2027, 8, 15)),
    ("29 февруари 2028", (2028, 2, 29)),
])
def test_the_date_runs_day_month_year(text, expect):
    assert start_end(text) == day(*expect)


@pytest.mark.parametrize("text,expect", [
    ("5.6.2027", (2027, 6, 5)),
    ("05.06.2027", (2027, 6, 5)),
    ("25.12.2020", (2020, 12, 25)),
])
def test_the_numeric_date_is_little_endian(text, expect):
    assert start_end(text) == day(*expect)


def test_the_month_is_never_read_first():
    # 5.6 is the fifth of June; a month-first reading would answer the sixth
    # of May, which is a date this locale must never return for that string.
    assert start_end("5.6.2027") == day(2027, 6, 5)


@pytest.mark.parametrize("text,year", [
    ("2027 г", 2027), ("1918 г", 1918), ("2027", 2027), ("1918", 1918),
])
def test_the_year_with_and_without_its_abbreviation(text, year):
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (year, 1, 1)


@pytest.mark.parametrize("text,y,m", [
    ("јуни 2027", 2027, 6), ("декември 2027", 2027, 12),
    ("јануари 2030", 2030, 1),
])
def test_a_bare_month_and_year(text, y, m):
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (y, m, 1)


WEEKDAYS = ["понеделник", "вторник", "среда", "четврток", "петок", "сабота",
            "недела"]


@pytest.mark.parametrize("n,name", list(enumerate(WEEKDAYS)))
def test_every_weekday_name(n, name):
    # The anchor is a Wednesday; следен picks each weekday's next occurrence.
    s = span(f"следниот {name}") if name in ("понеделник", "вторник",
                                             "четврток", "петок") \
        else span(f"следната {name}")
    assert s.start.weekday() == n


@pytest.mark.parametrize("text,expect", [
    ("од 5 јуни до 8 јуни", ((2027, 6, 5), (2027, 6, 9))),
    ("меѓу 5 јуни и 8 јуни", ((2027, 6, 5), (2027, 6, 9))),
    ("од понеделник до петок", ((2027, 5, 17), (2027, 5, 22))),
])
def test_a_closed_range(text, expect):
    assert start_end(text) == (day(*expect[0])[0], day(*expect[1])[0])


def test_until_opens_the_range_at_the_anchor():
    s = span("до 8 јуни")
    assert (s.start.year, s.start.month, s.start.day) == (2027, 5, 12)
    assert (s.end.year, s.end.month, s.end.day) == (2027, 6, 9)


@pytest.mark.parametrize("text,months", [
    ("пролет", (3, 6)), ("лето", (6, 9)), ("есен", (9, 12)),
])
def test_the_seasons(text, months):
    s = span(text)
    assert (s.start.month, s.end.month) == months


def test_winter_crosses_the_year():
    s = span("зима")
    assert (s.start.year, s.start.month) == (2027, 12)
    assert (s.end.year, s.end.month) == (2028, 3)


@pytest.mark.parametrize("text,expect", [
    ("викенд", ((2027, 5, 15), (2027, 5, 17))),
    ("овој викенд", ((2027, 5, 15), (2027, 5, 17))),
    ("следниот викенд", ((2027, 5, 22), (2027, 5, 24))),
])
def test_the_weekend(text, expect):
    assert start_end(text) == (day(*expect[0])[0], day(*expect[1])[0])
