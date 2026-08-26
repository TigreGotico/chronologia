# -*- coding: utf-8 -*-
"""Thai is written without spaces, so a date phrase arrives as one run.

The segmenter cuts a run into words only when the WHOLE run is covered by
surfaces this locale knows, longest first.  These tests hold both halves of
that rule: the covered runs cut correctly, and an uncovered one is handed on
untouched so the extractor answers nothing rather than a reading pulled out of
the middle of ordinary prose.
"""
import pytest

from chronologia.extract.numfold_thai import dictionary, segment

from ._corpus import day, nomatch, start_end


@pytest.mark.parametrize("run,words", [
    ("วันจันทร์", ["วันจันทร์"]),
    ("วันจันทร์หน้า", ["วันจันทร์", "หน้า"]),
    ("วันนี้", ["วันนี้"]),
    ("สามวันที่ผ่านมา", ["สาม", "วัน", "ที่ผ่านมา"]),
    ("ในอีกสองสัปดาห์", ["ในอีก", "สอง", "สัปดาห์"]),
    ("สามทุ่มครึ่ง", ["สาม", "ทุ่ม", "ครึ่ง"]),
    ("บ่ายโมงสิบห้านาที", ["บ่าย", "โมง", "สิบ", "ห้า", "นาที"]),
    ("เที่ยงคืน", ["เที่ยงคืน"]),
    ("ยี่สิบเอ็ดวัน", ["ยี่", "สิบ", "เอ็ด", "วัน"]),
])
def test_a_covered_run_is_cut_into_its_words(run, words):
    assert segment(run) == words


def test_the_longest_surface_wins():
    """วันจันทร์ is Monday; วัน + จันทร์ would be "day" plus "moon", and
    วันนี้ is today rather than "day" plus the this-marker."""
    assert segment("วันจันทร์") == ["วันจันทร์"]
    assert segment("วันนี้") == ["วันนี้"]
    assert segment("เที่ยงคืน") == ["เที่ยงคืน"]


@pytest.mark.parametrize("run", [
    "ฉันจะไปโรงเรียน",     # "I will go to school" -- no temporal word at all
    "สามารถ",              # "can, be able to" -- opens with the syllable สาม (3)
    "หกสิบสี่เหลี่ยม",       # numeral syllables glued to a non-temporal word
])
def test_an_uncovered_run_is_left_whole(run):
    assert segment(run) is None


@pytest.mark.parametrize("text", ["ฉันจะไปโรงเรียน", "สามารถ"])
def test_ordinary_prose_with_a_numeral_syllable_names_no_time(text):
    nomatch(text)


def test_the_dictionary_is_read_from_the_shipped_vocabulary():
    """The segmenter's word list is the locale's own ``.voc`` surfaces, so a
    surface can never be matchable but unsegmentable."""
    words = dictionary()
    for surface in ("วันจันทร์", "มกราคม", "พรุ่งนี้", "สัปดาห์", "ที่ผ่านมา",
                    "ในอีก", "กลางคืน"):
        assert surface in words


def test_a_run_glued_to_prose_is_refused_rather_than_mined():
    """Thai spaces phrases, not words; a date phrase run into the surrounding
    prose with no space is withdrawn whole instead of having a reading cut out
    of its middle."""
    nomatch("ฉันจะไปพรุ่งนี้")


def test_the_same_phrase_reads_when_the_phrase_space_is_present():
    assert start_end("ฉันจะไป พรุ่งนี้") == day(2027, 5, 13)
