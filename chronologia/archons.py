"""Athenian eponymous archons: the eponymous-year dating of classical Athens.

Classical Athens named each civil year after its *eponymous archon* -- "in the
archonship of Eucleides" is 403/402 BC, the year Athens restored the democracy
and adopted the Ionic alphabet.  The archon-year ran from around midsummer (the
month Hekatombaion, ~July) to the next midsummer, so it straddles two of our BC
years; we model it as the half-open span ``[1 Jul opening, 1 Jul next)`` on the
proleptic Gregorian axis, the same midsummer convention the Olympiad era uses.

Only securely-dated, unambiguously-named archons are wired -- an eponymous
archon is *attested*, never interpolated, and a name held in two different
years (Callias: 456/455 and 412/411) is left out rather than bound to a guess.
This is a small, demonstrative subset, not the full fasti.

Source: ``attic_archons.tab`` (see its header for the primary source).
"""
from __future__ import annotations

import os
from typing import Dict, Tuple

from chronologia.astrodate import AstroDate

_DATA = os.path.join(os.path.dirname(__file__), "calendar_data",
                     "attic_archons.tab")


def _load() -> Dict[str, Tuple[AstroDate, AstroDate]]:
    spans: Dict[str, Tuple[AstroDate, AstroDate]] = {}
    with open(_DATA, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, bc_year, _name = line.split(None, 2)
            # BC year Y -> astronomical opening year -(Y-1); the archon-year
            # opens ~midsummer and runs to the next midsummer.
            opening = -(int(bc_year) - 1)
            spans[key] = (AstroDate(opening, 7, 1), AstroDate(opening + 1, 7, 1))
    return spans


#: archon key -> ``(start, end)`` proleptic-Gregorian span of that archon-year.
ARCHONS: Dict[str, Tuple[AstroDate, AstroDate]] = _load()
