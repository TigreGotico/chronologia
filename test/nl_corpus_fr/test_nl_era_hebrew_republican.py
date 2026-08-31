"""French surfaces for calendar-backed era years: the Hebrew Anno Mundi
year ("... du calendrier hébraïque") and the French Republican calendar's
own year numbering ("l'an N de la République"), plus the accented
Republican month surface "vendémiaire".

Both years used to be read as literal Gregorian years, stranding the
calendar-name marker in the remainder ("5786 du calendrier hébraïque" ->
Gregorian year 5786) or discarded entirely ("l'an II de la République" ->
no match at all).

Reference values are INDEPENDENT of the extractor: they come straight from
``chronologia.resolve_era`` (the era registry), never from the parser's own
output.
"""
import pytest

from chronologia import resolve_era

from ._corpus import span, start_end, nomatch


def _greg_year(era, n):
    d = resolve_era(era, n)
    return d.year


# -- Hebrew Anno Mundi year, resolved through the calendar's own epoch ----

@pytest.mark.parametrize("text,n", [
    ("5786 du calendrier hébraïque", 5786),
    ("l'an 5786 du calendrier hébraïque", 5786),
    ("année 5786 du calendrier hébraïque", 5786),
])
def test_hebrew_anno_mundi_resolves_through_epoch(text, n):
    s, _ = start_end(text)
    assert s.year == _greg_year("anno_mundi", n)


def test_hebrew_year_name_is_consumed():
    r = span("5786 du calendrier hébraïque")
    assert r.start.year == 2025


# adversarial: 5786 is also a plausible-looking bare year, but the marker
# forces the Hebrew reading, not a literal Gregorian year 5786.
def test_hebrew_year_not_read_as_gregorian():
    s, _ = start_end("5786 du calendrier hébraïque")
    assert s.year != 5786
    assert s.year == 2025


# -- French Republican year, pinned to LITERAL Gregorian dates -----------
#
# These are NOT derived from ``chronologia.eras.ERAS``/``resolve_era`` --
# that registry is the very epoch the resolver itself reads through
# ``_era_span`` -> ``resolve_era_year_span``, so a circular gold would still
# pass under a whole-year epoch shift.  The dates below are historical facts
# (the Republic was proclaimed 22 September 1792 = An I day 1; each
# Republican year begins 22 September, one day later after a 366-day
# sextile year) cross-checked by independent day-count arithmetic, not by
# calling any chronologia function.

def test_french_republican_an_ii_starts_literal_date():
    s, _ = start_end("l'an II de la République")
    assert (s.year, s.month, s.day) == (1793, 9, 22)


def test_french_republican_an_iii_is_a_366_day_sextile_year():
    # An III (1794-09-22 .. 1795-09-23) is one of the calendar's sextile
    # (leap) years: pinning BOTH endpoints catches an epoch shift (wrong
    # start) and a naive 365-day-year assumption (wrong end) in one
    # assertion.
    s, e = start_end("l'an III de la République")
    assert (s.year, s.month, s.day) == (1794, 9, 22)
    assert (e.year, e.month, e.day) == (1795, 9, 23)
    assert (e - s).days == 366


# adversarial: 1789 is a plausible bare Gregorian year AND a well-formed
# Republican year number; the explicit "de la République" marker must force
# the Republican reading (An 1789 == Gregorian 3580), not the Gregorian one.
def test_french_republican_year_not_read_as_gregorian():
    s, _ = start_end("l'an 1789 de la République")
    assert s.year == _greg_year("french_republican", 1789)
    assert s.year != 1789


# a bare "an II" with no Republican marker is still ambiguous and refused
# rather than guessed.
def test_bare_an_roman_numeral_without_marker_is_refused():
    nomatch("an II")


# -- accented Republican month surfaces -------------------------------------
#
# The correct French spellings carry a circumflex/acute accent (Wiktionary
# lemma entries: fr.wiktionary.org/wiki/vendémiaire, /nivôse,
# /pluviôse, /ventôse, /floréal -- confirmed live, 2026-08-31).
# The other seven months (brumaire, frimaire, germinal, prairial, messidor,
# thermidor, fructidor) carry no accent in their own lemma entries.
#
# Golds are LITERAL Gregorian dates, not a live call into
# ``chronologia.calendars`` -- calling the calendar's own JDN hub at test
# time would read the very epoch/leap-year arithmetic the resolver reads
# for these bare-month-and-day phrases, so a bug there would move the gold
# along with the bug.  Each literal was cross-checked against the mission
# anchor (2017-06-27) and the calendar's day-count from the Year I epoch
# (22 September 1792) before being pinned here.

@pytest.mark.parametrize("unaccented,accented,day,y,m,d", [
    ("vendemiaire", "vendémiaire", 18, 2017, 10, 9),
    ("nivose", "nivôse", 2, 2017, 12, 22),
    ("pluviose", "pluviôse", 5, 2018, 1, 24),
    ("ventose", "ventôse", 10, 2018, 2, 28),
    ("floreal", "floréal", 5, 2018, 4, 24),
])
def test_accented_month_matches_literal_gold(unaccented, accented, day, y, m, d):
    for surface in (unaccented, accented):
        s, e = start_end(f"{day} {surface}")
        assert (s.year, s.month, s.day) == (y, m, d)
        assert (e - s).days == 1
