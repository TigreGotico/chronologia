# -*- coding: utf-8 -*-
"""Per-dialect short/long scale in Portuguese deep time.

European Portuguese uses the LONG scale: 10^9 is "mil milhões", "bilião" =
10^12.  Brazilian Portuguese uses the SHORT scale: "bilhão" = 10^9.  Bare "pt"
(= pt-PT) defaults to long, "pt-BR" to short, both loading the same base pt
locale; an explicit ``scale=`` hard-overrides.

Sources: Wikipedia, "Long and short scales" (Portuguese section); ovos-number-
parser pt vocabulary (bilião: 10^9 short / 10^12 long).
"""
from datetime import datetime

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)


def _year(text, lang="pt", scale=None):
    r = extract_timespan(text, lang, ANCHOR, scale=scale)
    assert r is not None, f"{text!r} ({lang}, scale={scale}) did not parse"
    return r[0].start.year


def _about(year, magnitude):
    assert abs(year - (-magnitude)) < magnitude * 0.001 + 10_000, \
        f"{year} is not ~ -{magnitude}"


def test_mil_milhoes_is_1e9():
    _about(_year("há mil milhões de anos"), 1_000_000_000)


def test_biliao_is_1e12_under_pt_long_default():
    _about(_year("há um bilião de anos"), 1_000_000_000_000)


def test_biliao_1e12_under_region_code_pt_PT():
    _about(_year("há um bilião de anos", lang="pt-PT"), 1_000_000_000_000)


def test_bilhao_is_1e9_under_pt_BR():
    _about(_year("há um bilhão de anos", lang="pt-BR"), 1_000_000_000)


def test_biliao_is_1e9_under_explicit_short():
    _about(_year("há um bilião de anos", scale="short"), 1_000_000_000)
