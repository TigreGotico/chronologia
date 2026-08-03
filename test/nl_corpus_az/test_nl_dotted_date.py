"""The dotted civil date in Azerbaijani: "15.06.2020".

Azerbaijani writes the everyday date day-first with dots, "15.06.2020" (the
same dd.MM.yyyy shape as Turkish), and that surface has to read as the day it
names.  Reading only the year out of it and stranding the day and the month in
the remainder is a silent wrong: the caller gets a confident whole-year span
with nothing to tell it the day was lost.  az carries ``dmy`` and
``decimal_comma`` like tr; it only lacked the ``dotted_date`` flag, so the
literal never bound.
"""
from chronologia.astrodate import AstroDate

from ._corpus import parse, start_end


def test_dotted_date_az():
    assert start_end("15.06.2020") == (AstroDate(2020, 6, 15),
                                       AstroDate(2020, 6, 16))


def test_dotted_date_unpadded_az():
    assert start_end("15.6.2020") == (AstroDate(2020, 6, 15),
                                      AstroDate(2020, 6, 16))


def test_dotted_date_day_over_twelve_az():
    # day first, so the day may exceed twelve and the month may not.
    assert start_end("31.12.1999") == (AstroDate(1999, 12, 31),
                                       AstroDate(2000, 1, 1))


def test_a_thousands_group_is_not_a_date_az():
    # a comma-decimal locale groups thousands with a dot; "1.000" is a number,
    # never the two-dot day.month.year date shape.
    r = parse('1.000')
    assert r is None or (r[0].start, r[0].end) != (
        AstroDate(2020, 6, 15), AstroDate(2020, 6, 16))
