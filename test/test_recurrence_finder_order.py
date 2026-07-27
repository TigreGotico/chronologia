"""The recurrence finder chain is order-sensitive: enforce the two edges.

``chronologia.extract.nseries._FINDERS`` is tried first-match-wins, and its
order carries meaning that the definition order in the module does not.  The
comment at ``_FINDERS`` records two constraints; this file makes them fail
loudly instead of merely being described, by rebuilding the tuple in the
broken order and asserting the phrases that depend on the constraint change
their reading.

Only the two real edges are asserted.  The remaining five finders are
order-independent (every adjacent swap of the shipped order leaves the whole
recurrence corpus green), so nothing here pretends they are ranked.
"""
import pytest

from chronologia.extract import nseries
from chronologia.extract.nseries import extract_recurrence


@pytest.fixture
def reordered(monkeypatch):
    """Run the extractor with ``finder`` moved to the front / back of the chain."""
    def _apply(finder, first=True):
        rest = [f for f in nseries._FINDERS if f is not finder]
        order = [finder] + rest if first else rest + [finder]
        monkeypatch.setattr(nseries, "_FINDERS", tuple(order))
    return _apply


# ``_recur_every`` is a greedy catch-all and must run AFTER the specific
# finders: these phrases all embed an "every"/"cada"/"chaque"/"jeden"
# determiner inside a longer, more specific frame.
_EVERY_FIRST_BREAKS = [
    ("en", "every 10th of may", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10"),
    ("en", "first monday of every month", "FREQ=MONTHLY;BYDAY=1MO"),
    ("de", "jeden 25. dezember", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25"),
    ("es", "el 10 de cada mes", "FREQ=MONTHLY;BYMONTHDAY=10"),
    ("fr", "le 10 de chaque mois", "FREQ=MONTHLY;BYMONTHDAY=10"),
    ("pt", "no dia 15 de cada mês", "FREQ=MONTHLY;BYMONTHDAY=15"),
]


@pytest.mark.parametrize("lang,text,rrule", _EVERY_FIRST_BREAKS)
def test_shipped_order_reads_the_specific_frame(lang, text, rrule):
    got = extract_recurrence(text, lang)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule


@pytest.mark.parametrize("lang,text,rrule", _EVERY_FIRST_BREAKS)
def test_every_first_breaks_the_specific_frame(lang, text, rrule, reordered):
    reordered(nseries._recur_every, first=True)
    got = extract_recurrence(text, lang)
    assert got is None or got[0].to_string() != rrule, (
        f"{text!r} survived _recur_every running first -- if this reading is "
        "genuinely order-independent now, update the constraint comment at "
        "_FINDERS rather than deleting this test")


# ``_recur_habitual_weekday`` must run LAST: a habitual phrase carries a
# frequency count whose weekday tail belongs to the more specific reading.
_HABITUAL_FIRST_BREAKS = [
    ("pt", "uma vez por semana à segunda", "FREQ=WEEKLY;BYDAY=MO", ""),
]


@pytest.mark.parametrize("lang,text,rrule,remainder", _HABITUAL_FIRST_BREAKS)
def test_shipped_order_reads_the_habitual_phrase(lang, text, rrule, remainder):
    got = extract_recurrence(text, lang)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert (got[0].to_string(), got[1]) == (rrule, remainder)


@pytest.mark.parametrize("lang,text,rrule,remainder", _HABITUAL_FIRST_BREAKS)
def test_habitual_first_breaks_the_habitual_phrase(lang, text, rrule,
                                                   remainder, reordered):
    reordered(nseries._recur_habitual_weekday, first=True)
    got = extract_recurrence(text, lang)
    assert got is None or (got[0].to_string(), got[1]) != (rrule, remainder), (
        f"{text!r} survived _recur_habitual_weekday running first -- if this "
        "reading is genuinely order-independent now, update the constraint "
        "comment at _FINDERS rather than deleting this test")


def test_finders_tuple_is_the_documented_order():
    """The shipped order, spelled out -- a reorder must be a deliberate edit."""
    assert [f.__name__ for f in nseries._FINDERS] == [
        "_recur_nth_weekday", "_recur_holiday", "_recur_date_anchored",
        "_recur_once", "_recur_on_weekdays", "_recur_every", "_recur_freq_word",
        "_recur_habitual_weekday",
    ]
