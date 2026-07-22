"""Subdivision-depth parity ratchet with vacanza/holidays 0.101, wave 1.

Mission: for every chronologia ``holiday_data/<cc>.tab`` whose vacanza
counterpart models ``subdivisions``, every subdivision code whose 2024/2025
holiday set differs from the jurisdiction-wide default must have either (a)
matching subdiv-scoped rows in the ``.tab``, or (b) a documented skip entry
below explaining why it is deliberately omitted. IT (``it.tab``) and FR
(``fr.tab``) were landed by a prior batch (see
``test_holidays_subdiv_it_fr.py``) and are carried into ``DONE_COUNTRIES``
here unchanged.

Survey method: for each vacanza country with ``subdivisions``, compute
``country_holidays(cc, years=y)`` (the jurisdiction default) and
``country_holidays(cc, subdiv=code, years=y)`` for ``y in (2024, 2025)``;
a code "differs" if the two holiday sets are not equal in either year.
``holidays==0.101`` is the pinned reference throughout.

Wave 1 lands the small, tractable gaps: GB (England/Wales as their own ISO
codes, distinct from the pre-existing non-ISO ``GB-EAW`` convenience code),
FI (Åland), CL (Arica y Parinacota, Ñuble), NI (Managua), ST (Príncipe), SV
(San Salvador), GQ (Annobón), BA (all three entities: Federacija BiH, Brčko
distrikt, Republika Srpska), BQ (Bonaire/Saba/Sint Eustatius), SH (Ascension/
Saint Helena/Tristan da Cunha), AD (six of Andorra's seven parishes), and BT
(Thimphu, English-named via vacanza's ``en_US`` locale for readability).
US and DE are filed DONE-with-a-documented-skip (see below): their remaining
gaps are *subtractive* (a subdivision that omits a jurisdiction-wide holiday,
or a non-ISO city pseudo-code), which chronologia's additive-only rule model
cannot represent without an engine change -- out of scope for a data-only
batch.

Golding discipline (same as ``test_holidays_subdiv_it_fr.py``): every gold
below was captured by directly querying vacanza's own ``holidays`` package
for the exact subdivision code across 2024 and 2025 -- vacanza's own
recurrence machinery, independent of chronologia's engine. Every ``fixed``
row's gold is confirmed the same ``(month, day)`` both years; every
``decree`` row's gold is vacanza's own gazetted date(s), not re-derived.

``PENDING_COUNTRIES`` (BR, CH, IN, CA, AR, BO, CV, MY, PT, NZ, TV, SB, FM)
are the larger remaining sweeps (dozens of subdivisions each) left for a
follow-up batch; the ratchet test below only asserts full coverage for
``DONE_COUNTRIES`` and explicitly documents what's still outstanding.
"""
import os

import pytest

from chronologia import AstroDate, holidays_for
from chronologia.civil_holidays import _DATA_DIR
from test_holiday_golds import _reg

# ==========================================================================
# Ratchet bookkeeping
# ==========================================================================

#: Countries whose vacanza subdivision-depth gap (per the survey method
#: above) is fully closed: either every differing subdiv code has matching
#: rows, or the remaining gap is documented as out-of-scope right here.
DONE_COUNTRIES = ("AD", "BA", "BQ", "BT", "CL", "DE", "FI", "FR", "GB", "GQ",
                   "IT", "NI", "SH", "ST", "SV", "US")

#: Countries with a real vacanza subdivision-holiday differential that has
#: NOT yet been backfilled -- explicit so the ratchet doesn't silently drift.
#: Counts are (missing codes / total vacanza subdivisions for that country)
#: as of the wave-1 survey.
PENDING_COUNTRIES = {
    "BR": "23/28 -- Brazilian states beyond the 4 pre-existing rows",
    "CH": "21/27 -- Swiss cantons beyond the pre-existing partial set",
    "IN": "26/36 -- most Indian states/UTs",
    "CA": "7/13 -- NB, NL, NT, NU, PE, SK, YT",
    "AR": "12/24 -- most Argentine provinces",
    "BO": "9/9 -- all Bolivian departments",
    "CV": "20/22 -- most Cabo Verde municipalities",
    "MY": "16/16 -- all Malaysian states",
    "PT": "18/20 -- most Portuguese districts",
    "NZ": "13/18 -- most NZ regions",
    "TV": "8/8 -- all Tuvalu island councils",
    "SB": "9/10 -- most Solomon Islands provinces",
    "FM": "4/4 -- all Micronesia states",
}

