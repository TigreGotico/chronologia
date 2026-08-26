"""Financial-market holiday calendars: XECB (ECB/TARGET2), XNYS (NYSE) and
IFEU (ICE Futures Europe) -- matching vacanza/holidays 0.101's
``list_supported_financial()`` market support.

These jurisdictions are FINANCIAL MARKETS, not ISO-3166-1 countries: an
institution's own trading/settlement calendar rather than a national civil
calendar. English is correct as their primary name -- each institution
(the ECB, the NYSE, ICE) publishes its own calendar in English, so this is
not a translation-fallback situation the way a non-English country's ``.tab``
would be.

vacanza registers several of these under more than one short code for the
identical calendar (``ECB``/``TAR`` both mean the TARGET2 settlement system;
``NYSE`` is the New York Stock Exchange's own ticker mnemonic). Rather than
ship duplicate ``.tab`` files, ``chronologia.civil_holidays.MARKET_ALIASES``
resolves the short codes onto the canonical file (``XECB``/``XNYS``) that
owns the rules -- exercised directly below.

Sourcing discipline
--------------------
Every ``.tab`` header cites the exchange/institution's own primary published
rules PDF or reference page, and explicitly flags "derived from
vacanza/holidays 0.101 (MIT)" -- the same house rule already applied to every
national jurisdiction batch. Every rule was cross-checked against vacanza
0.101's ``financial_holidays()`` output for 2024, 2025 AND 2026 (2026 is the
first year in this window an ``observed`` shift actually fires for either
market: NYSE's Independence Day, nominally Saturday 4 Jul 2026, is observed
Friday 3 Jul 2026).

Every rule is golded independently of the engine's own resolution machinery:

* ``fixed``       -> the rule's own ``(month, day)``, self-evident.
* ``nth_weekday`` -> recomputed here with plain ``datetime``/weekday
  arithmetic (never by reusing :mod:`chronologia.recurrence`), so a bug in
  the RRULE engine would still be caught.
* ``easter``      -> ``easter(year, "gregorian") + offset_days``, recomputed
  from :func:`chronologia.computus.easter` (the house standard already used
  by every other easter-offset gold in this suite).
* ``observed``    -> the nominal date is independently shifted by hand
  (Saturday -> preceding Friday, Sunday -> following Monday for the ``us``
  policy; Sunday -> following Monday only for IFEU's ``sun_mon`` policy) and
  asserted against a year where the shift actually fires.
"""
import os
from datetime import timedelta

import pytest

from chronologia import AstroDate, holidays_for, load_calendar
from chronologia.civil_holidays import MARKET_ALIASES, _DATA_DIR
from chronologia.computus import easter
from test_holiday_golds import _reg

MARKETS = ("XECB", "XNYS", "IFEU", "XCME", "XNAS", "XETR", "XSWX", "XTSE",
           "XHKG", "XJPX", "XSHG", "XBOM", "BVMF", "XMEX")


# ==========================================================================
# Register every rule's 2024/2025 dates into the shared HOLIDAY_GOLDS
# registry (test_holiday_golds._every_tab_rule_key() enforces that every
# .tab-shipped rule has a gold; these are the same dates asserted, kind by
# kind, in the tests below -- registered here so that cross-suite ratchet
# also covers these three new markets).
# ==========================================================================
for _year, (_gf, _em) in ((2024, ((3, 29), (4, 1))), (2025, ((4, 18), (4, 21)))):
    _reg("XECB", None, "New Year's Day", _year, 1, 1)
    _reg("XECB", None, "Good Friday", _year, *_gf)
    _reg("XECB", None, "Easter Monday", _year, *_em)
    _reg("XECB", None, "Labour Day", _year, 5, 1)
    _reg("XECB", None, "Christmas Day", _year, 12, 25)
    _reg("XECB", None, "Christmas Holiday", _year, 12, 26)

_reg("IFEU", None, "New Year's Day", 2024, 1, 1)
_reg("IFEU", None, "New Year's Day", 2025, 1, 1)
_reg("IFEU", None, "Good Friday", 2024, 3, 29)
_reg("IFEU", None, "Good Friday", 2025, 4, 18)
_reg("IFEU", None, "Christmas Day", 2024, 12, 25)
_reg("IFEU", None, "Christmas Day", 2025, 12, 25)

