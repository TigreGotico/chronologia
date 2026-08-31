# -*- coding: utf-8 -*-
"""Ranges.  Dash-framed ranges parse language-agnostically; the word-framed
Hebrew form ("מ-ינואר עד מרץ") parses too -- the "from" lead (the proclitic מ־)
and the "to" connector (עד) ship per-locale (marker_from/marker_to), so range
framing is not English-only.  The proclitic מ set off by a maqaf/hyphen
tokenizes as its own token (the hyphen is a separator), and עד is a free word;
the earlier date is always the span start, never inverted by right-to-left
reading order."""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, AstroDate, span, start_end, nomatch


@pytest.mark.parametrize("text,s,e", [
    ("ינואר - מרץ", (2017, 1, 1), (2017, 4, 1)),
    ("יוני - אוגוסט", (2017, 6, 1), (2017, 9, 1)),
    ("15 בינואר - 20 בינואר", (2018, 1, 15), (2018, 1, 21)),
])
def test_dash_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.parametrize("text,s,e", [
    ("מ-ינואר עד מרץ", (2017, 1, 1), (2017, 4, 1)),
    ("מ-יוני עד אוגוסט", (2017, 6, 1), (2017, 9, 1)),
    ("מ-15 בינואר עד 20 בינואר", (2018, 1, 15), (2018, 1, 21)),
])
def test_word_framed_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


# -- adversarial: a bare range connector with no valid endpoints must not crash
# and must not fabricate a span.
@pytest.mark.parametrize("text", ["מ", "עד", "בין", "מ עד"])
def test_bare_connector_is_nomatch(text):
    nomatch(text)


