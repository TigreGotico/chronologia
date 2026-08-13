# -*- coding: utf-8 -*-
"""R161: a bare year under the "Jahr" marker must not absorb a following
SENTENCE-terminal period into its own mention text.

German is an ``ordinal_dot`` locale: the tokenizer folds a digit run
followed by a dot into one token so a genuine ordinal ("15." in "15. Juni")
keeps its dot glued on. That regex used to fire on ANY digit run, so a bare
4-digit year immediately followed by a sentence period ("2027.", no space)
was folded the same way -- even though a bare year is never itself an
ordinal -- and the trailing "." rode along into the mention's ``.text``.

The fix is a new PER-LOCALE tokenizer fact, ``ordinal_dot_max_digits``
(``TokenizerModes`` / ``lang.json`` ``tokenizer`` key), not a blanket cap on
the shared ``ordinal_dot`` regex: German ordinals never run past 2 digits
(a day-of-month, a two-digit count), so de sets it to 2 and a bare 4-digit
year's digit run no longer matches the ordinal-dot rule -- the trailing
period is then dropped as ordinary punctuation, exactly as it already is
for a non-ordinal-dot locale (en/ru) or for a de sentence that does not end
on a bare year. Every OTHER ``ordinal_dot`` locale keeps the field unset
(unbounded, the original ``\\d+`` behaviour): Hungarian, for one, legitimately
opens a dotted date with a dotted 4-digit YEAR ("2026. június 20."), where
the trailing dot after the year is a real part of that construction and
must survive -- a blanket digit cap broke exactly this (see
``test_r161_hu_dotted_year_date_unaffected`` below, the regression this
file's first version introduced and this rework fixes).

Controls pin dotted civil dates ('15.06.2020.') and genuine ordinal dots
('3. märz', 'der 15. Juni') as unaffected -- both stay 1-2 digit surfaces the
de cap still matches -- and the Hungarian year-first dotted date as
unaffected by a cap that only applies to de.
"""
from datetime import datetime

from chronologia.extract import extract_timespans
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2026, 8, 13, 10, 0)


def mentions(text, lang="de"):
    return extract_timespans(text, lang, ANCHOR)


def test_r161_de_bare_year_under_jahr_marker_clean_text():
    ms = mentions("Das Jahr 2027. Es wird toll.")
    assert len(ms) == 1
    assert ms[0].text == "das jahr 2027"
    assert ms[0].span.start == AstroDate(2027, 1, 1)


def test_r161_de_bare_year_no_marker_still_clean():
    """Without the 'Jahr' marker the year is not even ordinal-dot-adjacent
    to a preceding word the same way -- pinned as a same-shape control."""
    ms = mentions("2027 wird toll.")
    assert len(ms) == 1
    assert ms[0].text == "2027"


def test_r161_de_bare_year_mid_sentence_two_mentions_still_split():
    """The sentence-boundary clustering fix (R148) must still see the
    period as a genuine clause break even though the year token no longer
    swallows it itself -- two SEPARATE mentions, not a fused range."""
    ms = mentions("Das Jahr 2027. Der Termin ist am Montag.")
    assert len(ms) == 2
    assert ms[0].text == "das jahr 2027"
    assert ms[1].span.start == AstroDate(2026, 8, 17)


# --------------------------------------------------------------------------
# en/ru controls: same shape, always had clean text (no ordinal-dot
# tokenizer to have leaked the period in the first place).
# --------------------------------------------------------------------------
def test_r161_en_control_clean_text():
    ms = mentions("The year 2027. It will be great.", lang="en-us")
    assert len(ms) == 1
    assert ms[0].text == "the year 2027"


def test_r161_ru_control_clean_text():
    ms = mentions("Год 2027. Будет здорово.", lang="ru")
    assert len(ms) == 1
    assert ms[0].text == "год 2027"


# --------------------------------------------------------------------------
# Ordinal-dot / dotted-date controls: must NOT be affected by capping the
# ordinal-dot rule at 1-2 digits -- both are already 1-2 digit surfaces.
# --------------------------------------------------------------------------
def test_r161_de_dotted_civil_date_unaffected():
    ms = mentions("Das Treffen ist am 15.06.2020.")
    assert len(ms) == 1
    assert ms[0].span.start == AstroDate(2020, 6, 15)
    assert ms[0].text == "15.06.2020"


def test_r161_de_ordinal_dot_bare_date_unaffected():
    ms = mentions("Das Meeting ist am 15. Juni.")
    assert len(ms) == 1
    assert ms[0].span.start == AstroDate(2027, 6, 15)
    assert ms[0].text == "15. juni"


def test_r161_de_ordinal_dot_one_digit_unaffected():
    ms = mentions("Wir treffen uns am 3. Maerz um 9 Uhr.")
    assert len(ms) == 1
    assert ms[0].span.start == AstroDate(2027, 3, 3, 9, 0)


# --------------------------------------------------------------------------
# hu control: a year-first DOTTED date, where the ordinal dot after the
# 4-digit year is a genuine, load-bearing part of the construction -- the de
# cap must not apply here (hu leaves ``ordinal_dot_max_digits`` unset).
# --------------------------------------------------------------------------
def test_r161_hu_dotted_year_date_unaffected():
    ms = mentions("2026. június 20. vagy 2026. augusztus 4.", lang="hu")
    assert len(ms) == 2
    assert ms[0].text == "2026. június 20."
    assert ms[1].text == "2026. augusztus 4."
    assert ms[0].span.start == AstroDate(2026, 6, 20)
    assert ms[1].span.start == AstroDate(2026, 8, 4)