_reg("XNYS", None, "New Year's Day", 2024, 1, 1)
_reg("XNYS", None, "New Year's Day", 2025, 1, 1)
_reg("XNYS", None, "Martin Luther King Jr. Day", 2024, 1, 15)
_reg("XNYS", None, "Martin Luther King Jr. Day", 2025, 1, 20)
_reg("XNYS", None, "Washington's Birthday", 2024, 2, 19)
_reg("XNYS", None, "Washington's Birthday", 2025, 2, 17)
_reg("XNYS", None, "Good Friday", 2024, 3, 29)
_reg("XNYS", None, "Good Friday", 2025, 4, 18)
_reg("XNYS", None, "Memorial Day", 2024, 5, 27)
_reg("XNYS", None, "Memorial Day", 2025, 5, 26)
_reg("XNYS", None, "Juneteenth National Independence Day", 2024, 6, 19)
_reg("XNYS", None, "Juneteenth National Independence Day", 2025, 6, 19)
_reg("XNYS", None, "Independence Day", 2024, 7, 4)
_reg("XNYS", None, "Independence Day", 2025, 7, 4)
_reg("XNYS", None, "Labor Day", 2024, 9, 2)
_reg("XNYS", None, "Labor Day", 2025, 9, 1)
_reg("XNYS", None, "Thanksgiving Day", 2024, 11, 28)
_reg("XNYS", None, "Thanksgiving Day", 2025, 11, 27)
_reg("XNYS", None, "Christmas Day", 2024, 12, 25)
_reg("XNYS", None, "Christmas Day", 2025, 12, 25)
_reg("XCME", None, "New Year's Day", 2024, 1, 1)
_reg("XCME", None, 'Good Friday', 2024, 3, 29)
_reg("XCME", None, 'Independence Day', 2024, 7, 4)
_reg("XCME", None, 'Thanksgiving Day', 2024, 11, 28)
_reg("XCME", None, 'Christmas Day', 2024, 12, 25)
_reg("XCME", None, "New Year's Day", 2025, 1, 1)
_reg("XCME", None, 'National Day of Mourning for former President Jimmy Carter', 2025, 1, 9)
_reg("XCME", None, 'Good Friday', 2025, 4, 18)
_reg("XCME", None, 'Independence Day', 2025, 7, 4)
_reg("XCME", None, 'Thanksgiving Day', 2025, 11, 27)
_reg("XCME", None, 'Christmas Day', 2025, 12, 25)
_reg("XNAS", None, "New Year's Day", 2024, 1, 1)
_reg("XNAS", None, 'Martin Luther King Jr. Day', 2024, 1, 15)
_reg("XNAS", None, "Washington's Birthday", 2024, 2, 19)
_reg("XNAS", None, 'Good Friday', 2024, 3, 29)
_reg("XNAS", None, 'Memorial Day', 2024, 5, 27)
_reg("XNAS", None, 'Juneteenth National Independence Day', 2024, 6, 19)
_reg("XNAS", None, 'Independence Day', 2024, 7, 4)
_reg("XNAS", None, 'Labor Day', 2024, 9, 2)
_reg("XNAS", None, 'Thanksgiving Day', 2024, 11, 28)
_reg("XNAS", None, 'Christmas Day', 2024, 12, 25)
_reg("XNAS", None, "New Year's Day", 2025, 1, 1)
_reg("XNAS", None, 'National Day of Mourning for former President Jimmy Carter', 2025, 1, 9)
_reg("XNAS", None, 'Martin Luther King Jr. Day', 2025, 1, 20)
_reg("XNAS", None, "Washington's Birthday", 2025, 2, 17)
_reg("XNAS", None, 'Good Friday', 2025, 4, 18)
_reg("XNAS", None, 'Memorial Day', 2025, 5, 26)
_reg("XNAS", None, 'Juneteenth National Independence Day', 2025, 6, 19)
_reg("XNAS", None, 'Independence Day', 2025, 7, 4)
_reg("XNAS", None, 'Labor Day', 2025, 9, 1)
_reg("XNAS", None, 'Thanksgiving Day', 2025, 11, 27)
_reg("XNAS", None, 'Christmas Day', 2025, 12, 25)
_reg("XETR", None, 'Neujahr', 2024, 1, 1)
_reg("XETR", None, 'Karfreitag', 2024, 3, 29)
_reg("XETR", None, 'Ostermontag', 2024, 4, 1)
_reg("XETR", None, 'Erster Mai', 2024, 5, 1)
_reg("XETR", None, 'Heiligabend', 2024, 12, 24)
_reg("XETR", None, 'Erster Weihnachtstag', 2024, 12, 25)
_reg("XETR", None, 'Zweiter Weihnachtstag', 2024, 12, 26)
_reg("XETR", None, 'Silvester', 2024, 12, 31)
_reg("XETR", None, 'Neujahr', 2025, 1, 1)
_reg("XETR", None, 'Karfreitag', 2025, 4, 18)
_reg("XETR", None, 'Ostermontag', 2025, 4, 21)
_reg("XETR", None, 'Erster Mai', 2025, 5, 1)
_reg("XETR", None, 'Heiligabend', 2025, 12, 24)
_reg("XETR", None, 'Erster Weihnachtstag', 2025, 12, 25)
_reg("XETR", None, 'Zweiter Weihnachtstag', 2025, 12, 26)
_reg("XETR", None, 'Silvester', 2025, 12, 31)
_reg("XSWX", None, 'Neujahrstag', 2024, 1, 1)
_reg("XSWX", None, 'Berchtoldstag', 2024, 1, 2)
_reg("XSWX", None, 'Karfreitag', 2024, 3, 29)
_reg("XSWX", None, 'Ostermontag', 2024, 4, 1)
_reg("XSWX", None, 'Tag der Arbeit', 2024, 5, 1)
_reg("XSWX", None, 'Auffahrt', 2024, 5, 9)
_reg("XSWX", None, 'Pfingstmontag', 2024, 5, 20)
_reg("XSWX", None, 'Nationalfeiertag', 2024, 8, 1)
_reg("XSWX", None, 'Heiligabend', 2024, 12, 24)
_reg("XSWX", None, 'Weihnachten', 2024, 12, 25)
_reg("XSWX", None, 'Stephanstag', 2024, 12, 26)
_reg("XSWX", None, 'Vortag vor Neujahr', 2024, 12, 31)
_reg("XSWX", None, 'Neujahrstag', 2025, 1, 1)
_reg("XSWX", None, 'Berchtoldstag', 2025, 1, 2)
_reg("XSWX", None, 'Karfreitag', 2025, 4, 18)
_reg("XSWX", None, 'Ostermontag', 2025, 4, 21)
_reg("XSWX", None, 'Tag der Arbeit', 2025, 5, 1)
_reg("XSWX", None, 'Auffahrt', 2025, 5, 29)
_reg("XSWX", None, 'Pfingstmontag', 2025, 6, 9)
_reg("XSWX", None, 'Nationalfeiertag', 2025, 8, 1)
_reg("XSWX", None, 'Heiligabend', 2025, 12, 24)
_reg("XSWX", None, 'Weihnachten', 2025, 12, 25)
_reg("XSWX", None, 'Stephanstag', 2025, 12, 26)
_reg("XSWX", None, 'Vortag vor Neujahr', 2025, 12, 31)
_reg("XTSE", None, "New Year's Day", 2024, 1, 1)
_reg("XTSE", None, 'Family Day', 2024, 2, 19)
_reg("XTSE", None, 'Good Friday', 2024, 3, 29)
_reg("XTSE", None, 'Victoria Day', 2024, 5, 20)
_reg("XTSE", None, 'Canada Day', 2024, 7, 1)
_reg("XTSE", None, 'Civic Holiday', 2024, 8, 5)
_reg("XTSE", None, 'Labour Day', 2024, 9, 2)
_reg("XTSE", None, 'Thanksgiving Day', 2024, 10, 14)
_reg("XTSE", None, 'Christmas Day', 2024, 12, 25)
_reg("XTSE", None, 'Boxing Day', 2024, 12, 26)
_reg("XTSE", None, "New Year's Day", 2025, 1, 1)
_reg("XTSE", None, 'Family Day', 2025, 2, 17)
_reg("XTSE", None, 'Good Friday', 2025, 4, 18)
_reg("XTSE", None, 'Victoria Day', 2025, 5, 19)
_reg("XTSE", None, 'Canada Day', 2025, 7, 1)
_reg("XTSE", None, 'Civic Holiday', 2025, 8, 4)
_reg("XTSE", None, 'Labour Day', 2025, 9, 1)
_reg("XTSE", None, 'Thanksgiving Day', 2025, 10, 13)
_reg("XTSE", None, 'Christmas Day', 2025, 12, 25)
_reg("XTSE", None, 'Boxing Day', 2025, 12, 26)
_reg("XHKG", None, 'The first day of January', 2024, 1, 1)
_reg("XHKG", None, 'Lunar New Year', 2024, 2, 12)
_reg("XHKG", None, 'Lunar New Year', 2024, 2, 13)
_reg("XHKG", None, 'Good Friday', 2024, 3, 29)
_reg("XHKG", None, 'Easter Monday', 2024, 4, 1)
_reg("XHKG", None, 'Ching Ming Festival', 2024, 4, 4)
_reg("XHKG", None, 'Labour Day', 2024, 5, 1)
_reg("XHKG", None, 'The Birthday of the Buddha', 2024, 5, 15)
_reg("XHKG", None, 'Tuen Ng Festival', 2024, 6, 10)
_reg("XHKG", None, 'Hong Kong Special Administrative Region Establishment Day', 2024, 7, 1)
_reg("XHKG", None, 'The day following the Chinese Mid-Autumn Festival', 2024, 9, 18)
_reg("XHKG", None, 'National Day', 2024, 10, 1)
_reg("XHKG", None, 'Chung Yeung Festival', 2024, 10, 11)
_reg("XHKG", None, 'Christmas Day', 2024, 12, 25)
_reg("XHKG", None, 'The first weekday after Christmas Day', 2024, 12, 26)
_reg("XHKG", None, 'The first day of January', 2025, 1, 1)
_reg("XHKG", None, 'Lunar New Year', 2025, 1, 29)
_reg("XHKG", None, 'Lunar New Year', 2025, 1, 30)
_reg("XHKG", None, 'Lunar New Year', 2025, 1, 31)
_reg("XHKG", None, 'Ching Ming Festival', 2025, 4, 4)
_reg("XHKG", None, 'Good Friday', 2025, 4, 18)
_reg("XHKG", None, 'Easter Monday', 2025, 4, 21)
_reg("XHKG", None, 'Labour Day', 2025, 5, 1)
_reg("XHKG", None, 'The Birthday of the Buddha', 2025, 5, 5)
_reg("XHKG", None, 'Hong Kong Special Administrative Region Establishment Day', 2025, 7, 1)
_reg("XHKG", None, 'National Day', 2025, 10, 1)
_reg("XHKG", None, 'The day following the Chinese Mid-Autumn Festival', 2025, 10, 7)
_reg("XHKG", None, 'Chung Yeung Festival', 2025, 10, 29)
_reg("XHKG", None, 'Christmas Day', 2025, 12, 25)
_reg("XHKG", None, 'The first weekday after Christmas Day', 2025, 12, 26)
_reg("XJPX", None, "New Year's Day", 2024, 1, 1)
_reg("XJPX", None, 'Bank Holiday', 2024, 1, 2)
_reg("XJPX", None, 'Bank Holiday', 2024, 1, 3)
_reg("XJPX", None, 'Coming of Age Day', 2024, 1, 8)
_reg("XJPX", None, 'Foundation Day', 2024, 2, 11)
_reg("XJPX", None, 'Foundation Day (振替休日)', 2024, 2, 12)
_reg("XJPX", None, "Emperor's Birthday", 2024, 2, 23)
_reg("XJPX", None, 'Vernal Equinox Day', 2024, 3, 20)
_reg("XJPX", None, 'Showa Day', 2024, 4, 29)
_reg("XJPX", None, 'Constitution Day', 2024, 5, 3)
_reg("XJPX", None, 'Greenery Day', 2024, 5, 4)
_reg("XJPX", None, "Children's Day", 2024, 5, 5)
_reg("XJPX", None, "Children's Day (振替休日)", 2024, 5, 6)
_reg("XJPX", None, 'Marine Day', 2024, 7, 15)
_reg("XJPX", None, 'Mountain Day', 2024, 8, 11)
_reg("XJPX", None, 'Mountain Day (振替休日)', 2024, 8, 12)
_reg("XJPX", None, 'Respect for the Aged Day', 2024, 9, 16)
_reg("XJPX", None, 'Autumnal Equinox Day', 2024, 9, 22)
_reg("XJPX", None, 'Autumnal Equinox Day (振替休日)', 2024, 9, 23)
_reg("XJPX", None, 'Sports Day', 2024, 10, 14)
_reg("XJPX", None, 'Culture Day', 2024, 11, 3)
_reg("XJPX", None, 'Culture Day (振替休日)', 2024, 11, 4)
_reg("XJPX", None, 'Labor Thanksgiving Day', 2024, 11, 23)
_reg("XJPX", None, 'Bank Holiday', 2024, 12, 31)
_reg("XJPX", None, "New Year's Day", 2025, 1, 1)
_reg("XJPX", None, 'Bank Holiday', 2025, 1, 2)
_reg("XJPX", None, 'Bank Holiday', 2025, 1, 3)
_reg("XJPX", None, 'Coming of Age Day', 2025, 1, 13)
_reg("XJPX", None, 'Foundation Day', 2025, 2, 11)
_reg("XJPX", None, "Emperor's Birthday", 2025, 2, 23)
_reg("XJPX", None, "Emperor's Birthday (振替休日)", 2025, 2, 24)
_reg("XJPX", None, 'Vernal Equinox Day', 2025, 3, 20)
_reg("XJPX", None, 'Showa Day', 2025, 4, 29)
_reg("XJPX", None, 'Constitution Day', 2025, 5, 3)
_reg("XJPX", None, 'Greenery Day', 2025, 5, 4)
_reg("XJPX", None, "Children's Day", 2025, 5, 5)
_reg("XJPX", None, 'Greenery Day (振替休日)', 2025, 5, 6)
_reg("XJPX", None, 'Marine Day', 2025, 7, 21)
_reg("XJPX", None, 'Mountain Day', 2025, 8, 11)
_reg("XJPX", None, 'Respect for the Aged Day', 2025, 9, 15)
_reg("XJPX", None, 'Autumnal Equinox Day', 2025, 9, 23)
_reg("XJPX", None, 'Sports Day', 2025, 10, 13)
_reg("XJPX", None, 'Culture Day', 2025, 11, 3)
_reg("XJPX", None, 'Labor Thanksgiving Day', 2025, 11, 23)
_reg("XJPX", None, 'Labor Thanksgiving Day (振替休日)', 2025, 11, 24)
_reg("XJPX", None, 'Bank Holiday', 2025, 12, 31)
_reg("XSHG", None, '元旦', 2024, 1, 1)
_reg("XSHG", None, '农历除夕', 2024, 2, 9)
_reg("XSHG", None, '春节', 2024, 2, 10)
_reg("XSHG", None, '春节', 2024, 2, 11)
_reg("XSHG", None, '春节', 2024, 2, 12)
_reg("XSHG", None, '春节（补假）', 2024, 2, 13)
_reg("XSHG", None, '春节（补假）', 2024, 2, 14)
_reg("XSHG", None, '清明节', 2024, 4, 4)
_reg("XSHG", None, '劳动节', 2024, 5, 1)
_reg("XSHG", None, '端午节', 2024, 6, 10)
_reg("XSHG", None, '中秋节', 2024, 9, 17)
_reg("XSHG", None, '国庆节', 2024, 10, 1)
_reg("XSHG", None, '国庆节', 2024, 10, 2)
_reg("XSHG", None, '国庆节', 2024, 10, 3)
_reg("XSHG", None, '元旦', 2025, 1, 1)
_reg("XSHG", None, '农历除夕', 2025, 1, 28)
_reg("XSHG", None, '春节', 2025, 1, 29)
_reg("XSHG", None, '春节', 2025, 1, 30)
_reg("XSHG", None, '春节', 2025, 1, 31)
_reg("XSHG", None, '清明节', 2025, 4, 4)
_reg("XSHG", None, '劳动节', 2025, 5, 1)
_reg("XSHG", None, '劳动节', 2025, 5, 2)
_reg("XSHG", None, '端午节', 2025, 5, 31)
_reg("XSHG", None, '端午节（补假）', 2025, 6, 2)
_reg("XSHG", None, '国庆节', 2025, 10, 1)
_reg("XSHG", None, '国庆节', 2025, 10, 2)
_reg("XSHG", None, '国庆节', 2025, 10, 3)
_reg("XSHG", None, '中秋节', 2025, 10, 6)
_reg("XBOM", None, 'Republic Day', 2024, 1, 26)
_reg("XBOM", None, 'Maha Shivaratri', 2024, 3, 8)
_reg("XBOM", None, 'Holi', 2024, 3, 25)
_reg("XBOM", None, 'Good Friday', 2024, 3, 29)
_reg("XBOM", None, 'Id-Ul-Fitr (Ramadan Eid)', 2024, 4, 11)
_reg("XBOM", None, 'Ram Navami', 2024, 4, 17)
_reg("XBOM", None, 'Maharashtra Day', 2024, 5, 1)
_reg("XBOM", None, 'Bakri Id', 2024, 6, 17)
_reg("XBOM", None, 'Muharram', 2024, 7, 17)
_reg("XBOM", None, 'Independence Day', 2024, 8, 15)
_reg("XBOM", None, 'Mahatma Gandhi Jayanti', 2024, 10, 2)
_reg("XBOM", None, 'Diwali Laxmi Pujan', 2024, 11, 1)
_reg("XBOM", None, 'Guru Nanak Jayanti', 2024, 11, 15)
_reg("XBOM", None, 'Christmas Day', 2024, 12, 25)
_reg("XBOM", None, 'Republic Day', 2025, 1, 26)
_reg("XBOM", None, 'Maha Shivaratri', 2025, 2, 26)
_reg("XBOM", None, 'Holi', 2025, 3, 14)
_reg("XBOM", None, 'Id-Ul-Fitr (Ramadan Eid)', 2025, 3, 31)
_reg("XBOM", None, 'Mahavir Jayanti', 2025, 4, 10)
_reg("XBOM", None, 'Dr. Baba Saheb Ambedkar Jayanti', 2025, 4, 14)
_reg("XBOM", None, 'Good Friday', 2025, 4, 18)
_reg("XBOM", None, 'Maharashtra Day', 2025, 5, 1)
_reg("XBOM", None, 'Independence Day', 2025, 8, 15)
_reg("XBOM", None, 'Ganesh Chaturthi', 2025, 8, 27)
_reg("XBOM", None, 'Dussehra', 2025, 10, 2)
_reg("XBOM", None, 'Mahatma Gandhi Jayanti', 2025, 10, 2)
_reg("XBOM", None, 'Diwali Laxmi Pujan', 2025, 10, 21)
_reg("XBOM", None, 'Diwali Balipratipada', 2025, 10, 22)
_reg("XBOM", None, 'Guru Nanak Jayanti', 2025, 11, 5)
_reg("XBOM", None, 'Christmas Day', 2025, 12, 25)
_reg("BVMF", None, 'Confraternização Universal', 2024, 1, 1)
_reg("BVMF", None, 'Carnaval', 2024, 2, 12)
_reg("BVMF", None, 'Carnaval', 2024, 2, 13)
_reg("BVMF", None, 'Sexta-feira Santa', 2024, 3, 29)
_reg("BVMF", None, 'Tiradentes', 2024, 4, 21)
_reg("BVMF", None, 'Dia do Trabalhador', 2024, 5, 1)
_reg("BVMF", None, 'Corpus Christi', 2024, 5, 30)
_reg("BVMF", None, 'Independência do Brasil', 2024, 9, 7)
_reg("BVMF", None, 'Nossa Senhora Aparecida', 2024, 10, 12)
_reg("BVMF", None, 'Finados', 2024, 11, 2)
_reg("BVMF", None, 'Proclamação da República', 2024, 11, 15)
_reg("BVMF", None, 'Dia Nacional de Zumbi e da Consciência Negra', 2024, 11, 20)
_reg("BVMF", None, 'Natal', 2024, 12, 25)
_reg("BVMF", None, 'Confraternização Universal', 2025, 1, 1)
_reg("BVMF", None, 'Carnaval', 2025, 3, 3)
_reg("BVMF", None, 'Carnaval', 2025, 3, 4)
_reg("BVMF", None, 'Sexta-feira Santa', 2025, 4, 18)
_reg("BVMF", None, 'Tiradentes', 2025, 4, 21)
_reg("BVMF", None, 'Dia do Trabalhador', 2025, 5, 1)
_reg("BVMF", None, 'Corpus Christi', 2025, 6, 19)
_reg("BVMF", None, 'Independência do Brasil', 2025, 9, 7)
_reg("BVMF", None, 'Nossa Senhora Aparecida', 2025, 10, 12)
_reg("BVMF", None, 'Finados', 2025, 11, 2)
_reg("BVMF", None, 'Proclamação da República', 2025, 11, 15)
_reg("BVMF", None, 'Dia Nacional de Zumbi e da Consciência Negra', 2025, 11, 20)
_reg("BVMF", None, 'Natal', 2025, 12, 25)
_reg("XMEX", None, 'Año Nuevo', 2024, 1, 1)
_reg("XMEX", None, 'Día de la Constitución', 2024, 2, 5)
_reg("XMEX", None, 'Natalicio de Benito Juárez', 2024, 3, 18)
_reg("XMEX", None, 'Jueves Santo', 2024, 3, 28)
_reg("XMEX", None, 'Viernes Santo', 2024, 3, 29)
_reg("XMEX", None, 'Día del Trabajo', 2024, 5, 1)
_reg("XMEX", None, 'Día de la Independencia', 2024, 9, 16)
_reg("XMEX", None, 'Transmisión del Poder Ejecutivo Federal', 2024, 10, 1)
_reg("XMEX", None, 'Día de la Revolución', 2024, 11, 18)
_reg("XMEX", None, 'Día del Empleado Bancario', 2024, 12, 12)
_reg("XMEX", None, 'Navidad', 2024, 12, 25)
_reg("XMEX", None, 'Año Nuevo', 2025, 1, 1)
_reg("XMEX", None, 'Día de la Constitución', 2025, 2, 3)
_reg("XMEX", None, 'Natalicio de Benito Juárez', 2025, 3, 17)
_reg("XMEX", None, 'Jueves Santo', 2025, 4, 17)
_reg("XMEX", None, 'Viernes Santo', 2025, 4, 18)
_reg("XMEX", None, 'Día del Trabajo', 2025, 5, 1)
_reg("XMEX", None, 'Día de la Independencia', 2025, 9, 16)
_reg("XMEX", None, 'Día de la Revolución', 2025, 11, 17)
_reg("XMEX", None, 'Día del Empleado Bancario', 2025, 12, 12)
_reg("XMEX", None, 'Navidad', 2025, 12, 25)


