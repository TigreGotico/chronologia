# -*- coding: utf-8 -*-
"""Season + explicit year sweep (ru) -- "весна 2019" etc.

Meteorological northern-hemisphere seasons: весна = Mar-May (Mar1..Jun1), лето
= Jun-Aug, осень = Sep-Nov, зима = Dec..Feb (Dec1 of the named year to Mar1 of
the next).  Gold is that fixed mapping, independent of the parser.  Anchor
2017-06-27."""
import pytest

from ._corpus import AstroDate, start_end

_YEARS = (2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2025)


def _cases():
    out = []
    for year in _YEARS:
        out.append((f"весна {year}", AstroDate(year, 3, 1), AstroDate(year, 6, 1)))
        out.append((f"лето {year}", AstroDate(year, 6, 1), AstroDate(year, 9, 1)))
        out.append((f"осень {year}", AstroDate(year, 9, 1), AstroDate(year, 12, 1)))
        out.append((f"зима {year}", AstroDate(year, 12, 1), AstroDate(year + 1, 3, 1)))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_season_year(text, s, e):
    st, en = start_end(text)
    assert st == s
    assert en == e


# -- adjectival early/late season forms ("ранней весны 2027") -------------

# Regression: "ранней весны 2027" ("of an early spring 2027") used to match
# the bare genitive season_ref order ("SEASON<gen> YEAR?"), claiming the
# whole 3-month span and stranding the adjective "ранней" (feminine
# genitive of "ранний", agreeing with genitive "весны") in the remainder --
# the same silently-too-wide failure the ``season_fuzzy`` construction
# fixes for the noun period_part surface (начало/середина/конец).  Only the
# noun paradigm was in period_part_early/late.voc; the adjectival paradigm
# of "ранний"/"поздний" (Зализняк, hard-stem adjective declension) was
# missing.  Added here: nominative fem ранняя, genitive/dative/instr/prep
# fem ранней, neuter nom/acc раннее, genitive masc/neut раннего,
# accusative fem раннюю; parallel late forms поздняя/поздней/позднего/
# позднюю.  "позднее" is DELIBERATELY withheld: it is homographic with the
# comparative adverb "позднее" ("later") -- Зализняк's neuter nom/acc of
# "поздний" happens to coincide exactly with that adverb's comparative
# form, so adding it risks hijacking any future "позднее"-as-adverb
# construction; "раннее" has no such collision (the comparative of "рано"
# is "раньше", not "раннее"). Comparative adverbs "ранее"/"позднее" are
# likewise never added as PART entries for the same reason. Grepped the
# full ru corpus (test/nl_corpus_ru/) and ru/*.voc for any existing use of
# ранее/позднее/ранняя/поздняя before adding -- none found.
#
# Expected boundaries are the same independent thirds-of-92-days arithmetic
# already pinned for "early/late spring 2027" in the en corpus
# (test_nl_scoped_seasons_fuzzy.py); spring 2027 (2027-03-01..2027-06-01,
# non-leap) is calendar-identical across locales.

@pytest.mark.parametrize("text,s,e", [
    ("ранней весны 2027", AstroDate(2027, 3, 1, 0, 0), AstroDate(2027, 3, 31, 16, 0)),
    ("поздней весны 2027", AstroDate(2027, 5, 1, 8, 0), AstroDate(2027, 6, 1, 0, 0)),
])
def test_season_fuzzy_adjectival(text, s, e):
    st, en = start_end(text)
    assert st == s
    assert en == e


def test_season_fuzzy_adjectival_consumes_part():
    from ._corpus import parse
    r = parse("ранней весны 2027")
    assert r is not None
    span_, remainder = r
    assert span_.start == AstroDate(2027, 3, 1, 0, 0)
    assert not remainder.strip()
