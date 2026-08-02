# -*- coding: utf-8 -*-
"""Durations in id: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "id"

_CASES = [
    ('5 menit', timedelta(minutes=5)),
    ('45 menit', timedelta(minutes=45)),
    ('2 jam', timedelta(hours=2)),
    ('1 jam', timedelta(hours=1)),
    ('2 hari', timedelta(days=2)),
    ('3 minggu', timedelta(weeks=3)),
    ('90 menit', timedelta(minutes=90)),
    ('setengah jam', timedelta(minutes=30)),
    ('seperempat jam', timedelta(minutes=15)),
    ('2 hari 4 jam', timedelta(days=2, hours=4)),
    ('1 jam 30 menit', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 juni', 'tidak ada waktu di sini'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None


@pytest.mark.parametrize("text,expected", [
    ('dua puluh lima hari', timedelta(days=25)),   # tens: dua puluh lima
    ('dua belas hari', timedelta(days=12)),         # teens: dua belas
    ('dua ratus hari', timedelta(days=200)),        # hundreds: dua ratus
    ('tiga ratus lima puluh hari', timedelta(days=350)),
    ('seratus dua puluh lima hari', timedelta(days=125)),
])
def test_duration_multiplier_compounds(text, expected):
    # Indonesian builds numbers with bare multiplier words (puluh=ten,
    # ratus=hundred, belas=-teen) that have no standalone value, so the per-token
    # value probe severed the run at them and hundreds/tens returned None (or a
    # wrong trailing component). They are now admitted to the run as join words.
    got = extract_duration(text, LANG)
    assert got is not None and got[0] == expected
