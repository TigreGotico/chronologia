"""The Irish spoken clock, which counts from the hour just PAST.

"leathuair tar éis a trí" is half an hour after three -- 03:30, not the
03:30-means-two-thirty reading Irish's Nordic neighbours use.  "ceathrú tar
éis" counts up from the named hour and "ceathrú chun" counts down to it, and
a minute count reads the same way with the unit noun spoken between the count
and the direction ("deich nóiméad tar éis a hocht").  Ulster substitutes
"i ndiaidh" for "tar éis" and "go dtí" for "chun", and both variants read
identically.

Every direction is pinned adversarially: the wrong reading is asserted
absent, not merely the right one asserted present.  The hour itself is the
disjunctive numeral carried by the particle "a" -- "a trí", "a haon",
"a hocht" -- never the counting form a noun would take.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, nomatch, start


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


@pytest.mark.parametrize("text,h,mi", [
    ("leathuair tar éis a haon", 1, 30),
    ("leathuair tar éis a dó", 2, 30),
    ("leathuair tar éis a trí", 3, 30),
    ("leathuair tar éis a ceathair", 4, 30),
    ("leathuair tar éis a cúig", 5, 30),
    ("leathuair tar éis a sé", 6, 30),
    ("leathuair tar éis a seacht", 7, 30),
    ("leathuair tar éis a hocht", 8, 30),
    ("leathuair tar éis a naoi", 9, 30),
    ("leathuair tar éis a deich", 10, 30),
])
def test_half_past_names_the_hour_just_gone(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,wrong_hour", [
    ("leathuair tar éis a trí", 2),
    ("leathuair tar éis a cúig", 4),
    ("leathuair tar éis a hocht", 7),
    ("leathuair tar éis a deich", 9),
])
def test_half_past_is_never_the_previous_hour(text, wrong_hour):
    """The toward-the-coming-hour reading ("half three" = 02:30) must never
    occur: it is the one mistake this locale's direction can make, and it
    moves every stated time back a full hour."""
    assert start(text).hour != wrong_hour


@pytest.mark.parametrize("text,h,mi", [
    ("ceathrú tar éis a trí", 3, 15),
    ("ceathrú tar éis a haon", 1, 15),
    ("ceathrú tar éis a seacht", 7, 15),
    ("ceathrú tar éis a deich", 10, 15),
])
def test_quarter_past_counts_up(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("ceathrú chun a dó", 1, 45),
    ("ceathrú chun a trí", 2, 45),
    ("ceathrú chun a seacht", 6, 45),
])
def test_quarter_to_counts_down(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("past,to", [
    ("ceathrú tar éis a trí", "ceathrú chun a trí"),
    ("ceathrú tar éis a seacht", "ceathrú chun a seacht"),
])
def test_past_and_to_are_not_the_same_time(past, to):
    """"tar éis" and "chun" are the two halves of one opposition; reading
    either as the other moves the answer half an hour and an hour."""
    assert start(past) != start(to)


@pytest.mark.parametrize("text,h,mi", [
    ("deich nóiméad tar éis a hocht", 8, 10),
    ("cúig nóiméad tar éis a dó", 2, 5),
    ("fiche nóiméad tar éis a ceathair", 4, 20),
    ("cúig nóiméad chun a dó", 1, 55),
    ("deich nóiméad chun a trí", 2, 50),
])
def test_minutes_past_and_to(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,wrong_hour", [
    ("cúig nóiméad chun a dó", 2), ("deich nóiméad chun a trí", 3),
])
def test_minutes_to_rolls_the_hour_back(text, wrong_hour):
    assert start(text).hour != wrong_hour


@pytest.mark.parametrize("past,ulster", [
    ("leathuair tar éis a trí", "leathuair i ndiaidh a trí"),
    ("ceathrú tar éis a seacht", "ceathrú i ndiaidh a seacht"),
])
def test_ulster_i_ndiaidh_reads_as_tar_eis(past, ulster):
    assert start(past) == start(ulster)


@pytest.mark.parametrize("to,ulster", [
    ("ceathrú chun a dó", "ceathrú go dtí a dó"),
    ("ceathrú chun a seacht", "ceathrú go dtí a seacht"),
])
def test_ulster_go_dti_reads_as_chun(to, ulster):
    assert start(to) == start(ulster)


@pytest.mark.parametrize("text,h", [
    ("a haon a chlog", 1), ("a dó a chlog", 2), ("a trí a chlog", 3),
    ("a ceathair a chlog", 4), ("a cúig a chlog", 5), ("a sé a chlog", 6),
    ("a seacht a chlog", 7), ("a hocht a chlog", 8), ("a naoi a chlog", 9),
    ("a deich a chlog", 10), ("a dó dhéag a chlog", 12),
])
def test_a_chlog_names_a_bare_hour(text, h):
    """The hour after the particle "a" is the disjunctive numeral, with the
    h-prothesis one and eight carry there ("a haon", "a hocht")."""
    assert start(text).hour == h


@pytest.mark.parametrize("text,h,mi", [
    ("15:30", 15, 30), ("09:05", 9, 5), ("00:00", 0, 0), ("23:59", 23, 59),
])
def test_digit_clock(text, h, mi):
    s = start(text)
    assert (s.hour, s.minute) == (h, mi)


@pytest.mark.parametrize("text,h", [("meán oíche", 0), ("meán lae", 12)])
def test_clock_landmarks(text, h):
    assert start(text).hour == h


@pytest.mark.parametrize("text,h", [
    ("a trí i.n.", 15), ("a haon i.n.", 13), ("a naoi r.n.", 9),
    ("a deich r.n.", 10),
])
def test_meridiem_corroborates_the_hour_particle(text, h):
    assert start(text).hour == h


@pytest.mark.parametrize("text", [
    "leathuair",          # a bare half-hour with no direction and no hour
    "ceathrú",            # a bare quarter, likewise
    "tar éis",            # a bare direction with nothing to count from
    "ceathrú tar éis",    # a direction with no hour named
    "a chlog",            # the o'clock word with no hour
])
def test_incomplete_clock_is_not_a_time(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "seomra a 3", "uimhir a 7", "leathanach a 2", "caibidil a 5",
    "a 5 euro", "bhí a trí cinn aige",
])
def test_enumerative_particle_is_not_a_clock(text):
    """The particle "a" also ENUMERATES -- "uimhir a 3" is number three,
    "seomra a 5" is room five -- and nothing in the surface distinguishes
    that use from the clock's.  Reading it as an hour answers a time for a
    phrase that names none, which is worse than answering nothing."""
    nomatch(text)


@pytest.mark.parametrize("text", ["a trí", "a haon", "a dó dhéag", "a hocht"])
def test_bare_hour_particle_needs_corroboration(text):
    """Every source that gives the particle before an hour gives it inside a
    fuller phrase -- "Tá sé a haon a chlog", "leathuair tar éis a trí" --
    and none shows the bare form standing alone as a time in running text.
    The bare reading is therefore given up so the enumerative uses above can
    be refused; "a chlog", a meridiem or a clock direction buys it back."""
    nomatch(text)
