"""A civil-holidays .tab file declares its schema version, and the loader gates
it: an unrecognised version fails loudly instead of being silently mis-parsed
after a future format change."""
import pytest

from chronologia.civil_holidays.loader import load_calendar

_GOOD = """# civil-holidays v1
# jurisdiction: ZZ
# source: https://example.org/holidays
# retrieved: 2026-01-01
fixed | New Year | 1 1 | public
"""

_BAD = _GOOD.replace("# civil-holidays v1", "# civil-holidays v99")


def test_supported_version_loads(tmp_path):
    p = tmp_path / "zz.tab"
    p.write_text(_GOOD, encoding="utf-8")
    cal = load_calendar(str(p))
    assert any(r.name == "New Year" for r in cal.rules)


def test_unsupported_version_is_a_load_error(tmp_path):
    p = tmp_path / "zz.tab"
    p.write_text(_BAD, encoding="utf-8")
    with pytest.raises(ValueError, match="unsupported civil-holidays schema version"):
        load_calendar(str(p))
