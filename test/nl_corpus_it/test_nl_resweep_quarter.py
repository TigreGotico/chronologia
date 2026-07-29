# -*- coding: utf-8 -*-
"""Second-pass sweep: calendar quarters "Qn <anno>" over 8 fresh years, and the
Italian ordinal-quarter phrasing "primo/secondo/terzo/quarto trimestre <anno>",
not overlapping test_nl_quarter.py's small hand-picked set. Gold: quarter N spans
months [3N-2 .. 3N], hand-derived, never the parser.

"terzo"/"quarto trimestre" hit the same fraction-homograph bug documented in
test_nl_ordinal_weekday_month.py (terzo/quarto spelled like "un terzo"/"un quarto"
the fraction) -- now FIXED for trimestre too: the ordinal reading is licensed
directly before the quarter noun so both words bind the quarter ordinal, while
the clock/duration fraction readings stay byte-identical."""
import pytest
from ._corpus import start_end, AstroDate

_CASES = [
    ('Q1 2015', AstroDate(2015, 1, 1, 0, 0), AstroDate(2015, 4, 1, 0, 0)),
    ('Q2 2015', AstroDate(2015, 4, 1, 0, 0), AstroDate(2015, 7, 1, 0, 0)),
    ('Q3 2015', AstroDate(2015, 7, 1, 0, 0), AstroDate(2015, 10, 1, 0, 0)),
    ('Q4 2015', AstroDate(2015, 10, 1, 0, 0), AstroDate(2016, 1, 1, 0, 0)),
    ('Q1 2016', AstroDate(2016, 1, 1, 0, 0), AstroDate(2016, 4, 1, 0, 0)),
    ('Q2 2016', AstroDate(2016, 4, 1, 0, 0), AstroDate(2016, 7, 1, 0, 0)),
    ('Q3 2016', AstroDate(2016, 7, 1, 0, 0), AstroDate(2016, 10, 1, 0, 0)),
    ('Q4 2016', AstroDate(2016, 10, 1, 0, 0), AstroDate(2017, 1, 1, 0, 0)),
    ('Q1 2019', AstroDate(2019, 1, 1, 0, 0), AstroDate(2019, 4, 1, 0, 0)),
    ('Q2 2019', AstroDate(2019, 4, 1, 0, 0), AstroDate(2019, 7, 1, 0, 0)),
    ('Q3 2019', AstroDate(2019, 7, 1, 0, 0), AstroDate(2019, 10, 1, 0, 0)),
    ('Q4 2019', AstroDate(2019, 10, 1, 0, 0), AstroDate(2020, 1, 1, 0, 0)),
    ('Q1 2022', AstroDate(2022, 1, 1, 0, 0), AstroDate(2022, 4, 1, 0, 0)),
    ('Q2 2022', AstroDate(2022, 4, 1, 0, 0), AstroDate(2022, 7, 1, 0, 0)),
    ('Q3 2022', AstroDate(2022, 7, 1, 0, 0), AstroDate(2022, 10, 1, 0, 0)),
    ('Q4 2022', AstroDate(2022, 10, 1, 0, 0), AstroDate(2023, 1, 1, 0, 0)),
    ('Q1 2024', AstroDate(2024, 1, 1, 0, 0), AstroDate(2024, 4, 1, 0, 0)),
    ('Q2 2024', AstroDate(2024, 4, 1, 0, 0), AstroDate(2024, 7, 1, 0, 0)),
    ('Q3 2024', AstroDate(2024, 7, 1, 0, 0), AstroDate(2024, 10, 1, 0, 0)),
    ('Q4 2024', AstroDate(2024, 10, 1, 0, 0), AstroDate(2025, 1, 1, 0, 0)),
    ('Q1 2027', AstroDate(2027, 1, 1, 0, 0), AstroDate(2027, 4, 1, 0, 0)),
    ('Q2 2027', AstroDate(2027, 4, 1, 0, 0), AstroDate(2027, 7, 1, 0, 0)),
    ('Q3 2027', AstroDate(2027, 7, 1, 0, 0), AstroDate(2027, 10, 1, 0, 0)),
    ('Q4 2027', AstroDate(2027, 10, 1, 0, 0), AstroDate(2028, 1, 1, 0, 0)),
    ('Q1 2029', AstroDate(2029, 1, 1, 0, 0), AstroDate(2029, 4, 1, 0, 0)),
    ('Q2 2029', AstroDate(2029, 4, 1, 0, 0), AstroDate(2029, 7, 1, 0, 0)),
    ('Q3 2029', AstroDate(2029, 7, 1, 0, 0), AstroDate(2029, 10, 1, 0, 0)),
    ('Q4 2029', AstroDate(2029, 10, 1, 0, 0), AstroDate(2030, 1, 1, 0, 0)),
    ('Q1 2033', AstroDate(2033, 1, 1, 0, 0), AstroDate(2033, 4, 1, 0, 0)),
    ('Q2 2033', AstroDate(2033, 4, 1, 0, 0), AstroDate(2033, 7, 1, 0, 0)),
    ('Q3 2033', AstroDate(2033, 7, 1, 0, 0), AstroDate(2033, 10, 1, 0, 0)),
    ('Q4 2033', AstroDate(2033, 10, 1, 0, 0), AstroDate(2034, 1, 1, 0, 0)),
    ('primo trimestre 2015', AstroDate(2015, 1, 1, 0, 0), AstroDate(2015, 4, 1, 0, 0)),
    ('secondo trimestre 2015', AstroDate(2015, 4, 1, 0, 0), AstroDate(2015, 7, 1, 0, 0)),
    ('primo trimestre 2016', AstroDate(2016, 1, 1, 0, 0), AstroDate(2016, 4, 1, 0, 0)),
    ('secondo trimestre 2016', AstroDate(2016, 4, 1, 0, 0), AstroDate(2016, 7, 1, 0, 0)),
    ('primo trimestre 2019', AstroDate(2019, 1, 1, 0, 0), AstroDate(2019, 4, 1, 0, 0)),
    ('secondo trimestre 2019', AstroDate(2019, 4, 1, 0, 0), AstroDate(2019, 7, 1, 0, 0)),
    ('primo trimestre 2022', AstroDate(2022, 1, 1, 0, 0), AstroDate(2022, 4, 1, 0, 0)),
    ('secondo trimestre 2022', AstroDate(2022, 4, 1, 0, 0), AstroDate(2022, 7, 1, 0, 0)),
    ('primo trimestre 2024', AstroDate(2024, 1, 1, 0, 0), AstroDate(2024, 4, 1, 0, 0)),
    ('secondo trimestre 2024', AstroDate(2024, 4, 1, 0, 0), AstroDate(2024, 7, 1, 0, 0)),
    ('primo trimestre 2027', AstroDate(2027, 1, 1, 0, 0), AstroDate(2027, 4, 1, 0, 0)),
    ('secondo trimestre 2027', AstroDate(2027, 4, 1, 0, 0), AstroDate(2027, 7, 1, 0, 0)),
    ('primo trimestre 2029', AstroDate(2029, 1, 1, 0, 0), AstroDate(2029, 4, 1, 0, 0)),
    ('secondo trimestre 2029', AstroDate(2029, 4, 1, 0, 0), AstroDate(2029, 7, 1, 0, 0)),
    ('primo trimestre 2033', AstroDate(2033, 1, 1, 0, 0), AstroDate(2033, 4, 1, 0, 0)),
    ('secondo trimestre 2033', AstroDate(2033, 4, 1, 0, 0), AstroDate(2033, 7, 1, 0, 0)),
]

