"""Esperanto calendar dates: "la unua de januaro" (the first of January).

The day is the regular ordinal (cardinal + "-a"), "de" links it to the
invariant month noun, and "la" is the Esperanto definite article -- every
element attested in en.wikipedia.org "Esperanto grammar" (ordinals) and
esperanto.lingolia.com (worked date examples share the same "la ORD de
MONTH" shape as the clock's "la HOUR").

With no year stated the date resolves FORWARD from the anchor
(2017-06-27), matching every other locale's ``prefer_future`` convention.
"""
import pytest

from ._corpus import remainder, start


@pytest.mark.parametrize("text,y,m,d", [
    ("la unua de januaro", 2018, 1, 1),
    ("la kvina de julio", 2017, 7, 5),
    ("la kvina de decembro", 2017, 12, 5),
    ("la dudek kvina de decembro", 2017, 12, 25),
])
def test_month_day_without_year(text, y, m, d):
    got = start(text)
    assert (got.year, got.month, got.day) == (y, m, d)


@pytest.mark.parametrize("text", [
    "la unua de januaro", "la kvina de julio",
])
def test_full_date_consumes_everything(text):
    assert remainder(text) == ""


@pytest.mark.parametrize("text,y", [("1990", 1990), ("2019", 2019)])
def test_bare_year_reference(text, y):
    got = start(text)
    assert (got.year, got.month, got.day) == (y, 1, 1)


@pytest.mark.parametrize("text", [
    "de januaro",           # a bare "of MONTH" with no day at all
    "asdf qwerty", "",
])
def test_no_date_without_a_day_and_month(text):
    from ._corpus import nomatch
    nomatch(text)


@pytest.mark.parametrize("text,y,m,d", [
    # the DIGIT ordinal day ("15-a" = 15th): the tokenizer shears the
    # hyphen into a bare digit plus a dangling "a"/"an" fragment, which
    # numfold_esperanto glues back onto the digit (see
    # ``_digit_ordinal_rewrite``) so it binds the same DAY slot the
    # spelled ordinal does -- both with and without the leading article,
    # and with the accusative "-an" a fully-specified date takes.
    ("la 15-a de marto", 2018, 3, 15), ("la 3-a de januaro", 2018, 1, 3),
    ("la 1-a de aprilo", 2018, 4, 1), ("15-a de marto", 2018, 3, 15),
    ("la 15-an de marto", 2018, 3, 15), ("la 25-a de decembro", 2017, 12, 25),
])
def test_digit_ordinal_day_of_month(text, y, m, d):
    got = start(text)
    assert (got.year, got.month, got.day) == (y, m, d)
    # the fully-qualified reading is a whole DAY, never a clock time: a
    # digit ordinal misread as an hour is the exact silent-wrong this
    # table exists to prevent (see test_digit_ordinal_is_never_an_hour).
    assert (got.hour, got.minute) == (0, 0)


@pytest.mark.parametrize("text", [
    "la 15-a de marto", "la 3-a de januaro", "la 1-a de aprilo",
])
def test_digit_ordinal_day_consumes_everything(text):
    """The old defect left "a de MONTH" stranded in the remainder while the
    clock construction silently claimed the bare digit as an hour; the
    fixed reading consumes the whole phrase."""
    assert remainder(text) == ""


@pytest.mark.parametrize("text,wrong_hour,wrong_minute", [
    ("la 15-a de marto", 15, 0), ("la 3-a de januaro", 3, 0),
    ("la 1-a de aprilo", 1, 0),
])
def test_digit_ordinal_is_never_an_hour(text, wrong_hour, wrong_minute):
    """Adversarial pin, against the original defect: "la 15-a de marto"
    must never resolve as TODAY at 15:00 (the digit misread as an hour,
    with the anchor's own date silently substituted for March)."""
    from ._corpus import ANCHOR
    got = start(text)
    assert (got.date(), got.hour, got.minute) != \
        (ANCHOR.date(), wrong_hour, wrong_minute)
