# -*- coding: utf-8 -*-
"""A dotted clock beside a clock word reads as the colon clock does.

Writers of es, nl and de use the dot for the colon: Spanish "18.20" is the
older form that the press still uses (Wikipedia, "Date and time notation in
Spain"), Dutch writes "22.51 uur" (Wikipedia, "Date and time notation in the
Netherlands"), and German DIN 1355 and DIN 5008 set the dot as the separator
until 1995 (Wikipedia, "Date and time notation in Europe", Germany).  The
rows for pt, it, ca, gl and fr follow the issue; no source for them was
checked, and a native reviewer is to confirm them.

The dot also marks a price or a list number, so the clock needs a clock word
before it ("a las", "um", "om") or after it ("Uhr", "horas"), and a counted
noun after it makes a count.  A dotted date and a bare number stay unread.
The hour reads as the colon clock does (ruling 23: the next of its two
twelve-hour readings), and a clock with a leading zero, a 24-hour hour or a
part of the day reads as written.

Every expected instant is worked out by hand from the anchor.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

NOON = datetime(2026, 9, 25, 12, 0)
EARLY = datetime(2026, 9, 25, 6, 0)

# text, language: the next 8:30 or 8:15 after 12:00 on the 25th is the evening
EVENING_READING = [
    ("a las 8.30", "es", datetime(2026, 9, 25, 20, 30)),
    ("a las 8.15", "es", datetime(2026, 9, 25, 20, 15)),
    ("às 8.30", "pt", datetime(2026, 9, 25, 20, 30)),
    ("às 8.15", "pt", datetime(2026, 9, 25, 20, 15)),
    ("um 8.15", "de", datetime(2026, 9, 25, 20, 15)),
    ("um 8.15 Uhr", "de", datetime(2026, 9, 25, 20, 15)),
    ("8.30 Uhr", "de", datetime(2026, 9, 25, 20, 30)),
    ("alle 8.30", "it", datetime(2026, 9, 25, 20, 30)),
    ("à 8.15", "fr", datetime(2026, 9, 25, 20, 15)),
    ("om 8.30", "nl", datetime(2026, 9, 25, 20, 30)),
    ("a les 8.30", "ca", datetime(2026, 9, 25, 20, 30)),
    ("ás 8.30", "gl", datetime(2026, 9, 25, 20, 30)),
    ("às 8.30 horas", "pt", datetime(2026, 9, 25, 20, 30)),
]

# text, language, expected instant: a part of the day beside the clock decides
# the half, and the part of the day joins the clock, as with the colon
DAYPART_READING = [
    ("a las 8.30 de la tarde", "es", datetime(2026, 9, 25, 20, 30)),
    ("a las 8.30 de la noche", "es", datetime(2026, 9, 25, 20, 30)),
    ("a las 8.30 de la mañana", "es", datetime(2026, 9, 26, 8, 30)),
    ("às 8.30 da noite", "pt", datetime(2026, 9, 25, 20, 30)),
    ("às 8.30 da manhã", "pt", datetime(2026, 9, 26, 8, 30)),
    ("alle 8.30 di sera", "it", datetime(2026, 9, 25, 20, 30)),
    ("alle 8.30 di mattina", "it", datetime(2026, 9, 26, 8, 30)),
    ("à 8.30 du soir", "fr", datetime(2026, 9, 25, 20, 30)),
    ("à 8.30 du matin", "fr", datetime(2026, 9, 26, 8, 30)),
    ("om 8.30 's avonds", "nl", datetime(2026, 9, 25, 20, 30)),
    ("a les 8.30 de la tarda", "ca", datetime(2026, 9, 25, 20, 30)),
    ("ás 8.30 da tarde", "gl", datetime(2026, 9, 25, 20, 30)),
    ("um 8.30 Uhr abends", "de", datetime(2026, 9, 25, 20, 30)),
]

# the clock written as it is spoken in the morning, said at 06:00
EARLY_READING = [
    ("a las 8.30", "es", datetime(2026, 9, 25, 8, 30)),
    ("às 8.15", "pt", datetime(2026, 9, 25, 8, 15)),
    ("om 8.30", "nl", datetime(2026, 9, 25, 8, 30)),
]

# text, language, expected instant: the written hour stands
AS_WRITTEN = [
    ("a las 08.30", "es", datetime(2026, 9, 26, 8, 30)),
    ("a las 15.30", "es", datetime(2026, 9, 25, 15, 30)),
    ("às 8.30 da manhã", "pt", datetime(2026, 9, 26, 8, 30)),
    ("amanhã às 8.30", "pt", datetime(2026, 9, 26, 8, 30)),
    ("um 20.15 Uhr", "de", datetime(2026, 9, 25, 20, 15)),
    ("at 8.30", "en", datetime(2026, 9, 26, 8, 30)),
    ("kello 8.30", "fi", datetime(2026, 9, 26, 8, 30)),
]

# a price, a count or a bare number is no clock
NO_CLOCK = [
    ("8.30", "es"), ("8.30", "pt"), ("8.30", "it"), ("8.15", "fr"),
    ("8.30", "nl"), ("8.30", "ca"), ("8.30", "gl"), ("8.30", "de"),
    ("cuesta 8.30 euros", "es"),
    ("vende a 8.30 euros", "es"),
    ("a 8.30", "es"),
    ("a las 8.30 euros", "es"),
    ("às 8.30 euros", "pt"),
    ("alle 8.30 euro", "it"),
    ("à 8.15 euros", "fr"),
    ("om 8.30 euro", "nl"),
    ("a les 8.30 euros", "ca"),
    ("ás 8.30 euros", "gl"),
    ("um 8.30 Euro", "de"),
    ("8.3.2026", "es"),
    ("8.3.2026", "fr"),
]


@pytest.mark.parametrize("text,lang,expected", EVENING_READING)
def test_a_dotted_clock_takes_the_next_twelve_hour_reading(text, lang,
                                                           expected):
    found = extract_timespan(text, lang, NOON)
    assert found.span.start.datetime() == expected
    assert found.remainder == ""


@pytest.mark.parametrize("text,lang,expected", DAYPART_READING)
def test_a_part_of_the_day_joins_a_dotted_clock(text, lang, expected):
    found = extract_timespan(text, lang, NOON)
    assert found.span.start.datetime() == expected
    assert found.remainder == ""


@pytest.mark.parametrize("text,lang,expected", EARLY_READING)
def test_a_dotted_clock_said_early_keeps_the_morning_hour(text, lang, expected):
    assert extract_timespan(text, lang, EARLY).span.start.datetime() == expected


@pytest.mark.parametrize("text,lang,expected", AS_WRITTEN)
def test_a_marked_dotted_clock_reads_as_written(text, lang, expected):
    assert extract_timespan(text, lang, NOON).span.start.datetime() == expected


@pytest.mark.parametrize("text,lang", NO_CLOCK)
def test_a_price_a_count_or_a_bare_number_is_no_clock(text, lang):
    assert extract_timespan(text, lang, NOON) is None


def test_a_dotted_date_is_a_date_and_no_clock():
    found = extract_timespan("8.3.2026", "de", NOON)
    assert found.span.start.datetime() == datetime(2026, 3, 8)
    assert found.span.end.datetime() == datetime(2026, 3, 9)
