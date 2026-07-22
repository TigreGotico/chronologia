"""IT + FR subdivision-depth extension, matching vacanza/holidays 0.101.

Italy (it.tab): the pre-existing 20 regional-capital patron-saint rows were
independently sourced (papers/holidays/it_holidays.md,
https://it.wikipedia.org/wiki/Santi_patroni_cattolici_delle_città_capoluogo_di_provincia_italiane)
and are left untouched even where a code's vacanza entry differs (e.g.
IT-PG: our "San Costanzo" vs vacanza's "Santa Chiara d'Assisi"/"San Francesco
d'Assisi" -- a documented divergence, not merged in). The other 87 of
vacanza's 107 ISO 3166-2 province subdivisions are added here, derived from
vacanza/holidays 0.101 (MIT) -- holidays/countries/italy.py -- rather than
independently re-verified against each comune's gazette, per the house rule
that permits vacanza-derived data as long as it is flagged as such. Vacanza's
114-subdivision count also includes 7 non-ISO "city" duplicate codes
(Andria/Barletta/Cesena/Forli/Pesaro/Trani/Urbino, which mirror their parent
province BT/FC/PU) -- these are deliberately omitted as duplicates of an
ISO code we already carry.

France (fr.tab): the pre-existing FR-57/FR-6AE (Alsace-Moselle local law)
rows are untouched. The ten overseas/Pacific subdivisions vacanza models
(FR-971 Guadeloupe, FR-972 Martinique, FR-973 Guyane, FR-974 La Réunion,
FR-976 Mayotte, FR-BL Saint-Barthélemy, FR-MF Saint-Martin, FR-NC
Nouvelle-Calédonie, FR-PF Polynésie Française, FR-WF Wallis-et-Futuna) are
added, likewise derived from vacanza/holidays 0.101 (MIT) --
holidays/countries/france.py. FR-PM (Saint-Pierre-et-Miquelon) and FR-TF
(Terres australes françaises) carry no subdivision-specific holidays in
vacanza and are omitted. FR-PF's autonomy holiday changed in 2025 (Décret du
30 avril 2024 replaced "Fête de l'autonomie" with "Matāri'i"); the ``valid``
column models both eras so 2024 and 2025 each resolve the era-correct rule.

Golding discipline
-------------------
Every new rule's gold is *not* hand-typed from the ``.tab`` file: it was
captured by directly querying vacanza's own ``holidays`` package (the
independent upstream this batch is derived from) for the exact subdivision
code across 2024 and 2025 (see IT_SUBDIV_GOLD / FR_SUBDIV_GOLD below) --
the vacanza package computed these dates and names itself, on its own
recurrence machinery, entirely independent of chronologia's engine. Every
``fixed`` rule's gold is its own literal ``(month, day)``, confirmed
constant across both 2024 and 2025 (a movable rule masquerading as fixed
would show up as a mismatch between the two years). Every ``nth_weekday``
rule (IT-AT, IT-BR, IT-BT's San Riccardo di Andria, IT-SU) and ``easter``
rule (IT-BZ's Lunedì di Pentecoste; FR-971/972/PF's Vendredi saint;
FR-971's Mi-Carême) was confirmed to differ in date between 2024 and 2025 in
exactly the way the movable arithmetic predicts, ruling out a coincidental
single-year match.
"""
import os

import pytest

from chronologia import AstroDate, holidays_for
from chronologia.civil_holidays import (_DATA_DIR, EasterOffsetRule,
                                        FixedRule, NthWeekdayRule)
from test_holiday_golds import HOLIDAY_GOLDS, _reg

