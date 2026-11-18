"""Pins that ruling 34 moved: a lone numeral is a candidate, not a reading.

Ruling 34 of the chronologia disagreement rulings: a numeral that is the
whole text, written in digits of any script, is not a date in
``extract_timespan``; ``extract_candidates`` lists its year reading.  A test
that pinned the year as the reading of such a numeral asserts that the year's
span is among ``candidate_spans`` instead.
"""
from chronologia import extract_candidates, extract_timespan


def candidate_spans(text, lang, anchor):
    """The ``(start, end)`` of every candidate of ``text``, or ``[]`` when
    ``extract_timespan`` reads ``text`` as a date."""
    if extract_timespan(text, lang, anchor) is not None:
        return []
    return [(c.span.start, c.span.end)
            for c in extract_candidates(text, lang, anchor)]
