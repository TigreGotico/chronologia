"""Every construction a grammar names has a resolver, or is declared unresolved."""
import glob
import json
import os

from chronologia.extract.base_grammar import BASE_GRAMMAR
from chronologia.extract.compiler import PRECEDENCE, UNIMPLEMENTED
from chronologia.extract.loader import LOCALE_DIR
from chronologia.extract.resolver import Resolver


def _locale_constructions():
    names = set()
    for path in glob.glob(os.path.join(LOCALE_DIR, "*", "lang.json")):
        with open(path, encoding="utf-8") as fh:
            cfg = json.load(fh)
        names.update(cfg.get("constructions", {}))
        bg = cfg.get("base_grammar", {})
        for section in ("override", "extend"):
            names.update(bg.get(section, {}))
    return names


def test_every_named_construction_has_a_handler_or_is_unresolved():
    named = set(BASE_GRAMMAR) | set(PRECEDENCE) | _locale_constructions()
    assert named - set(Resolver._HANDLERS) == set(UNIMPLEMENTED) & named


def test_every_handler_is_a_resolver_method_for_a_known_construction():
    for name, handler in Resolver._HANDLERS.items():
        assert name in PRECEDENCE, name
        assert handler is getattr(Resolver, f"_resolve_{name}"), name


def test_every_resolver_method_is_in_the_table():
    methods = {n[len("_resolve_"):] for n in vars(Resolver)
               if n.startswith("_resolve_")}
    assert methods == set(Resolver._HANDLERS)
