# -*- coding: utf-8 -*-
"""The "Nth week of <month>" construction for sv.

Swedish names an ordinal week inside a month with the preposition "i"
("tredje veckan i mars" = the third week in March), the same "i" that means
"in" in "i mars".  Before the connector was taught, the ordinal-week qualifier
was silently dropped and the bare month returned; now the phrase reads the
week itself.  "av mars" is the partitive-flavoured variant and is accepted too.
"""
import pytest

from ._corpus import AstroDate, start_end


@pytest.mark.parametrize("text", [
    'tredje veckan i mars',
    'tredje vecka i mars',
    'tredje veckan av mars',
])
def test_third_week_of_march(text):
    s, e = start_end(text)
    assert (s, e) == (AstroDate(2017, 3, 20), AstroDate(2017, 3, 27))


@pytest.mark.parametrize("text,ymd", [
    ('första veckan i mars', (2017, 3, 6, 2017, 3, 13)),
    ('andra veckan i mars', (2017, 3, 13, 2017, 3, 20)),
])
def test_other_weeks_of_march(text, ymd):
    s, e = start_end(text)
    assert (s, e) == (AstroDate(*ymd[:3]), AstroDate(*ymd[3:]))
