"""R122: a bound "von A bis B" range must consume its own marker words.

German closes a range with the two-word compound "bis zum"/"bis zur" (the
plain terminator "bis" fused with the dative article "zum"/"zur" -- "vom 3.
bis zum 5. April").  The connector scanner only had the bare "bis" registered,
so it split on "bis" alone and left "zum"/"zur" sitting unclaimed in front of
the right endpoint: the span came out correct, but the marker word leaked into
``.remainder`` -- this repo's defect signature (a stranded temporal function
word) even though the math was right.
"""
from ._corpus import parse, span, AstroDate


def test_bis_zum_range_consumes_the_compound_marker():
    text = "vom 3. März bis zum 5. April"
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r[0] == span(text)
    assert r[0].start == AstroDate(2018, 3, 3)
    assert r[0].end == AstroDate(2018, 4, 6)
    assert r[1] == "", f"marker word leaked into remainder: {r[1]!r}"


def test_bis_zur_range_consumes_the_compound_marker():
    text = "vom 3. März bis zur Wanderung am 5. April"
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r[0].start == AstroDate(2018, 3, 3)
    assert r[0].end == AstroDate(2018, 4, 6)
    # "Wanderung am" (the hike, on) is real non-temporal content named by the
    # range's own trailing clause and must survive in the remainder -- only
    # the "zur" marker glue is swallowed, never the noun/preposition it
    # introduces.
    assert r[1] == "Wanderung am", f"unexpected remainder: {r[1]!r}"


def test_range_embedded_in_a_sentence_keeps_the_surrounding_words():
    text = "Ich habe vom 3. März bis zum 5. April Urlaub genommen."
    r = parse(text)
    assert r is not None
    assert r[0].start == AstroDate(2018, 3, 3)
    assert r[0].end == AstroDate(2018, 4, 6)
    # "Urlaub genommen" (took vacation) and the sentence subject are real
    # content -- the fix must only swallow the marker, not everything else.
    assert r[1] == "Ich habe vom Urlaub genommen", f"remainder: {r[1]!r}"


def test_open_range_bis_zum_still_consumes_the_marker():
    # An open range ("until April 5") has no "from" lead at all -- the fix
    # must not depend on one being present.
    text = "bis zum 5. April"
    r = parse(text)
    assert r is not None
    assert r[0].end == AstroDate(2018, 4, 6)
    assert r[1] == "", f"marker word leaked into remainder: {r[1]!r}"


def test_lone_zum_outside_a_range_is_left_alone():
    # Control: "zum" is an ordinary German contraction ("zu dem") used all
    # over the language outside of range constructions.  A bare "bis" with
    # no following "zum"/"zur" article, or "zum" with no preceding "bis",
    # must not have "zum" swallowed by this fix.
    text = "Ich gehe zum Bahnhof."
    r = parse(text)
    assert r is None, f"{text!r} unexpectedly parsed to {r!r}"