IT_SUBDIV_GOLD = [
    ("IT-AG", "San Gerlando", 2024, 2, 25),
    ("IT-AG", "San Gerlando", 2025, 2, 25),
    ("IT-AL", "San Baudolino", 2024, 11, 10),
    ("IT-AL", "San Baudolino", 2025, 11, 10),
    ("IT-AP", "Sant'Emidio", 2024, 8, 5),
    ("IT-AP", "Sant'Emidio", 2025, 8, 5),
    ("IT-AR", "San Donato d'Arezzo", 2024, 8, 7),
    ("IT-AR", "San Donato d'Arezzo", 2025, 8, 7),
    ("IT-AT", "San Secondo di Asti", 2024, 5, 7),
    ("IT-AT", "San Secondo di Asti", 2025, 5, 6),
    ("IT-AV", "San Modestino", 2024, 2, 14),
    ("IT-AV", "San Modestino", 2025, 2, 14),
    ("IT-BG", "Sant'Alessandro di Bergamo", 2024, 8, 26),
    ("IT-BG", "Sant'Alessandro di Bergamo", 2025, 8, 26),
    # IT-BI/IT-PO's patron day coincides in both name and date with the
    # national Santo Stefano (26 Dec) -- the holidays-lib subdiv_only diff
    # against national dropped these as identical, so they're golded here by
    # hand from the .tab row's own self-evident (month, day) rather than
    # from the captured vacanza diff.
    ("IT-BI", "Santo Stefano", 2024, 12, 26),
    ("IT-BI", "Santo Stefano", 2025, 12, 26),
    ("IT-BL", "San Martino", 2024, 11, 11),
    ("IT-BL", "San Martino", 2025, 11, 11),
    ("IT-BN", "San Bartolomeo apostolo", 2024, 8, 24),
    ("IT-BN", "San Bartolomeo apostolo", 2025, 8, 24),
    ("IT-BR", "San Teodoro d'Amasea e San Lorenzo da Brindisi", 2024, 9, 1),
    ("IT-BR", "San Teodoro d'Amasea e San Lorenzo da Brindisi", 2025, 9, 7),
    ("IT-BS", "Santi Faustino e Giovita", 2024, 2, 15),
    ("IT-BS", "Santi Faustino e Giovita", 2025, 2, 15),
    ("IT-BT", "San Nicola Pellegrino", 2024, 5, 3),
    ("IT-BT", "San Riccardo di Andria", 2024, 9, 15),
    ("IT-BT", "San Ruggero", 2024, 12, 30),
    ("IT-BT", "San Nicola Pellegrino", 2025, 5, 3),
    ("IT-BT", "San Riccardo di Andria", 2025, 9, 21),
    ("IT-BT", "San Ruggero", 2025, 12, 30),
    ("IT-BZ", "Lunedì di Pentecoste", 2024, 5, 20),
    ("IT-BZ", "Lunedì di Pentecoste", 2025, 6, 9),
    ("IT-CE", "San Sebastiano", 2024, 1, 20),
    ("IT-CE", "San Sebastiano", 2025, 1, 20),
    ("IT-CH", "San Giustino di Chieti", 2024, 5, 11),
    ("IT-CH", "San Giustino di Chieti", 2025, 5, 11),
    ("IT-CL", "San Michele Arcangelo", 2024, 9, 29),
    ("IT-CL", "San Michele Arcangelo", 2025, 9, 29),
    ("IT-CN", "San Michele Arcangelo", 2024, 9, 29),
    ("IT-CN", "San Michele Arcangelo", 2025, 9, 29),
    ("IT-CO", "Sant'Abbondio", 2024, 8, 31),
    ("IT-CO", "Sant'Abbondio", 2025, 8, 31),
    ("IT-CR", "Sant'Omobono", 2024, 11, 13),
    ("IT-CR", "Sant'Omobono", 2025, 11, 13),
    ("IT-CS", "Madonna del Pilerio", 2024, 2, 12),
    ("IT-CS", "Madonna del Pilerio", 2025, 2, 12),
    ("IT-CT", "Sant'Agata", 2024, 2, 5),
    ("IT-CT", "Sant'Agata", 2025, 2, 5),
    ("IT-EN", "Madonna della Visitazione", 2024, 7, 2),
    ("IT-EN", "Madonna della Visitazione", 2025, 7, 2),
    ("IT-FC", "Madonna del Fuoco", 2024, 2, 4),
    ("IT-FC", "San Giovanni Battista", 2024, 6, 24),
    ("IT-FC", "Madonna del Fuoco", 2025, 2, 4),
    ("IT-FC", "San Giovanni Battista", 2025, 6, 24),
    ("IT-FE", "San Giorgio", 2024, 4, 23),
    ("IT-FE", "San Giorgio", 2025, 4, 23),
    ("IT-FG", "Madonna dei Sette Veli", 2024, 3, 22),
    ("IT-FG", "Madonna dei Sette Veli", 2025, 3, 22),
    ("IT-FM", "Maria Santissima Assunta", 2024, 8, 15),
    ("IT-FM", "Maria Santissima Assunta", 2024, 8, 16),
    ("IT-FM", "Maria Santissima Assunta", 2025, 8, 15),
    ("IT-FM", "Maria Santissima Assunta", 2025, 8, 16),
    ("IT-FR", "San Silverio", 2024, 6, 20),
    ("IT-FR", "San Silverio", 2025, 6, 20),
    ("IT-GO", "Santi Ilario e Taziano", 2024, 3, 16),
    ("IT-GO", "Santi Ilario e Taziano", 2025, 3, 16),
    ("IT-GR", "San Lorenzo", 2024, 8, 10),
    ("IT-GR", "San Lorenzo", 2025, 8, 10),
    ("IT-IM", "San Leonardo da Porto Maurizio", 2024, 11, 26),
    ("IT-IM", "San Leonardo da Porto Maurizio", 2025, 11, 26),
    ("IT-IS", "San Pietro Celestino", 2024, 5, 19),
    ("IT-IS", "San Pietro Celestino", 2025, 5, 19),
    ("IT-KR", "San Dionigi", 2024, 10, 9),
    ("IT-KR", "San Dionigi", 2025, 10, 9),
    ("IT-LC", "San Nicola", 2024, 12, 6),
    ("IT-LC", "San Nicola", 2025, 12, 6),
    ("IT-LE", "Sant'Oronzo", 2024, 8, 26),
    ("IT-LE", "Sant'Oronzo", 2025, 8, 26),
    ("IT-LI", "Santa Giulia", 2024, 5, 22),
    ("IT-LI", "Santa Giulia", 2025, 5, 22),
    ("IT-LO", "San Bassiano", 2024, 1, 19),
    ("IT-LO", "San Bassiano", 2025, 1, 19),
    ("IT-LT", "San Marco Evangelista", 2024, 4, 25),
    ("IT-LT", "Santa Maria Goretti", 2024, 7, 6),
    ("IT-LT", "San Marco Evangelista", 2025, 4, 25),
    ("IT-LT", "Santa Maria Goretti", 2025, 7, 6),
    ("IT-LU", "San Paolino di Lucca", 2024, 7, 12),
    ("IT-LU", "San Paolino di Lucca", 2025, 7, 12),
    ("IT-MB", "San Giovanni Battista", 2024, 6, 24),
    ("IT-MB", "San Giovanni Battista", 2025, 6, 24),
    ("IT-MC", "San Giuliano l'ospitaliere", 2024, 8, 31),
    ("IT-MC", "San Giuliano l'ospitaliere", 2025, 8, 31),
    ("IT-ME", "Madonna della Lettera", 2024, 6, 3),
    ("IT-ME", "Madonna della Lettera", 2025, 6, 3),
    ("IT-MN", "Sant'Anselmo da Baggio", 2024, 3, 18),
    ("IT-MN", "Sant'Anselmo da Baggio", 2025, 3, 18),
    ("IT-MO", "San Geminiano", 2024, 1, 31),
    ("IT-MO", "San Geminiano", 2025, 1, 31),
    ("IT-MS", "San Francesco d'Assisi", 2024, 10, 4),
    ("IT-MS", "San Francesco d'Assisi", 2025, 10, 4),
    ("IT-MT", "Madonna della Bruna", 2024, 7, 2),
    ("IT-MT", "Madonna della Bruna", 2025, 7, 2),
    ("IT-NO", "San Gaudenzio", 2024, 1, 22),
    ("IT-NO", "San Gaudenzio", 2025, 1, 22),
    ("IT-NU", "Nostra Signora della Neve", 2024, 8, 5),
    ("IT-NU", "Nostra Signora della Neve", 2025, 8, 5),
    ("IT-OR", "Sant'Archelao", 2024, 2, 13),
    ("IT-OR", "Sant'Archelao", 2025, 2, 13),
    ("IT-PC", "Sant'Antonino di Piacenza", 2024, 7, 4),
    ("IT-PC", "Sant'Antonino di Piacenza", 2025, 7, 4),
    ("IT-PD", "Sant'Antonio di Padova", 2024, 6, 13),
    ("IT-PD", "Sant'Antonio di Padova", 2025, 6, 13),
    ("IT-PE", "San Cetteo", 2024, 10, 10),
    ("IT-PE", "San Cetteo", 2025, 10, 10),
    ("IT-PI", "San Ranieri", 2024, 6, 17),
    ("IT-PI", "San Ranieri", 2025, 6, 17),
    ("IT-PN", "San Marco Evangelista", 2024, 4, 25),
    ("IT-PN", "Madonna delle Grazie", 2024, 9, 8),
    ("IT-PN", "San Marco Evangelista", 2025, 4, 25),
    ("IT-PN", "Madonna delle Grazie", 2025, 9, 8),
    ("IT-PO", "Santo Stefano", 2024, 12, 26),
    ("IT-PO", "Santo Stefano", 2025, 12, 26),
    ("IT-PR", "Sant'Ilario di Poitiers", 2024, 1, 13),
    ("IT-PR", "Sant'Ilario di Poitiers", 2025, 1, 13),
    ("IT-PT", "San Jacopo", 2024, 7, 25),
    ("IT-PT", "San Jacopo", 2025, 7, 25),
    ("IT-PU", "San Crescentino", 2024, 6, 1),
    ("IT-PU", "San Terenzio di Pesaro", 2024, 9, 24),
    ("IT-PU", "San Crescentino", 2025, 6, 1),
    ("IT-PU", "San Terenzio di Pesaro", 2025, 9, 24),
    ("IT-PV", "San Siro", 2024, 12, 9),
    ("IT-PV", "San Siro", 2025, 12, 9),
    ("IT-RA", "Sant'Apollinare", 2024, 7, 23),
    ("IT-RA", "Sant'Apollinare", 2025, 7, 23),
    ("IT-RC", "San Giorgio", 2024, 4, 23),
    ("IT-RC", "San Giorgio", 2025, 4, 23),
    ("IT-RE", "San Prospero Vescovo", 2024, 11, 24),
    ("IT-RE", "San Prospero Vescovo", 2025, 11, 24),
    ("IT-RG", "San Giorgio Martire", 2024, 4, 23),
    ("IT-RG", "San Giovanni Battista", 2024, 8, 29),
    ("IT-RG", "San Giorgio Martire", 2025, 4, 23),
    ("IT-RG", "San Giovanni Battista", 2025, 8, 29),
    ("IT-RI", "Santa Barbara", 2024, 12, 4),
    ("IT-RI", "Santa Barbara", 2025, 12, 4),
    ("IT-RN", "San Gaudenzio", 2024, 10, 14),
    ("IT-RN", "San Gaudenzio", 2025, 10, 14),
    ("IT-RO", "San Bellino", 2024, 11, 26),
    ("IT-RO", "San Bellino", 2025, 11, 26),
    ("IT-SA", "San Matteo Evangelista", 2024, 9, 21),
    ("IT-SA", "San Matteo Evangelista", 2025, 9, 21),
    ("IT-SI", "Sant'Ansano", 2024, 12, 1),
    ("IT-SI", "Sant'Ansano", 2025, 12, 1),
    ("IT-SO", "San Gervasio e San Protasio", 2024, 6, 19),
    ("IT-SO", "San Gervasio e San Protasio", 2025, 6, 19),
    ("IT-SP", "San Giuseppe", 2024, 3, 19),
    ("IT-SP", "San Giuseppe", 2025, 3, 19),
    ("IT-SR", "Santa Lucia", 2024, 12, 13),
    ("IT-SR", "Santa Lucia", 2025, 12, 13),
    ("IT-SS", "San Nicola", 2024, 12, 6),
    ("IT-SS", "San Nicola", 2025, 12, 6),
    ("IT-SU", "San Ponziano", 2024, 5, 16),
    ("IT-SU", "San Ponziano", 2025, 5, 15),
    ("IT-SV", "Nostra Signora della Misericordia", 2024, 3, 18),
    ("IT-SV", "Nostra Signora della Misericordia", 2025, 3, 18),
    ("IT-TA", "San Cataldo", 2024, 5, 10),
    ("IT-TA", "San Cataldo", 2025, 5, 10),
    ("IT-TE", "San Berardo da Pagliara", 2024, 12, 19),
    ("IT-TE", "San Berardo da Pagliara", 2025, 12, 19),
    ("IT-TP", "Sant'Alberto degli Abati", 2024, 8, 7),
    ("IT-TP", "Sant'Alberto degli Abati", 2025, 8, 7),
    ("IT-TR", "San Valentino", 2024, 2, 14),
    ("IT-TR", "San Valentino", 2025, 2, 14),
    ("IT-TV", "San Liberale", 2024, 4, 27),
    ("IT-TV", "San Liberale", 2025, 4, 27),
    ("IT-UD", "Santi Ermacora e Fortunato", 2024, 7, 12),
    ("IT-UD", "Santi Ermacora e Fortunato", 2025, 7, 12),
    ("IT-VA", "San Vittore il Moro", 2024, 5, 8),
    ("IT-VA", "San Vittore il Moro", 2025, 5, 8),
    ("IT-VB", "San Vittore il Moro", 2024, 5, 8),
    ("IT-VB", "San Vittore il Moro", 2025, 5, 8),
    ("IT-VC", "Sant'Eusebio di Vercelli", 2024, 8, 1),
    ("IT-VC", "Sant'Eusebio di Vercelli", 2025, 8, 1),
    ("IT-VI", "Madonna di Monte Berico", 2024, 9, 8),
    ("IT-VI", "Madonna di Monte Berico", 2025, 9, 8),
    ("IT-VR", "San Zeno", 2024, 5, 21),
    ("IT-VR", "San Zeno", 2025, 5, 21),
    ("IT-VT", "Santa Rosa da Viterbo", 2024, 9, 4),
    ("IT-VT", "Santa Rosa da Viterbo", 2025, 9, 4),
    ("IT-VV", "San Leoluca", 2024, 3, 1),
    ("IT-VV", "San Leoluca", 2025, 3, 1),
]

