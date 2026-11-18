"""pt "ao fim da tarde" is the end of the afternoon, and "na hora" is no length.

"fim", "início" and "meio" before "da <part of the day>" keep the last, first
or middle third of the band, as they do for a month ("fim de março").  The
pt bands are the CLDR 47 ones: manhã 06:00-12:00, tarde 12:00-19:00, noite
19:00-24:00.  A third of the 7-hour tarde is 2 h 20 min, so the end of the
tarde is 16:40-19:00 and the middle is 14:20-16:40.  "no", "na", "nos" and
"nas" are "em" fused with the article (Priberam s.v. "na") and "os" and "as"
are plural articles, so none of them counts one unit: "na hora de ir" says
when, not how long.  Every instant is worked out by hand from the anchor,
Tuesday 2017-06-27 13:04.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_duration, extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

THIRDS = [
    ("ao fim da tarde", datetime(2017, 6, 27, 16, 40), datetime(2017, 6, 27, 19)),
    ("no fim da tarde", datetime(2017, 6, 27, 16, 40), datetime(2017, 6, 27, 19)),
    ("no final da tarde", datetime(2017, 6, 27, 16, 40), datetime(2017, 6, 27, 19)),
    ("no início da tarde", datetime(2017, 6, 27, 12), datetime(2017, 6, 27, 14, 20)),
    ("a meio da tarde", datetime(2017, 6, 27, 14, 20), datetime(2017, 6, 27, 16, 40)),
    ("no fim da manhã", datetime(2017, 6, 27, 10), datetime(2017, 6, 27, 12)),
    ("ao final da noite", datetime(2017, 6, 27, 22, 20), datetime(2017, 6, 28)),
    ("ao fim da tarde amanhã", datetime(2017, 6, 28, 16, 40), datetime(2017, 6, 28, 19)),
    ("amanhã ao fim da tarde", datetime(2017, 6, 28, 16, 40), datetime(2017, 6, 28, 19)),
]


@pytest.mark.parametrize("text,start,end", THIRDS)
def test_a_part_before_a_part_of_the_day_keeps_that_third(text, start, end):
    found = extract_timespan(text, "pt", ANCHOR)
    assert (found.span.start.datetime(), found.span.end.datetime()) == (start, end)
    assert found.remainder == ""


def test_the_reminder_sentence_keeps_the_end_of_the_afternoon():
    text = "não me deixes esquecer de comprar pão ao fim da tarde"
    found = extract_timespan(text, "pt", ANCHOR)
    assert found.span.start.datetime() == datetime(2017, 6, 27, 16, 40)
    assert found.remainder == "não me deixes esquecer de comprar pão"


@pytest.mark.parametrize("text", [
    "na hora", "no dia", "nos dias", "nas horas", "os dias", "as horas",
    "nos dias de semana às oito da manhã avisa-me que está na hora de ir trabalhar",
])
def test_a_contracted_or_plural_article_names_no_length(text):
    assert extract_duration(text, "pt", anchor=ANCHOR) is None


@pytest.mark.parametrize("text,expected", [
    ("a hora", timedelta(hours=1)),
    ("uma hora", timedelta(hours=1)),
    ("um dia", timedelta(days=1)),
    ("nas duas horas", timedelta(hours=2)),
    ("nos três dias", timedelta(days=3)),
])
def test_a_counted_unit_keeps_its_length(text, expected):
    found = extract_duration(text, "pt", anchor=ANCHOR)
    assert found.duration == expected
    assert found.remainder == ""


def test_the_weekday_alarm_keeps_its_clock():
    text = "nos dias de semana às oito da manhã avisa-me que está na hora de ir trabalhar"
    assert extract_timespan(text, "pt", ANCHOR).span.start.datetime() == datetime(2017, 6, 28, 8)
