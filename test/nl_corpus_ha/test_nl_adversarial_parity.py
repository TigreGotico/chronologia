"""Adversarial Hausa cases plus the shared English semantic-parity block."""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, nomatch, parse


@pytest.mark.parametrize("text", ["kwana", "shekara", "mako", "minti"])
def test_a_bare_singular_unit_without_a_count_is_not_an_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["ga", "na", "ta", "da", "wannan", "kowace"])
def test_a_lone_particle_is_not_a_date(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["gabata", "wuce", "zuwa", "gaba"])
def test_half_a_marker_is_not_a_date(text):
    """The past marker is a whole relative clause; its verb alone is not it."""
    nomatch(text)


def test_the_month_noun_does_not_claim_a_month():
    """wata is both "month" and "moon", and it names no particular month."""
    nomatch("wata")


PAIRS = [
    ("yau", "today"),
    ("gobe", "tomorrow"),
    ("jiya", "yesterday"),
    ("shekaranjiya", "the day before yesterday"),
    ("kwanaki biyu da suka gabata", "2 days ago"),
    ("kwanaki biyar da suka gabata", "5 days ago"),
    ("awanni uku da suka gabata", "3 hours ago"),
    ("mintuna goma da suka gabata", "10 minutes ago"),
    ("dakiku talatin da suka gabata", "30 seconds ago"),
    ("makonni biyu da suka gabata", "2 weeks ago"),
    ("watanni uku da suka gabata", "3 months ago"),
    ("shekaru biyu da suka gabata", "2 years ago"),
    ("shekaru goma sha ɗaya da suka gabata", "11 years ago"),
    ("mintuna sha biyar da suka gabata", "15 minutes ago"),
    ("shekaru ɗari da suka gabata", "100 years ago"),
    ("cikin kwanaki biyu", "in 2 days"),
    ("cikin awanni uku", "in 3 hours"),
    ("cikin mintuna arba'in da biyar", "in 45 minutes"),
    ("a cikin shekaru huɗu", "in 4 years"),
    ("cikin makonni biyu", "in 2 weeks"),
    ("shekarar da ta gabata", "last year"),
    ("shekara mai zuwa", "next year"),
    ("wannan shekarar", "this year"),
    ("watan da ya gabata", "last month"),
    ("wata na gaba", "next month"),
    ("wannan watan", "this month"),
    ("satin da ya gabata", "last week"),
    ("sati na gaba", "next week"),
    ("wannan satin", "this week"),
    ("Jumaʼa da ta gabata", "last friday"),
    ("Laraba da ta gabata", "last wednesday"),
    ("ƙarfe 09:30", "09:30"),
    ("00:00", "00:00"),
    ("ƙarfe 21:50", "21:50"),
    ("14:05", "14:05"),
    ("ƙarfe 7:45 na dare", "7:45 pm"),
    ("ƙarfe 9 na safe", "9 am"),
    ("2027", "2027"),
    ("1918", "1918"),
    ("5 ga Yuni 2027", "5 june 2027"),
    ("25 ga Disamba 2020", "25 december 2020"),
    ("1 ga Janairu 2030", "1 january 2030"),
    ("15 ga Agusta 2027", "15 august 2027"),
    ("Yuli 2027", "july 2027"),
    ("daga Litinin zuwa Jumaʼa", "from monday to friday"),
]


@pytest.mark.parametrize("ha_text,en_text", PAIRS)
def test_span_parity(ha_text, en_text):
    ha = extract_timespan(ha_text, "ha", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert ha is not None, f"ha {ha_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert ha[0].start == en[0].start and ha[0].end == en[0].end, (ha_text,
                                                                   en_text)