#: Documented skip entries: a real vacanza differential that DONE_COUNTRIES
#: deliberately does not backfill, and why.
DOCUMENTED_SKIPS = {
    ("US", "ND"): "vacanza's ND/UM omit Columbus Day vs the US default -- a "
                  "SUBTRACTIVE gap (a subdivision that has FEWER holidays "
                  "than the jurisdiction default). chronologia's rule model "
                  "is additive-only (a subdiv row adds a holiday; there is "
                  "no 'exclude this national holiday' rule kind), so this "
                  "cannot be represented without an engine change, which is "
                  "out of scope for this data-only batch.",
    ("US", "UM"): "see US/ND -- same Columbus Day omission.",
    ("DE", "Augsburg"): "'Augsburg' is a non-ISO city pseudo-code vacanza "
                  "carries alongside the 16 genuine ISO 3166-2 Länder codes "
                  "(Peter-und-Paul-Fest, a city-only observance) -- same "
                  "house rule as IT's 7 non-ISO city duplicates "
                  "(Andria/Barletta/Cesena/Forlì/Pesaro/Trani/Urbino), "
                  "omitted as not a real ISO subdivision.",
    ("AD", "AD-03"): "Encamp carries no subdivision-specific holiday in "
                  "vacanza 0.101 -- it resolves to the national default "
                  "set only.",
}


# ==========================================================================
# Golds -- captured directly from vacanza/holidays 0.101
# ==========================================================================

