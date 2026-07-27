"""Globally well-known holidays — the set a *language* binds for NL reference.

The movable/religious/civil set a *language* binds for natural-language
reference ("christmas", "when is easter", "next christmas").  This is
deliberately NOT "every rule in all 45 jurisdictions": it is a small, curated
set of holidays that are well-known *across* borders, each anchored to one
jurisdiction whose data file already carries its rule and its official name.
Behaviour (the date math) stays in the rule kinds; the surfaces a language
speaks are FACTS harvested at load time from the engine's existing i18n tables
(official native names + ``translations.tab``) plus a curated spoken-alias table
(``i18n/well_known.tab``) — never a giant hand-authored per-language vocabulary
file.

The second tier (:class:`JurisdictionKnownHoliday`) carries the holidays whose
rule only picks out a date once a jurisdiction is assumed (Mother's / Father's
Day differ per country), keyed by ``(key, lang)``.
"""
from __future__ import annotations

import os
import threading
from typing import Dict, FrozenSet, Optional, Tuple

from chronologia.astrodate import AstroDate, DateSpan

from .loader import _DATA_DIR, _translations_for
from .model import _shape_span
from .rules import (CalendarDateRule, DecreeTableRule, EasterOffsetRule,
                    FixedRule, NthWeekdayRule, RuleKind)

from dataclasses import dataclass


# --------------------------------------------------------------------------
# Globally well-known holidays — the movable/religious/civil set a *language*
# binds for natural-language reference ("christmas", "when is easter", "next
# christmas").
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class _KnownHoliday:
    """The shared contract of both well-known tiers: a keyed, datable rule.

    Both the cross-border first tier (:class:`WellKnownHoliday`) and the
    locale-bound second tier (:class:`JurisdictionKnownHoliday`) are the same
    thing at heart — a language-neutral ``key`` bound to a date ``kind`` and a
    set of ``categories`` — differing only in their *binding* (one canonical
    rule vs one rule chosen per locale). The common ``date_for`` / ``span_for``
    resolution lives here once, so the resolver treats both tiers alike and
    neither subclass re-implements the date math. Subclasses supply the
    binding-specific provenance fields and their own ``span_shape``.
    """

    key: str
    kind: RuleKind
    categories: FrozenSet[str]

    def date_for(self, year: int) -> Optional[Tuple[AstroDate, str]]:
        """The ``(AstroDate, basis)`` of this holiday in ``year`` (or None)."""
        obs = self.kind.observances(year)
        return obs[0] if obs else None

    def span_for(self, year: int) -> Optional[Tuple[DateSpan, str]]:
        """The resolved ``(DateSpan, basis)`` for ``year`` (span shape applied)."""
        got = self.date_for(year)
        if got is None:
            return None
        date, basis = got
        return _shape_span(date, basis, self.span_shape), basis


@dataclass(frozen=True)
class WellKnownHoliday(_KnownHoliday):
    """A globally well-known holiday keyed for cross-language reference.

    ``key`` is a stable, language-neutral identifier (``christmas``,
    ``easter``); ``kind`` is the canonical (Western) date rule, reusing the
    same rule kinds every jurisdiction uses, so a movable holiday still
    resolves through :func:`~chronologia.computus.easter` and never re-derives
    date math.  ``anchor_jurisdiction`` / ``anchor_name`` name the real
    jurisdiction + official native name the surfaces are harvested from (the
    provenance ``explain`` traces); ``anchor_lang`` is the language of that
    native name (so it is offered as a surface for its own language).
    """

    anchor_jurisdiction: str
    anchor_name: str
    anchor_lang: str
    span_shape: str = "day"


