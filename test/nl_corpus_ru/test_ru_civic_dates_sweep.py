# -*- coding: utf-8 -*-
"""Fixed civic-calendar dates sweep (ru) -- "23 февраля 2020" etc.

The Russian public-holiday *names* (День Победы, День России, ...) are not
modelled as holiday tokens by the engine, but their fixed calendar dates parse
cleanly as ordinary day-month-year dates.  This sweep pins each fixed civic
date across many years; gold is the literal calendar date (a one-day span),
computed independently.  Anchor 2017-06-27."""
import pytest

from ._corpus import AstroDate, start_end

# (day, genitive-month, month-number) for each fixed Russian civic holiday
_FIXED = [
    (1, "января", 1),    # Новый год
    (7, "января", 1),    # Рождество Христово
    (23, "февраля", 2),  # День защитника Отечества
    (8, "марта", 3),     # Международный женский день
    (1, "мая", 5),       # Праздник Весны и Труда
    (9, "мая", 5),       # День Победы
    (12, "июня", 6),     # День России
    (4, "ноября", 11),   # День народного единства
]

_YEARS = (2018, 2019, 2020, 2021, 2022, 2023)


def _cases():
    out = []
    for day, mon_gen, mon in _FIXED:
        for year in _YEARS:
            out.append((f"{day} {mon_gen} {year}", year, mon, day))
    return out


@pytest.mark.parametrize("text,y,m,d", _cases())
def test_fixed_civic_date(text, y, m, d):
    st, en = start_end(text)
    assert st == AstroDate(y, m, d)
    assert en == AstroDate(y, m, d + 1)
