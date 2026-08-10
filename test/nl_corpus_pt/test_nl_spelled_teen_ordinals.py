# -*- coding: utf-8 -*-
"""Two-word compound "décimo <unit>" ordinals (11th-19th) fold to ORD for
Portuguese -- R87.

Portuguese "décimo" is at once the ORDINAL_TENS surface for 10th and the
FRACTION denominator for a-tenth (``NumberVocabulary.FRACTION[10] ==
"décimo"``), a homograph the shared Romance number-fold already resolved for
1st-9th UNIT ordinals ("quarto"/"cuarto" = fourth vs. a-quarter) but not for
the tens word itself, so "décimo" was silently subtracted from the fold's
word set as a fraction word.  Portuguese writes its 11th-19th ordinals as
the TWO-word compound "décimo <unit>" ("décimo terceiro" = thirteenth) --
unlike Spanish, it does not fuse them into one word -- so dropping "décimo"
broke the compound at its first word: "o décimo terceiro mês de 2026"
previously landed on the WRONG month (February, reading only the stranded
"terceiro" -- misread as 3rd rather than composing to 13th) rather than
refusing outright, a silent-WRONG-value defect, not merely a non-match.

Source: standard Portuguese ordinal-numeral vocabulary (``ovos_number_parser``
``numbers_pt.NumberVocabulary.ORDINAL_TENS``/``FRACTION``, both listing
"décimo" for value 10).  Portuguese ordinals 11-19 are conventionally
written as two words, never fused ("décimo terceiro", not "decimoterceiro").

Golds are computed by independent calendar reasoning, never read back from
the parser.

KNOWN REMAINING GAP (out of scope here, not fixed): "décimo quarto"/"décimo
quinto"/"décimo sexto" etc. -- where the UNIT half is ALSO a fraction
homograph ("quarto"/"quinto"/"sexto"/"sétimo"/"oitavo"/"nono" are all in
``FRACTION`` too) -- still fail, because the existing unit-homograph
licensing only fires after a definite article ("o"/"a"), not after a
preceding NUMBER token (the now-licensed "décimo").  "décimo primeiro" and
"décimo segundo" are unaffected (neither "primeiro" nor "segundo" collides
with a pt fraction word) and are the two compounds this file locks down;
extending the positional licence to "after a number" is a separate,
larger change to the shared homograph machinery, not this fix's scope.
"""
import pytest

from ._corpus import start, nomatch, parse


@pytest.mark.parametrize("text,mo", [
    ("o décimo primeiro mês de 2026", 11),
    ("o décimo segundo mês de 2026", 12),
])
def test_compound_ordinal_valid_month(text, mo):
    s = start(text)
    assert (s.year, s.month) == (2026, mo)


def test_compound_ordinal_impossible_month_refuses():
    # the exact silent-WRONG-value bug this fix closes: pre-fix this
    # returned February 2026 (reading only the stranded "terceiro" = 3rd),
    # not a refusal -- there is no 13th month.
    nomatch("o décimo terceiro mês de 2026")


def test_no_wrong_value_regression():
    r = parse("o décimo terceiro mês de 2026")
    assert r is None, (
        f"'o décimo terceiro mês de 2026' must refuse (None); the pre-fix "
        f"defect silently truncated the compound and returned month=2 "
        f"(February), got {r!r}")


def test_decimo_segundo_is_not_misread_as_segundo_alone():
    """The specific failure shape: before the fix, 'décimo' vanished from
    the fold and 'segundo' alone (2nd) won, giving February instead of the
    correct December (12th month)."""
    s = start("o décimo segundo mês de 2026")
    assert (s.year, s.month) == (2026, 12)