#: The curated global well-known set.  Each entry anchors on a jurisdiction
#: whose ``.tab`` file already carries the same rule and the official name.
WELL_KNOWN: Tuple[WellKnownHoliday, ...] = (
    WellKnownHoliday("new_year", FixedRule(1, 1),
                     frozenset({"public"}), "PT", "Ano Novo", "pt"),
    WellKnownHoliday("new_year_eve", FixedRule(12, 31),
                     frozenset({"public"}), "US", "New Year's Eve", "en"),
    WellKnownHoliday("epiphany", FixedRule(1, 6),
                     frozenset({"public", "religious"}), "IT", "Epifania", "it"),
    WellKnownHoliday("carnival", EasterOffsetRule(-47),
                     frozenset({"public"}), "PT", "Carnaval", "pt"),
    # Palm Sunday — the Sunday before Easter (Easter -7), opening Holy Week.
    # A computable Western liturgical date fixed by the same Easter computus as
    # Good Friday; the Roman Missal / General Roman Calendar defines it as
    # "Dominica in Palmis de Passione Domini", the sixth Sunday of Lent. It is a
    # liturgical (not civil day-off) observance, so it carries only
    # ``religious`` — never ``public``. Easter 2024 = 31 Mar, so Palm Sunday
    # 2024 = 24 Mar (verified against the 2024 liturgical calendar,
    # USCCB/Roman Missal). Anchored on ``en`` for its English surface.
    # Ash Wednesday — the first day of Lent, Easter -46 (46 days before Easter,
    # counting the Sundays; the Roman Missal / General Roman Calendar,
    # "Feria IV Cinerum"). Purely liturgical, so ``religious`` only. Easter 2018
    # = 1 Apr, so Ash Wednesday 2018 = 14 Feb (verified against the 2018
    # liturgical calendar). NOTE its name embeds "Wednesday" — the feast surface
    # is longer/more specific than the bare weekday and must win over it.
    WellKnownHoliday("ash_wednesday", EasterOffsetRule(-46),
                     frozenset({"religious"}),
                     "VA", "Ash Wednesday", "en"),
    # Palm Sunday — the Sunday before Easter (Easter -7), opening Holy Week.
    # A computable Western liturgical date fixed by the same Easter computus as
    # Good Friday; the Roman Missal / General Roman Calendar defines it as
    # "Dominica in Palmis de Passione Domini", the sixth Sunday of Lent. It is a
    # liturgical (not civil day-off) observance, so it carries only
    # ``religious`` — never ``public``. Easter 2024 = 31 Mar, so Palm Sunday
    # 2024 = 24 Mar (verified against the 2024 liturgical calendar,
    # USCCB/Roman Missal). Anchored on ``en`` for its English surface.
    WellKnownHoliday("palm_sunday", EasterOffsetRule(-7),
                     frozenset({"religious"}),
                     "VA", "Palm Sunday", "en"),
    # Maundy (Holy) Thursday — the Thursday of Holy Week, Easter -3, when the
    # Mass of the Lord's Supper is celebrated ("Feria V in Cena Domini").
    # Liturgical only. Easter 2018 = 1 Apr -> 29 Mar 2018. Name embeds
    # "Thursday" — same longest-match precedence as Ash Wednesday.
    WellKnownHoliday("maundy_thursday", EasterOffsetRule(-3),
                     frozenset({"religious"}),
                     "VA", "Maundy Thursday", "en"),
    WellKnownHoliday("good_friday", EasterOffsetRule(-2),
                     frozenset({"public", "religious"}),
                     "PT", "Sexta-feira Santa", "pt"),
    # Holy Saturday — the Saturday of Holy Week, Easter -1, the Easter Vigil
    # ("Sabbatum Sanctum"). Liturgical only. Easter 2018 = 1 Apr -> 31 Mar 2018.
    WellKnownHoliday("holy_saturday", EasterOffsetRule(-1),
                     frozenset({"religious"}),
                     "VA", "Holy Saturday", "en"),
    WellKnownHoliday("easter", EasterOffsetRule(0),
                     frozenset({"public", "religious"}),
                     "PT", "Domingo de Pascoa", "pt"),
    WellKnownHoliday("easter_monday", EasterOffsetRule(1),
                     frozenset({"public", "religious"}),
                     "FR", "Lundi de Pâques", "fr"),
    WellKnownHoliday("ascension", EasterOffsetRule(39),
                     frozenset({"public", "religious"}), "FR", "Ascension", "fr"),
    WellKnownHoliday("pentecost", EasterOffsetRule(49),
                     frozenset({"public", "religious"}),
                     "DE", "Pfingstsonntag", "de"),
    WellKnownHoliday("whit_monday", EasterOffsetRule(50),
                     frozenset({"public", "religious"}),
                     "FR", "Lundi de Pentecôte", "fr"),
    # Trinity Sunday — the Sunday after Pentecost, Easter +56 ("Dominica
    # Sanctissimae Trinitatis"). Liturgical only. Easter 2018 = 1 Apr -> 27 May
    # 2018. Name embeds "Sunday" — same longest-match precedence.
    WellKnownHoliday("trinity_sunday", EasterOffsetRule(56),
                     frozenset({"religious"}),
                     "VA", "Trinity Sunday", "en"),
    WellKnownHoliday("corpus_christi", EasterOffsetRule(60),
                     frozenset({"public", "religious"}),
                     "PT", "Corpo de Deus", "pt"),
    WellKnownHoliday("assumption", FixedRule(8, 15),
                     frozenset({"public", "religious"}),
                     "PT", "Assuncao de Nossa Senhora", "pt"),
    WellKnownHoliday("all_saints", FixedRule(11, 1),
                     frozenset({"public", "religious"}),
                     "PT", "Dia de Todos os Santos", "pt"),
    WellKnownHoliday("christmas_eve", FixedRule(12, 24),
                     frozenset({"public", "religious"}),
                     "US", "Christmas Eve", "en"),
    WellKnownHoliday("christmas", FixedRule(12, 25),
                     frozenset({"public", "religious"}), "PT", "Natal", "pt"),
    WellKnownHoliday("boxing_day", FixedRule(12, 26),
                     frozenset({"public", "religious"}),
                     "NL", "Tweede Kerstdag", "nl"),

    # ---- Orthodox-Easter cycle (Julian computus, already modelled) --------
    # The Orthodox Pascha rendered on the civil calendar via
    # ``EasterOffsetRule(..., "julian_gregorian_date")``.  Because Orthodox
    # Easter is a real Sunday, the whole cycle reduces to integer offsets, just
    # like the Western one — no new date math.  Basis ``exact``.
    WellKnownHoliday("orthodox_easter", EasterOffsetRule(0, "julian_gregorian_date"),
                     frozenset({"public", "religious", "orthodox"}),
                     "GR", "Πάσχα", "el"),
    WellKnownHoliday("orthodox_good_friday",
                     EasterOffsetRule(-2, "julian_gregorian_date"),
                     frozenset({"public", "religious", "orthodox"}),
                     "GR", "Μεγάλη Παρασκευή", "el"),
    WellKnownHoliday("orthodox_easter_monday",
                     EasterOffsetRule(1, "julian_gregorian_date"),
                     frozenset({"public", "religious", "orthodox"}),
                     "GR", "Δευτέρα του Πάσχα", "el"),

    # ---- Orthodox (Julian-calendar) Christmas -----------------------------
    # The Nativity fixed at Julian December 25, rendered on the civil calendar
    # through the registered ``julian`` calendar (NOT a hard-coded Gregorian
    # Jan 7): the Julian->Gregorian offset the calendar carries lands it on
    # Gregorian Jan 7 for 1900-2099 and Jan 6 in early 1900 — the repo's own
    # Julian arithmetic, never a magic constant. Basis ``exact``.
    # Bound to churches on the Julian calendar (RU/BG/UA/RS/GE ...). Greece and
    # the other New-Calendar churches keep Christmas on Gregorian Dec 25, i.e.
    # the plain ``christmas`` key — el is deliberately NOT an alias here.
    WellKnownHoliday("orthodox_christmas", CalendarDateRule("julian", 12, 25),
                     frozenset({"public", "religious", "orthodox"}),
                     "RU", "Рождество Христово", "ru"),
    WellKnownHoliday("orthodox_christmas_eve", CalendarDateRule("julian", 12, 24),
                     frozenset({"religious", "orthodox"}),
                     "RU", "Рождественский сочельник", "ru"),

    # ---- Movable Islamic feasts (Umm al-Qura table, ``calendar_date``) ----
    # These resolve through the tabulated Umm al-Qura calendar (basis
    # ``tabulated``): inside its published range (AH 1356..1500, roughly
    # 1937..2077 CE) the Gregorian date is looked up, never computed here; a
    # year whose occurrence falls outside the table contributes NO date, so the
    # reference is honestly silent out of range rather than fabricating one.
    WellKnownHoliday("eid_al_fitr", CalendarDateRule("umm_al_qura", 10, 1),
                     frozenset({"public", "religious", "islamic"}),
                     "SA", "عيد الفطر", "ar"),
    WellKnownHoliday("eid_al_adha", CalendarDateRule("umm_al_qura", 12, 10),
                     frozenset({"public", "religious", "islamic"}),
                     "SA", "عيد الأضحى", "ar"),
    WellKnownHoliday("ramadan", CalendarDateRule("umm_al_qura", 9, 1),
                     frozenset({"religious", "islamic"}),
                     "SA", "رمضان", "ar"),
    WellKnownHoliday("islamic_new_year", CalendarDateRule("umm_al_qura", 1, 1),
                     frozenset({"public", "religious", "islamic"}),
                     "SA", "رأس السنة الهجرية", "ar"),
    WellKnownHoliday("ashura", CalendarDateRule("umm_al_qura", 1, 10),
                     frozenset({"religious", "islamic"}),
                     "SA", "عاشوراء", "ar"),
    WellKnownHoliday("mawlid", CalendarDateRule("umm_al_qura", 3, 12),
                     frozenset({"public", "religious", "islamic"}),
                     "SA", "المولد النبوي", "ar"),

    # ---- Movable Jewish feasts (arithmetic Hebrew calendar, ``calendar_date``)
    # The Hebrew calendar here is the arithmetic (Hillel II) one, so its basis
    # is ``exact`` — the civil date is derived, not looked up.  Each feast is a
    # fixed Hebrew (month, day); a feast begins the preceding sunset, so the
    # date is the first *full* civil day (the convention the published Jewish
    # date tables tabulate).
    WellKnownHoliday("rosh_hashanah", CalendarDateRule("hebrew", 7, 1),
                     frozenset({"public", "religious", "hebrew"}),
                     "IL", "ראש השנה", "he"),
    WellKnownHoliday("yom_kippur", CalendarDateRule("hebrew", 7, 10),
                     frozenset({"public", "religious", "hebrew"}),
                     "IL", "יום כיפור", "he"),
    WellKnownHoliday("passover", CalendarDateRule("hebrew", 1, 15),
                     frozenset({"public", "religious", "hebrew"}),
                     "IL", "פסח", "he"),
    WellKnownHoliday("hanukkah", CalendarDateRule("hebrew", 9, 25),
                     frozenset({"religious", "hebrew"}),
                     "IL", "חנוכה", "he"),

    # ---- Movable East-Asian feasts (tabulated Chinese calendar) -----------
    # ``calendar_date`` against the tabulated Chinese lunisolar calendar
    # (basis ``tabulated``, published range lunar years 1901..2099); silent
    # outside the table, never computed here.
    WellKnownHoliday("chinese_new_year", CalendarDateRule("chinese", 1, 1),
                     frozenset({"public"}), "CN", "春节", "zh"),
    WellKnownHoliday("mid_autumn", CalendarDateRule("chinese", 8, 15),
                     frozenset({"public"}), "CN", "中秋节", "zh"),

    # ---- Nowruz (Persian New Year) ----------------------------------------
    # The March-equinox new year, taken here from the arithmetic Solar Hijri
    # calendar (1 Farvardin) — the same calendar the ``fa``/``az`` locales
    # already model, basis ``exact``.
    WellKnownHoliday("nowruz", CalendarDateRule("solar_hijri_arithmetic", 1, 1),
                     frozenset({"public"}), "IR", "نوروز", "fa"),

    # ---- Decree-tabulated feasts (no closed form modelled here) -----------
    # Diwali (Hindu, lunar Amanta/Purnimanta) and Vesak (Buddhist, full moon of
    # Vaisakha) have no arithmetic calendar in this engine, so — per house
    # style — they are ``DecreeTableRule`` with explicit published per-year
    # dates (Diwali = Lakshmi Puja main day; Vesak = the UN/observed full-moon
    # date).  Basis ``tabulated``; a year outside the listed range is honestly
    # silent (the reference simply does not resolve), so out-of-range corpus
    # cases are xfailed, not asserted to a fabricated date.
    WellKnownHoliday("diwali", DecreeTableRule((
        (2016, (10, 30)), (2017, (10, 19)), (2018, (11, 7)), (2019, (10, 27)),
        (2020, (11, 14)), (2021, (11, 4)), (2022, (10, 24)), (2023, (11, 12)),
        (2024, (10, 31)), (2025, (10, 20)), (2026, (11, 8)), (2027, (10, 29)),
    )), frozenset({"religious", "hindu"}), "IN", "दिवाली", "hi"),
    WellKnownHoliday("vesak", DecreeTableRule((
        (2016, (5, 21)), (2017, (5, 10)), (2018, (5, 29)), (2019, (5, 18)),
        (2020, (5, 7)), (2021, (5, 26)), (2022, (5, 16)), (2023, (5, 5)),
        (2024, (5, 23)), (2025, (5, 12)), (2026, (5, 31)), (2027, (5, 20)),
    )), frozenset({"religious"}), "LK", "Vesak", "en"),

    # ---- Jurisdiction-invariant secular / cross-anglosphere fixed days ----
    # These are the same rule everywhere they are spoken, so they need no
    # per-locale tier: Halloween (31 Oct), St Valentine's (14 Feb) and
    # St Patrick's (17 Mar, a statutory holiday in Ireland) are fixed Gregorian
    # dates; Thanksgiving here is the **U.S.** rule (4th Thursday of November).
    # Canada's Thanksgiving is the 2nd Monday of October — a genuinely
    # different rule — so the ``thanksgiving`` surface is offered for ``en``
    # only under the documented U.S. reading; a Canadian reference needs its own
    # jurisdiction-scoped resolution (out of scope here, and NOT silently
    # resolved to the U.S. date).
    WellKnownHoliday("halloween", FixedRule(10, 31),
                     frozenset({"unofficial"}), "US", "Halloween", "en"),
    WellKnownHoliday("valentines", FixedRule(2, 14),
                     frozenset({"unofficial"}), "US", "Valentine's Day", "en"),
    WellKnownHoliday("st_patricks", FixedRule(3, 17),
                     frozenset({"public", "religious"}),
                     "IE", "Saint Patrick's Day", "en"),
    WellKnownHoliday("thanksgiving", NthWeekdayRule(11, 4, 3),
                     frozenset({"public"}), "US", "Thanksgiving", "en"),
)

