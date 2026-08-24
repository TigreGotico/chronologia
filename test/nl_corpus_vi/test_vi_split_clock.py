"""The clock that runs BOTH ways inside one hour.

Vietnamese names the half hour forward and the minutes-before backward, in the
same grammar, with no cue but the marker word:

    hai giờ rưỡi        02:30   rưỡi counts from the hour already named
    ba giờ kém mười lăm 02:45   kém names the hour approached and subtracts

Every other locale in this corpus family picks one direction and holds it --
Icelandic "hálf" always looks forward to the coming hour, Welsh "wedi" always
looks back at the one just spoken.  Here both live side by side, so each half
of the split is pinned against the wrong answer the other half would give:
rưỡi must never land an hour early, and kém must never land past the hour it
names.

Sources for both directions are the dictionary's own worked examples --
"ba (giờ) rưỡi chiều" glossed as 3:30 PM, and "ba giờ kém mười" glossed as ten
to three, 2:50.
"""
import pytest

from ._corpus import parse, remainder, start


@pytest.mark.parametrize("text,hour", [
    ("một giờ rưỡi", 1),
    ("hai giờ rưỡi", 2),
    ("ba giờ rưỡi", 3),
    ("bốn giờ rưỡi", 4),
    ("năm giờ rưỡi", 5),
    ("chín giờ rưỡi", 9),
    ("mười giờ rưỡi", 10),
    ("mười một giờ rưỡi", 11),
])
def test_ruoi_counts_from_the_hour_it_names(text, hour):
    s = start(text)
    assert (s.hour, s.minute) == (hour, 30)


@pytest.mark.parametrize("text,hour", [
    ("hai rưỡi", 2),
    ("mười rưỡi", 10),
])
def test_ruoi_without_the_hour_word(text, hour):
    s = start(text)
    assert (s.hour, s.minute) == (hour, 30)


@pytest.mark.parametrize("text,hour", [
    ("hai giờ rưỡi", 2),
    ("bảy giờ rưỡi", 7),
    ("mười giờ rưỡi", 10),
])
def test_ruoi_never_lands_in_the_previous_hour(text, hour):
    """The toward-the-hour reading of the Germanic and Icelandic locales
    would put every one of these thirty minutes too early.  Vietnamese does
    not, and this is the assertion that says so."""
    s = start(text)
    assert (s.hour, s.minute) != (hour - 1, 30)
    assert s.hour == hour


@pytest.mark.parametrize("text,hour,minute", [
    ("ba giờ kém mười", 2, 50),
    ("ba giờ kém mười lăm", 2, 45),
    ("năm giờ kém mười", 4, 50),
    ("năm giờ kém hai mươi", 4, 40),
    ("mười giờ kém mười lăm", 9, 45),
    ("bốn giờ kém 5 phút", 3, 55),
    ("ba giờ kém mười lăm phút", 2, 45),
])
def test_kem_subtracts_from_the_hour_it_names(text, hour, minute):
    s = start(text)
    assert (s.hour, s.minute) == (hour, minute)


@pytest.mark.parametrize("text,named", [
    ("ba giờ kém mười", 3),
    ("năm giờ kém hai mươi", 5),
    ("mười giờ kém mười lăm", 10),
])
def test_kem_never_reads_as_past_the_hour(text, named):
    """The additive reading -- treating kém as if it were rưỡi or a bare
    "and" -- would put the time INSIDE the hour that was spoken.  It must
    land in the hour before it instead."""
    s = start(text)
    assert s.hour == named - 1
    assert s.hour != named


@pytest.mark.parametrize("text,hour,minute", [
    ("bốn giờ mười phút", 4, 10),
    ("hai giờ hai mươi phút", 2, 20),
    ("bảy giờ bốn mươi lăm phút", 7, 45),
    ("2 giờ 30 phút", 2, 30),
])
def test_additive_minutes_keep_the_hour_they_follow(text, hour, minute):
    s = start(text)
    assert (s.hour, s.minute) == (hour, minute)


@pytest.mark.parametrize("text,hour", [
    ("hai giờ", 2),
    ("mười giờ", 10),
    ("mười hai giờ", 12),
])
def test_bare_hour(text, hour):
    s = start(text)
    assert (s.hour, s.minute) == (hour, 0)


@pytest.mark.parametrize("text,hour", [
    ("bảy giờ sáng", 7),
    ("hai giờ chiều", 14),
    ("tám giờ tối", 20),
    ("mười hai giờ trưa", 12),
    ("một giờ đêm", 1),
])
def test_daypart_follows_the_clock_and_places_the_hour(text, hour):
    s = start(text)
    assert (s.hour, s.minute) == (hour, 0)


def test_midnight_landmark():
    s = start("nửa đêm")
    assert (s.hour, s.minute) == (0, 0)


@pytest.mark.parametrize("text", [
    "hai giờ rưỡi", "ba giờ kém mười lăm", "bốn giờ mười phút",
    "hai giờ chiều", "nửa đêm",
])
def test_clock_phrases_are_fully_consumed(text):
    assert remainder(text) == ""


@pytest.mark.parametrize("text", ["kém mười lăm", "giờ rưỡi", "kém"])
def test_a_bare_direction_word_names_no_time(text):
    r = parse(text)
    assert r is None or r[0].start.date() == parse("hôm nay")[0].start.date()


@pytest.mark.parametrize("text", ["hai giờ mười lăm", "chín giờ kém năm"])
def test_a_minute_count_needs_its_direction_word_or_its_noun(text):
    """No dedicated quarter lexeme was attested, so a quarter past is spoken
    compositionally and must carry phút; and a bare năm after kém is the
    year/five collision, not a minute count.  Both leave the minutes in the
    remainder rather than folding them into the wrong side of the hour."""
    r = parse(text)
    assert r is not None
    assert r[1] != ""
    assert r[0].start.minute == 0
