"""R90: a remainder-integrity defect class -- correct spans, but the leading
article silently stranded in the remainder instead of being consumed.

Three base orders in ``chronologia/extract/base_grammar.py`` and one
per-locale order in ``chronologia/locale/en/lang.json`` were missing a
leading ``article?``, even though every sibling/postposed order around them
already carried one:

* ``rel_span``          ("REL_MARKER NUM UNIT")          -- "the next 3 weeks"
* ``rel_span_quarter``  ("REL_MARKER NUM quarter_word")  -- "the next 2 quarters"
* ``rel_span_weekend``  ("REL_MARKER NUM WEEKEND")        -- "the next 3 weekends"
* ``calendar_date``'s bare "DAY of MONTH YEAR? ERA?" / "DAY MONTH YEAR? ERA?"
  / "MONTH DAY? YEAR? ERA?" orders (en) -- "the 1st of january 1999"

Because ``rel_span``/``rel_span_quarter``/``rel_span_weekend`` live in the
SHARED base grammar, the fix benefits every locale that uses the
marker-first order, not just English -- see the es/it/gl/pt/ca sibling test
files (``test_nl_rel_span_quarters_weekends.py``) for the per-locale
article-led marker-first cases.

None of this changes resolution semantics: every span below is bit-for-bit
identical before and after the fix (verified against the pre-existing
``test_nl_rel_span_quarters_weekends.py`` / ``test_nl_era_composition.py``
golds, computed independently there) -- only the leading article moves from
the remainder into the consumed match.

Anchor: Tuesday 2017-06-27 13:04 (matches ``_corpus.py``'s ``ANCHOR``, the
shared en corpus anchor), except where a test needs a different anchor to
line up with a sibling file's independently-computed golds (noted inline).
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, parse, start_end

# The rel_span_quarter/rel_span_weekend siblings' golds below are pinned to
# the SAME anchor as ``test_nl_rel_span_quarters_weekends.py`` (Wednesday
# 2026-08-05 12:00) so the expected spans can be cross-checked against that
# file's independently hand-computed values without re-deriving them here.
B = datetime(2026, 8, 5, 12, 0)


def _at(text, anchor):
    r = extract_timespan(text, "en", anchor)
    assert r is not None, f"{text!r} did not parse"
    return r


# -- rel_span: "the next/last N weeks" --------------------------------------

@pytest.mark.parametrize("text,s,e", [
    ("the next 3 weeks", AstroDate(2026, 8, 5), AstroDate(2026, 8, 26)),
])
def test_rel_span_article_consumed(text, s, e):
    r = _at(text, B)
    assert (r.span.start, r.span.end) == (s, e), text
    assert r.remainder == "", (text, r.remainder)


# -- rel_span_quarter: "the next/last N quarters" ---------------------------

@pytest.mark.parametrize("text,s,e", [
    ("the next 2 quarters", AstroDate(2026, 10, 1), AstroDate(2027, 4, 1)),
    ("the last 2 quarters", AstroDate(2026, 1, 1), AstroDate(2026, 7, 1)),
])
def test_rel_span_quarter_article_consumed(text, s, e):
    r = _at(text, B)
    assert (r.span.start, r.span.end) == (s, e), text
    assert r.remainder == "", (text, r.remainder)


# -- rel_span_weekend: "the next/last N weekends" ---------------------------

@pytest.mark.parametrize("text,s,e", [
    ("the next 3 weekends", AstroDate(2026, 8, 8), AstroDate(2026, 8, 24)),
    ("the next 10 weekends", AstroDate(2026, 8, 8), AstroDate(2026, 10, 12)),
])
def test_rel_span_weekend_article_consumed(text, s, e):
    r = _at(text, B)
    assert (r.span.start, r.span.end) == (s, e), text
    assert r.remainder == "", (text, r.remainder)


# -- calendar_date with era (#644) and plain (control) ----------------------

def test_calendar_date_era_article_consumed():
    assert parse("the 1st of january 500 BC")[1] == ""
    assert parse("the 15th of march 44 BC")[1] == ""


def test_calendar_date_plain_article_consumed():
    # the bare (non-era) form uses the same order -- it strands "the" too,
    # confirming this is an order-level defect, not era-specific.
    s, e = start_end("the 1st of january 1999")
    assert s == AstroDate(1999, 1, 1)
    assert e == AstroDate(1999, 1, 2)
    assert parse("the 1st of january 1999")[1] == ""


# -- controls: bare (article-less) forms unchanged ---------------------------

@pytest.mark.parametrize("text,s,e", [
    ("next 3 weeks", AstroDate(2026, 8, 5), AstroDate(2026, 8, 26)),
    ("next 2 quarters", AstroDate(2026, 10, 1), AstroDate(2027, 4, 1)),
    ("next 3 weekends", AstroDate(2026, 8, 8), AstroDate(2026, 8, 24)),
])
def test_bare_forms_unchanged(text, s, e):
    r = _at(text, B)
    assert (r.span.start, r.span.end) == (s, e), text
    assert r.remainder == "", (text, r.remainder)


def test_bare_calendar_date_unchanged():
    s, e = start_end("1st of january 1999")
    assert s == AstroDate(1999, 1, 1)
    assert e == AstroDate(1999, 1, 2)
    assert parse("1st of january 1999")[1] == ""


# -- controls: other article-bearing idioms unaffected -----------------------

def test_day_after_tomorrow_unaffected():
    r = parse("the day after tomorrow")
    assert r is not None
    assert r[1] == ""


def test_singular_rel_period_unaffected():
    # "the next quarter" / "the next weekend" go through rel_period /
    # weekday_ref-family constructions this fix does not touch; they never
    # carried a leading article? in the base grammar and still don't --
    # unchanged, "the" still stranded there (a pre-existing, separate,
    # out-of-scope surface this PR does not fix).
    r = _at("the next quarter", B)
    assert (r.span.start, r.span.end) == (AstroDate(2026, 10, 1), AstroDate(2027, 1, 1))
    assert r.remainder == "the"


# -- control: "the" inside non-matching text stays in the remainder ----------

def test_unrelated_the_stays_in_remainder():
    r = _at("the meeting next week", B)
    assert r.remainder == "the meeting"
