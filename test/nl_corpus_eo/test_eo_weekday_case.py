"""The Esperanto weekday accusative (-n) vs adverbial (-e) split.

Accusative "lundon" names a SINGLE, specific occurrence ("La stevardino
flugos al Parizo lundon" -- the flight attendant will fly to Paris [this
coming] Monday); adverbial "lunde" names a HABITUAL recurrence ("lunde" --
on Mondays, "flugas ... lunde" -- flies ... on Mondays).
Source: en.wiktionary.org, "lundo".

The two BARE (unmarked) suffixes are gated to DIFFERENT vocabulary: only the
accusative forms are shipped in ``weekday_N.voc``, feeding the
single-occurrence ``weekday_ref``/``calendar_date`` constructions.  The
adverbial forms are never added to that vocabulary at all -- adding them
would let a bare "lunde" (habitual, no occurrence implied) resolve to a
concrete next-Monday date, exactly the silent conflation the two suffixes
must never share.  A BARE accusative or adverbial weekday, with no
distributive marker in front of it, therefore only ever reads as a single
date (accusative) or refuses outright (adverbial) -- never a recurrence.

"ĉiu"/"ĉiun" (every) + the SAME accusative weekday is a genuinely
DIFFERENT, well-attested construction, not a conflation of the bare split
above: Esperanto's distributive determiner "ĉiu" governs the accusative on
the noun it distributes over exactly as it does for units ("ĉiun tagon" --
every day, see test_eo_recurrence.py), and the combination names a WEEKLY
recurrence ("ĉiun lundon" -- every Monday), never a single date. The
adverbial "-e" form is still never wired to any recurrence surface: "ĉiu
lunde"/"lunde" alone refuse, mirroring the Hindi locale's documented
refusal of a bare recurring weekday (``locale/hi/marker_weekday_word.voc``)
-- Esperanto's "ĉiu(n) ACCUSATIVE" idiom covers the same meaning through
attested vocabulary instead.
"""
import pytest

from chronologia import extract_recurrence

from ._corpus import ANCHOR, nomatch, start


def test_bare_accusative_is_a_single_upcoming_monday():
    got = start("lundon")
    assert (got - ANCHOR).days >= 0
    assert got.weekday() == 0  # Monday


def test_bare_adverbial_never_reads_as_a_date():
    """The habitual "-e" form is NOT wired into any construction: reading it
    as a single date would be the exact conflation this split forbids."""
    nomatch("lunde")


@pytest.mark.parametrize("text", ["marde", "merkrede", "ĵaŭde", "vendrede",
                                  "sabate", "dimanĉe"])
def test_every_weekday_s_adverbial_form_is_refused(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["ĉiu lunde", "lunde"])
def test_adverbial_recurrence_is_refused_even_under_every(text):
    """The adverbial form gains no recurrence reading from a leading "ĉiu"
    either -- only the accusative idiom is wired."""
    assert extract_recurrence(text, "eo", ANCHOR) is None


def test_bare_accusative_alone_is_still_not_a_recurrence():
    """With no distributive marker in front of it, the accusative stays the
    single-date reading -- extract_recurrence must not promote it."""
    assert extract_recurrence("lundon", "eo", ANCHOR) is None


@pytest.mark.parametrize("text,wd", [
    ("ĉiu lundon", 0), ("ĉiun lundon", 0), ("ĉiun mardon", 1),
])
def test_every_plus_accusative_weekday_is_a_weekly_recurrence(text, wd):
    """"ĉiu(n) ACCUSATIVE" is the attested distributive-accusative idiom
    (mirrors "ĉiun tagon" -- every day), not a reuse of the bare
    single-occurrence reading: it resolves to a WEEKLY rule on that
    weekday, both with and without "ĉiu" itself taking the accusative."""
    got = extract_recurrence(text, "eo", ANCHOR)
    assert got is not None
    assert got.recurrence.freq == "WEEKLY"
    assert got.recurrence.byday == ((None, wd),)
