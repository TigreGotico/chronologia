"""R77 -- anchored offsets composed onto a BC/BCE reference must resolve in
AstroDate's own proleptic (astronomical) year space, never round-trip through
stdlib ``datetime`` (``MINYEAR == 1``).

Confirmed live crash on dev (ea224b41): ``extract_timespan('2000 years
before 500 BC')`` raised an uncaught ``ValueError('year -499 is out of
range')`` from ``anchored._try_offset`` building ``datetime(s.year, ...)``
with a proleptic-negative year.  Extractors are documented to never raise.

Expected years are derived independently, astronomical numbering (chronologia
already establishes -- see ``test_nl_eras_deep_time.test_bc`` -- that BC/BCE
maps ``year -> 1 - n``, i.e. "1 BC" == year 0, "44 BC" == year -43):

    500 BC  == year -499;  -499 - 2000 == -2499  ("2000 years before 500 BC")
    44 BCE  == year  -43;   -43 +  300 ==   257  ("3 centuries after 44 BCE")
    44 BC   == year  -43;   -43 -  100 ==  -143  ("100 years before 44 BC")
"""
import pytest

from ._corpus import AstroDate, nomatch, parse, span, start

from datetime import date, timedelta


# -- the three confirmed crash repros --------------------------------------

@pytest.mark.parametrize("text,year", [
    ("2000 years before 500 BC", -2499),
    ("3 centuries after 44 BCE", 257),
    ("100 years before 44 BC", -143),
])
def test_bc_offset_no_longer_raises(text, year):
    # must not raise -- extractors are documented to never raise.
    result = parse(text)
    assert result is not None, f"{text!r} did not parse (expected a span)"
    assert start(text) == AstroDate(year, 1, 1, 0, 0, 0, 0)


# -- controls: ordinary (non-BC) offset composition is unchanged ----------

CHRISTMAS = date(2017, 12, 25)


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


def test_control_weeks_after_christmas_unchanged():
    assert start("2 weeks after christmas") == _ad(CHRISTMAS + timedelta(days=14))


def test_control_days_before_june5_unchanged():
    # "june 5" with no year resolves to the next occurrence on/after the
    # anchor (2017-06-27) -> 2018-06-05; 3 days before it.
    assert start("3 days before june 5") == AstroDate(2018, 6, 2)


def test_control_plain_bc_unchanged():
    assert start("500 BC") == AstroDate(-499, 1, 1)


def test_control_deep_time_unchanged():
    assert start("66 million years ago").year == 1950 - 66_000_000


# -- bare-year_ref offset anchor (same family: the offset pass silently
# stranded "N years before/after" when the reference was a plain calendar
# year -- "year_ref" was simply missing from DATE_CONSTRUCTIONS, so
# _one_offset_pass skipped it, and the bare year_ref match survived
# untouched -> a confidently WRONG non-None span (2020, whole-year) with the
# offset words dumped in the remainder instead of composed.  Convention
# (matches the BC fix and the "100 years before june 2020" case already on
# dev): the offset shifts the reference's START, result is DAY-WIDE at that
# shifted start -- not year-wide. ------------------------------------------

@pytest.mark.parametrize("text,year", [
    ("100 years before 2020", 1920),
    ("2 years after 1990", 1992),
    ("a century after 1900", 2000),
])
def test_year_ref_offset_composes(text, year):
    result = parse(text)
    assert result is not None, f"{text!r} did not parse (expected a span)"
    span_, remainder = result
    assert remainder == "", f"{text!r} left a remainder: {remainder!r}"
    assert span_.start == AstroDate(year, 1, 1)
    assert span_.end == AstroDate(year, 1, 2)  # day-wide, not year-wide


# -- controls: bare-year reading itself, and adjacent constructs, unchanged -

def test_control_plain_year_unchanged():
    s, e = span("2020").start, span("2020").end
    assert s == AstroDate(2020, 1, 1) and e == AstroDate(2021, 1, 1)


def test_control_the_year_2020_unchanged():
    s, e = span("the year 2020").start, span("the year 2020").end
    assert s == AstroDate(2020, 1, 1) and e == AstroDate(2021, 1, 1)


def test_control_in_2020_unchanged():
    s, e = span("in 2020").start, span("in 2020").end
    assert s == AstroDate(2020, 1, 1) and e == AstroDate(2021, 1, 1)


def test_control_offset_before_month_year_unchanged():
    # a year_ref carrying a MONTH ("june 2020") is calendar_date, not
    # year_ref -- already composed on dev; must stay day-wide and correct.
    assert start("100 years before june 2020") == AstroDate(1920, 6, 1)


def test_control_years_before_then_unaffected():
    # "then"/"now" are relative anchors, not a year_ref match -- must not be
    # swept up by widening DATE_CONSTRUCTIONS to include year_ref.
    nomatch("3 years before then")


def test_control_era_bc_offset_still_works():
    # the R77 BC fix itself, re-asserted alongside the year_ref fix.
    assert start("100 years before 44 BC") == AstroDate(-143, 1, 1)


# -- probe: extract_duration on the same phrases pins current behaviour ---
# (dev already returns None for these -- an anchored offset onto an era
# reference is not a bounded "duration"; this fix is scoped to extract_timespan
# and must not change extract_duration's behaviour.)

@pytest.mark.parametrize("text", [
    "2000 years before 500 BC",
    "3 centuries after 44 BCE",
    "100 years before 44 BC",
    "2 weeks after christmas",
    "3 days before june 5",
])
def test_duration_probe_pinned(text):
    from chronologia import extract_duration
    if text in ("2 weeks after christmas", "3 days before june 5"):
        assert extract_duration(text) is not None
    else:
        assert extract_duration(text) is None
