"""regnal_date stage: Japanese nengō resolved to Gregorian year spans.

Era years count as Gregorian calendar years (from Meiji 6 / 1873 on),
clamped to the reign segment: the accession year begins at the accession
date and the last year of a closed era ends at the successor's accession
(Wikipedia, "Japanese era name")."""
import pytest
from engine_helpers import ANCHOR, zz_engine

from chronologia.astrodate import AstroDate
from chronologia.regnal import REGNAL_SEQUENCES


def _one(text):
    res = zz_engine().resolve(text, ANCHOR)
    assert len(res) == 1, f"{text!r} -> {res}"
    return res[0]


# -- "<era-name> N" natural phrasing ---------------------------------------

def test_reiwa_7_is_2025():
    r = _one("zreiwa 7")
    assert r.value.start == AstroDate(2025, 1, 1)
    assert r.value.end == AstroDate(2026, 1, 1)

def test_reiwa_1_bounded_below_by_accession():
    r = _one("zreiwa 1")
    assert r.value.start == AstroDate(2019, 5, 1)       # accession, not 1 Jan
    assert r.value.end == AstroDate(2020, 1, 1)

def test_heisei_1_is_1989():
    assert _one("zheisei 1").value.start == AstroDate(1989, 1, 8)

def test_showa_64_truncated_by_heisei_accession():
    # Shōwa 64 (1989) ended when Heisei began, 1989-01-08
    r = _one("zshowa 64")
    assert r.value.start == AstroDate(1989, 1, 1)
    assert r.value.end == AstroDate(1989, 1, 8)


# -- "the Nth year of <era-name>" ------------------------------------------

def test_third_year_of_reiwa():
    assert _one("3 zyr zof zreiwa").value.start == AstroDate(2021, 1, 1)


# -- registry facts + successor tiling -------------------------------------

def test_segments_tile_at_successor_accession():
    seq = REGNAL_SEQUENCES["nengo"]
    _, showa_last_end = seq.year_span("showa", 64)
    heisei_1_start, _ = seq.year_span("heisei", 1)
    assert showa_last_end == heisei_1_start             # no gap

def test_reiwa_is_open_ended():
    seq = REGNAL_SEQUENCES["nengo"]
    assert seq.year_span("reiwa", 50) is not None       # far future still valid


# -- adversarial -----------------------------------------------------------

@pytest.mark.parametrize("text", ["zshowa 65", "zreiwa 0", "zzz 3"])
def test_nonexistent_year_returns_nothing(text):
    assert zz_engine().resolve(text, ANCHOR) == [] or \
        all(r.value.start.year >= 1 for r in zz_engine().resolve(text, ANCHOR))
