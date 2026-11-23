"""Day-part registry: named stretches *within* a civil day, resolved to spans.

A :class:`DayPart` binds a name for a portion of the day ("morning", "tarde")
to a start and end time of day, tagged with an optional ``lang`` (``None`` is
the global default) and a ``source``.  :func:`daypart_span` applies it to a
civil date and returns a :class:`DateSpan`.

A day-part is a convention and conventions differ: English splits the
post-noon day into *afternoon* and *evening*, Spanish runs one *tarde* across
both.  The boundaries are therefore data, tagged by language (``tarde`` is
Spanish in Madrid and Los Angeles alike), never engine logic.  ``region`` stays
as an alias of ``lang`` on :class:`DayPart`, :func:`lookup` and
:func:`daypart_span`.

Sources.  The per-language rows are transcribed from the Unicode CLDR Day
Period Rules (TR35, CLDR 47; the chart is in the papers library at
``standards/cldr47_day_period_rules.html``).  CLDR gives each period a start
time and lets the next row's start close it, so a band runs ``[own start, next
start)`` and the last row of the day closes at 24:00.  When one name holds both
the first row (00:00) and the last row, the rows are one midnight-crossing
band: Romanian ``noapte`` is ``[22:00, 05:00)``.  Where the names differ the
rows stay apart: Italian ``notte`` is the small hours ``[00:00, 06:00)``.

The default set (``lang=None``) is not CLDR.  It is chronologia's own English
convention, which departs from CLDR ``en`` at the morning start and in the
wrapping night:

============ =============== ==================
day-part     interval        note
============ =============== ==================
``morning``  ``[06:00, 12:00)``
``afternoon`` ``[12:00, 18:00)``
``evening``  ``[18:00, 21:00)``
``night``    ``[21:00, 06:00)`` crosses midnight
``noon``     ``[12:00, 12:01)`` minimal-width anchor
``midnight`` ``[00:00, 00:01)`` minimal-width anchor
============ =============== ==================

Languages that the deictic ``daypart_ref`` grammar reads ("this morning",
"yesterday evening") are collapsed into the four-band vocabulary ``morning``,
``afternoon``, ``evening``, ``night``.  A band whose only surface is multi-word
(Czech ``v noci``, Polish ``po południu``, Turkish ``öğleden sonra``) ships its
boundaries but no ``daypart_*.voc`` yet.  Bands English has no word for
(``Vormittag``, ``förmiddag``, ``migdia``) keep their own names.

:func:`lookup` falls back from a language to the global default: ``morning``
in ``es`` is the default morning, while ``tarde`` with no language raises.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone, tzinfo as _tzinfo
from typing import Dict, List, Optional, Tuple, Union

from chronologia.astrodate import (AstroDate, DateSpan, _fold_offsets,
                                   civil_add, resolve_wall_clock)
from chronologia.timelines import NeverExisted

#: One-minute minimal width for instant anchors (noon, midnight), matching the
#: point convention used elsewhere ("3 pm" == ``[15:00, 15:01)``).
_ANCHOR_WIDTH = timedelta(minutes=1)

#: CLDR release the per-language boundaries are transcribed from.
CLDR_VERSION = "47"


def _cldr(lang: str) -> str:
    """Citation string for a language's rows in the CLDR day-period chart."""
    return f"Unicode CLDR {CLDR_VERSION} Day Period Rules (locale {lang})"


#: The default set is chronologia's own English convention, not CLDR ``en``.
_CHRONOLOGIA_EN = "chronologia English day-part convention (see module docs)"
#: West Frisian has no CLDR rules; it takes the Dutch boundaries and Frisian
#: surfaces.
_FY_NL_SHARED = (
    "West Frisian shares the Netherlands day-period convention (no CLDR fy "
    "rules exist); boundaries from " + _cldr("nl") + ", surfaces from the "
    "Frysk Wurdboek (Fryske Akademy)")


class UnknownDayPartError(KeyError):
    """Neither a language entry nor the global default carries the name."""


@dataclass(frozen=True, slots=True)
class DayPart:
    """A named portion of the civil day, bound to a start/end time-of-day.

    :param name: the human-facing name ("morning", "tarde").
    :param start: the day-fraction time the part opens at (inclusive).
    :param end: the day-fraction time the part closes at (exclusive, half-open).
    :param lang: language tag (``"es"``) or ``None`` for the global default.
    :param source: the versioned authority the boundaries came from.
    :param crosses_midnight: ``True`` when the part wraps past 24:00 into the
        next civil day (``end <= start``), e.g. ``night`` ``[21:00, 06:00)``.
    :param follows_evening: ``True`` for a night band that opens at midnight
        but belongs to the evening before it: Russian "сегодня ночью" said in
        the afternoon is the coming night, so the night of a day named
        relative to the anchor is the band on the NEXT civil date.  The span
        API itself never shifts: a calendar date keeps its own small hours.

    ``start``/``end`` are times of day; :func:`daypart_span` anchors them to a
    date.
    """
    name: str
    start: time
    end: time
    lang: Optional[str]
    source: str
    crosses_midnight: bool
    follows_evening: bool = False

    def __post_init__(self):
        if not isinstance(self.start, time) or not isinstance(self.end, time):
            raise TypeError("DayPart start/end must be datetime.time")
        wraps = self.end <= self.start
        if wraps != self.crosses_midnight:
            raise ValueError(
                f"crosses_midnight={self.crosses_midnight} disagrees with "
                f"endpoints {self.start}..{self.end}; a part wraps iff "
                f"end <= start")

    @property
    def region(self) -> Optional[str]:
        """Deprecated spelling of :attr:`lang`."""
        return self.lang

    @property
    def key(self) -> str:
        """Registry key: the bare name (global) or ``name_lang``."""
        return self.name if self.lang is None \
            else f"{self.name}_{self.lang.lower()}"