#: ``key -> WellKnownHoliday`` for O(1) lookup by the resolver.
WELL_KNOWN_BY_KEY: Dict[str, WellKnownHoliday] = {w.key: w for w in WELL_KNOWN}


# --------------------------------------------------------------------------
# Second tier — JURISDICTION-BOUND well-known holidays.
#
# Some holiday *names* only pick out a date once a jurisdiction is assumed: the
# same colloquial name resolves to a DIFFERENT rule in different countries.
# "Mother's Day" is the 2nd Sunday of May in the U.S./Germany/Italy/Netherlands,
# the 1st Sunday of May in Portugal/Spain, and the last Sunday of May in France;
# "Father's Day" is the 3rd Sunday of June in the U.S./France/Netherlands, but
# 19 March (St Joseph) in Portugal/Spain/Italy and Ascension Day in Germany.
# A single ``WELL_KNOWN`` entry (one key, one rule) cannot honestly carry that,
# so these live in a second tier keyed by ``(key, lang)``: the rule offered for
# a surface is chosen by the *locale's* documented jurisdiction default.
#
# Jurisdiction-default decisions (the fact each locale is bound to):
#   pt->PT  es->ES  ca->ES  gl->ES  de->DE  fr->FR  it->IT  nl->NL  en->US
# (``en`` is deliberately given the U.S. reading and no other; a multi-country
# anglosphere name like "independence day" is NOT added here — it is left
# unresolved because no single country is implied, and inventing one would be
# dishonest. A jurisdiction word would be required to disambiguate it.)
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class JurisdictionKnownHoliday(_KnownHoliday):
    """A well-known holiday whose rule depends on the speaking ``lang``'s country.

    ``key`` is the language-neutral base identifier (``mothers_day``);
    ``lang`` is the locale this binding serves; ``kind`` is the rule that
    locale's jurisdiction default fixes. ``jurisdiction`` records the country
    the default reflects (provenance for ``explain``). It shares
    :class:`_KnownHoliday`'s date/span interface, so the resolver treats both
    tiers alike.
    """

    lang: str
    jurisdiction: str
    span_shape: str = "day"


