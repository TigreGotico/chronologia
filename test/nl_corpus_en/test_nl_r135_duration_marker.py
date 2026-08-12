"""R135: a duration-marking preposition immediately preceding a BOUND
duration is temporal glue, not leftover text.

``extract_duration("for 90 minutes", "en")`` used to return the correct
90-minute :class:`~datetime.timedelta` but strand the leading "for" alone in
the remainder -- true of every locale whose duration marker sits directly
before the count ("for"/"für"/"durante"/"pendant"/"per"/"przez"...). The
marker is consumed from the SAME ``recur_for`` connector vocabulary
(``marker_recur_for.voc``) already used by the recurrence grammar's own
"every monday *for* 3 weeks" bound and by :mod:`chronologia.extract.timespan`
for its trailing "... for <duration>" clock extension (R119) -- one marker
family, not a parallel one.

Consumption is adjacency-gated: the marker must sit immediately before the
duration's own first token, so a marker separated by other words is left
alone (it modifies something else, not this duration). "in" is deliberately
NOT consumed -- it marks a relative OFFSET ("in 90 minutes" from now), not a
bound duration, and "in" is not a ``recur_for`` member in any locale.

Expected values are hand-derived seconds arithmetic that never touches the
parser; expected remainders are hand-derived from the input string.
"""
from datetime import timedelta

from chronologia.extract import extract_duration

LANG = "en"


# -- the fix: adjacent marker is consumed ------------------------------------

def test_bare_for_duration_marker_consumed():
    d, rem = extract_duration("for 90 minutes", LANG)
    assert d == timedelta(minutes=90)
    assert rem == ""


def test_leading_words_before_for_kept_marker_consumed():
    d, rem = extract_duration("meet for 90 minutes", LANG)
    assert d == timedelta(minutes=90)
    assert rem == "meet"


def test_for_duration_compound_marker_consumed():
    # "for" attaches to the whole compound, not just its first component.
    d, rem = extract_duration("wait for 2 hours and 15 minutes", LANG)
    assert d == timedelta(hours=2, minutes=15)
    assert rem == "wait"


def test_for_duration_range_marker_consumed():
    # the range-to fold (upper bound wins) runs before the marker check, so
    # "for" attaches to the LOWER bound "3", not the "5" it composed onto.
    d, rem = extract_duration("for 3 to 5 days", LANG)
    assert d == timedelta(days=5)
    assert rem == ""


# -- controls: non-adjacent marker is NOT swallowed --------------------------

def test_marker_separated_by_words_not_swallowed():
    r = extract_duration("meet for lunch in 90 minutes", LANG)
    assert r is not None
    d, rem = r
    assert d == timedelta(minutes=90)
    assert rem == "meet for lunch in"


def test_in_offset_marker_left_stranded():
    # "in" marks a relative offset, not a bound duration -- not a
    # ``recur_for`` member, so it is deliberately left in the remainder.
    d, rem = extract_duration("in 90 minutes", LANG)
    assert d == timedelta(minutes=90)
    assert rem == "in"


# -- controls: bare / marker-free durations unchanged ------------------------

def test_bare_duration_unchanged():
    d, rem = extract_duration("90 minutes", LANG)
    assert d == timedelta(minutes=90)
    assert rem == ""


def test_bare_duration_with_unrelated_leading_word_unchanged():
    d, rem = extract_duration("cook 20 minutes", LANG)
    assert d == timedelta(minutes=20)
    assert rem == "cook"
