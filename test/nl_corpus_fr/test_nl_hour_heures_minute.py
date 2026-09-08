"""The French spoken clock names the minute straight after "heures".

"neuf heures dix" is ten past nine: no connector stands between the hour
word and the minute, unlike "neuf heures et quart" and "neuf heures moins
dix", which take one.

Anchor 2017-06-27 13:04.
"""
import pytest

from ._corpus import AstroDate, parse, start


@pytest.mark.parametrize("text,day,hour,minute", [
    ("neuf heures dix", 28, 9, 10),
    ("à neuf heures dix", 28, 9, 10),
    ("à 9 heures 10", 28, 9, 10),
    # 20:30 is still ahead of the 13:04 anchor, so it stays today
    ("vingt heures trente", 27, 20, 30),
])
def test_the_minute_after_heures(text, day, hour, minute):
    assert start(text) == AstroDate(2017, 6, day, hour, minute)
    assert parse(text).remainder == ""


@pytest.mark.parametrize("text,day,hour,minute", [
    # the connector forms and the bare hour must keep their readings
    ("neuf heures", 28, 9, 0),
    ("neuf heures et quart", 28, 9, 15),
    ("neuf heures moins dix", 28, 8, 50),
    ("9h10", 28, 9, 10),
    ("à neuf heures du soir", 27, 21, 0),
])
def test_the_forms_that_already_read(text, day, hour, minute):
    assert start(text) == AstroDate(2017, 6, day, hour, minute)
