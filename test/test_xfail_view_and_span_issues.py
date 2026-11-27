"""Known defects in how the readings of one text agree with each other.

Four groups, each a strict xfail that names its issue: the candidate list and
extract_timespan reading one text differently, a shared-month range that drops
the unrelated words before and after it from the remainder, a range read across
a full stop, and decomposed (NFD) input reading differently from the composed
(NFC) form.  Every expected value is worked out by hand from the anchor.
"""
import unicodedata
from datetime import datetime

import pytest

from chronologia import extract_candidates, extract_timespan

MORNING = datetime(2017, 6, 27, 6, 4)  # Tuesday
NOON = datetime(2017, 6, 27, 13, 4)    # Tuesday

VIEW = "https://github.com/TigreGotico/chronologia/issues/1350"
REMAINDER = "https://github.com/TigreGotico/chronologia/issues/1351"
SENTENCE = "https://github.com/TigreGotico/chronologia/issues/1352"
NFD = "https://github.com/TigreGotico/chronologia/issues/1353"


def _ends(span):
    return span.start, span.end


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=VIEW)
@pytest.mark.parametrize("lang,text,start,end", [
    ("de", "um 9 Uhr für 2 Stunden", datetime(2017, 6, 27, 9, 0), datetime(2017, 6, 27, 11, 0)),
    ("de", "Besprechung um 15:15 für 45 Minuten", datetime(2017, 6, 27, 15, 15), datetime(2017, 6, 27, 16, 0)),
    ("en", "at 9 am for 2 hours", datetime(2017, 6, 27, 9, 0), datetime(2017, 6, 27, 11, 0)),
    ("en", "meeting at 3 pm for 45 minutes", datetime(2017, 6, 27, 15, 0), datetime(2017, 6, 27, 15, 45)),
    ("fr", "à 9h pendant 2 heures", datetime(2017, 6, 27, 9, 0), datetime(2017, 6, 27, 11, 0)),
])
def test_first_candidate_is_the_clock_for_a_length(lang, text, start, end):
    assert _ends(extract_candidates(text, lang, MORNING)[0].span) == (start, end)


@pytest.mark.parametrize("lang,text,start,end", [
    ("de", "um 9 Uhr für 2 Stunden", datetime(2017, 6, 27, 9, 0), datetime(2017, 6, 27, 11, 0)),
    ("fr", "à 9h pendant 2 heures", datetime(2017, 6, 27, 9, 0), datetime(2017, 6, 27, 11, 0)),
])
def test_timespan_reads_the_clock_for_a_length(lang, text, start, end):
    assert _ends(extract_timespan(text, lang, MORNING)[0]) == (start, end)


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=REMAINDER)
@pytest.mark.parametrize("lang,text,remainder", [
    ("en", "please 5-12 June", "please"),
    ("en", "meet me 5-12 June ok", "meet me ok"),
    ("en", "June 5 to 12 yy", "yy"),
    ("de", "xx 3. bis 10. Juli", "xx"),
    ("fr", "xx du 10h au 12h", "xx"),
])
def test_shared_range_keeps_unrelated_words_in_the_remainder(lang, text, remainder):
    assert extract_timespan(text, lang, NOON)[1] == remainder
    assert extract_candidates(text, lang, NOON)[0].remainder == remainder


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=SENTENCE)
@pytest.mark.parametrize("lang,text,start,end", [
    ("de", "Wir treffen uns am Montag. Der Bericht ist bis Freitag fällig.",
     datetime(2017, 7, 3), datetime(2017, 7, 4)),
    ("ru", "Мы встретимся в понедельник. Отчёт должен быть готов до пятницы.",
     datetime(2017, 7, 3), datetime(2017, 7, 4)),
])
def test_range_does_not_cross_a_full_stop(lang, text, start, end):
    assert _ends(extract_timespan(text, lang, NOON)[0]) == (start, end)
    assert _ends(extract_candidates(text, lang, NOON)[0].span) == (start, end)


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=SENTENCE)
def test_range_does_not_swallow_the_next_clause():
    text = ("From june 5th to june 12th we will travel, "
            "then rest next monday morning at 9 for 1 hour.")
    want = (datetime(2018, 6, 5), datetime(2018, 6, 13))
    assert _ends(extract_timespan(text, "en", MORNING)[0]) == want
    assert _ends(extract_candidates(text, "en", MORNING)[0].span) == want


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=NFD)
@pytest.mark.parametrize("lang,text", [
    ("fr", "dans 2 jours ouvrés"),
    ("ru", "3 рабочих дней"),
    ("tr", "akşam saat sekiz"),
])
def test_nfd_remainder_equals_nfc(lang, text):
    nfd = unicodedata.normalize("NFD", text)
    assert nfd != text
    assert extract_timespan(nfd, lang, MORNING)[1] == ""


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=NFD)
@pytest.mark.parametrize("lang,text,start,end", [
    ("pt", "dia 5 de março de 2027", datetime(2027, 3, 5), datetime(2027, 3, 6)),
    ("fr", "le 5 février 2027", datetime(2027, 2, 5), datetime(2027, 2, 6)),
    ("de", "am 5. März 2027 um 15 Uhr", datetime(2027, 3, 5, 15), datetime(2027, 3, 5, 15, 1)),
    ("fr", "cinq heures de l'après-midi", datetime(2017, 6, 27, 17), datetime(2017, 6, 27, 17, 1)),
])
def test_nfd_reads_the_same_span_as_nfc(lang, text, start, end):
    nfd = unicodedata.normalize("NFD", text)
    assert nfd != text
    got = extract_timespan(nfd, lang, MORNING)
    assert (got and _ends(got[0])) == (start, end)
