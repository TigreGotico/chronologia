"""A Romance number fold finds its language's vocabulary when the language
subclasses ``NumberVocabulary``.

ovos-number-parser's Occitan module holds an ``OccitanVocabulary``. Every
Romance fold is built when the first one loads, so one subclass broke
extraction in all seven languages below."""
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from ovos_number_parser.util import NumberVocabulary

from chronologia import extract_duration, extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

# (lang, "tomorrow", "three days")
ROWS = [
    ("oc", "deman", "tres jorns"),
    ("pt", "amanhã", "três dias"),
    ("es", "mañana", "tres días"),
    ("fr", "demain", "trois jours"),
    ("it", "domani", "tre giorni"),
    ("ca", "demà", "tres dies"),
    ("gl", "mañá", "tres días"),
]


@pytest.mark.parametrize("lang,tomorrow,three_days", ROWS)
def test_romance_language_reads_after_the_subclass(lang, tomorrow, three_days):
    span = extract_timespan(tomorrow, lang, anchor=ANCHOR).span
    assert (span.start.year, span.start.month, span.start.day) == (2017, 6, 28)
    assert extract_duration(three_days, lang).duration == timedelta(days=3)


def test_subclass_instance_is_found():
    from chronologia.extract.numfold_romance import _number_vocabulary

    class LocalVocabulary(NumberVocabulary):
        pass

    vocab = object.__new__(LocalVocabulary)
    module = SimpleNamespace(NumberVocabulary=NumberVocabulary, _XX=vocab)
    assert _number_vocabulary(module) is vocab
