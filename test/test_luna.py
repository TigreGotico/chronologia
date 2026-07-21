"""Lunar time: the natural cycle registered, the civil LTC standard withheld."""
from datetime import date

import pytest

from chronologia.astrodate import AstroDate
from chronologia.axes import AXES
from chronologia.moon import EPOCH_NEW_MOON, MEAN_SYNODIC_MONTH_DAYS
from chronologia.luna import (LTC_DRIFT_MICROSECONDS_PER_DAY, LTC_STATUS,
                              LUNAR_DAY_SECONDS, LunarTimeStandardStatus,
                              ltc_offset)


def test_lunar_axis_registered():
    assert "lunar" in AXES
    axis = AXES["lunar"]
    assert axis.key == "lunar"


def test_lunar_day_equals_mean_synodic_month():
    # tidally locked: the lunar solar day == one mean synodic month
    assert LUNAR_DAY_SECONDS == MEAN_SYNODIC_MONTH_DAYS * 86400.0
    assert AXES["lunar"].unit_seconds == LUNAR_DAY_SECONDS


def test_lunar_axis_epoch_is_lunation_zero():
    assert AXES["lunar"].epoch_tt == EPOCH_NEW_MOON


def test_lunar_axis_counts_one_unit_per_lunation():
    # one lunar day after the epoch new moon is count 1.0
    one_later = AXES["lunar"].tt_from_count(1.0)
    assert abs(AXES["lunar"].count_from_tt(one_later) - 1.0) < 1e-9
    # and it is ~29.53 Earth days after the epoch
    days = (one_later._total_us() - EPOCH_NEW_MOON._total_us()) / 86_400_000_000
    assert abs(days - MEAN_SYNODIC_MONTH_DAYS) < 1e-6


def test_drift_constant_cited_value():
    # the downloaded source figure is 58.7 microseconds per Earth-day
    assert LTC_DRIFT_MICROSECONDS_PER_DAY == 58.7


def test_ltc_status_fields():
    assert isinstance(LTC_STATUS, LunarTimeStandardStatus)
    assert LTC_STATUS.key == "coordinated_lunar_time"
    assert LTC_STATUS.name == "Coordinated Lunar Time"
    assert LTC_STATUS.status == "mandated_unpublished"
    assert LTC_STATUS.mandate_date == date(2024, 4, 2)
    assert LTC_STATUS.drift_microseconds_per_day == LTC_DRIFT_MICROSECONDS_PER_DAY
    assert "OSTP" in LTC_STATUS.mandate
    assert "wikipedia" in LTC_STATUS.source.lower()


def test_ltc_status_is_frozen():
    with pytest.raises(Exception):
        LTC_STATUS.status = "published"  # type: ignore[misc]


def test_ltc_offset_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        ltc_offset(AstroDate(2030, 1, 1))


def test_ltc_offset_message_names_standard_and_source():
    with pytest.raises(NotImplementedError) as exc:
        ltc_offset(AstroDate(2030, 1, 1))
    msg = str(exc.value)
    assert "Coordinated Lunar Time" in msg
    assert "mandated" in msg
    assert "not yet published" in msg
    assert "58.7" in msg              # the cited drift figure
    assert "Source:" in msg           # points at the citation


def test_ltc_offset_raises_for_datetime_and_date_too():
    from datetime import datetime
    for value in (datetime(2030, 1, 1), date(2030, 1, 1)):
        with pytest.raises(NotImplementedError):
            ltc_offset(value)
