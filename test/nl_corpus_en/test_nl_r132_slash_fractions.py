"""R132: a slash fraction ("1/2 hour") was silently misread as the
DENOMINATOR count, stranding the numerator in the remainder.

Before the fix, the tokenizer had no lexical shape for a bare "N/D" written
fraction: the '/' matched nothing in the token regex and vanished between two
independent bare-number tokens, so "1/2 hour" tokenized exactly like the
three separate words "1 2 hour". The unit-count fold then bound the LAST
number before the unit -- "2 hours" -- and stranded the first as an
unexplained remainder ("1"). "3/4 hour" read as "4 hours" remainder "3": the
DENOMINATOR was read as the count, the numerator dropped on the floor. This
is silent-wrong, not a refusal -- exactly the defect class this corpus exists
to catch.

The fix folds "N/D" (both 1-2 digit components, exactly one '/') into a
single decimal-valued token at tokenize time, ahead of the bare-number rule,
so "1/2 hour" reads identically to the already-correct "0.5 hour". Policy
decision (see ``tokenizer._SLASHFRAC``): no denominator allow-list is
enforced -- an oddball fraction ("5/7 hour") is arithmetically well-defined
and is read as the decimal it names, the same as any other fractional count
would be. The fold's job is only to stop the slash from being silently
DROPPED, not to police which fractions are sensible durations.

Every expected value is hand-computed (N/D * unit-length), never read back
from the parser. Date-slash forms ("01/02/2025", "3/4/2025") are pinned
UNCHANGED: ``_NUMDATE`` (which requires a third, year, component) is tried
before the new fraction literal in the tokenizer's alternation, so a real
date still wins that position outright and the fraction literal is never
even attempted there.
"""
from datetime import datetime, timedelta

from chronologia import extract_duration, extract_timespan

LANG = "en"
ANCHOR = datetime(2025, 1, 1, 12, 0, 0)


# ---------------------------------------------------------------------------
# the defect itself: extract_duration on a bare slash fraction
# ---------------------------------------------------------------------------

def test_half_hour_slash():
    r = extract_duration("1/2 hour", LANG)
    assert r.duration == timedelta(minutes=30)
    assert r.remainder == ""


def test_quarter_hour_slash():
    r = extract_duration("1/4 hour", LANG)
    assert r.duration == timedelta(minutes=15)
    assert r.remainder == ""


def test_three_quarter_hour_slash():
    r = extract_duration("3/4 hour", LANG)
    assert r.duration == timedelta(minutes=45)
    assert r.remainder == ""


def test_half_day_slash():
    r = extract_duration("1/2 day", LANG)
    assert r.duration == timedelta(hours=12)
    assert r.remainder == ""


def test_embedded_in_sentence():
    r = extract_duration("wait 1/2 hour before calling back", LANG)
    assert r.duration == timedelta(minutes=30)


def test_three_quarter_embedded():
    r = extract_duration("it took 3/4 hour to cool down", LANG)
    assert r.duration == timedelta(minutes=45)


# ---------------------------------------------------------------------------
# nonsense-denominator policy: SUPPORTED, read as the exact decimal named.
# 5/7 hour = (5/7) * 3600s = 2571.428571... seconds.
# ---------------------------------------------------------------------------

def test_odd_fraction_supported_as_exact_decimal():
    r = extract_duration("5/7 hour", LANG)
    expected = timedelta(seconds=5 / 7 * 3600)
    assert r.duration == expected
    assert r.remainder == ""


# ---------------------------------------------------------------------------
# controls that already worked -- must keep working identically
# ---------------------------------------------------------------------------

def test_control_half_an_hour_words():
    r = extract_duration("half an hour", LANG)
    assert r.duration == timedelta(minutes=30)
    assert r.remainder == ""


def test_control_quarter_of_an_hour_words():
    r = extract_duration("quarter of an hour", LANG)
    assert r.duration == timedelta(minutes=15)
    assert r.remainder == ""


def test_control_hour_and_a_half_words():
    r = extract_duration("an hour and a half", LANG)
    assert r.duration == timedelta(hours=1, minutes=30)
    assert r.remainder == ""


# ---------------------------------------------------------------------------
# extract_timespan compositions ("N/D unit" as a relative offset)
# ---------------------------------------------------------------------------

def test_timespan_half_hour_ago():
    r = extract_timespan("1/2 hour ago", LANG, anchor=ANCHOR)
    assert r is not None
    assert r.remainder == ""
    assert r.span.start_datetime == ANCHOR - timedelta(minutes=30)


def test_timespan_in_half_hour():
    r = extract_timespan("in 1/2 hour", LANG, anchor=ANCHOR)
    assert r is not None
    assert r.remainder == ""
    assert r.span.start_datetime == ANCHOR + timedelta(minutes=30)


# ---------------------------------------------------------------------------
# date-slash pins -- must NOT be touched by the fraction fold
# ---------------------------------------------------------------------------

def test_pin_numeric_date_month_first():
    # en is month-first: 01/02/2025 = January 2nd, 2025.
    r = extract_timespan("01/02/2025", LANG, anchor=ANCHOR)
    assert r is not None
    assert r.span.start_datetime == datetime(2025, 1, 2)
    assert r.remainder == ""


def test_pin_numeric_date_month_first_single_digit():
    # 3/4/2025 = March 4th, 2025 (month-first), NOT a fraction reading.
    r = extract_timespan("3/4/2025", LANG, anchor=ANCHOR)
    assert r is not None
    assert r.span.start_datetime == datetime(2025, 3, 4)
    assert r.remainder == ""


def test_pin_bare_slash_pair_is_not_a_date():
    # "3/4" alone (no year component) does not resolve to a date either
    # before or after this fix -- pinning the existing behaviour so the
    # fraction fold is not later blamed for a pre-existing refusal.
    assert extract_timespan("3/4", LANG, anchor=ANCHOR) is None


def test_pin_on_bare_slash_pair_is_not_a_date():
    assert extract_timespan("on 3/4", LANG, anchor=ANCHOR) is None
