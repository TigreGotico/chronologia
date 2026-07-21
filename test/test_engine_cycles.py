"""cycle_ref stage: the generalisation of weekday_ref to any named day cycle,
against the fixed anchor datetime(2017, 6, 27) (a Tuesday; French Republican
9 Messidor 225, nundinal position 2).

Three cycles are exercised: the canonical Gregorian week (proving byte
equivalence with the legacy weekday path), the month-anchored French
Republican décade, and the free-running Roman nundinal cycle."""
import pytest
from engine_helpers import ANCHOR, zz_engine

from chronologia.astrodate import AstroDate
from chronologia.cycles import DAY_CYCLES


def _one(text):
    res = zz_engine().resolve(text, ANCHOR)
    assert len(res) == 1, f"{text!r} -> {res}"
    return res[0]


# -- the week cycle reproduces weekday_ref exactly -------------------------

@pytest.mark.parametrize("cycle_word,weekday_word", [
    ("zwkmon", "zmon"), ("zwkwed", "zwed"), ("zwksun", "zsun")])
@pytest.mark.parametrize("marker", ["znext", "zlast", "zthis"])
def test_week_cycle_matches_weekday_ref(cycle_word, weekday_word, marker):
    via_cycle = _one(f"{marker} {cycle_word}").value.start
    via_weekday = _one(f"{marker} {weekday_word}").value.start
    assert via_cycle == via_weekday          # byte-identical day


def test_week_cycle_is_canonical_instance():
    assert DAY_CYCLES["week"].length == 7
    assert DAY_CYCLES["week"].kind == "free_running"


# -- nundinal (free-running, length 8) -------------------------------------

def test_next_nundinal_day():
    assert _one("znext znund").value.start == AstroDate(2017, 6, 28)

def test_last_nundinal_day():
    assert _one("zlast znund").value.start == AstroDate(2017, 6, 20)

def test_this_nundinal_day():
    assert _one("zthis znuna").value.start == AstroDate(2017, 6, 25)


# -- French Republican décade (month-anchored, length 10) ------------------

def test_next_primidi():
    assert _one("znext zprimidi").value.start == AstroDate(2017, 6, 29)

def test_next_decadi():
    assert _one("znext zdecadi").value.start == AstroDate(2017, 6, 28)

def test_this_quintidi():
    assert _one("zthis zquintidi").value.start == AstroDate(2017, 6, 23)

def test_republican_decade_is_month_anchored():
    assert DAY_CYCLES["republican_decade"].kind == "month_anchored"
    assert DAY_CYCLES["republican_decade"].length == 10


# -- adversarial -----------------------------------------------------------

def test_garbage_never_raises():
    zz_engine().resolve("znext zzz", ANCHOR)
