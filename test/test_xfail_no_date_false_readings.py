"""Strict xfails: sentences that name no date but read as one.

The rows come from the business-day bench, class business_word_no_date.
Each row asserts the issue's expected value, no reading. A fix that lands
turns the run red, so the fix removes the mark from its rows.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2023, 6, 27, 9, 0)
URL = "https://github.com/TigreGotico/chronologia/issues/"


def xfail(issue):
    return pytest.mark.xfail(raises=AssertionError, strict=True, reason=URL + str(issue))


@xfail(1455)
@pytest.mark.parametrize("text", [
    "um dia útil passado a resolver papéis",
    "Para muitos enfermeiros, um dia útil parece nunca ter fim quando as urgências estão cheias.",
])
def test_pt_article_before_business_day_is_no_count(text):
    assert extract_timespan(text, "pt-PT", ANCHOR) is None


@pytest.mark.parametrize("text,lang", [
    ("Pentru o asistentă medicală, ziua de lucru pare uneori să nu se mai termine.", "ro"),
] + [pytest.param(*row, marks=xfail(1456)) for row in [
    ("ficou em casa quando o mar não deixou", "pt-PT"),
    ("Pentru mulți părinți, ziua de lucru pare să nu se termine niciodată, mai ales când copiii au nevoie de ajutor la teme seara.", "ro"),
    ("O zi lucrătoare petrecută în fața calculatorului te poate lăsa mai obosit decât ai crede.", "ro"),
    ("Pentru o asistentă medicală, ziua de lucru pare uneori fără sfârșit, mai ales când secția e plină.", "ro"),
    ("Pracovní den v nemocnici bývá pro sestry vyčerpávající, ale zároveň plný drobných radostí.", "cs"),
]])
def test_common_word_is_no_month(text, lang):
    assert extract_timespan(text, lang, ANCHOR) is None


@pytest.mark.parametrize("text,lang,month", [
    ("1 mai", "ro", 5),
    ("5. pro", "cs", 12),
    ("em março", "pt-PT", 3),
])
def test_control_a_month_with_a_cue_reads(text, lang, month):
    assert extract_timespan(text, lang, ANCHOR).span.start.month == month