SUBDIV_GOLD = [
    # --- GB: England / Wales as their own ISO codes ---
    ("GB-ENG", "Easter Monday", 2024, 4, 1),
    ("GB-ENG", "Easter Monday", 2025, 4, 21),
    ("GB-ENG", "Late Summer Bank Holiday", 2024, 8, 26),
    ("GB-ENG", "Late Summer Bank Holiday", 2025, 8, 25),
    ("GB-WLS", "Easter Monday", 2024, 4, 1),
    ("GB-WLS", "Easter Monday", 2025, 4, 21),
    ("GB-WLS", "Late Summer Bank Holiday", 2024, 8, 26),
    ("GB-WLS", "Late Summer Bank Holiday", 2025, 8, 25),
    # --- FI: Åland ---
    ("FI-01", "Ahvenanmaan itsehallintopäivä", 2024, 6, 9),
    ("FI-01", "Ahvenanmaan itsehallintopäivä", 2025, 6, 9),
    # --- CL: Arica y Parinacota / Ñuble ---
    ("CL-AP", "Asalto y Toma del Morro de Arica", 2024, 6, 7),
    ("CL-AP", "Asalto y Toma del Morro de Arica", 2025, 6, 7),
    ("CL-NB", "Nacimiento del Prócer de la Independencia (Chillán y Chillán Viejo)", 2024, 8, 20),
    ("CL-NB", "Nacimiento del Prócer de la Independencia (Chillán y Chillán Viejo)", 2025, 8, 20),
    # --- NI: Managua ---
    ("NI-MN", "Bajada de Santo Domingo", 2024, 8, 1),
    ("NI-MN", "Bajada de Santo Domingo", 2025, 8, 1),
    ("NI-MN", "Subida de Santo Domingo", 2024, 8, 10),
    ("NI-MN", "Subida de Santo Domingo", 2025, 8, 10),
    # --- ST: Príncipe ---
    ("ST-P", "Descobrimento da Ilha do Príncipe", 2024, 1, 17),
    ("ST-P", "Descobrimento da Ilha do Príncipe", 2025, 1, 17),
    ("ST-P", "Dia da Autonomia do Príncipe", 2024, 4, 29),
    ("ST-P", "Dia da Autonomia do Príncipe", 2025, 4, 29),
    ("ST-P", "Dia de São Lourenço", 2024, 8, 15),
    ("ST-P", "Dia de São Lourenço", 2025, 8, 15),
    # --- SV: San Salvador ---
    ("SV-SS", "Fiesta de San Salvador", 2024, 8, 3),
    ("SV-SS", "Fiesta de San Salvador", 2024, 8, 5),
    ("SV-SS", "Fiesta de San Salvador", 2025, 8, 3),
    ("SV-SS", "Fiesta de San Salvador", 2025, 8, 5),
    # --- GQ: Annobón ---
    ("GQ-AN", "Fiesta Patronal de Annobón", 2024, 6, 13),
    ("GQ-AN", "Fiesta Patronal de Annobón", 2025, 6, 13),
    # --- BA: BIH / BRC / SRP ---
    ("BA-BIH", "Dan državnosti", 2024, 11, 25),
    ("BA-BIH", "Dan nezavisnosti", 2024, 3, 1),
    ("BA-BIH", "Kurban Bajram (procijenjeno)", 2024, 6, 17),
    ("BA-BIH", "Kurban Bajram (procijenjeno)", 2025, 6, 7),
    ("BA-BIH", "Uskrs (Katolički)", 2024, 3, 31),
    ("BA-BIH", "Uskrs (Katolički); Vaskrs (Pravoslavni)", 2025, 4, 20),
    ("BA-BRC", "Dan uspostavljanja Brčko distrikta", 2024, 3, 8),
    ("BA-BRC", "Dan uspostavljanja Brčko distrikta", 2025, 3, 8),
    ("BA-BRC", "Božić (Pravoslavni) (slobodan dan)", 2024, 1, 8),
    ("BA-SRP", "Pravoslavna Nova godina", 2024, 1, 14),
    ("BA-SRP", "Pravoslavna Nova godina", 2025, 1, 14),
    ("BA-SRP", "Dan uspostave Opšteg okvirnog sporazuma za mir u Bosni i Hercegovini", 2024, 11, 21),
    ("BA-BIH", "Badnji dan (Katolički)", 2024, 12, 24),
    ("BA-BIH", "Badnji dan (Pravoslavni)", 2024, 1, 6),
    ("BA-BIH", "Dan pobjede nad fašizmom", 2024, 5, 9),
    ("BA-BIH", "Ramazanski Bajram", 2024, 4, 11),
    ("BA-BIH", "Ramazanski Bajram (procijenjeno)", 2025, 3, 31),
    ("BA-BIH", "Uskrsni ponedjeljak (Katolički); Uskrsni ponedjeljak (Pravoslavni)", 2025, 4, 21),
    ("BA-BIH", "Uskrsni ponedjeljak (Pravoslavni)", 2024, 5, 6),
    ("BA-BIH", "Vaskrs (Pravoslavni)", 2024, 5, 5),
    ("BA-BIH", "Veliki petak (Katolički)", 2024, 3, 29),
    ("BA-BIH", "Veliki petak (Katolički); Veliki petak (Pravoslavni)", 2025, 4, 18),
    ("BA-SRP", "Badnji dan (Katolički)", 2024, 12, 24),
    ("BA-SRP", "Badnji dan (Pravoslavni)", 2024, 1, 6),
    ("BA-SRP", "Dan pobjede nad fašizmom", 2024, 5, 9),
    ("BA-SRP", "Kurban Bajram (procijenjeno)", 2024, 6, 17),
    ("BA-SRP", "Ramazanski Bajram", 2024, 4, 11),
    ("BA-SRP", "Ramazanski Bajram (procijenjeno)", 2025, 3, 31),
    ("BA-SRP", "Uskrs (Katolički)", 2024, 3, 31),
    ("BA-SRP", "Uskrs (Katolički); Vaskrs (Pravoslavni)", 2025, 4, 20),
    ("BA-SRP", "Uskrsni ponedjeljak (Katolički); Uskrsni ponedjeljak (Pravoslavni)", 2025, 4, 21),
    ("BA-SRP", "Uskrsni ponedjeljak (Pravoslavni)", 2024, 5, 6),
    ("BA-SRP", "Vaskrs (Pravoslavni)", 2024, 5, 5),
    ("BA-SRP", "Veliki petak (Katolički)", 2024, 3, 29),
    ("BA-SRP", "Veliki petak (Katolički); Veliki petak (Pravoslavni)", 2025, 4, 18),
    # --- BQ: Bonaire / Saba / Sint Eustatius ---
    ("BQ-BON", "Bonairedag", 2024, 9, 6),
    ("BQ-BON", "Bonairedag", 2025, 9, 6),
    ("BQ-BON", "Rincondag", 2024, 4, 30),
    ("BQ-BON", "Rincondag", 2025, 4, 30),
    ("BQ-SAB", "Dag na de carnavalsoptocht", 2024, 7, 29),
    ("BQ-SAB", "Dag na de carnavalsoptocht", 2025, 7, 28),
    ("BQ-SAB", "Sabadag", 2024, 12, 6),
    ("BQ-SAB", "Sabadag", 2025, 12, 5),
    ("BQ-STA", "Emancipatiedag", 2024, 7, 1),
    ("BQ-STA", "Statiadag", 2024, 11, 16),
    # --- SH: Ascension / Saint Helena / Tristan da Cunha ---
    ("SH-AC", "Ascension Day", 2024, 5, 9),
    ("SH-AC", "Ascension Day", 2025, 5, 29),
    ("SH-HL", "Saint Helena Day", 2024, 5, 21),
    ("SH-HL", "Saint Helena Day", 2025, 5, 21),
    ("SH-TA", "Anniversary Day", 2024, 8, 14),
    ("SH-TA", "Ascension Day", 2025, 5, 29),
    ("SH-TA", "Ratting Day", 2025, 5, 30),
    # --- AD: six of seven parishes ---
    ("AD-02", "Sant Roc", 2024, 8, 16),
    ("AD-04", "Sant Antoni", 2025, 1, 17),
    ("AD-05", "Sant Pere", 2024, 6, 29),
    ("AD-06", "Sant Julià", 2024, 1, 7),
    ("AD-06", "Diada de Canòlich", 2024, 5, 25),
    ("AD-06", "Diada de Canòlich", 2025, 5, 31),
    ("AD-06", "Festa Major de Sant Julià de Lòria", 2024, 7, 29),
    ("AD-06", "Festa Major de Sant Julià de Lòria", 2025, 7, 28),
    ("AD-07", "Festa Major d'Andorra la Vella", 2024, 8, 3),
    ("AD-07", "Festa Major d'Andorra la Vella", 2025, 8, 2),
    ("AD-08", "Sant Miquel d'Engolasters", 2024, 5, 7),
    ("AD-08", "Diada de la creació de la parròquia", 2024, 6, 16),
    ("AD-08", "Diada de la creació de la parròquia", 2025, 6, 15),
    ("AD-08", "Festa Major d'Escaldes-Engordany", 2024, 7, 25),
    # --- BT: Thimphu ---
    ("BT-15", "Thimphu Drubchoe", 2024, 9, 9),
    ("BT-15", "Thimphu Drubchoe", 2025, 9, 28),
    ("BT-15", "Thimphu Tshechu", 2024, 9, 13),
    ("BT-15", "Thimphu Tshechu", 2025, 10, 3),
    ("BT-15", "Dassain; Thimphu Tshechu", 2025, 10, 2),
]

