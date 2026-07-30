"""The resolver's degrade-to-None guard must never swallow an engine bug.

``Resolver.resolve`` catches ``(ValueError, OverflowError, KeyError)`` and
returns ``None`` -- the correct "this reading is not a real date" contract. But
an exhaustive elif that falls through on an unmapped unit/kind is a BUG in the
engine or locale data, not a non-date: it raises ``ResolverInvariant``, which is
deliberately outside that catch so it surfaces loudly instead of silently
dropping a date.
"""
from chronologia.extract.resolver import ResolverInvariant


def test_resolver_invariant_is_not_swallowed_by_dispatch():
    # If ResolverInvariant ever derived from one of these, the dispatch's
    # `except (ValueError, OverflowError, KeyError)` would convert an engine bug
    # into a silent None -- the exact failure mode it exists to prevent.
    assert not issubclass(ResolverInvariant, (ValueError, OverflowError, KeyError))
    assert issubclass(ResolverInvariant, Exception)
