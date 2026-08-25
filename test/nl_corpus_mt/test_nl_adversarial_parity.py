"""Adversarial Maltese cases plus the shared English semantic-parity block."""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, nomatch, parse


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


@pytest.mark.parametrize("text", ["ġranet ilu", "snin ilu", "xhur ilu"])
def test_a_plural_unit_without_a_count_is_not_an_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


def test_a_lone_article_is_not_a_date():
    for text in ("il", "is", "iż", "l"):
        nomatch(text)


def test_a_lone_linker_is_not_a_count():
    nomatch("il jum")


PAIRS = [
    ("illum", "today"), ("għada", "tomorrow"), ("lbieraħ", "yesterday"),
    ("pitgħada", "overmorrow"),
    ("jumejn ilu", "2 days ago"), ("tliet ġranet ilu", "3 days ago"),
    ("ġimagħtejn ilu", "2 weeks ago"), ("xahrejn ilu", "2 months ago"),
    ("sentejn ilu", "2 years ago"), ("sagħtejn ilu", "2 hours ago"),
    ("għaxar minuti ilu", "10 minutes ago"),
    ("ħdax-il sena ilu", "11 years ago"),
    ("ħames snin ilu", "5 years ago"),
    ("ħmistax-il minuta ilu", "15 minutes ago"),
    ("seklu ilu", "a century ago"),
    ("fi żmien jumejn oħra", "in 2 days"),
    ("fi żmien tliet snin oħra", "in 3 years"),
    ("fi żmien ħames ġimgħat oħra", "in 5 weeks"),
    ("il-Ħadd li ġej", "next sunday"),
    ("it-Tnejn li għadda", "last monday"),
    ("is-sena d-dieħla", "next year"), ("din is-sena", "this year"),
    ("dan ix-xahar", "this month"), ("ix-xahar li għadda", "last month"),
    ("din il-ġimgħa", "this week"),
    ("15:30", "15:30"), ("00:00", "00:00"), ("09:30", "09:30"),
    ("2019", "2019"), ("1918", "1918"),
    ("15 ta' Awwissu 2027", "15 august 2027"),
    ("25 ta' Diċembru 2020", "25 december 2020"),
    ("1 ta' Jannar 2030", "1 january 2030"),
    ("nofsinhar", "noon"), ("nofsillejl", "midnight"),
    ("is-sitta u nofs", "06:30"), ("it-tmienja nieqes kwart", "07:45"),
    ("fis-sebgħa filgħodu", "07:00"),
]


@pytest.mark.parametrize("mt_text,en_text", PAIRS)
def test_span_parity(mt_text, en_text):
    mt = extract_timespan(mt_text, "mt", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert mt is not None, f"mt {mt_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert mt[0].start == en[0].start and mt[0].end == en[0].end, (mt_text, en_text)
