"""The two Filipino clocks, and the direction switch inside the native one.

Filipino tells the time two ways.  The Spanish-lexified clock puts the hour
after ``alas`` (``ala`` before one) as a bare Spanish cardinal and hangs the
half off it with ``y medya``, additively: "alas kuwatro y medya ng hapon" is
16:30, half past the hour just named.  The native clock names the hour as an
``ika-`` ordinal and counts native minutes toward it, forward with
``makalipas`` and backward with ``bago`` -- and the direction word is the
whole difference between 16:15 and 15:45 on the same stated hour.

Every reading here is pinned adversarially: the rival direction is asserted
to give a different answer, not merely the right one asserted present.  The
worked pairs come from en.wikipedia.org, "Date and time notation in the
Philippines", which gives both spoken forms for each of a set of clock times.
"""
import pytest

from ._corpus import next_time, nomatch, remainder, start

#: (Spanish-lexified form, native form, hour, minute) -- the source states
#: both spoken forms for the same clock time.
BOTH_SYSTEMS = [
    ("alas sais ng umaga", "ika-anim ng umaga", 6, 0),
    ("alas dose ng tanghali", "ikalabindalawa ng tanghali", 12, 0),
    ("alas dose ng hatinggabi", "ikalabindalawa ng hatinggabi", 0, 0),
    ("alas kuwatro y medya ng hapon",
     "tatlumpung minuto makalipas ang ika-apat ng hapon", 16, 30),
    ("alas otso y medya ng gabi",
     "tatlumpung minuto makalipas ang ikawalo ng gabi", 20, 30),
]


@pytest.mark.parametrize("spanish,native,h,mi", BOTH_SYSTEMS)
def test_the_two_systems_name_the_same_time(spanish, native, h, mi):
    assert start(spanish) == next_time(h, mi)
    assert start(native) == next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("ala uno", 1, 0),
    ("alas dos", 2, 0),
    ("alas tres", 3, 0),
    ("alas kuwatro", 4, 0),
    ("alas singko", 5, 0),
    ("alas sais ng umaga", 6, 0),
    ("alas siyete ng umaga", 7, 0),
    ("alas otso ng umaga", 8, 0),
    ("alas nuwebe ng umaga", 9, 0),
    ("alas diyes ng umaga", 10, 0),
    ("alas onse ng umaga", 11, 0),
    ("alas dose ng tanghali", 12, 0),
])
def test_spanish_hour_on_the_hour(text, h, mi):
    assert start(text) == next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("ala uno y medya", 1, 30),
    ("alas dos y medya", 2, 30),
    ("alas kuwatro y medya ng hapon", 16, 30),
    ("alas otso y medya ng gabi", 20, 30),
    ("alas onse y medya ng umaga", 11, 30),
])
def test_y_medya_is_half_past_the_named_hour(text, h, mi):
    assert start(text) == next_time(h, mi)


@pytest.mark.parametrize("text,stated", [
    ("alas dos y medya", 2), ("alas kuwatro y medya ng hapon", 16),
    ("alas otso y medya ng gabi", 20),
])
def test_y_medya_is_not_the_toward_hour_reading(text, stated):
    """The Continental-Germanic reading ("halb neun" == 08:30) would put the
    half BEFORE the stated hour; Filipino puts it after."""
    assert start(text).hour == stated


@pytest.mark.parametrize("text,h,mi", [
    ("limang minuto makalipas ang ika-anim ng umaga", 6, 5),
    ("labingwalong minuto makalipas ang ikasiyam ng umaga", 9, 18),
    ("labinlimang minuto makalipas ang ikalabing-isa ng umaga", 11, 15),
    ("tatlumpung minuto makalipas ang ika-apat ng hapon", 16, 30),
    ("labinlimang minuto makalipas ang ika-apat ng hapon", 16, 15),
    ("apat na minuto makalipas ang ika-anim ng umaga", 6, 4),
    ("labing-anim na minuto makalipas ang ika-anim ng umaga", 6, 16),
])
def test_makalipas_counts_forward_from_the_named_hour(text, h, mi):
    assert start(text) == next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("labinlimang minuto bago ang ika-apat ng hapon", 15, 45),
    ("dalawampu't dalawang minuto bago mag ika-anim ng gabi", 17, 38),
    ("dalawampu't limang minuto bago mag ikalabing-isa ng gabi", 22, 35),
    ("limang minuto bago ang ika-anim ng umaga", 5, 55),
    ("tatlumpung minuto bago ang ika-apat ng hapon", 15, 30),
    ("anim na minuto bago ang ika-apat ng hapon", 15, 54),
    ("labing-anim na minuto bago ang ika-apat ng hapon", 15, 44),
])
def test_bago_counts_backward_from_the_named_hour(text, h, mi):
    assert start(text) == next_time(h, mi)