_MD_2SUN_MAY = NthWeekdayRule(5, 2, 6)   # 2nd Sunday of May
_MD_1SUN_MAY = NthWeekdayRule(5, 1, 6)   # 1st Sunday of May
_MD_LAST_SUN_MAY = NthWeekdayRule(5, -1, 6)  # last Sunday of May
_FD_3SUN_JUN = NthWeekdayRule(6, 3, 6)   # 3rd Sunday of June
_FD_MAR19 = FixedRule(3, 19)             # 19 March (St Joseph)
_FD_ASCENSION = EasterOffsetRule(39)     # Ascension Day (Germany, Vatertag)
_UNOFF = frozenset({"unofficial"})

#: The jurisdiction-bound second tier (see the block comment above).
JURISDICTION_KNOWN: Tuple[JurisdictionKnownHoliday, ...] = (
    # Mother's Day — rule per the locale's jurisdiction default.
    JurisdictionKnownHoliday("mothers_day", _MD_2SUN_MAY, _UNOFF, "en", "US"),
    JurisdictionKnownHoliday("mothers_day", _MD_2SUN_MAY, _UNOFF, "de", "DE"),
    JurisdictionKnownHoliday("mothers_day", _MD_2SUN_MAY, _UNOFF, "it", "IT"),
    JurisdictionKnownHoliday("mothers_day", _MD_2SUN_MAY, _UNOFF, "nl", "NL"),
    JurisdictionKnownHoliday("mothers_day", _MD_1SUN_MAY, _UNOFF, "pt", "PT"),
    JurisdictionKnownHoliday("mothers_day", _MD_1SUN_MAY, _UNOFF, "es", "ES"),
    JurisdictionKnownHoliday("mothers_day", _MD_1SUN_MAY, _UNOFF, "ca", "ES"),
    JurisdictionKnownHoliday("mothers_day", _MD_1SUN_MAY, _UNOFF, "gl", "ES"),
    JurisdictionKnownHoliday("mothers_day", _MD_LAST_SUN_MAY, _UNOFF, "fr", "FR"),
    # Father's Day — rule per the locale's jurisdiction default.
    JurisdictionKnownHoliday("fathers_day", _FD_3SUN_JUN, _UNOFF, "en", "US"),
    JurisdictionKnownHoliday("fathers_day", _FD_3SUN_JUN, _UNOFF, "fr", "FR"),
    JurisdictionKnownHoliday("fathers_day", _FD_3SUN_JUN, _UNOFF, "nl", "NL"),
    JurisdictionKnownHoliday("fathers_day", _FD_MAR19, _UNOFF, "pt", "PT"),
    JurisdictionKnownHoliday("fathers_day", _FD_MAR19, _UNOFF, "es", "ES"),
    JurisdictionKnownHoliday("fathers_day", _FD_MAR19, _UNOFF, "ca", "ES"),
    JurisdictionKnownHoliday("fathers_day", _FD_MAR19, _UNOFF, "gl", "ES"),
    JurisdictionKnownHoliday("fathers_day", _FD_MAR19, _UNOFF, "it", "IT"),
    JurisdictionKnownHoliday("fathers_day", _FD_ASCENSION, _UNOFF, "de", "DE"),
)