# ==========================================================================
# Calendar loads and basic shape
# ==========================================================================
@pytest.mark.parametrize("market", MARKETS)
def test_market_calendar_loads_and_has_rules(market):
    cal = load_calendar(os.path.join(_DATA_DIR, f"{market.lower()}.tab"))
    assert cal.rules
    assert cal.jurisdiction == market


def test_market_aliases_resolve_to_shipped_canonical_files():
    for alias, canonical in MARKET_ALIASES.items():
        path = os.path.join(_DATA_DIR, f"{canonical.lower()}.tab")
        assert os.path.exists(path), f"{alias} -> {canonical}: no such .tab"


@pytest.mark.parametrize("alias,canonical", list(MARKET_ALIASES.items()))
def test_alias_and_canonical_produce_identical_holidays(alias, canonical):
    for year in (2024, 2025):
        alias_dates = {(h.name, h.date) for h in holidays_for(alias, year)}
        canon_dates = {(h.name, h.date) for h in holidays_for(canonical, year)}
        assert alias_dates == canon_dates


# ==========================================================================
# In-test independent weekday/easter arithmetic helpers
# ==========================================================================
def _nth_weekday(year, month, n, weekday):
    """The n-th (n=-1 -> last) `weekday` (Mon=0..Sun=6) of `month`/`year`.

    Implemented with plain calendar arithmetic, independent of
    :mod:`chronologia.recurrence`, per the house rule that nth_weekday golds
    must not re-run the engine on itself.
    """
    first = AstroDate(year, month, 1)
    first_wd = first.weekday()
    if n > 0:
        delta = (weekday - first_wd) % 7 + (n - 1) * 7
        return first + timedelta(days=delta)
    # n == -1: last such weekday in the month
    if month == 12:
        next_month = AstroDate(year + 1, 1, 1)
    else:
        next_month = AstroDate(year, month + 1, 1)
    last_day = next_month - timedelta(days=1)
    delta = (last_day.weekday() - weekday) % 7
    return last_day - timedelta(days=delta)


