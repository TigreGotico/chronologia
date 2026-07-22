"""Character offsets (fr): every TimeMention carries a char_span into the
ORIGINAL utterance, from the tokenizer's own offsets (never a re-search)."""
from datetime import datetime
import pytest
from chronologia.extract.nseries import extract_timespans

ANCHOR = datetime(2017, 6, 27, 13, 4)
_SINGLE = ['Q3 2026', 'troisième trimestre 2026', 'premier trimestre 2020', 'quatrième trimestre 2019', 'semaine 32', 'semaine 1', 'semaine 26', 'début du mois', 'milieu du mois', 'fin du mois']

@pytest.mark.parametrize("utterance", _SINGLE)
def test_char_span_recovers_full_mention(utterance):
    ms = extract_timespans(utterance, "fr", anchor=ANCHOR)
    assert len(ms) == 1, [m.text for m in ms]
    cs, ce = ms[0].char_span
    assert utterance.lower()[cs:ce] == utterance.lower()

def test_char_span_embedded_offset():
    u = "réunion 2026-07-05"
    ms = extract_timespans(u, "fr", anchor=ANCHOR)
    assert len(ms) == 1
    cs, ce = ms[0].char_span
    assert u.lower()[cs:ce] == "2026-07-05"
    assert cs > 0

def test_no_mention_empty():
    assert extract_timespans("xxxxx yyyyy zzzzz", "fr", anchor=ANCHOR) == []
