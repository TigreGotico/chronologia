"""EDTF <-> DateSpan: spec-example corpus, hand-derived golds, round-trips.

Every string in ``SPEC_EXAMPLES`` is an example lifted verbatim from the
Library of Congress EDTF specification
(https://www.loc.gov/standards/datetime/, spec dated 2019-02-04); the
comment on each names the level and section it comes from.  The golds are
hand-derived from the spec's prose, never from the parser's own output.
"""
import pytest

from chronologia import (AstroDate, DateSpan, EdtfDate, EdtfParseError,
                         format_edtf, parse_edtf)
from chronologia.astrodate import BASIS_EXACT, BASIS_RECONSTRUCTED


def _span(*a):
    """(y,m,d,...) start / end shorthand -> AstroDate, for gold spans."""
    return AstroDate(*a)


# --------------------------------------------------------------------------
# The spec-example corpus: every worked example string in the LoC spec that
# maps to a single contiguous span.  (index -> (string, level, note)).
# --------------------------------------------------------------------------

SPEC_EXAMPLES = [
    # -- Level 0: date -----------------------------------------------------
    "1985-04-12", "1985-04", "1985",
    # -- Level 0: date and time -------------------------------------------
    "1985-04-12T23:20:30", "1985-04-12T23:20:30Z",
    "1985-04-12T23:20:30-04", "1985-04-12T23:20:30+04:30",
    # -- Level 0: time interval -------------------------------------------
    "1964/2008", "2004-06/2006-08", "2004-02-01/2005-02-08",
    "2004-02-01/2005-02", "2004-02-01/2005", "2005/2006-02",
    # -- Level 1: letter-prefixed / negative years ------------------------
    "Y170000002", "Y-170000002", "-1985",
    # -- Level 1: seasons --------------------------------------------------
    "2001-21",
    # -- Level 1: qualification of a date ---------------------------------
    "1984?", "2004-06~", "2004-06-11%",
    # -- Level 1: unspecified digit(s) from the right ---------------------
    "201X", "20XX", "2004-XX", "1985-04-XX", "1985-XX-XX",
    # -- Level 1: extended interval (open end) ----------------------------
    "1985-04-12/..", "1985-04/..", "1985/..",
    # -- Level 1: extended interval (open start) --------------------------
    "../1985-04-12", "../1985-04", "../1985",
    # -- Level 1: extended interval (unknown end) -------------------------
    "1985-04-12/", "1985-04/", "1985/",
    # -- Level 1: extended interval (unknown start) -----------------------
    "/1985-04-12", "/1985-04", "/1985",
    # -- Level 2: exponential year ----------------------------------------
    "Y-17E7", "Y17E7",
    # -- Level 2: significant digits --------------------------------------
    "1950S2", "Y171010000S3", "Y3388E2S3",
    # -- Level 2: sub-year groupings --------------------------------------
    "2001-34",
    # -- Level 2: unspecified digit anywhere ------------------------------
    "1984-1X",
    # -- Level 2: interval with approximate/unspecified components --------
    "2004-06-~01/2004-06-~20", "2004-06-XX/2004-07-03",
    # -- Level 2: group / individual qualification ------------------------
    "2004-06-11%", "2004-06~-11", "2004?-06-11",
    "?2004-06-~11", "2004-%06-11",
    # -- set-representation example endpoints (as standalone dates) -------
    "1667", "1668", "1760-12", "1760-12-03", "1760-01", "1760-02",
    "1960", "1961-12", "1984", "1670", "1671", "1672",
]


def test_corpus_size():
    """The harvested spec-example corpus is large (spec asks 60+)."""
    assert len(SPEC_EXAMPLES) >= 60


@pytest.mark.parametrize("s", SPEC_EXAMPLES)
def test_every_spec_example_parses(s):
    ed = parse_edtf(s)
    assert isinstance(ed, EdtfDate)
    assert isinstance(ed.span, DateSpan)


@pytest.mark.parametrize("s", SPEC_EXAMPLES)
def test_round_trip_parse_format_parse(s):
    """parse . format . parse == parse (the span is invariant)."""
    ed = parse_edtf(s)
    reparsed = parse_edtf(format_edtf(ed))
    assert reparsed.span == ed.span


# --------------------------------------------------------------------------
# Hand-derived golds (from the spec's prose, not the parser).
# --------------------------------------------------------------------------

