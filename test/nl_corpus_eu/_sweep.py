# -*- coding: utf-8 -*-
"""Shared construction tables for the Basque oracle sweeps.

The month surfaces and their genitive (-aren) stems are the canonical CLDR eu
month names.  The genitive is the stem (month minus final -a) plus -aren:
``martxoa`` -> ``martxo`` -> ``martxoaren``.  These tables build *idiomatic*
Basque surface strings; every expected value is derived by independent
``datetime`` arithmetic in the test module, never from the parser.
"""

#: absolutive month names (CLDR eu)
MONTH_ABS = {
    1: "urtarrila", 2: "otsaila", 3: "martxoa", 4: "apirila",
    5: "maiatza", 6: "ekaina", 7: "uztaila", 8: "abuztua",
    9: "iraila", 10: "urria", 11: "azaroa", 12: "abendua",
}

#: genitive month forms: stem (drop final -a) + -aren
MONTH_GEN = {m: name[:-1] + "aren" for m, name in MONTH_ABS.items()}

#: -ak absolutive-plural surface used in the colloquial "martxoak 5" idiom
MONTH_AK = {m: name[:-1] + "ak" for m, name in MONTH_ABS.items()}
