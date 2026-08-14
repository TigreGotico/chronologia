# -*- coding: utf-8 -*-
"""R166: German ASCII-umlaut fallback for "nächst-" (next) was inconsistent.

``marker_next.voc`` shipped umlaut "nächster"/"nächstes" without their ASCII
twins "naechster"/"naechstes", while "nächste"/"nächsten" did have theirs
("naechste"/"naechsten"). "naechstes quartal"/"naechstes jahr" therefore
refused to parse, and "naechster sommer" silently mis-bound (the marker
stranded as remainder, so the season read as the CURRENT year's, not next
year's). Gold: every ASCII spelling must resolve to the SAME span as its
umlaut twin.
"""
from ._corpus import ANCHOR, start_end  # noqa: F401


def test_naechstes_quartal_matches_umlaut_twin():
    assert start_end("naechstes quartal") == start_end("nächstes quartal")


def test_naechstes_jahr_matches_umlaut_twin():
    assert start_end("naechstes jahr") == start_end("nächstes jahr")


def test_naechster_sommer_matches_umlaut_twin():
    assert start_end("naechster sommer") == start_end("nächster sommer")


def test_control_naechsten_monat_still_works():
    assert start_end("naechsten monat") == start_end("nächsten monat")


def test_control_naechste_woche_still_works():
    assert start_end("naechste woche") == start_end("nächste woche")
