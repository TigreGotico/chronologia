"""A bare month keeps its leading "in/during" marker out of the remainder.

"in January" parsed the right span but left "in" unconsumed: no locale's
``calendar_date`` order let a marker precede a bare MONTH, so the marker fell
out of the match.  The base grammar now carries one marker-prefixed order
("during MONTH DAY? YEAR?") and each locale supplies the locative preposition
in ``marker_during.voc``.

The span never moves -- every phrase below is asserted equal to the bare-month
reading of the same month, and to January of the anchor year, derived by hand.
The controls pin the ways a locale must NOT gain the reading: a marker that
means the future offset "in N units" ("через", "za", "pärast") stays out of the
month frame, a locale whose during-word is a postposition ("jooksul", "aikana",
"alatt", "zehar") keeps refusing the prefixed word order, and the Scandinavian
"jul" keeps its Christmas reading.

Anchor 2026-08-14 10:00.
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate
from chronologia.extract import extract_timespan

_REF = datetime(2026, 8, 14, 10, 0)

#: locale -> ("<marker> <january>", "<january>")
_IN_MONTH = {
    "an": ("en chinero", "chinero"),
    "ar": ("في يناير", "يناير"),
    "ast": ("durante xineru", "xineru"),
    "ca": ("al gener", "gener"),
    "cs": ("v lednu", "lednu"),
    "de": ("im Januar", "Januar"),
    "en": ("in January", "January"),
    "es": ("en enero", "enero"),
    "fa": ("در ژانویه", "ژانویه"),
    "fr": ("en janvier", "janvier"),
    "fy": ("yn jannewaris", "jannewaris"),
    "hr": ("u siječnju", "siječnju"),
    "is": ("í janúar", "janúar"),
    "it": ("in gennaio", "gennaio"),
    "nl": ("in januari", "januari"),
    "oc": ("en genièr", "genièr"),
    "pl": ("w styczniu", "styczniu"),
    "ro": ("în ianuarie", "ianuarie"),
    "ru": ("в январе", "январе"),
    "sk": ("v januári", "januári"),
    "sl": ("v januarju", "januarju"),
    "uk": ("у січні", "січні"),
}

#: locale -> (phrase, the marker that must stay in the remainder).  Either the
#: word is the future-offset "in N units" marker, which never opens a month
#: frame, or it is a postposition that cannot precede its noun.
_STRANDED = {
    "cs": ("za leden", "za"),
    "et": ("jooksul jaanuar", "jooksul"),
    "eu": ("zehar urtarrila", "zehar"),
    "fi": ("aikana tammikuu", "aikana"),
    "hu": ("alatt január", "alatt"),
    "pl": ("za styczeń", "za"),
    "ru": ("через январь", "через"),
    "sl": ("čez januar", "čez"),
    "uk": ("через січень", "через"),
}


@pytest.mark.parametrize("lang,phrase,bare",
                         [(l, p, b) for l, (p, b) in sorted(_IN_MONTH.items())])
def test_marker_is_consumed(lang, phrase, bare):
    marked = extract_timespan(phrase, lang, _REF)
    assert marked is not None, f"{lang}: {phrase!r} did not parse"
    assert marked.remainder == ""
    assert marked[0].start == AstroDate(2026, 1, 1)
    assert marked[0].end == AstroDate(2026, 2, 1)
    plain = extract_timespan(bare, lang, _REF)
    assert (marked[0].start, marked[0].end) == (plain[0].start, plain[0].end)


@pytest.mark.parametrize("lang,phrase,marker",
                         [(l, p, m) for l, (p, m) in sorted(_STRANDED.items())])
def test_offset_and_postposed_markers_stay_out(lang, phrase, marker):
    r = extract_timespan(phrase, lang, _REF)
    assert r is not None
    assert r.remainder == marker
    assert r[0].start == AstroDate(2026, 1, 1)


@pytest.mark.parametrize("lang,phrase", [("da", "i jul"), ("da", "under jul"),
                                         ("nb", "i jul"), ("nn", "i jul"),
                                         ("sv", "i jul"), ("sv", "under jul")])
def test_scandinavian_jul_stays_christmas(lang, phrase):
    # "jul" is both Christmas and the July abbreviation these locales ship in
    # month_7.voc.  They therefore opt out of the marker-prefixed month order:
    # with it, "i jul" would parse as the month and silently displace the
    # holiday.
    r = extract_timespan(phrase, lang, _REF)
    assert (r[0].start, r[0].end) == (AstroDate(2026, 12, 25),
                                      AstroDate(2026, 12, 26))


def test_after_marker_still_refuses_a_month():
    # Estonian "pärast" is "after": an open-ended "after January" span has no
    # DateSpan representation and must keep refusing.
    assert extract_timespan("pärast jaanuar", "et", _REF) is None
