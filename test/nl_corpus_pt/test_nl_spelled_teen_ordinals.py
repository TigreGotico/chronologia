# -*- coding: utf-8 -*-
"""Two-word compound "décimo <unit>" ordinals (11th-19th) fold to ORD for
Portuguese -- R87.

Portuguese "décimo" is the ordinal of 10th and the denominator of a-tenth.
Portuguese writes its 11th-19th ordinals as the TWO-word compound "décimo
<unit>" ("décimo terceiro" = thirteenth), unlike Spanish, which fuses them.
"o décimo terceiro mês de 2026" must refuse (no 13th month exists), not land
on the WRONG month (February, reading only "terceiro" as 3rd).

Source: standard Portuguese ordinal-numeral vocabulary; the numtag Portuguese
lexicon lists "décimo" for value 10 as both ordinal and denominator.

Golds are computed by independent calendar reasoning, never read back from
the parser.

"quarto" is also the clock quarter, and the last word of a compound ordinal
("décimo quarto") keeps its ordinal reading, so "o décimo quarto mês de 2026"
refuses like the other teens.
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


def test_decimo_quarto_is_refused_not_read_as_the_year():
    # pre-fix: the whole year 2026 with the remainder 'o décimo quarto mês de'
    nomatch("o décimo quarto mês de 2026")
