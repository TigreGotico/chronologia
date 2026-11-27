"""Hindi rows the native reviewer confirmed.

Source: native answer, chronologia#1484 (comment 7209012484).

* कल is yesterday with a past verb ("कल की दावत कैसी थी") and tomorrow with
  an imperative or future verb ("कल की दावत में आना ज़रूर").  With no verb it
  "depends on context", so it stays refused.
* क्रिसमस ईव and न्यू ईयर ईव are the spoken names of the two eves.  The
  written पूर्व संध्या forms are not used, so they are not read.
* "सर्दियों की एक सुबह" is indefinite: one morning, no day named.
* "अगले रविवार को" is the coming Sunday; "अगले हफ़्ते के रविवार को" is the
  Sunday of next week.

The anchor is Friday 2026-11-27 10:00.  Every expected date is counted by hand
from it: the coming Sunday is 29 November, and the Sunday of the next
Monday-start week is 6 December.
"""
from datetime import datetime

import pytest

from ._corpus import parse

ANCHOR = datetime(2026, 11, 27, 10, 0)
YESTERDAY = datetime(2026, 11, 26)
TOMORROW = datetime(2026, 11, 28)


def start(text):
    r = parse(text, ANCHOR)
    assert r is not None, f"{text!r} did not parse"
    return r[0].start.datetime()


@pytest.mark.parametrize("text,expected", [
    ("कल की दावत कैसी थी", YESTERDAY),
    ("कल दावत थी", YESTERDAY),
    ("कल की दावत में आना ज़रूर", TOMORROW),
    ("कल आना", TOMORROW),
])
def test_kal_takes_its_direction_from_the_verb(text, expected):
    assert start(text) == expected


@pytest.mark.parametrize("text", ["कल की दावत", "कल आना था"])
def test_kal_without_one_tense_is_refused(text):
    assert parse(text, ANCHOR) is None


@pytest.mark.parametrize("text,expected", [
    ("क्रिसमस", datetime(2026, 12, 25)),
    ("क्रिसमस पर", datetime(2026, 12, 25)),
    ("क्रिसमस के दिन", datetime(2026, 12, 25)),
    ("क्रिसमस ईव", datetime(2026, 12, 24)),
    ("नया साल", datetime(2027, 1, 1)),
    ("नए साल पर", datetime(2027, 1, 1)),
    ("न्यू ईयर ईव", datetime(2026, 12, 31)),
])
def test_holiday(text, expected):
    assert start(text) == expected


@pytest.mark.parametrize("text", [
    "क्रिसमस की पूर्व संध्या", "नए साल की पूर्व संध्या",
])
def test_written_eve_form_is_refused(text):
    """The holiday name before की is an attribute, so the phrase must not
    read as the holiday itself (25 December or 1 January)."""
    assert parse(text, ANCHOR) is None


def test_holiday_name_before_a_genitive_is_no_date():
    assert parse("क्रिसमस के गीत सुनते ही मन भर जाता है", ANCHOR) is None


@pytest.mark.parametrize("text", [
    # कल-पुर्ज़े: "machine parts" (en.wiktionary.org, "कल", etymology 3).
    "जंग लगे कल-पुर्ज़े भी चल पड़ते थे",
    # कल पड़ना: "to find ease" (en.wiktionary.org, "कल", etymology 4).
    "माँ के दिल को ज़रा भी कल नहीं पड़ रही थी",
])
def test_kal_as_a_noun_is_no_date(text):
    assert parse(text, ANCHOR) is None


def test_afternoon_range():
    r = parse("आज दोपहर चार बजे से शाम सात बजे तक", ANCHOR)
    assert r[0].start.datetime() == datetime(2026, 11, 27, 16, 0)
    assert r[0].end.datetime().replace(minute=0) == datetime(2026, 11, 27, 19)


def test_one_winter_morning_is_indefinite():
    assert parse("सर्दियों की एक सुबह", ANCHOR) is None


@pytest.mark.parametrize("text,expected", [
    ("अगले रविवार को", datetime(2026, 11, 29)),
    ("अगले हफ़्ते के रविवार को", datetime(2026, 12, 6)),
])
def test_next_sunday(text, expected):
    assert start(text) == expected
