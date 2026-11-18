# -*- coding: utf-8 -*-
"""A multi-token spelled-number run is folded to one digit token only when the
back-end genuinely consumes the whole run.  Dutch reads its runs through numtag;
the tests below keep the rows that guard against a dropped leading magnitude.

``ovos_number_parser`` can greedily read only a *trailing* component of a run
and silently drop a leading magnitude: ``extract_number_nl("tweehonderd
vijftig")`` returns 50, dropping the 200.  The fold used to stamp that
50 over the whole run, committing a confidently-wrong value with an empty
remainder.  The consumption guard in ``_fold_run`` cuts such a run instead --
the un-consumed magnitude survives as an honest, non-empty remainder -- while
leaving every genuinely-consumed run (including the implied-multiplier
"hundred twenty three") folded exactly as before.
"""
from chronologia.extract.loader import load_lang_spec
from chronologia.extract.pipeline import prematch_tokens
from chronologia.extract.tokenizer import Tokenizer, TokenizerModes


def _toks(text):
    return Tokenizer(TokenizerModes(dotted_date=True, ordinal_dot=True)).tokenize(text)


def _en(text):
    """English reads its numbers through numtag, on the pipeline's layer."""
    return prematch_tokens(text, load_lang_spec("en"))


def _nl(text):
    """Dutch reads its numbers through numtag, on the pipeline's layer."""
    return prematch_tokens(text, load_lang_spec("nl"))


def _values(out):
    return [t.value for t in out if t.is_number]


def _numtexts(out):
    return [t.text for t in out if t.is_number]


# --- the defect: a dropped leading magnitude must never become the value -----

def test_nl_thousand_with_space_is_folded_whole():
    # "na duizend een spatie" (Taaladvies): "tweeduizend vierentwintig" is the
    # written form of 2024 and the back-end consumes the whole run.
    out = _nl("tweeduizend vierentwintig dagen")
    assert _values(out) == [2024]
    assert [t.text for t in out if not t.is_number] == ["dagen"]


def test_nl_split_hundred_is_read_whole():
    # the former back-end read only the trailing 50 of "tweehonderd vijftig";
    # numtag reads the run as 200 + 50
    out = _nl("tweehonderd vijftig dagen")
    assert _values(out) == [250], f"run not read whole: {_values(out)}"


# --- must NOT regress: genuinely-consumed runs stay folded --------------------

def test_en_implied_multiplier_hundred_twenty_three_stays_123():
    out = _en("one hundred twenty three days")
    assert 123 in _values(out)


def test_en_two_hundred_fifty_stays_250():
    out = _en("two hundred fifty days")
    assert 250 in _values(out)


def test_en_twenty_three_stays_23():
    out = _en("twenty three days")
    assert 23 in _values(out)
