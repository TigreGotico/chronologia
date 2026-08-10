"""Tokens -> matches, with precedence and longest-span resolution.

Each construction order is matched by a plain backtracking walk over its
:class:`SlotElement` sequence (optional slots try both present and
skipped; the longest consumption wins).  Slot binding is a single lookup
into the language's typed vocab maps -- there are no per-language regexes
to debug, only named slots.

Overlap resolution follows the doc: among competing matches the longest
span wins, ties broken by precedence (era > scoped > calendar > ...).
Selected matches never overlap.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from chronologia.extract import tokenizer
from chronologia.calendars import CALENDARS
from chronologia.extract.compiler import CompiledSpec
from chronologia.extract.model import (LangSpec, Match, SlotElement,
                                           Token)

# the literal shapes a slot may bind are exactly the shapes the tokenizer kept
# whole, so they are compiled from the tokenizer's own patterns rather than
# restated here -- a second copy of a regex this subtle drifts out of step, and
# a slot that accepts more than the tokenizer emits can never fire anyway.
_ISO = re.compile(tokenizer._ISO)
_ISOWEEK = re.compile(tokenizer._ISOWEEK)
_NUMDATE = re.compile(tokenizer._NUMDATE_ANY)
_CLOCK = re.compile(tokenizer._CLOCK)


def _calendar_for_surface(spec: LangSpec, surface: str):
    """Which registered calendar owns a calendar-month surface (surfaces are
    unique across calendars within a language, so the first hit is the
    only hit)."""
    for cal_key, months in spec.calendar_months.items():
        if surface in months:
            return cal_key
    return None


#: The years a bare numeral may name.  A written year is a 4-5 digit run, so
#: the window is 1000..99999: four digits for the Common Era, five for the
#: Human/Holocene Era form (HE = CE + 10000, see :mod:`chronologia.eras`) that
#: "the year 12000" is written in.  Every path that reads a year from a plain
#: number -- digits here, a spelled composition in the number fold, a
#: NUM x SCALE phrase in the resolver -- measures against this one window, so
#: a magnitude no digit year could carry is refused rather than resolved.
GYEAR_MIN, GYEAR_MAX = 1000, 99999


@dataclass(frozen=True)
class MatchCandidate:
    match: Match
    precedence: int


def _bind(element: SlotElement, token: Token, spec: LangSpec) -> bool:
    name = element.name
    if not element.is_slot:
        return token.text in spec.connectors.get(name, frozenset())
    if name == "NUM":
        return token.is_number
    if name == "UNIT":
        return token.text in spec.units
    if name == "DMUNIT":
        # day/month only -- the narrow sibling of UNIT that licenses the
        # "Nth UNIT of <bare year>" order (no "the year"/ISO-week wording).
        # Week and quarter already resolve a bare trailing year through their
        # own dedicated constructions (iso_week_ref, quarter_ref); adding them
        # here too would create a same-span precedence tie against those
        # constructions with no guarantee scoped_ordinal's plain WEEK_OF_YEAR/
        # day-counting semantics agree with iso_week_ref's ISO semantics, so
        # this slot deliberately stays narrower than UNIT.
        return spec.units.get(token.text) in ("day", "month")
    if name == "USG":
        return token.text in spec.singular_units
    if name in ("MARKER", "DIRECTION_MARKER"):
        return token.text in spec.directions
    if name == "DAY_WORD":
        return token.text in spec.named_days
    if name == "REL_MARKER":
        return token.text in spec.rel_markers
    if name == "WEEKEND":
        return token.text in spec.weekend_words
    if name == "WEEKDAY":
        return token.text in spec.weekdays
    if name == "WEEKDAYFULL":
        return token.text in spec.weekday_full
    if name == "HOLIDAY":
        return token.text in spec.holidays
    if name == "MONTH":
        return token.text in spec.months
    if name == "CAL_MONTH":
        return any(token.text in months
                   for months in spec.calendar_months.values())
    if name == "DAY":
        return token.is_number and 1 <= (token.value or 0) <= 31
    if name == "ERA":
        # an era marker trailing a bare YEAR ("500 BC", "44 AD") so a
        # construction that grounds on a year -- calendar_date,
        # weekend_of_month, quarter_ref -- can compose with an era-qualified
        # year exactly like the dedicated era_bc/era_ad constructions do,
        # instead of silently reading the number as a bare (common-era)
        # Gregorian year and stranding the marker as remainder.
        #
        # Deliberately BC/AD only, not the full offset-era set:
        # * calendar-backed eras (hijri, solar_hijri) number a DIFFERENT
        #   calendar's own months, so mixing them with a Gregorian
        #   MONTH/quarter slot would be incoherent -- those stay on their
        #   own dedicated era_* constructions.
        # * Buddhist Era's "be" marker is guarded to fire ONLY at
        #   end-of-clause everywhere else in the grammar (see era_buddhist_be
        #   construction) specifically because it collides with the common
        #   English verb "be" ("will june be there").  This slot has no
        #   such position guard, and a resolver decline (``None``) here
        #   does NOT fall back to a shorter match without ERA -- the
        #   matcher tries the longest candidate span first and does not
        #   retry -- so speculatively binding "be" would silently break
        #   ordinary "june" + verb-"be" sentences that used to resolve
        #   fine.  Buddhist-Era composition with these three constructions
        #   stays unsupported (refuses -- see the resolvers' guards) rather
        #   than risk that regression.
        return (token.text in spec.connectors.get("bc", frozenset())
                or token.text in spec.connectors.get("ad", frozenset()))
    if name == "YEAR":
        # a bare number reads as a year when it is too big to be a day/count
        # (>=32) or written with >=4 digits; an apostrophe cue ("'20", "'08")
        # licenses even a small two-digit run as a year -- it is the strong
        # signal a two-digit year was intended, so it is not silently dropped.
        # The length checks measure the DIGIT run, not the raw: a 2-digit
        # ordinal ("10th") is 4 raw chars (two digits + "th") and used to sneak
        # "March 5th, 10th" into a bogus GYEAR=10 reading, yet a language year
        # surface carries its own suffix too (Basque "2020ko" = "of 2020"), so
        # counting digits keeps the real 4-digit year while rejecting the
        # 2-digit ordinal.
        n_digits = sum(c.isdigit() for c in token.raw)
        return token.is_number and ((token.value or 0) >= 32
                                    or n_digits >= 4
                                    or (token.apostrophe and n_digits == 2))
    if name == "YEARANY":
        # like YEAR, but WITHOUT the >=32 lower bound: used only by
        # constructions whose leading word already disambiguates a trailing
        # number as a year rather than a day/count ("new year 27" cannot mean
        # a day-of-month -- there is no month/day slot in this construction),
        # so the two-digit-year pivot must bind uniformly regardless of
        # whether the value happens to be <32 ("27") or >=32 ("99").  Still
        # requires >=2 digits so a stray single digit doesn't get read as a
        # year.
        n_digits = sum(c.isdigit() for c in token.raw)
        return token.is_number and n_digits >= 2
    if name == "GYEAR":
        # a standalone Gregorian year: a bare digit run inside the GYEAR
        # window, so small integers ("5", "123") and digit soup
        # ("1234567890") never read as a year when nothing else anchors them
        raw = token.raw.rstrip(".")
        # an apostrophe two-digit run is a bare year on its own ("'99", "in
        # '05"): the apostrophe licenses it even though it falls below the
        # 4-digit GYEAR window -- the resolver pivots it through the anchor
        # window.  A leading zero here is a written year digit ("'05"), not a
        # clock reading, so it is allowed for the apostrophe form only.
        if token.apostrophe and raw.isdigit() and len(raw) == 2:
            return True
        # a leading zero marks a clock reading ("0600"), never a year
        return (token.is_number and raw.isdigit() and raw[0] != "0"
                and GYEAR_MIN <= int(raw) <= GYEAR_MAX)
    if name in ("MILTIME", "MILTIMEZ"):
        raw = token.raw.rstrip(".")
        if not (token.is_number and raw.isdigit() and len(raw) == 4):
            return False
        hh, mm = int(raw[:2]), int(raw[2:])
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            return False
        # MILTIMEZ (the bare, no-"hours" form) only fires with a leading zero,
        # so "1500" stays a year while "0600" reads as a clock
        return raw[0] == "0" if name == "MILTIMEZ" else True
    if name == "MILTIMENZ":
        # a bare four-digit HHMM whose leading digit is NOT zero -- the shape
        # that reads as a year on its own ("1500"), licensed to a clock only
        # when a military zone qualifier follows ("1500 Zulu", "1500Z").  The
        # leading-zero forms are already MILTIMEZ, so excluding them here keeps
        # "0800Z"/"0300 Zulu" resolving through their existing order, unchanged.
        raw = token.raw.rstrip(".")
        if not (token.is_number and raw.isdigit() and len(raw) == 4):
            return False
        hh, mm = int(raw[:2]), int(raw[2:])
        return 0 <= hh <= 23 and 0 <= mm <= 59 and raw[0] != "0"
    if name == "LANDMARK":
        return token.text in spec.clock_landmarks
    if name == "DAYPART":
        return token.text in spec.dayparts
    if name == "DPDEIX":
        return token.text in spec.daypart_deictics
    if name == "ZONE":
        # the base acronym ("utc"/"gmt") must be a known zone surface; any
        # trailing signed offset ("utc+2") rides on the same token and is
        # parsed at resolve time.
        base = re.match(r"[a-z]+", token.text)
        if base is not None:
            return base.group(0) in spec.clock_zones
        # a bare RFC/ISO signed numeric offset ("-0500", "+05:30") is a zone
        # with no acronym; its fixed offset is parsed at resolve time.
        return re.fullmatch(r"[+-](?:0\d|1[0-4]):?[0-5]\d", token.text) is not None
    if name == "QUANT":
        return token.text in spec.quantifiers
    if name == "ISO":
        return _ISO.fullmatch(token.text) is not None
    if name == "ISOWEEK":
        return _ISOWEEK.fullmatch(token.text) is not None
    if name == "NUMDATE":
        return _NUMDATE.fullmatch(token.text) is not None
    # -- clock_time slots --------------------------------------------------
    if name == "CLOCK":
        return _CLOCK.fullmatch(token.text) is not None
    if name in ("DOTCLOCK", "PADCLOCK"):
        # the dot as a clock separator -- the British/European 24-hour
        # timetable form "HH.MM" ("the 07.42 to London", "departs at 15.30").
        # The tokenizer reads a dotted run as a decimal number ("07.42" ->
        # value 7.42), so the shape is recovered from the surviving ``raw``:
        # a valid wall clock, hour 0..23 and minute 00..59, spelled with a
        # single interior dot.  PADCLOCK additionally requires the zero-padded
        # two-digit hour of the timetable convention -- the stricter form used
        # where the licensing cue is only a leading article, so "the 3.14
        # release" keeps its decimal reading while "the 09.15 departure" reads
        # as a clock.  Licensing lives in the grammar orders (a leading "at",
        # a trailing meridiem, or an article on the padded form); an uncued
        # bare decimal binds no clock order and stays a number.
        m = re.fullmatch(r"(\d{1,2})\.(\d{2})", token.raw)
        if m is None:
            return False
        hh, mm = int(m.group(1)), int(m.group(2))
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            return False
        return len(m.group(1)) == 2 if name == "PADCLOCK" else True
    if name == "HOUR":
        # an hour is an integer count -- a dotted decimal ("7.42") is the
        # timetable clock's HH.MM, handled by DOTCLOCK, not an hour whose
        # fractional minutes get silently truncated to :00.
        return (token.is_number and "." not in token.raw
                and 0 <= (token.value or 0) <= 24)
    if name == "MINUTE":
        return token.is_number and 0 <= (token.value or 0) <= 59
    if name == "QUARTS":
        # the quarter *count* of the Catalan sistema de campanar ("dos quarts
        # de deu"): how many quarters of the coming hour have already struck.
        # Bound generously (0..9) so a nonsense count still binds here and is
        # refused explicitly by the resolver, rather than falling through to
        # some other construction that would guess a time.
        return token.is_number and 0 <= (token.value or 0) <= 9
    if name == "FRACTION":
        return token.text in spec.clock_fractions
    if name == "CLOCKDIR":
        return token.text in spec.clock_dirs
    if name == "MERIDIEM":
        return token.text in spec.meridiems
    # -- season_ref / scoped_ordinal slots ---------------------------------
    if name == "SEASON":
        return token.text in spec.seasons
    if name == "EVENT":
        return token.text in spec.solar_events
    if name == "SOLARQUAL":
        return token.text in spec.solar_quals
    if name in ("ORD", "SORD"):
        return token.is_number and (token.value or 0) >= 1
    if name == "NORD":
        # a *digit* day-of-month ordinal ("3rd", "15th") -- the surface run
        # still carries its ordinal suffix, so ``raw`` is not all-digits.
        # Spelled ordinals ("first", "third") fold to a bare-digit ``raw``
        # and are deliberately excluded: "on the third floor"/"on the first
        # try" are homographs, not dates.  A plain cardinal ("3") is excluded
        # for the same reason.  Range-capped 1..31 (a day-of-month).
        raw = token.raw.rstrip(".")
        return (token.is_number and 1 <= (token.value or 0) <= 31
                and raw[:1].isdigit() and not raw.isdigit())
    if name in ("SUBH", "SUBM", "SUBS"):
        return token.is_number and (token.value or 0) >= 0
    if name == "SEL_UNIT":
        return token.text in spec.scope_units or token.text in spec.units
    if name == "CMUNIT":
        # a century or millennium scope unit ONLY -- the postposed Romance
        # ordinal ("século XII", "secolo XII") binds this, never a plain unit
        # like "anno"/"semana" (which would hijack a year or ISO-week reading)
        return spec.scope_units.get(token.text) in ("century", "millennium")
    if name == "SCOPE_UNIT":
        # the outer scope of an ordinal ("the third CENTURY") is never a
        # sub-day unit -- excluding hour/minute keeps "15 uur"/"15 uhr" a
        # clock, not a spurious "15th hour" scoped ordinal (matters where a
        # unit word doubles as the o'clock word, e.g. Dutch "uur").
        if token.text in spec.scope_units:
            return True
        kind = spec.units.get(token.text)
        return kind is not None and kind not in ("hour", "minute", "second")
    # -- day-cycle / regnal / roman slots ----------------------------------
    if name == "CYCLE_DAY":
        return token.text in spec.cycle_positions
    if name == "ERANAME":
        return token.text in spec.regnal_names
    if name == "ANCHOR_DAY":
        return token.text in spec.roman_anchors
    if name == "ARCHON":
        return token.text in spec.archon_names
    if name == "PRIDIE":
        return token.text in spec.connectors.get("pridie", frozenset())
    # -- deep-time / named-period slots ------------------------------------
    if name == "PERIOD":
        return token.text in spec.periods
    if name == "SCALE":
        return token.text in spec.scales
    if name == "PART":
        return token.text in spec.period_parts
    if name == "DECADE":
        return token.text in spec.decade_words
    if name == "DNUM":
        # a numeral that *names* a decade, for the languages whose decade
        # phrase is a framing year-word plus a plain number ("les années 1980",
        # "gli anni ottanta", "anii optzeci").  A decade opens on a whole ten,
        # so only a whole ten binds here: either a bare tens the nearest-past
        # century convention places ("les années 80"), or a four-digit year
        # that is itself the base of its decade ("les années 1980").  The same
        # framing word introduces an ordinary run of years -- "les années
        # 1914-1918" are the war years, not a decade -- and refusing 1914 here
        # rather than in the resolver is what leaves that reading to the
        # range machinery, since the parse winner is chosen before any
        # construction is resolved.
        if not token.is_number or token.value is None:
            return False
        n = token.value
        if not float(n).is_integer() or int(n) % 10:
            return False
        n = int(n)
        return 0 <= n <= 90 or GYEAR_MIN <= n <= GYEAR_MAX
    return False


def _connector_span(name: str, tokens: Tuple[Token, ...], ti: int,
                    spec: LangSpec) -> int:
    """Longest run of tokens from ``ti`` matching a connector surface.

    A connector surface may be **multi-word** ("vor christus", "v. chr.",
    "before the present"): it is compared word-for-word against the token
    stream, punctuation-split the same way the tokenizer splits it (dots
    dropped).  Returns the number of tokens consumed (0 if none matched).
    """
    surfaces = spec.connectors.get(name)
    if not surfaces or ti >= len(tokens):
        return 0
    best = 0
    for surf in surfaces:
        words = surf.lower().replace(".", " ").split()
        n = len(words)
        if n and ti + n <= len(tokens) and all(
                tokens[ti + k].text == words[k] for k in range(n)):
            best = max(best, n)
    return best


def _walk(elements: Tuple[SlotElement, ...], tokens: Tuple[Token, ...],
          ei: int, ti: int, spec: LangSpec,
          slots: Dict[str, Token]) -> Optional[Tuple[int, Dict[str, Token]]]:
    """The single longest completion of ``elements`` from token ``ti``.

    Returns the ``(end, slots)`` with the greatest end position, or ``None`` if
    the elements cannot be matched from here. Branches are explored in a fixed
    order (bind, suffix-absorb, optional-skip) and ties are broken toward the
    earlier branch -- identical to ``max(all_completions, key=end)`` with
    Python's first-maximal tie-break, since that max is associative. Keeping
    only the running best (rather than materialising every completion) turns the
    exponential *space* of an order with many optional slots into O(depth), and
    avoids the list-concatenation churn on the hot path.
    """
    if ei == len(elements):
        return (ti, dict(slots))
    el = elements[ei]
    best: Optional[Tuple[int, Dict[str, Token]]] = None

    def consider(cand: Optional[Tuple[int, Dict[str, Token]]]) -> None:
        nonlocal best
        # strict ``>`` keeps the earlier branch on a tie (first-maximal)
        if cand is not None and (best is None or cand[0] > best[0]):
            best = cand

    if el.is_slot:
        if ti < len(tokens) and _bind(el, tokens[ti], spec):
            bound = dict(slots)
            bound[el.name] = tokens[ti]
            consider(_walk(elements, tokens, ei + 1, ti + 1, spec, bound))
            # A digit ordinal the language writes with a hyphenated
            # inflectional suffix ("5-е", "2-го") tokenises as the number plus
            # a stray suffix letter; absorb that trailing suffix so the numeral
            # binds its day-of-month / Nth-weekday slot exactly as the spelled
            # ordinal ("второе") does.  Only fires where a language declares the
            # suffix surfaces (ordinal_suffix connector, Russian and kin); the
            # decade "1980-е годы" still matches through its own plural slot on
            # the non-absorbing path, so nothing changes there.
            suffixes = spec.connectors.get("ordinal_suffix")
            if (suffixes and tokens[ti].is_number
                    and ti + 1 < len(tokens)
                    and tokens[ti + 1].text in suffixes):
                consider(_walk(elements, tokens, ei + 1, ti + 2, spec, bound))
    else:
        consumed = _connector_span(el.name, tokens, ti, spec)
        if consumed:
            consider(_walk(elements, tokens, ei + 1, ti + consumed, spec,
                           slots))
    if el.optional:
        consider(_walk(elements, tokens, ei + 1, ti, spec, slots))
    return best


class ConstructionMatcher:
    """Runs a compiled table over a token stream."""

    def __init__(self, compiled: CompiledSpec):
        self.compiled = compiled
        self.spec = compiled.spec

    def _candidates(self, tokens: Tuple[Token, ...]) -> List[MatchCandidate]:
        out: List[MatchCandidate] = []
        for precedence, name, order in self.compiled.table:
            for start in range(len(tokens)):
                best = _walk(order.elements, tokens, 0, start, self.spec, {})
                if best is None:
                    continue
                end, slots = best
                if end > start:
                    # "the year 1 am" is the Anno Mundi era marker, not the
                    # 01:00 ante-meridiem clock: veto a bare HOUR+MERIDIEM
                    # clock reading whose hour sits immediately after a
                    # year-word ("year"/"years"), so the clock parser never
                    # captures the era-marked value.
                    if (name == "clock_time" and "MERIDIEM" in slots
                            and "CLOCK" not in slots and start > 0
                            and tokens[start - 1].text
                            in self.spec.connectors.get(
                                "year_word", frozenset())):
                        continue
                    # A subtractive-clock reading ("6 to 8" == 6 minutes to
                    # eight) whose hour is immediately followed by a DURATION
                    # unit is not a clock at all: "6 to 8 hours" / "5 to 10
                    # minutes" name an interval length, not a time of day.
                    # Reading them as a clock fabricated a bogus time (07:54)
                    # and stranded the unit -- so "cook for 6 to 8 hours" was
                    # returned as a minute-wide span.  Veto the CLOCKDIR reading
                    # when a duration unit trails the match, so the phrase stays
                    # a duration(-range) and extract_timespan defers to
                    # extract_duration.  A real clock range carries no trailing
                    # unit ("6 to 8 pm", "from 9 to 5"), so this is untouched.
                    if (name == "clock_time" and "CLOCKDIR" in slots
                            and end < len(tokens)
                            and tokens[end].text in (
                                set(self.spec.units)
                                | set(self.spec.singular_units))):
                        continue
                    # "new year 15 minutes" is a duration, not the year 2015:
                    # YEARANY's only gate below YEAR's own is >=2 digits (no
                    # >=32 lower bound, see its _bind docstring), so it also
                    # swallows the leading number of a trailing duration/count
                    # phrase. A unit word immediately after the bound YEARANY
                    # token means the number was never a year at all -- veto
                    # this order so the bare "new year_word" order wins at the
                    # same start instead, leaving the whole "15 minutes" in
                    # the remainder for extract_duration to read.
                    if (name == "new_year_ref" and "YEARANY" in slots
                            and end < len(tokens)
                            and tokens[end].text in (
                                set(self.spec.units)
                                | set(self.spec.singular_units))):
                        continue
                    # Positional licensing for the bare-daypart reading: a
                    # capitalised daypart word that is the tail of a capitalised
                    # multi-word phrase ("Guy Fawkes Night", "Twelfth Night") is
                    # a proper-noun holiday name, not the night band -- refuse
                    # the bare "DAYPART" order so the daypart never hijacks the
                    # noun and strands the rest of the name.  Only the BARE form
                    # (no REL_MARKER licensing it) is guarded; "this Night" is
                    # not.  Gated on the locale convention so noun-capitalising
                    # languages are unaffected.
                    if (name == "daypart_ref" and "DAYPART" in slots
                            and "REL_MARKER" not in slots
                            and self.spec.conventions.daypart_proper_noun_guard
                            and start > 0
                            and tokens[start].cap
                            and tokens[start].prev_cap):
                        continue
                    # "the last TWO days of the month" is not "the 2nd day of
                    # the month": a rel-marker ("last"/"next"/"this") sitting
                    # UNCONSUMED immediately before a scoped-ordinal match means
                    # the number is a COUNT under that modifier ("last two" -- a
                    # 2-day span), not the ordinal day-of-month the ORD slot
                    # read.  Reading it fabricated June 2 for "the last two days
                    # of the month".  Veto the candidate so the mis-read
                    # cardinal-as-ordinal reading is not returned (honest None
                    # over silently-wrong); the legitimate "the last day" /
                    # "the 2nd day" (only an article before the match, the
                    # modifier bound INSIDE the order) is untouched.
                    if (name == "scoped_ordinal" and start > 0
                            and tokens[start - 1].text in self.spec.rel_markers):
                        continue
                    # A bare hour that is really a day-of-month is a date, not
                    # a clock: "June 15 in the morning" tokenises the day number
                    # "15" as a HOUR under the "at? HOUR in? article? MERIDIEM"
                    # order, whose 4-token span then out-spans the 2-token
                    # "June 15" calendar_date in _select -- so the clock hijacks
                    # the day-of-month and strands the month.  A HOUR sitting
                    # immediately after a MONTH surface (modulo one unconsumed
                    # article, "June the 15 ...") is not a time of day; veto the
                    # clock reading so the calendar_date wins.  A real clock
                    # after a month ("June 15 at 3pm") leads with "at", so its
                    # HOUR is preceded by that connector (or the day number),
                    # never a bare month, and stays untouched.
                    if name == "clock_time" and "HOUR" in slots:
                        _hi = slots["HOUR"].index - 1
                        _art = self.spec.connectors.get(
                            "article", frozenset())
                        if _hi >= 0 and tokens[_hi].text in _art:
                            _hi -= 1
                        if _hi >= 0 and tokens[_hi].text in self.spec.months:
                            continue
                    if "CAL_MONTH" in slots:
                        cal = _calendar_for_surface(
                            self.spec, slots["CAL_MONTH"].text)
                        # A calendar with a bounded tabulated sibling (umm_al_qura
                        # backs the unbounded islamic_civil arithmetic) must not
                        # read a YEAR beyond that table as a genuine reckoned
                        # year: "ramadan 2027" is the Gregorian-2027 occurrence of
                        # the holiday, not AH 2027 (2588 CE).  Dropping the
                        # reckoned candidate lets the holiday_ref reading win the
                        # selection.  Past/near AH years stay on the arithmetic
                        # path ("ramadan 1446", "ramadan 1000" are untouched).
                        if cal is not None and "YEAR" in slots:
                            sib = next((c for c in CALENDARS.values()
                                        if getattr(c, "fallback", None) == cal
                                        and getattr(c, "labels", None)), None)
                            try:
                                _yr = int(slots["YEAR"].value)
                            except (TypeError, ValueError):
                                _yr = None
                            if (sib is not None and _yr is not None
                                    and _yr > max(y for y, _ in sib.labels)):
                                continue
                    elif "HOLIDAY" in slots:
                        # trace the well-known binding (key + provenance) so
                        # explain() shows which holiday and which source named it
                        key = self.spec.holidays.get(slots["HOLIDAY"].text)
                        src = self.spec.holiday_sources.get(key, "")
                        cal = f"{key} <{src}>" if key else None
                    else:
                        cal = None
                    out.append(MatchCandidate(
                        Match(name, (start, end), slots, calendar=cal),
                        precedence))
        return out

    @staticmethod
    def _select(candidates: List[MatchCandidate]) -> List[MatchCandidate]:
        """Pick the non-overlapping winners: longest span, then precedence.

        This is the parse-winner contest, and it is deliberately
        **resolution-independent** -- it runs on the raw enumerated candidates
        before the resolver is consulted, so the winner stands even for
        readings the resolver later declines.  It is *not* the same question as
        confidence ranking (:func:`chronologia.extract.confidence.confidence`),
        which scores already-*resolved* readings for the candidate API: the two
        legitimately disagree (a bare ``calendar_date`` may out-score the
        anchored-offset reading that wins the parse), and they are kept as two
        explicit layers rather than one algorithm.  See ``docs/extraction.md``.
        """
        ordered = sorted(candidates,
                         key=lambda c: (-c.match.length, c.precedence,
                                        c.match.span[0]))
        taken: set = set()
        chosen: List[MatchCandidate] = []
        for cand in ordered:
            span = range(*cand.match.span)
            if any(i in taken for i in span):
                continue
            taken.update(span)
            chosen.append(cand)
        chosen.sort(key=lambda c: c.match.span[0])
        return chosen

    def match(self, tokens: Tuple[Token, ...], veto=None) -> Tuple[Match, ...]:
        """The non-overlapping parse winners.

        ``veto`` is an optional ``match -> bool`` predicate applied to the raw
        candidates BEFORE the overlap contest (:meth:`_select`).  A vetoed
        candidate is removed up front, so a shorter reading it would otherwise
        out-span survives the contest instead of being silently suppressed by a
        winner the caller means to decline (e.g. a bare-"be" era reading that
        must yield to the plain year when it is not clause-final).
        """
        cands = self._candidates(tokens)
        if veto is not None:
            cands = [c for c in cands if not veto(c.match)]
        return tuple(c.match for c in self._select(cands))
