"""R119: a resolved PINPOINT clock start ("at 9am", "next monday at 9am") with
a trailing bare "for <duration>" extends the span's END by that duration,
instead of leaving the minute-wide clock as a bogus "point span" with the
duration stranded in the remainder.

"next monday at 9am for 2 hours" names a two-hour MEETING starting 9am, not
an instantaneous 9:00-9:01 event with "for 2 hours" left over -- the same
silent-wrong shape #660 / the duration-range veto fixed for "for 6 to 8
hours" (see ``test_nl_duration_range_not_timespan.py``), just on the other
side of the clock-vs-duration boundary: here a clock DID resolve, and the
trailing duration should compose onto it rather than being dropped.

Expected values are independently hand-computed against the anchor
(Tuesday 2017-06-27 13:04, from ``_corpus.ANCHOR``), never read back from the
parser.
"""
from datetime import datetime, timedelta

from ._corpus import ANCHOR, ad, nomatch, parse, span, start_end


# -- the fix: clock start + bare "for <duration>" extends the end -----------

def test_dated_clock_plus_hours_extends_end():
    # next Monday from Tue 2017-06-27 is 2017-07-03; 9am + 2h = 11am.
    s, e = start_end("next monday at 9am for 2 hours")
    assert (s, e) == (ad(datetime(2017, 7, 3, 9, 0)),
                      ad(datetime(2017, 7, 3, 11, 0)))


def test_dateless_clock_plus_minutes_extends_end():
    # bare "at 3:15pm" on the anchor day (15:15 is still ahead of 13:04
    # anchor time) -> today, + 45 min = 16:00.
    s, e = start_end("at 3:15pm for 45 minutes")
    assert (s, e) == (ad(datetime(2017, 6, 27, 15, 15)),
                      ad(datetime(2017, 6, 27, 16, 0)))


def test_clock_plus_hour_and_a_half_extends_end():
    # a compound "an hour and a half" duration (90 min) -- regression pin for
    # the number-fold overlap that used to truncate this to a bare 1h (see
    # the ``_extend_clock_for_duration`` docstring): 9am + 90min = 10:30.
    s, e = start_end("next monday at 9am for an hour and a half")
    assert (s, e) == (ad(datetime(2017, 7, 3, 9, 0)),
                      ad(datetime(2017, 7, 3, 10, 30)))


def test_clock_plus_minutes_no_lead_words():
    s, e = start_end("call starts at 9am for 90 minutes")
    # "9am" with no date, 13:04 anchor already past 9am -> rolls to tomorrow.
    assert (s, e) == (ad(datetime(2017, 6, 28, 9, 0)),
                      ad(datetime(2017, 6, 28, 10, 30)))
    assert parse("call starts at 9am for 90 minutes").remainder == "call starts"


def test_midnight_crossing_clock_plus_hours():
    # 11pm hasn't happened yet today (anchor 13:04) -> today 23:00 + 2h rolls
    # past midnight into tomorrow 01:00.
    s, e = start_end("at 11pm for 2 hours")
    assert (s, e) == (ad(datetime(2017, 6, 27, 23, 0)),
                      ad(datetime(2017, 6, 28, 1, 0)))


def test_embedded_sentence_keeps_trailing_clause():
    # the duration reading only claims "for 2 hours"; the rest of the
    # sentence is neither swallowed nor silently dropped.
    r = parse("lets meet next monday at 9am for 2 hours to discuss the budget")
    assert r is not None
    s, e = r.span.start, r.span.end
    assert (s, e) == (ad(datetime(2017, 7, 3, 9, 0)),
                      ad(datetime(2017, 7, 3, 11, 0)))
    assert r.remainder == "lets meet to discuss the budget"


def test_leading_words_before_from_clock_kept_in_remainder():
    r = parse("meeting from 9am for 2 hours")
    assert r is not None
    assert (r.span.start, r.span.end) == (ad(datetime(2017, 6, 28, 9, 0)),
                                          ad(datetime(2017, 6, 28, 11, 0)))
    assert r.remainder == "meeting from"


# -- controls: pinned, must NOT change ---------------------------------------

def test_explicit_end_clock_range_keeps_its_own_shape():
    # "9am to 11am on monday" is an EXPLICIT end-clock range, composed by
    # _extract_range -- its own end-of-minute convention (+1 minute) is
    # untouched by the R119 fix, which never runs on this path.
    s, e = start_end("9am to 11am on monday")
    assert (s, e) == (ad(datetime(2017, 7, 3, 9, 0)),
                      ad(datetime(2017, 7, 3, 11, 1)))


def test_bare_for_duration_alone_still_refused():
    # design-pinned (test_nl_duration_range_not_timespan.py): no anchoring
    # clock resolved at all, so there is nothing for the duration to extend.
    nomatch("for 2 hours")
    nomatch("cook for 20 minutes")


def test_for_duration_range_still_refused():
    # a "for N to M <unit>" DURATION RANGE after no clock is still the
    # duration-range veto's territory, untouched by this fix.
    nomatch("from 6 to 8 hours")
    nomatch("cook on low for 6 to 8 hours")


def test_whole_day_span_plus_for_duration_left_stranded():
    # POLICY DECISION (see commit body): a "for <duration>" trailing a
    # WHOLE-DAY (or wider) span -- not a pinpoint clock -- is left stranded
    # in the remainder rather than composed. There is no single unambiguous
    # rule for what "on monday for 2 hours" should mean (2 hours starting at
    # which time of day?), so per the repo's refusal-over-silently-wrong
    # convention the whole-day reading of "monday" wins and the duration is
    # not silently attached anywhere.
    r = parse("on monday for 2 hours")
    assert r is not None
    assert (r.span.start, r.span.end) == (ad(datetime(2017, 7, 3, 0, 0)),
                                          ad(datetime(2017, 7, 4, 0, 0)))
    assert "for 2 hours" in r.remainder


def test_spurious_for_with_no_duration_does_not_fabricate():
    # "for" not followed by any duration reading must never fabricate an end.
    r = parse("waiting for the bus at 9am")
    assert r is not None
    s, e = r.span.start, r.span.end
    assert (s, e) == (ad(datetime(2017, 6, 28, 9, 0)),
                      ad(datetime(2017, 6, 28, 9, 1)))
    assert r.remainder == "waiting for the bus"


def test_extract_duration_alone_unaffected():
    # extract_duration on these sentences keeps working exactly as before --
    # this fix lives entirely in extract_timespan's composition layer.
    from chronologia.extract.nseries import extract_duration
    d, rem = extract_duration("next monday at 9am for 2 hours", "en")
    assert d == timedelta(hours=2)
    d2, rem2 = extract_duration("for an hour and a half", "en")
    assert d2 == timedelta(minutes=90)
