# -*- coding: utf-8 -*-
"""Second-pass resweep: clock + daypart-suffix combinations (nl) -- xfail.

Idiomatic Dutch routinely disambiguates a 12-hour clock reading with a
trailing daypart marker: "acht uur 's avonds" (eight o'clock in the evening)
is unambiguously 20:00 to a native speaker, and "drie uur 's middags"
(three o'clock in the afternoon) is unambiguously 15:00.

Probing confirms the parser does NOT fold the daypart suffix into the hour:
it parses the bare clock reading (am-style, 0-11) and then separately
attaches the daypart word as an unconsumed/ornamental token, so "acht uur
's avonds" resolves to 08:00, not 20:00 (own-anchor probe below). This is a
real vocabulary gap, not a corpus mistake -- the CORRECT gold per the
idiomatic sentence is the 12-hour-shifted time, so these are recorded as
strict xfail with the honest (shifted) gold rather than silently asserting
the wrong (bare) hour the engine currently returns.

Anchor: Tuesday 2017-06-27 13:04.
"""
import pytest

from ._corpus import clk, span

pytestmark = pytest.mark.xfail(
    strict=True,
    reason="nl: daypart suffix ('s avonds/'s middags/'s nachts) does not "
           "shift a bare 12h clock reading into 24h form; parser keeps the "
           "bare (0-11) hour instead of the idiomatically-intended PM hour",
)


@pytest.mark.parametrize("text,h,mi", [
    ("acht uur 's avonds", 20, 0),
    ("drie uur 's middags", 15, 0),
    ("tien uur 's avonds", 22, 0),
    ("negen uur 's avonds", 21, 0),
    ("vier uur 's middags", 16, 0),
    ("kwart over drie 's middags", 15, 15),
    ("kwart voor negen 's avonds", 20, 45),
    ("half twee 's middags", 13, 30),
])
def test_clock_daypart_pm_shift_expected(text, h, mi):
    assert span(text).start == clk(h, mi)
