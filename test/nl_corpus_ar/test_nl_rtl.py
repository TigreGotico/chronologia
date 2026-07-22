# -*- coding: utf-8 -*-
"""RTL / mixed-direction tokenisation.

Arabic is right-to-left but the tokenizer is script-agnostic: a digit run
embedded in RTL text is one token, and Arabic-Indic digits (٠-٩) carry the
same value as Western digits.  These assert that mixed-direction strings
tokenize and resolve identically to their Western-digit twins."""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, ad, start, start_end, span


@pytest.mark.parametrize("arabic_indic,western", [
    ("١٥ يناير ٢٠٢٠", "15 يناير 2020"),
    ("٢٠ يوليو ١٩٦٩", "20 يوليو 1969"),
    ("قبل ٣ أيام", "قبل 3 أيام"),
    ("بعد ٥ سنوات", "بعد 5 سنوات"),
    ("٤٤ ق.م", "44 ق.م"),
])
def test_arabic_indic_equals_western(arabic_indic, western):
    assert start_end(arabic_indic) == start_end(western)


@pytest.mark.parametrize("text,h,mi", [
    ("الساعة ١٥:٣٠", 15, 30),   # Arabic-Indic digits inside a clock literal
])
def test_arabic_indic_clock(text, h, mi):
    dt = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    assert start(text) == ad(dt)


def test_digit_embedded_in_sentence():
    # a date embedded mid-sentence; the surrounding RTL words are residue
    s, e = start_end("سافرت في 15 يناير 2020 إلى القاهرة")
    assert s == AstroDate(2020, 1, 15) and e == AstroDate(2020, 1, 16)


def test_offset_embedded_in_sentence():
    s = start("سوف أراك بعد 3 أيام إن شاء الله")
    from datetime import timedelta as _td
    assert s == ad(ANCHOR + _td(days=3))
