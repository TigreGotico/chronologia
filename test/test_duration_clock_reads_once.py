"""extract_duration reads the clocks of a text once, however many hour counts it holds."""
from chronologia import extract_duration
from chronologia.extract.nseries import _timespan_engine


def test_duration_runs_the_matcher_once(monkeypatch):
    matcher = _timespan_engine("nl").matcher
    match, runs = matcher.match, []
    monkeypatch.setattr(matcher, "match",
                        lambda *args: runs.append(1) or match(*args))
    extract_duration(" en ".join(f"{k} uur" for k in range(2, 12)), "nl")
    assert len(runs) == 1


def test_a_clock_hour_is_still_no_length():
    assert extract_duration("om 8 uur", "nl") is None
    assert extract_duration("à 8 heures", "fr") is None
    assert extract_duration("over 2 uur", "nl").duration.total_seconds() == 7200
