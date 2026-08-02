"""Regression: a plural COUNT ("the two days of March") must not be fabricated
into an ordinal date across 13 more locales.

Each locale derived its ``plural_units`` from an ``-s`` suffix heuristic that
fails for non-Latin / irregular / case-inflected plurals, so the derived set was
empty/incomplete and the scoped-ordinal veto was starved -- inventing March 2
with an empty remainder.  The fix ships ``unit1_<kind>.voc`` singular vocab for
every unit kind each locale ships, so the plural COUNT is flagged and vetoed.

Anchor 2017-06-27 13:04.  Mirrors test/nl_corpus_de/test_nl_ordinal_count.py's
plural-count nomatch style.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_timespan

_REF = datetime(2017, 6, 27, 13, 4)

# locale -> plural-COUNT phrase that previously fabricated 2017-03-02
_FABRICATIONS = {
    "ast": "dos díes de marzu",
    "da": "de to dage i marts",
    "fy": "twa dagen fan maart",
    "he": "שני ימים של מרץ",
    "hr": "dva dana ožujka",
    "kab": "sin wussan n meɣres",
    "nb": "to dager av mars",
    "nn": "to dagar av mars",
    "ro": "două zile din martie",
    "sk": "dva dni marca",
    "sl": "dva dneva marca",
    "sv": "två dagar av mars",
    "cs": "dva dny března",
}


@pytest.mark.parametrize("lang,phrase", sorted(_FABRICATIONS.items()))
def test_plural_count_not_fabricated_into_ordinal(lang, phrase):
    assert extract_timespan(phrase, lang, _REF) is None
