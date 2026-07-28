# -*- coding: utf-8 -*-
"""Holidays with explicit year (cs), day-wide. Fixed feasts (Nový rok, Štědrý den, Boží hod vánoční, Tři králové) at their calendar date; movable Easter-cycle feasts (Velikonoce, Velikonoční pondělí, Velký pátek) derived from an INDEPENDENT Western computus (dateutil.easter, Gregorian). Year 2020 is left to test_nl_holiday_ref.py."""
import pytest
from datetime import timedelta
from ._corpus import AstroDate, start_end


CASES = [
    ('nový rok 2018', (2018, 1, 1, 0, 0), (2018, 1, 2, 0, 0)),
    ('nový rok 2019', (2019, 1, 1, 0, 0), (2019, 1, 2, 0, 0)),
    ('nový rok 2021', (2021, 1, 1, 0, 0), (2021, 1, 2, 0, 0)),
    ('nový rok 2022', (2022, 1, 1, 0, 0), (2022, 1, 2, 0, 0)),
    ('nový rok 2023', (2023, 1, 1, 0, 0), (2023, 1, 2, 0, 0)),
    ('štědrý den 2018', (2018, 12, 24, 0, 0), (2018, 12, 25, 0, 0)),
    ('štědrý den 2019', (2019, 12, 24, 0, 0), (2019, 12, 25, 0, 0)),
    ('štědrý den 2021', (2021, 12, 24, 0, 0), (2021, 12, 25, 0, 0)),
    ('štědrý den 2022', (2022, 12, 24, 0, 0), (2022, 12, 25, 0, 0)),
    ('štědrý den 2023', (2023, 12, 24, 0, 0), (2023, 12, 25, 0, 0)),
    ('boží hod vánoční 2018', (2018, 12, 25, 0, 0), (2018, 12, 26, 0, 0)),
    ('boží hod vánoční 2019', (2019, 12, 25, 0, 0), (2019, 12, 26, 0, 0)),
    ('boží hod vánoční 2021', (2021, 12, 25, 0, 0), (2021, 12, 26, 0, 0)),
    ('boží hod vánoční 2022', (2022, 12, 25, 0, 0), (2022, 12, 26, 0, 0)),
    ('boží hod vánoční 2023', (2023, 12, 25, 0, 0), (2023, 12, 26, 0, 0)),
    ('tři králové 2018', (2018, 1, 6, 0, 0), (2018, 1, 7, 0, 0)),
    ('tři králové 2019', (2019, 1, 6, 0, 0), (2019, 1, 7, 0, 0)),
    ('tři králové 2021', (2021, 1, 6, 0, 0), (2021, 1, 7, 0, 0)),
    ('tři králové 2022', (2022, 1, 6, 0, 0), (2022, 1, 7, 0, 0)),
    ('tři králové 2023', (2023, 1, 6, 0, 0), (2023, 1, 7, 0, 0)),
    ('velikonoce 2018', (2018, 4, 1, 0, 0), (2018, 4, 2, 0, 0)),
    ('velikonoční pondělí 2018', (2018, 4, 2, 0, 0), (2018, 4, 3, 0, 0)),
    ('velký pátek 2018', (2018, 3, 30, 0, 0), (2018, 3, 31, 0, 0)),
    ('velikonoce 2019', (2019, 4, 21, 0, 0), (2019, 4, 22, 0, 0)),
    ('velikonoční pondělí 2019', (2019, 4, 22, 0, 0), (2019, 4, 23, 0, 0)),
    ('velký pátek 2019', (2019, 4, 19, 0, 0), (2019, 4, 20, 0, 0)),
    ('velikonoce 2021', (2021, 4, 4, 0, 0), (2021, 4, 5, 0, 0)),
    ('velikonoční pondělí 2021', (2021, 4, 5, 0, 0), (2021, 4, 6, 0, 0)),
    ('velký pátek 2021', (2021, 4, 2, 0, 0), (2021, 4, 3, 0, 0)),
    ('velikonoce 2022', (2022, 4, 17, 0, 0), (2022, 4, 18, 0, 0)),
    ('velikonoční pondělí 2022', (2022, 4, 18, 0, 0), (2022, 4, 19, 0, 0)),
    ('velký pátek 2022', (2022, 4, 15, 0, 0), (2022, 4, 16, 0, 0)),
    ('velikonoce 2023', (2023, 4, 9, 0, 0), (2023, 4, 10, 0, 0)),
    ('velikonoční pondělí 2023', (2023, 4, 10, 0, 0), (2023, 4, 11, 0, 0)),
    ('velký pátek 2023', (2023, 4, 7, 0, 0), (2023, 4, 8, 0, 0)),
]


@pytest.mark.parametrize("text,s,e", CASES)
def test_span(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))