FR_SUBDIV_GOLD = [
    ("FR-971", "Mi-Carême", 2024, 3, 7),
    ("FR-971", "Vendredi saint", 2024, 3, 29),
    ("FR-971", "Abolition de l'esclavage", 2024, 5, 27),
    ("FR-971", "Fête de Victor Schoelcher", 2024, 7, 21),
    ("FR-971", "Mi-Carême", 2025, 3, 27),
    ("FR-971", "Vendredi saint", 2025, 4, 18),
    ("FR-971", "Abolition de l'esclavage", 2025, 5, 27),
    ("FR-971", "Fête de Victor Schoelcher", 2025, 7, 21),
    ("FR-972", "Vendredi saint", 2024, 3, 29),
    ("FR-972", "Abolition de l'esclavage", 2024, 5, 22),
    ("FR-972", "Fête de Victor Schoelcher", 2024, 7, 21),
    ("FR-972", "Vendredi saint", 2025, 4, 18),
    ("FR-972", "Abolition de l'esclavage", 2025, 5, 22),
    ("FR-972", "Fête de Victor Schoelcher", 2025, 7, 21),
    ("FR-973", "Abolition de l'esclavage", 2024, 6, 10),
    ("FR-973", "Abolition de l'esclavage", 2025, 6, 10),
    ("FR-974", "Abolition de l'esclavage", 2024, 12, 20),
    ("FR-974", "Abolition de l'esclavage", 2025, 12, 20),
    ("FR-976", "Abolition de l'esclavage", 2024, 4, 27),
    ("FR-976", "Abolition de l'esclavage", 2025, 4, 27),
    ("FR-BL", "Abolition de l'esclavage", 2024, 10, 9),
    ("FR-BL", "Abolition de l'esclavage", 2025, 10, 9),
    ("FR-MF", "Abolition de l'esclavage", 2024, 5, 28),
    ("FR-MF", "Fête de Victor Schoelcher", 2024, 7, 21),
    ("FR-MF", "Abolition de l'esclavage", 2025, 5, 28),
    ("FR-MF", "Fête de Victor Schoelcher", 2025, 7, 21),
    ("FR-NC", "Fête de la Citoyenneté", 2024, 9, 24),
    ("FR-NC", "Fête de la Citoyenneté", 2025, 9, 24),
    ("FR-PF", "Arrivée de l'Évangile", 2024, 3, 5),
    ("FR-PF", "Vendredi saint", 2024, 3, 29),
    ("FR-PF", "Fête de l'autonomie", 2024, 6, 29),
    ("FR-PF", "Arrivée de l'Évangile", 2025, 3, 5),
    ("FR-PF", "Vendredi saint", 2025, 4, 18),
    ("FR-PF", "Matāri'i", 2025, 11, 20),
    ("FR-WF", "Saint Pierre Chanel", 2024, 4, 28),
    ("FR-WF", "Saints Pierre et Paul", 2024, 6, 29),
    ("FR-WF", "Fête du Territoire", 2024, 7, 29),
    ("FR-WF", "Saint Pierre Chanel", 2025, 4, 28),
    ("FR-WF", "Saints Pierre et Paul", 2025, 6, 29),
    ("FR-WF", "Fête du Territoire", 2025, 7, 29),
]

