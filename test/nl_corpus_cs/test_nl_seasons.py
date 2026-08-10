"""Czech seasons and scoped references.

Seasons are meteorological and northern-hemisphere (spring = MAM).
next/this <season> resolve against the 2017-06-27 anchor.
"""
import pytest

from ._corpus import AstroDate, start_end, start


# meteorological northern-hemisphere season blocks
@pytest.mark.parametrize("text,s,e", [
    ("příští zima", "2017-12-1", "2018-3-1"),
    ("příští jaro", "2018-3-1", "2018-6-1"),
    ("léto 2020", "2020-6-1", "2020-9-1"),
    ("zima 2019", "2019-12-1", "2020-3-1"),
    ("podzim 2018", "2018-9-1", "2018-12-1"),
])
def test_season(text, s, e):
    def _d(x):
        y, m, dd = (int(v) for v in x.split("-"))
        return AstroDate(y, m, dd)
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


@pytest.mark.parametrize("text,s,e", [
    # Genitive singular per Internetová jazyková příručka (ÚJČ AV ČR)
    # declension tables: "jaro" (neut., "město" type) -> gen. jara; "zima"
    # (fem., "žena" type) -> gen. zimy.  "podzim" (masc. inanimate, "hrad"
    # type) is SKIPPED: its genitive is "podzimu", already present in
    # season_fall.voc (identical to the locative/dative form already
    # there), so there is no gap to fix.  "léto" (neut.) -> gen. "léta" is
    # included: checked for collision with "years" (cs counts years with
    # "roky"/"let"/"lety", never "léta") and no such usage exists in
    # unit_year.voc or the cs test corpus, so it is safe to add (unlike the
    # analogous Polish "lata", which IS the live plural of "rok").
    ("jara 2027", "2027-3-1", "2027-6-1"),
    ("léta 2027", "2027-6-1", "2027-9-1"),
    ("zimy 2027", "2027-12-1", "2028-3-1"),
    # control: nominative unchanged
    ("jaro 2027", "2027-3-1", "2027-6-1"),
])
def test_season_genitive_case(text, s, e):
    def _d(x):
        y, m, dd = (int(v) for v in x.split("-"))
        return AstroDate(y, m, dd)
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


def test_scoped_century():
    # "21. století" = the 21st century (engine convention: 2000-01-01 ..
    # 2100-01-01, matching the English "the 21st century" staple)
    ss, ee = start_end("21. století")
    assert ss == AstroDate(2000, 1, 1) and ee == AstroDate(2100, 1, 1)