def _p(name: str, start: Tuple[int, int], end: Tuple[int, int],
       lang: Optional[str], source: str) -> DayPart:
    s = time(*start)
    e = time(*end)
    return DayPart(name, s, e, lang, source, crosses_midnight=e <= s)


def _night_after_evening(name: str, end: Tuple[int, int], lang: str,
                          source: str) -> DayPart:
    """A small-hours night band ``[00:00, end)`` that names the night after
    the given date's evening."""
    return DayPart(name, time(0, 0), time(*end), lang, source,
                   crosses_midnight=False, follows_evening=True)


def _anchor(name: str, hm: Tuple[int, int], lang: Optional[str],
            source: str) -> DayPart:
    s = time(*hm)
    e = (datetime(2000, 1, 1, *hm) + _ANCHOR_WIDTH).time()
    return DayPart(name, s, e, lang, source, crosses_midnight=False)


_DEFAULTS: List[DayPart] = [
    _p("morning", (6, 0), (12, 0), None, _CHRONOLOGIA_EN),
    _p("afternoon", (12, 0), (18, 0), None, _CHRONOLOGIA_EN),
    _p("evening", (18, 0), (21, 0), None, _CHRONOLOGIA_EN),
    _p("night", (21, 0), (6, 0), None, _CHRONOLOGIA_EN),   # crosses midnight
    _anchor("noon", (12, 0), None, _CHRONOLOGIA_EN),
    _anchor("midnight", (0, 0), None, _CHRONOLOGIA_EN),
]

