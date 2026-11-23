"""Token passes shared by the Romance number folds.

The Romance languages read their numbers through numtag (``numlayer_ca``,
``numlayer_ro`` and their siblings).  The passes here prepare the tokens
before the number fold: an elided proclitic splits off its word ("d'annadas"
to "d" and "annadas"), a fixed phrase collapses to one connector ("înainte
de hristos"), the "NhMM" clock notation folds to an ``HH:MM`` literal, a
digit and its ordinal ending merge ("20-lea" to 20), and an abbreviation the
tokenizer splits glues back ("a.c.").
"""
from __future__ import annotations

import os
from dataclasses import replace

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import run_extent, reindex as _reindex

#: locale root, for reading a language's ``marker_quarter_word.voc`` (the
#: calendar-quarter noun -- "trimestre").
_LOCALE_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locale")


# abbreviations the tokenizer shatters on their dots/hyphens ("a.c." -> a,c;
# "meio-dia" -> meio,dia).  The fold glues the fragments back into the single
# token a marker/landmark slot binds.  Keyed by the fragment tuple, longest
# match first; shared across the Romance locales (surfaces are the same).
_ROMANCE_GLUE = {
    ("a", "e", "c"): "aec", ("a", "c"): "ac", ("d", "c"): "dc",
    ("e", "c"): "ec", ("a", "p"): "ap",
    ("meio", "dia"): "meiodia", ("meia", "noite"): "meianoite",
    ("migdia",): "migdia",
}


def _glue(tokens):
    seqs = sorted(_ROMANCE_GLUE, key=len, reverse=True)
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        for seq in seqs:
            k = len(seq)
            if tuple(t.text for t in tokens[i:i + k]) == seq:
                raw = "".join(t.raw for t in tokens[i:i + k])
                cs, ce = run_extent(tokens[i:i + k])
                out.append(Token(text=_ROMANCE_GLUE[seq], raw=raw, index=0,
                                 char_start=cs, char_end=ce))
                i += k
                break
        else:
            out.append(tokens[i])
            i += 1
    return tuple(out)


def _elision_split(tokens, proclitics):
    """Split a leading elided proclitic ("d'annees" -> "d", "annees").

    Only the closed proclitic set splits, so a lexical apostrophe inside a
    word ("aujourd'hui") stays whole."""
    out = []
    for t in tokens:
        head, sep, tail = t.text.partition("'")
        if not sep:
            head, sep, tail = t.text.partition("’")
        if sep and head in proclitics and tail:
            # keep each half's character extent into the original utterance --
            # the proclitic occupies the head chars, the elided word the tail
            # chars past the apostrophe -- so a mention built on the split word
            # ("d'abril") still recovers a char span instead of ``None``.
            cs, ce = t.char_start, t.char_end
            if cs is None or ce is None:
                h_start = h_end = w_start = None
            else:
                h_start, h_end, w_start = cs, cs + len(head), ce - len(tail)
            out.append(Token(text=head, raw=head, index=0,
                             char_start=h_start, char_end=h_end))
            out.append(Token(text=tail, raw=tail, index=0,
                             char_start=w_start, char_end=ce if cs is not None
                             else None))
        else:
            out.append(t)
    return _reindex(out)


def _collapse_phrase(tokens, words, surface):
    """Collapse a fixed multiword sequence ("il y a") to one token."""
    n = len(words)
    out = []
    i = 0
    while i < len(tokens):
        if [t.text for t in tokens[i:i + n]] == words:
            raw = " ".join(t.raw for t in tokens[i:i + n])
            cs, ce = run_extent(tokens[i:i + n])
            out.append(Token(text=surface, raw=raw, index=0,
                             char_start=cs, char_end=ce))
            i += n
        else:
            out.append(tokens[i])
            i += 1
    return _reindex(out)


def _collapse_h_clock(tokens, governors=frozenset(), followers=frozenset()):
    """Fold French/Occitan "20h30"/"20h" into one ``HH:MM`` clock literal.

    ``governors`` and ``followers`` keep "h" a word: after a counted-offset
    preposition ("dans 2 h") it is the unit of a length, and before a clock
    direction ("9 h et quart") it is the hour word the direction counts from.
    Both readings come from "h" being the symbol of "heure", so the grammar
    reads them as it reads "dans 2 heures" and "9 heures et quart".
    """
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        nn = tokens[i + 2] if i + 2 < n else None
        spared = ((out and out[-1].text in governors)
                  or (nn is not None and nn.text in followers))
        if (not spared
                and t.is_number and t.value is not None and 0 <= t.value <= 24
                and float(t.value).is_integer() and nxt is not None
                and nxt.text == "h"):
            if (nn is not None and nn.is_number and nn.value is not None
                    and 0 <= nn.value <= 59 and float(nn.value).is_integer()):
                lit = "%d:%02d" % (int(t.value), int(nn.value))
                cs, ce = run_extent(tokens[i:i + 3])
                out.append(Token(text=lit, raw=lit, index=0,
                                 char_start=cs, char_end=ce))
                i += 3
                continue
            lit = "%d:00" % int(t.value)
            cs, ce = run_extent(tokens[i:i + 2])
            out.append(Token(text=lit, raw=lit, index=0,
                             char_start=cs, char_end=ce))
            i += 2
            continue
        out.append(t)
        i += 1
    return _reindex(out)


def _merge_digit_ordinal(tokens, suffixes):
    """Drop a lone ordinal-suffix word after a digit ("1 er" -> 1)."""
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        if (t.is_number and nxt is not None and not nxt.is_number
                and nxt.text in suffixes):
            out.append(replace(t, ordinal=True))
            i += 2
            continue
        out.append(t)
        i += 1
    return _reindex(out)
