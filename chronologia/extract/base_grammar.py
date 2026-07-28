"""A shared BASE GRAMMAR of construction orders that every locale inherits.

Historically each ``locale/<code>/lang.json`` declared its ``constructions``
order-data standalone: the same abstract order strings (``"article? ORD
WEEKDAY of MONTH YEAR?"`` ...) were copy-pasted into every locale, and were
*silently missing* wherever nobody added them.  ``scoped_ordinal`` -- "the Nth
<weekday> of <month>", "the 3rd century" -- shipped in only 27 of 40 locales,
and each gap was a separate per-language bug fixed by hand, one PR at a time.

This module replaces that with a single source of truth.  ``BASE_GRAMMAR``
holds the default orders for a construction, expressed in the abstract slots
that already work language-neutrally (``ORD`` / ``WEEKDAY`` / ``MONTH`` /
``SCOPE_UNIT`` / ``SEL_UNIT`` / ``article`` / ``of`` / ...).  Every locale
inherits them; a locale supplies only its genuine exceptions through a small
``base_grammar`` block in its ``lang.json``:

* ``disable: [name]``          -- opt a base construction out entirely.
* ``override: {name: [orders]}`` -- REPLACE the base orders (a genuinely
                                    different word order, e.g. Hebrew's
                                    postposed ordinal, Slavic genitive "of").
* ``extend: {name: [orders]}``   -- APPEND locale-specific orders on top of
                                    the inherited base (an extra accepted form,
                                    e.g. Spanish/Italian/Portuguese ``CMUNIT
                                    ORD`` for postposed compound-unit ordinals).

An inline ``constructions`` block for a base construction still works and is
merged too: its orders are UNIONED with the base contribution, never replaced,
so a locale can never LOSE an order it already shipped.  That union is the
**additive-superset guarantee** the loader upholds and ``test_base_grammar``
proves: the refactor only ever *adds* matching power.

The knob schema below records the typological axes the exceptions fall on --
so the long tail stays a handful of named dimensions, not 40 bespoke order
lists.  This PR realises ``scoped_ordinal`` through the escape hatches
(``disable`` / ``override`` / ``extend``); later PRs migrate more
constructions and fold the repeated patterns into the enum knobs.
"""
from __future__ import annotations

from typing import Dict, List, Mapping, Sequence

