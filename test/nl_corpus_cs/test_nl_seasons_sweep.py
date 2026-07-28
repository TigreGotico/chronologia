# -*- coding: utf-8 -*-
"""Meteorological northern-hemisphere seasons + year (cs): jaro=MAM, léto=JJA, podzim=SON, zima=DJF (December of the named year through the following March). Independent month-block arithmetic, six years."""
import pytest
from datetime import timedelta
from ._corpus import AstroDate, start_end


CASES = [
    ('jaro 2021', (2021, 3, 1), (2021, 6, 1)),
    ('léto 2021', (2021, 6, 1), (2021, 9, 1)),
    ('podzim 2021', (2021, 9, 1), (2021, 12, 1)),
    ('zima 2021', (2021, 12, 1), (2022, 3, 1)),
    ('jaro 2022', (2022, 3, 1), (2022, 6, 1)),
    ('léto 2022', (2022, 6, 1), (2022, 9, 1)),
    ('podzim 2022', (2022, 9, 1), (2022, 12, 1)),
    ('zima 2022', (2022, 12, 1), (2023, 3, 1)),
    ('jaro 2023', (2023, 3, 1), (2023, 6, 1)),
    ('léto 2023', (2023, 6, 1), (2023, 9, 1)),
    ('podzim 2023', (2023, 9, 1), (2023, 12, 1)),
    ('zima 2023', (2023, 12, 1), (2024, 3, 1)),
    ('jaro 2024', (2024, 3, 1), (2024, 6, 1)),
    ('léto 2024', (2024, 6, 1), (2024, 9, 1)),
    ('podzim 2024', (2024, 9, 1), (2024, 12, 1)),
    ('zima 2024', (2024, 12, 1), (2025, 3, 1)),
    ('jaro 2025', (2025, 3, 1), (2025, 6, 1)),
    ('léto 2025', (2025, 6, 1), (2025, 9, 1)),
    ('podzim 2025', (2025, 9, 1), (2025, 12, 1)),
    ('zima 2025', (2025, 12, 1), (2026, 3, 1)),
    ('jaro 2026', (2026, 3, 1), (2026, 6, 1)),
    ('léto 2026', (2026, 6, 1), (2026, 9, 1)),
    ('podzim 2026', (2026, 9, 1), (2026, 12, 1)),
    ('zima 2026', (2026, 12, 1), (2027, 3, 1)),
]


@pytest.mark.parametrize("text,s,e", CASES)
def test_span(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))
