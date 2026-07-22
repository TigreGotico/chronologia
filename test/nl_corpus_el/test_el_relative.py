"""Greek relative offsets in BOTH directions ("πριν N" past / "σε N" future),
named days (σήμερα/αύριο/χθες/μεθαύριο/προχθές) and weekday references
(επόμενη/προηγούμενη + weekday).  Oracles are independent date arithmetic,
never the engine's own output.
"""
import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, start_end, nomatch

UNIT = {
    "μέρα": relativedelta(days=1), "μέρες": relativedelta(days=1),
    "ημέρες": relativedelta(days=1),
    "εβδομάδα": relativedelta(weeks=1), "εβδομάδες": relativedelta(weeks=1),
    "μήνα": relativedelta(months=1), "μήνες": relativedelta(months=1),
    "χρόνο": relativedelta(years=1), "χρόνια": relativedelta(years=1),
    "ώρα": relativedelta(hours=1), "ώρες": relativedelta(hours=1),
    "λεπτό": relativedelta(minutes=1), "λεπτά": relativedelta(minutes=1),
}


def past(n, unit):
    d = UNIT[unit]
    return ad(ANCHOR - n * d), ad(ANCHOR - (n - 1) * d)


def future(n, unit):
    d = UNIT[unit]
    return ad(ANCHOR + n * d), ad(ANCHOR + (n + 1) * d)


# -- past: "πριν N UNIT" --------------------------------------------------

@pytest.mark.parametrize("text,n,unit", [
    ("πριν 3 μέρες", 3, "μέρες"),
    ("πριν τρεις μέρες", 3, "μέρες"),
    ("πριν μία μέρα", 1, "μέρα"),
    ("πριν 2 εβδομάδες", 2, "εβδομάδες"),
    ("πριν δύο εβδομάδες", 2, "εβδομάδες"),
    ("πριν 5 μήνες", 5, "μήνες"),
    ("πριν πέντε μήνες", 5, "μήνες"),
    ("πριν 10 χρόνια", 10, "χρόνια"),
    ("πριν δέκα χρόνια", 10, "χρόνια"),
    ("πριν 7 μέρες", 7, "μέρες"),
    ("πριν 30 λεπτά", 30, "λεπτά"),
    ("πριν είκοσι πέντε λεπτά", 25, "λεπτά"),
    ("πριν 3 ώρες", 3, "ώρες"),
    ("πριν μία ώρα", 1, "ώρα"),
])
def test_past_prefix(text, n, unit):
    assert start_end(text) == past(n, unit)


# -- past: "N UNIT πριν" (postposed marker) -------------------------------

@pytest.mark.parametrize("text,n,unit", [
    ("3 μέρες πριν", 3, "μέρες"),
    ("δύο εβδομάδες πριν", 2, "εβδομάδες"),
    ("δέκα χρόνια πριν", 10, "χρόνια"),
    ("6 μήνες πριν", 6, "μήνες"),
])
def test_past_postfix(text, n, unit):
    assert start_end(text) == past(n, unit)


# -- future: "σε N UNIT" --------------------------------------------------

@pytest.mark.parametrize("text,n,unit", [
    ("σε 3 μέρες", 3, "μέρες"),
    ("σε τρεις μέρες", 3, "μέρες"),
    ("σε 2 εβδομάδες", 2, "εβδομάδες"),
    ("σε δύο εβδομάδες", 2, "εβδομάδες"),
    ("σε 1 μήνα", 1, "μήνα"),
    ("σε 10 χρόνια", 10, "χρόνια"),
    ("σε δέκα χρόνια", 10, "χρόνια"),
    ("σε 5 μέρες", 5, "μέρες"),
    ("σε μία ώρα", 1, "ώρα"),
    ("σε 45 λεπτά", 45, "λεπτά"),
    ("σε 3 ώρες", 3, "ώρες"),
    ("σε μία εβδομάδα", 1, "εβδομάδα"),
])
def test_future(text, n, unit):
    assert start_end(text) == future(n, unit)


# -- named days -----------------------------------------------------------

@pytest.mark.parametrize("text,offset", [
    ("σήμερα", 0), ("αύριο", 1), ("χθες", -1), ("χτες", -1),
    ("μεθαύριο", 2), ("προχθές", -2), ("προχτές", -2),
])
def test_named_days(text, offset):
    from datetime import timedelta
    base = (ANCHOR + timedelta(days=offset)).replace(hour=0, minute=0)
    assert start(text) == ad(base)


# -- weekday references ---------------------------------------------------
# anchor 2017-06-27 is a Tuesday.

@pytest.mark.parametrize("text,y,mo,d", [
    ("επόμενη τρίτη", 2017, 7, 4),
    ("επόμενη δευτέρα", 2017, 7, 3),
    ("επόμενη παρασκευή", 2017, 6, 30),
    ("προηγούμενη παρασκευή", 2017, 6, 23),
    ("προηγούμενη δευτέρα", 2017, 6, 26),
    ("περασμένη κυριακή", 2017, 6, 25),
])
def test_weekday_ref(text, y, mo, d):
    from datetime import datetime
    assert start(text) == ad(datetime(y, mo, d))


def test_bare_number_no_unit_nomatch():
    nomatch("είκοσι τρεις")


def test_gibberish_nomatch():
    nomatch("τρώω μήλα κάθε πρωί")