#: the switch, stated as the pair it is: one stated hour, one minute count,
#: two direction words, two different clock times.
SWITCH = [
    ("labinlimang minuto makalipas ang ika-apat ng hapon",
     "labinlimang minuto bago ang ika-apat ng hapon", (16, 15), (15, 45)),
    ("limang minuto makalipas ang ika-anim ng umaga",
     "limang minuto bago ang ika-anim ng umaga", (6, 5), (5, 55)),
    ("tatlumpung minuto makalipas ang ika-apat ng hapon",
     "tatlumpung minuto bago ang ika-apat ng hapon", (16, 30), (15, 30)),
]


@pytest.mark.parametrize("forward,backward,fwd,bwd", SWITCH)
def test_the_direction_word_moves_the_answer(forward, backward, fwd, bwd):
    f, b = start(forward), start(backward)
    assert (f.hour, f.minute) == fwd
    assert (b.hour, b.minute) == bwd
    assert f != b


@pytest.mark.parametrize("forward,backward,fwd,bwd", SWITCH)
def test_neither_direction_can_be_read_as_the_other(forward, backward,
                                                    fwd, bwd):
    """Reading ``bago`` as ``makalipas`` (or the reverse) is the failure this
    locale exists to prevent: it moves the answer by twice the minute count
    and, past the half hour, by a whole hour as well."""
    assert (start(forward).hour, start(forward).minute) != bwd
    assert (start(backward).hour, start(backward).minute) != fwd


@pytest.mark.parametrize("text,h", [
    ("ikalabindalawa ng hatinggabi", 0),
    ("ikalabindalawa ng tanghali", 12),
    ("ika-anim ng umaga", 6),
    ("ikasiyam ng umaga", 9),
    ("ika-apat ng hapon", 16),
    ("ikawalo ng gabi", 20),
])
def test_bare_ika_ordinal_hour(text, h):
    assert start(text).hour == h


@pytest.mark.parametrize("text,h", [
    ("alas dose ng hatinggabi", 0),
    ("alas dose ng tanghali", 12),
    ("alas otso ng umaga", 8),
    ("alas otso ng gabi", 20),
])
def test_the_daypart_fixes_which_half_of_the_day(text, h):
    assert start(text).hour == h


def test_morning_and_evening_eight_are_twelve_hours_apart():
    assert start("alas otso ng gabi").hour - start("alas otso ng umaga").hour \
        == 12


@pytest.mark.parametrize("text,h,mi", [
    ("15:30", 15, 30), ("09:05", 9, 5), ("00:00", 0, 0), ("23:59", 23, 59),
])
def test_digit_clock(text, h, mi):
    s = start(text)
    assert (s.hour, s.minute) == (h, mi)


@pytest.mark.parametrize("text,h", [("hatinggabi", 0), ("tanghali", 12)])
def test_clock_landmarks(text, h):
    assert start(text).hour == h


@pytest.mark.parametrize("text", [
    "alas",                        # the lead-in with no hour
    "medya",                       # a half with no hour
    "bago",                        # a direction with nothing to count from
    "makalipas",                   # the other direction, likewise
    "minuto bago ang ika-apat",    # a count word with no count
    "ika",                         # a stranded ordinal prefix
])
def test_incomplete_clock_is_not_a_time(text):
    nomatch(text)


def test_spanish_minute_count_is_left_unconsumed():
    """The Spanish-lexified clock also states arbitrary minutes ("alas onse
    kinse ng umaga" == 11:15), but that form is NOT shipped: reading it would
    need the engine to apply a bare minute slot with no direction word, which
    it does not do.  The hour still parses; the minute stays visibly in the
    remainder rather than being silently dropped from an 11:15 answer."""
    assert start("alas onse kinse ng umaga").hour == 11
    assert start("alas onse kinse ng umaga").minute == 0
    assert "kinse" in remainder("alas onse kinse ng umaga")
