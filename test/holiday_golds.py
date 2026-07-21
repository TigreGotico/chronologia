"""Hand-derived holiday golds for the wave-1b countries — a discoverable registry.

``HOLIDAY_GOLDS`` maps an ISO country code to a list of :class:`Gold` records,
each a ``(name, subdiv, year, month, day)`` tuple naming one holiday and the
Gregorian date it is expected to resolve to. Golds are derived from the primary
sources cited in ``~/AgentWorkspaces/papers/holidays/`` (see the module docstring
of ``test_civil_holidays_w1b``), never from the ``holidays`` package.

The registry is kept in its own importable module so the golds are shared data:
the per-country gold-application test and the coverage lint both walk it, and any
sibling structural-enforcement test can discover it the same way. Each country
appends its own key; the wave keeps the keys disjoint.
"""
from collections import namedtuple

Gold = namedtuple("Gold", "name subdiv year month day")

#: {country_code: [Gold, ...]} — populated per country below.
HOLIDAY_GOLDS = {}


def _g(name, year, month, day, subdiv=None):
    return Gold(name, subdiv, year, month, day)