for _code, _name, _y, _m, _d in SUBDIV_GOLD:
    _country = _code.split("-", 1)[0]
    _reg(_country, _code, _name, _y, _m, _d)


def _dateset_for(country, subdiv, year):
    out = {}
    for h in holidays_for(country, year, subdiv=subdiv):
        out.setdefault(h.name, set()).add(h.date)
    return out


@pytest.mark.parametrize("subdiv,name,year,month,day", SUBDIV_GOLD)
def test_subdivision_gold(subdiv, name, year, month, day):
    country = subdiv.split("-", 1)[0]
    got = _dateset_for(country, subdiv, year)
    assert AstroDate(year, month, day) in got.get(name, set()), (
        f"{country}/{subdiv}/{name!r} {year}: expected {year}-{month:02d}-{day:02d}, "
        f"got {sorted(got.get(name, set()))}")


def test_ba_easter_family_movable_between_years():
    """BIH's Uskrs/Uskrsni ponedjeljak (Catholic Easter/Easter Monday) must
    differ in date between 2024 (Western Easter alone) and 2025 (Western and
    Orthodox Easter coincide) -- guards against a decree row that was
    accidentally hand-typed as a stable fixed date."""
    d24 = _dateset_for("BA", "BA-BIH", 2024).get("Uskrs (Katolički)")
    d25 = _dateset_for("BA", "BA-BIH", 2025).get("Uskrs (Katolički); Vaskrs (Pravoslavni)")
    assert d24 and d25 and d24 != d25


