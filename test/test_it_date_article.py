"""The Italian article that opens a date belongs to the date.

"Hanno però l'articolo i nomi degli anni (il 1974), i giorni del mese (il 12
luglio) e della settimana (il martedì)" (Treccani, Enciclopedia
dell'Italiano, "articolo", "Formule senza articolo").  So "il" in front of a
date is part of it and must not stay in the remainder.  The anchor is
Saturday 2026-10-17 12:00.
"""
from datetime import datetime

import pytest

from chronologia import AstroDate, extract_timespan

ANCHOR = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("text, start, end, rest", [
    # 15 March 2026 has passed, so the next one
    ("il 15 marzo", (2027, 3, 15), (2027, 3, 16), ""),
    ("il 12 luglio", (2027, 7, 12), (2027, 7, 13), ""),
    ("il 12 luglio 2027", (2027, 7, 12), (2027, 7, 13), ""),
    # the next Tuesday after Saturday 17 October
    ("il martedì", (2026, 10, 20), (2026, 10, 21), ""),
    ("il prossimo martedì", (2026, 10, 20), (2026, 10, 21), ""),
    ("il 1974", (1974, 1, 1), (1975, 1, 1), ""),
    ("ci vediamo il 15 marzo", (2027, 3, 15), (2027, 3, 16), "ci vediamo"),
    # only the article next to the date folds
    ("il bambino nasce il 15 marzo", (2027, 3, 15), (2027, 3, 16),
     "il bambino nasce"),
])
def test_article_opens_the_date(text, start, end, rest):
    r = extract_timespan(text, "it", ANCHOR)
    assert (r.span.start, r.span.end, r.remainder) == (
        AstroDate(*start), AstroDate(*end), rest)
