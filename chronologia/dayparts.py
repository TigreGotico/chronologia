"""Day-part registry: named stretches *within* a civil day, resolved to spans.

A :class:`DayPart` binds a human name for a portion of the day ("morning",
"tarde") to a start and end **time-of-day** (a day fraction: 06:00 is a quarter
of the way through the day), tagged with an optional *lang* (``None`` == the
global default convention) and a versioned *source*.  Applied to a concrete
civil date by :func:`daypart_span`, it becomes a :class:`DateSpan` — the same
half-open interval type every other reckoning layer produces.

The golden rule this module teaches: **a day-part is a convention, and
conventions differ.**  "Morning" is not a fact about the sun; it is a boundary
a culture draws, and different cultures draw it differently.  English splits the
post-noon day into *afternoon* and *evening*; Spanish runs one *tarde* straight
across both.  So the boundaries are *data*, language-tagged exactly like the
region-tagged named periods in :mod:`chronologia.periods`, never hard-coded
engine logic.

Why the tag is a *language*, not a region
-----------------------------------------
It says ``lang`` because a language is what it is.  ``tarde`` is Spanish, and
it is Spanish in Madrid, Lima and Los Angeles alike; nothing about the entry is
geographic, and calling the tag a region invited the reader to think a
Spanish-speaker in Texas somehow gets the English bands.  :mod:`periods` keeps
``region`` because *its* tag really is geographic — the British bronze age is
not the Chinese one.  The old ``region`` spelling stays available on
:class:`DayPart`, :func:`lookup` and :func:`daypart_span` as a documented
alias, because :data:`DAY_PARTS` and both functions are public API and a rename
must not break a caller who wrote ``region="es"`` while the name was wrong.
Genuine geographic variation within one language can be layered on the day it
is actually needed; it is not modelled now.

Canonical source
----------------
The per-language boundaries are the **Unicode CLDR Day Period Rules** (TR35 /
CLDR 47), the machine-readable authority for locale-specific day periods —
precisely because it encodes that these boundaries vary by locale.  A copy of
the chart lives in the papers library
(``standards/cldr47_day_period_rules.html``) and every language row below is
transcribed from it.

The **default** set (lang ``None``) is *not* CLDR, and earlier versions of this
docstring were wrong to say it was.  CLDR's ``en`` rows run ``morning1`` from
00:00 and place no band before it; chronologia's default starts morning at
06:00 and runs a ``night`` that wraps 21:00 → 06:00.  That is chronologia's own
English convention — the reading an English speaker means by "this morning" and
"tonight" — and it is what the library has always shipped.  It is kept as-is
deliberately: changing it would silently move every English span already in
use.  The honest description is therefore "chronologia's English convention,
which departs from CLDR ``en`` at the morning start and in wrapping night", and
the CLDR citation is reserved for the per-language rows, where it is exact.

Default convention (lang ``None``), chronologia's own English convention:

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

Reading CLDR's rows into spans
------------------------------
CLDR states a day period as a *start time* and lets the next row's start close
it, so a locale's rows are a cyclic partition of the 24 hours.  Transcribing
that mechanically gives every band ``[own start, next start)``, with the last
row of the day closing at 24:00.  One rule handles the wrap, and it is applied
uniformly: **when the same period name occupies both the first row (anchored at
00:00) and the last row, the two rows are one band and are joined into a single
midnight-crossing span.**  Romanian is the case that shows it — ``noapte``
appears at 00:00 *and* at 22:00, one night split by the chart's own
start-time-only notation, so it is stored once as ``[22:00, 05:00)``.

Where the names differ, the rows are left apart.  Italian ``sera`` closes at
24:00 and ``notte`` opens at 00:00, so ``notte`` is ``[00:00, 06:00)`` — the
small hours — and is *not* re-cut into an English-shaped night beginning the
previous evening.  That is the whole point of transcribing rather than
translating: English's night wraps because English's night wraps, and Italian's
does not have to.

Per-language conventions, all from the CLDR 47 chart above:

* ``es`` madrugada ``[00:00, 06:00)``, mañana ``[06:00, 12:00)``, tarde
  ``[12:00, 20:00)``, noche ``[20:00, 24:00)`` — one *tarde* across what
  English calls afternoon *and* early evening.
* ``pt`` madrugada ``[00:00, 06:00)``, manhã ``[06:00, 12:00)``, tarde
  ``[12:00, 19:00)``, noite ``[19:00, 24:00)``.
* ``ca`` matinada ``[00:00, 06:00)``, matí ``[06:00, 12:00)``, migdia
  ``[12:00, 13:00)``, tarda ``[13:00, 19:00)``, vespre ``[19:00, 21:00)``, nit
  ``[21:00, 24:00)``.
* ``gl`` madrugada ``[00:00, 06:00)``, mañá ``[06:00, 12:00)``, mediodía
  ``[12:00, 13:00)``, tarde ``[13:00, 21:00)``, noite ``[21:00, 24:00)``.
* ``fr`` nuit ``[00:00, 04:00)``, matin ``[04:00, 12:00)``, après-midi
  ``[12:00, 18:00)``, soir ``[18:00, 24:00)``.
* ``it`` notte ``[00:00, 06:00)``, mattina ``[06:00, 12:00)``, pomeriggio
  ``[12:00, 18:00)``, sera ``[18:00, 24:00)``.
* ``ro`` noapte ``[22:00, 05:00)`` (the joined wrap), dimineață
  ``[05:00, 12:00)``, după-amiază ``[12:00, 18:00)``, seară ``[18:00, 22:00)``.
* ``de`` Nacht ``[00:00, 05:00)``, Morgen ``[05:00, 10:00)``, Vormittag
  ``[10:00, 12:00)``, Mittag ``[12:00, 13:00)``, Nachmittag ``[13:00, 18:00)``,
  Abend ``[18:00, 24:00)`` — six bands, none of which is English's afternoon.
* ``nl`` nacht ``[00:00, 06:00)``, ochtend ``[06:00, 12:00)``, middag
  ``[12:00, 18:00)``, avond ``[18:00, 24:00)``.
* ``sv`` natt ``[00:00, 05:00)``, morgon ``[05:00, 10:00)``, förmiddag
  ``[10:00, 12:00)``, eftermiddag ``[12:00, 18:00)``, kväll
  ``[18:00, 24:00)``.
* ``da`` nat ``[00:00, 05:00)``, morgen ``[05:00, 10:00)``, formiddag
  ``[10:00, 12:00)``, eftermiddag ``[12:00, 18:00)``, aften ``[18:00, 24:00)``.
* ``nb``/``nn`` natt ``[00:00, 06:00)``, morgen/morgon ``[06:00, 10:00)``,
  formiddag/føremiddag ``[10:00, 12:00)``, ettermiddag ``[12:00, 18:00)``,
  kveld ``[18:00, 24:00)``.

Eighteen further locales (``ar az bg cs el et eu fa he hr hu id ms pl sk sl
tr uk``) are transcribed the same way, but collapsed into chronologia's own
four-band model — ``morning`` (CLDR morning1+morning2), ``afternoon``
(afternoon1/2), ``evening`` (evening1) and ``night`` (night1, joined with a
00:00 night2 into one midnight-crossing band) — because these locales are
consumed through the deictic ``daypart_ref`` grammar ("this morning",
"yesterday evening"), which speaks that four-band vocabulary.  The bands are
always shipped; a band whose only natural surface is multi-word (Czech ``v
noci``, Polish ``po południu``, Turkish ``öğleden sonra``, Malay ``tengah
hari``) carries no ``daypart_*.voc`` yet, exactly as French ``après-midi``
already does, and a few locales (``az`` ``el``) ship the bands but hold their
surfaces for native review.

``Vormittag``, ``förmiddag``, ``formiddag``, ``føremiddag`` and ``migdia`` have
no English name at all, which is why they are stored under their own names
rather than folded into ``morning`` or ``noon``.  Inventing an English label
for a band English does not have would be the same mistake as assuming English's
hours.

Lookup falls back from a language to the global default: asking for ``morning``
in ``es`` yields the default morning (Spanish contributes ``tarde``, not a
``morning`` override); asking for ``tarde`` with no language raises, since
``tarde`` is not a global name.
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


#: The default set's authority.  Deliberately *not* a CLDR citation: the bands
#: below are chronologia's own English convention and differ from CLDR ``en``
#: (which starts morning at 00:00 and does not wrap night).  See the module
#: docstring for why the shipped default is kept rather than re-cut.
_CHRONOLOGIA_EN = "chronologia English day-part convention (see module docs)"


class UnknownDayPartError(KeyError):
    """No day-part matches the requested ``(name, region)``.

    Raised by :func:`lookup` (and therefore :func:`daypart_span`) when neither
    a region-specific entry nor a global default carries the name.
    """


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

    ``start``/``end`` are *times of day*, not instants: a :class:`DayPart` is a
    convention with no date until :func:`daypart_span` anchors it to one.  The
    ``crosses_midnight`` flag is validated against the endpoints so it can never
    silently disagree with them.
    """
    name: str
    start: time
    end: time
    lang: Optional[str]
    source: str
    crosses_midnight: bool

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
        """Deprecated spelling of :attr:`lang`, kept so existing callers work.

        The field was called ``region`` before it was noticed that every value
        it ever held was a language code.  Reading it still works and returns
        the language tag; new code should say :attr:`lang`.
        """
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
    _p("noch", (0, 0), (4, 0), "ru", _cldr("ru")),
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
    # Polish "po poludniu" -- carries no ``daypart_*.voc`` yet, exactly as
    # French "apres-midi" already does).
    # uk: evening runs to midnight, night is the small hours (like ru).
    _p("morning", (4, 0), (12, 0), "uk", _cldr("uk")),
    _p("afternoon", (12, 0), (18, 0), "uk", _cldr("uk")),
    _p("evening", (18, 0), (0, 0), "uk", _cldr("uk")),
    _p("night", (0, 0), (4, 0), "uk", _cldr("uk")),
    # hr
    _p("morning", (4, 0), (12, 0), "hr", _cldr("hr")),
    _p("afternoon", (12, 0), (18, 0), "hr", _cldr("hr")),
    _p("evening", (18, 0), (21, 0), "hr", _cldr("hr")),
    _p("night", (21, 0), (4, 0), "hr", _cldr("hr")),
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
    # pl (afternoon "po poludniu" and night "w nocy" are multi-word: bands
    # shipped, no voc; morning "rano" and evening "wieczorem" carry surfaces).
    _p("morning", (6, 0), (12, 0), "pl", _cldr("pl")),
    _p("afternoon", (12, 0), (18, 0), "pl", _cldr("pl")),
    _p("evening", (18, 0), (21, 0), "pl", _cldr("pl")),
    _p("night", (21, 0), (6, 0), "pl", _cldr("pl")),
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
    # el: surfaces held for native review (the deictic forms carry an article
    # -- "to proi" -- that strands as a separate token here).
    _p("morning", (4, 0), (12, 0), "el", _cldr("el")),
    _p("afternoon", (12, 0), (17, 0), "el", _cldr("el")),
    _p("evening", (17, 0), (20, 0), "el", _cldr("el")),
    _p("night", (20, 0), (4, 0), "el", _cldr("el")),
]

