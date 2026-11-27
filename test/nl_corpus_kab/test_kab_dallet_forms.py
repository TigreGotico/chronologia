# -*- coding: utf-8 -*-
"""Kabyle forms that Dallet 1982, Dictionnaire kabyle-français, prints.

Anchor Tuesday 2017-06-27 13:04.  Gold is calendar arithmetic from the
anchor with ``timedelta``.
"""
from datetime import timedelta

import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, LANG

MIDNIGHT = ANCHOR.replace(hour=0, minute=0)
NEXT_MONDAY = MIDNIGHT + timedelta(days=(0 - ANCHOR.weekday()) % 7 or 7)


def _parse(text):
    r = extract_timespan(text, LANG, ANCHOR)
    assert r is not None, f"{text!r} did not parse"
    return r.span.start.datetime(), r.remainder


@pytest.mark.parametrize("text,expected,remainder", [
    # p. 939: "seld azekka, après-demain."
    ("seld azekka", MIDNIGHT + timedelta(days=2), ""),
    # p. 938: "ḥebbṛ i wass-a, ḥebbṛ i uzekka" (annexed today, tomorrow)
    ("ḥebbṛ i uzekka", MIDNIGHT + timedelta(days=1), "ḥebbṛ i"),
    ("ḥebbṛ i wass-a", MIDNIGHT, "ḥebbṛ i"),
    # p. 162: "ddurt i ă-iteddun, la semaine prochaine (qui vient)";
    # the clause without the relative "i" after a weekday
    ("ssebt n ddurt d-iteddun", NEXT_MONDAY + timedelta(days=5), ""),
    ("lḥedd d-iteddun", MIDNIGHT + timedelta(days=5), ""),
    ("lexmis iteddun", MIDNIGHT + timedelta(days=2), ""),
    # p. 703: "ṛebɛa ... S'il est suivi d'un nom, celui-ci est à l'ann.",
    # "ṛebɛa warrac": one to ten take the annexed noun with no "n"
    ("deg ṛebɛa wussan", ANCHOR + timedelta(days=4), ""),
    ("deg sin wussan", ANCHOR + timedelta(days=2), ""),
    ("deg xemsa wussan, ɣef xemsa n tmeddit",
     MIDNIGHT + timedelta(days=5, hours=17), ""),
])
def test_dallet_form(text, expected, remainder):
    assert _parse(text) == (expected, remainder)
