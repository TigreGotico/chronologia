# -*- coding: utf-8 -*-
"""R148: a sentence-final period must break mention clustering/range binding.

German (like Russian) is an ``ordinal_dot`` locale: the tokenizer folds a
digit run followed by a dot into ONE token when it forms an ordinal
("15." in "15. Juni"), stripping the dot from the token stream.  A
sentence-final period after a WORD ("...um 14 Uhr.") is never part of any
token to begin with -- the tokenizer drops standalone punctuation entirely
-- so two matches sitting either side of it have an EMPTY token-index gap
that :func:`~chronologia.extract.nseries._cluster_resolved` used to read as
vacuously adjacent, and :func:`~chronologia.extract.nseries._merge_ranges`
used to happily bridge with a "from ... to ..." range read.  The result was
two mentions in two different SENTENCES silently fused into one -- a point
mention absorbing a later clause's deadline, or a bare weekday and a later
"until <weekday>" clause misread as one range spanning both sentences.

The fix (``_sentence_period_between``) checks the character GAP between two
matches' edge tokens for a literal "." the tokenizer never leaves there
except when it is a genuine sentence break: an ordinal or decimal dot is
always INSIDE its own token's char span, never in the gap between two
tokens.  This file pins the two reported repros, an adversarial variant
of each that drops the second clause's own mention entirely if the fix is
too broad, and a battery of ordinal-dot controls that must NOT be affected
(including a two-sentence text where sentence 1 itself ends on an ordinal
date).  en/es non-regression spot pins live alongside as controls: the
same shapes without a dot-folding tokenizer must keep splitting exactly as
before.
"""
from datetime import datetime

from chronologia.extract import extract_timespans
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2026, 8, 10, 9, 0)


def mentions(text, lang="de"):
    return extract_timespans(text, lang, ANCHOR)


# --------------------------------------------------------------------------
# The two reported repros.
# --------------------------------------------------------------------------

def test_r148_de_meeting_and_deadline_stay_two_mentions():
    ms = mentions(
        "Das naechste Meeting ist am kommenden Freitag um 14 Uhr. "
        "Bitte reichen Sie Ihre Berichte bis Ende des Monats ein."
    )
    assert len(ms) == 2
    friday, deadline = ms
    assert friday.span.start == AstroDate(2026, 8, 14, 14, 0)
    assert friday.span.end == AstroDate(2026, 8, 14, 14, 1)
    assert deadline.span.start == AstroDate(2026, 8, 21, 16, 0)
    assert deadline.span.end == AstroDate(2026, 9, 1, 0, 0)


def test_r148_de_monday_and_friday_stay_two_mentions_not_a_range():
    ms = mentions(
        "Wir treffen uns am Montag. Der Bericht ist bis Freitag faellig."
    )
    assert len(ms) == 2
    monday, friday = ms
    # a genuine "Mon .. Sat" RANGE (what the defect produced) always has a
    # single mention whose span crosses several days; two SEPARATE point
    # mentions, one per sentence, is the only correct reading here.
    assert monday.span.start == AstroDate(2026, 8, 17)
    assert monday.span.end == AstroDate(2026, 8, 18)
    assert friday.span.start == AstroDate(2026, 8, 14)
    assert friday.span.end == AstroDate(2026, 8, 15)


# --------------------------------------------------------------------------
# Adversarial: the fix must not overshoot and drop the second clause.
# --------------------------------------------------------------------------

def test_r148_de_second_clause_survives_as_its_own_mention():
    """A regression that merely swallowed the boundary token instead of
    splitting on it would leave only the FIRST mention; both must survive."""
    ms = mentions("Der Termin ist am Dienstag. Die Frist ist am Mittwoch.")
    assert len(ms) == 2
    assert ms[0].span.start == AstroDate(2026, 8, 11)
    assert ms[1].span.start == AstroDate(2026, 8, 12)


def test_r148_de_three_sentences_four_mentions():
    """'Heute' (today) itself names a mention, so three sentences carrying
    four dated references ('heute', 'Montag', 'Mittwoch', 'Freitag') must
    each survive as their own mention -- none absorbed across a period."""
    ms = mentions(
        "Heute ist Montag. Das Meeting ist am Mittwoch. "
        "Die Frist ist am Freitag."
    )
    assert len(ms) == 4
    assert [m.span.start.day for m in ms] == [10, 17, 12, 14]


# --------------------------------------------------------------------------
# Ordinal-dot controls -- must NOT be treated as a sentence boundary.
# --------------------------------------------------------------------------

def test_r148_de_ordinal_dot_bare_date_unaffected():
    ms = mentions("Das Meeting ist am 15. Juni.")
    assert len(ms) == 1
    assert ms[0].span.start == AstroDate(2027, 6, 15)


def test_r148_de_ordinal_dot_composition_unaffected():
    """'3. März um 9 Uhr' -- ordinal day, month, and a clock composing into
    ONE reading; the ordinal dot must not be misread as a clause break that
    would split date and month apart."""
    ms = mentions("Wir treffen uns am 3. Maerz um 9 Uhr.")
    assert len(ms) == 1
    assert ms[0].span.start == AstroDate(2027, 3, 3, 9, 0)


def test_r148_de_sentence_ending_on_an_ordinal_date_still_splits():
    """Sentence 1 itself ENDS with an ordinal date ('am 15. Juni.'); the
    period after that ordinal-dot construction is a genuine sentence
    break (it follows the whole "15. Juni" mention, not the bare ordinal
    token) and must still split off sentence 2's own mention."""
    ms = mentions("Wir treffen uns am 15. Juni. Danach gibt es ein Fest am Montag.")
    assert len(ms) == 2
    assert ms[0].span.start == AstroDate(2027, 6, 15)
    assert ms[1].span.start == AstroDate(2026, 8, 17)


def test_r148_de_dotted_civil_date_unaffected():
    """The DIN 5008 dotted date '15.06.2020' reads as one date literal;
    nothing about the sentence-boundary fix should touch its internal dots."""
    ms = mentions("Das Treffen ist am 15.06.2020.")
    assert len(ms) == 1
    assert ms[0].span.start == AstroDate(2020, 6, 15)


# --------------------------------------------------------------------------
# en/es non-regression: the same shapes, no dot-folding tokenizer involved.
# --------------------------------------------------------------------------

def test_r148_en_control_still_splits():
    ms = mentions(
        "Our next meeting is next Friday at 2pm. "
        "Please submit your reports by the end of the month.",
        lang="en-us",
    )
    assert len(ms) == 2
    assert ms[0].span.start == AstroDate(2026, 8, 14, 14, 0)
    assert ms[1].span.start == AstroDate(2026, 8, 21, 16, 0)
    assert ms[1].span.end == AstroDate(2026, 9, 1, 0, 0)


def test_r148_en_control_weekday_pair_still_two_mentions():
    ms = mentions(
        "We will meet on Monday. The report is due by Friday.",
        lang="en-us",
    )
    assert len(ms) == 2
    assert ms[0].span.start == AstroDate(2026, 8, 17)
    assert ms[1].span.start == AstroDate(2026, 8, 14)


def test_r148_es_control_still_splits():
    ms = mentions(
        "Nuestra proxima reunion es el proximo viernes a las 14:00. "
        "Por favor entregue sus informes antes de fin de mes.",
        lang="es",
    )
    assert len(ms) == 2
    assert ms[0].span.start == AstroDate(2026, 8, 14, 14, 0)
    assert ms[1].span.start == AstroDate(2026, 8, 21, 16, 0)
    assert ms[1].span.end == AstroDate(2026, 9, 1, 0, 0)
