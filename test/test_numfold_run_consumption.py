# -*- coding: utf-8 -*-
"""A multi-token spelled-number run is folded to one digit token only when the
back-end genuinely consumes the whole run.

``ovos_number_parser`` can greedily read only a *trailing* component of a run
and silently drop a leading magnitude: ``extract_number_nl("tweeduizend
vierentwintig")`` returns 24, dropping the 2000.  The fold used to stamp that
24 over the whole run, committing a confidently-wrong value with an empty
remainder.  The consumption guard in ``_fold_run`` cuts such a run instead --
the un-consumed magnitude survives as an honest, non-empty remainder -- while
leaving every genuinely-consumed run (including the implied-multiplier
"hundred twenty three") folded exactly as before.
"""
from chronologia.extract.numfold import fold_en
from chronologia.extract.numfold_germanic import fold_nl
from chronologia.extract.tokenizer import Tokenizer, TokenizerModes


def _toks(text):
    return Tokenizer(TokenizerModes(dotted_date=True, ordinal_dot=True)).tokenize(text)


def _values(out):
    return [t.value for t in out if t.is_number]


def _numtexts(out):
    return [t.text for t in out if t.is_number]


# --- the defect: a dropped leading magnitude must never become the value -----

def test_nl_dropped_thousand_is_not_silently_folded_to_the_remainder():
    out = fold_nl(_toks("tweeduizend vierentwintig dagen"))
    vals = _values(out)
    # never the confidently-wrong 24 with an empty remainder
    assert vals != [24], f"leading 2000 was silently dropped: {vals}"
    # honest partial: the 2000 magnitude survives as its own token
    assert 2000 in vals, f"un-consumed magnitude vanished: {vals}"


# --- must NOT regress: genuinely-consumed runs stay folded --------------------

def test_en_implied_multiplier_hundred_twenty_three_stays_123():
    out = fold_en(_toks("one hundred twenty three days"))
    assert 123 in _values(out)


def test_en_two_hundred_fifty_stays_250():
    out = fold_en(_toks("two hundred fifty days"))
    assert 250 in _values(out)


def test_en_twenty_three_stays_23():
    out = fold_en(_toks("twenty three days"))
    assert 23 in _values(out)
