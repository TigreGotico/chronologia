"""Business-day counting ("in 5 business days", "the next working day",
"3 working days after christmas").

A **business day** (a.k.a. working day) is a calendar day that is neither a
weekend day nor a public holiday:

* the *weekend* is the locale's own two-day rest period -- the pair of
  weekdays ``(weekend_start, weekend_start+1)`` read from
  :attr:`~chronologia.extract.model.Conventions.weekend_start` (Saturday+Sunday
  in the Western default, Friday+Saturday where a locale declares it), never
  hard-coded here;
* a *public holiday* is looked up through the shared civil-holiday engine
  (:func:`~chronologia.civil_holidays.is_civil_holiday` with
  ``categories=("public",)``), which **requires a jurisdiction**.  Holiday data
  is never re-derived here -- the calendar owns it.

Because the holiday calendar is jurisdiction-scoped, the public edge takes an
optional ``jurisdiction`` (``extract_timespan(..., jurisdiction='PT')``).  With
**no jurisdiction** the count is *holiday-blind*: a business day is simply a
non-weekend weekday.  This is an honest, documented default -- weekday counting
is universal, but which weekdays are public holidays is not knowable without a
jurisdiction.

On the ``ouvrable``/``ouvré`` distinction (and the like in other languages):
French law draws a fine line between *jours ouvrables* (all days except the
weekly rest day and public holidays, historically up to six per week) and
*jours ouvrés* (days actually worked, typically five).  Chronologia does not
model that payroll-grade distinction: **both** surfaces resolve to the same
Monday-to-Friday-minus-public-holidays business day, matching the everyday
"working day" sense a speaker means when they say "in five working days".

Two shapes fire, both by composition on the token stream (objects-in,
objects-out), mirroring :mod:`chronologia.extract.anchored`:

* **count from the anchor** ("in N business days", "N working days", "the next
  working day" == N=1): the N-th business day strictly after the anchor date, a
  day-wide span;
* **count from a resolved reference** ("3 working days after christmas", "two
  business days before new year"): the same count, but taken from a
  date-resolving submatch the engine already produced -- the reference is
  *whatever was resolved* just past the ``after``/``before`` marker.

The surfaces are a per-locale fact (``marker_business.voc``: business/working,
dia útil, día hábil/laborable, Werktag/Arbeitstag, jour ouvrable/ouvré); the
counting logic is generic.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional, Set, Tuple

from chronologia.civil_holidays import is_civil_holiday
from chronologia.extract.anchored import _gap_words
from chronologia.extract.model import LangSpec, Match, Resolution, Token
from chronologia.extract.resolver import (DATE_CONSTRUCTIONS, _day_span,
                                              _midnight)

Pair = Tuple[Match, Resolution]


def _is_business_day(day: datetime, weekend_start: int,
                     jurisdiction: Optional[str]) -> bool:
    """True when ``day`` is neither a weekend day nor (with a jurisdiction) a
    public holiday of that jurisdiction."""
    wd = day.weekday()
    if wd == weekend_start or wd == (weekend_start + 1) % 7:
        return False
    if jurisdiction and is_civil_holiday(day, jurisdiction,
                                         categories=("public",)):
        return False
    return True


def _nth_business_day(base: datetime, n: int, sign: int, weekend_start: int,
                      jurisdiction: Optional[str]) -> datetime:
    """The ``n``-th business day strictly after (``sign>0``) or before
    (``sign<0``) the midnight of ``base``."""
    day = _midnight(base)
    step = timedelta(days=1 if sign > 0 else -1)
    seen = 0
    while seen < n:
        day = day + step
        if _is_business_day(day, weekend_start, jurisdiction):
            seen += 1
    return day


def _is_day_unit(tok: Token, spec: LangSpec) -> bool:
    return spec.units.get(tok.text) == "day"


def _date_ref(tokens, hi: int, resolved: List[Pair], spec: LangSpec,
              gap, resolve_ref=None
              ) -> Optional[Tuple[datetime, int, int, Set[int]]]:
    """A ``after``/``before`` reference sitting just past the business unit.

    Returns ``(base_datetime, sign, end_index, consumed_ids)`` when a
    directional marker at ``hi`` (modulo an article/of gap) is followed by a
    date-resolving submatch; otherwise ``None``.

    The flat scan of ``resolved`` only sees matcher-native references.  When it
    finds none at the reference position, ``resolve_ref`` (when threaded) is the
    additive fallback: it recurses the reference token slice through the
    single-span core, so a **composed** reference -- itself an offset ("the
    monday after christmas"), an nth-weekday-of-month, ... -- also binds.  The
    recursion returns consumed positions in the *original* stream, so the outer
    remainder stays correct.
    """
    after = spec.connectors.get("after", frozenset())
    before = spec.connectors.get("before", frozenset())
    k = hi
    while k < len(tokens) and tokens[k].text in gap:
        k += 1
    for words_set, sign in ((after, 1), (before, -1)):
        for surface in sorted(words_set, key=lambda s: len(s.split()),
                              reverse=True):
            w = surface.split()
            if [t.text for t in tokens[k:k + len(w)]] != w:
                continue
            p = k + len(w)
            while p < len(tokens) and tokens[p].text in gap:
                p += 1
            flat = next(((m, r) for m, r in resolved
                         if m.construction in DATE_CONSTRUCTIONS
                         and m.span[0] == p), None)
            # the composed-reference fallback: a reference that is itself a
            # composed construction ("the monday after christmas") extends
            # strictly beyond the bare matcher-native match the flat scan sees
            # ("monday").  Recurse, and prefer it ONLY when it reaches further
            # than the flat match -- so every reference the flat scan already
            # covers in full keeps its exact binding.
            if resolve_ref is not None and p < len(tokens):
                got = resolve_ref(p)
                if got is not None and got[1]:
                    rec_end = max(got[1]) + 1
                    if flat is None or rec_end > flat[0].span[1]:
                        ref_start, consumed = got
                        base = datetime(ref_start.year, ref_start.month,
                                        ref_start.day)
                        ids = set(consumed) | set(range(hi, p))
                        return base, sign, rec_end, ids
            if flat is not None:
                m, r = flat
                s = r.value.start
                base = datetime(s.year, s.month, s.day)
                ids = set(range(m.span[0], m.span[1])) | set(range(hi, p))
                return base, sign, m.span[1], ids
    return None


def apply_business_days(tokens, resolved: List[Pair], spec: LangSpec,
                        anchor: datetime,
                        jurisdiction: Optional[str],
                        resolve_ref=None) -> List[Pair]:
    """Rewrite a "in N business days" / "the next working day" / "N working
    days after <date>" phrase into its day-wide business-day span.

    A business phrase claims its tokens and drops any weaker match overlapping
    them, exactly as the other anchor-relative passes do.
    """
    surfaces = spec.connectors.get("business")
    if not surfaces:
        return resolved
    gap = _gap_words(spec) | frozenset(spec.connectors.get("article", ())) \
        | frozenset(spec.connectors.get("in", ()))
    nextw = frozenset(s for s, v in spec.rel_markers.items() if v > 0)
    weekend_start = spec.conventions.weekend_start
    n = len(tokens)
    for i, t in enumerate(tokens):
        if t.text not in surfaces:
            continue
        lo, hi = i, i + 1
        # a bare day unit adjacent to the marker (either order) is part of the
        # business unit: "business days" / "dias úteis".  A one-word compound
        # ("Werktag") stands alone.
        if hi < n and _is_day_unit(tokens[hi], spec):
            hi += 1
        elif lo - 1 >= 0 and _is_day_unit(tokens[lo - 1], spec):
            lo -= 1
        # the count sits just left of the business unit
        j = lo - 1
        while j >= 0 and tokens[j].text in gap:
            j -= 1
        if j >= 0 and tokens[j].is_number and tokens[j].value \
                and tokens[j].value >= 1:
            count, start = int(tokens[j].value), j
        elif j >= 0 and tokens[j].text in nextw:
            count, start = 1, j
        else:
            continue
        # swallow a leading "in" marker ("in 5 business days") into the claim so
        # it does not strand in the remainder -- the clock ("... at 3pm") that
        # composes onto this span must not see "in" as leftover text.
        inwords = frozenset(spec.connectors.get("in", ()))
        while start - 1 >= 0 and tokens[start - 1].text in inwords:
            start -= 1
        ref = _date_ref(tokens, hi, resolved, spec, gap, resolve_ref)
        if ref is not None:
            base, sign, end, claimed = ref
            claimed = claimed | set(range(start, hi))
        else:
            base, sign, end = anchor, 1, hi
            claimed = set(range(start, hi))
        value = _nth_business_day(base, count, sign, weekend_start,
                                  jurisdiction)
        pair = (Match("business_days", (start, end), {}),
                Resolution(_day_span(value), tuple(sorted(claimed))))
        kept = [(m, r) for m, r in resolved
                if not (set(range(*m.span)) & claimed)]
        kept.append(pair)
        return kept
    return resolved
