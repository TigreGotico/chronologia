#!/usr/bin/env python
"""Standing differential benchmark: chronologia vs dateparser vs dateutil.

House rule: benchmark, don't assert -- this script never fails a build; it
*measures* three independent-ish natural-language date engines against the
same hand-derived gold set (the repo's own ``test/nl_corpus_*`` corpora, see
``benchmark/adapter.py``) and prints/writes an honest per-language,
per-engine scoreboard, including any category where a competitor wins.

Usage::

    python benchmark/run.py                    # full run, all corpora
    python benchmark/run.py --langs en de ar    # restrict to some languages
    python benchmark/run.py --sample 50 --seed 0  # fast smoke sample
    python benchmark/run.py --out benchmark/SCOREBOARD.md

Each gold case is a ``(text, expected_date)`` pair anchored at a fixed
"now" (the corpus's own ``ANCHOR``).  Each engine is scored per case as
exactly one of:

* **exact** -- the engine's parsed date equals ``expected_date``;
* **no-parse** -- the engine returned nothing (``None`` / empty);
* **wrong** -- the engine returned a date but it does not match.

dateparser and dateutil parse to a plain ``datetime``; chronologia's
``extract_timespan`` returns a :class:`~chronologia.astrodate.DateSpan`, so
per the house rule ("competitors emit datetimes -- score against
span.start date") chronologia is scored on ``span.start.date()``.
"""
from __future__ import annotations

import argparse
import random
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Tuple

sys.path.insert(0, __file__.rsplit("/benchmark/", 1)[0])

from benchmark.adapter import GoldCase, collect_gold_cases  # noqa: E402

ENGINES = ("chronologia", "dateparser", "dateutil")


def _score_chronologia(case: GoldCase) -> str:
    from chronologia import extract_timespan
    try:
        r = extract_timespan(case.text, case.lang, case.anchor)
    except Exception:
        return "wrong"  # a raised exception is a wrong-parse, never a crash
    if r is None:
        return "no-parse"
    span, _remainder = r
    got = span.start
    try:
        got_date = got.date() if hasattr(got, "date") else got
    except Exception:
        return "wrong"
    return "exact" if got_date == case.expected else "wrong"


def _score_dateparser(case: GoldCase) -> str:
    import dateparser
    try:
        got = dateparser.parse(
            case.text,
            languages=[case.lang] if _dateparser_supports(case.lang) else None,
            settings={"RELATIVE_BASE": case.anchor},
        )
    except Exception:
        return "wrong"
    if got is None:
        return "no-parse"
    return "exact" if got.date() == case.expected else "wrong"


_DATEPARSER_LOCALES = None


def _dateparser_supports(lang: str) -> bool:
    global _DATEPARSER_LOCALES
    if _DATEPARSER_LOCALES is None:
        try:
            from dateparser.languages.loader import LocaleDataLoader
            _DATEPARSER_LOCALES = set(LocaleDataLoader().get_locale_map().keys())
        except Exception:
            _DATEPARSER_LOCALES = set()
    return lang in _DATEPARSER_LOCALES


def _score_dateutil(case: GoldCase) -> str:
    from dateutil import parser as du_parser
    try:
        got = du_parser.parse(case.text, default=case.anchor, fuzzy=True)
    except Exception:
        return "no-parse"
    return "exact" if got.date() == case.expected else "wrong"


_SCORERS = {
    "chronologia": _score_chronologia,
    "dateparser": _score_dateparser,
    "dateutil": _score_dateutil,
}


def run_benchmark(cases: List[GoldCase]) -> Dict[Tuple[str, str], Dict[str, int]]:
    """Return ``{(lang, engine): {"exact": n, "no-parse": n, "wrong": n}}``."""
    tallies: Dict[Tuple[str, str], Dict[str, int]] = defaultdict(
        lambda: {"exact": 0, "no-parse": 0, "wrong": 0})
    for case in cases:
        for engine, scorer in _SCORERS.items():
            outcome = scorer(case)
            tallies[(case.lang, engine)][outcome] += 1
    return tallies