for _c, _n, _y, _m, _d in IT_SUBDIV_GOLD:
    _country, _subdiv = _c.split("-", 1)
    _reg(_country, _c, _n, _y, _m, _d)

for _c, _n, _y, _m, _d in FR_SUBDIV_GOLD:
    _country, _subdiv = _c.split("-", 1)
    _reg(_country, _c, _n, _y, _m, _d)


def _dateset_for(country, subdiv, year):
    out = {}
    for h in holidays_for(country, year, subdiv=subdiv):
        out.setdefault(h.name, set()).add(h.date)
    return out


@pytest.mark.parametrize("subdiv,name,year,month,day", IT_SUBDIV_GOLD)
def test_it_subdivision_gold(subdiv, name, year, month, day):
    got = _dateset_for("IT", subdiv, year)
    assert AstroDate(year, month, day) in got.get(name, set()), (
        f"IT/{subdiv}/{name!r} {year}: expected {year}-{month:02d}-{day:02d}, "
        f"got {sorted(got.get(name, set()))}")


@pytest.mark.parametrize("subdiv,name,year,month,day", FR_SUBDIV_GOLD)
def test_fr_subdivision_gold(subdiv, name, year, month, day):
    got = _dateset_for("FR", subdiv, year)
    assert AstroDate(year, month, day) in got.get(name, set()), (
        f"FR/{subdiv}/{name!r} {year}: expected {year}-{month:02d}-{day:02d}, "
        f"got {sorted(got.get(name, set()))}")


