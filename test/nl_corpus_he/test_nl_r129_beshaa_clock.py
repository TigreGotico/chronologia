# -*- coding: utf-8 -*-
"""R129: the digit/spelled 'בשעה N' clock phrase ("at hour N") did not bind
as a clock_time at all -- ``clock_time``'s ``at? HOUR MERIDIEM ZONE?`` order
made the MERIDIEM slot MANDATORY while leaving the ``at`` marker (which
``בשעה``/``השעה`` already satisfy) optional, so a bare hour with no
am/pm word ("בשעה 9") never matched and the marker+hour tokens fell straight
into the remainder.  Once a date shared the sentence ("ביום שלישי בשעה 9"),
the stranded clock could not compose onto it either.

Mirroring en's ``at HOUR MERIDIEM? ZONE?`` order (marker required, meridiem
optional) lets ``בשעה N`` bind on its own.  That in turn re-enables
:func:`chronologia.extract.resolver.compose_daypart_clock` (the R117/PR#678
daypart-as-meridiem fix): a leading vague day-part ("בערב"/"בבוקר") no
longer wins outright over a stranded explicit hour -- it now supplies the
meridiem for it ("בערב בשעה 9" -> 21:00, not the coarse 18:00-22:00 band).

Gold values are hand-derived from the mission anchor (Tuesday 2017-06-27
13:04); the next Tuesday is 2017-07-04.  Never read back from the parser.
"""
from ._corpus import ANCHOR, ad, nomatch, parse, span, start


def clk(y, m, d, h, mi):
    return ad(ANCHOR.replace(year=y, month=m, day=d, hour=h, minute=mi,
                              second=0, microsecond=0))


# -- bare clock, no date in the sentence --------------------------------
# anchor is 13:04; 09:00 has already passed today, so prefer_future rolls
# to tomorrow (2017-06-28).
def test_bare_digit_binds_and_rolls_to_tomorrow():
    r = parse("בשעה 9")
    assert r is not None, "'בשעה 9' did not parse (R129: clock never bound)"
    assert r.remainder == ""
    assert r.span.start == clk(2017, 6, 28, 9, 0)


def test_bare_spelled_binds_same_as_digit():
    # 'תשע' (spelled nine) folds to the digit 9 upstream of the grammar fix
    # (numfold_semitic); confirms the new order isn't digit-only by accident.
    r = parse("בשעה תשע")
    assert r is not None, "'בשעה תשע' did not parse"
    assert r.remainder == ""
    assert r.span.start == clk(2017, 6, 28, 9, 0)


def test_bare_clock_with_explicit_colon_unchanged():
    # was already working pre-fix -- guards against regressing the existing
    # "at? CLOCK ..." order while adding the new HOUR order.
    r = parse("בשעה 21:00")
    assert r is not None
    assert r.remainder == ""
    assert r.span.start == clk(2017, 6, 27, 21, 0)


# -- date + bare clock composition ---------------------------------------
def test_weekday_plus_digit_clock_composes_with_empty_remainder():
    r = parse("ביום שלישי בשעה 9")
    assert r is not None, "R129: clock stranded, date+clock never composed"
    assert r.remainder == ""
    assert r.span.start == clk(2017, 7, 4, 9, 0)


# -- daypart-as-meridiem composition (PR #678 pattern) --------------------
def test_evening_daypart_overrides_coarse_band_to_pinpoint_2100():
    r = parse("ביום שלישי בערב בשעה 9")
    assert r is not None
    assert r.remainder == "", (
        "R129: coarse evening band must not beat the explicit hour and "
        "strand 'בשעה 9' in the remainder")
    assert r.span.start == clk(2017, 7, 4, 21, 0)
    assert r.span.width.total_seconds() == 60, (
        "expected a minute-wide pinpoint clock, not the 4h evening band")


def test_morning_daypart_composes_to_0900():
    r = parse("ביום שלישי בבוקר בשעה 9")
    assert r is not None
    assert r.remainder == ""
    assert r.span.start == clk(2017, 7, 4, 9, 0)


def test_evening_daypart_meridiem_spelled_hour():
    r = parse("ביום שלישי בערב בשעה תשע")
    assert r is not None
    assert r.remainder == ""
    assert r.span.start == clk(2017, 7, 4, 21, 0)


def test_evening_daypart_clock_composes_inside_embedded_sentence():
    r = parse("ניפגש ביום שלישי בערב בשעה תשע בבית קפה")
    assert r is not None
    assert r.span.start == clk(2017, 7, 4, 21, 0)
    # the date+daypart+clock tokens are all consumed; only the unrelated
    # surrounding words remain.
    assert "בשעה" not in r.remainder
    assert "בערב" not in r.remainder
    assert "שלישי" not in r.remainder


def test_morning_daypart_clock_composes_inside_embedded_sentence():
    r = parse("אתקשר אליך בשעה 9 בבוקר")
    assert r is not None
    assert r.span.start == clk(2017, 6, 28, 9, 0)
    assert "בשעה" not in r.remainder
    assert "בבוקר" not in r.remainder


# -- controls: must stay exactly as before this fix -----------------------
def test_bare_evening_band_unchanged():
    r = parse("בערב")
    assert r is not None
    assert r.remainder == ""
    assert r.span.start == clk(2017, 6, 27, 18, 0)
    assert r.span.width.total_seconds() == 4 * 3600, (
        "a lone 'בערב' with no clock must stay the coarse 4h band")


def test_date_only_sentence_unchanged():
    assert start("ביום שלישי") == clk(2017, 7, 4, 0, 0)
    assert span("ביום שלישי").width.total_seconds() == 24 * 3600


def test_shaa_as_plain_noun_not_a_clock():
    # 'שעה ארוכה' = "a long hour" -- שעה here is the bare noun, not the
    # agglutinated 'בשעה' clock marker; must not spuriously bind a clock.
    nomatch("שעה ארוכה")


def test_shaa_in_duration_phrase_not_a_clock():
    # 'עבדתי שעה שלמה' = "I worked a whole hour" -- a duration, not a clock.
    nomatch("עבדתי שעה שלמה")


def test_shaa_ago_not_a_clock():
    # 'לפני שעה' = "an hour ago" -- must not be swept into a clock reading.
    nomatch("לפני שעה")
