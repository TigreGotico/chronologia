"""Russian part word before a numbered year names that third of the year.

"early 2024" is the first third of 2024, as in English.  2024 has 366 days, so
each third is 122 days: January 1 to May 2, May 2 to September 1, and
September 1 to January 1.  The expected values come from ``timedelta``.  The
part word stays out of the remainder.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import AstroDate, parse

YEAR = datetime(2024, 1, 1)
THIRDS = [(YEAR + timedelta(days=122 * i), YEAR + timedelta(days=122 * (i + 1)))
          for i in range(3)]


def _ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute)


@pytest.mark.parametrize("text,part,third", [
    ("в начале 2024 года", "начале", 0),
    ("в середине 2024 года", "середине", 1),
    ("в конце 2024 года", "конце", 2),
])
def test_part_before_numbered_year(text, part, third):
    result = parse(text)
    assert result is not None
    start, end = THIRDS[third]
    assert result.span.start == _ad(start)
    assert result.span.end == _ad(end)
    assert part not in result.remainder.split()
