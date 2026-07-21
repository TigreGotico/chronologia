"""Japanese nengō regnal-year spans, ported from the reckoning-core
assertions the parser exercised through its ``regnal_date`` engine stage.

Era years count as Gregorian calendar years (Meiji 6 / 1873 onward), clamped
to the reign segment: the accession year begins at the accession date, and
the last year of a closed era ends at the successor's accession
(japanese_nengo_reference.html).  Rewritten against ``RegnalSequence.
year_span`` directly -- the natural-language phrasings ("the Nth year of
<era>") are parser-side vocabulary; the asserted year spans are the core.
"""
import pytest

from chronologia.astrodate import AstroDate
from chronologia.regnal import REGNAL_SEQUENCES

NENGO = REGNAL_SEQUENCES["nengo"]


# -- accession-clamped and full-year spans -------------------------------

def test_reiwa_7_is_2025():
    assert NENGO.year_span("reiwa", 7) == (AstroDate(2025, 1, 1),
                                           AstroDate(2026, 1, 1))


def test_reiwa_1_bounded_below_by_accession():
    # Reiwa 1 begins at the 2019-05-01 accession, not 1 January
    start, end = NENGO.year_span("reiwa", 1)
    assert start == AstroDate(2019, 5, 1)
    assert end == AstroDate(2020, 1, 1)


def test_heisei_1_starts_at_accession():
    start, _ = NENGO.year_span("heisei", 1)
    assert start == AstroDate(1989, 1, 8)


def test_showa_64_truncated_by_heisei_accession():
    # Shōwa 64 (1989) ended when Heisei began, 1989-01-08
    assert NENGO.year_span("showa", 64) == (AstroDate(1989, 1, 1),
                                            AstroDate(1989, 1, 8))


def test_third_year_of_reiwa():
    start, _ = NENGO.year_span("reiwa", 3)
    assert start == AstroDate(2021, 1, 1)


# -- successor tiling + open-ended era -----------------------------------

def test_segments_tile_at_successor_accession():
    _, showa_last_end = NENGO.year_span("showa", 64)
    heisei_1_start, _ = NENGO.year_span("heisei", 1)
    assert showa_last_end == heisei_1_start          # no gap


def test_reiwa_is_open_ended():
    assert NENGO.year_span("reiwa", 50) is not None  # far future still valid


# -- adversarial: nonexistent years resolve to nothing -------------------

@pytest.mark.parametrize("name,n", [
    ("showa", 65),   # past the Heisei accession
    ("reiwa", 0),    # n < 1
])
def test_nonexistent_year_returns_none(name, n):
    assert NENGO.year_span(name, n) is None


def test_unknown_segment_raises_keyerror():
    # an unknown segment name is a lookup error at the core (the engine's
    # "garbage never resolves" is a parser-side vocabulary concern instead)
    with pytest.raises(KeyError):
        NENGO.year_span("zzz", 3)
