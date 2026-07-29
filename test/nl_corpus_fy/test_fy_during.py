"""fy: the 'yn' (in / during) preposition fronting a period.

'yn juny', 'yn 2020', 'yn maart 2020', 'yn de simmer' resolve to the same span
as the bare period -- the preposition is transparent.
"""
import pytest

from ._corpus import start_end, AstroDate


@pytest.mark.parametrize("text,s,e", [
    ('yn juny', (2017, 6, 1), (2017, 7, 1)),
    ('yn 2020', (2020, 1, 1), (2021, 1, 1)),
    ('yn maart 2020', (2020, 3, 1), (2020, 4, 1)),
    ('yn de simmer', (2017, 6, 1), (2017, 9, 1)),
])
def test_during_period(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))
