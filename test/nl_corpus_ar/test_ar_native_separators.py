# -*- coding: utf-8 -*-
"""Arabic native decimal/thousands separators (U+066B/U+066C) must be
recognised by the tokenizer's number rule.

``ar`` is configured ``decimal_comma: True`` (Latin '.' groups thousands,
Latin ',' is the decimal), but real Arabic text uses the NATIVE Arabic-script
separators -- ARABIC DECIMAL SEPARATOR (U+066B, '٫') and ARABIC THOUSANDS
SEPARATOR (U+066C, '٬') -- which the regex, built from the two Latin chars
only, previously did not match at all: the run split on the unrecognised
separator and the leading digit group was silently dropped. Expected values
are independent arithmetic, never read back from the parser.
"""
from datetime import timedelta

from chronologia import extract_duration

from ._corpus import parse


def test_native_decimal_separator_fraction():
    # ١٫٥ = "1.5" (Arabic-Indic 1, U+066B, Arabic-Indic 5) hours -> 1h30m,
    # NOT the pre-fix wrong reading of a bare "5" hours.
    r = extract_duration("١٫٥ ساعة", "ar")
    assert r is not None
    assert r.duration == timedelta(hours=1, minutes=30)


def test_native_thousands_separator():
    # ١٬٥٠٠ = "1,500" (native thousands separator) days -> 1500 days, NOT the
    # pre-fix wrong reading of a bare "500" days from the dropped leading digit.
    r = extract_duration("١٬٥٠٠ يوم", "ar")
    assert r is not None
    assert r.duration == timedelta(days=1500)


def test_bare_native_digit_year_regression():
    # regression guard: a bare native-digit year (no separators involved)
    # must keep resolving after the translate step is introduced.
    r = parse("٢٠٢٠")
    assert r is not None
    assert r[0].start.year == 2020


def test_native_decimal_separator_remainder_offset_invariant():
    # the native separator must not leak into (or corrupt) the remainder --
    # the char-offset invariant that lets the remainder slice the ORIGINAL
    # text verbatim must hold even though ``low`` was translated in-place.
    r = extract_duration("١٫٥ ساعة بعد ذلك", "ar")
    assert r is not None
    assert "بعد ذلك" in r.remainder