def render_scoreboard(cases: List[GoldCase],
                      tallies: Dict[Tuple[str, str], Dict[str, int]],
                      generation_cmd: str) -> str:
    langs = sorted({c.lang for c in cases})
    n_total = len(cases)
    lines = [
        "# Differential benchmark scoreboard",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"Gold cases: {n_total} hand-derived `(text, expected_date)` pairs "
        f"across {len(langs)} languages, pulled live from the repo's own "
        "`test/nl_corpus_*` corpora (see `benchmark/adapter.py`) -- "
        "independent of all three engines under test.",
        "",
        f"Generation command: `{generation_cmd}`",
        "",
        "House rule: **benchmark, don't assert.** This is a snapshot, not a "
        "gate; nothing here fails CI. Competitors emit plain `datetime`s, so "
        "every engine is scored against the gold case's exact expected "
        "*date* (chronologia's result is reduced to `span.start.date()`).",
        "",
        "Outcome key: **exact** = parsed date matches gold; **no-parse** = "
        "engine returned nothing; **wrong** = engine returned a date that "
        "does not match.",
        "",
    ]

    lines.append("## Per-language accuracy (exact-match %)")
    lines.append("")
    header = "| lang | n | " + " | ".join(ENGINES) + " |"
    sep = "|---|---|" + "---|" * len(ENGINES)
    lines.append(header)
    lines.append(sep)
    overall = {e: {"exact": 0, "no-parse": 0, "wrong": 0} for e in ENGINES}
    for lang in langs:
        n = sum(1 for c in cases if c.lang == lang)
        row = [lang, str(n)]
        for engine in ENGINES:
            t = tallies[(lang, engine)]
            for k in overall[engine]:
                overall[engine][k] += t[k]
            pct = 100.0 * t["exact"] / n if n else 0.0
            row.append(f"{pct:.0f}% ({t['exact']}/{n})")
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append("## Overall (all languages combined)")
    lines.append("")
    lines.append("| engine | exact | no-parse | wrong | accuracy |")
    lines.append("|---|---|---|---|---|")
    for engine in ENGINES:
        t = overall[engine]
        acc = 100.0 * t["exact"] / n_total if n_total else 0.0
        lines.append(
            f"| {engine} | {t['exact']} | {t['no-parse']} | {t['wrong']} | "
            f"{acc:.1f}% |")

    lines.append("")
    lines.append("## Honest notes")
    lines.append("")
    winners = []
    for lang in langs:
        best_engine, best_pct = None, -1.0
        n = sum(1 for c in cases if c.lang == lang)
        for engine in ENGINES:
            pct = 100.0 * tallies[(lang, engine)]["exact"] / n if n else 0.0
            if pct > best_pct:
                best_engine, best_pct = engine, pct
        if best_engine != "chronologia":
            winners.append((lang, best_engine, best_pct))
    if winners:
        lines.append("Languages where a competitor's exact-match rate beats "
                      "chronologia's on this gold set:")
        lines.append("")
        for lang, engine, pct in winners:
            lines.append(f"- **{lang}**: `{engine}` leads ({pct:.0f}% exact)")
    else:
        lines.append("chronologia leads (or ties) exact-match accuracy on "
                      "every language in this run.")
    lines.append("")
    lines.append("Caveats: dateparser/dateutil are general-purpose date "
                  "parsers, not span-native (they collapse a phrase to its "
                  "left edge datetime, never a width); this benchmark only "
                  "credits the start-of-span comparison chronologia's own "
                  "spec calls for, so it necessarily understates what "
                  "chronologia additionally returns (the end of the span, "
                  "resolution, calendar metadata) that the competitors "
                  "cannot represent at all.")
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--langs", nargs="*", default=None,
                    help="restrict to these chronologia locale codes")
    ap.add_argument("--sample", type=int, default=None,
                    help="randomly sample this many gold cases (fast smoke)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None,
                    help="write the rendered scoreboard to this path")
    args = ap.parse_args(argv)

    t0 = time.time()
    cases = collect_gold_cases(args.langs)
    if args.sample is not None and args.sample < len(cases):
        rng = random.Random(args.seed)
        cases = rng.sample(cases, args.sample)

    tallies = run_benchmark(cases)
    cmd = "python benchmark/run.py" + (
        f" --langs {' '.join(args.langs)}" if args.langs else "")
    report = render_scoreboard(cases, tallies, cmd)
    print(report)
    print(f"[{len(cases)} cases scored in {time.time() - t0:.1f}s]",
          file=sys.stderr)

    if args.out:
        with open(args.out, "w") as f:
            f.write(report)
        print(f"[written to {args.out}]", file=sys.stderr)


if __name__ == "__main__":
    main()
