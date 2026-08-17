"""Differential harness: chronologia's calendar math vs the ``holidays`` DB.

Two independent implementations of the same astronomy are the strongest test
either one gets.  chronologia computes feast anchors by converting off its JDN
hub; ``vacanza/holidays`` computes the *same* anchors from its own, unrelated
code.  Where they agree we gain confidence in both; where they diverge we get
a *lead* — a dated disagreement worth a human look — and this harness never
"fixes" one library to match the other, it only reports.

Four axes, each with a different expectation:

* **Easter / computus** — chronologia's computus lives on a parallel branch not
  present here, so this axis is a documented placeholder (see
  :func:`easter_differential`).  Wire it up once ``chronologia.computus`` lands.
* **Islamic** (Eid al-Fitr / al-Adha vs Saudi Arabia and others) — arithmetic
  calendars are *expected* to sit 1-2 days off a country's *observed* date,
  because observation depends on a moon sighting.  The harness therefore
  reports the **offset distribution** and only flags an outlier ``|offset| > 2``
  as a lead.
* **Hebrew** (Rosh Hashanah vs Israel) — the Hebrew calendar is fully
  arithmetic on both sides; exact agreement is expected.
* **Chinese** (Spring Festival, within chronologia's tabulated 1901-2099 range)
  — a fixed astronomical table on both sides; **any** mismatch is a lead.

Run it directly for a printed report::

    python benchmark/holiday_differential.py
"""
from __future__ import annotations

import collections
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional, Tuple

from chronologia import CALENDARS


@dataclass
class AxisResult:
    """Outcome for one differential axis."""

    axis: str
    years_tested: int
    exact_agreements: int = 0
    offset_distribution: Dict[int, int] = field(default_factory=dict)
    leads: List[Tuple] = field(default_factory=list)
    note: str = ""


# --- Islamic ---------------------------------------------------------------

def _islamic_anchor(cal, greg_year: int, month: int, day: int) -> Optional[date]:
    """chronologia's ``month``/``day`` anchor that lands in ``greg_year``.

    Sweeps the three plausible Hijri years so the returned civil date falls in
    the target Gregorian year's first half (where Eid al-Fitr sits early-year
    for the far-future window ``holidays`` estimates).
    """
    approx_hy = greg_year - 579
    for cand in (approx_hy - 1, approx_hy, approx_hy + 1):
        try:
            anchor = cal.date(cand, month, day).date()
        except Exception:
            continue
        if anchor.year == greg_year:
            return anchor
    return None


def islamic_differential(years=range(2015, 2031), country="SA",
                         calendar_key="umm_al_qura") -> AxisResult:
    """Eid al-Fitr (1 Shawwal) vs a country's *observed* Eid al-Fitr.

    Offsets are observance-vs-arithmetic and expected within +/-2 days; only
    ``|offset| > 2`` is recorded as a lead.
    """
    import holidays

    cal = CALENDARS[calendar_key]
    dist = collections.Counter()
    leads = []
    tested = 0
    res = AxisResult(axis=f"islamic:{calendar_key}:Eid-al-Fitr:{country}",
                     years_tested=0)
    for y in years:
        obj = holidays.country_holidays(country, years=y, language="en_US")
        observed = sorted(d for d, n in obj.items()
                          if n == "Eid al-Fitr Holiday" or n == "Eid al-Fitr")
        if not observed:
            continue
        ours = _islamic_anchor(cal, y, 10, 1)  # 1 Shawwal
        if ours is None:
            continue
        tested += 1
        offset = (ours - observed[0]).days
        dist[offset] += 1
        if abs(offset) > 2:
            leads.append((y, ours, observed[0], offset))
    res.years_tested = tested
    res.offset_distribution = dict(sorted(dist.items()))
    res.leads = leads
    res.note = ("arithmetic vs observed sighting; +/-1-2 day spread is normal, "
                "|offset|>2 flagged")
    return res


