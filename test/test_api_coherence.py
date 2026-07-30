"""API-coherence guarantees: the three ``extract_*`` edges that return a
value+remainder pair hand back a NamedTuple, so a caller may either unpack it
as a plain 2-tuple (the historical shape) or read the domain-named fields --
and the two ``Candidate`` classes no longer share a name.
"""
import unittest
from datetime import timedelta

from chronologia import (DateSpanResult, DurationResult, RecurrenceResult,
                         extract_duration, extract_recurrence,
                         extract_timespan)
from chronologia.astrodate import DateSpan


class TestNamedReturns(unittest.TestCase):
    def test_timespan_unpacks_and_names(self):
        res = extract_timespan("june 2027")
        self.assertIsInstance(res, DateSpanResult)
        # tuple unpacking still works (NamedTuple IS a tuple)
        span, remainder = res
        self.assertIsInstance(span, DateSpan)
        # indexed access still works
        self.assertIs(res[0], span)
        self.assertEqual(res[1], remainder)
        # named access
        self.assertIs(res.span, span)
        self.assertEqual(res.remainder, remainder)

    def test_duration_unpacks_and_names(self):
        res = extract_duration("an hour and a half")
        self.assertIsInstance(res, DurationResult)
        duration, remainder = res
        self.assertEqual(duration, timedelta(minutes=90))
        self.assertEqual(res[0], duration)
        self.assertEqual(res.duration, timedelta(minutes=90))
        self.assertEqual(res.remainder, remainder)

    def test_recurrence_unpacks_and_names(self):
        res = extract_recurrence("every friday")
        self.assertIsInstance(res, RecurrenceResult)
        recurrence, remainder = res
        self.assertEqual(res[0], recurrence)
        self.assertIs(res.recurrence, recurrence)
        self.assertEqual(res.remainder, remainder)
        self.assertEqual(recurrence.to_string(), "FREQ=WEEKLY;BYDAY=FR")

    def test_no_match_still_none(self):
        self.assertIsNone(extract_timespan("nothing temporal here at all"))
        self.assertIsNone(extract_duration("nothing temporal here at all"))
        self.assertIsNone(extract_recurrence("nothing temporal here at all"))


class TestCandidateNameCollision(unittest.TestCase):
    def test_public_candidate_is_the_exported_one(self):
        from chronologia import Candidate as PublicCandidate
        from chronologia.extract import Candidate as ExtractCandidate
        self.assertIs(PublicCandidate, ExtractCandidate)
        # the public Candidate carries the span/remainder/confidence surface
        for field in ("span", "remainder", "confidence", "construction"):
            self.assertIn(field, PublicCandidate.__dataclass_fields__)

    def test_internal_matcher_candidate_renamed(self):
        from chronologia.extract.matcher import MatchCandidate
        self.assertEqual(MatchCandidate.__name__, "MatchCandidate")
        # the internal one is the match+precedence detail, a different class
        from chronologia.extract import Candidate as PublicCandidate
        self.assertIsNot(MatchCandidate, PublicCandidate)
        # and the old internal name is gone from the matcher module
        import chronologia.extract.matcher as m
        self.assertFalse(hasattr(m, "Candidate"))


class TestDeprecatedAliases(unittest.TestCase):
    def test_timespanresult_is_deprecated_alias_of_datespanresult(self):
        import warnings

        import chronologia
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            alias = chronologia.TimeSpanResult
        self.assertIs(alias, DateSpanResult)
        self.assertTrue(
            any(issubclass(w.category, DeprecationWarning) for w in caught),
            "accessing the deprecated TimeSpanResult must warn")


if __name__ == "__main__":
    unittest.main()