# Every row below is a mechanical transcription of that language's rows in the
# CLDR 47 day-period chart: each band runs from its own start time to the next
# row's start, the last row of the day closing at 24:00, and a name occupying
# both the first and last rows joined into one midnight-crossing band.  The
# names are the language's own words, ASCII-folded so they can be a registry
# key and a ``daypart_<key>.voc`` filename; the accented spellings live in the
# vocabulary files, which is where surfaces belong.
_LANGUAGES: List[DayPart] = [
    # es: one "tarde" covers English afternoon *and* early evening, and the
    # small hours have their own name English cannot say in one word.
    _p("madrugada", (0, 0), (6, 0), "es", _cldr("es")),
    _p("manana", (6, 0), (12, 0), "es", _cldr("es")),
    _p("tarde", (12, 0), (20, 0), "es", _cldr("es")),
    _p("noche", (20, 0), (0, 0), "es", _cldr("es")),
    # pt: the same four-way carve-up as Spanish, but tarde yields to noite an
    # hour earlier.  One locale serves European and Brazilian Portuguese alike;
    # the chart draws no distinction here and neither does this row.
    _p("madrugada", (0, 0), (6, 0), "pt", _cldr("pt")),
    _p("manha", (6, 0), (12, 0), "pt", _cldr("pt")),
    _p("tarde", (12, 0), (19, 0), "pt", _cldr("pt")),
    _p("noite", (19, 0), (0, 0), "pt", _cldr("pt")),
    # ca: six bands.  "migdia" is an hour-wide band around noon, not the
    # minute-wide noon instant, and "vespre" is an early-evening band Spanish
    # runs straight through.
    _p("matinada", (0, 0), (6, 0), "ca", _cldr("ca")),
    _p("mati", (6, 0), (12, 0), "ca", _cldr("ca")),
    _p("migdia", (12, 0), (13, 0), "ca", _cldr("ca")),
    _p("tarda", (13, 0), (19, 0), "ca", _cldr("ca")),
    _p("vespre", (19, 0), (21, 0), "ca", _cldr("ca")),
    _p("nit", (21, 0), (0, 0), "ca", _cldr("ca")),
    # gl: Galician "tarde" is the widest of the Romance afternoons, eight hours
    # running to nine at night.
    _p("madrugada", (0, 0), (6, 0), "gl", _cldr("gl")),
    _p("mana", (6, 0), (12, 0), "gl", _cldr("gl")),
    _p("mediodia", (12, 0), (13, 0), "gl", _cldr("gl")),
    _p("tarde", (13, 0), (21, 0), "gl", _cldr("gl")),
    _p("noite", (21, 0), (0, 0), "gl", _cldr("gl")),
    # fr: "matin" opens at 04:00, two hours before English morning, and "soir"
    # runs to midnight rather than yielding to a night band before it.
    _p("nuit", (0, 0), (4, 0), "fr", _cldr("fr")),
    _p("matin", (4, 0), (12, 0), "fr", _cldr("fr")),
    _p("apres_midi", (12, 0), (18, 0), "fr", _cldr("fr")),
    _p("soir", (18, 0), (0, 0), "fr", _cldr("fr")),
    # it: "notte" is the small hours, not the late evening; "sera" holds
    # 18:00 to midnight on its own.
    _p("notte", (0, 0), (6, 0), "it", _cldr("it")),
    _p("mattina", (6, 0), (12, 0), "it", _cldr("it")),
    _p("pomeriggio", (12, 0), (18, 0), "it", _cldr("it")),
    _p("sera", (18, 0), (0, 0), "it", _cldr("it")),
    # ro: the one language whose chart rows name the same band twice, at 00:00
    # and at 22:00; joined here into the single wrapping night it is.
    _p("noapte", (22, 0), (5, 0), "ro", _cldr("ro")),
    _p("dimineata", (5, 0), (12, 0), "ro", _cldr("ro")),
    _p("dupa_amiaza", (12, 0), (18, 0), "ro", _cldr("ro")),
    _p("seara", (18, 0), (22, 0), "ro", _cldr("ro")),
    # de: six bands and not one of them is English's afternoon.  "Mittag" is an
    # hour-wide band, "Vormittag" and "Nachmittag" split what English runs
    # together, and "Abend" reaches midnight.
    _p("nacht", (0, 0), (5, 0), "de", _cldr("de")),
    _p("morgen", (5, 0), (10, 0), "de", _cldr("de")),
    _p("vormittag", (10, 0), (12, 0), "de", _cldr("de")),
    _p("mittag", (12, 0), (13, 0), "de", _cldr("de")),
    _p("nachmittag", (13, 0), (18, 0), "de", _cldr("de")),
    _p("abend", (18, 0), (0, 0), "de", _cldr("de")),
    # nl: the same four shapes as English at the same hours until the evening,
    # where "avond" runs to midnight and "nacht" takes the small hours.
    _p("nacht", (0, 0), (6, 0), "nl", _cldr("nl")),
    _p("ochtend", (6, 0), (12, 0), "nl", _cldr("nl")),
    _p("middag", (12, 0), (18, 0), "nl", _cldr("nl")),
    _p("avond", (18, 0), (0, 0), "nl", _cldr("nl")),
    # fy (West Frisian): CLDR ships no fy day-period rules, but West Frisian is
    # co-official in Fryslan (Netherlands) and follows the same clock-of-day
    # convention as Dutch, so the boundaries are nl's; the surfaces are Frisian
    # (Frysk Wurdboek, Fryske Akademy).  Band names are ASCII (as elsewhere);
    # the Frisian surfaces carry the diacritics in the .voc files.
    _p("nacht", (0, 0), (6, 0), "fy", _FY_NL_SHARED),
    _p("moarns", (6, 0), (12, 0), "fy", _FY_NL_SHARED),
    _p("middeis", (12, 0), (18, 0), "fy", _FY_NL_SHARED),
    _p("joun", (18, 0), (0, 0), "fy", _FY_NL_SHARED),
    # sv/da/nb/nn: the Nordic five-band day, with a short "morgon" and a
    # separate late-morning band before noon.  Swedish and Danish open the
    # morning at 05:00; Norwegian at 06:00.
    _p("natt", (0, 0), (5, 0), "sv", _cldr("sv")),
    _p("morgon", (5, 0), (10, 0), "sv", _cldr("sv")),
    _p("formiddag", (10, 0), (12, 0), "sv", _cldr("sv")),
    _p("eftermiddag", (12, 0), (18, 0), "sv", _cldr("sv")),
    _p("kvall", (18, 0), (0, 0), "sv", _cldr("sv")),
    _p("nat", (0, 0), (5, 0), "da", _cldr("da")),
    _p("morgen", (5, 0), (10, 0), "da", _cldr("da")),
    _p("formiddag", (10, 0), (12, 0), "da", _cldr("da")),
    _p("eftermiddag", (12, 0), (18, 0), "da", _cldr("da")),
    _p("aften", (18, 0), (0, 0), "da", _cldr("da")),
    # nb/nn take their boundaries from the chart's Norwegian ("no") rows, which
    # carry the day-period codes both written standards share; the words differ
    # between them and are supplied per standard.
    _p("natt", (0, 0), (6, 0), "nb", _cldr("no")),
    _p("morgen", (6, 0), (10, 0), "nb", _cldr("no")),
    _p("formiddag", (10, 0), (12, 0), "nb", _cldr("no")),
    _p("ettermiddag", (12, 0), (18, 0), "nb", _cldr("no")),
    _p("kveld", (18, 0), (0, 0), "nb", _cldr("no")),
    _p("natt", (0, 0), (6, 0), "nn", _cldr("no")),
    _p("morgon", (6, 0), (10, 0), "nn", _cldr("no")),
    _p("foremiddag", (10, 0), (12, 0), "nn", _cldr("no")),
    _p("ettermiddag", (12, 0), (18, 0), "nn", _cldr("no")),
    _p("kveld", (18, 0), (0, 0), "nn", _cldr("no")),
    # ru: the four-band Russian day.  "вечер" runs all the way to midnight and
    # "ночь" is the small hours (00:00-04:00), not a midnight-crosser -- the
    # same Abend/Nacht shape German draws, with the morning opening two hours
    # before English at 04:00.
    # A speaker names that small-hours band from the day before it: "ночь"
    # is "Часть суток от захода до восхода солнца, от вечера до утра"
    # (gramota.ru, s.v. ночь), so "сегодня ночью" said at 13:04 is the coming
    # night and "завтра ночью" is the night after tomorrow evening.
    _night_after_evening("noch", (4, 0), "ru", _cldr("ru")),
    _p("utro", (4, 0), (12, 0), "ru", _cldr("ru")),
    _p("den", (12, 0), (18, 0), "ru", _cldr("ru")),
    _p("vecher", (18, 0), (0, 0), "ru", _cldr("ru")),
    # ------------------------------------------------------------------
    # CLDR 46/47 day-period bands for 18 further locales, each a mechanical
    # transcription of that locale's CLDR rows collapsed into chronologia's
    # four-band model: morning1+morning2 -> morning, afternoon1/2 -> afternoon,
    # evening1 -> evening, night1(+night2) -> night (joined into one
    # midnight-crossing band where the chart splits it at 00:00).  The band
    # boundaries are always shipped even where no single-token deictic surface
    # exists for a band (a band with a multi-word surface -- Czech "v noci",
    # Polish "po poludniu" -- carries no ``daypart_*.voc`` yet).
    # uk: evening runs to midnight, night is the small hours (like ru).
    _p("morning", (4, 0), (12, 0), "uk", _cldr("uk")),
    _p("afternoon", (12, 0), (18, 0), "uk", _cldr("uk")),
    _p("evening", (18, 0), (0, 0), "uk", _cldr("uk")),
    # "ніч" is "Частина доби від заходу до сходу сонця, з вечора до ранку"
    # (СУМ-11, s.v. ніч), so "сьогодні вночі" is the coming night, as in ru.
    _night_after_evening("night", (4, 0), "uk", _cldr("uk")),
    # hr
    _p("morning", (4, 0), (12, 0), "hr", _cldr("hr")),
    _p("afternoon", (12, 0), (18, 0), "hr", _cldr("hr")),
    _p("evening", (18, 0), (21, 0), "hr", _cldr("hr")),
    _p("night", (21, 0), (4, 0), "hr", _cldr("hr")),
    # sr: the chart's rows land on the same clock hours as chronologia's own
    # English default (06/12/18/21), unlike hr's morning opening two hours
    # earlier -- a coincidence of the source, not a shortcut taken here.
    _p("morning", (6, 0), (12, 0), "sr", _cldr("sr")),
    _p("afternoon", (12, 0), (18, 0), "sr", _cldr("sr")),
    _p("evening", (18, 0), (21, 0), "sr", _cldr("sr")),
    _p("night", (21, 0), (6, 0), "sr", _cldr("sr")),
    # sl
    _p("morning", (6, 0), (12, 0), "sl", _cldr("sl")),
    _p("afternoon", (12, 0), (18, 0), "sl", _cldr("sl")),
    _p("evening", (18, 0), (22, 0), "sl", _cldr("sl")),
    _p("night", (22, 0), (6, 0), "sl", _cldr("sl")),
    # cs (night = "v noci", multi-word: band shipped, no voc)
    _p("morning", (4, 0), (12, 0), "cs", _cldr("cs")),
    _p("afternoon", (12, 0), (18, 0), "cs", _cldr("cs")),
    _p("evening", (18, 0), (22, 0), "cs", _cldr("cs")),
    _p("night", (22, 0), (4, 0), "cs", _cldr("cs")),
    # sk (night = "v noci", multi-word: band shipped, no voc)
    _p("morning", (4, 0), (12, 0), "sk", _cldr("sk")),
    _p("afternoon", (12, 0), (18, 0), "sk", _cldr("sk")),
    _p("evening", (18, 0), (22, 0), "sk", _cldr("sk")),
    _p("night", (22, 0), (4, 0), "sk", _cldr("sk")),
    # hu: reggel+delelott -> morning, ejjel+hajnal -> night (wraps to dawn).
    _p("morning", (6, 0), (12, 0), "hu", _cldr("hu")),
    _p("afternoon", (12, 0), (18, 0), "hu", _cldr("hu")),
    _p("evening", (18, 0), (21, 0), "hu", _cldr("hu")),
    _p("night", (21, 0), (6, 0), "hu", _cldr("hu")),
    # bg: the long morning runs to 14:00.
    _p("morning", (4, 0), (14, 0), "bg", _cldr("bg")),
    _p("afternoon", (14, 0), (18, 0), "bg", _cldr("bg")),
    _p("evening", (18, 0), (22, 0), "bg", _cldr("bg")),
    _p("night", (22, 0), (4, 0), "bg", _cldr("bg")),
    # mk: five bands, kept under their own names rather than collapsed, because
    # Macedonian splits the forenoon the way German does -- претпладне is the
    # two hours before noon and наутро the six before that -- so a single
    # "morning" would answer 04:00-12:00 for a word that means 10:00-12:00.
    # The noon and midnight points CLDR also lists are the global anchors, and
    # ship as clock landmarks (напладне, полноќ) rather than as bands.
    _p("nokje", (0, 0), (4, 0), "mk", _cldr("mk")),
    _p("nautro", (4, 0), (10, 0), "mk", _cldr("mk")),
    _p("pretpladne", (10, 0), (12, 0), "mk", _cldr("mk")),
    _p("popladne", (12, 0), (18, 0), "mk", _cldr("mk")),
    _p("navecher", (18, 0), (0, 0), "mk", _cldr("mk")),
    # sw: five bands, kept under their own names rather than collapsed, for the
    # same reason Macedonian's are -- alfajiri is the three hours before
    # sunrise and asubuhi the five after it, so a single "morning" spanning
    # both would answer 04:00-12:00 for a word that means 07:00-12:00.  The
    # afternoon closes at 16:00 and the evening at 19:00, so the night is the
    # long band from 19:00 round to dawn.  The noon and midnight points CLDR
    # also lists are spelled "saa sita za mchana" and "saa sita za usiku" --
    # sunrise-anchored clock readings -- and are NOT shipped as landmarks; see
    # the Swahili clock refusal in locale/sw/unit_hour.voc.
    _p("usiku", (19, 0), (4, 0), "sw", _cldr("sw")),
    _p("alfajiri", (4, 0), (7, 0), "sw", _cldr("sw")),
    _p("asubuhi", (7, 0), (12, 0), "sw", _cldr("sw")),
    _p("mchana", (12, 0), (16, 0), "sw", _cldr("sw")),
    _p("jioni", (16, 0), (19, 0), "sw", _cldr("sw")),
    # pl (afternoon "po poludniu" and night "w nocy" are multi-word: bands
    # shipped, no voc; morning "rano" and evening "wieczorem" carry surfaces).
    _p("morning", (6, 0), (12, 0), "pl", _cldr("pl")),
    _p("afternoon", (12, 0), (18, 0), "pl", _cldr("pl")),
    _p("evening", (18, 0), (21, 0), "pl", _cldr("pl")),
    _p("night", (21, 0), (6, 0), "pl", _cldr("pl")),
    # ko: five bands, kept under their own names rather than collapsed into an
    # English-shaped four, because Korean cuts the forenoon in two -- 아침 is
    # the three hours before the working day and 오전 the six after them, so a
    # single "morning" would answer 03:00-12:00 for a word that means
    # 06:00-12:00.  오전 and 오후 do double duty: the same two words are the
    # am/pm markers of a clock reading and the names of these bands.  The noon
    # and midnight points CLDR also lists (정오, 자정) ship as clock landmarks
    # rather than bands.
    _p("achim", (3, 0), (6, 0), "ko", _cldr("ko")),
    _p("ojeon", (6, 0), (12, 0), "ko", _cldr("ko")),
    _p("ohu", (12, 0), (18, 0), "ko", _cldr("ko")),
    _p("jeonyeok", (18, 0), (21, 0), "ko", _cldr("ko")),
    _p("bam", (21, 0), (3, 0), "ko", _cldr("ko")),
    # hi: the morning opens at 04:00, the afternoon closes at 16:00 and the
    # evening at 20:00, so the night is the long band from 20:00 round to 04:00.
    _p("morning", (4, 0), (12, 0), "hi", _cldr("hi")),
    _p("afternoon", (12, 0), (16, 0), "hi", _cldr("hi")),
    _p("evening", (16, 0), (20, 0), "hi", _cldr("hi")),
    _p("night", (20, 0), (4, 0), "hi", _cldr("hi")),
    # is: same shape as lt -- the evening runs to midnight and the night is
    # the small hours -- and CLDR lists the two locales under the same rules.
    _p("morning", (6, 0), (12, 0), "is", _cldr("is")),
    _p("afternoon", (12, 0), (18, 0), "is", _cldr("is")),
    _p("evening", (18, 0), (0, 0), "is", _cldr("is")),
    _p("night", (0, 0), (6, 0), "is", _cldr("is")),
    # lt: the evening runs to midnight and the night is the small hours.
    _p("morning", (6, 0), (12, 0), "lt", _cldr("lt")),
    _p("afternoon", (12, 0), (18, 0), "lt", _cldr("lt")),
    _p("evening", (18, 0), (0, 0), "lt", _cldr("lt")),
    _p("night", (0, 0), (6, 0), "lt", _cldr("lt")),
    # lv: the evening runs to 23:00 and the night is the small hours from
    # there, one hour earlier on both edges than the Lithuanian shape.
    _p("morning", (6, 0), (12, 0), "lv", _cldr("lv")),
    _p("afternoon", (12, 0), (18, 0), "lv", _cldr("lv")),
    _p("evening", (18, 0), (23, 0), "lv", _cldr("lv")),
    _p("night", (23, 0), (6, 0), "lv", _cldr("lv")),
    # sq: CLDR draws two morning bands (04:00-09:00 and 09:00-12:00), joined
    # here into the one morning the registry names; the evening then runs to
    # midnight and the night is the small hours.
    _p("morning", (4, 0), (12, 0), "sq", _cldr("sq")),
    _p("afternoon", (12, 0), (18, 0), "sq", _cldr("sq")),
    _p("evening", (18, 0), (0, 0), "sq", _cldr("sq")),
    _p("night", (0, 0), (4, 0), "sq", _cldr("sq")),
    # hy: same shape as is/lt -- the evening runs to midnight and the night is
    # the small hours.
    _p("morning", (6, 0), (12, 0), "hy", _cldr("hy")),
    _p("afternoon", (12, 0), (18, 0), "hy", _cldr("hy")),
    _p("evening", (18, 0), (0, 0), "hy", _cldr("hy")),
    _p("night", (0, 0), (6, 0), "hy", _cldr("hy")),
    # cy: Welsh draws only THREE bands.  The morning opens at midnight and runs
    # to noon, and the rule set carries no night row at all, so none is
    # invented here -- a Welsh "night" would be a boundary nobody stated.
    _p("morning", (0, 0), (12, 0), "cy", _cldr("cy")),
    _p("afternoon", (12, 0), (18, 0), "cy", _cldr("cy")),
    _p("evening", (18, 0), (0, 0), "cy", _cldr("cy")),
    # id: morning opens at midnight (CLDR "pagi" 00:00-10:00); no wrap.
    _p("morning", (0, 0), (10, 0), "id", _cldr("id")),
    _p("afternoon", (10, 0), (15, 0), "id", _cldr("id")),
    _p("evening", (15, 0), (18, 0), "id", _cldr("id")),
    _p("night", (18, 0), (0, 0), "id", _cldr("id")),
    # ms: afternoon "tengah hari" is multi-word (band shipped, no voc); the
    # morning ("pagi") swallows the 00:00-01:00 "tengah malam" sliver.
    _p("morning", (0, 0), (12, 0), "ms", _cldr("ms")),
    _p("afternoon", (12, 0), (14, 0), "ms", _cldr("ms")),
    _p("evening", (14, 0), (19, 0), "ms", _cldr("ms")),
    _p("night", (19, 0), (0, 0), "ms", _cldr("ms")),
    # th: five bands under their own names rather than collapsed, for the same
    # reason Swahili's and Macedonian's are.  CLDR draws two afternoon rows
    # (12:00-13:00 and 13:00-16:00) and labels both บ่าย, so they are one band;
    # the two evening rows are NOT, because they carry different words -- เย็น
    # is the late afternoon and ค่ำ the hours after dark -- and a single
    # "evening" spanning both would answer 16:00-21:00 for a word that means
    # 18:00-21:00.  The night wraps 21:00 round to dawn.  CLDR's เที่ยง and
    # เที่ยงคืน points add no boundary of their own and ship as clock
    # landmarks instead.
    _p("chao", (6, 0), (12, 0), "th", _cldr("th")),
    _p("bai", (12, 0), (16, 0), "th", _cldr("th")),
    _p("yen", (16, 0), (18, 0), "th", _cldr("th")),
    _p("kham", (18, 0), (21, 0), "th", _cldr("th")),
    _p("klangkhuen", (21, 0), (6, 0), "th", _cldr("th")),
    # ta: nine CLDR rows, at the high end of what the standard carries for
    # any locale, and they are kept under their own names rather than folded
    # into an English-shaped four because the extra cuts are real words with
    # narrow senses.  அதிகாலை is the pre-dawn stretch and a separate band from
    # காலை, not a synonym for it; மதியம் and பிற்பகல் split the afternoon at
    # 14:00; மாலை and அந்தி மாலை split the evening at 18:00.  Collapsing any
    # pair would answer a wider span than the word names.  CLDR's நண்பகல்
    # (12:00) point falls on the மதியம் boundary and adds none of its own, so
    # it ships as a clock landmark instead of a band; the midnight point ships
    # as neither, because no source consulted for this locale gave its label.
    _p("adhikaalai", (3, 0), (5, 0), "ta", _cldr("ta")),
    _p("kaalai", (5, 0), (12, 0), "ta", _cldr("ta")),
    _p("madhiyam", (12, 0), (14, 0), "ta", _cldr("ta")),
    _p("pirpakal", (14, 0), (16, 0), "ta", _cldr("ta")),
    _p("maalai", (16, 0), (18, 0), "ta", _cldr("ta")),
    _p("andhimaalai", (18, 0), (21, 0), "ta", _cldr("ta")),
    _p("iravu", (21, 0), (3, 0), "ta", _cldr("ta")),
    # vi: the morning opens at 04:00 and the night from 21:00 wraps to it.
    # CLDR's noon point (trưa, 12:00) falls inside the afternoon band and adds
    # no boundary of its own, so none is invented.
    _p("morning", (4, 0), (12, 0), "vi", _cldr("vi")),
    _p("afternoon", (12, 0), (18, 0), "vi", _cldr("vi")),
    _p("evening", (18, 0), (21, 0), "vi", _cldr("vi")),
    _p("night", (21, 0), (4, 0), "vi", _cldr("vi")),
    # fil: CLDR's two morning bands are collapsed as everywhere else, which
    # also sidesteps their labelling -- CLDR fil names 00:00-06:00 "ng umaga"
    # and 06:00-12:00 "madaling-araw", the reverse of the two words' ordinary
    # senses.  The evening band ships no surface: CLDR gives "gabi" for both
    # it and the night.
    _p("morning", (0, 0), (12, 0), "fil", _cldr("fil")),
    _p("afternoon", (12, 0), (16, 0), "fil", _cldr("fil")),
    _p("evening", (16, 0), (18, 0), "fil", _cldr("fil")),
    _p("night", (18, 0), (0, 0), "fil", _cldr("fil")),
    # ka: the morning opens at 05:00 and the night from 21:00 wraps to it.
    _p("morning", (5, 0), (12, 0), "ka", _cldr("ka")),
    _p("afternoon", (12, 0), (18, 0), "ka", _cldr("ka")),
    _p("evening", (18, 0), (21, 0), "ka", _cldr("ka")),
    _p("night", (21, 0), (5, 0), "ka", _cldr("ka")),
    # tr: afternoon "ogleden sonra" is multi-word (band shipped, no voc).
    _p("morning", (6, 0), (12, 0), "tr", _cldr("tr")),
    _p("afternoon", (12, 0), (19, 0), "tr", _cldr("tr")),
    _p("evening", (19, 0), (21, 0), "tr", _cldr("tr")),
    _p("night", (21, 0), (6, 0), "tr", _cldr("tr")),
    # et
    _p("morning", (5, 0), (12, 0), "et", _cldr("et")),
    _p("afternoon", (12, 0), (18, 0), "et", _cldr("et")),
    _p("evening", (18, 0), (23, 0), "et", _cldr("et")),
    _p("night", (23, 0), (5, 0), "et", _cldr("et")),
    # he: afternoon2 "achar ha-tzohorayim" is multi-word; the single-word
    # "batzohorayim" surfaces the whole afternoon.  night folds the dawn band.
    _p("morning", (6, 0), (12, 0), "he", _cldr("he")),
    _p("afternoon", (12, 0), (18, 0), "he", _cldr("he")),
    _p("evening", (18, 0), (22, 0), "he", _cldr("he")),
    _p("night", (22, 0), (6, 0), "he", _cldr("he")),
    # fa: Persian draws no distinct evening -- afternoon (bad-az-zohr / asr)
    # runs to 19:00 and night (shab) takes over to the small hours.
    _p("morning", (1, 0), (12, 0), "fa", _cldr("fa")),
    _p("afternoon", (12, 0), (19, 0), "fa", _cldr("fa")),
    _p("night", (19, 0), (1, 0), "fa", _cldr("fa")),
    # eu: morning opens at midnight; night 21:00-24:00, no wrap.
    _p("morning", (0, 0), (12, 0), "eu", _cldr("eu")),
    _p("afternoon", (12, 0), (19, 0), "eu", _cldr("eu")),
    _p("evening", (19, 0), (21, 0), "eu", _cldr("eu")),
    _p("night", (21, 0), (0, 0), "eu", _cldr("eu")),
    # ar: evening runs to midnight, night is the small hours 00:00-03:00.
    _p("morning", (3, 0), (12, 0), "ar", _cldr("ar")),
    _p("afternoon", (12, 0), (18, 0), "ar", _cldr("ar")),
    _p("evening", (18, 0), (0, 0), "ar", _cldr("ar")),
    _p("night", (0, 0), (3, 0), "ar", _cldr("ar")),
    # az: night wraps 19:00 -> 04:00.  Surfaces held for native review (the
    # morning word "seher" is a near-homograph of "sabah" = tomorrow).
    _p("morning", (4, 0), (12, 0), "az", _cldr("az")),
    _p("afternoon", (12, 0), (17, 0), "az", _cldr("az")),
    _p("evening", (17, 0), (19, 0), "az", _cldr("az")),
    _p("night", (19, 0), (4, 0), "az", _cldr("az")),
    _p("morning", (4, 0), (12, 0), "el", _cldr("el")),
    _p("afternoon", (12, 0), (17, 0), "el", _cldr("el")),
    _p("evening", (17, 0), (20, 0), "el", _cldr("el")),
    _p("night", (20, 0), (4, 0), "el", _cldr("el")),
    # fi: five bands, kept under their own names rather than collapsed, for the
    # reason Macedonian's are -- Finnish cuts the forenoon in two, aamu is the
    # five hours from 05:00 and aamupaiva only the two before noon, so a single
    # "morning" would answer 05:00-12:00 for a word that means 10:00-12:00.
    # The remaining three are the ordinary afternoon/evening/night bands, but
    # they too keep the Finnish name so one language reads as one set.  Noon
    # and midnight ship as clock landmarks (keskipaiva, keskiyo), not bands.
    _p("aamu", (5, 0), (10, 0), "fi", _cldr("fi")),
    _p("aamupaiva", (10, 0), (12, 0), "fi", _cldr("fi")),
    _p("iltapaiva", (12, 0), (18, 0), "fi", _cldr("fi")),
    _p("ilta", (18, 0), (23, 0), "fi", _cldr("fi")),
    _p("yo", (23, 0), (5, 0), "fi", _cldr("fi")),
]