def test_it_movable_rules_actually_differ_between_years():
    """Guards against a fixed-date miscoding masquerading as movable: every
    nth_weekday/easter subdiv rule in it.tab must resolve to different dates
    in 2024 vs 2025."""
    cal = os.path.join(_DATA_DIR, "it.tab")
    from chronologia.civil_holidays import load_calendar
    calendar = load_calendar(cal)
    movable = [r for r in calendar.rules
               if r.subdiv is not None
               and isinstance(r.kind, (NthWeekdayRule, EasterOffsetRule))]
    assert movable, "expected at least one movable IT subdiv rule"
    for rule in movable:
        d24 = _dateset_for("IT", rule.subdiv, 2024).get(rule.name)
        d25 = _dateset_for("IT", rule.subdiv, 2025).get(rule.name)
        assert d24 and d25 and d24 != d25, (
            f"IT/{rule.subdiv}/{rule.name!r} expected to move year to year, "
            f"got {d24} == {d25}")


def test_fr_pf_autonomy_holiday_valid_range_switches_in_2025():
    pf_2024 = _dateset_for("FR", "FR-PF", 2024)
    pf_2025 = _dateset_for("FR", "FR-PF", 2025)
    assert "Fête de l'autonomie" in pf_2024
    assert "Fête de l'autonomie" not in pf_2025
    assert "Matāri'i" not in pf_2024
    assert "Matāri'i" in pf_2025


def test_it_existing_capital_rows_untouched():
    # The pre-existing, independently-sourced IT-PG patron day is NOT
    # replaced by vacanza's differing entry for the same code.
    pg = {h.name for h in holidays_for("IT", 2024, subdiv="IT-PG")}
    assert "San Costanzo" in pg
    assert "Santa Chiara d'Assisi" not in pg
    assert "San Francesco d'Assisi" not in pg


@pytest.mark.parametrize("country", ["IT", "FR"])
def test_calendar_still_loads_and_has_rules(country):
    from chronologia.civil_holidays import load_calendar
    cal = load_calendar(os.path.join(_DATA_DIR, f"{country.lower()}.tab"))
    assert cal.rules
    assert cal.jurisdiction == country