#: Deprecated alias for :data:`_LANGUAGES`, from when the tag was miscalled a
#: region.  Kept because it is short, private, and free.
_REGIONAL = _LANGUAGES

#: The day-part registry, keyed by :attr:`DayPart.key`.
DAY_PARTS: Dict[str, DayPart] = {p.key: p for p in _DEFAULTS + _LANGUAGES}


def lookup(name: str, lang: Optional[str] = None, *,
           region: Optional[str] = None) -> DayPart:
    """Resolve a day-part by ``name``, preferring a ``lang`` entry.

    A language-specific entry (``tarde`` in ``es``) wins; otherwise the global
    default carries the name (``morning`` has no ``es`` entry, so ``es`` falls
    back to it).  Raises :class:`UnknownDayPartError` when neither exists.

    ``region`` is the old spelling of ``lang`` and still works; it is honoured
    only when ``lang`` was not given, so a caller who passes both gets the one
    they named properly.
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


def _civil_ymd(date_or_span: Union[AstroDate, date, datetime, DateSpan]
               ) -> Tuple[int, int, int]:
    anchor: Union[AstroDate, date, datetime]
    if isinstance(date_or_span, DateSpan):
        anchor = date_or_span.start
    else:
        anchor = date_or_span
    return anchor.year, anchor.month, anchor.day


def _resolve_boundary(y: int, m: int, d: int, part_time: time,
                      zone: _tzinfo) -> AstroDate:
    """A day-part endpoint's wall-clock reading, resolved aware in ``zone``.

    Delegates to :func:`~chronologia.astrodate.resolve_wall_clock` for the
    fold/gap semantics, then applies the documented convention for the two
    ambiguous outcomes: **fold** (the reading occurs twice, DST falling back)
    keeps the *later* of the two real instants; **gap** (the reading is
    skipped, DST springing forward) is resolved to the *post-transition*
    instant — the moment with the new, post-jump offset, at that same wall
    clock reading.  Either way, the boundary is always a single, well-defined
    instant, never a raised error and never a silently-picked earlier one.
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

    ``lang`` selects a language's own carve-up of the day ("tarde" in ``es``
    runs to 20:00); omitted, the global default set applies.  ``region`` is the
    old spelling of ``lang`` and still works, as on :func:`lookup`.

    ``date_or_span`` supplies the civil date to anchor to — an
    :class:`AstroDate`/``date``/``datetime`` names the day directly; a
    :class:`DateSpan` contributes the civil date of its ``start``.

    A midnight-crosser anchors to the *named* date and reaches into the next
    civil day: ``daypart_span(tuesday, "night")`` is Tue 21:00 → **Wed** 06:00
    (the documented convention — "tuesday night" belongs to Tuesday even though
    it ends on Wednesday).

    When ``date_or_span`` is itself a :class:`DateSpan`, the result is
    *composed* with it via :meth:`DateSpan.intersect` — ``daypart_span(some_day,
    "morning")`` returns morning clipped to that day-span, so applying a
    day-part to "tuesday" and to a truncated slice of Tuesday differ exactly by
    the overlap.  A day-part disjoint from the given span raises
    :class:`ValueError`, since there is no interval to return.

    **``zone``.**  ``None`` (the default) keeps every endpoint a naive
    wall-clock reading, byte-identical to the library's behaviour before
    ``zone`` existed.  Given a ``tzinfo``, both endpoints become **aware**
    :class:`AstroDate` instants in that zone instead of bare wall-clock
    readings — resolved via
    :func:`~chronologia.astrodate.resolve_wall_clock`, so a boundary landing
    in a DST **gap** (spring-forward) or **fold** (fall-back) resolves
    deterministically to the *post-transition* instant (see
    :func:`_resolve_boundary`) rather than raising or guessing.  Because the
    two endpoints can therefore each pick up a different UTC offset across a
    transition, :attr:`DateSpan.width` on the result honestly reflects the
    real elapsed time -- 23 or 25 hours instead of the nominal 24 (or, for a
    day-part narrower than a full day, a similar hour thinner/thicker than its
    naive width) whenever the transition falls inside the part's boundaries.
    """
    part = lookup(name, lang, region=region)
    y, m, d = _civil_ymd(date_or_span)
    span = _span_on_date(part, y, m, d, zone=zone)
    if isinstance(date_or_span, DateSpan):
        composed = span.intersect(date_or_span)
        if composed is None:
            raise ValueError(
                f"day-part {name!r} on {y:04d}-{m:02d}-{d:02d} does not "
                f"intersect the given span {date_or_span}")
        return composed
    return span
