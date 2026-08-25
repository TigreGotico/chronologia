# -*- coding: utf-8 -*-
"""The built artefact is what users get -- test *that*, not the source tree.

Every other test here imports ``chronologia`` from the working directory (or an
editable install pointing at it), so a package that exists on disk always
imports.  A wheel ships only what packaging was *told* to ship.  When
``civil_holidays`` was split from a module into a package, the hand-written
``packages`` list was not updated; the wheel shipped without it; and since
``chronologia/__init__.py`` imports from it, the whole library became
unimportable once installed -- while every other test stayed green.

Two guards, deliberately different in kind:

* :func:`test_declaration_covers_every_package` reads what ``pyproject.toml``
  actually declares and compares it against what is on disk.  No build, no
  subprocess -- it fails in milliseconds and names the missing package.
* the wheel tests build a real artefact and use it from a clean interpreter,
  which is the only way to catch a break that lives outside the declaration.

The wheel tests remove ``build/`` first, on purpose: ``python -m build
--no-isolation`` *reuses* a stale ``build/lib``, which will happily re-ship a
package the current configuration no longer includes and hide the very bug
these tests exist to catch.
"""
import shutil
import subprocess
import sys
import sysconfig
import zipfile
from pathlib import Path

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:                                       # tomllib entered the stdlib in 3.11
    import tomli as tomllib

_REPO_ROOT = Path(__file__).resolve().parent.parent
_PKG_ROOT = _REPO_ROOT / "chronologia"


def _packages_on_disk():
    """Every importable subpackage physically present under ``chronologia/``."""
    found = {"chronologia"}
    for init in _PKG_ROOT.rglob("__init__.py"):
        found.add(".".join(init.parent.relative_to(_REPO_ROOT).parts))
    return found


def _packages_declared():
    """What ``pyproject.toml`` tells the backend to ship.

    Handles both spellings: an explicit ``packages`` list, and automatic
    discovery via ``[tool.setuptools.packages.find]``.
    """
    with open(_REPO_ROOT / "pyproject.toml", "rb") as fh:
        cfg = tomllib.load(fh)
    tool = cfg.get("tool", {}).get("setuptools", {})
    packages = tool.get("packages")
    if isinstance(packages, list):          # hand-written list
        return set(packages)
    from setuptools import find_packages
    find_cfg = {}
    if isinstance(packages, dict):          # [tool.setuptools.packages.find]
        find_cfg = packages.get("find", {})
    find_cfg = find_cfg or tool.get("packages", {}).get("find", {}) or {}
    return set(find_packages(
        str(_REPO_ROOT),
        include=find_cfg.get("include", ("*",)),
        exclude=find_cfg.get("exclude", ()),
    ))


def test_declaration_covers_every_package():
    """A subpackage on disk that the declaration misses ships broken.

    This reads ``pyproject.toml`` itself rather than re-running discovery, so
    it fails when someone hand-lists packages and then adds a new one.
    """
    missing = _packages_on_disk() - _packages_declared()
    assert not missing, (
        f"present on disk but not declared in pyproject.toml: {sorted(missing)} "
        f"-- these would be omitted from the wheel, and any of them imported by "
        f"chronologia/__init__.py would make the installed library unimportable"
    )


#: Build leftovers that make a build lie about the current configuration.
_STALE = shutil.ignore_patterns("build", "*.egg-info", "__pycache__", ".git",
                                ".pytest_cache", "dist", "test", "benchmark")


@pytest.fixture(scope="module")
def built_wheel(tmp_path_factory):
    """Build a real wheel from a pristine copy of the source tree.

    The copy is the whole point.  ``python -m build --no-isolation`` reuses
    both ``build/lib`` and ``*.egg-info/SOURCES.txt``, either of which will
    re-ship a package the current configuration no longer includes -- so
    building in place can report success for a wheel that is already broken.
    Copying is cheap next to the build itself, and unlike deleting those
    directories it cannot disturb a developer's editable install.
    """
    src = tmp_path_factory.mktemp("src") / "chronologia-src"
    shutil.copytree(_REPO_ROOT, src, ignore=_STALE, symlinks=True)
    out = tmp_path_factory.mktemp("wheel")
    proc = subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--no-isolation",
         "--outdir", str(out), str(src)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, f"wheel build failed:\n{proc.stdout}\n{proc.stderr}"
    wheels = list(out.glob("*.whl"))
    assert len(wheels) == 1, f"expected exactly one wheel, got {wheels}"
    return wheels[0]


def test_wheel_contains_every_package(built_wheel):
    """Each package on disk contributes at least its ``__init__`` to the wheel."""
    with zipfile.ZipFile(built_wheel) as zf:
        names = set(zf.namelist())
    for pkg in sorted(_packages_on_disk()):
        expected = pkg.replace(".", "/") + "/__init__.py"
        assert expected in names, f"{pkg} is missing from the wheel ({expected})"


def test_wheel_carries_the_locale_and_holiday_data(built_wheel):
    """The data trees *are* the library; a wheel without them parses nothing."""
    with zipfile.ZipFile(built_wheel) as zf:
        names = zf.namelist()
    # Ratios, not exact counts: this must not need editing every time a locale
    # or a jurisdiction is added.
    assert sum(n.endswith(".voc") for n in names) > 1000
    assert sum(n.endswith(".tab") for n in names) > 100
    assert sum(n.endswith("lang.json") for n in names) > 30


def test_installed_wheel_imports_and_parses(built_wheel, tmp_path):
    """Unpack the wheel somewhere clean and use it as a user would.

    Importing is what regressed before, but an import that succeeds while the
    data files are missing would still be useless, so this also resolves a date
    and reaches into the holiday package through the unpacked copy.
    """
    site = tmp_path / "site"
    with zipfile.ZipFile(built_wheel) as zf:
        zf.extractall(site)

    script = (
        f"site = {str(site)!r}\n"
        "import chronologia\n"
        # Prove which copy answered before trusting anything it says.
        "assert chronologia.__file__.startswith(site), (\n"
        "    'loaded %s, not the unpacked wheel at %s' % (chronologia.__file__, site))\n"
        "import chronologia.civil_holidays as ch\n"
        "assert ch.__file__.startswith(site), ch.__file__\n"
        "assert ch.CATEGORIES\n"
        "from chronologia.extract import extract_timespan\n"
        "from datetime import datetime\n"
        "r = extract_timespan('5 March 2024', anchor=datetime(2017, 6, 27))\n"
        "assert r is not None and r.span.start.year == 2024, r\n"
        "print('OK')\n"
    )
    # site-packages must stay reachable -- the real dependencies live there,
    # several of them as editable installs of their own.  That also means this
    # repo's editable hook is live and will inject the working copy into
    # ``chronologia.__path__``, serving submodules from source while the
    # top-level package comes from the wheel.  Hence the provenance assertions
    # in the script above: they are what make this test fail on a wheel that
    # is missing a package, rather than silently borrowing it from disk.
    env = {
        "PATH": "/usr/bin:/bin",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTHONPATH": f"{site}:{sysconfig.get_paths()['purelib']}",
    }
    proc = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True, cwd=str(tmp_path), env=env,
    )
    assert proc.returncode == 0, (
        f"the built wheel is not usable once installed:\n"
        f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}"
    )
    assert "OK" in proc.stdout