#: The day-part registry, keyed by :attr:`DayPart.key`.
DAY_PARTS: Dict[str, DayPart] = {p.key: p for p in _DEFAULTS + _LANGUAGES}


def lookup(name: str, lang: Optional[str] = None, *,
           region: Optional[str] = None) -> DayPart:
    """Resolve a day-part by ``name``: the ``lang`` entry, else the global
    default.  ``region`` is the old spelling of ``lang``, used only when
    ``lang`` is absent.  Raises :class:`UnknownDayPartError` when neither
    exists.
    """
    if lang is None:
        lang = region
    if lang is not None:
        specific = DAY_PARTS.get(f"{name}_{lang.lower()}")
        if specific is not None:
            return specific
    default = DAY_PARTS.get(name)
    if default is not None:
        return default
    raise UnknownDayPartError(
        f"no day-part {name!r} for language {lang!r}; known: "
        f"{sorted(DAY_PARTS)}")


def _resolve_boundary(y: int, m: int, d: int, part_time: time,
                      zone: _tzinfo) -> AstroDate:
    """A day-part endpoint resolved to an aware instant in ``zone``.

    A **fold** (DST falling back) keeps the later instant; a **gap** (DST
    springing forward) takes the post-transition offset at the same wall-clock
    reading.
    """
    h, mi = part_time.hour, part_time.minute
    resolved = resolve_wall_clock(y, m, d, h, mi, zone)
    if isinstance(resolved, tuple):
        boundary = resolved[1]  # fold: later occurrence == post-transition
    elif isinstance(resolved, NeverExisted):
        _, off1 = _fold_offsets(y, m, d, h, mi, zone)
        boundary = AstroDate(y, m, d, h, mi, tzinfo=timezone(off1))
    else:
        boundary = resolved
    if part_time.second or part_time.microsecond:
        boundary = boundary.replace(second=part_time.second,
                                    microsecond=part_time.microsecond)
    return boundary