# -- fused proclitic "and": Hebrew writes the "ו" (and) conjunction GLUED onto
# the word it precedes, with no space -- "בין ינואר ומרץ" ("between January
# andMarch").  The spaced and fused forms are the same range and must pin the
# same span; a bare word that legitimately starts with "ו" ("ורוד" pink) must
# NOT be mistaken for a glued endpoint.
@pytest.mark.parametrize("text,s,e", [
    ("בין ינואר ו מרץ", (2017, 1, 1), (2017, 4, 1)),
    ("בין ינואר ומרץ", (2017, 1, 1), (2017, 4, 1)),
])
def test_fused_vav_range_endpoint(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


def test_varod_is_not_split_as_fused_vav():
    # "ורוד" (pink) starts with "ו" but is not "ו" + a recognised temporal
    # word -- the guard must not mistake it for a glued range endpoint, and
    # since "ורוד" is not otherwise a date/time word it must not match at all.
    nomatch("ורוד בהיר")


# -- fused vav closes classes beyond Gregorian months: the single-word
# weekday ("שבת" Saturday, the only weekday name that is not multiword --
# see the module docstring in numfold_semitic.py) and dayparts also ship as
# single-word he vocabulary and fuse the same way.  Each pins the exact span
# its already-working spaced-vav sibling resolves to.

# Weekday range: a bare weekday resolves to its next strictly-future
# occurrence, searched forward from the first endpoint once it is resolved
# (test_nl_bare_weekday.py's rule).  Anchor is Tuesday 2017-06-27
# (weekday() == 1); Monday (idx 0) is 6 days ahead -> 2017-07-03, and the
# following Saturday (idx 5), counted forward from that Monday, is 5 days
# ahead -> 2017-07-08, end exclusive 2017-07-09.
@pytest.mark.parametrize("text,s,e", [
    ("בין יום שני ו שבת", (2017, 7, 3), (2017, 7, 9)),
    ("בין יום שני ושבת", (2017, 7, 3), (2017, 7, 9)),
])
def test_fused_vav_weekday_range_endpoint(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


# Daypart range: CLDR 47 he day-period bands (chronologia/dayparts.py)
# morning [06:00, 12:00) and evening [18:00, 22:00), both anchored on the
# anchor's own civil day (2017-06-27, a Tuesday) since no deictic day is
# named.
@pytest.mark.parametrize("text", ["בין בבוקר ו בערב", "בין בבוקר ובערב"])
def test_fused_vav_daypart_range_endpoint(text):
    sp = span(text)
    assert sp.start_datetime == ANCHOR.replace(hour=6, minute=0, second=0,
                                               microsecond=0)
    assert sp.end_datetime == ANCHOR.replace(hour=22, minute=0, second=0,
                                             microsecond=0)


# Multiword weekday names ("יום שלישי" Tuesday) are NOT closed by this guard:
# splitting only the leading "ו" off a multiword surface leaves a remainder
# the multiword-merge pass was never asked to re-glue, so the fused form
# still truncates.  Left open deliberately (tracked separately, same
# limitation as the Arabic sibling fix); pinned here so a future fix flips
# this from xfail to a real assertion.
@pytest.mark.xfail(reason="multiword weekday surfaces not covered by the fused-vav guard", strict=True)
def test_fused_vav_multiword_weekday_not_yet_closed():
    ss, ee = start_end("בין יום שני ויום שלישי")
    assert ss == AstroDate(2017, 7, 3) and ee == AstroDate(2017, 7, 5)


def test_fused_vav_yields_two_mentions_not_one():
    # extract_timespans on a bare "MONTH וMONTH" utterance (no range lead)
    # now correctly reports two separate month mentions instead of folding
    # the second, fused month invisibly into the first's remainder.
    from chronologia import extract_timespans
    mentions = extract_timespans("ינואר ומרץ", "he", ANCHOR)
    assert len(mentions) == 2
    assert mentions[0].span.start == AstroDate(2017, 1, 1)
    assert mentions[0].span.end == AstroDate(2017, 2, 1)
    assert mentions[1].span.start == AstroDate(2017, 3, 1)
    assert mentions[1].span.end == AstroDate(2017, 4, 1)


def test_fused_vav_bare_word_still_resolves_clean():
    # Not a regression: "ומרץ" alone (no range lead) already resolved as bare
    # March via the pre-existing curated ``_HE_VAV_STEMS``/``_he_vav_strip``
    # hook, with the vav fully consumed (no leftover remainder). The new
    # range-endpoint pre_hook splits the same fused word earlier, so a
    # companion re-merge (``_he_vav_remerge``) undoes that split for any pair
    # not consumed as a range connector, keeping this bare-mention reading
    # exactly as clean as before the range fix existed.
    r = extract_timespan("ומרץ", "he", ANCHOR)
    assert r is not None
    assert r[0].start == AstroDate(2017, 3, 1) and r[0].end == AstroDate(2017, 4, 1)
    assert r[1] == ""


# -- Av ("אב") is deliberately excluded from the vav-glued temporal-word
# guard, both for the range-endpoint split and its bare-mention remerge
# companion: it is not only the Hebrew month Av but also the ordinary,
# extremely common noun "father", and admitting it let a fused bare mention
# resolve as a confident month span for text that was never talking about a
# date ("אם ואב" / "אבא ואב", "mother and father" / "dad and father").
@pytest.mark.parametrize("text", ["אם ואב", "אבא ואב"])
def test_fused_vav_father_not_month(text):
    nomatch(text)


def test_fused_vav_av_range_endpoint_still_open():
    # The Av exclusion is a stated trade-off, not a silent gap: a fused range
    # ending in Av ("בין ניסן ואב") still truncates to the first endpoint
    # alone -- the original defect, left open for this one month.  The
    # spaced sibling is unaffected (test_fused_vav_av_range_endpoint_spaced).
    ss, ee = start_end("בין ניסן ואב")
    assert ss == AstroDate(2017, 3, 28) and ee == AstroDate(2017, 4, 27)


def test_fused_vav_av_range_endpoint_spaced():
    ss, ee = start_end("בין ניסן ו אב")
    assert ss == AstroDate(2017, 3, 28) and ee == AstroDate(2017, 8, 23)


# -- the bare-mention remerge (``_he_vav_remerge``) does not merely restore
# the pre-existing Gregorian-month absorption -- it broadens it to three
# classes that previously had no match at all when fused: the single-word
# weekday ("שבת"), dayparts, and Hebrew-calendar months.  Each is pinned
# against its own already-attested bare (unprefixed) sibling, so the gold
# is the parser's own independently-tested bare-month/weekday/daypart
# resolution rule, not a value read back from the fused case itself.
@pytest.mark.parametrize("fused,bare", [
    ("ושבת", "שבת"),
    ("ובבוקר", "בבוקר"),
    ("וניסן", "ניסן"),
    ("וסיון", "סיון"),
])
def test_fused_vav_bare_mention_widening(fused, bare):
    got = extract_timespan(fused, "he", ANCHOR)
    want = extract_timespan(bare, "he", ANCHOR)
    assert got is not None and want is not None
    assert got[0].start == want[0].start
    assert got[0].end == want[0].end
    assert got[1] == ""
