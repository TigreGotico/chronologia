"""R131: comma glued to digits with no following space must never corrupt
number tokenization into a silent-wrong span or duration.

The tokenizer's grouping regex (``chronologia/extract/tokenizer.py``) is
locale-aware: en groups thousands with ',' and reads '.' as the decimal
point, de/pl (comma-decimal locales) do the reverse.  Two bugs shared one
root cause -- a digit run glued straight onto a comma with no space, where
what follows the comma is NOT a valid grouping for the locale:

* ``extract_timespan("march5,2025", "en")`` used to read the year as
  **5202**: the grouped alternative only required ONE exactly-three-digit
  group after the comma and had no requirement that nothing else follow, so
  it greedily matched "5,202" out of "5,2025", folded it to 5202, and
  stranded a bare "5" as a separate token right after.
* ``extract_duration("2,5 hours", "en")`` used to read **5 hours**: "2,5"
  is not a valid en grouping (a single digit after the comma is not a
  three-digit group) so the tokenizer already split it into two separate
  number tokens "2" and "5" -- but the duration matcher bound the "5"
  token, the one adjacent to "hours", and silently dropped the "2".

Chosen policy (documented, not merely implied by the assertions below):
en does not read a bare, space-less "<D>,<YYYY>" as day+year -- the fix
withdraws the NUMBER READING of both digit runs on either side of an
invalid glue, so the date extractor is left with no day/year numbers to
bind and degrades to the month-only span it can still support, with the
untouched "day,year" text kept verbatim in the remainder.  The duration
case has nothing left to support at all, so it refuses outright (returns
None).  Either way, the two invariants that matter are enforced:
year is NEVER silently corrupted (never 5202, never a truncated/glued
value), and no valid year is ever silently dropped -- if a year can't be
read confidently, it must show up in the remainder, not vanish.

de and pl are genuinely comma-decimal, so "2,5 hours"/"godziny" must keep
meaning 2.5 -- pinned here as controls so the en-only fix cannot regress
them.
"""
from datetime import timedelta

from chronologia.extract import extract_duration, extract_timespan

from ._corpus import ANCHOR


# ---------------------------------------------------------------------------
# extract_timespan("en") -- comma glued directly to the year, no space
# ---------------------------------------------------------------------------

def test_month_day_comma_year_no_space_never_reads_year_5202():
    r = extract_timespan("march5,2025", "en", ANCHOR)
    assert r is not None
    span, remainder = r
    # the historical defect: year folded to 5202 with the day silently
    # dropped as an unrelated stray token
    assert span.start.year != 5202
    assert span.end.year != 5202
    # policy: degrades to the month-only span chronologia can still stand
    # behind; the ungrounded "day,year" text is NOT silently discharged
    assert (span.start.year, span.start.month, span.start.day) == (2017, 3, 1)
    assert "2025" in remainder or remainder == "5,2025"


def test_month_spaced_day_comma_glued_year_never_reads_year_5202():
    # space after the month, but the comma-to-year glue is still bare
    r = extract_timespan("march 5,2025", "en", ANCHOR)
    assert r is not None
    span, remainder = r
    assert span.start.year != 5202
    assert span.end.year != 5202
    assert (span.start.year, span.start.month, span.start.day) == (2017, 3, 1)
    assert "2025" in remainder


def test_month_day_comma_two_digit_year_no_space_never_drops_the_year():
    # historical defect: read as 2027-03-05 with "25" stranded in the
    # remainder -- a full, confident (and WRONG) date with the two-digit
    # year silently discarded
    r = extract_timespan("march5,25", "en", ANCHOR)
    assert r is not None
    span, remainder = r
    assert (span.start.year, span.start.month, span.start.day) == (2017, 3, 1)
    # the "25" must be visible in the remainder, never silently absorbed
    # into a full, wrong date
    assert "25" in remainder


def test_month_two_digit_day_comma_year_no_space_no_silent_wrong_date():
    r = extract_timespan("march12,2025", "en", ANCHOR)
    if r is None:
        return
    span, remainder = r
    assert span.start.year != 5212
    assert (span.start.year, span.start.month, span.start.day) == (2017, 3, 1)
    assert "2025" in remainder


def test_month_25_day_comma_year_no_space_no_silent_wrong_date():
    r = extract_timespan("march25,2025", "en", ANCHOR)
    if r is None:
        return
    span, remainder = r
    assert span.start.year != 5225
    assert (span.start.year, span.start.month, span.start.day) == (2017, 3, 1)
    assert "2025" in remainder


def test_month_day_comma_space_year_control_still_reads_cleanly():
    """Control: the normal spaced US form is untouched by the fix."""
    r = extract_timespan("march 5, 2025", "en", ANCHOR)
    assert r is not None
    span, remainder = r
    assert (span.start.year, span.start.month, span.start.day) == (2025, 3, 5)
    assert remainder == ""


# ---------------------------------------------------------------------------
# extract_duration("en") -- comma glued mid-number is not a valid en
# grouping or decimal, so the fold must be refused rather than silently
# picking one side
# ---------------------------------------------------------------------------

def test_invalid_comma_glued_number_refuses_duration_fold():
    # historical defect: read as 5 hours with the leading "2" dropped
    r = extract_duration("2,5 hours", "en")
    assert r is None


def test_valid_en_thousands_grouping_control_still_works():
    """Control: a real en thousands grouping keeps folding correctly."""
    r = extract_duration("1,000 days", "en")
    assert r is not None
    duration, remainder = r
    assert duration == timedelta(days=1000)
    assert remainder == ""


# ---------------------------------------------------------------------------
# de / pl controls -- genuinely comma-decimal locales must be unaffected
# ---------------------------------------------------------------------------

def test_de_comma_decimal_duration_control_unaffected():
    r = extract_duration("2,5 Stunden", "de")
    assert r is not None
    duration, remainder = r
    assert duration == timedelta(hours=2, minutes=30)
    assert remainder == ""


def test_pl_comma_decimal_duration_control_unaffected():
    r = extract_duration("1,5 godziny", "pl")
    assert r is not None
    duration, remainder = r
    assert duration == timedelta(hours=1, minutes=30)
    assert remainder == ""