# ---------------------------------------------------------------------------
# The base grammar.  Only ``scoped_ordinal`` lives here this PR (more
# constructions migrate in later PRs).  The orders are the richest set in the
# tree -- harvested verbatim from ``en`` -- using the abstract slots the
# resolver already binds language-neutrally.  A leading ``article?`` is
# OPTIONAL, so an article-less language (Estonian, Basque) matches the same
# orders without shipping an article: ``article?`` covers the article-less
# surface.
# ---------------------------------------------------------------------------
BASE_GRAMMAR: Dict[str, List[str]] = {
    "scoped_ordinal": [
        "article? ORD SEL_UNIT of article? SORD SCOPE_UNIT",
        "article? ordlast SEL_UNIT of article? SORD SCOPE_UNIT",
        "article? ORD WEEKDAY of MONTH YEAR?",
        "article? ordlast WEEKDAY of MONTH YEAR?",
        "article? ORD WEEKDAY of REL_MARKER? article? SCOPE_UNIT",
        "article? ordlast WEEKDAY of REL_MARKER? article? SCOPE_UNIT",
        "article? ORD UNIT of MONTH YEAR?",
        "article? ordlast UNIT of MONTH YEAR?",
        "article? ORD UNIT of article? year_word YEAR?",
        "article? ordlast UNIT of article? year_word YEAR?",
        "article? ORD UNIT of REL_MARKER? article? SCOPE_UNIT",
        "article? ordlast UNIT of REL_MARKER? article? SCOPE_UNIT",
        # a fuzzy early/mid/late PART on an absolute ordinal period ("the
        # mid-20th century", "the early 21st century") -- narrows the whole
        # period to its first/middle/last third (resolver snaps to whole
        # years).  Must precede the bare "ORD SCOPE_UNIT" so the PART is not
        # stranded and the whole century returned.
        "article? PART ORD SCOPE_UNIT",
        "article? ORD SCOPE_UNIT",
    ],
    # "last/next <weekday>" and a bare full weekday name meaning its next
    # occurrence.  The prefix form ("REL_MARKER WEEKDAY" -- "last Friday") and
    # the bare full-weekday form ("WEEKDAYFULL" -- "Friday" -> next Friday) are
    # the language-neutral core every locale shares.  The postposed idiom
    # ("el viernes pasado", "marțea trecută" -- the marker TRAILS the weekday)
    # is not universal, so it is gated behind the ``marker_position`` knob
    # rather than shipped in the base: a locale that does not postpose must not
    # gain a trailing-marker order that could mis-parse.
    "weekday_ref": [
        "REL_MARKER WEEKDAY",
        "WEEKDAYFULL",
    ],
    # "last/next <unit>" -- "last week", "next month", "this year".  The prefix
    # form ("REL_MARKER UNIT" -- the marker LEADS the unit) is the
    # language-neutral core every locale shares.  The postposed idiom
    # ("semana pasada", "mês que vem" -- the marker TRAILS the unit) is not
    # universal, so it lives in ``MARKER_POSTFIX_ORDERS`` gated behind the
    # ``marker_position`` knob, exactly like ``weekday_ref``: a locale that does
    # not postpose must not gain a trailing-marker order that could mis-parse.
    # An article inside the prefix (Romance "la semana que viene", Greek's
    # doubly-articled form, Hungarian's medial article) is a per-locale
    # exception carried by ``override`` -- the shared prefix stays article-less.
    "rel_period": [
        "REL_MARKER UNIT",
    ],
    # "last/next <season>" ("next winter"), "<season> of <year>" ("summer of
    # 2024") and the bare "<season> <year>?" ("summer 2024", or a deictic
    # "summer" on its own).  These three -- the relative-marker prefix, the
    # connector-word "of YEAR", and the trailing optional YEAR -- are the
    # language-neutral core every locale shares; a leading ``article?`` on the
    # year forms carries the Romance "el verano de 2024" without a locale
    # shipping an article.  Two idioms are NOT universal and stay out of the
    # base.  The year-first order ("YEAR SEASON" -- Turkic/Basque "2024 yaz")
    # lives in ``SEASON_YEAR_FIRST_ORDERS`` behind the ``season_year_order``
    # knob, which ≥2 locales share.  The postposed relative marker ("SEASON
    # REL_MARKER" -- Romance "el verano pasado", Semitic "الصيف الماضي",
    # Austronesian "musim panas lalu") lives in ``MARKER_POSTFIX_ORDERS`` gated
    # behind ``marker_position``, exactly like ``weekday_ref``/``rel_period``.
    # Season postposing is INDEPENDENT of weekday/period postposing -- Romance
    # and Semitic postpose all three, but Greek/Turkic postpose weekday/period
    # while keeping the season marker PREPOSED ("το περασμένο καλοκαίρι",
    # "geçen yaz").  A locale therefore opts season postfix in or out on its
    # own via the PER-CONSTRUCTION ``marker_position`` mapping; a scalar
    # ``post`` (Romance/Semitic) enables it for every construction at once.
    "season_ref": [
        "article? SEASON of YEAR",
        "REL_MARKER SEASON",
        "article? SEASON YEAR?",
    ],
    # "the first/second half of <period>" ("the first half of 2020" -> Jan-Jun;
    # "the second half of the century").  ``NUM`` binds the ordinal (first/second
    # -> 1/2), the literal ``half`` binds the locale's period-noun surface
    # (``marker_half``: en "half", es "mitad", de "Hälfte", it "metà"), ``of``
    # the connector, and the period is either a Gregorian ``GYEAR`` or a
    # ``SCOPE_UNIT`` (decade/century/millennium).  These two orders are the
    # language-neutral core every locale shares -- harvested verbatim from the
    # richest inline set (``en``); a leading ``article?`` carries the Romance/
    # Germanic "la première moitié" / "die erste Hälfte" without a locale
    # shipping an article, and ``article?`` equally covers the article-less
    # surface (Basque "lehen erdia"), so an article-less locale matches the same
    # orders.  The connector ``of?`` is OPTIONAL, so the ONE order carries BOTH
    # the prepositional connector ("first half OF 2020", Bulgarian "на") AND the
    # Slavic connector-less genitive ("первая половина 2020", "erste Hälfte
    # 2020" -- no "of" word), inheriting cleanly into de/ru/pl/uk/cs/bg with no
    # per-locale order.  Two word orders still genuinely differ and stay a
    # per-locale ``extend``: the Semitic POSTPOSED ordinal ("النصف الأول من
    # 2020" -- half then ordinal) and the Turkic YEAR-first possessive
    # ("2020'nin ilk yarısı" -- year, then ordinal-half).  (A locale whose
    # feminine ordinal the numfold does not yet emit -- the Slavic "первая/
    # pierwsza/perша/první" family -- supplies that surface as a fold entry;
    # Arabic's النصف ordinal الأول/الثاني is withheld from the fold as a
    # Levantine month-name homograph, so spelled Arabic first/second half stays
    # the same documented xfail as spelled Q1/Q2.)
    "half_period": [
        "article? NUM half of? GYEAR",
        "article? NUM half of? article? SCOPE_UNIT",
    ],
    # "early/mid/late <month>" ("early March" -> the first third of March, a
    # ~10-day span; "late December" -> the last third).  ``PART`` binds the
    # locale's fuzzy period-part surface (``period_part_early/mid/late.voc`` --
    # en "early/mid/late", de "Anfang/Mitte/Ende", ru "начало/середина/конец"),
    # ``MONTH`` the month, and the resolver slices the Gregorian month into
    # thirds via :func:`chronologia.subdivide`.  This single order is the
    # language-neutral core every locale shares -- harvested from the richest
    # inline set (Romance ``article? PART of? MONTH``): a leading ``article?``
    # carries the Romance/Germanic determiner without a locale shipping an
    # article, ``article?`` equally covers the article-less surface, and the
    # optional ``of?`` covers BOTH the connector-less genitive ("PART MONTH":
    # en/de "early March", Slavic "начало марта" with a genitive month) AND the
    # prepositional connector ("PART of MONTH": Scandinavian "begyndelsen af
    # marts", Bulgarian "началото на март" with ``на`` bound as ``of``).  The
    # one order therefore inherits cleanly into the pre-posed-PART locales
    # (Germanic, Romance, all Slavic bar none, Austronesian id/ms) with no
    # per-locale exception.  The genuinely different word order -- the Turkic
    # POSTPOSED possessive ("mart başı", MONTH then PART) -- is not expressible
    # by adding a leading-``article?`` order and stays a per-locale ``extend``.
    "month_fuzzy": [
        "article? PART of? MONTH YEAR?",
    ],
    # "this morning", "tonight", "yesterday evening", "tomorrow afternoon" --
    # a time-of-day band selected deictically.  ``DAYPART`` binds the locale's
    # daypart surface (``daypart_<key>.voc`` -- en "morning/afternoon/evening/
    # night", ru "утром/днём/вечером/ночью"), and the resolver narrows the
    # anchored day to that band via :func:`chronologia.dayparts.daypart_span`,
    # whose boundaries are CLDR day-period data.  Two orders are the
    # language-neutral core every locale shares: the relative-marker prefix
    # ("REL_MARKER DAYPART" -- "this morning") and the bare band ("DAYPART" --
    # "in the morning", and, composed with a same-text ``named_day``,
    # "yesterday evening" = named_day + bare daypart).  Historically only 14 of
    # 40 locales declared these; the other 26 SILENTLY returned the whole day
    # and stranded the daypart word ("сегодня утром" -> whole day, "утром"
    # dropped).  The bare "DAYPART" order is NOT universal-safe: where the
    # morning word is a homograph of "tomorrow" (Spanish "mañana", Galician
    # "mañá", Portuguese carries its own guarded set) the bare reading would
    # hijack the tomorrow parse, so those locales ``override`` daypart_ref to
    # drop the bare order -- exactly the reason es/gl/pt keep an explicit order
    # list instead of inheriting the base bare form.
    "daypart_ref": [
        "REL_MARKER DAYPART",
        "DAYPART",
    ],
}

