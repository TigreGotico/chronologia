# -*- coding: utf-8 -*-
"""Persian native decimal/thousands separators (U+066B/U+066C) must be
recognised by the tokenizer's number rule.

``fa`` is configured ``decimal_comma: True`` (Latin '.' groups thousands,
Latin ',' is the decimal), but real Persian text uses the native
Arabic-script separators -- U+066B (decimal) / U+066C (thousands) -- with
Extended Arabic-Indic digits (۰-۹, U+06F0-U+06F9). Before the fix these were
not matched at all, so the run split on the separator and the leading digit
group was silently dropped. Expected values are independent arithmetic,
never read back from the parser.
"""
from datetime import timedelta

from chronologia import extract_duration

from ._corpus import parse


def test_native_decimal_separator_fraction():
    # ۱٫۵ = "1.5" (Extended Arabic-Indic digits, U+066B decimal separator)
    # hours -> 1h30m, NOT the pre-fix wrong reading of a bare "5" hours.
    r = extract_duration("۱٫۵ ساعت", "fa")
    assert r is not None
    assert r.duration == timedelta(hours=1, minutes=30)


def test_bare_native_digit_year_regression():
    # regression guard: a bare native-digit year (no separators involved)
    # must keep resolving after the translate step is introduced.
    r = parse("۲۰۲۰")
    assert r is not None
    assert r[0].start.year == 2020


def test_native_decimal_separator_remainder_offset_invariant():
    # the native separator must not leak into (or corrupt) the remainder --
    # the char-offset invariant that lets the remainder slice the ORIGINAL
    # text verbatim must hold even though ``low`` was translated in-place.
    r = extract_duration("۱٫۵ ساعت بعد از آن", "fa")
    assert r is not None
    assert "بعد از آن" in r.remainder
