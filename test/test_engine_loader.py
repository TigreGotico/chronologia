"""Loader: filename-encoded slot values and lang.json facts."""
import json

import pytest
from engine_helpers import load_zz

from chronologia.extract import load_lang_spec


def test_months_carry_numbers():
    spec = load_zz()
    assert spec.months["zjun"] == 6 and spec.months["zdec"] == 12


def test_weekday_index_monday_zero():
    assert load_zz().weekdays["zmon"] == 0


def test_units_carry_kind():
    spec = load_zz()
    assert spec.units["zweek"] == "week" and spec.units["zyears"] == "year"


def test_named_day_offsets_signed():
    nd = load_zz().named_days
    assert nd["ztoday"] == 0 and nd["zmorrow"] == 1 and nd["zyester"] == -1


def test_direction_signs():
    spec = load_zz()
    assert spec.directions["zago"] == -1 and spec.directions["zhence"] == 1


def test_rel_marker_values():
    spec = load_zz()
    assert (spec.rel_markers["znext"], spec.rel_markers["zlast"],
            spec.rel_markers["zthis"]) == (1, -1, 0)


def test_connector_named_by_suffix():
    assert "zof" in load_zz().connectors["of"]


def test_json_facts_loaded():
    spec = load_zz()
    assert spec.tokenizer.split_contractions and spec.tokenizer.ordinal_dot
    assert spec.lemmas["zwochen"] == "zweek"
    assert ("-aren", "") in spec.suffix_strip
    assert spec.construction_flags["calendar_date"]["prefer_future"] is True
    assert "relative_offset" in spec.orders and spec.hook is None


# -- calendar-month vocab (month_<calendar>_<n>.voc) -----------------------

def test_calendar_months_parsed_and_keyed_by_calendar():
    cm = load_zz().calendar_months
    assert cm["islamic_civil"]["zram"] == 9 and cm["islamic_civil"]["zmuh"] == 1


def test_gregorian_months_unaffected_by_calendar_months():
    # the z-nonsense gregorian months keep their own numbering
    assert load_zz().months["zjun"] == 6


def _write_locale(root, files, cfg=None):
    d = root / "xx"
    d.mkdir()
    for name, body in files.items():
        (d / name).write_text(body, encoding="utf-8")
    (d / "lang.json").write_text(json.dumps(cfg or {}), encoding="utf-8")
    return str(root)


def test_unknown_calendar_key_is_a_load_error(tmp_path):
    root = _write_locale(tmp_path, {"month_klingon_1.voc": "qeng\n"})
    with pytest.raises(ValueError, match="unknown calendar"):
        load_lang_spec("xx", root)


def test_cross_calendar_surface_collision_is_a_load_error(tmp_path):
    root = _write_locale(tmp_path, {
        "month_islamic_civil_9.voc": "clash\n",
        "month_hebrew_7.voc": "clash\n"})
    with pytest.raises(ValueError, match="claimed by both calendars"):
        load_lang_spec("xx", root)


def test_gregorian_month_out_of_range_is_a_load_error(tmp_path):
    root = _write_locale(tmp_path, {"month_13.voc": "zmonth\n"})
    with pytest.raises(ValueError, match="month number 13 out of range 1..12"):
        load_lang_spec("xx", root)


def test_weekday_out_of_range_is_a_load_error(tmp_path):
    root = _write_locale(tmp_path, {"weekday_7.voc": "zday\n"})
    with pytest.raises(ValueError, match="weekday index 7 out of range 0..6"):
        load_lang_spec("xx", root)


def test_calendar_month_out_of_range_is_a_load_error(tmp_path):
    # hebrew has 13 months; month 14 is impossible and must fail loudly.
    root = _write_locale(tmp_path, {"month_hebrew_14.voc": "zadar\n"})
    with pytest.raises(ValueError, match="out of range 1..13"):
        load_lang_spec("xx", root)


def test_calendar_month_at_upper_bound_loads(tmp_path):
    # hebrew month 13 (Adar II) is legitimate and must NOT be rejected.
    root = _write_locale(tmp_path, {"month_hebrew_13.voc": "zadar2\n"})
    spec = load_lang_spec("xx", root)
    assert spec.calendar_months["hebrew"]["zadar2"] == 13