# ---------------------------------------------------------------------------
# Knob-generated orders, keyed BY CONSTRUCTION.  A construction's postfix
# (marker-trailing) variants are appended by ``merge_orders`` -- for whichever
# construction it is merging -- only when the locale sets
# ``marker_position: post`` (or ``both``); see the KNOB SCHEMA note on
# ``marker_position``.  The postfix order set is PER-CONSTRUCTION (a weekday
# trails its marker as "<weekday> <marker>", a unit as "<unit> <marker>"), so
# the one ``marker_position`` knob a locale sets appends the RIGHT postfix set
# for each postposing construction it inherits.  Adding a new postposing
# construction is therefore a single new entry here -- no change to
# ``merge_orders`` or the knob.  The article is OPTIONAL, so an article-less
# language ("marțea trecută", "minggu lalu") matches the same order without
# shipping an article; the Romance article-bearing idiom ("el viernes pasado",
# "la semana pasada") is the richest shared form and is what these encode.
# ---------------------------------------------------------------------------
MARKER_POSTFIX_ORDERS: Dict[str, List[str]] = {
    "weekday_ref": [
        "article? WEEKDAY REL_MARKER",
        "article? WEEKDAYFULL REL_MARKER",
    ],
    "rel_period": [
        "article? UNIT REL_MARKER",
    ],
    # "last/next <season>" postposed -- the marker TRAILS the season
    # ("el verano pasado", "l'été dernier", "الصيف الماضي", "musim panas
    # lalu").  Whether a locale postposes its season is INDEPENDENT of whether
    # it postposes weekday/period: Romance and Semitic postpose all three,
    # while Greek/Turkic postpose weekday/period but keep the season marker
    # PREPOSED ("το περασμένο καλοκαίρι", "geçen yaz").  That split is exactly
    # why ``marker_position`` is per-construction: a locale opts season postfix
    # in (or out) on its own, without disturbing weekday/period.
    "season_ref": [
        "article? SEASON REL_MARKER",
    ],
}

