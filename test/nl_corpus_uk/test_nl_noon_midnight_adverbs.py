"""Ukrainian "опівдні" (at noon) and "опівночі" (at midnight).

Both are adverbs of the landmarks this locale already reads as nouns
("полудень", "північ").  СУМ-11 glosses "опівдні" as "В середині дня, в час,
коли сонце стоїть у зеніті" and "опівночі" as "Серед ночі, о дванадцятій чи
близько дванадцятої години ночі".  At the 13:04 anchor, today's noon has
passed, so the next noon and the next midnight both fall on 28 June.
"""
import pytest

from ._corpus import ANCHOR, ad, parse


def _at(day, hour):
    return ad(ANCHOR.replace(day=day, hour=hour, minute=0, second=0,
                             microsecond=0))


@pytest.mark.parametrize("text,day,hour,remainder", [
    ("опівдні", 28, 12, ""),
    ("опівночі", 28, 0, ""),
    ("завтра опівдні", 28, 12, ""),
    ("нагадай мені опівдні", 28, 12, "нагадай мені"),
])
def test_noon_and_midnight_adverbs(text, day, hour, remainder):
    r = parse(text)
    assert r is not None
    assert r.span.start == _at(day, hour)
    assert r.remainder == remainder
