# -*- coding: utf-8 -*-
"""R122: a bound "בין A ל-B" range must consume its own leading "between".

Hebrew's proclitic ל־ ("to/for") is only trusted as a range terminator when a
"from" (מ/מן) or "between" (בין) lead licenses it (``marker_to_after_from``).
The "from A to B" branch stripped a "from" lead but not a "between" lead when
the split landed on that licensed ל terminator, so "בין 3 במרץ ל-5 באפריל"
resolved the correct span while leaving "בין" stranded, unclaimed, in the
remainder -- the span was right, the marker word was not consumed.
"""
from ._corpus import parse, AstroDate


def test_bein_lead_range_consumes_the_leading_marker():
    text = "בין 3 במרץ ל-5 באפריל"
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r[0].start == AstroDate(2018, 3, 3)
    assert r[0].end == AstroDate(2018, 4, 6)
    assert r[1] == "", f"marker word leaked into remainder: {r[1]!r}"


def test_range_embedded_in_a_sentence_keeps_the_surrounding_words():
    text = "הפגישות מתקיימות בין 3 במרץ ל-5 באפריל בבניין הראשי."
    r = parse(text)
    assert r is not None
    assert r[0].start == AstroDate(2018, 3, 3)
    assert r[0].end == AstroDate(2018, 4, 6)
    # "הפגישות מתקיימות" (the meetings take place) and "בבניין הראשי" (in the
    # main building) are real non-temporal content -- the fix must only
    # swallow the "בין" lead, never the surrounding sentence.
    assert r[1] == "הפגישות מתקיימות בבניין הראשי", f"remainder: {r[1]!r}"


def test_bare_lamed_with_no_lead_is_not_a_range():
    # Control: the proclitic ל is a hyper-common directional/dative
    # preposition ("for 3 hours") -- without a from/between lead it must
    # never be mistaken for a range terminator, exactly as before this fix.
    text = "ל-3 שעות"
    r = parse(text)
    assert r is None, f"{text!r} unexpectedly parsed to {r!r}"


def test_bein_outside_a_range_is_left_in_the_remainder():
    # Control: "בין" as an ordinary preposition ("between the parties") with
    # no range actually binding through it must NOT be swallowed -- only a
    # "בין" that genuinely leads a bound range is consumed.
    text = "הפגישה בין הצדדים תתקיים ב-5 באפריל."
    r = parse(text)
    assert r is not None
    assert r[0].start == AstroDate(2018, 4, 5)
    assert "בין" in r[1], f"'between' should have stayed in remainder: {r[1]!r}"
