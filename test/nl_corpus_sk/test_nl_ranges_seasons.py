"""Slovak ranges and seasons.

Ranges: "od A do B" and "medzi A a B"; framing words are the Slovak
connectors od/do/medzi/a.  Between-ranges take instrumental month forms.
Seasons are meteorological, northern hemisphere.
"""
import pytest

from ._corpus import AstroDate, start_end


def _d(s):
    y, m, dd = (int(x) for x in s.split("-"))
    return AstroDate(y, m, dd)


@pytest.mark.parametrize("text,s,e", [
    ("od júna do augusta", "2017-6-1", "2017-9-1"),
    ("od januára do marca", "2017-1-1", "2017-4-1"),
    ("od októbra do decembra", "2017-10-1", "2018-1-1"),
    ("od júna 2020 do augusta 2021", "2020-6-1", "2021-9-1"),
])
def test_from_to_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


@pytest.mark.parametrize("text,s,e", [
    ("medzi júnom a septembrom", "2017-6-1", "2017-10-1"),
    ("medzi aprílom a júnom", "2017-4-1", "2017-7-1"),
])
def test_between_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


@pytest.mark.parametrize("text,s,e", [
    ("budúca zima", "2017-12-1", "2018-3-1"),
    ("leto 2020", "2020-6-1", "2020-9-1"),
    ("zima 2019", "2019-12-1", "2020-3-1"),
])
def test_season(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)
