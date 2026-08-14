# -*- coding: utf-8 -*-
"""R170 (de): two independent number-folding gaps.

1. "anderthalb" (== "eineinhalb", 1.5) is the more common everyday synonym
   for "eineinhalb" but ovos-number-parser does not read it back
   (``extract_number_de('anderthalb')`` is ``None``), so it silently refused
   to fold and the whole duration phrase stranded.

2. The recent ASCII-umlaut fallback work (#714, "naechster"/"naechstes")
   covered the German function words but not the spelled number words:
   ovos-number-parser only reads the umlaut spelling ("fünf" -> 5), not its
   ASCII transliteration ("fuenf" -> None), so "in fuenf tagen" refused to
   parse while "in fünf tagen" worked.
"""
from datetime import datetime, timedelta

from chronologia import extract_timespan
from chronologia.extract import extract_duration

LANG = "de"

ANCHOR = datetime(2026, 8, 14, 10, 0)


def test_anderthalb_stunden_matches_eineinhalb_twin():
    got = extract_duration("anderthalb Stunden", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert got.remainder.strip() == ""


def test_anderthalb_matches_eineinhalb_exactly():
    assert extract_duration("anderthalb Stunden", LANG) \
        == extract_duration("eineinhalb Stunden", LANG)


def test_control_eineinhalb_stunden_unaffected():
    got = extract_duration("eineinhalb Stunden", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)


def test_control_1_5_stunden_unaffected():
    got = extract_duration("1,5 Stunden", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)


def test_control_eine_halbe_stunde_unaffected():
    got = extract_duration("eine halbe Stunde", LANG)
    assert got is not None
    assert got.duration == timedelta(minutes=30)


def test_in_fuenf_tagen_offset_matches_umlaut_twin():
    ascii_result = extract_timespan("in fuenf tagen", LANG, ANCHOR)
    umlaut_result = extract_timespan("in fünf tagen", LANG, ANCHOR)
    assert ascii_result is not None
    assert ascii_result[0] == umlaut_result[0]


def test_in_fuenf_tagen_offset_span():
    # independently computed: 2026-08-14 + 5 days == 2026-08-19, same
    # time-of-day as the anchor.
    got = extract_timespan("in fuenf tagen", LANG, ANCHOR)
    assert got is not None
    span, remainder = got
    assert span.start == datetime(2026, 8, 19, 10, 0)
    assert span.end == datetime(2026, 8, 20, 10, 0)


def test_in_zwoelf_tagen_offset_matches_umlaut_twin():
    ascii_result = extract_timespan("in zwoelf tagen", LANG, ANCHOR)
    umlaut_result = extract_timespan("in zwölf tagen", LANG, ANCHOR)
    assert ascii_result is not None
    assert ascii_result[0] == umlaut_result[0]


def test_in_fuenfzehn_tagen_offset_matches_umlaut_twin():
    ascii_result = extract_timespan("in fuenfzehn tagen", LANG, ANCHOR)
    umlaut_result = extract_timespan("in fünfzehn tagen", LANG, ANCHOR)
    assert ascii_result is not None
    assert ascii_result[0] == umlaut_result[0]


def test_in_fuenfzig_tagen_offset_matches_umlaut_twin():
    ascii_result = extract_timespan("in fuenfzig tagen", LANG, ANCHOR)
    umlaut_result = extract_timespan("in fünfzig tagen", LANG, ANCHOR)
    assert ascii_result is not None
    assert ascii_result[0] == umlaut_result[0]


def test_control_umlaut_fuenf_tagen_still_works():
    got = extract_timespan("in fünf tagen", LANG, ANCHOR)
    assert got is not None
    span, remainder = got
    assert span.start == datetime(2026, 8, 19, 10, 0)
