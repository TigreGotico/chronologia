"""The package loads its heavy submodules on first use, not on import."""
import importlib
import subprocess
import sys

import chronologia

HEAVY = ("eras", "civil_holidays", "mars", "luna", "cosmology", "moon", "ical")


def _loaded_after(statement: str) -> set:
    code = (f"import sys; {statement}; "
            f"print(*[m for m in sys.modules if m.startswith('chronologia.')])")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True,
                         text=True, check=True).stdout
    return set(out.split())


def test_import_skips_heavy_modules():
    loaded = _loaded_after("import chronologia")
    for name in HEAVY:
        assert f"chronologia.{name}" not in loaded, name


def test_extractor_import_skips_calendar_extras():
    loaded = _loaded_after("from chronologia.extract import extract_timespan")
    for name in ("eras", "mars", "luna", "cosmology", "moon", "ical"):
        assert f"chronologia.{name}" not in loaded, name


def test_first_access_loads_the_module():
    loaded = _loaded_after("import chronologia; chronologia.ERAS")
    assert "chronologia.eras" in loaded


def test_every_exported_name_is_the_defining_modules_object():
    assert set(chronologia.__all__) == set(chronologia._MODULE_OF)
    for name, module in chronologia._MODULE_OF.items():
        defined = getattr(importlib.import_module(module), name)
        assert getattr(chronologia, name) is defined, name


def test_dir_lists_every_exported_name():
    assert set(chronologia.__all__) <= set(dir(chronologia))


def test_prayer_times_is_the_function():
    from chronologia.prayer_times import PrayerTimes  # noqa: F401
    assert callable(chronologia.prayer_times)
