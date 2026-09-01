"""Ranges: *daga X zuwa Y*, *tsakanin X da Y*, and the past-anchored *tun*."""
import pytest

from ._corpus import ANCHOR, ad, day, month_span, nomatch, start_end, year_span


@pytest.mark.parametrize("text,lo,hi", [
    ("daga Litinin zuwa Jumaʼa", (2027, 5, 17), (2027, 5, 22)),
    ("daga Asabar zuwa Laraba", (2027, 5, 15), (2027, 5, 20)),
    ("daga 5 ga Yuni zuwa 9 ga Yuni", (2027, 6, 5), (2027, 6, 10)),
    ("daga 1 ga Janairu 2030 zuwa 5 ga Janairu 2030",
     (2030, 1, 1), (2030, 1, 6)),
])
def test_the_closed_range_runs_daga_to_zuwa(text, lo, hi):
    """A closed range covers both endpoints whole: it ends where the last
    day ends, which is the following midnight."""
    assert start_end(text) == (day(*lo)[0], day(*hi)[0])


def test_a_month_range():
    assert start_end("daga Janairu zuwa Maris") == (month_span(2027, 1)[0],
                                                    month_span(2027, 3)[1])


@pytest.mark.parametrize("text,lo,hi", [
    ("tsakanin Litinin da Jumaʼa", (2027, 5, 17), (2027, 5, 22)),
    ("tsakanin 5 ga Yuni da 9 ga Yuni", (2027, 6, 5), (2027, 6, 10)),
])
def test_the_between_frame_joins_its_bounds_with_da(text, lo, hi):
    assert start_end(text) == (day(*lo)[0], day(*hi)[0])


def test_a_year_range():
    """ha.wikipedia.org: "tsakanin shekarar 1945 da 1947"."""
    assert start_end("tsakanin shekarar 1945 da 1947") == (year_span(1945)[0],
                                                           year_span(1947)[1])


@pytest.mark.parametrize("text,lo", [
    ("tun jiya", (2027, 5, 11)),
    ("tun Litinin", (2027, 5, 10)),
])
def test_tun_opens_a_stretch_reaching_back_to_the_anchor(text, lo):
    assert start_end(text) == (day(*lo)[0], ad(ANCHOR))


def test_tun_daga_reaches_back_the_same_way():
    """ha.wikipedia.org writes tun before daga: "tun daga watan Fabrairun
    shekarar 2024"."""
    assert start_end("tun daga jiya") == start_end("tun jiya")


def test_tun_daga_reaches_back_from_a_calendar_date():
    """The attested sentence itself: a stretch from February 2024 up to the
    anchor instant."""
    assert start_end("tun daga watan Fabrairun shekarar 2024") == (
        month_span(2024, 2)[0], ad(ANCHOR))


@pytest.mark.parametrize("text", ["daga", "zuwa", "tsakanin", "tun", "da"])
def test_a_lone_range_marker_is_not_a_date(text):
    nomatch(text)
