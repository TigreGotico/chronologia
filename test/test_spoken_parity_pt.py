"""pt-PT writer parity with ovos-date-parser on a fixed grid.

Each difference is listed in DIFFERENCES with the cited reason, so the
parity holds on every other cell.
"""
import pytest

from chronologia import spoken

odp = pytest.importorskip("ovos_date_parser.spoken")

TAG = "pt-PT"
DAYS = (1, 2, 21, 31)
YEARS = (1900, 2000, 2024, 2100)
MINUTES = (0, 1, 15, 30, 45)
TIME_OPTIONS = [
    dict(),
    dict(style="units"),
    dict(clock="12h"),
    dict(clock="12h", period=True),
    dict(style="units", clock="12h", period=True),
    dict(style="phrase", clock="12h"),
    dict(style="phrase", clock="12h", period=True),
]

# Cells where chronologia gives a different reading, with the reason.
DIFFERENCES = {}


def _cells():
    for month in range(1, 13):
        yield "date", dict(month=month)
        for day in DAYS:
            for year in (None,) + YEARS:
                try:
                    odp._check_date(day, month, year, None)
                except ValueError:
                    continue
                yield "date", dict(day=day, month=month, year=year)
    for year in YEARS:
        yield "year", dict(year=year)
    for hour in range(24):
        for minute in MINUTES:
            for options in TIME_OPTIONS:
                yield "time", dict(hour=hour, minute=minute, **options)


CELLS = list(_cells())


def _read(module, kind, fields):
    if kind == "date":
        return module.spoken_date(TAG, **fields)
    if kind == "year":
        return module.spoken_year(TAG, fields["year"])
    return module.spoken_time(TAG, **fields)


def _key(kind, fields):
    return kind, tuple(sorted(fields.items()))


@pytest.mark.parametrize("kind,fields", CELLS,
                         ids=[f"{k}-{f}" for k, f in CELLS])
def test_parity(kind, fields):
    expected = _read(odp, kind, fields)
    got = _read(spoken, kind, fields)
    reason = DIFFERENCES.get(_key(kind, fields))
    if reason:
        assert got != expected, f"listed difference is gone: {reason}"
    else:
        assert got == expected


def test_grid_size():
    # day 31 does not exist in five months
    assert len(CELLS) == 12 + 12 * 4 * 5 - 5 * 5 + 4 + 24 * 5 * 7
