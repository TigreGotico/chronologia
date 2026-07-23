"""English time-of-day daypart deixis: a daypart narrows a resolved day to a
conventional sub-day band, and the deictic forms ("this morning", "tonight",
"last night") resolve on their own.

Bands are the Unicode CLDR 47 day-period rules (locale ``en``), the same source
:mod:`chronologia.dayparts` cites: morning ``[06:00, 12:00)``, afternoon
``[12:00, 18:00)``, evening ``[18:00, 21:00)``, night ``[21:00, 06:00)``
(crossing midnight into the next civil day).  Every band is
``BASIS_RECONSTRUCTED`` -- a daypart is a cultural boundary, not a clock reading
the speaker gave, so it must never claim the exactness of "at 6am".

Anchor: Wednesday 2024-03-06 12:00.  Two regressions guarded here:

* the SILENT DROP -- "yesterday morning" used to return the whole of yesterday,
  the "morning" word stranded; it must now be yesterday's morning band;
* noon/midnight are clock *landmarks*, not dayparts, and must keep resolving to
  their minute-wide exact anchors unchanged.
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate, BASIS_EXACT, BASIS_RECONSTRUCTED
from chronologia.extract import extract_timespan

ANCHOR = datetime(2024, 3, 6, 12, 0)          # Wednesday noon


def _span(text):
    return extract_timespan(text, "en-us", anchor=ANCHOR).span


def _assert_band(text, start, end):
    s = _span(text)
    assert s.start == start, f"{text!r} start {s.start} != {start}"
    assert s.end == end, f"{text!r} end {s.end} != {end}"
    assert s.basis == BASIS_RECONSTRUCTED, f"{text!r} basis {s.basis!r}"


# -- silent-drop fix: a daypart narrows the resolved day -------------------

def test_yesterday_morning_narrows_to_morning_band():
    # was the whole of 03-05; now yesterday's morning band
    _assert_band("yesterday morning",
                 AstroDate(2024, 3, 5, 6, 0), AstroDate(2024, 3, 5, 12, 0))

def test_yesterday_afternoon():
    _assert_band("yesterday afternoon",
                 AstroDate(2024, 3, 5, 12, 0), AstroDate(2024, 3, 5, 18, 0))

def test_tomorrow_evening():
    _assert_band("tomorrow evening",
                 AstroDate(2024, 3, 7, 18, 0), AstroDate(2024, 3, 7, 21, 0))

def test_tomorrow_afternoon():
    _assert_band("tomorrow afternoon",
                 AstroDate(2024, 3, 7, 12, 0), AstroDate(2024, 3, 7, 18, 0))

def test_tomorrow_night_crosses_midnight():
    # night belongs to the named day but reaches into the day after
    _assert_band("tomorrow night",
                 AstroDate(2024, 3, 7, 21, 0), AstroDate(2024, 3, 8, 6, 0))

def test_yesterday_morning_consumes_the_daypart_word():
    # the fix's whole point: "morning" no longer strands in the remainder
    assert extract_timespan("yesterday morning", "en-us",
                            anchor=ANCHOR).remainder == ""


# -- deictic standalone forms ---------------------------------------------

def test_this_morning():
    _assert_band("this morning",
                 AstroDate(2024, 3, 6, 6, 0), AstroDate(2024, 3, 6, 12, 0))

def test_this_afternoon():
    _assert_band("this afternoon",
                 AstroDate(2024, 3, 6, 12, 0), AstroDate(2024, 3, 6, 18, 0))

def test_this_evening():
    _assert_band("this evening",
                 AstroDate(2024, 3, 6, 18, 0), AstroDate(2024, 3, 6, 21, 0))

def test_tonight_is_today_night_band():
    # "tonight" == today's night band, running into tomorrow's small hours
    _assert_band("tonight",
                 AstroDate(2024, 3, 6, 21, 0), AstroDate(2024, 3, 7, 6, 0))

def test_last_night_is_the_night_that_just_ended():
    # defined convention: yesterday's night band, [yesterday 21:00, today 06:00)
    # -- the night that ended this morning, reaching through midnight into today
    _assert_band("last night",
                 AstroDate(2024, 3, 5, 21, 0), AstroDate(2024, 3, 6, 6, 0))


# -- adversarial ----------------------------------------------------------

def test_bare_daypart_defaults_to_today():
    # a bare "morning" with no day is the deictic default: today's band, the
    # same as "this morning".  (Chosen over None: the current day is the only
    # defensible referent absent other context.)
    _assert_band("morning",
                 AstroDate(2024, 3, 6, 6, 0), AstroDate(2024, 3, 6, 12, 0))

def test_bare_yesterday_without_daypart_is_still_whole_day():
    # no daypart present -> the whole-day parse is untouched, still exact
    s = _span("yesterday")
    assert s.start == AstroDate(2024, 3, 5, 0, 0)
    assert s.end == AstroDate(2024, 3, 6, 0, 0)
    assert s.basis == BASIS_EXACT

def test_bare_tomorrow_without_daypart_unchanged():
    s = _span("tomorrow")
    assert s.start == AstroDate(2024, 3, 7, 0, 0)
    assert s.end == AstroDate(2024, 3, 8, 0, 0)
    assert s.basis == BASIS_EXACT

def test_noon_is_still_an_exact_clock_landmark_not_a_daypart():
    # noon is a clock landmark (minute-wide, exact), never a reconstructed band
    s = _span("noon")
    assert s.start == AstroDate(2024, 3, 6, 12, 0)
    assert s.end == AstroDate(2024, 3, 6, 12, 1)
    assert s.basis == BASIS_EXACT

def test_midnight_is_still_an_exact_clock_landmark():
    s = _span("midnight")
    assert s.end - s.start == (AstroDate(2024, 3, 7, 0, 1)
                               - AstroDate(2024, 3, 7, 0, 0))
    assert s.basis == BASIS_EXACT

def test_daypart_never_raises_on_junk():
    # a daypart word buried in noise must never raise; it resolves or is dropped
    assert extract_timespan("xyzzy morning qwerty", "en-us",
                            anchor=ANCHOR).span is not None


# -- honest deferral: dawn / dusk -----------------------------------------

@pytest.mark.xfail(strict=True, reason=(
    "dawn/dusk are astronomical solar events, location-dependent: without "
    "coordinates the library cannot place them on a real clock. Deferred rather "
    "than faked with an invented civil-twilight hour. The solar machinery "
    "(chronologia.solar / prayer_times) resolves them once a location is "
    "supplied."))
def test_dawn_is_a_located_solar_event_not_a_nominal_band():
    s = extract_timespan("at dawn", "en-us", anchor=ANCHOR).span
    assert s is not None and s.start.hour < 12
