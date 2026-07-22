# -*- coding: utf-8 -*-
"""Confusables corpus for he -- temporal-looking tokens that must NOT bind.

Each case is a natural sentence carrying a token that *looks* temporal but is
not meant that way (a season word inside a place name or metaphor, a unit or
number word with no count, a scale word, a bare weekday). The desired outcome
is one of two:

  * ``extract_timespan`` returns ``None`` -- nothing temporal to bind; or
  * it binds a genuinely temporal part of the sentence and the confusable
    token lands in the remainder (the span-elsewhere cases).

Structurally-safe classes (unit/number/scale word with no count, bare
weekday -- which needs a relative marker to form a construction) are asserted
as hard ``None``. The residue -- a season word inside a proper name
(תל אביב "Tel Aviv" carries אביב "spring") or a figurative season use -- are
*documented limitations*: the parser binds the token, disambiguation is a
downstream concern. They are marked ``xfail`` (non-strict). A cheap
adjacent-token guard for one proper noun would not generalise, so the
policy-consistent record is the limitation, matching the season-name/metaphor
xfails in the other locales. See the "Known limitations" section of
docs/extraction.md.
"""
import pytest

from ._corpus import parse, nomatch  # noqa: F401


_SAFE_NONE = [
    'שלושה ספרים על השולחן',      # "three books" -- number, no unit
    'חמישה אנשים',               # "five people" -- number, no unit
    'רגע אחד',                   # "one moment"
    'שנייה אחת',                 # "one second" -- no temporal count construction
    'דקה בבקשה',                 # "a minute please" -- unit, no count
    'חצי מהכמות',                # "half the amount"
    'מיליון סיבות',              # "a million reasons" -- scale word, no year
    'אלפי אנשים',                # "thousands of people" -- scale word
    'לפני הכל',                  # "before everything" -- lone past marker
    'אחרי הכל',                  # "after all"
    'ראשון בין שווים',            # "first among equals" -- ordinal, bare weekday
    'שלישי ברשימה',              # "third on the list"
]


@pytest.mark.parametrize("text", _SAFE_NONE)
def test_confusable_returns_none(text):
    # structurally safe: no count/modifier, nothing to bind.
    nomatch(text)


_LIMITATIONS = [
    pytest.param(
        'תל אביב עיר גדולה',
        marks=pytest.mark.xfail(reason='place name תל אביב carries the season word אביב ("spring") and binds as the season; a one-name adjacent guard would not generalise, disambiguation is downstream', strict=True)),
    pytest.param(
        'הקיץ החם',
        marks=pytest.mark.xfail(reason='season word in a descriptive phrase binds as the season; downstream concern', strict=True)),
    pytest.param(
        'אביב חדש',
        marks=pytest.mark.xfail(reason='season word אביב used as a name/metaphor binds as spring; downstream concern', strict=True)),
    pytest.param(
        'שבת שלום',
        marks=pytest.mark.xfail(reason='full weekday שבת ("Saturday") binds as the next Saturday inside the greeting "Shabbat shalom"; the bare-weekday order resolves the day, disambiguation is downstream', strict=True)),
]


@pytest.mark.parametrize("text", _LIMITATIONS)
def test_documented_limitation(text):
    # desired outcome is None; the parser binds the confusable token.
    nomatch(text)


_SPAN_ELSEWHERE = [
    ('אלפי אנשים בעוד 3 ימים', 'אלפי'),
    ('שלושה ספרים לפני 5 שנים', 'ספרים'),
]


@pytest.mark.parametrize("text,confusable", _SPAN_ELSEWHERE)
def test_span_elsewhere(text, confusable):
    r = parse(text)
    assert r is not None, f"{text!r} should bind its genuine temporal part"
    assert confusable in r[1], (
        f"confusable {confusable!r} should stay in remainder {r[1]!r}")