@pytest.mark.parametrize("text,s,e", _CASES)
def test_quarter_resweep(text, s, e):
    assert start_end(text) == (s, e)


# "terzo"/"quarto trimestre <anno>" now bind the quarter ordinal: the ordinal
# reading of the fraction-homograph ("un terzo"/"un quarto") is licensed
# directly before the quarter noun "trimestre" (fix:
# numfold._license_ordinal_fraction quarter-word frame), while every clock/
# duration fraction reading ("un quarto d'ora", "le tre e un quarto") is
# untouched.  Gold is the correct quarter boundary, hand-derived.
_ORDINAL_TRIMESTRE_CASES = [
    ('terzo trimestre 2015', AstroDate(2015, 7, 1, 0, 0), AstroDate(2015, 10, 1, 0, 0)),
    ('quarto trimestre 2015', AstroDate(2015, 10, 1, 0, 0), AstroDate(2016, 1, 1, 0, 0)),
    ('terzo trimestre 2016', AstroDate(2016, 7, 1, 0, 0), AstroDate(2016, 10, 1, 0, 0)),
    ('quarto trimestre 2016', AstroDate(2016, 10, 1, 0, 0), AstroDate(2017, 1, 1, 0, 0)),
    ('terzo trimestre 2019', AstroDate(2019, 7, 1, 0, 0), AstroDate(2019, 10, 1, 0, 0)),
    ('quarto trimestre 2019', AstroDate(2019, 10, 1, 0, 0), AstroDate(2020, 1, 1, 0, 0)),
    ('terzo trimestre 2022', AstroDate(2022, 7, 1, 0, 0), AstroDate(2022, 10, 1, 0, 0)),
    ('quarto trimestre 2022', AstroDate(2022, 10, 1, 0, 0), AstroDate(2023, 1, 1, 0, 0)),
    ('terzo trimestre 2024', AstroDate(2024, 7, 1, 0, 0), AstroDate(2024, 10, 1, 0, 0)),
    ('quarto trimestre 2024', AstroDate(2024, 10, 1, 0, 0), AstroDate(2025, 1, 1, 0, 0)),
    ('terzo trimestre 2027', AstroDate(2027, 7, 1, 0, 0), AstroDate(2027, 10, 1, 0, 0)),
    ('quarto trimestre 2027', AstroDate(2027, 10, 1, 0, 0), AstroDate(2028, 1, 1, 0, 0)),
    ('terzo trimestre 2029', AstroDate(2029, 7, 1, 0, 0), AstroDate(2029, 10, 1, 0, 0)),
    ('quarto trimestre 2029', AstroDate(2029, 10, 1, 0, 0), AstroDate(2030, 1, 1, 0, 0)),
    ('terzo trimestre 2033', AstroDate(2033, 7, 1, 0, 0), AstroDate(2033, 10, 1, 0, 0)),
    ('quarto trimestre 2033', AstroDate(2033, 10, 1, 0, 0), AstroDate(2034, 1, 1, 0, 0)),
]

@pytest.mark.parametrize("text,s,e", _ORDINAL_TRIMESTRE_CASES)
def test_quarter_resweep_trimestre_ordinal(text, s, e):
    assert start_end(text) == (s, e)