# ---------------------------------------------------------------------------
# Knob-generated orders for the YEAR-first season surface, keyed BY
# CONSTRUCTION.  ``merge_orders`` appends these only when the locale sets
# ``season_year_order: year_first`` (or ``both``); see the KNOB SCHEMA note on
# ``season_year_order``.  The base ``season_ref`` orders are SEASON-first
# ("summer 2024"); Turkic and Basque also (or instead) put the year first
# ("2024 yaz", "2024ko uda").  A locale that does not accept the year-first
# surface must not gain a "YEAR SEASON" order that could mis-parse a bare
# "YEAR" phrase, so it stays out of the base and behind the knob -- exactly
# like ``marker_position`` gates the postposed marker.
# ---------------------------------------------------------------------------
SEASON_YEAR_FIRST_ORDERS: Dict[str, List[str]] = {
    "season_ref": [
        "YEAR SEASON",
    ],
}

# ---------------------------------------------------------------------------
# KNOB SCHEMA -- the typological axes the per-locale exceptions collapse onto.
# Documented here as the target vocabulary for ``base_grammar`` blocks; this PR
# expresses ``scoped_ordinal``'s exceptions through the escape hatches below,
# and later PRs fold the repeated patterns into these enum knobs so 40 files
# stop shipping the same duplicated order string.
#
#   marker_position : pre | post | both  -- OR a per-construction mapping
#                     {construction: pre|post|both}
#       Whether a REL_MARKER may trail its slot ("el viernes pasado").  As a
#       SCALAR it applies to every postfix-capable construction (weekday_ref,
#       rel_period, season_ref) at once -- the Romance/Semitic case, which
#       postpose all three.  As a MAPPING it sets the axis per construction
#       (a construction absent from the mapping defaults to ``pre``) -- the
#       Greek/Turkic case, which postpose weekday/period but keep the season
#       marker preposed: ``{"weekday_ref": "post", "rel_period": "post"}``.
#       ``both`` names the symmetry (base is retained) explicitly; ``post``
#       reads as the locale's dominant idiom.  See ``MARKER_POSTFIX_ORDERS``
#       for the per-construction postfix order sets.
#   season_year_order : season_first | year_first | both
#       Whether ``season_ref`` accepts a YEAR-first surface ("2024 yaz",
#       "2024ko uda").  The base is SEASON-first ("summer 2024"), always kept;
#       ``year_first`` / ``both`` append the "YEAR SEASON" order so the
#       year-leading idiom also matches.  ``both`` names the symmetry (base
#       season-first is always retained) explicitly; ``year_first`` reads as
#       the locale's dominant idiom.
#   ordinal_position : pre | post
#       Postposed ordinal ("WEEKDAY ORD of MONTH" in Hebrew; compound-unit
#       "CMUNIT ORD" in Romance).
#   article : optional-leading | none
#       Whether base orders carry a leading ``article?`` (Romance/Germanic yes;
#       article-less Slavic/Semitic/Uralic no).  ``article?`` already covers the
#       article-less surface, so ``none`` is informational for this PR.
#   connector : word | genitive | none
#       How "of" binds MONTH.  Genitive-case languages (Polish *marca*, Russian,
#       Bulgarian) express "of March" morphologically and drop the connector
#       word -- their order is "article? ORD WEEKDAY MONTH", realised here as an
#       ``override``.
#
# ESCAPE HATCHES (the true long tail, realised this PR):
#   disable / override / extend -- see the module docstring.
# ---------------------------------------------------------------------------
KNOB_SCHEMA: Dict[str, frozenset] = {
    "marker_position": frozenset({"pre", "post", "both"}),
    "season_year_order": frozenset({"season_first", "year_first", "both"}),
    "ordinal_position": frozenset({"pre", "post"}),
    "article": frozenset({"optional-leading", "none"}),
    "connector": frozenset({"word", "genitive", "none"}),
}

