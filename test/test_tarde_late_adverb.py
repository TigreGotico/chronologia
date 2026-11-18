# -*- coding: utf-8 -*-
"""es, pt and gl "tarde" is the afternoon and also the adverb "late".

Before a clock and after another word of its clause, "tarde" is the adverb
("llego tarde a las 6:30", I arrive late at 6:30) and does not put the clock
in the pm half; the clock takes the next of its two twelve-hour readings
(rulings 17 and 23).  A "tarde" that opens the clause or follows a preposition
is the afternoon (ruling 27), and clause punctuation keeps a word in another
clause from deciding the half.  Sources: Wikcionario (es), Dicionário Priberam
(pt) and Dicionario da Real Academia Galega (gl), s.v. "tarde".

Expected instants are worked out by hand: said at 23:00 on 27 June, the next
06:30 is 28 June 06:30; said at 05:00, it is 27 June 06:30.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan

LATE = datetime(2017, 6, 27, 23, 0)
EARLY = datetime(2017, 6, 27, 5, 0)

ROWS = [
    # "tarde" means late: the next twelve-hour reading
    ("es", "llego tarde a las 6:30", LATE, datetime(2017, 6, 28, 6, 30)),
    ("es", "llego tarde a las 6:30", EARLY, datetime(2017, 6, 27, 6, 30)),
    ("es", "llego tarde a las 6", LATE, datetime(2017, 6, 28, 6, 0)),
    ("es", "salgo tarde a las 6", EARLY, datetime(2017, 6, 27, 6, 0)),
    ("es", "muy tarde a las 6:30", LATE, datetime(2017, 6, 28, 6, 30)),
    ("pt", "cheguei tarde às 6:30", LATE, datetime(2017, 6, 28, 6, 30)),
    ("pt", "cheguei tarde às 6:30", EARLY, datetime(2017, 6, 27, 6, 30)),
    ("gl", "chego tarde ás 6:30", LATE, datetime(2017, 6, 28, 6, 30)),
    # clause punctuation ends the clock's side: a word in another sentence is
    # not beside the clock (ruling 27)
    ("es", "tarde. a las 6:30", LATE, datetime(2017, 6, 28, 6, 30)),
    ("es", "llegaré tarde, a las 6:30", LATE, datetime(2017, 6, 28, 6, 30)),
    ("es", "es tarde: a las 6:30", LATE, datetime(2017, 6, 28, 6, 30)),
    ("pt", "vou chegar tarde, às 6", LATE, datetime(2017, 6, 28, 6, 0)),
    ("pt", "já é tarde, às 6:30", EARLY, datetime(2017, 6, 27, 6, 30)),
    # "tarde" is the afternoon: the pm half
    ("es", "tarde a las 4:30", LATE, datetime(2017, 6, 28, 16, 30)),
    ("es", "no puedo antes. tarde a las 4:30", LATE,
     datetime(2017, 6, 28, 16, 30)),
    ("gl", "tarde ás 4:30", EARLY, datetime(2017, 6, 27, 16, 30)),
    ("pt", "de tarde às 5:30", LATE, datetime(2017, 6, 28, 17, 30)),
    ("pt", "à tarde às 5:30", EARLY, datetime(2017, 6, 27, 17, 30)),
]


@pytest.mark.parametrize("lang,text,anchor,expected", ROWS)
def test_tarde_before_the_clock(lang, text, anchor, expected):
    found = extract_timespan(text, lang, anchor)
    assert found.span.start.datetime() == expected
    assert found.span.end.datetime() == expected + timedelta(minutes=1)