# --- Hebrew ----------------------------------------------------------------

def hebrew_differential(years=range(2015, 2031)) -> AxisResult:
    """Rosh Hashanah (1 Tishrei) vs Israel's Rosh Hashanah. Exact expected."""
    import holidays

    cal = CALENDARS["hebrew"]
    dist = collections.Counter()
    leads = []
    exact = 0
    tested = 0
    for y in years:
        obj = holidays.country_holidays("IL", years=y, language="en_US")
        observed = sorted(d for d, n in obj.items() if n == "Rosh Hashanah")
        if not observed:
            continue
        hy = y + 3761
        ours = cal.date(hy, 7, 1).date()  # 1 Tishrei
        tested += 1
        offset = (ours - observed[0]).days
        dist[offset] += 1
        if offset == 0:
            exact += 1
        else:
            leads.append((y, ours, observed[0], offset))
    return AxisResult(
        axis="hebrew:Rosh-Hashanah:IL", years_tested=tested,
        exact_agreements=exact, offset_distribution=dict(sorted(dist.items())),
        leads=leads, note="both sides arithmetic; exact agreement expected")


# --- Chinese ---------------------------------------------------------------

def chinese_differential(years=range(1970, 2036)) -> AxisResult:
    """Spring Festival vs China's Chinese New Year. Any mismatch is a lead."""
    import holidays

    cal = CALENDARS["chinese"]
    dist = collections.Counter()
    leads = []
    exact = 0
    tested = 0
    for y in years:
        obj = holidays.country_holidays("CN", years=y, language="en_US")
        observed = sorted(d for d, n in obj.items()
                          if n == "Chinese New Year (Spring Festival)")
        if not observed:
            continue
        ours = cal.date(y, 1, 1).date()  # chinese 1-1 == Spring Festival day
        tested += 1
        offset = (ours - observed[0]).days
        dist[offset] += 1
        if offset == 0:
            exact += 1
        else:
            leads.append((y, ours, observed[0], offset))
    return AxisResult(
        axis="chinese:Spring-Festival:CN", years_tested=tested,
        exact_agreements=exact, offset_distribution=dict(sorted(dist.items())),
        leads=leads,
        note="tabulated 1901-2099 both sides; ANY mismatch is a lead")


# --- Easter (placeholder) --------------------------------------------------

def easter_differential(years=range(2015, 2031)) -> AxisResult:
    """Placeholder: chronologia.computus is not present on this branch.

    Once a computus lands, compare ``easter(y)`` against
    ``holidays.country_holidays(...)`` Easter Sunday for a Western-rite country
    (e.g. ``DE``) and an Orthodox-rite one, expecting exact agreement per rite.
    """
    return AxisResult(
        axis="easter:computus", years_tested=0,
        note="SKIPPED: chronologia.computus absent on this branch")


def run_differential() -> Dict[str, AxisResult]:
    """Run every axis and return the results keyed by axis name."""
    axes = [
        easter_differential(),
        islamic_differential(calendar_key="umm_al_qura"),
        islamic_differential(calendar_key="islamic_civil"),
        hebrew_differential(),
        chinese_differential(),
    ]
    return {a.axis: a for a in axes}


def _format(results: Dict[str, AxisResult]) -> str:
    lines = ["chronologia x holidays differential", "=" * 40]
    for a in results.values():
        lines.append(f"\n[{a.axis}]  years={a.years_tested}")
        if a.note:
            lines.append(f"  note: {a.note}")
        if a.offset_distribution:
            lines.append(f"  offset distribution (days): {a.offset_distribution}")
        if a.exact_agreements:
            lines.append(f"  exact agreements: {a.exact_agreements}"
                         f"/{a.years_tested}")
        if a.leads:
            lines.append(f"  LEADS ({len(a.leads)}):")
            for lead in a.leads:
                lines.append(f"    {lead}")
        elif a.years_tested:
            lines.append("  leads: none")
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(_format(run_differential()))
