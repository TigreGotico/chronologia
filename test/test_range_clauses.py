"""One role per range word: a connector that opens a "from A to B" clause is a
range word, also where its surface is an "until" word (de "bis", nl "tot")."""
from datetime import datetime

import pytest

from chronologia import extract_recurrence
from chronologia.extract import _timespan_engine
from chronologia.extract.timespan import RangeClause, range_clauses

ANCHOR = datetime(2026, 11, 22, 9, 0)


def clauses(lang, text, consumed=()):
    engine = _timespan_engine(lang)
    return range_clauses(engine.tokenize(text), engine.spec, set(consumed),
                         lambda left: left[0].text != "9")


# Token indexes are counted by hand from the words of each phrase.
@pytest.mark.parametrize("lang, text, consumed, expected", [
    # von(0) Juni(1) bis(2) August(3)
    ("de", "von Juni bis August", (), [RangeClause(0, 1, 2, 3, 4)]),
    # from(0) june(1) until(2) august(3)
    ("en", "from june until august", (), [RangeClause(0, 1, 2, 3, 4)]),
    # until alone is no clause
    ("en", "every friday until june", (), []),
    # a clock before an until word is no clause (from 9 am until 5 december)
    ("en", "from 9am until 5 december", (), []),
    # but a clock before a plain "to" is one
    ("en", "from 9am to 5 december", (), [RangeClause(0, 1, 3, 4, 6)]),
    # pt "até à" is an until word only, a longer match than the "to" word "até"
    ("pt", "do dia 3 até à sexta", (), []),
    # a clause with nothing before the connector or after it is no clause
    ("de", "von bis August", (), []),
    ("de", "von Juni bis", (), []),
    # van(0) maandag(1) tot(2) en(3) met(4) vrijdag(5): "tot en met" and the
    # "tot" prefix of it, then the "en" of "tussen A en B"
    ("nl", "van maandag tot en met vrijdag", (),
     [RangeClause(0, 1, 2, 5, 6), RangeClause(0, 1, 3, 4, 6)]),
    # two leads, rightmost first, and the first lead also pairs with the
    # farther "to": from(0) 9(1) to(2) 5(3) from(4) june(5) to(6) august(7)
    ("en", "from 9 to 5 from june to august", (),
     [RangeClause(4, 5, 6, 7, 8), RangeClause(0, 1, 2, 3, 4),
      RangeClause(0, 1, 6, 7, 8)]),
    # a consumed clause opens none and no longer ends the bound before it
    ("en", "from 9 to 5 from june to august", (4, 5, 6, 7),
     [RangeClause(0, 1, 2, 3, 8)]),
])
def test_range_clauses(lang, text, consumed, expected):
    assert clauses(lang, text, consumed) == expected


@pytest.mark.parametrize("lang, text, rule, remainder", [
    ("de", "jeden Montag von Juni bis August",
     "FREQ=WEEKLY;UNTIL=20270801T000000;BYDAY=MO", ""),
    ("en", "every monday from june until august",
     "FREQ=WEEKLY;UNTIL=20270801T000000;BYDAY=MO", ""),
    ("nl", "elke dag van maandag tot en met vrijdag",
     "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR", ""),
    # a plain until bound keeps its role
    ("de", "jeden Montag bis August",
     "FREQ=WEEKLY;UNTIL=20270801T000000;BYDAY=MO", ""),
    ("en", "every friday until june",
     "FREQ=WEEKLY;UNTIL=20270601T000000;BYDAY=FR", ""),
])
def test_a_range_word_is_read_once(lang, text, rule, remainder):
    got = extract_recurrence(text, lang, ANCHOR)
    assert str(got.recurrence) == rule
    assert got.remainder == remainder
