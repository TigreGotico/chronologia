"""Greek adversarial cases: things that look temporal but are not, case-form
near-misses, and bare fragments.  Every case asserts a clean non-match (or a
deliberately correct match) so the parser stays conservative.
"""
import pytest

from ._corpus import nomatch, span, start
from datetime import datetime
from ._corpus import ad, AstroDate, parse


# -- pure non-temporal text: must not parse -------------------------------

@pytest.mark.parametrize("text", [
    "η γάτα κοιμάται",
    "καλημέρα σας",
    "ένα ωραίο βιβλίο",
    "πάμε σινεμά",
    "το τραπέζι είναι ξύλινο",
    "σκουπίδια",
    "εντάξει",
    "ευχαριστώ πολύ",
    "πράσινο άλογο",
])
def test_non_temporal_nomatch(text):
    nomatch(text)


# -- bare numbers / units with no anchor: must not parse ------------------

@pytest.mark.parametrize("text", [
    "είκοσι τρεις",
    "μερικά",
    "ώρα",
    "λεπτό",
    "χρόνια",
    "πριν",
    "σε",
    "παρά",
])
def test_bare_fragment_nomatch(text):
    nomatch(text)


# -- a month name alone still resolves to that month (not a nomatch) ------

@pytest.mark.parametrize("text,mo", [
    ("ιανουάριος", 1),
    ("ιούνιος", 6),
    ("δεκέμβριος", 12),
])
def test_bare_month_resolves(text, mo):
    assert span(text).start.month == mo


# -- direction words must not flip each other -----------------------------

def test_ago_needs_a_count_or_unit():
    # "πριν" with nothing to offset must not parse to a bogus span
    nomatch("πριν καλά")


def test_future_marker_alone_nomatch():
    nomatch("σε καλή")


def test_wrong_month_case_still_reads_as_nominative():
    # nominative month + digit day is a valid Greek surface too
    assert start("5 ιούνιος 2020") == ad(datetime(2020, 6, 5))


def test_daypart_inside_sentence_binds_the_band():
    # "τρώω μήλα κάθε πρωί" ("I eat apples every morning") carries a genuine
    # πρωί daypart mention and binds the CLDR el morning band
    # [04:00, 12:00). Recurrence ("κάθε" -- "every") is unimplemented in el,
    # so κάθε strands in the remainder along with the rest of the sentence.
    r = parse("τρώω μήλα κάθε πρωί")
    assert r is not None
    sp, remainder = r
    assert sp.start == AstroDate(2017, 6, 27, 4, 0)
    assert sp.end == AstroDate(2017, 6, 27, 12, 0)
    assert remainder == "τρώω μήλα κάθε"
