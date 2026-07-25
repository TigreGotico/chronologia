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
