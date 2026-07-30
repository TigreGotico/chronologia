"""The construction vocabulary and the resolver's handlers are one contract.

The resolver dispatches by building a method name: ``_resolve_<construction>``
(:meth:`Resolver.resolve`). That is convenient and open, but the set of valid
constructions is otherwise only an emergent property of ``dir(Resolver)``. These
tests make it a declared, exhaustively-checked contract so a typo, a renamed
handler, or a new construction added to ``PRECEDENCE`` without a resolver fails
here -- at collection time -- instead of per-utterance at runtime.

``schema.validate`` already checks the other seam (every construction a locale's
grammar references is a KNOWN construction); together the two close the loop:
locale grammar -> known construction -> resolver handler.
"""
from chronologia.extract.compiler import PRECEDENCE, UNIMPLEMENTED
from chronologia.extract.resolver import Resolver

_HANDLERS = {n[len("_resolve_"):] for n in dir(Resolver)
             if n.startswith("_resolve_")}
_NEED = set(PRECEDENCE) - set(UNIMPLEMENTED)


def test_every_construction_has_a_resolver_handler():
    missing = sorted(_NEED - _HANDLERS)
    assert not missing, (
        f"constructions in PRECEDENCE with no _resolve_* handler: {missing}. "
        f"Add the handler, or list the construction in compiler.UNIMPLEMENTED.")


def test_no_orphan_resolver_handlers():
    # a _resolve_* method that names no known construction is a dead handler --
    # usually a construction was renamed in PRECEDENCE but not on the resolver.
    orphans = sorted(_HANDLERS - set(PRECEDENCE) - set(UNIMPLEMENTED))
    assert not orphans, (
        f"_resolve_* handlers naming no known construction: {orphans}.")