def _span_on_date(part: DayPart, y: int, m: int, d: int,
                  zone: Optional[_tzinfo] = None) -> DateSpan:
    if part.crosses_midnight:
        nxt = civil_add(AstroDate(y, m, d), days=1)
        y2, m2, d2 = nxt.year, nxt.month, nxt.day
    else:
        y2, m2, d2 = y, m, d
    if zone is None:
        start = AstroDate(y, m, d, part.start.hour, part.start.minute,
                          part.start.second, part.start.microsecond)
        end = AstroDate(y2, m2, d2, part.end.hour, part.end.minute,
                        part.end.second, part.end.microsecond)
    else:
        start = _resolve_boundary(y, m, d, part.start, zone)
        end = _resolve_boundary(y2, m2, d2, part.end, zone)
    return DateSpan(start, end)


def daypart_span(date_or_span: Union[AstroDate, date, datetime, DateSpan],
                 name: str, lang: Optional[str] = None,
                 zone: Optional[_tzinfo] = None, *,
                 region: Optional[str] = None) -> DateSpan:
    """The span a day-part occupies on a concrete date.

    ``lang`` selects a language's carve-up of the day ("tarde" in ``es`` runs
    to 20:00); ``region`` is its old spelling.  A :class:`DateSpan` argument
    contributes the civil date of its ``start``.

    A midnight-crosser anchors to the named date and reaches into the next day:
    ``daypart_span(tuesday, "night")`` is Tue 21:00 to Wed 06:00.  When
    ``date_or_span`` is a :class:`DateSpan` the result is clipped to it with
    :meth:`DateSpan.intersect`; a disjoint day-part raises :class:`ValueError`.

    ``zone=None`` keeps both endpoints naive wall-clock readings.  A ``tzinfo``
    makes them aware :class:`AstroDate` instants, resolved as in
    :func:`_resolve_boundary`, so :attr:`DateSpan.width` shows the real elapsed
    time across a DST transition.
    """
    part = lookup(name, lang, region=region)
    anchor = (date_or_span.start if isinstance(date_or_span, DateSpan)
              else date_or_span)
    y, m, d = anchor.year, anchor.month, anchor.day
    span = _span_on_date(part, y, m, d, zone=zone)
    if isinstance(date_or_span, DateSpan):
        composed = span.intersect(date_or_span)
        if composed is None:
            raise ValueError(
                f"day-part {name!r} on {y:04d}-{m:02d}-{d:02d} does not "
                f"intersect the given span {date_or_span}")
        return composed
    return span
