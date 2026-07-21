"""Regnal sequences: era numberings attached to a *succession of reigns*.

The fourth registry kind alongside counts, calendars and eras.  A
:class:`RegnalSequence` is an ordered list of named segments, each starting
on a Julian Day Number; a segment ends exactly where its successor begins,
so the reigns tile with no gap, and the final segment is open-ended.
"Reiwa 7" or "the 3rd year of Reiwa" resolves to the Gregorian year span
that regnal year occupies inside its segment.

Year-count convention (documented, per the Japanese case):

From Meiji 6 (1873) Japan adopted the Gregorian calendar and counts a
regnal year as a **Gregorian calendar year** incrementing on 1 January:
regnal year 1 is the (partial) calendar year of accession, year N is
Gregorian year ``accession_year + N - 1``.  The span is clamped to the
segment, so the accession year is bounded below by the accession date
(Reiwa 1 = 2019-05-01..2020-01-01) and the final year of a closed segment
is bounded above by the successor's accession (Meiji 45 =
2019... -> 1912-01-01..1912-07-30).  Before 1873 Japan used a lunisolar
calendar, so the clean Gregorian-year identity holds only from Meiji 6 on;
earlier Meiji years are approximate under this arithmetic model.

Source: ``japanese_nengo_reference.html`` (accession dates of the modern
nengō).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from chronologia.astrodate import AstroDate
from chronologia.calendars import gregorian_to_jdn, jdn_to_gregorian


@dataclass(frozen=True)
class RegnalSequence:
    """An ordered succession of named reign segments.

    ``segments`` are ``(name, start_jdn)`` in chronological order; segment i
    runs ``[start_jdn_i, start_jdn_{i+1})`` and the last segment is open.
    """
    key: str
    segments: Tuple[Tuple[str, int], ...]

    def _bounds(self, name: str) -> Tuple[AstroDate, Optional[AstroDate]]:
        for i, (segname, start_jdn) in enumerate(self.segments):
            if segname != name:
                continue
            start = AstroDate(*jdn_to_gregorian(start_jdn))
            end = (AstroDate(*jdn_to_gregorian(self.segments[i + 1][1]))
                   if i + 1 < len(self.segments) else None)
            return start, end
        raise KeyError(name)

    def year_span(self, name: str, n: int
                  ) -> Optional[Tuple[AstroDate, AstroDate]]:
        """Gregorian year span of regnal year ``n`` in segment ``name``.

        Returns ``None`` when the year does not exist in the segment (``n <
        1``, or a year past the successor's accession).
        """
        if n < 1:
            return None
        seg_start, seg_end = self._bounds(name)
        target = seg_start.year + n - 1
        year_start = AstroDate(target, 1, 1)
        year_end = AstroDate(target + 1, 1, 1)
        span_start = max(seg_start, year_start)
        span_end = year_end if seg_end is None else min(seg_end, year_end)
        if span_start >= span_end:
            return None
        return span_start, span_end


def _jdn(y, m, d):
    return gregorian_to_jdn(y, m, d)


#: Registered regnal sequences, keyed by the ``regnal_<key>_<segment>.voc``
#: filename convention that binds vocabulary to a segment.
REGNAL_SEQUENCES = {
    # Modern Japanese nengō, Meiji -> Reiwa (accession dates from
    # japanese_nengo_reference.html); Reiwa is open-ended.
    "nengo": RegnalSequence("nengo", (
        ("meiji", _jdn(1868, 10, 23)),
        ("taisho", _jdn(1912, 7, 30)),
        ("showa", _jdn(1926, 12, 25)),
        ("heisei", _jdn(1989, 1, 8)),
        ("reiwa", _jdn(2019, 5, 1)),
    )),
    # Roman consular fasti: eponymous years named by their annual consul pair,
    # each entering office on 1 January (proleptic Gregorian year label).  A
    # small demonstrative subset of well-attested pairs (BC years are
    # astronomical: 59 BC == -58); the full fasti are later data work.  Source:
    # roman_consular_fasti_reference.html.
    "consuls": RegnalSequence("consuls", (
        ("cicero_hybrida", _jdn(-62, 1, 1)),        # 63 BC
        ("caesar_bibulus", _jdn(-58, 1, 1)),        # 59 BC
        ("pompeius_crassus", _jdn(-54, 1, 1)),      # 55 BC
        ("sulpicius_marcellus", _jdn(-50, 1, 1)),   # 51 BC
        ("caesar_antonius", _jdn(-43, 1, 1)),       # 44 BC
        ("hirtius_pansa", _jdn(-42, 1, 1)),         # 43 BC
        ("augustus_agrippa", _jdn(-26, 1, 1)),      # 27 BC
        ("caesar_paullus", _jdn(1, 1, 1)),          # AD 1
        ("pompeius_appuleius", _jdn(14, 1, 1)),     # AD 14
        ("vespasian_titus", _jdn(70, 1, 1)),        # AD 70
        ("trajan_frontinus", _jdn(100, 1, 1)),      # AD 100
        ("severus_quintianus", _jdn(235, 1, 1)),    # AD 235
    )),
    # New Kingdom Egypt (Dynasty 18-19), Ahmose I through Ramesses II: a
    # small demonstrative set of ~10 well-attested rulers, in THREE parallel
    # chronology variants -- "high", "middle" (conventional) and "low" --
    # the standard three-way split scholarship uses for this period because
    # the absolute anchor (the Sothic/heliacal-rise observation tied to
    # Amenhotep I's reign) is itself disputed by ~25 years depending on the
    # observation site assumed, and the dispute propagates down the whole
    # dynastic sequence via the attested relative reign lengths.  BC years
    # are astronomical (63 BC == -62), matching the ``consuls`` convention
    # above; accession day/month are not attested for most of these rulers,
    # so each segment starts 1 January proleptic Julian/Gregorian of its
    # accession year (a documented simplification, as for ``consuls``).
    #
    # Source: Wikipedia's per-ruler chronology sections (a sourced mirror of
    # the scholarly high/middle/low debate -- see e.g. "Ramesses II",
    # "Seti I", "Thutmose III", "Amenhotep II/III", "Ahmose I", "Akhenaten",
    # "Tutankhamun", "Horemheb"), which is where each ruler's high and/or low
    # figure below is directly attested.  Ramesses II is the one ruler whose
    # three variants (1304 / 1290 / 1279 BC) are ALL directly and
    # consistently attested by name in the literature; that triple is the
    # anchor.  For rulers where only a high/low pair (or only a low figure)
    # is directly attested, the missing variant(s) are interpolated --
    # documented per-entry below -- rather than independently sourced, which
    # is the honest boundary of this small demonstrative dataset.
    #
    # Uncertainty: +/-10 to +/-25 years per accession, growing toward the
    # earlier rulers (Ahmose I) and narrowing toward Ramesses II, per the
    # cited sources.  This composes with the suffixed-variant convention
    # used elsewhere in this registry (e.g. a caller distinguishing
    # ``egyptian_high``/``egyptian_middle``/``egyptian_low`` the same way
    # ``nengo``/``consuls`` are distinguished by key).
    "egyptian_high": RegnalSequence("egyptian_high", (
        ("ahmose_i", _jdn(-1569, 1, 1)),        # 1570 BC, attested
        ("amenhotep_i", _jdn(-1544, 1, 1)),     # 1545 BC, attested
        ("thutmose_i", _jdn(-1525, 1, 1)),      # 1526 BC, attested
        ("thutmose_iii", _jdn(-1503, 1, 1)),    # 1504 BC, attested
        ("amenhotep_ii", _jdn(-1453, 1, 1)),    # 1454 BC, attested
        ("amenhotep_iii", _jdn(-1416, 1, 1)),   # 1417 BC, attested
        ("akhenaten", _jdn(-1378, 1, 1)),       # 1379 BC, interpolated
        ("tutankhamun", _jdn(-1340, 1, 1)),     # 1341 BC, attested
        ("horemheb", _jdn(-1343, 1, 1)),        # 1344 BC, interpolated
        ("ramesses_ii", _jdn(-1303, 1, 1)),     # 1304 BC, attested
    )),
    "egyptian_middle": RegnalSequence("egyptian_middle", (
        ("ahmose_i", _jdn(-1559, 1, 1)),        # 1560 BC, interpolated
        ("amenhotep_i", _jdn(-1534, 1, 1)),     # 1535 BC, interpolated
        ("thutmose_i", _jdn(-1515, 1, 1)),      # 1516 BC, interpolated
        ("thutmose_iii", _jdn(-1491, 1, 1)),    # 1492 BC, interpolated
        ("amenhotep_ii", _jdn(-1440, 1, 1)),    # 1441 BC, interpolated
        ("amenhotep_iii", _jdn(-1403, 1, 1)),   # 1404 BC, interpolated
        ("akhenaten", _jdn(-1365, 1, 1)),       # 1366 BC, interpolated
        ("tutankhamun", _jdn(-1335, 1, 1)),     # 1336 BC, interpolated
        ("horemheb", _jdn(-1331, 1, 1)),        # 1332 BC, interpolated
        ("ramesses_ii", _jdn(-1289, 1, 1)),     # 1290 BC, attested
    )),
    "egyptian_low": RegnalSequence("egyptian_low", (
        ("ahmose_i", _jdn(-1549, 1, 1)),        # 1550 BC, attested
        ("amenhotep_i", _jdn(-1524, 1, 1)),     # 1525 BC, attested
        ("thutmose_i", _jdn(-1505, 1, 1)),      # 1506 BC, attested
        ("thutmose_iii", _jdn(-1478, 1, 1)),    # 1479 BC, attested
        ("amenhotep_ii", _jdn(-1426, 1, 1)),    # 1427 BC, attested
        ("amenhotep_iii", _jdn(-1390, 1, 1)),   # 1391 BC, attested
        ("akhenaten", _jdn(-1352, 1, 1)),       # 1353 BC, attested
        ("tutankhamun", _jdn(-1331, 1, 1)),     # 1332 BC, attested
        ("horemheb", _jdn(-1318, 1, 1)),        # 1319 BC, attested
        ("ramesses_ii", _jdn(-1278, 1, 1)),     # 1279 BC, attested
    )),
}
