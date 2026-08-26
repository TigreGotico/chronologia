"""Adversarial Korean cases plus the shared English semantic-parity block."""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, nomatch, parse


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


@pytest.mark.parametrize("text", ["일", "시간", "주", "분", "개월"])
def test_a_bare_unit_without_a_count_is_not_an_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["전", "후", "에", "부터", "까지"])
def test_a_lone_particle_is_not_a_date(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["지난", "이번", "다음"])
def test_a_lone_determiner_is_not_a_date(text):
    nomatch(text)


def test_the_minute_ago_pattern_and_the_minutes_to_the_hour_pattern_differ():
    """CLDR spells "N minutes ago" as {0}분 전, which is also the tail of
    the minutes-to-the-hour clock.  What separates them is the named hour in
    front: 십 분 전 is ten minutes ago, 세 시 십 분 전 is ten to three."""
    ago = extract_timespan("십 분 전", "ko", ANCHOR)
    clock = extract_timespan("세 시 십 분 전", "ko", ANCHOR)
    assert ago is not None and clock is not None
    assert ago[0].start.hour == 12 and ago[0].start.minute == 54
    assert clock[0].start.hour == 2 and clock[0].start.minute == 50


PAIRS = [
    ("오늘", "today"), ("내일", "tomorrow"), ("어제", "yesterday"),
    ("그저께", "the day before yesterday"), ("모레", "overmorrow"),
    ("3일 전", "3 days ago"),
    ("5일 전", "5 days ago"),
    ("3시간 전", "3 hours ago"),
    ("10분 전", "10 minutes ago"),
    ("30초 전", "30 seconds ago"),
    ("2주 전", "2 weeks ago"),
    ("3개월 전", "3 months ago"),
    ("2년 전", "2 years ago"),
    ("11년 전", "11 years ago"),
    ("15분 전", "15 minutes ago"),
    ("100년 전", "100 years ago"),
    ("2일 후", "in 2 days"),
    ("3시간 후", "in 3 hours"),
    ("45분 후", "in 45 minutes"),
    ("4년 후", "in 4 years"),
    ("2주 후", "in 2 weeks"),
    ("작년", "last year"), ("내년", "next year"), ("올해", "this year"),
    ("지난달", "last month"), ("다음 달", "next month"),
    ("이번 달", "this month"),
    ("다음 월요일", "next monday"),
    ("지난 금요일", "last friday"),
    ("다음 수요일", "next wednesday"),
    ("09:30", "09:30"), ("00:00", "00:00"), ("21:50", "21:50"),
    ("14:05", "14:05"),
    ("오후 3시 30분", "3:30 pm"),
    ("세 시 십 분", "3:10 am"),
    ("두 시 반", "2:30 am"),
    ("2027년 6월 5일", "5 june 2027"),
    ("2020년 12월 25일", "25 december 2020"),
    ("2030년 1월 1일", "1 january 2030"),
    ("2027년 8월 15일", "15 august 2027"),
    ("2027년 7월", "july 2027"),
    ("2027", "2027"), ("1918", "1918"),
]


@pytest.mark.parametrize("ko_text,en_text", PAIRS)
def test_span_parity(ko_text, en_text):
    ko = extract_timespan(ko_text, "ko", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert ko is not None, f"ko {ko_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert ko[0].start == en[0].start and ko[0].end == en[0].end, (ko_text,
                                                                   en_text)
