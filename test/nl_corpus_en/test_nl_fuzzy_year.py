"""Fuzzy narrowing of a bare calendar year -- "early/mid/late <year>".

A bare year resolves to the whole year ``[Jan 1 y, Jan 1 y+1)``.  Prefixing
it with a fuzzy period-part word (en "early/mid/late", also the hyphenated
"mid-2017") NARROWS that year to the corresponding third, honestly expressing
the speaker's uncertainty as a span rather than fabricating a precise point.

Convention (the standard English "early/mid/late" division of a period): the
year is cut into three equal parts -- the first, middle and last third.  This
is the SAME machinery decade fuzzy ("early 1980s") and month fuzzy ("late
december") already use: :func:`chronologia.subdivide`, which slices by equal
elapsed time.  For a 365-day year the cuts therefore fall at 1/3 and 2/3 of
the year -- ~early May and ~early September (early 2017: Jan 1 .. May 2 16:00;
mid: May 2 16:00 .. Sep 1 08:00; late: Sep 1 08:00 .. Jan 1) -- the common-
usage "early = first part / mid = middle / late = last part" reading.

Regression: on dev these stranded the qualifier and returned the WHOLE year
("late 2017" -> 2017-01-01..2018-01-01, remainder "late") -- a silent-wrong,
because the user narrowed the year and the parser ignored it.
"""
import datetime as _dt

import pytest

from ._corpus import AstroDate, parse, span, start_end


def _thirds(y):
    """The three equal-time thirds of calendar year ``y``, computed by
    independent date arithmetic (does NOT touch the parser)."""
    s = _dt.datetime(y, 1, 1)
    e = _dt.datetime(y + 1, 1, 1)
    tot = int((e - s).total_seconds() * 1_000_000)
    b1 = s + _dt.timedelta(microseconds=tot * 1 // 3)
    b2 = s + _dt.timedelta(microseconds=tot * 2 // 3)
    def ad(d):
        return AstroDate(d.year, d.month, d.day, d.hour, d.minute,
                         d.second, d.microsecond)
    return ad(s), ad(b1), ad(b2), ad(e)


@pytest.mark.parametrize("year", [2017, 2018])
@pytest.mark.parametrize("part_idx,part_words", [
    (0, ["early"]),
    (1, ["mid"]),
    (2, ["late"]),
])
def test_fuzzy_year_thirds(year, part_idx, part_words):
    s, b1, b2, e = _thirds(year)
    bounds = [(s, b1), (b1, b2), (b2, e)][part_idx]
    for word in part_words:
        ss, ee = start_end(f"{word} {year}")
        assert (ss, ee) == bounds, f"{word} {year}"


def test_fuzzy_year_hyphenated_mid():
    # "mid-2017" tokenizes to PART + GYEAR just like "mid 2017"
    _, b1, b2, _ = _thirds(2017)
    ss, ee = start_end("mid-2017")
    assert (ss, ee) == (b1, b2)


def test_fuzzy_year_thirds_are_contiguous():
    # the three thirds tile the whole year with no gap or overlap
    early = start_end("early 2017")
    mid = start_end("mid 2017")
    late = start_end("late 2017")
    assert early[0] == AstroDate(2017, 1, 1)
    assert early[1] == mid[0]
    assert mid[1] == late[0]
    assert late[1] == AstroDate(2018, 1, 1)


@pytest.mark.parametrize("text", [
    "early 2018", "mid 2017", "late 2017", "mid-2017", "early 2017", "late 2018",
])
def test_fuzzy_year_does_not_strand_qualifier(text):
    # the whole-year silent-wrong left the qualifier in the remainder
    r = parse(text)
    assert r is not None
    remainder = r[1] or ""
    for q in ("early", "mid", "late"):
        assert q not in remainder.lower(), f"{text!r} stranded {q!r}: {r!r}"


@pytest.mark.parametrize("text", [
    "early 2017", "mid 2017", "late 2017",
])
def test_fuzzy_year_is_narrower_than_whole_year(text):
    s = span(text)
    # each third is roughly a third of a year, never the whole year
    assert 100 <= s.width.days <= 130
