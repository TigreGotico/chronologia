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
    # small demonstrative, ATTESTED-ONLY set of rulers, in THREE parallel
    # chronology variants -- "high", "middle" (conventional) and "low" --
    # the standard three-way split scholarship uses for this period because
    # the absolute anchor (the Sothic/heliacal-rise observation tied to
    # Amenhotep I's reign) is itself disputed by ~25 years depending on the
    # observation site assumed, and the dispute propagates down the whole
    # dynastic sequence. BC years are astronomical (63 BC == -62), matching
    # the ``consuls`` convention above; accession day/month are not attested
    # for these rulers, so each segment starts 1 January proleptic
    # Julian/Gregorian of its accession year (a documented simplification,
    # as for ``consuls``).
    #
    # Every accession year below is a value **directly quoted, with an
    # explicit chronology label, from a per-ruler Wikipedia article**
    # (fetched and quoted verbatim during construction of this dataset; see
    # each ruler's own article for the primary citation trail). No accession
    # year here is interpolated, averaged, or otherwise derived -- an
    # earlier draft of this dataset filled gaps by interpolating between an
    # attested high and low figure, which silently produced a
    # chronologically-impossible ordering (Horemheb before Tutankhamun).
    # This dataset drops that approach entirely: a ruler appears in a
    # variant's segment list **only** where that variant's figure for them
    # is directly attested, and is simply absent from a variant otherwise --
    # so the three sequences below have DIFFERENT ruler subsets and
    # different lengths, and every gap is called out in a comment rather
    # than silently papered over.
    #
    # Per-ruler sources (all en.wikipedia.org, fetched and quoted directly):
    #   - "Ahmose I": infobox labels 1570-1546 BC "(HC)" i.e. High
    #     Chronology explicitly; no comparably labeled Low figure found ->
    #     high only.
    #   - "Amenhotep I": infobox "1545-1526 BC (high chr.)" / "1525-1506 BC
    #     (low chr.)" -> both high and low attested.
    #   - "Thutmose I": main text names both "low chronology" (1506-1493 BC)
    #     and "high chronology" (1526-1513 BC) explicitly -> both attested.
    #   - "Thutmose III": main text names "Low Chronology" (1479-1425 BC,
    #     "the conventional Egyptian chronology... since the 1960s") and
    #     "High Chronology of Egypt" (1504-1450 BC) explicitly -> both
    #     attested.
    #   - "Amenhotep II": main text: "dating his accession to either 1427 BC
    #     in the low chronology, or in 1452 BC in the high chronology" ->
    #     both attested.
    #   - "Amenhotep III": infobox/main text name only a "Low Chronology"
    #     figure (1391-1353 BC); no comparably labeled High figure found ->
    #     low only.
    #   - Akhenaten, Tutankhamun: no article gives a chronology-labeled
    #     high/middle/low split (only a single unlabeled conventional
    #     range each) -> DROPPED from this dataset entirely; the gap they
    #     leave (between Amenhotep III and Ay, in every variant) is
    #     intentional, not an oversight.
    #   - "Ay (pharaoh)": main text gives three unlabeled reign options
    #     ("1323 and 1319 BC, 1327-1323 BC, or 1310-1306 BC"); only the
    #     "1323-1319 BC" option is used here, because it alone tiles
    #     exactly against Horemheb's directly-attested "(low chr.)" start
    #     of 1319 BC with no gap or overlap -- the other two options are
    #     left out rather than guessed into a bucket, per the ordering
    #     failure above -> low only.
    #   - "Horemheb": infobox "1319-1292 BC (low chr.)" explicitly -> low
    #     only.
    #   - "Ramesses II": the one ruler with all three named variants
    #     attested across sources -- 1304 BC (High), 1290 BC (Middle), and
    #     1279 BC (Low, "which most Egyptologists believe to be 31 May 1279
    #     BC" per the article's own text) -> the anchor of this dataset.
    #
    # Uncertainty: the High/Low bracket runs +/-13 to +/-25 years per
    # accession across the attested rulers above (widest for Thutmose III,
    # narrowest for Ramesses II), consistent with the cited sources'
    # framing of the dispute as narrowing over the course of the New
    # Kingdom. This composes with the suffixed-variant convention used
    # elsewhere in this registry (e.g. a caller distinguishing
    # ``egyptian_high``/``egyptian_middle``/``egyptian_low`` the same way
    # ``nengo``/``consuls`` are distinguished by key).
    "egyptian_high": RegnalSequence("egyptian_high", (
        ("ahmose_i", _jdn(-1569, 1, 1)),        # 1570 BC
        ("amenhotep_i", _jdn(-1544, 1, 1)),     # 1545 BC
        ("thutmose_i", _jdn(-1525, 1, 1)),      # 1526 BC
        ("thutmose_iii", _jdn(-1503, 1, 1)),    # 1504 BC
        ("amenhotep_ii", _jdn(-1451, 1, 1)),    # 1452 BC
        # gap: Amenhotep III, Akhenaten, Tutankhamun, Ay, Horemheb have no
        # attested High figure in the sources checked.
        ("ramesses_ii", _jdn(-1303, 1, 1)),     # 1304 BC
    )),
    "egyptian_middle": RegnalSequence("egyptian_middle", (
        # gap: no ruler before Ramesses II has an attested Middle figure in
        # the sources checked; "Middle" as a named variant is specific to
        # the Ramesses II/Nineteenth-Dynasty debate in the sources found.
        ("ramesses_ii", _jdn(-1289, 1, 1)),     # 1290 BC
    )),
    "egyptian_low": RegnalSequence("egyptian_low", (
        ("amenhotep_i", _jdn(-1524, 1, 1)),     # 1525 BC
        ("thutmose_i", _jdn(-1505, 1, 1)),      # 1506 BC
        ("thutmose_iii", _jdn(-1478, 1, 1)),    # 1479 BC
        ("amenhotep_ii", _jdn(-1426, 1, 1)),    # 1427 BC
        ("amenhotep_iii", _jdn(-1390, 1, 1)),   # 1391 BC
        # gap: Ahmose I has no attested Low figure; Akhenaten and
        # Tutankhamun have no chronology-labeled figure at all (dropped
        # dataset-wide, see above).
        ("ay", _jdn(-1322, 1, 1)),              # 1323 BC
        ("horemheb", _jdn(-1318, 1, 1)),        # 1319 BC
        ("ramesses_ii", _jdn(-1278, 1, 1)),     # 1279 BC
    )),
}
