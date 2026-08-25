#!/usr/bin/env python
"""Coverage differential: chronologia's shipped catalog vs vacanza/holidays.

House rule: benchmark, don't assert. This script never fails a build; it asks
the ``vacanza/holidays`` package which countries and financial markets it
supports and reports which of them chronologia's ``holiday_data/*.tab`` catalog
has no file, alias, or documented exclusion for. Comparing library against
library needs the other library installed, so this lives here rather than in
the test suite, and it reports and exits when the package is absent.

Run it directly for a printed report::

    python benchmark/catalog_coverage.py
"""
from __future__ import annotations

import os
import sys

from chronologia.civil_holidays import MARKET_ALIASES, _DATA_DIR

#: Codes vacanza supports (as an ISO-3166-1 alpha-2 "country") that are
#: deliberately not filed as their own ``.tab`` — with the reason each is
#: excluded: every vacanza alpha-2 country code should be either shipped as a
#: ``.tab`` file or listed here with a reason.
COUNTRY_SKIP_LIST = {
    "UA": "national holiday calendar suspended/altered under martial law "
          "since 2022 (batch-4 decision, still in force)",
    "UK": "bare vacanza alias for GB -- holidays.country_holidays('UK', ...) "
          "and holidays.country_holidays('GB', ...) return an identical "
          "date/name mapping; not a distinct jurisdiction",
    "BV": "Bouvet Island: uninhabited, no statutory holiday calendar "
          "(empty vacanza output for 2024-2025)",
    "HM": "Heard Island and McDonald Islands: uninhabited, no statutory "
          "holiday calendar (empty vacanza output for 2024-2025)",
    "IO": "British Indian Ocean Territory: no permanent population, no "
          "statutory holiday calendar (empty vacanza output for 2024-2025)",
}

#: Financial-market codes deliberately not filed and not aliased, with the
#: reason each is excluded. Same allowlist discipline as COUNTRY_SKIP_LIST.
MARKET_SKIP_LIST = {}


def shipped():
    """Jurisdiction codes with a shipped ``.tab`` file."""
    return {f[:-4].upper() for f in os.listdir(_DATA_DIR) if f.endswith(".tab")}


def country_coverage(pkg):
    """(uncovered, overlap) for vacanza's alpha-2 country list."""
    supported = {c for c in pkg.list_supported_countries() if len(c) == 2}
    have = shipped()
    return (sorted(supported - have - set(COUNTRY_SKIP_LIST)),
            sorted(have & set(COUNTRY_SKIP_LIST)))


def market_coverage(pkg):
    """(uncovered, overlap) for vacanza's financial-market list."""
    supported = set(pkg.list_supported_financial())
    have = shipped()
    covered = have | set(MARKET_ALIASES) | set(MARKET_SKIP_LIST)
    return (sorted(supported - covered),
            sorted(set(MARKET_SKIP_LIST) & (have | set(MARKET_ALIASES))))


def _report(title, uncovered, overlap):
    lines = [f"\n[{title}]"]
    lines.append(f"  uncovered ({len(uncovered)}): {uncovered or 'none'}")
    if overlap:
        lines.append(f"  skip-listed but already covered: {overlap}")
    return "\n".join(lines)


def main():
    try:
        import holidays as pkg
    except ImportError:
        print("holidays (vacanza) is not installed -- nothing to compare "
              "against; install it to run this coverage differential.")
        return 0
    print("chronologia x holidays catalog coverage")
    print("=" * 40)
    print(_report("countries", *country_coverage(pkg)))
    print(_report("financial markets", *market_coverage(pkg)))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