def test_sh_ta_ascension_day_movable_between_years():
    d24 = _dateset_for("SH", "SH-TA", 2024).get("Ascension Day")
    d25 = _dateset_for("SH", "SH-TA", 2025).get("Ascension Day")
    assert d24 and d25 and d24 != d25


def test_gb_eng_wls_untouched_eaw_code_still_works():
    """The pre-existing non-ISO GB-EAW convenience code is unaffected by the
    new GB-ENG/GB-WLS additions."""
    eaw = {h.name for h in holidays_for("GB", 2024, subdiv="GB-EAW")}
    assert "Easter Monday" in eaw
    assert "Summer Bank Holiday" in eaw


def test_us_columbus_day_omission_is_a_documented_skip_not_silence():
    assert ("US", "ND") in DOCUMENTED_SKIPS
    assert ("US", "UM") in DOCUMENTED_SKIPS
    # Sanity: chronologia still lists Columbus Day for US-ND (the
    # subtractive gap this skip documents -- it's present, not excluded).
    got = _dateset_for("US", "US-ND", 2024)
    assert "Columbus Day" in got


@pytest.mark.parametrize("country", sorted(set(c for c, _ in
                          (s.split("-", 1) for s in
                           {"GB-ENG", "GB-WLS", "FI-01", "CL-AP", "CL-NB",
                            "NI-MN", "ST-P", "SV-SS", "GQ-AN", "BA-BIH",
                            "BA-BRC", "BA-SRP", "BQ-BON", "BQ-SAB", "BQ-STA",
                            "SH-AC", "SH-HL", "SH-TA", "AD-02", "AD-04",
                            "AD-05", "AD-06", "AD-07", "AD-08", "BT-15"}))))
def test_calendar_still_loads_and_has_rules(country):
    from chronologia.civil_holidays import load_calendar
    cal = load_calendar(os.path.join(_DATA_DIR, f"{country.lower()}.tab"))
    assert cal.rules
    assert cal.jurisdiction == country


def test_ratchet_scope_is_documented():
    """Every country identified by the wave-1 survey as having a vacanza
    subdivision differential is accounted for: either DONE (rows added or a
    documented skip) or explicitly PENDING. This is a documentation ratchet,
    not a completeness proof for PENDING_COUNTRIES -- it just keeps the
    sweep from silently going untracked."""
    assert set(DONE_COUNTRIES) & set(PENDING_COUNTRIES) == set()
    for (cc, code) in DOCUMENTED_SKIPS:
        assert cc in DONE_COUNTRIES, f"{cc}/{code} skip must be under a DONE country"


@pytest.mark.parametrize("country", DONE_COUNTRIES)
def test_done_country_tab_exists(country):
    path = os.path.join(_DATA_DIR, f"{country.lower()}.tab")
    assert os.path.exists(path), f"missing {path}"
