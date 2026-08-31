"""Turkish YEAR-first calendar quarter/half ("2020 birinci çeyrek", "2020'nin
ilk yarısı"): Turkish postposes its ordinal/period marker after the year
rather than preceding it the way "the first quarter of 2020" does. Before the
fix ``quarter_ref`` only offered the marker-first orders ("ORD quarter_word
YEAR?"), so a leading bare YEAR won the whole-year ``year_ref`` reading
instead and stranded the quarter word -- four times too wide.  The new
"YEAR ORD quarter_word" / "YEAR q NUM" orders mirror the YEAR-first
possessive ``half_period`` extend TR already ships (chronologia/locale/tr/
lang.json, base_grammar.py's Turkic YEAR-first possessive comment) but read
the BARE quarter noun: ``marker_quarter_word.voc`` only lists the bare
"çeyrek", never its possessive-marked "çeyreği" (TDK Güncel Türkçe Sözlük,
3. tekil iyelik eki -(s)I, https://sozluk.gov.tr), unlike ``marker_half``'s
"yarısı", which already IS the possessive form. Reading "çeyreği" would need
a new vocabulary surface this fix does not add, so the possessive/case-
marked genitive phrasings ("2020'nin birinci çeyreği", "2020 birinci
çeyreğinde") stay a documented, pinned known-unsupported gap rather than
silently returning a 4x-too-wide year. Gold is hand-derived: quarter N
spans months [3N-2 .. 3N+1); half H spans months [1 or 7 .. 7 or 13).
Anchor 2026-06-15."""
from datetime import datetime
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end

A = datetime(2026, 6, 15, 12, 0)

_QUARTER_CASES = [
    ("2020 birinci çeyrek", 2020, 1, 2020, 4),
    ("2020 ikinci çeyrek", 2020, 4, 2020, 7),
    ("2020 üçüncü çeyrek", 2020, 7, 2020, 10),
    ("2020 dördüncü çeyrek", 2020, 10, 2021, 1),
]


@pytest.mark.parametrize("text,sy,sm,ey,em", _QUARTER_CASES)
def test_year_first_quarter(text, sy, sm, ey, em):
    s, e = start_end(text, A)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)


def test_year_first_half():
    s, e = start_end("2020'nin ilk yarısı", A)
    assert s == AstroDate(2020, 1, 1)
    assert e == AstroDate(2020, 7, 1)


def test_bare_year_with_no_quarter_word_stays_whole_year():
    """Adversarial: a bare year with no quarter word must NOT be narrowed --
    "2020" alone stays the whole calendar year, proving the new orders bind
    only when the quarter/half word is actually present."""
    s, e = start_end("2020", A)
    assert s == AstroDate(2020, 1, 1)
    assert e == AstroDate(2021, 1, 1)


@pytest.mark.xfail(reason="çeyreği (possessive-marked quarter noun) has no "
                          "vocabulary surface; the phrase falls through to "
                          "the bare-year reading, four times too wide -- "
                          "see module docstring.", strict=True)
@pytest.mark.parametrize("text", [
    "2020'nin birinci çeyreği",
    "2020 birinci çeyreğinde",
])
def test_possessive_quarter_forms_known_unsupported(text):
    s, e = start_end(text, A)
    assert s == AstroDate(2020, 1, 1)
    assert e == AstroDate(2020, 4, 1)
