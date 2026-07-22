"""File-backed holiday gold fixtures, walker, and provenance report.

Golds are frozen, independent values living in ``test/holiday_golds/<cc>.tab``
(one file per jurisdiction), NOT re-derived from the engine at test time and NOT
accumulated into a shared registry at import. Each record carries a **provenance
tier** (see ``docs/transparency.md``):

* ``primary``      -- restated from a cited primary source (statute/gazette).
* ``computed``     -- an independent in-test arithmetic derivation
                      (``easter()`` + offset, nth-weekday, a standalone Hijri or
                      Julian-day conversion). The derivation is preserved in the
                      per-country witness tests below.
* ``witnessed``    -- the vacanza/``holidays`` reference package's output. A
                      witnessed gold proves we *agree with an outside witness*,
                      not that either party is correct against the statute.
* ``self-evident`` -- the rule's own arguments (a ``fixed`` row's month/day, a
                      ``decree`` row's listed date). Tautological against the
                      ``.tab`` file, kept so every rule has a gold.

Order-freedom
-------------
``HOLIDAY_GOLDS`` is materialised ONCE from the data files at import, so it is
complete regardless of which other test modules were collected. The single
parameterised walker (:func:`test_gold`) and the structural enforcement test
(:func:`test_every_tab_rule_has_a_gold`) both read the same files, so running any
single gold file's subset is green on its own -- there is no import-order
coupling and no silent under-registration. ``_reg`` remains only as an
idempotent back-compat shim for legacy import sites.
"""
import csv
import json
import os
import re
from datetime import timedelta

import pytest

from chronologia import AstroDate, holidays_for, load_calendar
from chronologia.civil_holidays import _DATA_DIR
from chronologia.computus import easter
from chronologia.recurrence import nth_weekday_of_month, occurrences

_PAPERS = os.path.expanduser("~/AgentWorkspaces/papers/holidays")
GOLD_DIR = os.path.join(os.path.dirname(__file__), "holiday_golds")
_TIER_FLOOR = os.path.join(GOLD_DIR, "_tier_floor.json")
_TIERS = ("primary", "computed", "witnessed", "self-evident")


