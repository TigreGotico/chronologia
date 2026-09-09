"""The Persian half word counts a length when a unit noun closes it.

Persian counts an offset with a number and a unit ("دو ساعت دیگه" in two
hours). The half word is withheld from the number fold because it owns the
clock fraction slot, so the half-length frame had no count at all and the
phrase resolved to nothing while its duration read correctly.

Attested in fa.wikipedia running prose: "ساعت به جای یک ساعت، نیم ساعت عقب
کشیده شد" (ساعت رسمی ایران), "هر نیم ساعت" (منیزیم), "بین نیم ساعت تا دو ساعت"
(داستان کوتاه). The construction has 602 insource hits for the hour and 877
for the century.

The clock reading is the control: "سه و نیم" is half past three, where the half
word follows the conjunction and no unit closes it, so it must stay a word.
"""
import pytest

from ._corpus import ANCHOR, nomatch, start

#: half + unit, counted forward from the anchor 2017-06-27 13:04.
HALF_LENGTHS = [
    ("نیم ساعت دیگه", "2017-06-27T13:34:00"),   # + 30 minutes
    ("نیم روز دیگه", "2017-06-28T01:04:00"),    # + 12 hours
]

#: whole counts in the same frame, which must not move.
WHOLE_LENGTHS = [
    ("یک ساعت دیگه", "2017-06-27T14:04:00"),
    ("دو ساعت دیگه", "2017-06-27T15:04:00"),
]

#: the clock fraction, where no unit closes the half word.
CLOCK_FRACTION = [
    ("سه و نیم", "2017-06-28T03:30:00"),
    ("ساعت سه و نیم", "2017-06-28T03:30:00"),
]


@pytest.mark.parametrize("text,expected", HALF_LENGTHS)
def test_a_half_length_counts_from_the_anchor(text, expected):
    assert str(start(text)) == expected


@pytest.mark.parametrize("text,expected", WHOLE_LENGTHS + CLOCK_FRACTION)
def test_the_neighbouring_readings_are_unchanged(text, expected):
    assert str(start(text)) == expected
