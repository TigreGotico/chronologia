# -*- coding: utf-8 -*-
"""Contract tests for the shared BASE GRAMMAR (``chronologia.extract.base_grammar``).

The base grammar centralises a construction's default orders so every locale
inherits them instead of copy-pasting (and silently omitting) the same order
strings.  Two properties make the refactor safe, and both are asserted here:

* **Totality** -- every locale has each base construction (via inheritance, an
  ``override``, or an inline block) unless it explicitly ``disable``s it.  No
  silent absence; removing a construction without disabling raises.
* **Additive superset** -- every locale's EFFECTIVE orders match everything the
  pre-refactor (dev) orders matched.  The merge only ever adds matching power,
  never drops an order a locale already shipped.
"""
import os

import pytest

from chronologia.extract import load_lang_spec
from chronologia.extract.base_grammar import (BASE_GRAMMAR,
                                                 MARKER_POSTFIX_ORDERS,
                                                 SEASON_YEAR_FIRST_ORDERS,
                                                 TotalityError,
                                                 assert_additive_superset,
                                                 assert_totality, merge_orders)

_LOCALE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                           "chronologia", "locale")
_LANGS = sorted(d for d in os.listdir(_LOCALE_DIR)
                if os.path.isfile(os.path.join(_LOCALE_DIR, d, "lang.json")))


def _effective_orders(lang, name):
    """The raw effective order strings for ``name`` in ``lang`` after merge."""
    spec = load_lang_spec(lang)
    return [o.raw for o in spec.orders.get(name, ())]


