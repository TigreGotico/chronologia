# -*- coding: utf-8 -*-
"""Regression for defect R130 (pt half): the spelled-out clock unit word
"horas"/"hora" after a bare numeral was stranded as unconsumed remainder
("terça às 21 horas" -> 21:00-21:01 span, remainder "horas").

Portuguese already folds the digital-clock suffix "h" into the CLOCK token
(defect R121, ``_collapse_h_clock`` in ``fold_pt``), but the fully spelled
unit word never had a grammar slot of its own -- no pt ``clock_time`` order
named it, so it fell through untouched.  French already solves the sibling
problem: "9 heures" consumes "heures" via the literal ``oclock`` slot
(``marker_oclock.voc`` -> "heures"/"heure"/"h"). The fix mirrors that:
``chronologia/locale/pt/marker_oclock.voc`` now lists "horas"/"hora", and
every pt ``clock_time`` order binds an optional ``oclock?`` slot right after
``HOUR``.

Anchor for extract_timespan cases is the shared pt corpus anchor,
2017-06-27 13:04 (Tuesday) -- see ``test/nl_corpus_pt/_corpus.py``.
"""
from ._corpus import ANCHOR, parse, span


# -- clean remainder: the spelled unit fully consumes ------------------------

def test_plural_horas_with_weekday():
    r = parse("terça às 21 horas")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (21, 0)
    assert remainder == ""


def test_plural_horas_bare():
    r = parse("às 9 horas")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (9, 0)
    assert remainder == ""


def test_plural_horas_with_meridiem_daypart():
    r = parse("às 9 horas da manhã")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (9, 0)
    assert remainder == ""


def test_singular_hora():
    r = parse("à 1 hora")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (1, 0)
    assert remainder == ""


# -- embedded in a longer sentence -------------------------------------------

def test_horas_embedded_in_sentence():
    r = parse("a reunião é terça às 21 horas no escritório")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (21, 0)
    assert "horas" not in remainder.split()


# -- the "h" digital-clock suffix (R121) still consumes cleanly -------------

def test_h_suffix_still_clean():
    r = parse("terça às 21h")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (21, 0)
    assert remainder == ""


# -- control: "horas" as a plain noun elsewhere must survive untouched ------

def test_horas_plain_noun_control():
    r = parse("muitas horas de trabalho ontem")
    assert r is not None
    s, remainder = r
    assert remainder == "muitas horas de trabalho"
