# -*- coding: utf-8 -*-
"""\"deste mês\" and \"deste ano\" name the anchor's own month and year, pt.

"deste" is "Contracção da preposição de com o pronome este" (Priberam s.v.
"deste"), and "este" is "Designativo de pessoa ou coisa que está presente,
ou mais próxima de quem fala que outra ou outras" (Priberam s.v. "este").
So "o dia 5 deste mês" is the 5th of the anchor's month, even when it has
passed.

Anchor Saturday 2026-10-17 12:00.  October 2026 starts on a Thursday, so
its first Monday is the 5th, its first Tuesday the 6th, its first Sunday the
4th, its last Monday the 26th and its last Friday the 30th.  Its first two
Tuesdays are the 6th and 13th, and its Fridays the 2nd, 9th, 16th, 23rd and
30th.  January 2026 starts on a Thursday, so its first Tuesday is the 6th and
its second the 13th.  The anchor's week starts on Monday 12 October.
Counted on the calendar by hand.
"""
from datetime import datetime

import pytest

from ._corpus import ad, parse

SATURDAY = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("text,ymd,rest", [
    ("o dia 5 deste mês", (2026, 10, 5), ""),
    ("dia 20 deste mês", (2026, 10, 20), ""),
    ("o primeiro dia deste mês", (2026, 10, 1), ""),
    ("o último dia deste mês", (2026, 10, 31), ""),
    ("a primeira semana deste mês", (2026, 10, 5), ""),
    ("a última semana deste mês", (2026, 10, 26), ""),
    ("a primeira terça-feira deste mês", (2026, 10, 6), ""),
    ("a última sexta-feira deste mês", (2026, 10, 30), ""),
    ("o primeiro domingo deste mês", (2026, 10, 4), ""),
    ("o último dia deste ano", (2026, 12, 31), ""),
    ("a primeira terça-feira deste ano", (2026, 1, 6), ""),
    ("a segunda terça-feira deste mês", (2026, 10, 13), ""),
    ("a segunda sexta-feira deste mês", (2026, 10, 9), ""),
    ("a quarta sexta-feira deste mês", (2026, 10, 23), ""),
    ("a segunda terça-feira deste ano", (2026, 1, 13), ""),
    ("desta semana", (2026, 10, 12), ""),
    ("gosto deste mês", (2026, 10, 1), "gosto"),
])
def test_deste(text, ymd, rest):
    r = parse(text, SATURDAY)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == ad(datetime(*ymd))
    assert r.remainder == rest
