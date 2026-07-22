# -*- coding: utf-8 -*-
"""Confusables corpus for el -- temporal-looking tokens that must NOT bind.

Each case is a natural sentence carrying a token that *looks* temporal but
is not meant that way (a month homograph used as a name or common word, a
unit or number word with no count, a weekday homograph, a season word in a
metaphor, an era initial, a scale word). The desired outcome is one of two:

  * ``extract_timespan`` returns ``None`` -- nothing temporal to bind; or
  * it binds a genuinely temporal part of the sentence and the confusable
    token lands in the remainder (the span-elsewhere cases).

Structurally-safe classes (unit-without-a-number, number words, era
initials, scale words) are asserted as hard ``None``. The residue -- bare
month/weekday content-word homographs, morning/tomorrow, figurative season
and unit uses, idioms -- are *documented limitations*: the parser binds the
token, disambiguation is a downstream (NLU/consumer) concern. They are
marked ``xfail`` (non-strict) so the file records the honest behaviour and
flips to green the day a guard or a downstream policy resolves them. See the
"Known limitations" section of docs/extraction.md.
"""
import pytest

from ._corpus import parse, nomatch  # noqa: F401


_SAFE_NONE = [
    'ένα δευτερόλεπτο υπομονή',
    'περίμενε ένα δευτερόλεπτο',
    'στον δεύτερο όροφο',
    'μικρή λεπτομέρεια',
    'στο μπάνιο',
    'μια φορά στη ζωή',
    'μισό τόσο άσχημα',
    'η μισή αλήθεια',
    'μισό κιλό ψωμί',
    'το ένα τέταρτο του πληθυσμού',
    'ένα εκατομμύριο λόγοι',
    'χιλιάδες άνθρωποι',
    'ανατέλλων ήλιος',
    'νωρίς το πρωί',
    'δευτερόλεπτο σιωπής',
    'οι περισσότεροι άνθρωποι',
    'μερικές μέρες',
    'μια χούφτα άνθρωποι',
    'στον πρώτο όροφο',
    'ώρα για φαγητό',
    'στροφή κατά το ήμισυ',
    'το μισό της ομάδας',
    'μικρή ποσότητα',
]


@pytest.mark.parametrize("text", _SAFE_NONE)
def test_confusable_returns_none(text):
    # structurally safe: no count/modifier, nothing to bind.
    nomatch(text)


def test_last_month_is_a_real_reference():
    # "τον περασμένο μήνα" is not a confusable: it is last month, the whole
    # calendar month preceding the anchor's, resolved by rel_period
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    from ._corpus import ANCHOR, span
    s = ANCHOR.replace(day=1, hour=0, minute=0, second=0, microsecond=0) \
        - relativedelta(months=1)
    e = s + relativedelta(months=1)
    sp = span('τον περασμένο μήνα')
    assert (sp.start.year, sp.start.month, sp.start.day) == (s.year, s.month, s.day)
    assert (sp.end.year, sp.end.month, sp.end.day) == (e.year, e.month, e.day)


_RESOLVED = [
    'μια χαμένη δεκαετία',
]

_LIMITATIONS = [
    pytest.param(
        'ο απρίλιος ως όνομα',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=True)),
    pytest.param(
        'ο αύγουστος ως όνομα',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=True)),
    pytest.param(
        'η άνοιξη των λαών',
        marks=pytest.mark.xfail(reason='season word in figurative use binds as the season; downstream concern', strict=True)),
    pytest.param(
        'το φθινόπωρο της ζωής',
        marks=pytest.mark.xfail(reason='season word in figurative use binds as the season; downstream concern', strict=True)),
    pytest.param(
        'τα χριστούγεννα ήρθαν νωρίς',
        marks=pytest.mark.xfail(reason='temporal token inside a fixed idiom binds literally; downstream concern', strict=True)),
]


@pytest.mark.parametrize("text", _LIMITATIONS)
def test_documented_limitation(text):
    # desired outcome is None; the parser binds the confusable token.
    nomatch(text)


_SPAN_ELSEWHERE = [
    ('μικρή λεπτομέρεια σε 3 ημέρες', 'λεπτομέρεια'),
    ('ένα εκατομμύριο λόγοι σε 2 εβδομάδες', 'εκατομμύριο'),
]


@pytest.mark.parametrize("text,confusable", _SPAN_ELSEWHERE)
def test_span_elsewhere(text, confusable):
    r = parse(text)
    assert r is not None, f"{text!r} should bind its genuine temporal part"
    assert confusable in r[1], (
        f"confusable {confusable!r} should stay in remainder {r[1]!r}")



@pytest.mark.parametrize("text", _RESOLVED)
def test_confusable_now_none(text):
    # formerly a documented limitation; the parser now correctly
    # binds nothing here.  A strict tripwire would misfire, so this is
    # a live positive assertion of the now-correct behaviour.
    nomatch(text)