#: recognised keys inside a ``lang.json`` ``base_grammar`` block.
BASE_GRAMMAR_KEYS: frozenset = frozenset(
    {"disable", "override", "extend"} | set(KNOB_SCHEMA))


class TotalityError(AssertionError):
    """A locale is silently missing a base construction it did not opt out of.

    The standalone-per-locale scheme could not raise this: an absent
    construction was indistinguishable from a deliberate omission.  With a
    shared base, absence is a load-time error unless the locale explicitly
    ``disable``s the construction.
    """


def merge_orders(cfg: Mapping,
                 inline_orders: Mapping[str, Sequence[str]]
                 ) -> Dict[str, List[str]]:
    """Merge the base-grammar orders into a locale's inline orders.

    ``inline_orders`` is ``{construction -> [raw order strings]}`` taken from
    the locale's own ``constructions`` block.  For every base construction the
    locale did not ``disable``, its base contribution (``override`` replaces the
    base orders, ``extend`` appends to them) is UNIONED onto whatever the locale
    already declared inline -- appended, dedup'd, never dropping an inline
    order.  The result is therefore an additive superset of the locale's inline
    orders for every base construction.

    Returns ``{construction -> [raw order strings]}`` ready for ``parse_order``.
    """
    bg = cfg.get("base_grammar", {})
    disable = set(bg.get("disable", ()))
    override = bg.get("override", {})
    extend = bg.get("extend", {})
    marker_position = bg.get("marker_position", "pre")
    season_year_order = bg.get("season_year_order", "season_first")

    def _marker_pos(name: str) -> str:
        """Resolve the ``marker_position`` for one construction.

        The knob is EITHER a scalar (``pre`` | ``post`` | ``both``) applied to
        every postfix-capable construction, OR a per-construction mapping
        ``{construction: pre|post|both}`` overriding individual constructions
        (a construction absent from the mapping defaults to ``pre``).  A locale
        that postposes weekday/period but not season (Greek, Turkic) sets the
        mapping; a locale that postposes all of them keeps the scalar.
        """
        if isinstance(marker_position, Mapping):
            return marker_position.get(name, "pre")
        return marker_position

    out: Dict[str, List[str]] = {name: list(orders)
                                 for name, orders in inline_orders.items()}
    for name, base_orders in BASE_GRAMMAR.items():
        if name in disable:
            continue
        contrib = list(override.get(name, base_orders))
        # ``marker_position`` gates the postposed (marker-trailing) variants.
        # ``pre`` (default): base orders only -- the marker precedes its slot.
        # ``post`` / ``both``: append the construction's postfix orders so a
        # trailing marker ("<weekday> last") also matches.  The base prefix
        # orders are ALWAYS retained (they are in ``base_orders``), so ``post``
        # and ``both`` accept the marker in either position and coincide for
        # ``weekday_ref``; ``both`` names that symmetry explicitly while
        # ``post`` reads as the locale's dominant idiom.  The distinction is
        # reserved for any future construction whose base is itself postposed.
        if _marker_pos(name) in ("post", "both"):
            contrib += MARKER_POSTFIX_ORDERS.get(name, [])
        # ``season_year_order`` gates the YEAR-first season surface, exactly as
        # ``marker_position`` gates the postposed marker.  ``season_first``
        # (default): base season-first orders only.  ``year_first`` / ``both``:
        # append "YEAR SEASON" so the year-leading idiom also matches; the
        # base season-first orders are always retained.
        if season_year_order in ("year_first", "both"):
            contrib += SEASON_YEAR_FIRST_ORDERS.get(name, [])
        contrib += list(extend.get(name, ()))
        merged = out.get(name, [])
        merged = list(merged) + [o for o in contrib if o not in merged]
        out[name] = merged
    return out


