"""The Hausa date line: day, *ga*, month, year -- and the month's linked form."""
import pytest

from ._corpus import day, month_span, nomatch, remainder, start_end, year_span


#: CLDR wide name, CLDR abbreviation, the genitive-linked form written
#: inside "watan <month>", and the month number.
MONTHS = [
    ("Janairu", "Jan", "Janairun", 1),
    ("Faburairu", "Fab", "Fabrairun", 2),
    ("Maris", "Mar", None, 3),
    ("Afirilu", "Afi", "Afirilun", 4),
    ("Mayu", "May", "Mayun", 5),
    ("Yuni", "Yun", "Yunin", 6),
    ("Yuli", "Yul", "Yulin", 7),
    ("Agusta", "Agu", "Agustan", 8),
    ("Satumba", "Sat", "Satumban", 9),
    ("Oktoba", "Okt", "Oktoban", 10),
    ("Nuwamba", "Nuw", "Nuwamban", 11),
    ("Disamba", "Dis", "Disamban", 12),
]


@pytest.mark.parametrize("wide,abbr,linked,n", MONTHS)
def test_the_wide_month_name_reads(wide, abbr, linked, n):
    assert start_end(f"15 ga {wide} 2027") == day(2027, n, 15)


@pytest.mark.parametrize("wide,abbr,linked,n", MONTHS)
def test_the_abbreviated_month_name_reads(wide, abbr, linked, n):
    """CLDR abbreviates February as Fab and September as Sat, not Feb and Sep."""
    assert start_end(f"15 ga {abbr} 2027") == day(2027, n, 15)


@pytest.mark.parametrize(
    "wide,abbr,linked,n", [m for m in MONTHS if m[2] is not None])
def test_the_linked_month_name_reads_after_the_month_noun(wide, abbr, linked, n):
    """A month name leaned on by "watan" takes a genitive -n."""
    assert start_end(f"15 ga watan {linked} 2027") == day(2027, n, 15)


def test_maris_takes_no_linker():
    """Maris ends in a consonant and stays bare inside the same frame."""
    assert start_end("15 ga watan Maris 2027") == day(2027, 3, 15)


@pytest.mark.parametrize("text,expected", [
    ("5 ga Yuni 2027", (2027, 6, 5)),
    ("25 ga Disamba 2020", (2020, 12, 25)),
    ("1 ga Janairu 2030", (2030, 1, 1)),
    ("29 ga Faburairu 2028", (2028, 2, 29)),
    ("31 ga Disamba 1999", (1999, 12, 31)),
    ("10 ga watan Oktoban 2022", (2022, 10, 10)),
    ("21 ga watan Afirilu 1926", (1926, 4, 21)),
])
def test_the_date_line_runs_day_ga_month_year(text, expected):
    assert start_end(text) == day(*expected)
    assert remainder(text) == ""


@pytest.mark.parametrize("text,expected", [
    ("ranar 5 ga Yuli 2021", (2021, 7, 5)),
    ("ranar 14 ga Disamba 1991", (1991, 12, 14)),
])
def test_the_day_noun_may_open_the_date_line(text, expected):
    assert start_end(text) == day(*expected)
    assert remainder(text) == ""


def test_the_linker_may_be_dropped():
    """Written Hausa also sets the day beside the month with no ga."""
    assert start_end("15 Yuni 2027") == day(2027, 6, 15)


def test_a_bare_day_and_month_reads_forward():
    assert start_end("5 ga Yuni") == day(2027, 6, 5)


def test_a_bare_month_is_the_whole_month():
    assert start_end("Yuli 2027") == month_span(2027, 7)


def test_a_month_with_no_year_reads_forward():
    assert start_end("Yuli") == month_span(2027, 7)


def test_a_month_named_with_its_noun():
    assert start_end("watan Yuli 2027") == month_span(2027, 7)


@pytest.mark.parametrize("text,y", [
    ("2027", 2027), ("1918", 1918), ("1960", 1960),
    ("shekara ta 1926", 1926),
    ("shekarar 2024", 2024),
])
def test_the_year(text, y):
    assert start_end(text) == year_span(y)


@pytest.mark.parametrize("text", ["ga", "ranar", "watan", "shekarar"])
def test_a_lone_frame_word_names_no_date(text):
    nomatch(text)


@pytest.mark.parametrize("text,expected", [
    ("watan Fabrairun shekarar 2024", (2024, 2)),
    ("watan Yulin shekarar 2027", (2027, 7)),
])
def test_the_year_word_does_not_strand_a_month_reading(text, expected):
    """"watan Fabrairun shekarar 2024" names February of 2024, not February
    of the anchor year with "shekarar 2024" left unread beside it."""
    assert start_end(text) == month_span(*expected)
    assert remainder(text) == ""


def test_the_year_word_does_not_strand_a_full_date_reading():
    """"ranar 10 ga watan Oktoban shekarar 2022" is attested whole; the year
    must land on 2022, not on the anchor year."""
    assert start_end("ranar 10 ga watan Oktoban shekarar 2022") == day(2022, 10, 10)
    assert remainder("ranar 10 ga watan Oktoban shekarar 2022") == ""


@pytest.mark.parametrize("text,expected", [
    ("10 ga watan Oktoba shekarar", (2027, 10, 10)),
])
def test_a_bare_year_word_with_no_year_leaves_it_stranded(text, expected):
    """"shekarar" with no YEAR after it names no year at all -- the date
    line still reads day and month against the anchor, but the noun cannot
    bind on its own and silently borrow the anchor's year, so it stays
    unread beside the date rather than vanishing."""
    assert start_end(text) == day(*expected)
    assert remainder(text) == "shekarar"


def test_a_bare_month_and_year_word_with_no_year_leaves_it_stranded():
    assert start_end("watan Fabrairu shekarar") == month_span(2027, 2)
    assert remainder("watan Fabrairu shekarar") == "shekarar"