#: ``(key, lang) -> JurisdictionKnownHoliday`` for the resolver.
JURISDICTION_KNOWN_BY_KEY_LANG: Dict[Tuple[str, str], JurisdictionKnownHoliday] = {
    (j.key, j.lang): j for j in JURISDICTION_KNOWN}

#: The set of second-tier base keys (``well_known.tab`` may name these too).
JURISDICTION_KNOWN_KEYS: FrozenSet[str] = frozenset(
    j.key for j in JURISDICTION_KNOWN)

_WELL_KNOWN_FILE = os.path.join(_DATA_DIR, "i18n", "well_known.tab")


def load_well_known_aliases(path: str = _WELL_KNOWN_FILE
                            ) -> Dict[Tuple[str, str], Tuple[str, ...]]:
    """Parse ``i18n/well_known.tab`` into ``(key, lang) -> (surface, ...)``.

    **File format** (``# civil-holidays-well-known v1``).  ``#``-lines are
    comments; each data row is pipe-delimited ``key | lang | surfaces``, where
    ``surfaces`` is one or more ``;;``-separated spoken forms of the holiday in
    that language ("christmas ;; christmas day ;; xmas").  These are the
    curated *spoken aliases* — the colloquial names a person actually says —
    kept as data, distinct from the official native names (in the ``.tab``
    files) and the display translations (``translations.tab``).  A missing file
    yields ``{}``.
    """
    out: Dict[Tuple[str, str], Tuple[str, ...]] = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            cols = [c.strip() for c in line.split("|")]
            if len(cols) < 3:
                raise ValueError(
                    f"malformed well-known line (need 3 columns): {line!r}")
            key, lang, cell = cols[0], cols[1], cols[2]
            if key not in WELL_KNOWN_BY_KEY and key not in JURISDICTION_KNOWN_KEYS:
                raise ValueError(
                    f"well_known.tab names unknown holiday key {key!r}")
            surfaces = tuple(s.strip() for s in cell.split(";;") if s.strip())
            out[(key, lang.lower())] = out.get((key, lang.lower()), ()) + surfaces
    return out


