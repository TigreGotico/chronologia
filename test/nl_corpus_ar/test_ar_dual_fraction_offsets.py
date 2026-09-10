"""Arabic offsets on a dual noun, on a fused fraction, and "within"; the
vocalised clock hour; noon as an adverb.

Anchor: Tuesday 2017-06-27 13:04.  Every value is anchor arithmetic; an
offset in hours keeps the anchor's minute, an offset in days keeps its time.

Dual: a count of exactly two is inflected on the noun (ساعتان / ساعتين), not
written as a separate numeral -- W. Wright, A Grammar of the Arabic
Language, 3rd ed., vol. I, para. 299 (nominative -āni, oblique -ayni).

Fused fraction after the unit, ar.wikipedia running text: "رحلة بطول ساعة
ونصف" (كويرنافاكا), "على بعد ساعتين ونصف" (قرزة), "مدتها ساعة وربع"
(حنين (فلم 2005)), "تحدث الفوائد في غضون ثلاثة أيام" (ماكروغول).

Vowel marks are optional in ordinary writing (Unicode Arabic block
U+064B-U+0652), so "الثَّالِثة" is the same word as "الثالثة".  "ظُهْرًا" is
the accusative of ظهر used adverbially, "at noon" (Wiktionary, ظهر).
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse


def _offset(text, delta, grain):
    res = parse(text)
    assert res is not None, f"{text!r} did not parse"
    assert res.remainder == "", f"{text!r} stranded {res.remainder!r}"
    assert res[0].start == ad(ANCHOR + delta)
    assert res[0].end == ad(ANCHOR + delta + grain)


H, D = timedelta(hours=1), timedelta(days=1)


@pytest.mark.parametrize("text,delta,grain", [
    ("بعد ساعتين", 2 * H, H),
    ("قبل ساعتين", -2 * H, H),
    ("خلال ساعتين", 2 * H, H),
    ("بعد يومين", 2 * D, D),
    ("بعد أسبوعين", 14 * D, 7 * D),
    ("بعد دقيقتين", timedelta(minutes=2), timedelta(minutes=1)),
])
def test_dual_noun_counts_two(text, delta, grain):
    _offset(text, delta, grain)


@pytest.mark.parametrize("text,delta", [
    ("بعد ساعة ونصف", timedelta(minutes=90)),
    ("بعد ساعتين ونصف", timedelta(minutes=150)),
    ("بعد ساعة وربع", timedelta(minutes=75)),
    ("في غضون ساعة ونصف", timedelta(minutes=90)),
])
def test_fused_fraction_adds_to_the_count(text, delta):
    _offset(text, delta, H)


def test_within_three_days():
    _offset("في غضون ثلاثة أيام", 3 * D, D)


def test_half_and_quarter_do_not_collapse():
    half, _ = parse("بعد ساعة ونصف")
    quarter, _ = parse("بعد ساعة وربع")
    assert half.start - quarter.start == timedelta(minutes=15)


def test_vocalised_clock_hour():
    plain = parse("الساعة الثالثة صباحاً")
    marked = parse("الساعة الثَّالِثة صباحاً")
    assert plain is not None and marked is not None
    assert plain[0].start == ad(ANCHOR.replace(hour=3, minute=0) + D)
    assert marked[0].start == plain[0].start
    assert marked.remainder == ""


@pytest.mark.parametrize("text", ["ظهراً", "ظهرا"])
def test_noon_adverb(text):
    res = parse(text)
    assert res is not None and res.remainder == ""
    assert res[0].start == ad(ANCHOR.replace(hour=12, minute=0) + D)
