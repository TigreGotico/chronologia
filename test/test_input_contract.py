"""The shared input contract of the public extractors.

Every extractor reads natural-language text, so the two ways a call can go
wrong are kept apart.  Handing an extractor something that is not text is a
mistake in the calling program and raises :class:`TypeError` naming the
contract; handing it text the library cannot read -- the empty string, a
whitespace run, a sentence with no date in it -- is an ordinary answer of
"nothing here" and yields the extractor's empty result.

Before this contract existed ``None`` was silently accepted and returned
``None`` while ``123`` leaked an ``AttributeError`` from deep inside the
tokenizer, so the same category of mistake produced two different outcomes,
neither of them documented.
"""
import pytest

from chronologia.events import extract_event
from chronologia.extract import (extract_candidates, extract_duration,
                                 extract_recurrence, extract_timespan,
                                 extract_timespans)

#: every public extractor with the empty result its docstring promises
EXTRACTORS = [
    (extract_timespan, None),
    (extract_timespans, []),
    (extract_duration, None),
    (extract_recurrence, None),
    (extract_candidates, []),
    (extract_event, None),
]

NON_TEXT = [None, 123, 1.5, b"tomorrow", ["tomorrow"], {"text": "tomorrow"}]


@pytest.mark.parametrize("extractor,empty", EXTRACTORS)
@pytest.mark.parametrize("value", NON_TEXT)
def test_non_text_raises_type_error(extractor, empty, value):
    with pytest.raises(TypeError) as excinfo:
        extractor(value, "en")
    message = str(excinfo.value)
    assert extractor.__name__ in message
    assert "str" in message


@pytest.mark.parametrize("extractor,empty", EXTRACTORS)
@pytest.mark.parametrize("text", ["", "   ", "\n", "the quick brown fox"])
def test_unreadable_text_returns_the_empty_result(extractor, empty, text):
    assert extractor(text, "en") == empty


@pytest.mark.parametrize("extractor,empty", EXTRACTORS)
def test_readable_text_is_untouched_by_the_contract(extractor, empty):
    assert extractor("every friday at 9 for two weeks", "en") != empty


@pytest.mark.parametrize("extractor,empty", EXTRACTORS)
def test_none_and_a_number_are_treated_alike(extractor, empty):
    # the defect: ``None`` used to be accepted where ``123`` raised, so a
    # caller passing a missing value learned nothing about the mistake
    with pytest.raises(TypeError):
        extractor(None, "en")
    with pytest.raises(TypeError):
        extractor(123, "en")


@pytest.mark.parametrize("extractor,empty", EXTRACTORS)
def test_no_internal_exception_escapes(extractor, empty):
    # an AttributeError here would mean an implementation detail reached the
    # caller instead of the documented contract
    for value in NON_TEXT:
        try:
            extractor(value, "en")
        except TypeError:
            continue
        pytest.fail(f"{extractor.__name__}({value!r}) did not raise TypeError")
