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

    # ---- English quarter-days + Scottish term-days (fixed Gregorian) -------
    # The traditional English legal/church calendar's fixed feast-days on which
    # rents fell due and terms ran.  Each is a FIXED Gregorian date (NOT
    # Easter-relative), so it reuses ``FixedRule`` exactly like Christmas, and
    # carries only ``religious`` (a traditional feast, never a civil day-off).
    # The four English quarter-days are Lady Day (25 Mar), Midsummer (24 Jun),
    # Michaelmas (29 Sep) and Christmas (25 Dec, already carried as
    # ``christmas``).  Dates verified against the General Roman Calendar and the
    # standard English legal calendar.
    #
    # Lady Day = 25 Mar, the Feast of the Annunciation of the Blessed Virgin
    # Mary; also the English civil New Year until 1752 and a rent quarter-day.
    # Its surface embeds "Day" — the feast name is longer/more specific than a
    # bare "day" reading and must win longest-match, as Ash Wednesday does over
    # "Wednesday".
    WellKnownHoliday("lady_day", FixedRule(3, 25),
                     frozenset({"religious"}), "GB", "Lady Day", "en"),
    # Midsummer Day = 24 Jun, the Nativity of St John the Baptist; quarter-day.
    WellKnownHoliday("midsummer", FixedRule(6, 24),
                     frozenset({"religious"}), "GB", "Midsummer Day", "en"),
    # Michaelmas = 29 Sep, the Feast of St Michael and All Angels; quarter-day
    # and the Michaelmas legal/academic term.
    WellKnownHoliday("michaelmas", FixedRule(9, 29),
                     frozenset({"religious"}), "GB", "Michaelmas", "en"),
    # Candlemas = 2 Feb, the Presentation of the Lord (Purification of the
    # Virgin); a Scottish term-day.
    WellKnownHoliday("candlemas", FixedRule(2, 2),
                     frozenset({"religious"}), "GB", "Candlemas", "en"),
    # Lammas (Lammas Day) = 1 Aug, the loaf-mass harvest feast; Scottish
    # term-day.
    WellKnownHoliday("lammas", FixedRule(8, 1),
                     frozenset({"religious"}), "GB", "Lammas Day", "en"),
    # Martinmas = 11 Nov, the Feast of St Martin of Tours; Scottish term-day.
    WellKnownHoliday("martinmas", FixedRule(11, 11),
                     frozenset({"religious"}), "GB", "Martinmas", "en"),

    # ---- National / civil fixed-date holidays (es / fr / it / pt / en) ------
    # Major NATIONAL and CIVIL observances several locales bind by name. Each is
    # a FIXED Gregorian date, so it reuses ``FixedRule`` exactly like the feasts
    # above; the surfaces the locales speak live in ``i18n/well_known.tab``. A
    # public day-off carries ``public``; a religious feast that is also a civil
    # day off carries ``public religious``; a purely liturgical commemoration
    # carries ``religious``; a folk/observance day (not a statutory day off)
    # carries ``unofficial`` — mirroring how the sibling entries above are
    # categorised. Multi-word names bind as ONE holiday and win longest-match
    # over the bare month/"day"/weekday tokens they embed.

    # International Workers' Day / Labour Day = 1 May. A public holiday across
    # continental Europe (ES "Día del Trabajador", FR "Fête du Travail",
    # IT "Festa del Lavoro", PT "Dia do Trabalhador") and the folk "May Day" in
    # the anglosphere. (Source: national labour-day statutes; ILO.) Anchored on
    # the ES official name (which carries NO ``translations.tab`` row) on
    # purpose: the FR/IT/PT names auto-translate to en/de "Labour Day" /
    # "Tag der Arbeit", but the anglosphere/German "Labour Day"/"Labor Day" is a
    # DIFFERENT rule (1st Monday of Sep in the US, etc.), so those surfaces must
    # NOT be harvested. Every 1-May surface is listed explicitly per locale in
    # ``well_known.tab`` instead (en carries only "may day").
    WellKnownHoliday("labour_day", FixedRule(5, 1),
                     frozenset({"public"}), "ES", "Día del Trabajador", "es"),
    # Immaculate Conception = 8 Dec, the Solemnity of the Immaculate Conception
    # of the Blessed Virgin Mary; a Catholic holy day of obligation and a public
    # holiday in ES, IT and PT. (Source: General Roman Calendar; national
    # holiday laws.) Both civil and religious -> ``public religious``.
    WellKnownHoliday("immaculate_conception", FixedRule(12, 8),
                     frozenset({"public", "religious"}),
                     "ES", "Inmaculada Concepción", "es"),
    # Fiesta Nacional de España / Día de la Hispanidad = 12 Oct (Spain's national
    # day, commemorating 1492). (Source: Ley 18/1987.) Public holiday.
    WellKnownHoliday("hispanic_day", FixedRule(10, 12),
                     frozenset({"public"}), "ES", "Fiesta Nacional de España",
                     "es"),
    # Día de la Constitución = 6 Dec (Spanish Constitution Day, 1978
    # referendum). (Source: Spanish public-holiday calendar.) Public holiday.
    WellKnownHoliday("spain_constitution_day", FixedRule(12, 6),
                     frozenset({"public"}), "ES", "Día de la Constitución",
                     "es"),
    # Festa della Liberazione = 25 Apr (Italy's Liberation Day, 1945).
    # (Source: Italian national-holiday law, D.Lgs. 1946.) Public holiday.
    WellKnownHoliday("italy_liberation_day", FixedRule(4, 25),
                     frozenset({"public"}), "IT", "Festa della Liberazione",
                     "it"),
    # Festa della Repubblica = 2 Jun (Italian Republic Day, 1946 referendum).
    # (Source: Italian national-holiday law.) Public holiday.
    WellKnownHoliday("italy_republic_day", FixedRule(6, 2),
                     frozenset({"public"}), "IT", "Festa della Repubblica",
                     "it"),
    # Dia da Liberdade = 25 Apr (Portugal's Freedom Day, the 1974 Carnation
    # Revolution). (Source: Lei n.º 7/74.) Public holiday. A DIFFERENT event
    # from Italy's Liberation Day though the same civil date, hence its own key.
    WellKnownHoliday("portugal_freedom_day", FixedRule(4, 25),
                     frozenset({"public"}), "PT", "Dia da Liberdade", "pt"),
    # Dia de Portugal, de Camões e das Comunidades = 10 Jun (Portugal Day).
    # (Source: Portuguese public-holiday law.) Public holiday.
    WellKnownHoliday("portugal_day", FixedRule(6, 10),
                     frozenset({"public"}), "PT", "Dia de Portugal", "pt"),
    # Implantação da República = 5 Oct (Portuguese Republic Day, 1910).
    # (Source: Portuguese public-holiday law.) Public holiday.
    WellKnownHoliday("portugal_republic_day", FixedRule(10, 5),
                     frozenset({"public"}), "PT", "Implantação da República",
                     "pt"),
    # Restauração da Independência = 1 Dec (Restoration of Independence, 1640).
    # (Source: Portuguese public-holiday law.) Public holiday.
    WellKnownHoliday("portugal_restoration_day", FixedRule(12, 1),
                     frozenset({"public"}),
                     "PT", "Restauração da Independência", "pt"),
    # Fête Nationale française = 14 Jul (Bastille Day, 1789/1790). (Source: loi
    # du 6 juillet 1880.) Public holiday.
    WellKnownHoliday("bastille_day", FixedRule(7, 14),
                     frozenset({"public"}), "FR", "Fête Nationale", "fr"),
    # Fête de la Victoire = 8 May (Victoire 1945, V-E Day). (Source: loi
    # n° 81-893 du 2 octobre 1981.) Public holiday.
    WellKnownHoliday("ve_day", FixedRule(5, 8),
                     frozenset({"public"}), "FR", "Fête de la Victoire", "fr"),
    # Armistice = 11 Nov (Armistice of 1918 / Remembrance Day). A public holiday
    # in France; the anglosphere Remembrance/Armistice Day observance shares the
    # date. (Source: French public-holiday law; Commonwealth Remembrance Day.)
    WellKnownHoliday("armistice", FixedRule(11, 11),
                     frozenset({"public"}), "FR", "Armistice", "fr"),
    # Juneteenth = 19 Jun (U.S. Juneteenth National Independence Day, federal
    # holiday since 2021). (Source: Pub. L. 117-17.) Public holiday.
    WellKnownHoliday("juneteenth", FixedRule(6, 19),
                     frozenset({"public"}), "US", "Juneteenth", "en"),
    # Cinco de Mayo = 5 May (commemorates the 1862 Battle of Puebla; a widely
    # observed cultural day in the U.S.). NOT a U.S. federal day off, so
    # ``unofficial``. Its name embeds "Mayo" (the Spanish/Italian month name) —
    # the full holiday surface must win longest-match over the bare month token.
    WellKnownHoliday("cinco_de_mayo", FixedRule(5, 5),
                     frozenset({"unofficial"}), "US", "Cinco de Mayo", "en"),
    # Groundhog Day = 2 Feb (North American folk observance). ``unofficial``.
    WellKnownHoliday("groundhog_day", FixedRule(2, 2),
                     frozenset({"unofficial"}), "US", "Groundhog Day", "en"),
    # Earth Day = 22 Apr (environmental observance since 1970). ``unofficial``.
    WellKnownHoliday("earth_day", FixedRule(4, 22),
                     frozenset({"unofficial"}), "US", "Earth Day", "en"),
    # All Souls' Day = 2 Nov, the Commemoration of All the Faithful Departed
    # ("In Commemoratione Omnium Fidelium Defunctorum"); a liturgical feast the
    # day after All Saints'. Purely liturgical -> ``religious``. (Source:
    # General Roman Calendar.)
    WellKnownHoliday("all_souls", FixedRule(11, 2),
                     frozenset({"religious"}), "VA", "All Souls' Day", "en"),
    # April Fools' Day = 1 Apr (folk day of pranks). ``unofficial``. Its name
    # embeds the month "April" and the word "Day" — the full surface must win
    # longest-match so a bare "april" reading never strands a "fools day" tail.
    WellKnownHoliday("april_fools", FixedRule(4, 1),
                     frozenset({"unofficial"}), "US", "April Fools' Day", "en"),

    # ---- National / civil fixed-date holidays (round 2: pl uk cs ru nl de sv
    #      tr fi hu da nb el ro) --------------------------------------------
    # A second sweep of NATIONAL and CIVIL observances that native reviewers of
    # the Slavic / Uralic / Hellenic / Turkic / Nordic corpora bind by name.
    # Each is a FIXED Gregorian date reusing ``FixedRule`` exactly like the
    # feasts above; the spoken surfaces (incl. the inflected forms reviewers
    # cited) live per-locale in ``i18n/well_known.tab``. Statutory days off carry
    # ``public``; a traditional feast that is not a day off carries ``religious``
    # or ``unofficial``. Multi-word names bind as ONE holiday and win
    # longest-match over the bare month / "day" / weekday tokens they embed.
    # Holidays already carried by a shared key (Labour Day = 1 May ->
    # ``labour_day``; Assumption = 15 Aug -> ``assumption``; All Saints = 1 Nov
    # -> ``all_saints``; Epiphany = 6 Jan -> ``epiphany``; New Year = 1 Jan ->
    # ``new_year``; the 8 May V-E Day -> ``ve_day``) only gain a per-locale
    # surface in the ``.tab`` and are NOT re-keyed here.

    # Poland. Konstytucji 3 Maja = 3 May (Constitution of 3 May 1791, the
    # world's second written constitution; public holiday, Dz.U. 1990). Święto
    # Niepodległości = 11 Nov (National Independence Day, 1918; Dz.U. 1937 /
    # 1989). Distinct from the 11 Nov ``armistice`` (FR) though same date.
    WellKnownHoliday("poland_constitution_day", FixedRule(5, 3),
                     frozenset({"public"}), "PL",
                     "Święto Konstytucji 3 Maja", "pl"),
    WellKnownHoliday("poland_independence_day", FixedRule(11, 11),
                     frozenset({"public"}), "PL",
                     "Narodowe Święto Niepodległości", "pl"),

    # Ukraine. День незалежності = 24 Aug (Independence Day, 1991). День
    # Конституції = 28 Jun (Constitution Day, 1996). День захисників і
    # захисниць = 14 Oct (Defenders Day; decree since 2014, statute 2021).
    WellKnownHoliday("ukraine_independence_day", FixedRule(8, 24),
                     frozenset({"public"}), "UA",
                     "День незалежності України", "uk"),
    WellKnownHoliday("ukraine_constitution_day", FixedRule(6, 28),
                     frozenset({"public"}), "UA",
                     "День Конституції України", "uk"),
    WellKnownHoliday("ukraine_defenders_day", FixedRule(10, 14),
                     frozenset({"public"}), "UA",
                     "День захисників і захисниць України", "uk"),

    # Международный женский день / Міжнародний жіночий день = 8 Mar
    # (International Women's Day; a public day off in RU, UA and much of the
    # former USSR). Shared RU/UA key.
    WellKnownHoliday("womens_day", FixedRule(3, 8),
                     frozenset({"public"}), "RU",
                     "Международный женский день", "ru"),
    # День Победы / День перемоги = 9 May (the Soviet/post-Soviet Victory Day,
    # a full day later than the Western 8 May ``ve_day`` — a genuinely
    # different civil date, hence its own key). Shared RU/UA key.
    WellKnownHoliday("victory_day_east", FixedRule(5, 9),
                     frozenset({"public"}), "RU", "День Победы", "ru"),

    # Czechia. Cyril a Metoděj = 5 Jul (Saints Cyril & Methodius). Jan Hus =
    # 6 Jul (burning of Jan Hus, 1415). Den české státnosti = 28 Sep (St
    # Wenceslas / Czech Statehood). Vznik samostatného čs. státu = 28 Oct
    # (Czechoslovak independence, 1918). Boj za svobodu a demokracii = 17 Nov
    # (Struggle for Freedom and Democracy, 1939/1989). All public holidays
    # (zákon č. 245/2000 Sb.).
    WellKnownHoliday("cyril_methodius_day", FixedRule(7, 5),
                     frozenset({"public", "religious"}), "CZ",
                     "Den slovanských věrozvěstů Cyrila a Metoděje", "cs"),
    WellKnownHoliday("jan_hus_day", FixedRule(7, 6),
                     frozenset({"public"}), "CZ",
                     "Den upálení mistra Jana Husa", "cs"),
    WellKnownHoliday("czech_statehood_day", FixedRule(9, 28),
                     frozenset({"public"}), "CZ",
                     "Den české státnosti", "cs"),
    WellKnownHoliday("czechoslovak_state_day", FixedRule(10, 28),
                     frozenset({"public"}), "CZ",
                     "Den vzniku samostatného československého státu", "cs"),
    WellKnownHoliday("czech_freedom_day", FixedRule(11, 17),
                     frozenset({"public"}), "CZ",
                     "Den boje za svobodu a demokracii", "cs"),

    # Russia. День России = 12 Jun (Russia Day, 1990). День защитника
    # Отечества = 23 Feb (Defender of the Fatherland Day). День народного
    # единства = 4 Nov (Unity Day). Public holidays (Labour Code art. 112).
    WellKnownHoliday("russia_day", FixedRule(6, 12),
                     frozenset({"public"}), "RU", "День России", "ru"),
    WellKnownHoliday("defender_of_fatherland_day", FixedRule(2, 23),
                     frozenset({"public"}), "RU",
                     "День защитника Отечества", "ru"),
    WellKnownHoliday("russia_unity_day", FixedRule(11, 4),
                     frozenset({"public"}), "RU",
                     "День народного единства", "ru"),

    # Netherlands. Koningsdag = 27 Apr (King's Day, King Willem-Alexander's
    # birthday; public holiday). Bevrijdingsdag = 5 May (Liberation Day, 1945).
    # Sinterklaas = 5 Dec (St Nicholas' Eve; a folk gift-giving day, not a
    # statutory day off -> ``unofficial``).
    WellKnownHoliday("netherlands_kings_day", FixedRule(4, 27),
                     frozenset({"public"}), "NL", "Koningsdag", "nl"),
    WellKnownHoliday("netherlands_liberation_day", FixedRule(5, 5),
                     frozenset({"public"}), "NL", "Bevrijdingsdag", "nl"),
    WellKnownHoliday("sinterklaas", FixedRule(12, 5),
                     frozenset({"unofficial"}), "NL", "Sinterklaas", "nl"),

    # Germany. Tag der Deutschen Einheit = 3 Oct (German Unity Day, 1990; the
    # sole nationwide statutory holiday). Nikolaustag = 6 Dec (St Nicholas'
    # Day; a customary feast, not a day off -> ``religious``). Tag der Arbeit
    # (1 May) is the shared ``labour_day``.
    WellKnownHoliday("german_unity_day", FixedRule(10, 3),
                     frozenset({"public"}), "DE",
                     "Tag der Deutschen Einheit", "de"),
    WellKnownHoliday("nikolaus", FixedRule(12, 6),
                     frozenset({"religious"}), "DE", "Nikolaustag", "de"),

    # Sweden. Sveriges nationaldag = 6 Jun (National Day, 1523/1809; public
    # holiday since 2005). Trettondedag jul (6 Jan) is the shared ``epiphany``.
    WellKnownHoliday("sweden_national_day", FixedRule(6, 6),
                     frozenset({"public"}), "SE", "Sveriges nationaldag", "sv"),

    # Turkey. Cumhuriyet Bayramı = 29 Oct (Republic Day, 1923). Zafer Bayramı
    # = 30 Aug (Victory Day, 1922). Ulusal Egemenlik ve Çocuk Bayramı = 23 Apr
    # (National Sovereignty & Children's Day, 1920). Atatürk'ü Anma, Gençlik ve
    # Spor Bayramı = 19 May (Commemoration of Atatürk, Youth & Sports Day).
    # Demokrasi ve Millî Birlik Günü = 15 Jul (Democracy & National Unity Day,
    # 2016). Public holidays.
    WellKnownHoliday("turkey_republic_day", FixedRule(10, 29),
                     frozenset({"public"}), "TR", "Cumhuriyet Bayramı", "tr"),
    WellKnownHoliday("turkey_victory_day", FixedRule(8, 30),
                     frozenset({"public"}), "TR", "Zafer Bayramı", "tr"),
    WellKnownHoliday("turkey_sovereignty_day", FixedRule(4, 23),
                     frozenset({"public"}), "TR",
                     "Ulusal Egemenlik ve Çocuk Bayramı", "tr"),
    WellKnownHoliday("turkey_youth_day", FixedRule(5, 19),
                     frozenset({"public"}), "TR",
                     "Atatürk'ü Anma, Gençlik ve Spor Bayramı", "tr"),
    WellKnownHoliday("turkey_democracy_day", FixedRule(7, 15),
                     frozenset({"public"}), "TR",
                     "Demokrasi ve Millî Birlik Günü", "tr"),

    # Finland. Itsenäisyyspäivä = 6 Dec (Independence Day, 1917). Vappu (1 May)
    # is the shared ``labour_day``; Loppiainen (6 Jan) the shared ``epiphany``.
    WellKnownHoliday("finland_independence_day", FixedRule(12, 6),
                     frozenset({"public"}), "FI", "Itsenäisyyspäivä", "fi"),

    # Hungary. Nemzeti ünnep (1848) = 15 Mar (1848 Revolution). Az
    # államalapítás ünnepe = 20 Aug (St Stephen / State Foundation). Az 1956-os
    # forradalom emléknapja = 23 Oct (1956 Revolution). A munka ünnepe (1 May)
    # is the shared ``labour_day``. Public holidays.
    WellKnownHoliday("hungary_1848_day", FixedRule(3, 15),
                     frozenset({"public"}), "HU", "Nemzeti ünnep", "hu"),
    WellKnownHoliday("hungary_state_foundation_day", FixedRule(8, 20),
                     frozenset({"public"}), "HU",
                     "Az államalapítás ünnepe", "hu"),
    WellKnownHoliday("hungary_1956_day", FixedRule(10, 23),
                     frozenset({"public"}), "HU",
                     "Az 1956-os forradalom emléknapja", "hu"),

    # Denmark. Grundlovsdag = 5 Jun (Constitution Day, 1849; a partial day off,
    # widely observed -> ``public``).
    WellKnownHoliday("denmark_constitution_day", FixedRule(6, 5),
                     frozenset({"public"}), "DK", "Grundlovsdag", "da"),

    # Norway. Grunnlovsdag / syttende mai = 17 May (Constitution Day, 1814;
    # the national day). Arbeidernes dag (1 May) is the shared ``labour_day``.
    WellKnownHoliday("norway_constitution_day", FixedRule(5, 17),
                     frozenset({"public"}), "NO", "Grunnlovsdag", "nb"),

    # Greece. 25η Μαρτίου = 25 Mar (Independence Day, 1821; also the
    # Annunciation -> ``public religious``). Επέτειος του Όχι / 28η Οκτωβρίου =
    # 28 Oct ("Ohi Day", 1940). Πρωτομαγιά (1 May) is the shared ``labour_day``;
    # Θεοφάνεια (6 Jan) the shared ``epiphany``.
    WellKnownHoliday("greece_independence_day", FixedRule(3, 25),
                     frozenset({"public", "religious"}), "GR",
                     "Εικοστή Πέμπτη Μαρτίου", "el"),
    WellKnownHoliday("greece_ohi_day", FixedRule(10, 28),
                     frozenset({"public"}), "GR", "Επέτειος του Όχι", "el"),

    # Romania. Ziua Copilului = 1 Jun (Children's Day; public holiday since
    # 2017). Ziua Națională = 1 Dec (National Day / Great Union, 1918; distinct
    # from the 1 Dec ``portugal_restoration_day``). Unirea Principatelor =
    # 24 Jan (Union of the Principalities, 1859). Anul Nou (1 Jan) is the shared
    # ``new_year``; Ziua Muncii (1 May) the shared ``labour_day``; Adormirea
    # (15 Aug) the shared ``assumption``.
    WellKnownHoliday("romania_childrens_day", FixedRule(6, 1),
                     frozenset({"public"}), "RO", "Ziua Copilului", "ro"),
    WellKnownHoliday("romania_national_day", FixedRule(12, 1),
                     frozenset({"public"}), "RO",
                     "Ziua Națională a României", "ro"),
    WellKnownHoliday("romania_union_day", FixedRule(1, 24),
                     frozenset({"public"}), "RO",
                     "Ziua Unirii Principatelor Române", "ro"),

    # NOTE Twelfth Night (5 Jan, eve of the Epiphany) is deliberately NOT added:
    # "Twelfth Night" is pinned as a proper noun that must resolve to None (not a
    # daypart "night") by test_clock_daypart_night_fixes; adding it as a holiday
    # would collide with that contract.  Epiphany itself (6 Jan) is already
    # carried as ``epiphany``.
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

    Surface precedence: a curated spoken alias or the anchor's own official
    native name is *authoritative* for the language and always wins; a
    **display translation** of a foreign holiday is only a fallback that fills
    a surface no authoritative source already claims. National/civil days make
    this matter — Portugal's own "dia da república" (a pt alias for the 5 Oct
    ``portugal_republic_day``) must not be shadowed by the pt display
    translation of Turkey's 29 Oct ``turkey_republic_day`` ("Dia da
    República"). Authoritative-wins keeps each language bound to the day it
    actually speaks of, while a translation still supplies surfaces for a
    foreign holiday the language names no other way.
    """
    aliases = _well_known_aliases()
    out: Dict[str, str] = {}
    authoritative: set = set()
    translated: list = []
    for wk in WELL_KNOWN:
        surfaces = set(aliases.get((wk.key, lang.lower()), ()))
        if wk.anchor_lang == lang:
            surfaces.add(wk.anchor_name)
        for surface in surfaces:
            canon = surface.strip().lower()
            out[canon] = wk.key
            authoritative.add(canon)
        trans = _translations_for(wk.anchor_jurisdiction, wk.anchor_name)
        if lang in trans:
            translated.append((trans[lang].strip().lower(), wk.key))
    # Display translations fill only the surfaces no authoritative source owns
    # (later translations still win over earlier ones, as before).
    for canon, key in translated:
        if canon not in authoritative:
            out[canon] = key
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
