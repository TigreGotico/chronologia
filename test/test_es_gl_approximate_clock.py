"""es and gl "sobre" and es "tipo" before a clock join it to the part of the day.

"por la mañana sobre las 7" is 07:00 in the morning, as "por la mañana a las
7" is.  es "sobre": "Referido al tiempo, indica que se está cerca de un
momento determinado" (Wikcionario s.v. "sobre", 7).  es "tipo": "Aproximadamente
a las" (Wikcionario s.v. "tipo", adverbio de tiempo, 9).  gl "sobre": "Indica
unha localización temporal imprecisa", "Chegou sobre as seis" (Galizionario
s.v. "sobre").  The clock is the one the word qualifies.  Said at 13:04 on
Tuesday 2017-06-27 the morning hour 7 is Wednesday 2017-06-28 07:00.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)
SEVEN = datetime(2017, 6, 28, 7, 0)

ROWS = [
    ("por la mañana sobre las 7", "es", ""),
    ("por la mañana tipo las 7", "es", ""),
    ("pola mañá sobre as 7", "gl", ""),
    ("avíseme de lunes a viernes por la mañana sobre las 7", "es", "avíseme de lunes a viernes"),
    ("avísame de luns a venres pola mañá sobre as 7", "gl", "avísame de luns a venres"),
]


@pytest.mark.parametrize("text,lang,remainder", ROWS)
def test_an_approximate_clock_joins_the_part_of_the_day(text, lang, remainder):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == SEVEN
    assert found.remainder == remainder


def test_the_exact_clock_reads_the_same_way():
    found = extract_timespan("avíseme de lunes a viernes por la mañana a las 7", "es", ANCHOR)
    assert found.span.start.datetime() == SEVEN
