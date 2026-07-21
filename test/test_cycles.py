"""Named day cycles: the generalisation of weekday reckoning to any fixed
day cycle, resolved by pure ``resolve_cycle_day`` calls against the fixed
anchor 2017-06-27 (a Tuesday; French Republican décade position 8, nundinal
position 2).

Gold values are ported from the reckoning-core assertions that the parser
exercised through its ``cycle_ref`` engine stage, rewritten here against the
public API with no engine and no vocabulary binding: the vocabulary-to-
position mapping (which surface word means "primidi" / "nundina") is a
parser-side concern, so each named day is expressed directly as its integer
cycle position.
"""
from chronologia.astrodate import AstroDate
from chronologia.calendars import gregorian_to_jdn, jdn_to_gregorian
from chronologia.cycles import DAY_CYCLES, resolve_cycle_day

ANCHOR_JDN = gregorian_to_jdn(2017, 6, 27)


def _day(name, position, rel, anchor_jdn=ANCHOR_JDN):
    jdn = resolve_cycle_day(DAY_CYCLES[name], position, rel, anchor_jdn)
    return None if jdn is None else AstroDate(*jdn_to_gregorian(jdn))


# -- registry facts: the three cycles ------------------------------------

def test_week_is_canonical_seven_day_free_running():
    assert DAY_CYCLES["week"].length == 7
    assert DAY_CYCLES["week"].kind == "free_running"


def test_nundinal_is_eight_day_free_running():
    assert DAY_CYCLES["nundinal"].length == 8
    assert DAY_CYCLES["nundinal"].kind == "free_running"


def test_republican_decade_is_ten_day_month_anchored():
    assert DAY_CYCLES["republican_decade"].length == 10
    assert DAY_CYCLES["republican_decade"].kind == "month_anchored"


# -- the week cycle reproduces weekday next/last/this --------------------

def test_week_next_monday():
    # anchor is Tuesday (pos 1); next Monday (pos 0) is 2017-07-03
    assert _day("week", 0, 1) == AstroDate(2017, 7, 3)


def test_week_last_sunday():
    assert _day("week", 6, -1) == AstroDate(2017, 6, 25)


# -- nundinal (free-running, length 8) -----------------------------------

def test_next_nundinal_day():
    # anchor nundinal position 2; the day at position 3 ahead is 2017-06-28
    assert _day("nundinal", 3, 1) == AstroDate(2017, 6, 28)


def test_last_nundinal_day():
    assert _day("nundinal", 3, -1) == AstroDate(2017, 6, 20)


def test_this_nundinal_day():
    assert _day("nundinal", 0, 0) == AstroDate(2017, 6, 25)


# -- French Republican décade (month-anchored, length 10) ----------------

def test_next_primidi():
    # primidi == position 0; next is 2017-06-29
    assert _day("republican_decade", 0, 1) == AstroDate(2017, 6, 29)


def test_next_decadi():
    # decadi == position 9; next is 2017-06-28
    assert _day("republican_decade", 9, 1) == AstroDate(2017, 6, 28)


def test_this_quintidi():
    # quintidi == position 4; the one in the current décade is 2017-06-23
    assert _day("republican_decade", 4, 0) == AstroDate(2017, 6, 23)


# -- month-anchored discontinuity: target past the décade boundary -> None

def test_month_anchored_boundary_returns_none():
    # from 2017-09-12 (décade position 5), asking for the next position-5 day
    # would land past the republican month's décade boundary; no such day.
    boundary_anchor = gregorian_to_jdn(2017, 9, 12)
    assert resolve_cycle_day(DAY_CYCLES["republican_decade"], 5, 1,
                             boundary_anchor) is None


# -- adversarial ---------------------------------------------------------

def test_free_running_position_always_resolves():
    # a free-running cycle never hits the month-boundary None branch
    for pos in range(DAY_CYCLES["nundinal"].length):
        for rel in (-1, 0, 1):
            assert _day("nundinal", pos, rel) is not None