GOLDS = [
    # Level 0 dates: day / month / year precision.
    ("1985-04-12", _span(1985, 4, 12), _span(1985, 4, 13)),
    ("1985-04", _span(1985, 4, 1), _span(1985, 5, 1)),
    ("1985", _span(1985, 1, 1), _span(1986, 1, 1)),
    # Level 0 intervals: [start-of-start, end-of-end].
    ("1964/2008", _span(1964, 1, 1), _span(2009, 1, 1)),
    ("2004-06/2006-08", _span(2004, 6, 1), _span(2006, 9, 1)),
    ("2004-02-01/2005-02-08", _span(2004, 2, 1), _span(2005, 2, 9)),
    ("2005/2006-02", _span(2005, 1, 1), _span(2006, 3, 1)),
    # Level 1 seasons (Northern-Hemisphere meteorological convention).
    ("2001-21", _span(2001, 3, 1), _span(2001, 6, 1)),    # Spring
    ("2001-24", _span(2001, 12, 1), _span(2002, 3, 1)),   # Winter -> next year
    # Level 1 unspecified digits.
    ("201X", _span(2010, 1, 1), _span(2020, 1, 1)),       # the 2010s
    ("20XX", _span(2000, 1, 1), _span(2100, 1, 1)),       # the 2000s (century)
    ("156X", _span(1560, 1, 1), _span(1570, 1, 1)),       # the 1560s
    ("2004-XX", _span(2004, 1, 1), _span(2005, 1, 1)),    # unknown month
    ("1985-04-XX", _span(1985, 4, 1), _span(1985, 5, 1)),  # unknown day
    ("1985-XX-XX", _span(1985, 1, 1), _span(1986, 1, 1)),
    ("1984-1X", _span(1984, 10, 1), _span(1985, 1, 1)),   # Oct/Nov/Dec 1984
    # Level 1 negative & Y-prefix years.
    ("-1985", _span(-1985, 1, 1), _span(-1984, 1, 1)),
    ("Y170000002", _span(170000002, 1, 1), _span(170000003, 1, 1)),
    ("Y-170000002", _span(-170000002, 1, 1), _span(-170000001, 1, 1)),
    # Level 2 exponential year: Y-17E7 == -17 * 10^7 == -170000000.
    ("Y-17E7", _span(-170000000, 1, 1), _span(-169999999, 1, 1)),
    ("Y17E7", _span(170000000, 1, 1), _span(170000001, 1, 1)),
    # Level 2 significant digits: value shares its top S digits.
    ("1950S2", _span(1900, 1, 1), _span(2000, 1, 1)),
    ("Y171010000S3", _span(171000000, 1, 1), _span(172000000, 1, 1)),
    ("Y3388E2S3", _span(338000, 1, 1), _span(339000, 1, 1)),  # 3388E2 == 338800
    # Level 2 sub-year grouping: 34 == quarter 2 (Apr-Jun).
    ("2001-34", _span(2001, 4, 1), _span(2001, 7, 1)),
]


@pytest.mark.parametrize("s,start,end", GOLDS)
def test_parse_gold_spans(s, start, end):
    ed = parse_edtf(s)
    assert ed.span.start == start, s
    assert ed.span.end == end, s


def test_deep_time_flagship_Y170000002():
    """The Y-prefix flagship: a year far outside datetime's 1..9999 window."""
    ed = parse_edtf("Y170000002")
    assert ed.span.start.year == 170000002
    assert not ed.span.start.in_datetime_range
    # It survives a format round trip unchanged.
    assert format_edtf(ed) == "Y170000002"


# --------------------------------------------------------------------------
# Qualifiers -> basis and flags.
# --------------------------------------------------------------------------

def test_uncertain_sets_reconstructed_basis():
    ed = parse_edtf("1984?")
    assert ed.uncertain and not ed.approximate
    assert ed.span.basis == BASIS_RECONSTRUCTED
    assert ed.qualifier == "?"


def test_approximate_sets_reconstructed_basis():
    ed = parse_edtf("2004-06~")
    assert ed.approximate and not ed.uncertain
    assert ed.span.basis == BASIS_RECONSTRUCTED
    assert ed.qualifier == "~"


def test_both_qualifier_percent():
    ed = parse_edtf("2004-06-11%")
    assert ed.uncertain and ed.approximate
    assert ed.qualifier == "%"
    assert ed.span.basis == BASIS_RECONSTRUCTED


def test_no_qualifier_stays_exact():
    ed = parse_edtf("1985-04-12")
    assert not ed.uncertain and not ed.approximate
    assert ed.span.basis == BASIS_EXACT


def test_component_qualifiers_collapse_to_date_flags():
    # '?2004-06-~11' spec: year uncertain; month known; day approximate.
    ed = parse_edtf("?2004-06-~11")
    assert ed.uncertain and ed.approximate  # both present, scope collapsed
    assert ed.span.start == _span(2004, 6, 11)


