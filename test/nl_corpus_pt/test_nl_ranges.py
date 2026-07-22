# -*- coding: utf-8 -*-
"""Ranges.  Dash-framed ranges parse language-agnostically; the word-framed
Romance forms ("de junho a agosto", "entre ... e ...") need range framings
the engine only ships in English -- those are xfail'd with that reason."""
import pytest

from ._corpus import AstroDate, start_end, nomatch


@pytest.mark.parametrize("text,s,e", [
    ("junho - agosto", (2017, 6, 1), (2017, 9, 1)),
    ("janeiro - março", (2017, 1, 1), (2017, 4, 1)),
    ("5 de junho - 12 de junho", (2018, 6, 5), (2018, 6, 13)),
])
def test_dash_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.xfail(reason="engine range framings (from/to/between/and) are "
                          "English-only; Romance 'de X a Y' unsupported",
                   strict=True)
def test_word_framed_range():
    ss, ee = start_end("de junho a agosto")
    assert ss == AstroDate(2017, 6, 1) and ee == AstroDate(2017, 9, 1)


from ._corpus import ANCHOR, ad  # noqa: E402


def _d(s):
    return AstroDate(*(int(x) for x in s.split("-")))


# -- dash-framed date ranges: the prefer-future frame stays consistent across
# both endpoints even when the range straddles "now" (anchor 2017-06-27) -----

@pytest.mark.parametrize("text,s,e", [
    ("20 de junho - 30 de junho", "2017-6-20", "2017-7-1"),   # straddle
    ("10 de julho - 20 de julho", "2017-7-10", "2017-7-21"),  # both ahead
    ("28 de junho - 30 de junho", "2017-6-28", "2017-7-1"),   # both ahead
    ("1 de junho - 10 de junho", "2018-6-1", "2018-6-11"),    # both behind
    ("25 de junho - 5 de julho", "2017-6-25", "2017-7-6"),    # cross-month
    ("10 de agosto - 20 de setembro", "2017-8-10", "2017-9-21"),
    ("28 de dezembro - 3 de janeiro", "2017-12-28", "2018-1-4"),  # cross-year
    ("3 de março 2001 - 9 de março 2001", "2001-3-3", "2001-3-10"),  # years
])
def test_dash_date_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


# -- open-ended ranges: "até" (open start) / "desde" (open end) -------------

def test_ate_open_start():
    s, e = start_end("até sexta-feira")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2017, 7, 1)


def test_desde_open_end():
    s, e = start_end("desde 2010")
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(ANCHOR)


# -- negatives: non-temporal endpoints never fabricate a range --------------

@pytest.mark.parametrize("text", ["de maçã a laranja", "de aqui a ali"])
def test_non_temporal_range_is_none(text):
    nomatch(text)
