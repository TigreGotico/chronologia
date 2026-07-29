"""Shared gold generators for the Asturian NL corpus sweep.

Every expected value here is produced by independent Python date arithmetic
(``calendar`` / ``datetime`` / ``timedelta``) -- never by pinning the parser's
own output.  The surfaces are real Asturian phrasings a native speaker would
say; the maths is what a native reviewer independently expects them to mean.
"""
from calendar import monthrange
from datetime import date

#: primary Asturian month surfaces (index -> word)
MON = {1: "xineru", 2: "febreru", 3: "marzu", 4: "abril", 5: "mayu",
       6: "xunu", 7: "xunetu", 8: "agostu", 9: "setiembre", 10: "ochobre",
       11: "payares", 12: "avientu"}

#: weekday surfaces, Python weekday() convention (Mon=0 .. Sun=6)
WD = {0: "llunes", 1: "martes", 2: "miércoles", 3: "xueves",
      4: "vienres", 5: "sábadu", 6: "domingu"}

#: ordinals the Romance number-extractor resolves for ast (1..5).  cuartu/quintu
#: are fraction homographs; their ordinal reading is positionally licensed by a
#: preceding definite article (see numfold ``_ROMANCE_DEFINITE['ast']``).
ORD = {1: "primeru", 2: "segundu", 3: "terceru", 4: "cuartu", 5: "quintu"}

#: seasons -> (start_month, end_month) in a normal (non-wrapping) year
SEAS = {"primavera": (3, 6), "branu": (6, 9), "seronda": (9, 12),
        "iviernu": (12, 3)}


def nth_weekday(year, month, weekday, n):
    """Date of the ``n``-th ``weekday`` in ``year``/``month`` or None."""
    first = date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    day = 1 + offset + (n - 1) * 7
    if day > monthrange(year, month)[1]:
        return None
    return date(year, month, day)


def last_dom(year, month):
    return monthrange(year, month)[1]
