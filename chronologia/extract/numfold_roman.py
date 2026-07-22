"""Context-gated Roman-numeral fold (century / millennium / year ordinals).

Everyday Romance orthography writes an ordinal century in Roman numerals --
``século XII`` (pt), ``siglo XII`` (es), ``secolo XII`` (it), ``XIIe siècle``
(fr), ``the XII century`` (en) -- and an explicit year likewise (``anno
MMXX``, ``year MMXX``).  This pass turns such a Roman-numeral token into the
plain digit token the ``ORD`` / ``GYEAR`` slots already bind, so no new
resolver logic is needed: the numeral becomes a number and the existing
scoped-ordinal / year constructions do the rest.

**The homograph guard is the whole point.**  A bare ``I``/``V``/``X``/``C``/
``D``/``M`` -- or a word that merely looks Roman (``mix``, ``dix``, ``vi``,
``v``) -- must *never* bind a numeric value on its own.  Two independent
conditions gate every fold:

1. *Orthographic*: the token's **original surface is upper-case** and, after
   stripping a Romance ordinal suffix (French ``XIIe``/``Ier``), is a strictly
   well-formed Roman numeral per :func:`chronologia.roman.roman_to_int`.  This
   alone drops every lower-case confusable (``dix ans``, ``vi o filme``, ``mix
   it up``).
2. *Contextual*: an immediately adjacent token is a **century/millennium unit**
   (either side: ``século XII`` or ``XII century``) or the token directly
   **follows a year marker** (``year MMXX``, ``anno MMXX``).  This drops a
   capitalised confusable in the wrong place (``V for Vendetta`` -- ``V`` has
   no gating neighbour).

The pass is spec-aware (it reads the language's own century/millennium and
year-marker vocabulary), so it runs from the shared pre-match pipeline rather
than the per-language ``hook``.
"""
from __future__ import annotations

import re
from dataclasses import replace
from typing import Set, Tuple

from chronologia.extract.model import LangSpec, Token
from chronologia.roman import roman_to_int

# a Romance/English ordinal suffix riding on a Roman numeral: French "XIIe",
# "XIIème", "Ier"/"Iere", Portuguese/Italian "XIIº"/"XIIª", the plain "e".
# Stripped case-insensitively from the tail before the numeral is validated.
_ORD_SUFFIX = re.compile(r"(?:eme|ème|ere|er|re|es|e|os|as|os|º|ª|°)$", re.IGNORECASE)


def _century_millennium_surfaces(spec: LangSpec) -> Set[str]:
    """Surface forms of the century and millennium scope units."""
    return {s for s, kind in spec.scope_units.items()
            if kind in ("century", "millennium")}


def _roman_core(raw: str) -> str:
    """The numeral part of a surface, French/Romance ordinal suffix removed."""
    core = _ORD_SUFFIX.sub("", raw)
    return core or raw


def _candidate_value(tok: Token, text: str):
    """The int a token denotes as an upper-case Roman numeral, or ``None``.

    Requires the ORIGINAL surface (recovered case-preserved from ``text`` via
    the token's char extent -- the tokenizer lower-cases everything) to be
    upper-case: the first half of the homograph guard, so a lower-case
    ``vi``/``dix``/``mix`` never qualifies.
    """
    if tok.is_number or tok.char_start is None or tok.char_end is None:
        return None
    surface = text[tok.char_start:tok.char_end]
    core = _roman_core(surface)
    if not core or not core.isupper():
        return None
    if any(ch not in "IVXLCDM" for ch in core):
        return None
    return roman_to_int(core)


def fold_roman_numerals(tokens: Tuple[Token, ...], spec: LangSpec, text: str
                        ) -> Tuple[Token, ...]:
    """Fold context-gated Roman-numeral tokens to digit tokens."""
    units = _century_millennium_surfaces(spec)
    year_markers = spec.connectors.get("year_word", frozenset())
    anchors = spec.roman_anchors
    out = []
    for i, tok in enumerate(tokens):
        value = _candidate_value(tok, text)
        if value is None:
            out.append(tok)
            continue
        prev_text = tokens[i - 1].text if i > 0 else None
        next_text = tokens[i + 1].text if i + 1 < len(tokens) else None
        # gates: a century/millennium unit on either side ("século XII" /
        # "XII century"), a year marker just before ("anno MMXX"), or a Roman
        # calendar anchor just after -- the classical a.d. count ("ad III
        # kalends", "ante diem III kalendas").
        gated = (prev_text in units or next_text in units
                 or prev_text in year_markers or next_text in anchors)
        if not gated:
            out.append(tok)
            continue
        out.append(replace(tok, text=str(value), raw=str(value),
                           is_number=True, value=value))
    return tuple(replace(t, index=i) for i, t in enumerate(out))
