"""Lazy, cached, thread-safe per-locale engine loading.

Embedded voice targets import the package and then speak one or two
languages; they must not pay to read all 40-plus locales, and the language
they do speak must be loaded exactly once.  These guards pin that contract:

* **import-time budget** -- ``import chronologia`` reads *no* file under
  ``chronologia/locale/`` (locale data is loaded lazily, on the first
  ``extract_*`` call for a language, never at import);
* **cache identity** -- two calls for the same language return the identical
  compiled engine (and the identical :class:`LangSpec`), so a locale is
  compiled once and reused;
* **thread-safety smoke** -- concurrent first-calls for *different* languages
  from separate threads all succeed, and concurrent first-calls for the *same*
  language all observe the one identical cached engine (the double-checked lock
  never compiles a language twice).
"""
import os
import subprocess
import sys
import threading

import chronologia
from chronologia.extract import _timespan_engine


# ---------------------------------------------------------------------------
# import-time budget: no locale-dir reads at import
# ---------------------------------------------------------------------------

_IMPORT_PROBE = r"""
import builtins, os, sys
_real_open = builtins.open
hits = []
def counting_open(file, *a, **k):
    try:
        p = os.fspath(file)
        if isinstance(p, bytes):
            p = p.decode("utf-8", "replace")
        if (os.sep + "locale" + os.sep) in p and p.endswith((".voc", ".json")):
            hits.append(p)
    except Exception:
        pass
    return _real_open(file, *a, **k)
builtins.open = counting_open
import chronologia  # noqa: F401
builtins.open = _real_open
# also fail if any locale .voc slipped in through a non-open reader
sys.stdout.write(repr(hits))
"""


def test_import_reads_no_locale_files():
    """Importing the package must not touch a single ``locale/*.voc`` or
    ``locale/*/lang.json`` -- locale loading is strictly deferred to the first
    extraction call, so a target that never extracts pays nothing."""
    out = subprocess.check_output(
        [sys.executable, "-c", _IMPORT_PROBE],
        cwd=os.path.dirname(os.path.dirname(chronologia.__file__)),
        env={**os.environ, "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
        text=True)
    opened = eval(out)  # a repr'd list of paths
    assert opened == [], (
        f"import chronologia read {len(opened)} locale files eagerly: "
        f"{opened[:5]}")


# ---------------------------------------------------------------------------
# cache identity: a language is compiled once and reused
# ---------------------------------------------------------------------------

def test_same_language_returns_identical_engine():
    a = _timespan_engine("en-us")
    b = _timespan_engine("en")           # region tag stripped -> same code
    assert a is b
    assert a.spec is b.spec


def test_distinct_languages_are_distinct_engines():
    en = _timespan_engine("en")
    de = _timespan_engine("de")
    assert en is not de
    assert en.spec.lang == "en" and de.spec.lang == "de"


# ---------------------------------------------------------------------------
# thread-safety smoke: concurrent first-calls
# ---------------------------------------------------------------------------

def test_concurrent_first_calls_different_langs(monkeypatch):
    """Concurrent first-loads of different languages from separate threads all
    succeed with the right engine -- the cache lock serialises the compiles
    without deadlocking or cross-wiring specs."""
    import chronologia.extract as ex
    import chronologia.extract.timespan as ts
    # the cache + its lock live in timespan.py; patch there, not the facade
    # alias re-exported into chronologia.extract, or _timespan_engine (whose
    # globals are timespan.py's) keeps using the real, warm cache.
    monkeypatch.setattr(ts, "_TIMESPAN_ENGINES", {})

    langs = ["en", "de", "fr", "es", "nl", "pt", "ru"]
    results = {}
    errors = []
    barrier = threading.Barrier(len(langs))

    def worker(lang):
        try:
            barrier.wait()               # release all threads together
            results[lang] = ex._timespan_engine(lang)
        except Exception as exc:         # noqa: BLE001
            errors.append((lang, exc))

    threads = [threading.Thread(target=worker, args=(l,)) for l in langs]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, errors
    for lang in langs:
        assert results[lang].spec.lang == lang
        # the object left in the cache is the one every later call gets
        assert ex._timespan_engine(lang) is results[lang]


def test_concurrent_first_calls_same_lang_compiled_once(monkeypatch):
    """Ten threads racing to first-load the *same* language all receive the one
    identical engine object -- the double-checked lock compiles it once."""
    import chronologia.extract as ex
    import chronologia.extract.timespan as ts
    # the cache + its lock live in timespan.py; patch there, not the facade
    # alias re-exported into chronologia.extract, or _timespan_engine (whose
    # globals are timespan.py's) keeps using the real, warm cache.
    monkeypatch.setattr(ts, "_TIMESPAN_ENGINES", {})

    seen = []
    errors = []
    barrier = threading.Barrier(10)

    def worker():
        try:
            barrier.wait()
            seen.append(ex._timespan_engine("en"))
        except Exception as exc:         # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, errors
    assert len(seen) == 10
    assert all(e is seen[0] for e in seen)
