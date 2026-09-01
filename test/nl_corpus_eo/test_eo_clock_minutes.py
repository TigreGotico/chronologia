"""The Esperanto spoken clock's minute count -- "dek kvin minutoj", not just
the fraction words "duono"/"kvarono" test_eo_clock.py already covers.

PMEG, *Horoj* (https://bertilow.com/pmeg/gramatiko/nombroj/horoj.html)
parenthesises every optional element of the construction: "Estas la tria
(horo) (kaj) dek kvin (minutoj)." and "Estas dek kvin (minutoj) post la
tria (horo)." are one and the same 3:15, and "Estas la naŭa (horo) (kaj)
kvardek kvin (minutoj)." / "Estas dek kvin (minutoj) antaŭ la deka (horo)."
are one and the same 9:45.  "kaj"/"post" count the minutes FORWARD from the
hour they name, exactly like the half/quarter fractions in
test_eo_clock.py; "antaŭ" counts them BACK from the hour it names.

Before this file's fix, the grammar had no MINUTE slot at all: a spelled
minute count parsed as far as the bare hour, then silently stranded "kaj
dek kvin minutoj" (or the post/antaŭ phrase) in the remainder -- a
confident WRONG time (the bare hour) rather than a refusal or the correct
minute.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, nomatch, parse, remainder, start


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return cand


@pytest.mark.parametrize("text,h,mi", [
    ("la sesa kaj dek kvin minutoj", 6, 15),
    ("la sesa kaj tridek minutoj", 6, 30),
    ("la tria kaj dek kvin", 3, 15),
    ("la naŭa kaj kvardek kvin", 9, 45),
    ("la tria dek kvin", 3, 15),
    ("dek kvin minutoj post la tria", 3, 15),
    ("dek kvin minutoj antaŭ la deka", 9, 45),
])
def test_minute_counts_resolve_to_the_exact_minute(text, h, mi):
    got = start(text)
    assert (got.hour, got.minute) == (h, mi)
    assert got == _next_time(h, mi)
    assert remainder(text) == ""


def test_kaj_dek_kvin_minutoj_is_not_the_bare_hour():
    """The exact defect: a leaked partial parse used to hand back 6:00 with
    "kaj dek kvin minutoj" stranded in the remainder."""
    got = start("la sesa kaj dek kvin minutoj")
    assert (got.hour, got.minute) != (6, 0)
    assert (got.hour, got.minute) == (6, 15)


def test_la_tria_kaj_dek_kvin_is_not_the_bare_hour():
    """The exact defect quoted in the brief: this must resolve to 3:15, not
    the bare 3:00 the leaked partial parse used to return."""
    got = start("la tria kaj dek kvin")
    assert (got.hour, got.minute) != (3, 0)
    assert (got.hour, got.minute) == (3, 15)


def test_a_bare_minute_count_with_no_hour_does_not_resolve():
    nomatch("dek kvin minutoj")
    nomatch("dek kvin")


@pytest.mark.parametrize("text,h,mi", [
    ("la sesa kaj duono", 6, 30),
    ("duono antaŭ la sepa", 6, 30),
    ("duono post la sepa", 7, 30),
])
def test_the_half_hour_is_undisturbed(text, h, mi):
    """PMEG rules "duono de la naŭa" bad and "duono antaŭ/post la naŭa"
    good -- these must keep resolving exactly as before, with nothing left
    over in the remainder."""
    got = start(text)
    assert (got.hour, got.minute) == (h, mi)
    assert remainder(text) == ""
