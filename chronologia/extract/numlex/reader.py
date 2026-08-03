"""The generic additive-multiplicative run reader.

One composition grammar, parameterised by a :class:`NumberLexicon`, replaces
``extract_number_<lang>`` for every language as they migrate off
``ovos-number-parser``.  Only surfaces vary per locale; the algorithm below
is family-shared: sum bare units, let a TEN take a trailing unit, let a
HUNDRED/SCALE word multiply the group accumulated so far, and let a SCALE
word close the group into a running total (English "two thousand three
hundred" -> group 3 [made 300 by "hundred"] closes onto 2*1000 = 2300).
"""
from __future__ import annotations

from typing import Iterable, Optional, Union

from chronologia.extract.numlex.lexicon import NumberLexicon
from chronologia.extract.numlex.roles import Role

Number = Union[int, float]

_SCALE_ROLES = (Role.HUNDRED, Role.SCALE)


def _structural_class(role: Role, tags) -> str:
    """Which additive class a token behaves as, role or ordinal-tag alike."""
    if role in _SCALE_ROLES or "scale" in tags:
        return "scale"
    if role is Role.TEN or "ten" in tags:
        return "ten"
    return "unit"


def read_run(tokens: Iterable[str], lexicon: NumberLexicon, *,
             ordinals: bool = False) -> Optional[Number]:
    """Read the value of a joined run of number-word surfaces.

    ``tokens`` is the run's words, already split (no punctuation, no
    connectors -- those are stripped by the caller before this is reached,
    matching the ``joiner_in_text=False`` English fold).  Returns an
    ``int`` when the result is a whole number, a ``float`` for a fractional
    or ordinal-scale reading (matching ``extract_number_<lang>``'s
    contract), and ``None`` when the run is not a well-formed composed
    number -- a digit run mixed with an unrecognised surface, an empty run,
    or a run containing a :attr:`Role.PARTICLE` surface ("dozen", "score")
    that carries no value of its own.
    """
    words = list(tokens)
    if not words:
        return None

    total = 0
    current = 0
    used = False
    fraction = None

    for word in words:
        if word.isdigit():
            current += int(word)
            used = True
            continue

        entries = lexicon.get(word)
        if not entries:
            return None
        entry = entries[0]

        is_ordinal = entry.role is Role.ORDINAL or "ordinal" in entry.tags
        if is_ordinal and not ordinals:
            return None

        if entry.role is Role.FRACTION:
            if entry.value is None:
                return None
            fraction = entry.value
            used = True
            continue

        if entry.role in (Role.CONNECTOR, Role.PARTICLE, Role.MULTIPLIER):
            if entry.value is None:
                # a known surface with no value of its own ("dozen",
                # "score", a bare join word): the run cannot compose.
                return None
            current += entry.value
            used = True
            continue

        if entry.value is None:
            return None

        cls = _structural_class(entry.role, entry.tags)
        if cls == "scale":
            current = entry.value if current == 0 else current * entry.value
            total += current
            current = 0
        else:
            current += entry.value
        used = True

    if not used:
        return None

    result = total + current
    if fraction is not None:
        result = result + fraction if result else fraction

    if isinstance(result, float) or not float(result).is_integer():
        return float(result)
    return int(result)
