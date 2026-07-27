# -*- coding: utf-8 -*-
"""Italian fractional-hour durations: ``extract_duration(text, "it")``.

"tre quarti di un'ora" (three quarters of an hour) is 45 minutes; "un quarto di
un'ora" (a quarter of an hour) is 15 minutes.  The fraction ("un quarto" = 1/4,
"tre quarti" = 3/4, "mezza"/"mezzo" = 1/2) multiplies the hour it qualifies.

Source: Italian Wikipedia, "Ora (unita di misura)" and everyday usage
("un quarto d'ora", "tre quarti d'ora", "mezz'ora").
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "it"

_CASES = [
    ("un quarto di un'ora", timedelta(minutes=15)),
    ("tre quarti di un'ora", timedelta(minutes=45)),
    ("mezza di un'ora", timedelta(minutes=30)),
    # trailing additive fraction already worked; pin it as a regression.
    ("un'ora e mezza", timedelta(hours=1, minutes=30)),
    # plain unit durations must stay byte-exact.
    ("due ore", timedelta(hours=2)),
    ("30 minuti", timedelta(minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


# the contracted forms ("un quarto d'ora", "mezz'ora") are added when the
# tokenizer splits the elision the same way; pinned here so the behaviour is
# explicit whichever way it currently resolves.
@pytest.mark.parametrize("text,expected", [
    ("un quarto d'ora", timedelta(minutes=15)),
    ("tre quarti d'ora", timedelta(minutes=45)),
])
def test_contracted_hour(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected
