# -*- coding: utf-8 -*-
"""The Thai numeral system: positional concatenation with three irregularities.

A units digit of 1 after a higher place is ``เอ็ด``; a tens digit of 1 drops
its digit word, leaving bare ``สิบ``; a tens digit of 2 is ``ยี่``.  Those are
the only licensed spellings of their values, so the arithmetically obvious
``หนึ่งสิบ`` and ``สองสิบ`` are read as no numeral at all rather than invented
into 10 and 20.
"""
import pytest

from chronologia.extract.numfold_thai import read_run, surface

CASES = [
    ("ศูนย์", 0), ("หนึ่ง", 1), ("สอง", 2), ("สาม", 3), ("สี่", 4),
    ("ห้า", 5), ("หก", 6), ("เจ็ด", 7), ("แปด", 8), ("เก้า", 9),
    ("สิบ", 10), ("สิบเอ็ด", 11), ("สิบสอง", 12), ("สิบห้า", 15),
    ("ยี่สิบ", 20), ("ยี่สิบเอ็ด", 21), ("ยี่สิบห้า", 25),
    ("สามสิบ", 30), ("สี่สิบห้า", 45), ("เก้าสิบเก้า", 99),
    ("หนึ่งร้อย", 100), ("หนึ่งร้อยเอ็ด", 101),
    ("ห้าร้อยสี่สิบสาม", 543),
    ("สองพันห้าร้อยหกสิบแปด", 2568),
    ("หนึ่งหมื่น", 10000),
    ("หนึ่งแสนสองหมื่นสามพันสี่ร้อยห้าสิบหก", 123456),
    ("สองล้าน", 2000000),
]


@pytest.mark.parametrize("text,value", CASES)
def test_a_spelled_numeral_reads_as_its_value(text, value):
    assert read_run(text) == value


@pytest.mark.parametrize("text,value", CASES)
def test_the_generator_and_the_reader_agree(text, value):
    """The surface a value generates must be the surface that reads back to
    it, so the two can never drift apart on the irregular positions."""
    assert surface(value) == text
    assert read_run(surface(value)) == value


@pytest.mark.parametrize("n", list(range(0, 200)) + [543, 1997, 2025, 2568])
def test_every_value_round_trips(n):
    assert read_run(surface(n)) == n


@pytest.mark.parametrize("text", ["หนึ่งสิบ", "สองสิบ"])
def test_an_unattested_tens_spelling_is_not_a_numeral(text):
    """Thai spells 10 as bare สิบ and 20 as ยี่สิบ.  Reading these as 10 and
    20 anyway would invent an orthography no source attests."""
    assert read_run(text) is None


@pytest.mark.parametrize("text,value", [("ซาวเอ็ด", 21), ("ซาว", 20)])
def test_the_dialectal_twenty_is_read_but_never_generated(text, value):
    assert read_run(text) == value
    assert "ซาว" not in surface(value)


def test_thai_digits_are_read_by_the_shared_tokenizer():
    """๐-๙ are Unicode decimal digits, so no locale handling is needed."""
    from datetime import datetime

    from chronologia import extract_timespan
    anchor = datetime(2027, 5, 12, 13, 4)
    thai = extract_timespan("๒๐๒๖", "th", anchor)
    arabic = extract_timespan("2026", "th", anchor)
    assert thai is not None and arabic is not None
    assert (thai[0].start, thai[0].end) == (arabic[0].start, arabic[0].end)


@pytest.mark.parametrize("text,value", [("หนึ่งร้อยหนึ่ง", 101),
                                        ("ยี่สิบหนึ่ง", 21)])
def test_the_military_final_one_is_read_but_never_generated(text, value):
    """หนึ่ง in the units place after a higher place is a marked variant of
    เอ็ด; it reads, and the generator keeps to เอ็ด."""
    assert read_run(text) == value
    assert surface(value).endswith("เอ็ด")