def _us_observed(date):
    """5 U.S.C. 6103: Saturday -> preceding Friday, Sunday -> following Monday."""
    wd = date.weekday()
    if wd == 5:
        return date - timedelta(days=1)
    if wd == 6:
        return date + timedelta(days=1)
    return date


def _sun_mon_observed(date):
    """Sunday -> following Monday; otherwise unshifted."""
    return date + timedelta(days=1) if date.weekday() == 6 else date


def _dates_for(market, year):
    return {h.name: h.date for h in holidays_for(market, year)}


# ==========================================================================
# XECB (European Central Bank / TARGET2) -- fixed + easter offsets, no
# observed shift (TARGET2 simply does not fall on a weekend-adjacent policy;
# vacanza applies none for this market).
# ==========================================================================
@pytest.mark.parametrize("year", [2024, 2025])
def test_xecb_new_years_day(year):
    got = _dates_for("XECB", year)
    assert got["New Year's Day"] == AstroDate(year, 1, 1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xecb_good_friday(year):
    got = _dates_for("XECB", year)
    expected = easter(year, "gregorian") + timedelta(days=-2)
    assert got["Good Friday"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xecb_easter_monday(year):
    got = _dates_for("XECB", year)
    expected = easter(year, "gregorian") + timedelta(days=1)
    assert got["Easter Monday"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xecb_labour_day(year):
    got = _dates_for("XECB", year)
    assert got["Labour Day"] == AstroDate(year, 5, 1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xecb_christmas_day(year):
    got = _dates_for("XECB", year)
    assert got["Christmas Day"] == AstroDate(year, 12, 25)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xecb_christmas_holiday(year):
    got = _dates_for("XECB", year)
    assert got["Christmas Holiday"] == AstroDate(year, 12, 26)


def test_xecb_six_holidays_per_year():
    for year in (2024, 2025):
        assert len(_dates_for("XECB", year)) == 6


# ==========================================================================
# XNYS (New York Stock Exchange) -- nth_weekday, easter and `us`-observed
# fixed rules.
# ==========================================================================
@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_xnys_new_years_day_us_observed(year):
    got = _dates_for("XNYS", year)
    expected = _us_observed(AstroDate(year, 1, 1))
    assert got["New Year's Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_xnys_mlk_day_third_monday_january(year):
    got = _dates_for("XNYS", year)
    expected = _nth_weekday(year, 1, 3, 0)
    assert got["Martin Luther King Jr. Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_xnys_washingtons_birthday_third_monday_february(year):
    got = _dates_for("XNYS", year)
    expected = _nth_weekday(year, 2, 3, 0)
    assert got["Washington's Birthday"] == expected


@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_xnys_good_friday_easter_minus_2(year):
    got = _dates_for("XNYS", year)
    expected = easter(year, "gregorian") + timedelta(days=-2)
    assert got["Good Friday"] == expected


@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_xnys_memorial_day_last_monday_may(year):
    got = _dates_for("XNYS", year)
    expected = _nth_weekday(year, 5, -1, 0)
    assert got["Memorial Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_xnys_juneteenth_us_observed(year):
    got = _dates_for("XNYS", year)
    expected = _us_observed(AstroDate(year, 6, 19))
    assert got["Juneteenth National Independence Day"] == expected


def test_xnys_juneteenth_absent_before_2022():
    # NYSE only began observing Juneteenth once the 2021 Act took effect;
    # the exchange's own 2021 calendar (a Saturday nominal date that year)
    # carries no Juneteenth closure at all.
    got = _dates_for("XNYS", 2021)
    assert "Juneteenth National Independence Day" not in got


@pytest.mark.parametrize("year", [2024, 2025])
def test_xnys_independence_day_us_observed(year):
    got = _dates_for("XNYS", year)
    expected = _us_observed(AstroDate(year, 7, 4))
    assert got["Independence Day"] == expected


def test_xnys_independence_day_2026_saturday_observed_friday():
    # 4 July 2026 is a Saturday -> observed the preceding Friday, 3 July 2026.
    nominal = AstroDate(2026, 7, 4)
    assert nominal.weekday() == 5   # Saturday, confirms the shift fires
    got = _dates_for("XNYS", 2026)
    assert got["Independence Day"] == AstroDate(2026, 7, 3)


@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_xnys_labor_day_first_monday_september(year):
    got = _dates_for("XNYS", year)
    expected = _nth_weekday(year, 9, 1, 0)
    assert got["Labor Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_xnys_thanksgiving_fourth_thursday_november(year):
    got = _dates_for("XNYS", year)
    expected = _nth_weekday(year, 11, 4, 3)
    assert got["Thanksgiving Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xnys_christmas_day_us_observed(year):
    got = _dates_for("XNYS", year)
    expected = _us_observed(AstroDate(year, 12, 25))
    assert got["Christmas Day"] == expected


# ==========================================================================
# IFEU (ICE Futures Europe) -- fixed + easter, sun_mon-observed fixed rules.
# ==========================================================================
@pytest.mark.parametrize("year", [2024, 2025])
def test_ifeu_new_years_day_sun_mon_observed(year):
    got = _dates_for("IFEU", year)
    expected = _sun_mon_observed(AstroDate(year, 1, 1))
    assert got["New Year's Day"] == expected


def test_ifeu_new_years_day_2023_sunday_observed_monday():
    # 1 Jan 2023 is a Sunday -> observed the following Monday, 2 Jan 2023
    # (verified against vacanza/holidays 0.101 IFEU output).
    nominal = AstroDate(2023, 1, 1)
    assert nominal.weekday() == 6   # Sunday, confirms the shift fires
    got = _dates_for("IFEU", 2023)
    assert got["New Year's Day"] == AstroDate(2023, 1, 2)


@pytest.mark.parametrize("year", [2024, 2025])
def test_ifeu_good_friday_easter_minus_2(year):
    got = _dates_for("IFEU", year)
    expected = easter(year, "gregorian") + timedelta(days=-2)
    assert got["Good Friday"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_ifeu_christmas_day_sun_mon_observed(year):
    got = _dates_for("IFEU", year)
    expected = _sun_mon_observed(AstroDate(year, 12, 25))
    assert got["Christmas Day"] == expected


def test_ifeu_christmas_day_2022_sunday_observed_monday():
    # 25 Dec 2022 is a Sunday -> observed the following Monday, 26 Dec 2022
    # (verified against vacanza/holidays 0.101 IFEU output).
    nominal = AstroDate(2022, 12, 25)
    assert nominal.weekday() == 6   # Sunday, confirms the shift fires
    got = _dates_for("IFEU", 2022)
    assert got["Christmas Day"] == AstroDate(2022, 12, 26)


def test_ifeu_three_holidays_per_year():
    for year in (2024, 2025):
        assert len(_dates_for("IFEU", year)) == 3



# ==========================================================================
# XCME (Chicago Mercantile Exchange) -- the NYSE subset (5 of 10 XNYS
# closures) plus a one-off.
# ==========================================================================
@pytest.mark.parametrize("year", [2024, 2025])
def test_xcme_new_years_day(year):
    got = _dates_for("XCME", year)
    assert got["New Year's Day"] == AstroDate(year, 1, 1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xcme_good_friday(year):
    got = _dates_for("XCME", year)
    expected = easter(year, "gregorian") + timedelta(days=-2)
    assert got["Good Friday"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xcme_independence_day(year):
    got = _dates_for("XCME", year)
    assert got["Independence Day"] == AstroDate(year, 7, 4)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xcme_thanksgiving_day(year):
    got = _dates_for("XCME", year)
    expected = _nth_weekday(year, 11, 4, 3)
    assert got["Thanksgiving Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xcme_christmas_day(year):
    got = _dates_for("XCME", year)
    assert got["Christmas Day"] == AstroDate(year, 12, 25)


def test_xcme_carter_mourning_day_one_off_2025_only():
    got_2025 = _dates_for("XCME", 2025)
    assert got_2025["National Day of Mourning for former President Jimmy Carter"] \
        == AstroDate(2025, 1, 9)
    got_2024 = _dates_for("XCME", 2024)
    assert "National Day of Mourning for former President Jimmy Carter" not in got_2024


# ==========================================================================
# XNAS (Nasdaq) -- date-for-date identical to XNYS's `us`-observed rule
# shape, plus the same one-off Carter mourning day as XCME.
# ==========================================================================
@pytest.mark.parametrize("year", [2024, 2025])
def test_xnas_new_years_day_us_observed(year):
    got = _dates_for("XNAS", year)
    expected = _us_observed(AstroDate(year, 1, 1))
    assert got["New Year's Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xnas_mlk_day_third_monday_january(year):
    got = _dates_for("XNAS", year)
    expected = _nth_weekday(year, 1, 3, 0)
    assert got["Martin Luther King Jr. Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xnas_washingtons_birthday_third_monday_february(year):
    got = _dates_for("XNAS", year)
    expected = _nth_weekday(year, 2, 3, 0)
    assert got["Washington's Birthday"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xnas_good_friday(year):
    got = _dates_for("XNAS", year)
    expected = easter(year, "gregorian") + timedelta(days=-2)
    assert got["Good Friday"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xnas_memorial_day_last_monday_may(year):
    got = _dates_for("XNAS", year)
    expected = _nth_weekday(year, 5, -1, 0)
    assert got["Memorial Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xnas_juneteenth_us_observed(year):
    got = _dates_for("XNAS", year)
    expected = _us_observed(AstroDate(year, 6, 19))
    assert got["Juneteenth National Independence Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xnas_independence_day_us_observed(year):
    got = _dates_for("XNAS", year)
    expected = _us_observed(AstroDate(year, 7, 4))
    assert got["Independence Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xnas_labor_day_first_monday_september(year):
    got = _dates_for("XNAS", year)
    expected = _nth_weekday(year, 9, 1, 0)
    assert got["Labor Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xnas_thanksgiving_fourth_thursday_november(year):
    got = _dates_for("XNAS", year)
    expected = _nth_weekday(year, 11, 4, 3)
    assert got["Thanksgiving Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xnas_christmas_day_us_observed(year):
    got = _dates_for("XNAS", year)
    expected = _us_observed(AstroDate(year, 12, 25))
    assert got["Christmas Day"] == expected


def test_xnas_carter_mourning_day_one_off_2025_only():
    got_2025 = _dates_for("XNAS", 2025)
    assert got_2025["National Day of Mourning for former President Jimmy Carter"] \
        == AstroDate(2025, 1, 9)
    got_2024 = _dates_for("XNAS", 2024)
    assert "National Day of Mourning for former President Jimmy Carter" not in got_2024


# ==========================================================================
# XETR (Xetra / Frankfurt Stock Exchange) -- fixed + easter offsets, German
# primary names.
# ==========================================================================
@pytest.mark.parametrize("year", [2024, 2025])
def test_xetr_neujahr(year):
    got = _dates_for("XETR", year)
    assert got["Neujahr"] == AstroDate(year, 1, 1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xetr_karfreitag(year):
    got = _dates_for("XETR", year)
    expected = easter(year, "gregorian") + timedelta(days=-2)
    assert got["Karfreitag"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xetr_ostermontag(year):
    got = _dates_for("XETR", year)
    expected = easter(year, "gregorian") + timedelta(days=1)
    assert got["Ostermontag"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xetr_erster_mai(year):
    got = _dates_for("XETR", year)
    assert got["Erster Mai"] == AstroDate(year, 5, 1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xetr_christmas_block(year):
    got = _dates_for("XETR", year)
    assert got["Heiligabend"] == AstroDate(year, 12, 24)
    assert got["Erster Weihnachtstag"] == AstroDate(year, 12, 25)
    assert got["Zweiter Weihnachtstag"] == AstroDate(year, 12, 26)
    assert got["Silvester"] == AstroDate(year, 12, 31)


def test_xetr_eight_holidays_per_year():
    for year in (2024, 2025):
        assert len(_dates_for("XETR", year)) == 8


# ==========================================================================
# XSWX (SIX Swiss Exchange) -- fixed + easter offsets (Ascension/Whit
# Monday included), German primary names.
# ==========================================================================
@pytest.mark.parametrize("year", [2024, 2025])
def test_xswx_neujahrstag_and_berchtoldstag(year):
    got = _dates_for("XSWX", year)
    assert got["Neujahrstag"] == AstroDate(year, 1, 1)
    assert got["Berchtoldstag"] == AstroDate(year, 1, 2)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xswx_karfreitag_and_ostermontag(year):
    got = _dates_for("XSWX", year)
    e = easter(year, "gregorian")
    assert got["Karfreitag"] == e + timedelta(days=-2)
    assert got["Ostermontag"] == e + timedelta(days=1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xswx_auffahrt_ascension_easter_plus_39(year):
    got = _dates_for("XSWX", year)
    expected = easter(year, "gregorian") + timedelta(days=39)
    assert got["Auffahrt"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xswx_pfingstmontag_whit_monday_easter_plus_50(year):
    got = _dates_for("XSWX", year)
    expected = easter(year, "gregorian") + timedelta(days=50)
    assert got["Pfingstmontag"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xswx_tag_der_arbeit(year):
    got = _dates_for("XSWX", year)
    assert got["Tag der Arbeit"] == AstroDate(year, 5, 1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xswx_nationalfeiertag(year):
    got = _dates_for("XSWX", year)
    assert got["Nationalfeiertag"] == AstroDate(year, 8, 1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xswx_year_end_block(year):
    got = _dates_for("XSWX", year)
    assert got["Heiligabend"] == AstroDate(year, 12, 24)
    assert got["Weihnachten"] == AstroDate(year, 12, 25)
    assert got["Stephanstag"] == AstroDate(year, 12, 26)
    assert got["Vortag vor Neujahr"] == AstroDate(year, 12, 31)


def test_xswx_twelve_holidays_per_year():
    for year in (2024, 2025):
        assert len(_dates_for("XSWX", year)) == 12


# ==========================================================================
# XTSE (Toronto Stock Exchange) -- nth_weekday, weekday_onbefore, easter and
# `sat_sun_mon`-observed fixed rules.
# ==========================================================================
def _sat_sun_mon_observed(date):
    """Saturday -> following Monday (+2), Sunday -> following Monday (+1)."""
    return date + timedelta(days={5: 2, 6: 1}.get(date.weekday(), 0))


@pytest.mark.parametrize("year", [2024, 2025])
def test_xtse_new_years_day_sat_sun_mon_observed(year):
    got = _dates_for("XTSE", year)
    expected = _sat_sun_mon_observed(AstroDate(year, 1, 1))
    assert got["New Year's Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xtse_family_day_third_monday_february(year):
    got = _dates_for("XTSE", year)
    expected = _nth_weekday(year, 2, 3, 0)
    assert got["Family Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xtse_good_friday(year):
    got = _dates_for("XTSE", year)
    expected = easter(year, "gregorian") + timedelta(days=-2)
    assert got["Good Friday"] == expected


def _monday_on_or_before(year, month, day):
    d = AstroDate(year, month, day)
    return d - timedelta(days=d.weekday())


@pytest.mark.parametrize("year", [2024, 2025])
def test_xtse_victoria_day_monday_on_or_before_may_24(year):
    got = _dates_for("XTSE", year)
    expected = _monday_on_or_before(year, 5, 24)
    assert got["Victoria Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xtse_canada_day_sat_sun_mon_observed(year):
    got = _dates_for("XTSE", year)
    expected = _sat_sun_mon_observed(AstroDate(year, 7, 1))
    assert got["Canada Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xtse_civic_holiday_first_monday_august(year):
    got = _dates_for("XTSE", year)
    expected = _nth_weekday(year, 8, 1, 0)
    assert got["Civic Holiday"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xtse_labour_day_first_monday_september(year):
    got = _dates_for("XTSE", year)
    expected = _nth_weekday(year, 9, 1, 0)
    assert got["Labour Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xtse_thanksgiving_second_monday_october(year):
    got = _dates_for("XTSE", year)
    expected = _nth_weekday(year, 10, 2, 0)
    assert got["Thanksgiving Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xtse_christmas_and_boxing_day(year):
    got = _dates_for("XTSE", year)
    assert got["Christmas Day"] == _sat_sun_mon_observed(AstroDate(year, 12, 25))
    assert got["Boxing Day"] == _sat_sun_mon_observed(AstroDate(year, 12, 26))


@pytest.mark.parametrize("year,christmas,boxing", [
    # Christmas AND Boxing both on a weekend: Christmas relocates to Monday,
    # Boxing cascades one further business day so the pair never collides.
    (2021, (12, 27), (12, 28)),   # Sat 25 -> Mon 27, Sun 26 -> Tue 28
    (2027, (12, 27), (12, 28)),   # same shape as 2021
    # Christmas (Sun 25) relocates onto Boxing's own weekday (Mon 26), so Boxing
    # must bump forward too even though its nominal is a weekday.
    (2022, (12, 26), (12, 27)),   # Sun 25 -> Mon 26, Mon 26 -> Tue 27
])
def test_xtse_christmas_boxing_weekend_collision_cascade(year, christmas, boxing):
    # Regression for the relocating-cascade fix: the exchange lists only the
    # observed weekday closure (no weekend nominal) and the two closures must be
    # DISTINCT days. Independently arithmetic-verified above and matches
    # holidays.financial_holidays('XTSE') for these years.
    got = _dates_for("XTSE", year)
    assert got["Christmas Day"] == AstroDate(year, *christmas)
    assert got["Boxing Day"] == AstroDate(year, *boxing)
    assert got["Christmas Day"] != got["Boxing Day"]     # no collision


# ==========================================================================
# XHKG (Hong Kong Stock Exchange) -- Gregorian fixed/easter rules plus
# honest `decree` rows for the Chinese-lunar and Buddhist-lunar closures.
# ==========================================================================
@pytest.mark.parametrize("year", [2024, 2025])
def test_xhkg_first_day_of_january(year):
    got = _dates_for("XHKG", year)
    assert got["The first day of January"] == AstroDate(year, 1, 1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xhkg_good_friday_and_easter_monday(year):
    got = _dates_for("XHKG", year)
    e = easter(year, "gregorian")
    assert got["Good Friday"] == e + timedelta(days=-2)
    assert got["Easter Monday"] == e + timedelta(days=1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xhkg_labour_day(year):
    got = _dates_for("XHKG", year)
    assert got["Labour Day"] == AstroDate(year, 5, 1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xhkg_sar_establishment_and_national_day(year):
    got = _dates_for("XHKG", year)
    assert got["Hong Kong Special Administrative Region Establishment Day"] \
        == AstroDate(year, 7, 1)
    assert got["National Day"] == AstroDate(year, 10, 1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xhkg_christmas_block(year):
    got = _dates_for("XHKG", year)
    assert got["Christmas Day"] == AstroDate(year, 12, 25)
    assert got["The first weekday after Christmas Day"] == AstroDate(year, 12, 26)


def test_xhkg_lunar_new_year_2024_dates_tabulated():
    # Vacanza 0.101's 2024 Lunar New Year block (3rd/4th day only that
    # year -- the 1st/2nd days fell on the preceding weekend).
    got = holidays_for("XHKG", 2024)
    lunar = sorted(h.date for h in got if h.name == "Lunar New Year")
    assert lunar == [AstroDate(2024, 2, 12), AstroDate(2024, 2, 13)]


def test_xhkg_lunar_new_year_2025_dates_tabulated():
    got = holidays_for("XHKG", 2025)
    lunar = sorted(h.date for h in got if h.name == "Lunar New Year")
    assert lunar == [AstroDate(2025, 1, 29), AstroDate(2025, 1, 30), AstroDate(2025, 1, 31)]


@pytest.mark.parametrize("year,expected", [(2024, (4, 4)), (2025, (4, 4))])
def test_xhkg_ching_ming_festival_tabulated(year, expected):
    got = _dates_for("XHKG", year)
    assert got["Ching Ming Festival"] == AstroDate(year, *expected)


@pytest.mark.parametrize("year,expected", [(2024, (5, 15)), (2025, (5, 5))])
def test_xhkg_birthday_of_buddha_tabulated(year, expected):
    got = _dates_for("XHKG", year)
    assert got["The Birthday of the Buddha"] == AstroDate(year, *expected)


def test_xhkg_tuen_ng_festival_2024_only_tabulated():
    # 2025's Tuen Ng fell on a weekend and carries no vacanza 0.101 entry --
    # matching the IFEU/XSWX house precedent that a weekend closure with no
    # substitute policy is harmlessly absent, not a bug.
    got_2024 = _dates_for("XHKG", 2024)
    assert got_2024["Tuen Ng Festival"] == AstroDate(2024, 6, 10)
    got_2025 = _dates_for("XHKG", 2025)
    assert "Tuen Ng Festival" not in got_2025


@pytest.mark.parametrize("year,expected", [(2024, (9, 18)), (2025, (10, 7))])
def test_xhkg_mid_autumn_followed_day_tabulated(year, expected):
    got = _dates_for("XHKG", year)
    assert got["The day following the Chinese Mid-Autumn Festival"] == AstroDate(year, *expected)


@pytest.mark.parametrize("year,expected", [(2024, (10, 11)), (2025, (10, 29))])
def test_xhkg_chung_yeung_festival_tabulated(year, expected):
    got = _dates_for("XHKG", year)
    assert got["Chung Yeung Festival"] == AstroDate(year, *expected)


# ==========================================================================
# XJPX (Japan Exchange Group) -- shares its Gregorian/nth_weekday/equinox
# rule shape with jp.tab, plus the year-end bank-holiday block.
# ==========================================================================
@pytest.mark.parametrize("year", [2024, 2025])
def test_xjpx_new_years_day(year):
    got = _dates_for("XJPX", year)
    assert got["New Year's Day"] == AstroDate(year, 1, 1)


def test_xjpx_bank_holiday_block_all_three_dates_2024():
    dates = sorted(h.date for h in holidays_for("XJPX", 2024) if h.name == "Bank Holiday")
    assert dates == [AstroDate(2024, 1, 2), AstroDate(2024, 1, 3), AstroDate(2024, 12, 31)]


def test_xjpx_bank_holiday_block_all_three_dates_2025():
    dates = sorted(h.date for h in holidays_for("XJPX", 2025) if h.name == "Bank Holiday")
    assert dates == [AstroDate(2025, 1, 2), AstroDate(2025, 1, 3), AstroDate(2025, 12, 31)]


@pytest.mark.parametrize("year", [2024, 2025])
def test_xjpx_coming_of_age_day_second_monday_january(year):
    got = _dates_for("XJPX", year)
    expected = _nth_weekday(year, 1, 2, 0)
    assert got["Coming of Age Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xjpx_foundation_day(year):
    got = _dates_for("XJPX", year)
    assert got["Foundation Day"] == AstroDate(year, 2, 11)


def test_xjpx_foundation_day_furikae_2024_sunday():
    # 11 Feb 2024 is a Sunday -> furikae substitute the next non-holiday day.
    nominal = AstroDate(2024, 2, 11)
    assert nominal.weekday() == 6
    got = _dates_for("XJPX", 2024)
    assert got["Foundation Day (振替休日)"] == AstroDate(2024, 2, 12)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xjpx_emperors_birthday(year):
    got = _dates_for("XJPX", year)
    assert got["Emperor's Birthday"] == AstroDate(year, 2, 23)


def test_xjpx_emperors_birthday_furikae_2025_sunday():
    nominal = AstroDate(2025, 2, 23)
    assert nominal.weekday() == 6
    got = _dates_for("XJPX", 2025)
    assert got["Emperor's Birthday (振替休日)"] == AstroDate(2025, 2, 24)


@pytest.mark.parametrize("year,expected", [(2024, (3, 20)), (2025, (3, 20))])
def test_xjpx_vernal_equinox_day_tabulated(year, expected):
    got = _dates_for("XJPX", year)
    assert got["Vernal Equinox Day"] == AstroDate(year, *expected)


@pytest.mark.parametrize("year,expected", [(2024, (9, 22)), (2025, (9, 23))])
def test_xjpx_autumnal_equinox_day_tabulated(year, expected):
    got = _dates_for("XJPX", year)
    assert got["Autumnal Equinox Day"] == AstroDate(year, *expected)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xjpx_showa_day(year):
    got = _dates_for("XJPX", year)
    assert got["Showa Day"] == AstroDate(year, 4, 29)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xjpx_golden_week_fixed_days(year):
    got = _dates_for("XJPX", year)
    assert got["Constitution Day"] == AstroDate(year, 5, 3)
    assert got["Greenery Day"] == AstroDate(year, 5, 4)
    assert got["Children's Day"] == AstroDate(year, 5, 5)


def test_xjpx_golden_week_furikae_2024_childrens_day_sunday():
    nominal = AstroDate(2024, 5, 5)
    assert nominal.weekday() == 6
    got = _dates_for("XJPX", 2024)
    assert got["Children's Day (振替休日)"] == AstroDate(2024, 5, 6)


def test_xjpx_golden_week_furikae_2025_greenery_day_sunday():
    nominal = AstroDate(2025, 5, 4)
    assert nominal.weekday() == 6
    got = _dates_for("XJPX", 2025)
    assert got["Greenery Day (振替休日)"] == AstroDate(2025, 5, 6)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xjpx_marine_day_third_monday_july(year):
    got = _dates_for("XJPX", year)
    expected = _nth_weekday(year, 7, 3, 0)
    assert got["Marine Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xjpx_mountain_day(year):
    got = _dates_for("XJPX", year)
    assert got["Mountain Day"] == AstroDate(year, 8, 11)


def test_xjpx_mountain_day_furikae_2024_sunday():
    nominal = AstroDate(2024, 8, 11)
    assert nominal.weekday() == 6
    got = _dates_for("XJPX", 2024)
    assert got["Mountain Day (振替休日)"] == AstroDate(2024, 8, 12)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xjpx_respect_for_the_aged_day_third_monday_september(year):
    got = _dates_for("XJPX", year)
    expected = _nth_weekday(year, 9, 3, 0)
    assert got["Respect for the Aged Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xjpx_sports_day_second_monday_october(year):
    got = _dates_for("XJPX", year)
    expected = _nth_weekday(year, 10, 2, 0)
    assert got["Sports Day"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xjpx_culture_day(year):
    got = _dates_for("XJPX", year)
    assert got["Culture Day"] == AstroDate(year, 11, 3)


def test_xjpx_culture_day_furikae_2024_sunday():
    nominal = AstroDate(2024, 11, 3)
    assert nominal.weekday() == 6
    got = _dates_for("XJPX", 2024)
    assert got["Culture Day (振替休日)"] == AstroDate(2024, 11, 4)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xjpx_labor_thanksgiving_day(year):
    got = _dates_for("XJPX", year)
    assert got["Labor Thanksgiving Day"] == AstroDate(year, 11, 23)


def test_xjpx_labor_thanksgiving_day_furikae_2025_sunday():
    nominal = AstroDate(2025, 11, 23)
    assert nominal.weekday() == 6
    got = _dates_for("XJPX", 2025)
    assert got["Labor Thanksgiving Day (振替休日)"] == AstroDate(2025, 11, 24)


# ==========================================================================
# XSHG (Shanghai/Shenzhen Stock Exchange) -- entirely `decree` rows: China's
# State Council gazettes each year's actual trading-holiday dates fresh,
# with no fixed-arithmetic formula (see the .tab header for the excluded
# 调休 weekend-shuffle notice text, matching cn.tab's own precedent).
# ==========================================================================
@pytest.mark.parametrize("year,expected", [(2024, (1, 1)), (2025, (1, 1))])
def test_xshg_new_years_day_tabulated(year, expected):
    got = _dates_for("XSHG", year)
    assert got["元旦"] == AstroDate(year, *expected)


def test_xshg_spring_festival_block_2024_tabulated():
    dates = sorted(h.date for h in holidays_for("XSHG", 2024) if h.name == "春节")
    assert dates == [AstroDate(2024, 2, 10), AstroDate(2024, 2, 11), AstroDate(2024, 2, 12)]
    makeup = sorted(h.date for h in holidays_for("XSHG", 2024) if h.name == "春节（补假）")
    assert makeup == [AstroDate(2024, 2, 13), AstroDate(2024, 2, 14)]


def test_xshg_spring_festival_block_2025_tabulated():
    dates = sorted(h.date for h in holidays_for("XSHG", 2025) if h.name == "春节")
    assert dates == [AstroDate(2025, 1, 29), AstroDate(2025, 1, 30), AstroDate(2025, 1, 31)]


@pytest.mark.parametrize("year,expected", [(2024, (2, 9)), (2025, (1, 28))])
def test_xshg_chinese_new_years_eve_tabulated(year, expected):
    got = _dates_for("XSHG", year)
    assert got["农历除夕"] == AstroDate(year, *expected)


@pytest.mark.parametrize("year,expected", [(2024, (4, 4)), (2025, (4, 4))])
def test_xshg_ching_ming_festival_tabulated(year, expected):
    got = _dates_for("XSHG", year)
    assert got["清明节"] == AstroDate(year, *expected)


def test_xshg_labour_day_block_2025_two_days():
    dates = sorted(h.date for h in holidays_for("XSHG", 2025) if h.name == "劳动节")
    assert dates == [AstroDate(2025, 5, 1), AstroDate(2025, 5, 2)]


@pytest.mark.parametrize("year,expected", [(2024, (6, 10)), (2025, (5, 31))])
def test_xshg_dragon_boat_festival_tabulated(year, expected):
    got = _dates_for("XSHG", year)
    assert got["端午节"] == AstroDate(year, *expected)


@pytest.mark.parametrize("year,expected", [(2024, (9, 17)), (2025, (10, 6))])
def test_xshg_mid_autumn_festival_tabulated(year, expected):
    got = _dates_for("XSHG", year)
    assert got["中秋节"] == AstroDate(year, *expected)


def test_xshg_national_day_block_three_days():
    for year in (2024, 2025):
        dates = sorted(h.date for h in holidays_for("XSHG", year) if h.name == "国庆节")
        assert dates == [AstroDate(year, 10, 1), AstroDate(year, 10, 2), AstroDate(year, 10, 3)]


# ==========================================================================
# XBOM (Bombay Stock Exchange / NSE) -- fixed + easter rules for the
# Gregorian closures, honest `decree` rows for the Hindu-lunisolar and
# Islamic-lunar closures SEBI gazettes fresh each year.
# ==========================================================================
@pytest.mark.parametrize("year", [2024, 2025])
def test_xbom_republic_day(year):
    got = _dates_for("XBOM", year)
    assert got["Republic Day"] == AstroDate(year, 1, 26)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xbom_good_friday(year):
    got = _dates_for("XBOM", year)
    expected = easter(year, "gregorian") + timedelta(days=-2)
    assert got["Good Friday"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xbom_maharashtra_day(year):
    got = _dates_for("XBOM", year)
    assert got["Maharashtra Day"] == AstroDate(year, 5, 1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xbom_independence_day(year):
    got = _dates_for("XBOM", year)
    assert got["Independence Day"] == AstroDate(year, 8, 15)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xbom_mahatma_gandhi_jayanti(year):
    got = _dates_for("XBOM", year)
    assert got["Mahatma Gandhi Jayanti"] == AstroDate(year, 10, 2)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xbom_christmas_day(year):
    got = _dates_for("XBOM", year)
    assert got["Christmas Day"] == AstroDate(year, 12, 25)


@pytest.mark.parametrize("year,expected", [(2024, (3, 8)), (2025, (2, 26))])
def test_xbom_maha_shivaratri_tabulated(year, expected):
    got = _dates_for("XBOM", year)
    assert got["Maha Shivaratri"] == AstroDate(year, *expected)


@pytest.mark.parametrize("year,expected", [(2024, (3, 25)), (2025, (3, 14))])
def test_xbom_holi_tabulated(year, expected):
    got = _dates_for("XBOM", year)
    assert got["Holi"] == AstroDate(year, *expected)


@pytest.mark.parametrize("year,expected", [(2024, (4, 11)), (2025, (3, 31))])
def test_xbom_id_ul_fitr_tabulated(year, expected):
    got = _dates_for("XBOM", year)
    assert got["Id-Ul-Fitr (Ramadan Eid)"] == AstroDate(year, *expected)


def test_xbom_ram_navami_2024_only_tabulated():
    got_2024 = _dates_for("XBOM", 2024)
    assert got_2024["Ram Navami"] == AstroDate(2024, 4, 17)
    got_2025 = _dates_for("XBOM", 2025)
    assert "Ram Navami" not in got_2025


def test_xbom_mahavir_jayanti_2025_only_tabulated():
    got_2025 = _dates_for("XBOM", 2025)
    assert got_2025["Mahavir Jayanti"] == AstroDate(2025, 4, 10)
    got_2024 = _dates_for("XBOM", 2024)
    assert "Mahavir Jayanti" not in got_2024


def test_xbom_ambedkar_jayanti_2025_only_tabulated():
    got_2025 = _dates_for("XBOM", 2025)
    assert got_2025["Dr. Baba Saheb Ambedkar Jayanti"] == AstroDate(2025, 4, 14)


def test_xbom_bakri_id_and_muharram_2024_only_tabulated():
    got_2024 = _dates_for("XBOM", 2024)
    assert got_2024["Bakri Id"] == AstroDate(2024, 6, 17)
    assert got_2024["Muharram"] == AstroDate(2024, 7, 17)


def test_xbom_ganesh_chaturthi_2025_only_tabulated():
    got_2025 = _dates_for("XBOM", 2025)
    assert got_2025["Ganesh Chaturthi"] == AstroDate(2025, 8, 27)


def test_xbom_dussehra_2025_coincides_with_gandhi_jayanti():
    got_2025 = _dates_for("XBOM", 2025)
    assert got_2025["Dussehra"] == AstroDate(2025, 10, 2)
    assert got_2025["Mahatma Gandhi Jayanti"] == AstroDate(2025, 10, 2)


@pytest.mark.parametrize("year,expected", [(2024, (11, 1)), (2025, (10, 21))])
def test_xbom_diwali_laxmi_pujan_tabulated(year, expected):
    got = _dates_for("XBOM", year)
    assert got["Diwali Laxmi Pujan"] == AstroDate(year, *expected)


def test_xbom_diwali_balipratipada_2025_only_tabulated():
    got_2025 = _dates_for("XBOM", 2025)
    assert got_2025["Diwali Balipratipada"] == AstroDate(2025, 10, 22)


@pytest.mark.parametrize("year,expected", [(2024, (11, 15)), (2025, (11, 5))])
def test_xbom_guru_nanak_jayanti_tabulated(year, expected):
    got = _dates_for("XBOM", year)
    assert got["Guru Nanak Jayanti"] == AstroDate(year, *expected)


# ==========================================================================
# BVMF (B3, Brasil Bolsa Balcao) -- fixed Gregorian dates plus real
# Easter-offset rules (Carnaval, Sexta-feira Santa, Corpus Christi).
# ==========================================================================
@pytest.mark.parametrize("year", [2024, 2025])
def test_bvmf_confraternizacao_universal(year):
    got = _dates_for("BVMF", year)
    assert got["Confraternização Universal"] == AstroDate(year, 1, 1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_bvmf_carnaval_easter_minus_48_and_47(year):
    got = _dates_for("BVMF", year)
    e = easter(year, "gregorian")
    carnaval_dates = sorted(h.date for h in holidays_for("BVMF", year) if h.name == "Carnaval")
    assert carnaval_dates == sorted([e + timedelta(days=-48), e + timedelta(days=-47)])


@pytest.mark.parametrize("year", [2024, 2025])
def test_bvmf_sexta_feira_santa_good_friday(year):
    got = _dates_for("BVMF", year)
    expected = easter(year, "gregorian") + timedelta(days=-2)
    assert got["Sexta-feira Santa"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_bvmf_tiradentes(year):
    got = _dates_for("BVMF", year)
    assert got["Tiradentes"] == AstroDate(year, 4, 21)


@pytest.mark.parametrize("year", [2024, 2025])
def test_bvmf_dia_do_trabalhador(year):
    got = _dates_for("BVMF", year)
    assert got["Dia do Trabalhador"] == AstroDate(year, 5, 1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_bvmf_corpus_christi_easter_plus_60(year):
    got = _dates_for("BVMF", year)
    expected = easter(year, "gregorian") + timedelta(days=60)
    assert got["Corpus Christi"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_bvmf_independencia_do_brasil(year):
    got = _dates_for("BVMF", year)
    assert got["Independência do Brasil"] == AstroDate(year, 9, 7)


@pytest.mark.parametrize("year", [2024, 2025])
def test_bvmf_nossa_senhora_aparecida(year):
    got = _dates_for("BVMF", year)
    assert got["Nossa Senhora Aparecida"] == AstroDate(year, 10, 12)


@pytest.mark.parametrize("year", [2024, 2025])
def test_bvmf_finados(year):
    got = _dates_for("BVMF", year)
    assert got["Finados"] == AstroDate(year, 11, 2)


@pytest.mark.parametrize("year", [2024, 2025])
def test_bvmf_proclamacao_da_republica(year):
    got = _dates_for("BVMF", year)
    assert got["Proclamação da República"] == AstroDate(year, 11, 15)


@pytest.mark.parametrize("year", [2024, 2025])
def test_bvmf_dia_nacional_de_zumbi(year):
    got = _dates_for("BVMF", year)
    assert got["Dia Nacional de Zumbi e da Consciência Negra"] == AstroDate(year, 11, 20)


@pytest.mark.parametrize("year", [2024, 2025])
def test_bvmf_natal(year):
    got = _dates_for("BVMF", year)
    assert got["Natal"] == AstroDate(year, 12, 25)


def test_bvmf_thirteen_holidays_per_year():
    for year in (2024, 2025):
        assert len(list(holidays_for("BVMF", year))) == 13


# ==========================================================================
# XMEX (Bolsa Mexicana de Valores) -- fixed + easter + nth_weekday
# "ley del lunes" rules, plus a one-off and a decree row.
# ==========================================================================
@pytest.mark.parametrize("year", [2024, 2025])
def test_xmex_ano_nuevo(year):
    got = _dates_for("XMEX", year)
    assert got["Año Nuevo"] == AstroDate(year, 1, 1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xmex_dia_de_la_constitucion_first_monday_february(year):
    got = _dates_for("XMEX", year)
    expected = _nth_weekday(year, 2, 1, 0)
    assert got["Día de la Constitución"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xmex_natalicio_de_benito_juarez_third_monday_march(year):
    got = _dates_for("XMEX", year)
    expected = _nth_weekday(year, 3, 3, 0)
    assert got["Natalicio de Benito Juárez"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xmex_semana_santa_jueves_and_viernes_santo(year):
    got = _dates_for("XMEX", year)
    e = easter(year, "gregorian")
    assert got["Jueves Santo"] == e + timedelta(days=-3)
    assert got["Viernes Santo"] == e + timedelta(days=-2)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xmex_dia_del_trabajo(year):
    got = _dates_for("XMEX", year)
    assert got["Día del Trabajo"] == AstroDate(year, 5, 1)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xmex_dia_de_la_independencia(year):
    got = _dates_for("XMEX", year)
    assert got["Día de la Independencia"] == AstroDate(year, 9, 16)


@pytest.mark.parametrize("year", [2024, 2025])
def test_xmex_dia_de_la_revolucion_third_monday_november(year):
    got = _dates_for("XMEX", year)
    expected = _nth_weekday(year, 11, 3, 0)
    assert got["Día de la Revolución"] == expected


@pytest.mark.parametrize("year", [2024, 2025])
def test_xmex_navidad(year):
    got = _dates_for("XMEX", year)
    assert got["Navidad"] == AstroDate(year, 12, 25)


def test_xmex_transmision_del_poder_ejecutivo_one_off_2024_only():
    got_2024 = _dates_for("XMEX", 2024)
    assert got_2024["Transmisión del Poder Ejecutivo Federal"] == AstroDate(2024, 10, 1)
    got_2025 = _dates_for("XMEX", 2025)
    assert "Transmisión del Poder Ejecutivo Federal" not in got_2025


@pytest.mark.parametrize("year", [2024, 2025])
def test_xmex_dia_del_empleado_bancario_tabulated(year):
    got = _dates_for("XMEX", year)
    assert got["Día del Empleado Bancario"] == AstroDate(year, 12, 12)