# --- the pre-refactor (dev) scoped_ordinal orders, per locale ---------------
# Frozen snapshot of what every locale declared inline on `dev` BEFORE the base
# grammar existed.  The additive-superset test proves each locale's effective
# orders still cover every one of these.  Locales absent here declared no
# scoped_ordinal on dev (they gain it for free from the base now).
DEV_SCOPED_ORDINAL = {
    'an': ['article? ORD WEEKDAY of MONTH YEAR?', 'article? ORD UNIT of MONTH YEAR?', 'article? ORD UNIT of article? year_word YEAR?'],
    'ast': ['article? ORD SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ordlast SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ORD UNIT of MONTH YEAR?', 'article? ordlast UNIT of MONTH YEAR?', 'article? ORD UNIT of article? year_word YEAR?', 'article? ordlast UNIT of article? year_word YEAR?', 'article? ORD SCOPE_UNIT'],
    'ca': ['article? ORD WEEKDAY of MONTH YEAR?', 'article? ordlast WEEKDAY of MONTH YEAR?', 'article? ORD UNIT of MONTH YEAR?', 'article? ordlast UNIT of MONTH YEAR?', 'article? ORD UNIT of article? year_word YEAR?', 'article? ordlast UNIT of article? year_word YEAR?', 'article? ORD SCOPE_UNIT'],
    'cs': ['article? ORD SCOPE_UNIT', 'article? ORD UNIT of MONTH YEAR?'],
    'da': ['article? ORD SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ORD UNIT of MONTH YEAR?', 'article? ORD UNIT of article? year_word YEAR?', 'article? ORD SCOPE_UNIT'],
    'de': ['article? ORD SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ORD WEEKDAY of MONTH YEAR?', 'article? ORD UNIT of MONTH YEAR?', 'article? ORD UNIT of article? year_word YEAR?', 'article? ORD SCOPE_UNIT'],
    'el': ['article? ORD SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ORD UNIT of MONTH YEAR?', 'article? ORD SCOPE_UNIT'],
    'en': ['article? ORD SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ordlast SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ORD WEEKDAY of MONTH YEAR?', 'article? ordlast WEEKDAY of MONTH YEAR?', 'article? ORD UNIT of MONTH YEAR?', 'article? ordlast UNIT of MONTH YEAR?', 'article? ORD UNIT of article? year_word YEAR?', 'article? ordlast UNIT of article? year_word YEAR?', 'article? ORD UNIT of REL_MARKER? article? SCOPE_UNIT', 'article? ordlast UNIT of REL_MARKER? article? SCOPE_UNIT', 'article? ORD SCOPE_UNIT'],
    'es': ['article? ORD WEEKDAY of MONTH YEAR?', 'article? ordlast WEEKDAY of MONTH YEAR?', 'article? ORD UNIT of MONTH YEAR?', 'article? ordlast UNIT of MONTH YEAR?', 'article? ORD UNIT of article? year_word YEAR?', 'article? ordlast UNIT of article? year_word YEAR?', 'article? ORD SCOPE_UNIT', 'article? CMUNIT ORD'],
    'et': ['ORD SCOPE_UNIT'],
    'eu': ['ORD SEL_UNIT of SORD SCOPE_UNIT', 'ORD SCOPE_UNIT'],
    'fi': ['ORD SCOPE_UNIT'],
    'fr': ['article? ORD SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ordlast SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ORD WEEKDAY of MONTH YEAR?', 'article? ordlast WEEKDAY of MONTH YEAR?', 'article? ORD UNIT of MONTH YEAR?', 'article? ordlast UNIT of MONTH YEAR?', 'article? ORD UNIT of article? year_word YEAR?', 'article? ordlast UNIT of article? year_word YEAR?', 'article? ORD SCOPE_UNIT'],
    'fy': ['article? ORD SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ORD UNIT of MONTH YEAR?', 'article? ORD UNIT of article? year_word YEAR?', 'article? ORD SCOPE_UNIT'],
    'gl': ['article? ORD WEEKDAY of MONTH YEAR?', 'article? ordlast WEEKDAY of MONTH YEAR?', 'article? ORD UNIT of MONTH YEAR?', 'article? ordlast UNIT of MONTH YEAR?', 'article? ORD UNIT of article? year_word YEAR?', 'article? ordlast UNIT of article? year_word YEAR?', 'article? ORD SCOPE_UNIT'],
    'he': ['article? WEEKDAY ORD of MONTH YEAR?'],
    'hu': ['article? ORD SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ORD SCOPE_UNIT'],
    'it': ['article? ORD WEEKDAY of MONTH YEAR?', 'article? ordlast WEEKDAY of MONTH YEAR?', 'article? ORD SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ordlast SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ORD UNIT of MONTH YEAR?', 'article? ordlast UNIT of MONTH YEAR?', 'article? ORD UNIT of article? year_word YEAR?', 'article? ordlast UNIT of article? year_word YEAR?', 'article? ORD SCOPE_UNIT', 'article? CMUNIT ORD'],
    'nb': ['article? ORD SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ORD UNIT of MONTH YEAR?', 'article? ORD UNIT of article? year_word YEAR?', 'article? ORD SCOPE_UNIT'],
    'nl': ['article? ORD WEEKDAY of MONTH YEAR?', 'article? ORD SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ORD UNIT of MONTH YEAR?', 'article? ORD UNIT of article? year_word YEAR?', 'article? ORD SCOPE_UNIT'],
    'nn': ['article? ORD SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ORD UNIT of MONTH YEAR?', 'article? ORD UNIT of article? year_word YEAR?', 'article? ORD SCOPE_UNIT'],
    'oc': ['article? ORD SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ordlast SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ORD UNIT of MONTH YEAR?', 'article? ordlast UNIT of MONTH YEAR?', 'article? ORD UNIT of article? year_word YEAR?', 'article? ordlast UNIT of article? year_word YEAR?', 'article? ORD SCOPE_UNIT'],
    'pl': ['article? ORD WEEKDAY MONTH YEAR?'],
    'pt': ['article? ORD WEEKDAY of MONTH YEAR?', 'article? ordlast WEEKDAY of MONTH YEAR?', 'article? ORD UNIT of MONTH YEAR?', 'article? ordlast UNIT of MONTH YEAR?', 'article? ORD UNIT of article? year_word YEAR?', 'article? ordlast UNIT of article? year_word YEAR?', 'article? ORD SCOPE_UNIT', 'article? CMUNIT ORD'],
    'ro': ['article? ORD SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ordlast SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ORD UNIT of MONTH YEAR?', 'article? ordlast UNIT of MONTH YEAR?', 'article? ORD UNIT of article? year_word YEAR?', 'article? ordlast UNIT of article? year_word YEAR?', 'article? ORD SCOPE_UNIT'],
    'sv': ['article? ORD WEEKDAY of MONTH YEAR?', 'article? ORD SEL_UNIT of article? SORD SCOPE_UNIT', 'article? ORD UNIT of MONTH YEAR?', 'article? ORD UNIT of article? year_word YEAR?', 'article? ORD SCOPE_UNIT'],
    'uk': ['article? ORD WEEKDAY MONTH YEAR?'],
}