# ==========================================================================
# Load the frozen gold files.
# ==========================================================================
def _load_gold_records():
    """Every gold record as (country, subdiv, name, year, month, day, prov, src)."""
    recs = []
    for fn in sorted(os.listdir(GOLD_DIR)):
        if not fn.endswith(".tab"):
            continue
        cc = fn[:-4].upper()
        with open(os.path.join(GOLD_DIR, fn), encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("#") or not line.strip():
                    continue
                cols = line.rstrip("\n").split("|")
                subdiv, name, year, month, day, prov, src = cols
                recs.append((cc, subdiv or None, name,
                             int(year), int(month), int(day), prov, src))
    return recs


GOLD_RECORDS = _load_gold_records()

#: Legacy registry shape: (country, subdiv, name) -> {(year, month, day)}.
#: Materialised from the data files at import so it is always complete.
HOLIDAY_GOLDS: dict = {}
for _c, _s, _n, _y, _m, _d, _prov, _src in GOLD_RECORDS:
    HOLIDAY_GOLDS.setdefault((_c, _s, _n), set()).add((_y, _m, _d))


def _reg(country, subdiv, name, *ymd):
    """Back-compat shim for legacy import sites. Golds are frozen in
    ``test/holiday_golds/*.tab``; this only keeps old callers working and is
    idempotent against the already-loaded data."""
    HOLIDAY_GOLDS.setdefault((country, subdiv, name), set()).add(tuple(ymd))


def _dates_for(country, year, subdiv=None):
    return {(h.name, h.subdiv): h.date for h in holidays_for(country, year, subdiv)}


def _dateset_for(country, year, subdiv=None):
    """{(name, subdiv): {dates}} -- a set per rule, so a name that resolves to
    several dates in one year is not collapsed the way ``_dates_for`` would."""
    out = {}
    for h in holidays_for(country, year, subdiv=subdiv):
        out.setdefault((h.name, h.subdiv), set()).add(h.date)
    return out


def _have_tab(country):
    return os.path.exists(os.path.join(_DATA_DIR, f"{country.lower()}.tab"))


# ==========================================================================
# The single walker: every gold file record must reproduce against the engine.
# ==========================================================================
@pytest.mark.parametrize(
    "country,subdiv,name,year,month,day",
    [(c, s, n, y, m, d) for (c, s, n, y, m, d, _p, _src) in GOLD_RECORDS],
    ids=[f"{c}/{s}/{n}/{y}-{m:02d}-{d:02d}"
         for (c, s, n, y, m, d, _p, _src) in GOLD_RECORDS])
def test_gold(country, subdiv, name, year, month, day):
    # Compare at calendar-day granularity so a half-day span (whose start
    # carries an hour component, e.g. 12:00) still matches its (y, m, d) gold.
    days = {(x.year, x.month, x.day)
            for x in _dateset_for(country, year, subdiv=subdiv).get((name, subdiv), set())}
    assert (year, month, day) in days, (
        f"{country}/{subdiv}/{name!r} {year}: expected "
        f"{year}-{month:02d}-{day:02d}, got {sorted(days)}")


# ==========================================================================
# Structural enforcement: every rule in every holiday_data/*.tab needs a gold.
# ==========================================================================
def _every_tab_rule_key():
    """(country, subdiv, name) for every rule row in every shipped .tab file."""
    keys = []
    for fn in sorted(os.listdir(_DATA_DIR)):
        if not fn.endswith(".tab"):
            continue
        cal = load_calendar(os.path.join(_DATA_DIR, fn))
        for rule in cal.rules:
            # Exclude rules are subtractive: they remove an inherited holiday
            # and produce no date to gold. Their effect (the named holiday is
            # absent in the scoped subdivision, present nationally) is asserted
            # by test_holidays_horizon_exclusion, not by a date gold here.
            if type(getattr(rule, "kind", None)).__name__ == "ExcludeRule":
                continue
            keys.append((cal.jurisdiction.upper(), rule.subdiv, rule.name))
    return keys


_GOLD_KEYS = {(c, s, n) for (c, s, n, _y, _m, _d, _p, _src) in GOLD_RECORDS}


@pytest.mark.parametrize("country,subdiv,name", _every_tab_rule_key())
def test_every_tab_rule_has_a_gold(country, subdiv, name):
    """Every shipped rule has at least one frozen gold in test/holiday_golds/.
    Reads the same files the walker does, so it is order-free."""
    assert (country, subdiv, name) in _GOLD_KEYS, (
        f"no gold registered for {country}/{subdiv}/{name!r}; "
        f"add one to test/holiday_golds/{country.lower()}.tab")


# ==========================================================================
# R5: provenance-tier coverage report + ratchet against a frozen floor.
# ==========================================================================
def _tier_counts():
    counts = {}
    for (c, _s, _n, _y, _m, _d, prov, _src) in GOLD_RECORDS:
        counts.setdefault(c, {}).setdefault(prov, 0)
        counts[c][prov] += 1
    return counts


def test_provenance_tier_report(capsys):
    """Prints the per-jurisdiction per-tier coverage table and asserts the
    aggregate is internally consistent (every record carries a known tier)."""
    counts = _tier_counts()
    agg = {t: 0 for t in _TIERS}
    lines = ["", f"{'jur':<6} " + " ".join(f"{t:>12}" for t in _TIERS) + "   total"]
    for cc in sorted(counts):
        row = counts[cc]
        assert set(row) <= set(_TIERS), f"{cc}: unknown tier {set(row) - set(_TIERS)}"
        for t in _TIERS:
            agg[t] += row.get(t, 0)
        lines.append(f"{cc:<6} " + " ".join(f"{row.get(t, 0):>12}" for t in _TIERS)
                     + f"   {sum(row.values()):>5}")
    lines.append(f"{'ALL':<6} " + " ".join(f"{agg[t]:>12}" for t in _TIERS)
                 + f"   {sum(agg.values()):>5}")
    print("\n".join(lines))
    assert sum(agg.values()) == len(GOLD_RECORDS)


def test_provenance_ratchet_never_shrinks():
    """Per-jurisdiction per-tier counts never silently drop below the frozen
    floor (``test/holiday_golds/_tier_floor.json``). Lowering a count is a
    deliberate act: update the floor in the same commit."""
    floor = json.load(open(_TIER_FLOOR, encoding="utf-8"))
    cur = _tier_counts()
    for cc, tiers in floor.items():
        for tier, n in tiers.items():
            have = cur.get(cc, {}).get(tier, 0)
            assert have >= n, (
                f"{cc} tier {tier!r} shrank: floor {n}, now {have}. "
                f"If intentional, update {_TIER_FLOOR}.")


def test_gold_total_not_below_floor():
    floor = json.load(open(_TIER_FLOOR, encoding="utf-8"))
    floor_total = sum(sum(v.values()) for v in floor.values())
    assert len(GOLD_RECORDS) >= floor_total


# ==========================================================================
# Independent-witness tests (the derivations behind the ``computed`` /
# ``primary`` tiers, and the year-gating behaviours). These prove the golds
# rather than merely re-reading them.
# ==========================================================================
# --- US federal / state ---
def _us_subdiv_rules():
    """(subdiv_code, name) for every subdivision rule row in us.tab."""
    cal = load_calendar(os.path.join(_DATA_DIR, "us.tab"))
    return [(r.subdiv, r.name) for r in cal.rules if r.subdiv is not None]


def test_us_juneteenth_year_gated_federal_from_2021():
    """Juneteenth National Independence Day Act signed 17 Jun 2021 -- the federal
    holiday is absent in 2020 and present from 2021 (us.tab "2021-" range)."""
    name = "Juneteenth National Independence Day"
    assert name not in _dates_for("US", 2020)
    assert _dates_for("US", 2021)[(name, None)] == AstroDate(2021, 6, 18)  # Sat->Fri
    assert _dates_for("US", 2022)[(name, None)] == AstroDate(2022, 6, 20)  # Sun->Mon


@pytest.mark.parametrize("subdiv,name", _us_subdiv_rules())
def test_us_state_rule_reproduces_reference(subdiv, name):
    """Every us.tab subdivision rule resolves to the gold date(s) frozen from the
    independent reference (vacanza/holidays)."""
    want = HOLIDAY_GOLDS[("US", subdiv, name)]
    for (y, m, d) in want:
        days = {(x.year, x.month, x.day)
                for x in _dateset_for("US", y, subdiv=subdiv).get((name, subdiv), set())}
        assert (y, m, d) in days, (
            f"US/{subdiv}/{name!r} {y}: expected {y}-{m:02d}-{d:02d}, got {sorted(days)}")


def test_us_half_day_spans_are_twelve_hours():
    """The two half-day holidays resolve to a genuine [12:00, 24:00) afternoon
    span, not a full day -- the span-native width payoff."""
    pr = [h for h in holidays_for("US", 2024, subdiv="US-PR")
          if h.name == "Christmas Eve (from 12pm)"]
    assert len(pr) == 1
    assert pr[0].span.start == AstroDate(2024, 12, 24, 12)
    assert pr[0].span.end == AstroDate(2024, 12, 25)
    assert pr[0].span.width == timedelta(hours=12)
    assert not pr[0].span.contains(AstroDate(2024, 12, 24, 9))
    assert pr[0].span.contains(AstroDate(2024, 12, 24, 15))
    fed = [h for h in holidays_for("US", 2015)
           if h.name == "Christmas Eve (half-day closing)"]
    assert len(fed) == 1 and fed[0].span.width == timedelta(hours=12)
    assert not [h for h in holidays_for("US", 2016)
                if h.name == "Christmas Eve (half-day closing)"]


def test_us_pr_christmas_eve_half_day_year_gated_from_2003():
    """PR Christmas Eve half-day (Law 305 of 25 Dec 2002) is absent in 2002 and
    present from 2003 (us.tab "2003-" range)."""
    names = lambda y: {h.name for h in holidays_for("US", y, subdiv="US-PR")}
    assert "Christmas Eve (from 12pm)" not in names(2002)
    assert "Christmas Eve (from 12pm)" in names(2003)


# --- LATAM gating ---
@pytest.mark.skipif(not _have_tab("MX"), reason="mx.tab not present")
def test_mx_monday_moving_matches_reference():
    """Mexico's art.74 Monday-moving civil holidays resolve to the statutory
    Monday (nominal 2-5 / 3-21 / 11-20 never emitted)."""
    d = {h.name: h.date for h in holidays_for("MX", 2024)}
    assert d["Día de la Constitución"] == AstroDate(2024, 2, 5)
    assert d["Natalicio de Benito Juárez"] == AstroDate(2024, 3, 18)
    assert d["Día de la Revolución"] == AstroDate(2024, 11, 18)


@pytest.mark.skipif(not _have_tab("MX"), reason="mx.tab not present")
def test_mx_transmision_sexennial_only():
    """Transmisión del Poder Ejecutivo Federal is present only in a handover
    year (2024), silent in 2023/2025."""
    assert ("Transmisión del Poder Ejecutivo Federal", None) not in _dates_for("MX", 2023)
    assert _dates_for("MX", 2024)[("Transmisión del Poder Ejecutivo Federal", None)] == AstroDate(2024, 10, 1)
    assert ("Transmisión del Poder Ejecutivo Federal", None) not in _dates_for("MX", 2025)


@pytest.mark.skipif(not _have_tab("PE"), reason="pe.tab not present")
def test_pe_arica_year_gated_from_2024():
    """Batalla de Arica y Día de la Bandera national from 2024 (Ley 31794)."""
    assert ("Batalla de Arica y Día de la Bandera", None) not in _dates_for("PE", 2023)
    assert _dates_for("PE", 2024)[("Batalla de Arica y Día de la Bandera", None)] == AstroDate(2024, 6, 7)


# --- SA: fixed Gregorian days + Islamic days independently re-derived from the
#     raw umm_al_qura.tab JDN column (this file, not the engine, is the witness). ---
def _jdn_to_gregorian(jdn: int):
    """Fliegel & van Flandern (1968) JDN->Gregorian, standalone (no chronologia import)."""
    ell = jdn + 68569
    n = (4 * ell) // 146097
    ell = ell - (146097 * n + 3) // 4
    i = (4000 * (ell + 1)) // 1461001
    ell = ell - (1461 * i) // 4 + 31
    j = (80 * ell) // 2447
    day = ell - (2447 * j) // 80
    ell2 = j // 11
    month = j + 2 - 12 * ell2
    year = 100 * (n - 49) + i + ell2
    return year, month, day


def _umm_al_qura_month_start(ah_year: int, ah_month: int) -> int:
    """Read ``jdn_start`` straight out of the raw calendar_data table (no
    calendars.py machinery -- an independent re-read of the published source)."""
    path = os.path.join(os.path.dirname(_DATA_DIR), "calendar_data", "umm_al_qura.tab")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            y, m, leap, jdn = line.split()
            if int(y) == ah_year and int(m) == ah_month:
                return int(jdn)
    raise LookupError((ah_year, ah_month))


_shawwal_start = _umm_al_qura_month_start(1445, 10)
_dhulhijjah_start = _umm_al_qura_month_start(1445, 12)
_SA_ISLAMIC_DATES_2024 = sorted(
    _jdn_to_gregorian(_shawwal_start + i) for i in range(3)
) + sorted(_jdn_to_gregorian(_dhulhijjah_start + i) for i in range(8, 13))


def test_sa_fixed_golds_2024():
    got = _dates_for("SA", 2024)
    assert got[("يوم التأسيس", None)] == AstroDate(2024, 2, 22)   # Founding Day
    assert got[("اليوم الوطني", None)] == AstroDate(2024, 9, 23)  # National Day


def test_sa_islamic_golds_2024_independent_jdn_rederivation():
    got = sorted(h.date for h in holidays_for("SA", 2024)
                 if "religious" in h.categories)
    expect = [AstroDate(y, m, d) for (y, m, d) in _SA_ISLAMIC_DATES_2024]
    assert got == expect
    assert len(got) == 8
    assert AstroDate(2024, 4, 10) in got  # Eid al-Fitr
    assert AstroDate(2024, 6, 16) in got  # Eid al-Adha


# --- Islamic-breadth gating ---
@pytest.mark.skipif(not _have_tab("MA"), reason="ma.tab not present")
def test_ma_amazigh_new_year_gated_from_2024():
    """رأس السنة الأمازيغية (Yennayer) national from 2024 (2023 royal decree)."""
    name = "رأس السنة الأمازيغية"
    assert (name, None) not in _dateset_for("MA", 2023)
    assert AstroDate(2024, 1, 13) in _dateset_for("MA", 2024).get((name, None), set())


@pytest.mark.skipif(not _have_tab("PK"), reason="pk.tab not present")
def test_pk_youm_e_takbeer_gated_from_2024():
    """Youm-e-Takbeer national from 2024, absent 2023."""
    assert ("Youm-e-Takbeer", None) not in _dates_for("PK", 2023)
    assert _dates_for("PK", 2024)[("Youm-e-Takbeer", None)] == AstroDate(2024, 5, 28)


@pytest.mark.skipif(not _have_tab("ID"), reason="id.tab not present")
def test_id_four_calendars_present_2024():
    """Indonesia mixes four calendars in one year: Islamic (tabulated),
    Chinese/Balinese/Buddhist (decree) and Christian (Easter)."""
    hs = {h.name: h for h in holidays_for("ID", 2024)}
    assert hs["Hari Raya Idul Fitri"].basis == "exact"
    assert hs["Tahun Baru Imlek"].basis == "tabulated"
    assert hs["Hari Suci Nyepi"].basis == "tabulated"
    assert hs["Wafat Yesus Kristus"].basis == "exact"
    assert {hs["Hari Raya Idul Fitri"].date.month,
            hs["Tahun Baru Imlek"].date.month,
            hs["Hari Suci Nyepi"].date.month} == {4, 2, 3}


def test_jp_mountain_day_year_gated_from_2016():
    """Mountain Day (山の日) -- established by the 2014 amendment, in force from
    2016 (jp.tab "2016-"): absent 2015, present from 2016."""
    assert ("山の日", None) not in _dates_for("JP", 2015)
    assert _dates_for("JP", 2016)[("山の日", None)] == AstroDate(2016, 8, 11)


# ==========================================================================
# PT municipal source-vs-engine: the ``primary`` witness for PT municipal golds.
# Expected dates come from the cited seed TSVs, not from pt.tab's own args.
# ==========================================================================
_E2024 = easter(2024, "gregorian")

_MONTHS_PT = {
    "Janeiro": 1, "Fevereiro": 2, "Marco": 3, "Março": 3, "Abril": 4, "Maio": 5,
    "Junho": 6, "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10,
    "Novembro": 11, "Dezembro": 12,
}

_MUNI_ALIASES = {
    "Santa Cruz (Madeira)": "Santa Cruz",
    "Calheta (Madeira)": "Calheta (Funchal)",
    "Lagoa (Acores)": "Lagoa",
    "Santana (Madeira)": "Santana",
    "Praia da Vitoria": "Vila da Praia da Vitoria",
    "Vila Nova do Corvo": "Corvo",
    "Castanheira de Pera": "Castanheira de Pera",
    "Nordeste (Acores)": "Nordeste",
    "Silves (Portugal)": "Silves",
    "Meda": "Meda",
    "Povoacao (Acores)": "Povoacao",
    "Idanha-A-Nova": "Idanha-a-Nova",
}
_MUNI_NOT_A_CONCELHO = {"Quarteira"}


def _fold(name: str) -> str:
    """ASCII-fold (via Unicode NFKD decomposition) + normalize whitespace."""
    import unicodedata
    decomposed = unicodedata.normalize("NFKD", name)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return " ".join(stripped.split())


_MUNI_ALIASES_FOLDED = {_fold(k): v for k, v in _MUNI_ALIASES.items()}


def _load_municipio_codes() -> dict:
    path = os.path.join(_PAPERS, "municipios_portugal.csv")
    codes = {}
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            codes[_fold(row["Municipio"].strip())] = "PT-" + row["Codigo"].strip()
    return codes


def _resolve_muni_code(name: str, codes: dict):
    folded = _fold(name)
    name = _MUNI_ALIASES_FOLDED.get(folded, name)
    return codes.get(_fold(name))


def _split_municipalities(field: str):
    field = field.split(".")[0].replace(" e ", ", ")
    return [n.strip() for n in field.split(",") if n.strip()]


def _load_pt_tab_municipal(kinds):
    """Every ``kind in kinds`` municipal row of pt.tab, as (subdiv, kind, args, name)."""
    out = []
    with open(os.path.join(_DATA_DIR, "pt.tab"), encoding="utf-8") as fh:
        for line in fh:
            if line.lstrip().startswith("#") or not line.strip():
                continue
            cols = [c.strip() for c in line.split("|")]
            if "municipal" not in cols[3] or cols[0] not in kinds:
                continue
            out.append((cols[4], cols[0], cols[2], cols[1]))  # subdiv,kind,args,name
    return out


def _pt_fixed_municipal_source_golds():
    """Parse feriados.tsv -> {(subdiv, name): (month, day)} (source-derived)."""
    codes = _load_municipio_codes()
    out = {}
    path = os.path.join(_PAPERS, "feriados.tsv")
    with open(path, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            data, feriado, muni_field = parts[0], parts[1].strip(), parts[2]
            m = re.match(r"\s*(\d+)\s*de\s*(\w+)", data.strip())
            day, month = int(m.group(1)), _MONTHS_PT[m.group(2)]
            for n in _split_municipalities(muni_field):
                if n in _MUNI_NOT_A_CONCELHO:
                    continue
                code = _resolve_muni_code(n, codes)
                if code is None:
                    continue
                out[(code, feriado)] = (month, day)
    return out


_PT_MUNICIPAL_FIXED_SOURCE = _pt_fixed_municipal_source_golds()
_PT_MUNICIPAL_FIXED_TAB = [
    (subdiv, int(args.split()[0]), int(args.split()[1]), name)
    for subdiv, kind, args, name in _load_pt_tab_municipal({"fixed"})
]


@pytest.mark.parametrize("subdiv,name,month,day", sorted(
    (s, n, m, d) for s, m, d, n in _PT_MUNICIPAL_FIXED_TAB))
def test_pt_municipal_fixed_gold_matches_source(subdiv, name, month, day):
    """Source-vs-engine: the feriados.tsv-derived (month, day) must equal both
    the engine's resolved 2024 date AND the .tab file's own args."""
    src_month, src_day = _PT_MUNICIPAL_FIXED_SOURCE[(subdiv, name)]
    assert (src_month, src_day) == (month, day)
    got = _dates_for("PT", 2024, subdiv=subdiv)
    assert got[(name, subdiv)] == AstroDate(2024, month, day)


def test_pt_municipal_fixed_gold_count():
    assert len(_PT_MUNICIPAL_FIXED_TAB) == 224


def _nth_weekday_2024(month, n, weekday, post_offset=0):
    rec = nth_weekday_of_month(n, weekday, month=month)
    got = list(occurrences(rec, AstroDate(2024, 1, 1), until=AstroDate(2024, 12, 31)))
    return got[0].start + timedelta(days=post_offset)


_MOVABLE_PHRASE_RULES = [
    (r"^Segunda-feira apos a Pascoa$", lambda: _E2024 + timedelta(days=1)),
    (r"^Segunda Segunda-feira apos a Pascoa", lambda: _E2024 + timedelta(days=8)),
    (r"^Terceira Segunda-feira apos a Pascoa", lambda: _E2024 + timedelta(days=15)),
    (r"^Terca-feira que segue o primeiro domingo depois da Pascoa",
     lambda: _E2024 + timedelta(days=9)),
    (r"^Quinta Segunda-feira apos a Pascoa", lambda: _E2024 + timedelta(days=29)),
    (r"^Sexta Quinta-feira apos o Domingo de Pascoa", lambda: _E2024 + timedelta(days=39)),
    (r"^Segunda-feira apos o Domingo de Pentecostes", lambda: _E2024 + timedelta(days=50)),
    (r"^Terca-Feira apos o Domingo de Pentecostes", lambda: _E2024 + timedelta(days=51)),
    (r"^Sexta-feira a seguir ao Dia de Corpo de Deus", lambda: _E2024 + timedelta(days=61)),
    (r"^Segunda-feira apos o segundo Domingo de Julho", lambda: _nth_weekday_2024(7, 2, 6, 1)),
    (r"^Segunda-feira apos o terceiro Domingo de Julho", lambda: _nth_weekday_2024(7, 3, 6, 1)),
    (r"^Segunda-feira apos o ultimo Domingo de Julho", lambda: _nth_weekday_2024(7, -1, 6, 1)),
    (r"^Segunda-feira apos o primeiro Domingo de Agosto", lambda: _nth_weekday_2024(8, 1, 6, 1)),
    (r"^Segunda-feira apos o segundo Domingo de Agosto", lambda: _nth_weekday_2024(8, 2, 6, 1)),
    (r"^Segunda-feira apos o terceiro Domingo de Agosto", lambda: _nth_weekday_2024(8, 3, 6, 1)),
    (r"^Segunda-feira apos o quarto Domingo de Agosto", lambda: _nth_weekday_2024(8, 4, 6, 1)),
    (r"^Segunda Sexta-feira de Setembro", lambda: _nth_weekday_2024(9, 2, 4)),
    (r"^Terca-feira apos o segundo Domingo de Setembro", lambda: _nth_weekday_2024(9, 2, 6, 2)),
    (r"^Segunda-feira apos o primeiro Domingo de Outubro", lambda: _nth_weekday_2024(10, 1, 6, 1)),
    (r"^Segunda-feira apos o primeiro Sabado de Outubro", lambda: _nth_weekday_2024(10, 1, 5, 2)),
]


def _pt_movable_municipal_source_golds():
    """Parse feriados_moveis.tsv -> {subdiv: (AstroDate, name)}."""
    codes = _load_municipio_codes()
    out = {}
    path = os.path.join(_PAPERS, "feriados_moveis.tsv")
    with open(path, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            data, feriado, muni_field = parts[0], parts[1].strip(), parts[2]
            data_folded = _fold(data.strip())
            rule_fn = None
            for pat, fn in _MOVABLE_PHRASE_RULES:
                if re.match(_fold(pat), data_folded):
                    rule_fn = fn
                    break
            assert rule_fn is not None, f"unrecognised feriados_moveis.tsv phrase: {data!r}"
            date = rule_fn()
            for n in _split_municipalities(muni_field):
                if n in _MUNI_NOT_A_CONCELHO:
                    continue
                code = _resolve_muni_code(n, codes)
                if code is None:
                    continue
                out[code] = (date, feriado)
    return out


_PT_MUNICIPAL_MOVABLE_SOURCE = _pt_movable_municipal_source_golds()
_PT_MUNICIPAL_MOVABLE_TAB = _load_pt_tab_municipal({"easter", "nth_weekday"})


@pytest.mark.parametrize("subdiv,kind,args,name", sorted(_PT_MUNICIPAL_MOVABLE_TAB))
def test_pt_municipal_movable_gold_matches_source(subdiv, kind, args, name):
    """Source-vs-engine: the feriados_moveis.tsv phrase-derived date must equal
    the engine's resolved 2024 date."""
    src_date, _ = _PT_MUNICIPAL_MOVABLE_SOURCE[subdiv]
    got = _dates_for("PT", 2024, subdiv=subdiv)
    assert got[(name, subdiv)] == AstroDate(src_date.year, src_date.month, src_date.day)


def test_pt_municipal_movable_gold_count():
    assert len(_PT_MUNICIPAL_MOVABLE_TAB) == 73


def test_pt_municipal_gold_total():
    assert len(_PT_MUNICIPAL_FIXED_TAB) + len(_PT_MUNICIPAL_MOVABLE_TAB) == 297


# ==========================================================================
# ES autonomous-community layer -- golds parsed from the four cited BOE tables
# (source-vs-engine): the expected dates come from the BOE HTML, not es.tab args.
# ==========================================================================
_ES_CODES = ["ES-AN", "ES-AR", "ES-AS", "ES-IB", "ES-CN", "ES-CB", "ES-CM",
             "ES-CL", "ES-CT", "ES-EX", "ES-GA", "ES-MD", "ES-MC", "ES-NC",
             "ES-PV", "ES-RI", "ES-VC", "ES-CE", "ES-ML"]
_ES_MONTHS = {m.lower(): i for i, m in enumerate(
    ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto",
     "Septiembre", "Octubre", "Noviembre", "Diciembre"], 1)}
_ES_BOE = {2023: "es_boe_BOE-A-2022-16755.html",
           2024: "es_boe_BOE-A-2023-22014.html",
           2025: "es_boe_BOE-A-2024-21316.html",
           2026: "es_boe_BOE-A-2025-21667.html"}


def _es_canon(n):
    if n.startswith("Lunes siguiente") or n.startswith("Día siguiente"):
        if "Asturias" in n:
            return "Día de Asturias"
        if "Illes Balears" in n:
            return "Día de les Illes Balears"
        if "Rioja" in n:
            return "Día de La Rioja"
        if "San Jorge" in n:
            return "San Jorge/Día de Aragón"
        if "San José" in n:
            return "San José"
        return None
    if "Rioja" in n:
        return "Día de La Rioja"
    if "Sacrificio" in n or "Adha" in n:
        return "Fiesta del Sacrificio (Aid al-Adha)"
    if "Eid Fitr" in n or "Eid al-Fitr" in n:
        return "Fiesta del Aid al-Fitr"
    if n.startswith("Corpus") or n.startswith("Fiesta del Corpus"):
        return "Corpus Christi"
    return n


def _es_regional_source_golds():
    """Parse the four BOE tables into {(subdiv, name, year): (month, day)}."""
    out = {}
    for year, fn in _ES_BOE.items():
        path = os.path.join(_PAPERS, fn)
        html_text = open(path, encoding="utf-8").read()
        m = re.search(r'<table class="tabla_girada_condensada">(.*?)</table>',
                      html_text, re.S)
        rows = re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(1), re.S)
        curm = None
        for r in rows:
            cells = [re.sub(r"<[^>]+>", "", c).strip()
                     for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)]
            import html as _h
            cells = [_h.unescape(c) for c in cells]
            if not cells:
                continue
            if cells[0].lower() in _ES_MONTHS:
                curm = _ES_MONTHS[cells[0].lower()]
                continue
            mm = re.match(r"(\d+)\s+(.*)", cells[0])
            if not mm or curm is None:
                continue
            day = int(mm.group(1))
            name = mm.group(2).rstrip(".").strip()
            marks = {_ES_CODES[i]: v for i, v in enumerate(cells[1:])
                     if i < 19 and v in ("*", "**", "***")}
            if len(marks) == 19:
                continue
            base = _es_canon(name)
            if base is None:
                continue
            for sub in marks:
                out[(sub, base, year)] = (curm, day)
    return out


_ES_REGIONAL_SOURCE = _es_regional_source_golds()


@pytest.mark.parametrize("subdiv,name,year,month,day", sorted(
    (s, n, y, m, d) for (s, n, y), (m, d) in _ES_REGIONAL_SOURCE.items()))
def test_es_regional_gold_matches_boe_source(subdiv, name, year, month, day):
    """Source-vs-engine: the BOE-table date must equal the engine's decree
    resolution for that community and year."""
    got = _dates_for("ES", year, subdiv=subdiv)
    assert got[(name, subdiv)] == AstroDate(year, month, day)


def test_es_regional_covers_all_communities():
    assert {s for (s, _n, _y) in _ES_REGIONAL_SOURCE} == set(_ES_CODES)
