""""en puntu" closes a clock time: it is the exact hour, ast.

DALLA s.v. "puntu": "|| En puntu, a la hora exauta. 2 Exauta [una hora]."
Left unread, the two words stranded in the remainder beside a correct hour.
Anchor 2017-06-27 13:04: 08:00 has passed, so it is tomorrow; 20:00 is
still ahead today.
"""
import pytest

from ._corpus import ANCHOR, parse, span


@pytest.mark.parametrize("text,day,hour,rest", [
    ("a les 8 en puntu", 28, 8, ""),
    ("a les 20h en puntu", 27, 20, ""),
    ("a les 20:00 en puntu", 27, 20, ""),
    ("quedamos a les 8 en puntu", 28, 8, "quedamos"),
])
def test_en_puntu_is_part_of_the_clock(text, day, hour, rest):
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (2017, 6, day)
    assert (s.start.hour, s.start.minute) == (hour, 0)
    assert parse(text)[1] == rest