# --- the pre-refactor (dev) weekday_ref orders, per locale ------------------
# Frozen snapshot of what every locale declared inline on `dev` BEFORE
# weekday_ref inherited the base grammar.  Every locale had it, so unlike
# scoped_ordinal there are no free gains -- the migration is purely additive:
# the shared prefix + bare base plus the ``marker_position: post`` postfix
# orders must cover every one of these dev orders.
DEV_WEEKDAY_REF = {
    'an': ['article? WEEKDAY REL_MARKER', 'REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'ar': ['WEEKDAY REL_MARKER', 'REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'ast': ['REL_MARKER WEEKDAY', 'WEEKDAY REL_MARKER'],
    'az': ['REL_MARKER WEEKDAY', 'WEEKDAY REL_MARKER', 'WEEKDAYFULL'],
    'bg': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'ca': ['REL_MARKER WEEKDAY', 'article? WEEKDAY REL_MARKER', 'article? WEEKDAYFULL REL_MARKER', 'WEEKDAYFULL'],
    'cs': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'da': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'de': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'el': ['article? REL_MARKER article? WEEKDAY', 'article? WEEKDAY REL_MARKER', 'WEEKDAYFULL'],
    'en': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'es': ['REL_MARKER WEEKDAY', 'article? WEEKDAY REL_MARKER', 'article? WEEKDAYFULL REL_MARKER', 'WEEKDAYFULL'],
    'et': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'eu': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'fa': ['WEEKDAY REL_MARKER', 'REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'fi': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'fr': ['REL_MARKER WEEKDAY', 'WEEKDAY REL_MARKER'],
    'fy': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'gl': ['REL_MARKER WEEKDAY', 'article? WEEKDAY REL_MARKER', 'article? WEEKDAYFULL REL_MARKER', 'WEEKDAYFULL'],
    'he': ['WEEKDAY REL_MARKER', 'REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'hr': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'hu': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'id': ['WEEKDAY REL_MARKER', 'REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'it': ['REL_MARKER WEEKDAY', 'WEEKDAY REL_MARKER'],
    'kab': ['WEEKDAYFULL'],
    'ms': ['WEEKDAY REL_MARKER', 'REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'mwl': ['article? WEEKDAY REL_MARKER', 'REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'nb': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'nl': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'nn': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'oc': ['REL_MARKER WEEKDAY', 'WEEKDAY REL_MARKER'],
    'pl': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'pt': ['REL_MARKER WEEKDAY', 'article? WEEKDAY REL_MARKER', 'article? WEEKDAYFULL REL_MARKER', 'WEEKDAYFULL'],
    'ro': ['REL_MARKER WEEKDAY', 'WEEKDAY REL_MARKER'],
    'ru': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'sk': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'sl': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'sv': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
    'tr': ['REL_MARKER WEEKDAY', 'WEEKDAY REL_MARKER', 'WEEKDAYFULL'],
    'uk': ['REL_MARKER WEEKDAY', 'WEEKDAYFULL'],
}


# --- the pre-refactor (dev) rel_period orders, per locale -------------------
# Frozen snapshot of what every locale declared inline on `dev` BEFORE
# rel_period inherited the base grammar.  39/40 locales had it (``kab`` ships no
# relative markers, so it gains the -- unreachable -- base order for free).  The
# shared prefix ``REL_MARKER UNIT`` plus, where the locale postposes, the
# ``rel_period`` postfix order ``article? UNIT REL_MARKER`` (or a locale
# ``override`` for an article-bearing prefix) must cover every dev order.
DEV_REL_PERIOD = {
    'an': ['REL_MARKER UNIT', 'UNIT REL_MARKER'],
    'ar': ['UNIT REL_MARKER', 'REL_MARKER UNIT'],
    'ast': ['article? UNIT REL_MARKER', 'article? REL_MARKER UNIT'],
    'az': ['REL_MARKER UNIT', 'UNIT REL_MARKER'],
    'bg': ['REL_MARKER UNIT'],
    'ca': ['REL_MARKER UNIT', 'UNIT REL_MARKER'],
    'cs': ['REL_MARKER UNIT'],
    'da': ['REL_MARKER UNIT'],
    'de': ['REL_MARKER UNIT'],
    'el': ['article? REL_MARKER article? UNIT', 'UNIT REL_MARKER'],
    'en': ['REL_MARKER UNIT'],
    'es': ['REL_MARKER UNIT', 'UNIT REL_MARKER'],
    'et': ['REL_MARKER UNIT', 'UNIT REL_MARKER'],
    'eu': ['REL_MARKER UNIT', 'UNIT REL_MARKER'],
    'fa': ['REL_MARKER UNIT', 'UNIT REL_MARKER'],
    'fi': ['REL_MARKER UNIT', 'UNIT REL_MARKER'],
    'fr': ['article? UNIT REL_MARKER', 'article? REL_MARKER UNIT'],
    'fy': ['REL_MARKER UNIT'],
    'gl': ['REL_MARKER UNIT', 'UNIT REL_MARKER'],
    'he': ['UNIT REL_MARKER', 'REL_MARKER UNIT'],
    'hr': ['REL_MARKER UNIT'],
    'hu': ['REL_MARKER article? UNIT', 'UNIT REL_MARKER'],
    'id': ['UNIT REL_MARKER'],
    'it': ['article? UNIT REL_MARKER', 'article? REL_MARKER UNIT'],
    'ms': ['UNIT REL_MARKER'],
    'mwl': ['REL_MARKER UNIT', 'article? UNIT REL_MARKER'],
    'nb': ['REL_MARKER UNIT'],
    'nl': ['REL_MARKER UNIT'],
    'nn': ['REL_MARKER UNIT'],
    'oc': ['article? UNIT REL_MARKER', 'article? REL_MARKER UNIT'],
    'pl': ['REL_MARKER UNIT'],
    'pt': ['REL_MARKER UNIT', 'UNIT REL_MARKER'],
    'ro': ['article? UNIT REL_MARKER', 'article? REL_MARKER UNIT'],
    'ru': ['REL_MARKER UNIT'],
    'sk': ['REL_MARKER UNIT'],
    'sl': ['REL_MARKER UNIT'],
    'sv': ['REL_MARKER UNIT'],
    'tr': ['REL_MARKER UNIT', 'UNIT REL_MARKER'],
    'uk': ['REL_MARKER UNIT'],
}


# --- the pre-refactor (dev) season_ref orders, per locale -------------------
# Frozen snapshot of what every locale declared inline on `dev` BEFORE
# season_ref inherited the base grammar.  38/40 locales had it (``fa`` and
# ``kab`` ship no season vocabulary, so they gain the -- unreachable -- base
# orders for free).  The shared base ("REL_MARKER SEASON" prefix, connector-word
# "article? SEASON of YEAR", trailing "article? SEASON YEAR?") plus, where the
# locale sets ``season_year_order: year_first``, the "YEAR SEASON" order, and --
# for the two postposing locales -- an ``extend``ed "SEASON REL_MARKER", must
# cover every one of these dev orders.
DEV_SEASON_REF = {
    'an': ['article? SEASON of YEAR', 'REL_MARKER SEASON', 'article? SEASON YEAR?'],
    'ar': ['SEASON of YEAR', 'REL_MARKER SEASON', 'SEASON YEAR?'],
    'ast': ['SEASON of YEAR', 'REL_MARKER SEASON', 'SEASON YEAR?'],
    'az': ['REL_MARKER SEASON', 'SEASON YEAR?', 'YEAR SEASON'],
    'bg': ['REL_MARKER SEASON', 'SEASON of YEAR', 'SEASON YEAR?'],
    'ca': ['article? SEASON of YEAR', 'REL_MARKER SEASON', 'article? SEASON YEAR?'],
    'cs': ['REL_MARKER SEASON', 'SEASON of YEAR', 'SEASON YEAR?'],
    'da': ['REL_MARKER SEASON', 'SEASON of YEAR', 'SEASON YEAR?'],
    'de': ['REL_MARKER SEASON', 'SEASON of YEAR', 'SEASON YEAR?'],
    'el': ['REL_MARKER SEASON', 'SEASON of YEAR', 'SEASON YEAR?'],
    'en': ['SEASON of YEAR', 'REL_MARKER SEASON', 'SEASON YEAR?'],
    'es': ['article? SEASON of YEAR', 'REL_MARKER SEASON', 'article? SEASON YEAR?'],
    'et': ['REL_MARKER SEASON', 'SEASON YEAR?'],
    'eu': ['REL_MARKER SEASON', 'YEAR SEASON', 'SEASON YEAR?'],
    'fr': ['SEASON of YEAR', 'REL_MARKER SEASON', 'SEASON YEAR?'],
    'fy': ['REL_MARKER SEASON', 'SEASON of YEAR', 'SEASON YEAR?'],
    'gl': ['article? SEASON of YEAR', 'REL_MARKER SEASON', 'article? SEASON YEAR?'],
    'he': ['SEASON of YEAR', 'REL_MARKER SEASON', 'SEASON YEAR?'],
    'hr': ['REL_MARKER SEASON', 'SEASON of YEAR', 'SEASON YEAR?'],
    'hu': ['REL_MARKER SEASON', 'SEASON of YEAR', 'YEAR SEASON', 'SEASON YEAR?'],
    'id': ['SEASON REL_MARKER', 'SEASON YEAR?'],
    'it': ['SEASON of YEAR', 'REL_MARKER SEASON', 'SEASON YEAR?'],
    'ms': ['SEASON REL_MARKER', 'SEASON YEAR?'],
    'mwl': ['article? SEASON of YEAR', 'REL_MARKER SEASON', 'article? SEASON YEAR?'],
    'nb': ['REL_MARKER SEASON', 'SEASON of YEAR', 'SEASON YEAR?'],
    'nl': ['REL_MARKER SEASON', 'SEASON of YEAR', 'SEASON YEAR?'],
    'nn': ['REL_MARKER SEASON', 'SEASON of YEAR', 'SEASON YEAR?'],
    'oc': ['SEASON of YEAR', 'REL_MARKER SEASON', 'SEASON YEAR?'],
    'pl': ['REL_MARKER SEASON', 'SEASON of YEAR', 'SEASON YEAR?'],
    'pt': ['article? SEASON of YEAR', 'REL_MARKER SEASON', 'article? SEASON YEAR?'],
    'ro': ['SEASON of YEAR', 'REL_MARKER SEASON', 'SEASON YEAR?'],
    'ru': ['REL_MARKER SEASON', 'SEASON of YEAR', 'SEASON YEAR?'],
    'sk': ['REL_MARKER SEASON', 'SEASON of YEAR', 'SEASON YEAR?'],
    'sl': ['REL_MARKER SEASON', 'SEASON of YEAR', 'SEASON YEAR?'],
    'sv': ['REL_MARKER SEASON', 'SEASON of YEAR', 'SEASON YEAR?'],
    'tr': ['REL_MARKER SEASON', 'SEASON YEAR?', 'YEAR SEASON'],
    'uk': ['REL_MARKER SEASON', 'SEASON of YEAR', 'SEASON YEAR?'],
}


@pytest.mark.parametrize("lang", _LANGS)
def test_additive_superset_season_ref(lang):
    """Every dev season_ref order is still covered after the base merge.

    Proves the shared base plus the ``season_year_order`` year-first order and
    the two postposing locales' ``extend``ed "SEASON REL_MARKER" reproduce --
    never drop -- what each locale parsed on dev.
    """
    dev = DEV_SEASON_REF.get(lang, [])
    if not dev:
        return                          # gained season_ref for free; nothing to lose
    effective = _effective_orders(lang, "season_ref")
    missing = assert_additive_superset(lang, dev, effective)
    assert not missing, (
        f"{lang}: base-grammar merge DROPPED season_ref orders "
        f"(not additive): {missing}\n  effective={effective}")


def test_season_year_order_gates_year_first_order():
    """``season_year_order`` gates the YEAR-first season order independently.

    ``season_first`` (default) keeps only the base SEASON-first orders;
    ``year_first`` and ``both`` append season_ref's "YEAR SEASON" while
    retaining the base season-first orders (so they coincide for season_ref,
    whose base is always kept).
    """
    base = BASE_GRAMMAR["season_ref"]
    year_first = SEASON_YEAR_FIRST_ORDERS["season_ref"]

    default = merge_orders({}, {})["season_ref"]
    assert default == base                              # no year-first by default
    assert not any(o in default for o in year_first)

    for order in ("year_first", "both"):
        got = merge_orders({"base_grammar": {"season_year_order": order}},
                           {})["season_ref"]
        for o in base:                                  # season-first base kept
            assert o in got
        for o in year_first:                            # year-first appended
            assert o in got
    # year_first and both coincide for season_ref (base season-first always kept)
    assert (merge_orders({"base_grammar": {"season_year_order": "year_first"}}, {})
            == merge_orders({"base_grammar": {"season_year_order": "both"}}, {}))


def test_marker_position_gates_season_ref_postfix():
    """``marker_position`` gates the season_ref postfix, per construction.

    Fixes a silent-wrong: season_ref used to be OUT of the postfix set, so the
    Romance postposed idiom ("el verano pasado" -- the marker TRAILS the
    season) never matched and stranded the marker, resolving to *this* season
    instead of last/next.  season_ref now carries its own postfix order behind
    ``marker_position`` exactly like weekday_ref/rel_period; a scalar ``post``
    enables it, and the base season-first orders are always retained.
    """
    base = BASE_GRAMMAR["season_ref"]
    postfix = MARKER_POSTFIX_ORDERS["season_ref"]
    assert postfix                                      # season_ref now postfixes

    pre = merge_orders({}, {})["season_ref"]
    assert pre == base                                  # no postfix by default
    assert not any(o in pre for o in postfix)

    for pos in ("post", "both"):
        got = merge_orders({"base_grammar": {"marker_position": pos}},
                           {})["season_ref"]
        for o in base:                                  # base season orders kept
            assert o in got
        for o in postfix:                               # postfix appended
            assert o in got


def test_marker_position_mapping_is_per_construction():
    """``marker_position`` accepts a per-construction mapping.

    Greek/Turkic postpose weekday/period but keep the season marker PREPOSED
    ("geçen yaz"), so they set ``marker_position`` to a mapping that opts
    weekday_ref/rel_period into ``post`` while leaving season_ref at its ``pre``
    default -- the split a locale-wide scalar could not express.
    """
    cfg = {"base_grammar": {"marker_position": {"weekday_ref": "post",
                                                "rel_period": "post"}}}
    got = merge_orders(cfg, {})
    # weekday/period get their postfix orders...
    for o in MARKER_POSTFIX_ORDERS["weekday_ref"]:
        assert o in got["weekday_ref"]
    for o in MARKER_POSTFIX_ORDERS["rel_period"]:
        assert o in got["rel_period"]
    # ...but season_ref, absent from the mapping, stays pre (no postfix).
    assert got["season_ref"] == merge_orders({}, {})["season_ref"]
    for o in MARKER_POSTFIX_ORDERS["season_ref"]:
        assert o not in got["season_ref"]

    # a mapping opting season in DOES add the season postfix
    cfg2 = {"base_grammar": {"marker_position": {"season_ref": "post"}}}
    got2 = merge_orders(cfg2, {})
    for o in MARKER_POSTFIX_ORDERS["season_ref"]:
        assert o in got2["season_ref"]
    # ...and leaves weekday/period at their pre default
    assert got2["weekday_ref"] == BASE_GRAMMAR["weekday_ref"]


def test_scalar_marker_position_unchanged_for_weekday_and_period():
    """The per-construction change is byte-identical for scalar-knob locales.

    A scalar ``post`` must still produce exactly the same weekday_ref and
    rel_period orders it did before season_ref joined the postfix set -- the
    only added contribution is season_ref's own postfix.
    """
    scalar = merge_orders({"base_grammar": {"marker_position": "post"}}, {})
    mapping = merge_orders(
        {"base_grammar": {"marker_position": {"weekday_ref": "post",
                                              "rel_period": "post",
                                              "season_ref": "post"}}}, {})
    assert scalar == mapping             # scalar == the equivalent full mapping


@pytest.mark.parametrize("lang", _LANGS)
def test_additive_superset_rel_period(lang):
    """Every dev rel_period order is still covered after the base merge.

    Proves the shared prefix plus the per-construction ``marker_position``
    postfix orders (and the article-prefix ``override`` locales) reproduce --
    never drop -- what each locale parsed on dev.
    """
    dev = DEV_REL_PERIOD.get(lang, [])
    if not dev:
        return                          # gained rel_period for free; nothing to lose
    effective = _effective_orders(lang, "rel_period")
    missing = assert_additive_superset(lang, dev, effective)
    assert not missing, (
        f"{lang}: base-grammar merge DROPPED rel_period orders "
        f"(not additive): {missing}\n  effective={effective}")


def test_marker_position_gates_rel_period_postfix():
    """``marker_position`` gates the rel_period postfix independently.

    The postfix order set is PER-CONSTRUCTION: ``post`` appends rel_period's own
    ``article? UNIT REL_MARKER`` (not weekday_ref's), and ``pre`` keeps only the
    shared ``REL_MARKER UNIT`` prefix.
    """
    base = BASE_GRAMMAR["rel_period"]
    postfix = MARKER_POSTFIX_ORDERS["rel_period"]
    pre = merge_orders({}, {})["rel_period"]
    assert pre == base
    assert not any(o in pre for o in postfix)
    for pos in ("post", "both"):
        got = merge_orders({"base_grammar": {"marker_position": pos}},
                           {})["rel_period"]
        for o in base:
            assert o in got
        for o in postfix:
            assert o in got


@pytest.mark.parametrize("lang", _LANGS)
def test_additive_superset_weekday_ref(lang):
    """Every dev weekday_ref order is still covered after the base merge.

    Proves the prefix/bare base plus the ``marker_position`` postfix orders
    reproduce -- never drop -- what each locale parsed on dev.
    """
    dev = DEV_WEEKDAY_REF.get(lang, [])
    effective = _effective_orders(lang, "weekday_ref")
    missing = assert_additive_superset(lang, dev, effective)
    assert not missing, (
        f"{lang}: base-grammar merge DROPPED weekday_ref orders "
        f"(not additive): {missing}\n  effective={effective}")


def test_marker_position_gates_postfix_orders():
    """``marker_position`` controls whether the postfix orders are appended.

    ``pre`` (default) keeps only the prefix/bare base; ``post`` and ``both``
    append the marker-trailing orders while retaining the base prefix.
    """
    base = BASE_GRAMMAR["weekday_ref"]
    postfix = MARKER_POSTFIX_ORDERS["weekday_ref"]

    pre = merge_orders({}, {})["weekday_ref"]
    assert pre == base                                  # no postfix by default
    assert not any(o in pre for o in postfix)

    for pos in ("post", "both"):
        got = merge_orders({"base_grammar": {"marker_position": pos}},
                           {})["weekday_ref"]
        for o in base:                                  # prefix base retained
            assert o in got
        for o in postfix:                               # postfix appended
            assert o in got
    # post and both coincide for weekday_ref (its base is prefix, always kept)
    assert (merge_orders({"base_grammar": {"marker_position": "post"}}, {})
            == merge_orders({"base_grammar": {"marker_position": "both"}}, {}))


# --- the pre-refactor (dev) half_period orders, per locale ------------------
# Frozen snapshot of what every locale declared inline on `dev` BEFORE
# half_period inherited the base grammar.  Only 16/40 locales had it (the other
# ~24 SILENTLY returned the whole year/period and stranded "first half"); those
# gain the construction for free from the base now.  Fifteen declared exactly
# the shared en orders; ``eu`` declared the article-less variant, which the base
# ``article?`` orders cover (dropping the optional article).
DEV_HALF_PERIOD = {
    'ast': ['article? NUM half of GYEAR', 'article? NUM half of article? SCOPE_UNIT'],
    'da': ['article? NUM half of GYEAR', 'article? NUM half of article? SCOPE_UNIT'],
    'de': ['article? NUM half of GYEAR', 'article? NUM half of article? SCOPE_UNIT'],
    'el': ['article? NUM half of GYEAR', 'article? NUM half of article? SCOPE_UNIT'],
    'en': ['article? NUM half of GYEAR', 'article? NUM half of article? SCOPE_UNIT'],
    'eu': ['NUM half of GYEAR', 'NUM half of SCOPE_UNIT'],
    'fr': ['article? NUM half of GYEAR', 'article? NUM half of article? SCOPE_UNIT'],
    'fy': ['article? NUM half of GYEAR', 'article? NUM half of article? SCOPE_UNIT'],
    'hu': ['article? NUM half of GYEAR', 'article? NUM half of article? SCOPE_UNIT'],
    'it': ['article? NUM half of GYEAR', 'article? NUM half of article? SCOPE_UNIT'],
    'nb': ['article? NUM half of GYEAR', 'article? NUM half of article? SCOPE_UNIT'],
    'nl': ['article? NUM half of GYEAR', 'article? NUM half of article? SCOPE_UNIT'],
    'nn': ['article? NUM half of GYEAR', 'article? NUM half of article? SCOPE_UNIT'],
    'oc': ['article? NUM half of GYEAR', 'article? NUM half of article? SCOPE_UNIT'],
    'ro': ['article? NUM half of GYEAR', 'article? NUM half of article? SCOPE_UNIT'],
    'sv': ['article? NUM half of GYEAR', 'article? NUM half of article? SCOPE_UNIT'],
}


@pytest.mark.parametrize("lang", _LANGS)
def test_additive_superset_half_period(lang):
    """Every dev half_period order is still covered after the base merge.

    Proves the migration only ADDED matching power: the 16 locales that shipped
    half_period inline keep every order (``eu``'s article-less orders are
    covered by the base ``article?`` orders), and the ~24 that lacked it gain
    the construction for free instead of silently stranding "first half".
    """
    dev = DEV_HALF_PERIOD.get(lang, [])
    if not dev:
        return                          # gained half_period for free; nothing to lose
    effective = _effective_orders(lang, "half_period")
    missing = assert_additive_superset(lang, dev, effective)
    assert not missing, (
        f"{lang}: base-grammar merge DROPPED half_period orders "
        f"(not additive): {missing}\n  effective={effective}")


@pytest.mark.parametrize("lang", _LANGS)
def test_additive_superset_scoped_ordinal(lang):
    """Every dev scoped_ordinal order is still covered by the effective orders.

    Proves the base-grammar merge only ADDED matching power for this locale:
    nothing a locale parsed on dev stops parsing now.
    """
    dev = DEV_SCOPED_ORDINAL.get(lang, [])
    if not dev:
        return                          # gained scoped_ordinal for free; nothing to lose
    effective = _effective_orders(lang, "scoped_ordinal")
    missing = assert_additive_superset(lang, dev, effective)
    assert not missing, (
        f"{lang}: base-grammar merge DROPPED scoped_ordinal orders "
        f"(not additive): {missing}\n  effective={effective}")


# --- the pre-refactor (dev) daypart_ref orders, per locale -----------------
# Frozen snapshot of what every locale declared inline on `dev` BEFORE
# daypart_ref inherited the base grammar.  Only 14/40 locales had it; the other
# 26 SILENTLY returned the whole day and stranded the daypart word ("сегодня
# утром" -> whole day 2017-06-27, "утром" dropped).  Those 26 gain the two
# shared orders ("REL_MARKER DAYPART", "DAYPART") for free from the base now.
# The three Iberian locales whose morning word is a homograph of "tomorrow"
# (es "mañana", gl "mañá", pt's guarded set) ``override`` daypart_ref to drop
# the bare "DAYPART" order, so the base bare form can never hijack their
# tomorrow parse -- their effective orders are exactly the dev list below.
DEV_DAYPART_REF = {
    'da': ['REL_MARKER DAYPART', 'DAYPART'],
    'de': ['REL_MARKER DAYPART', 'DAYPART'],
    'en': ['REL_MARKER DAYPART', 'DAYPART'],
    'es': ['REL_MARKER DAYPART', 'article DAYPART', 'of DAYPART'],
    'fr': ['REL_MARKER DAYPART', 'DAYPART'],
    'gl': ['REL_MARKER DAYPART', 'article DAYPART', 'of DAYPART', 'at DAYPART', 'dayframe DAYPART'],
    'it': ['REL_MARKER DAYPART', 'DAYPART'],
    'nb': ['REL_MARKER DAYPART', 'DAYPART'],
    'nl': ['REL_MARKER DAYPART', 'DAYPART'],
    'nn': ['REL_MARKER DAYPART', 'DAYPART'],
    'pt': ['REL_MARKER DAYPART', 'article DAYPART', 'of DAYPART', 'at DAYPART', 'dayframe DAYPART', 'article? DAYPART REL_MARKER'],
    'ro': ['REL_MARKER DAYPART', 'DAYPART'],
    'sv': ['REL_MARKER DAYPART', 'DAYPART'],
    'ca': ['REL_MARKER DAYPART', 'DAYPART'],
}


@pytest.mark.parametrize("lang", _LANGS)
def test_additive_superset_daypart_ref(lang):
    """Every dev daypart_ref order is still covered after the base merge.

    Proves the migration only ADDED matching power: the 14 locales that shipped
    daypart_ref inline keep every order (es/gl/pt via an ``override`` that drops
    the bare "DAYPART" their tomorrow-homograph morning word must not gain), and
    the 26 that lacked it gain the construction for free instead of silently
    stranding the daypart word.
    """
    dev = DEV_DAYPART_REF.get(lang, [])
    if not dev:
        return                          # gained daypart_ref for free; nothing to lose
    effective = _effective_orders(lang, "daypart_ref")
    missing = assert_additive_superset(lang, dev, effective)
    assert not missing, (
        f"{lang}: base-grammar merge DROPPED daypart_ref orders "
        f"(not additive): {missing}\n  effective={effective}")


def test_es_gl_pt_daypart_ref_omit_the_bare_order():
    """The tomorrow-homograph locales must NOT inherit the bare "DAYPART".

    es "mañana"/gl "mañá" are also the word for *tomorrow*; a bare-band reading
    would hijack that parse.  Their ``override`` keeps the article/connector
    forms and drops the bare order, so "DAYPART" alone never fires for them.
    """
    for lang in ("es", "gl", "pt"):
        eff = _effective_orders(lang, "daypart_ref")
        assert "DAYPART" not in eff, f"{lang} unexpectedly gained bare DAYPART"
        assert "REL_MARKER DAYPART" in eff


def test_totality_every_locale_has_every_base_construction():
    """No locale is silently missing a base construction it did not disable."""
    specs = {}
    for lang in _LANGS:
        spec = load_lang_spec(lang)
        import json
        with open(os.path.join(_LOCALE_DIR, lang, "lang.json"),
                  encoding="utf-8") as fh:
            cfg = json.load(fh)
        specs[lang] = {"cfg": cfg,
                       "orders": {n: [o.raw for o in os_]
                                  for n, os_ in spec.orders.items()}}
    assert_totality(specs)              # raises TotalityError on any silent gap


def test_totality_raises_when_a_construction_is_silently_removed():
    """Removing a base construction WITHOUT disabling it must raise.

    This is the guarantee the standalone-per-locale scheme could not give: an
    absent construction was indistinguishable from a deliberate omission.
    """
    # a locale that has scoped_ordinal but neither declares nor disables it
    specs = {"xx": {"cfg": {}, "orders": {}}}
    with pytest.raises(TotalityError) as exc:
        assert_totality(specs)
    assert "scoped_ordinal" in str(exc.value)

    # ...and explicitly disabling every base construction is allowed (no raise)
    specs_ok = {"xx": {"cfg": {"base_grammar": {"disable": list(BASE_GRAMMAR)}},
                       "orders": {}}}
    assert_totality(specs_ok)


def test_merge_is_additive_by_construction():
    """merge_orders never drops an inline order and appends the base."""
    cfg = {}
    inline = {"scoped_ordinal": ["article? ORD WEEKDAY MONTH YEAR?"]}
    merged = merge_orders(cfg, inline)["scoped_ordinal"]
    # the locale's inline (genitive) order is preserved...
    assert "article? ORD WEEKDAY MONTH YEAR?" in merged
    # ...and the base orders are appended on top
    for base in BASE_GRAMMAR["scoped_ordinal"]:
        assert base in merged


def test_override_replaces_extend_appends():
    base = BASE_GRAMMAR["scoped_ordinal"]
    over = merge_orders({"base_grammar": {"override": {"scoped_ordinal": ["ORD X"]}}},
                        {})["scoped_ordinal"]
    assert over == ["ORD X"]            # override REPLACES the base
    ext = merge_orders({"base_grammar": {"extend": {"scoped_ordinal": ["ORD X"]}}},
                       {})["scoped_ordinal"]
    assert ext == base + ["ORD X"]      # extend APPENDS to the base


def test_disable_opts_out():
    out = merge_orders({"base_grammar": {"disable": ["scoped_ordinal"]}}, {})
    assert "scoped_ordinal" not in out