def test_width_imprecision_does_not_touch_basis():
    # A decade span is imprecise but its endpoints are exact -> basis exact.
    assert parse_edtf("156X").span.basis == BASIS_EXACT
    assert parse_edtf("1950S2").span.basis == BASIS_EXACT
    assert parse_edtf("2001-21").span.basis == BASIS_EXACT


# --------------------------------------------------------------------------
# Datetime and timezone.
# --------------------------------------------------------------------------

def test_datetime_is_one_second_wide():
    ed = parse_edtf("1985-04-12T23:20:30")
    assert ed.span.start == AstroDate(1985, 4, 12, 23, 20, 30)
    assert ed.span.width.total_seconds() == 1.0


def test_datetime_utc_and_offset_are_aware():
    z = parse_edtf("1985-04-12T23:20:30Z").span.start
    off = parse_edtf("1985-04-12T23:20:30-04").span.start
    assert z.utcoffset().total_seconds() == 0
    assert off.utcoffset().total_seconds() == -4 * 3600
    # Same wall clock, different zone -> different instant.
    assert z != off


def test_fractional_seconds_microsecond_wide():
    ed = parse_edtf("1985-04-12T23:20:30.5")
    assert ed.span.start.microsecond == 500000
    assert ed.span.width.total_seconds() == 1e-6


# --------------------------------------------------------------------------
# Open / unknown interval ends.
# --------------------------------------------------------------------------

def test_open_end():
    ed = parse_edtf("1985/..")
    assert ed.open_end and not ed.open_start
    assert ed.span == DateSpan(_span(1985, 1, 1), _span(1986, 1, 1))


def test_open_start():
    ed = parse_edtf("../1985-04")
    assert ed.open_start and not ed.open_end
    assert ed.span == DateSpan(_span(1985, 4, 1), _span(1985, 5, 1))


def test_unknown_end_equals_open_end():
    # EDTF null (unknown) and '..' (open) collapse to the same flag.
    assert parse_edtf("1985/").open_end
    assert parse_edtf("1985/").span == parse_edtf("1985/..").span


def test_unknown_start_equals_open_start():
    assert parse_edtf("/1985").open_start
    assert parse_edtf("/1985").span == parse_edtf("../1985").span


def test_format_open_end_round_trips():
    ed = parse_edtf("1985-04-12/..")
    assert format_edtf(ed) == "1985-04-12/.."


def test_format_open_start_round_trips():
    ed = parse_edtf("../1985")
    assert format_edtf(ed) == "../1985"


# --------------------------------------------------------------------------
# format_edtf: tightest-token selection and inputs.
# --------------------------------------------------------------------------

def test_format_reduced_precision_tokens():
    assert format_edtf(parse_edtf("1985").span) == "1985"
    assert format_edtf(parse_edtf("1985-04").span) == "1985-04"
    assert format_edtf(parse_edtf("1985-04-12").span) == "1985-04-12"
    assert format_edtf(parse_edtf("156X").span) == "156X"
    assert format_edtf(parse_edtf("20XX").span) == "20XX"


def test_format_qualifier_suffix():
    assert format_edtf(parse_edtf("1984?")) == "1984?"
    assert format_edtf(parse_edtf("2004-06~")) == "2004-06~"
    assert format_edtf(parse_edtf("2004-06-11%")) == "2004-06-11%"


def test_format_accepts_astrodate_point():
    assert format_edtf(AstroDate(1985, 4, 12)) == "1985-04-12"
    assert format_edtf(AstroDate(1985, 4, 12, 9, 30, 0)) == "1985-04-12T09:30:00"


def test_format_season_becomes_bounded_interval():
    # Seasons/quarters are parse-only; format emits the equivalent interval.
    assert format_edtf(parse_edtf("2001-21").span) == "2001-03/2001-05"
    assert format_edtf(parse_edtf("2001-34").span) == "2001-04/2001-06"


def test_format_lossy_exponential_and_sig_digits():
    assert format_edtf(parse_edtf("Y17E7").span) == "Y170000000"
    assert format_edtf(parse_edtf("1950S2").span) == "19XX"


def test_format_rejects_unknown_type():
    with pytest.raises(TypeError):
        format_edtf(42)


def test_format_rejects_inexpressible_subday_span():
    span = DateSpan(AstroDate(2000, 1, 1, 0, 0, 0),
                    AstroDate(2000, 1, 1, 5, 0, 0))
    with pytest.raises(ValueError):
        format_edtf(span)


# --------------------------------------------------------------------------
# Non-contiguous valid EDTF -> NotImplementedError (documented).
# --------------------------------------------------------------------------

