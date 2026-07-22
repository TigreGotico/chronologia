"""Holiday references in Greek (``holiday_ref``), including the Orthodox
Easter cycle.

Anchor 2017-06-27. Greece observes Orthodox Easter (Gregorian): 2018 = 8 Apr,
2020 = 19 Apr; Orthodox Good Friday 2018 = 6 Apr, Orthodox Easter Monday 2018 =
9 Apr -- each hand-derived and independent of the Western computus. Fixed feasts
follow the Revised Julian (= Gregorian) calendar. Movable non-Christian dates
are the anchor-shared reference gold."""
from datetime import datetime, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import span, start, nomatch

A = datetime(2017, 6, 27, 13, 4)

def _start(t):
    return start(t, A)

_BARE = [
    ("χριστούγεννα", (2017, 12, 25)),
    ("παραμονή χριστουγέννων", (2017, 12, 24)),
    ("πρωτοχρονιά", (2018, 1, 1)),
    ("θεοφάνεια", (2018, 1, 6)),
    ("κοίμηση της θεοτόκου", (2017, 8, 15)),
    ("πάσχα", (2018, 4, 8)),
    ("κυριακή του πάσχα", (2018, 4, 8)),
    ("μεγάλη παρασκευή", (2018, 4, 6)),
    ("δευτέρα του πάσχα", (2018, 4, 9)),
    ("δεκαπενταύγουστος", (2017, 8, 15)),
]

@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert _start(text) == AstroDate(*ymd)
    assert span(text, A).width == timedelta(days=1)

@pytest.mark.parametrize("text,ymd", [
    ("επόμενο πάσχα", (2018, 4, 8)),
    ("προηγούμενο πάσχα", (2017, 4, 16)),
])
def test_next_last(text, ymd):
    assert _start(text) == AstroDate(*ymd)

@pytest.mark.parametrize("text,ymd", [
    ("χριστούγεννα 2020", (2020, 12, 25)),
    ("πάσχα 2020", (2020, 4, 19)),
])
def test_explicit_year(text, ymd):
    assert _start(text) == AstroDate(*ymd)

_EXPANDED = [
    ("εΐντ αλ φιτρ", (2018, 6, 15)),
    ("ραμαζάνι", (2018, 5, 16)),
    ("νορούζ", (2018, 3, 21)),
    ("ντιβάλι", (2017, 10, 19)),
    ("βεσάκ", (2018, 5, 29)),
    ("χαλοουίν", (2017, 10, 31)),
    ("αγίου βαλεντίνου", (2018, 2, 14)),
    ("κινέζικη πρωτοχρονιά", (2018, 2, 16)),
    ("πέσαχ", (2018, 3, 31)),
    ("χανουκά", (2017, 12, 13)),
]

@pytest.mark.parametrize("text,ymd", _EXPANDED)
def test_bare_expanded(text, ymd):
    assert _start(text) == AstroDate(*ymd)
    assert span(text, A).width == timedelta(days=1)

@pytest.mark.parametrize("text", [
    "η τιμή του ρυζιού ανέβηκε",
    "σύσκεψη για τον προϋπολογισμό",
    "ένα μπολ σούπα",
])
def test_no_holiday_no_match(text):
    nomatch(text, A)
