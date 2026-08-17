"""cs: a bare PLURAL relative-offset unit is not an implied one.

relative_offset's bare-unit orders use "MARKER USG" / "USG MARKER" (schema
"singular_units", from unit1_<unit>.voc): USG only ever supplies the
noun's singular case surfaces, so a marker-bound bare unit reads as
quantity one exactly when it is grammatically singular. "za týdny" is
the plural "weeks" with no numeral -- not "in a week" -- and must stay a
hard non-match, the same way "za tygodnie" does in pl.
"""
from ._corpus import nomatch


def test_bare_plural_is_not_an_offset():
    nomatch("za týdny")
    nomatch("za roky")
    nomatch("za dny")