@pytest.mark.parametrize("s", [
    "156X-12-25",   # spec: Dec 25 sometime in the 1560s (non-contiguous)
    "15XX-12-25",   # spec: Dec 25 sometime in the 1500s
    "XXXX-12-XX",   # spec: some day in December in some year
    "1XXX-12",      # spec: some December during the 1000s
])
def test_noncontiguous_sets_raise_not_implemented(s):
    with pytest.raises(NotImplementedError):
        parse_edtf(s)


@pytest.mark.parametrize("s", ["[1667,1668,1670..1672]", "{1960,1961-12}"])
def test_set_representation_raises_not_implemented(s):
    with pytest.raises(NotImplementedError):
        parse_edtf(s)


def test_noncontiguous_interior_x():
    with pytest.raises(NotImplementedError):
        parse_edtf("1X23")


# --------------------------------------------------------------------------
# Adversarial: malformed strings must raise ValueError (never silent).
# --------------------------------------------------------------------------

@pytest.mark.parametrize("s", [
    "", "   ", "abcd", "1985-13", "1985-00", "1985-04-31",
    "1985-04-00", "1985-4", "1985-004", "19-04", "2004-06-11-07",
    "1985/2000/2010", "//", "/", "..", "../..", "1985 - 04",
    "1985-04 12", "Y", "YE7", "Y17E", "1950S", "1950S0",
    "1985-99", "2004-42", "20-04-11", "T23:20:30",
    "1985-04-12T25:00:00", "1985-04-12T23:70:00", "1985-04-12T",
    "not-a-date",
])
def test_malformed_raises_value_error(s):
    with pytest.raises(ValueError):
        parse_edtf(s)


def test_edtf_parse_error_is_value_error():
    assert issubclass(EdtfParseError, ValueError)


def test_non_string_input_raises():
    with pytest.raises(ValueError):
        parse_edtf(None)
    with pytest.raises(ValueError):
        parse_edtf(1985)


# --------------------------------------------------------------------------
# Public surface.
# --------------------------------------------------------------------------

def test_exports_present():
    import chronologia
    for name in ("parse_edtf", "format_edtf", "EdtfDate", "EdtfParseError"):
        assert name in chronologia.__all__
        assert hasattr(chronologia, name)


def test_edtfdate_is_frozen():
    ed = parse_edtf("1985")
    with pytest.raises(Exception):
        ed.uncertain = True


@pytest.mark.parametrize("s,lo,hi", [
    ("-19XX", -1999, -1899),   # negative + trailing-X used to crash (sign inverted lo/hi)
    ("-156X", -1569, -1559),
    ("199X", 1990, 2000),      # positive unchanged
    ("-1985", -1985, -1984),   # plain negative unchanged
])
def test_negative_year_with_unspecified_digits_parses(s, lo, hi):
    d = parse_edtf(s)
    assert d is not None
    assert d.span.start.year == lo and d.span.end.year == hi


@pytest.mark.parametrize("s", [
    "2001-13-01", "2001-99-01", "2001-14-15", "2001-00-01",   # EC1: bad month in Y-M-D
    "1985-01-01T25:00:00", "1985-01-01T00:60:00",             # EC2: bad time-of-day
    "1985-01-01T00:00:60", "1985-01-01T00:00:00+99:00",       # EC2: bad second / offset
    "9999-99-99T00:00:00",
])
def test_out_of_range_components_raise_edtf_parse_error_not_bare(s):
    # The documented contract is EdtfParseError for malformed input; these used
    # to leak a bare IndexError (Y-M-D month) / ValueError (datetime component).
    with pytest.raises(EdtfParseError):
        parse_edtf(s)


def test_mixed_granularity_forward_interval_accepted():
    # A forward interval whose right endpoint is COARSER than the left
    # ("2004-06/2004" = June 2004 through the end of 2004) is a valid ISO 8601-2
    # interval; the year's own start precedes June's, but the resolved span
    # [2004-06-01, 2005-01-01) is non-empty. Regression: the reversed-interval
    # guard compared the two START instants and wrongly rejected it.
    import datetime as _dt
    for s, start, end in [
        ("2004-06/2004", _dt.date(2004, 6, 1), _dt.date(2005, 1, 1)),
        ("2004-11/2004", _dt.date(2004, 11, 1), _dt.date(2005, 1, 1)),
        ("2004-06-15/2004", _dt.date(2004, 6, 15), _dt.date(2005, 1, 1)),
    ]:
        r = parse_edtf(s)
        assert (r.span.start.date(), r.span.end.date()) == (start, end), s
    # genuinely reversed / zero-width intervals are still rejected
    for s in ("2004-01/2003-12", "2004/2003", "2004-06/2004-05"):
        with pytest.raises(EdtfParseError):
            parse_edtf(s)
