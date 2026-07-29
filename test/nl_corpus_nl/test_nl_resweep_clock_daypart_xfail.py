# -*- coding: utf-8 -*-
"""Second-pass resweep: clock + daypart-suffix combinations (nl) -- xfail.

Idiomatic Dutch routinely disambiguates a 12-hour clock reading with a
trailing daypart marker: "acht uur 's avonds" (eight o'clock in the evening)
is unambiguously 20:00 to a native speaker, and "drie uur 's middags"
(three o'clock in the afternoon) is unambiguously 15:00.

Originally the parser did NOT fold the daypart suffix into the hour: it
parsed the bare clock reading (am-style, 0-11) and then separately stranded
the daypart word as an unconsumed token, so "acht uur 's avonds" resolved to
08:00, not 20:00.  The postposed genitive daypart now binds the clock's
meridiem slot (avond/middag -> pm, +12) through the shared clock path -- the
same mechanism de already used for "abends"/"nachmittags" -- so these assert
the idiomatically-intended PM hour directly.

Anchor: Tuesday 2017-06-27 13:04.
"""
import pytest

from ._corpus import clk, span


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