def _order_covers(effective: str, dev: str) -> bool:
    """Does effective order ``effective`` match everything ``dev`` matched?

    True when ``dev``'s element sequence can be obtained from ``effective`` by
    dropping zero or more of ``effective``'s OPTIONAL elements -- i.e. the base
    order is ``dev`` plus (only) extra optional elements, so it accepts every
    surface ``dev`` accepted.  A leading ``article?`` on a base order covering
    an article-less locale's ``ORD SCOPE_UNIT`` is the canonical case.
    """
    if effective == dev:
        return True
    eff = effective.split()
    want = [tok for tok in dev.split()]
    i = 0
    for tok in eff:
        if i < len(want) and tok.rstrip("?") == want[i].rstrip("?"):
            i += 1
        elif tok.endswith("?"):
            continue                # skip an optional element not in dev
        else:
            return False            # a required element dev lacks -> no cover
    return i == len(want)


def assert_additive_superset(lang: str,
                             dev_orders: Sequence[str],
                             effective_orders: Sequence[str]) -> List[str]:
    """Return the dev orders NOT covered by any effective order for ``lang``.

    An empty list means the merge is an additive superset for this locale: it
    only ever added matching power.  See :func:`_order_covers`.
    """
    missing = []
    for dev in dev_orders:
        if not any(_order_covers(eff, dev) for eff in effective_orders):
            missing.append(dev)
    return missing


def effective_construction_names(cfg: Mapping,
                                 inline_orders: Mapping[str, Sequence[str]]
                                 ) -> set:
    """The construction names a locale ends up with after the base merge."""
    return set(merge_orders(cfg, inline_orders))


def assert_totality(specs: Mapping[str, Mapping]) -> None:
    """Raise :class:`TotalityError` unless every locale has every base
    construction (via inheritance, an ``override``, or an inline block) or
    explicitly ``disable``s it.

    ``specs`` maps ``lang -> {"cfg": cfg, "orders": {name: [raw]}}`` where
    ``orders`` are the locale's EFFECTIVE (post-merge) orders and ``cfg`` its
    parsed ``lang.json``.  No silent absence: a construction missing without an
    explicit ``disable`` is a load-time error.
    """
    gaps = []
    for lang in sorted(specs):
        entry = specs[lang]
        disable = set(entry["cfg"].get("base_grammar", {}).get("disable", ()))
        present = {name for name, orders in entry["orders"].items() if orders}
        for name in BASE_GRAMMAR:
            if name in disable:
                continue            # explicit opt-out: allowed
            if name not in present:
                gaps.append(f"{lang}: missing base construction {name!r} "
                            f"(and did not disable it)")
    if gaps:
        raise TotalityError(
            "base-grammar totality check failed:\n  " + "\n  ".join(gaps))