_WELL_KNOWN_ALIASES: Optional[Dict[Tuple[str, str], Tuple[str, ...]]] = None
_WELL_KNOWN_LOCK = threading.Lock()


def _well_known_aliases() -> Dict[Tuple[str, str], Tuple[str, ...]]:
    global _WELL_KNOWN_ALIASES
    if _WELL_KNOWN_ALIASES is None:
        with _WELL_KNOWN_LOCK:
            if _WELL_KNOWN_ALIASES is None:
                _WELL_KNOWN_ALIASES = load_well_known_aliases()
    return _WELL_KNOWN_ALIASES


def well_known_surfaces(lang: str) -> Dict[str, str]:
    """Every spoken surface -> well-known ``key`` for ``lang`` (lowercased).

    The surfaces are *derived* — never hand-listed per locale — by unioning the
    engine's existing i18n facts with the curated spoken-alias table:

    * the curated spoken aliases (``i18n/well_known.tab``) for ``(key, lang)``;
    * the anchor holiday's **display translation** for ``lang`` from
      ``translations.tab`` (an existing i18n fact);
    * the anchor holiday's **official native name** when ``lang`` is that
      name's own language (the government's own word).

    A language with no data for a holiday simply contributes no surface for it,
    so the reference is honestly scoped to what the locale's language actually
    names.
    """
    aliases = _well_known_aliases()
    out: Dict[str, str] = {}
    for wk in WELL_KNOWN:
        surfaces = set(aliases.get((wk.key, lang.lower()), ()))
        trans = _translations_for(wk.anchor_jurisdiction, wk.anchor_name)
        if lang in trans:
            surfaces.add(trans[lang])
        if wk.anchor_lang == lang:
            surfaces.add(wk.anchor_name)
        for surface in surfaces:
            out[surface.strip().lower()] = wk.key
    # Second tier: jurisdiction-bound holidays contribute a surface only in the
    # locale they are bound to (its surfaces live under the base key in
    # well_known.tab); the resolver picks the per-``(key, lang)`` rule.
    for j in JURISDICTION_KNOWN:
        if j.lang != lang.lower():
            continue
        for surface in aliases.get((j.key, lang.lower()), ()):
            out[surface.strip().lower()] = j.key
    return out


def well_known_source(key: str, lang: Optional[str] = None) -> str:
    """The provenance label ``"JURIS:name"`` for a well-known ``key``.

    First-tier keys resolve straight from :data:`WELL_KNOWN_BY_KEY`; a
    second-tier (jurisdiction-bound) key needs ``lang`` to pick the binding, and
    its label is the bound country plus the base key.
    """
    wk = WELL_KNOWN_BY_KEY.get(key)
    if wk is not None:
        return f"{wk.anchor_jurisdiction}:{wk.anchor_name}"
    if lang is not None:
        j = JURISDICTION_KNOWN_BY_KEY_LANG.get((key, lang.lower()))
        if j is not None:
            return f"{j.jurisdiction}:{j.key}"
    return f":{key}"
