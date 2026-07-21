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


# --------------------------------------------------------------------------
# Australia (Fair Work Ombudsman + WA King's Birthday proclamations)
# --------------------------------------------------------------------------
HOLIDAY_GOLDS["AU"] = [
    # national 2024
    _g("New Year's Day", 2024, 1, 1),
    _g("Australia Day", 2024, 1, 26),
    _g("Good Friday", 2024, 3, 29),
    _g("Easter Monday", 2024, 4, 1),
    _g("ANZAC Day", 2024, 4, 25),
    _g("Christmas Day", 2024, 12, 25),
    _g("Boxing Day", 2024, 12, 26),
    # Australia Day weekend shift: 2025-01-26 is a Sunday -> observed Monday.
    _g("Australia Day", 2025, 1, 27),
    # state/territory 2024
    _g("King's Birthday", 2024, 6, 10, "AU-VIC"),
    _g("Melbourne Cup Day", 2024, 11, 5, "AU-VIC"),
    _g("Labour Day", 2024, 3, 11, "AU-VIC"),
    _g("King's Birthday", 2024, 10, 7, "AU-QLD"),
    _g("Labour Day", 2024, 5, 6, "AU-QLD"),
    _g("King's Birthday", 2024, 9, 23, "AU-WA"),   # proclaimed (decree)
    _g("Western Australia Day", 2024, 6, 3, "AU-WA"),
    _g("Labour Day", 2024, 3, 4, "AU-WA"),
    _g("King's Birthday", 2024, 6, 10, "AU-NSW"),
    _g("Labour Day", 2024, 10, 7, "AU-NSW"),
    _g("King's Birthday", 2024, 6, 10, "AU-SA"),
    _g("Labour Day", 2024, 10, 7, "AU-SA"),
    _g("King's Birthday", 2024, 6, 10, "AU-TAS"),
    _g("Eight Hours Day", 2024, 3, 11, "AU-TAS"),
    _g("King's Birthday", 2024, 6, 10, "AU-ACT"),
    _g("Labour Day", 2024, 10, 7, "AU-ACT"),
    _g("Canberra Day", 2024, 3, 11, "AU-ACT"),
    _g("King's Birthday", 2024, 6, 10, "AU-NT"),
    _g("May Day", 2024, 5, 6, "AU-NT"),
    _g("Picnic Day", 2024, 8, 5, "AU-NT"),
    # WA King's Birthday proclaimed dates other years (decree coverage)
    _g("King's Birthday", 2025, 9, 29, "AU-WA"),
    _g("King's Birthday", 2023, 9, 25, "AU-WA"),
]


# --------------------------------------------------------------------------
# India (MHA / DoPT central gazetted list)
# --------------------------------------------------------------------------
# Islamic golds assert OUR islamic_civil tabular date (the gazette can be +/-1).
HOLIDAY_GOLDS["IN"] = [
    # fixed national + gazetted 2024
    _g("Republic Day", 2024, 1, 26),
    _g("Independence Day", 2024, 8, 15),
    _g("Mahatma Gandhi's Jayanti", 2024, 10, 2),
    _g("Christmas", 2024, 12, 25),
    _g("Good Friday", 2024, 3, 29),
    # Islamic 2024 (islamic_civil tabular)
    _g("Id-ul-Fitr", 2024, 4, 10),
    _g("Id-ul-Zuha (Bakrid)", 2024, 6, 17),
    _g("Muharram", 2024, 7, 17),
    _g("Milad-un-Nabi", 2024, 9, 16),
    # Hindu/Buddhist/Sikh/Jain decree 2024 (gazette dates)
    _g("Holi", 2024, 3, 25),
    _g("Ram Navami", 2024, 4, 17),
    _g("Mahavir Jayanti", 2024, 4, 21),
    _g("Buddha Purnima", 2024, 5, 23),
    _g("Janmashtami", 2024, 8, 26),
    _g("Dussehra", 2024, 10, 12),
    _g("Diwali (Deepavali)", 2024, 10, 31),
    _g("Guru Nanak's Jayanti", 2024, 11, 15),
    _g("Maha Shivaratri", 2024, 3, 8),
    # a few other-year decree/fixed golds
    _g("Diwali (Deepavali)", 2025, 10, 20),
    _g("Holi", 2023, 3, 8),
    _g("Republic Day", 2025, 1, 26),
]
