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


def test_resolver_invariant_actually_raised_on_unmapped_unit():
    # Drive the real fallthrough: _point_span's exhaustive elif raises
    # ResolverInvariant on an unmapped unit, and it is NOT one of the swallowed
    # types, so it propagates rather than degrading to a silent None.
    from datetime import datetime
    import pytest
    from chronologia.extract import resolver as _r
    with pytest.raises(_r.ResolverInvariant):
        _r._point_span(datetime(2017, 6, 27), "fortnightly_nonsense_unit")
