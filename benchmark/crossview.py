"""Cross-view harness: one phrase through the four extractors, two trees compared.

Every phrase-like string of every ``test/nl_corpus_<lang>/`` package, plus generated
grids of ordinal, impossible-date and bound phrases, runs through
``extract_timespan``, ``extract_candidates``, ``extract_recurrence`` and
``extract_event`` in default and raise mode at two fixed anchors.  One TSV row
per call holds a normalised result and the call time in microseconds.

    python -m benchmark.crossview run out.tsv [--chunk 0/4] [--lang en,pt]
    python -m benchmark.crossview diff --base base.tsv... --head head.tsv...
    python -m benchmark.crossview disagree out.tsv... [--limit 20]

``run`` writes sorted rows, so two runs of one tree differ only in the time
column.  ``diff`` compares two trees on every column except the time and
reports per-view timing.  ``disagree`` lists phrases whose views contradict
each other on one tree.
"""
from __future__ import annotations

import argparse
import ast
import collections
import glob
import os
import re
import statistics
import sys
from datetime import datetime
from time import perf_counter_ns
from typing import Dict, Iterable, List, Set, Tuple

from chronologia import (extract_candidates, extract_event, extract_recurrence,
                         extract_timespan)
from chronologia.extract.impossible import ImpossibleDateError

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ANCHORS = (datetime(2026, 11, 22, 9, 0), datetime(2017, 6, 27, 13, 4))
MODES = ("none", "raise")
VIEWS = {
    "timespan": extract_timespan,
    "candidates": extract_candidates,
    "recurrence": extract_recurrence,
    "event": extract_event,
}
PARTS = {
    "timespan": ("span", "remainder"),
    "candidates": ("candidates",),
    "recurrence": ("rule", "remainder"),
    "event": ("summary", "span", "duration", "rule", "confidence"),
}
HEADER = ("lang", "text", "view", "mode", "anchor", "result", "micros")

Row = Tuple[str, ...]
Key = Tuple[str, str, str, str, str]

# The phrases the four views read differently.
SEEDS = (
    ("en", "the sixth monday of every month"),
    ("en", "the last business day of every month"),
    ("de", "de jeden Montag von Juni bis August"),
    ("en", "the 3rd weekday of march"),
)

# from, until, between, to, and, every, month pair, weekday pair
BOUND_WORDS = {
    "en": ("from", "until", "between", "to", "and", "every", ("june", "august"), ("monday", "friday")),
    "pt": ("de", "até", "entre", "a", "e", "toda", ("junho", "agosto"), ("segunda-feira", "sexta-feira")),
    "es": ("de", "hasta", "entre", "a", "y", "cada", ("junio", "agosto"), ("lunes", "viernes")),
    "de": ("von", "bis", "zwischen", "bis", "und", "jeden", ("Juni", "August"), ("Montag", "Freitag")),
    "fr": ("de", "jusqu'à", "entre", "à", "et", "chaque", ("juin", "août"), ("lundi", "vendredi")),
    "it": ("da", "fino a", "tra", "a", "e", "ogni", ("giugno", "agosto"), ("lunedì", "venerdì")),
    "nl": ("van", "tot", "tussen", "tot", "en", "elke", ("juni", "augustus"), ("maandag", "vrijdag")),
    "ca": ("de", "fins a", "entre", "a", "i", "cada", ("juny", "agost"), ("dilluns", "divendres")),
    "gl": ("de", "ata", "entre", "a", "e", "cada", ("xuño", "agosto"), ("luns", "venres")),
}

# A third month, apart from the range's two, for the until date of "from A to B until C".
UNTIL_MONTH = {"en": "december", "pt": "dezembro", "es": "diciembre", "de": "Dezember",
               "fr": "décembre", "it": "dicembre", "nl": "december", "ca": "desembre",
               "gl": "decembro"}

# "every day" and a weekday pair written with the locale's abbreviations.
ABBREVIATED_WEEKDAYS = {
    "en": ("every day", ("mon", "fri")),
    "pt": ("todos os dias", ("seg", "sex")),
    "es": ("todos los días", ("lun", "vie")),
    "de": ("jeden Tag", ("Mo", "Fr")),
    "fr": ("tous les jours", ("lun", "ven")),
    "it": ("ogni giorno", ("lun", "ven")),
    "nl": ("elke dag", ("ma", "vr")),
    "ca": ("cada dia", ("dl", "dv")),
    "gl": ("cada día", ("lun", "ven")),
}

# A date range with an inner "de": "from 3 de junho until 5 de agosto".
INNER_DE_RANGES = {"pt": "de 3 de junho até 5 de agosto",
                   "es": "del 3 de junio hasta el 5 de agosto"}

MONTHS = ("january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december")
SPELLED = ("first", "second", "third", "fourth", "fifth", "sixth", "seventh",
           "eighth", "ninth", "tenth")


# URLs, printf-style assert messages, "a,b" parametrize headers, snake_case names
NOT_A_PHRASE = re.compile(r"://|%[rsd]|^\w+(,\w+)+$|^[a-z0-9]+(_[a-z0-9]+)+$")


def _ordinal(n: int) -> str:
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def corpus_inputs() -> Set[Tuple[str, str]]:
    """Every phrase-like string literal in the nl_corpus packages, per language."""
    found = set()
    for path in glob.glob(os.path.join(_REPO_ROOT, "test", "nl_corpus_*", "*.py")):
        lang = os.path.basename(os.path.dirname(path))[len("nl_corpus_"):]
        tree = ast.parse(open(path, encoding="utf-8").read())
        docstrings = {id(node.body[0].value) for node in ast.walk(tree)
                      if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef))
                      and node.body and isinstance(node.body[0], ast.Expr)
                      and isinstance(node.body[0].value, ast.Constant)}
        fragments = {id(part) for node in ast.walk(tree) if isinstance(node, ast.JoinedStr)
                     for part in node.values}
        for node in ast.walk(tree):
            if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and id(node) not in docstrings and id(node) not in fragments
                    and 3 <= len(node.value) <= 90
                    and "\n" not in node.value and "\t" not in node.value
                    and any(ch.isalnum() for ch in node.value)
                    and not NOT_A_PHRASE.search(node.value)):
                found.add((lang, node.value))
    return found


def grid_inputs() -> Set[Tuple[str, str]]:
    found = set(SEEDS)

    ordinals = [_ordinal(n) for n in range(1, 61)] + list(SPELLED) + ["last", "second to last"]
    scopes = ("of every month", "of the month", "of every quarter", "of the quarter",
              "of every year", "of the year", "of march", "of march 2027")
    for ordinal in ordinals:
        for kind in ("monday", "sunday", "weekday", "business day"):
            found.add(("en", f"every {ordinal} {kind}"))
            for scope in scopes:
                found.add(("en", f"the {ordinal} {kind} {scope}"))

    for day in range(29, 33):
        for month in MONTHS:
            for tail in ("", " 2027", " 2028"):
                found.add(("en", f"the {_ordinal(day)} of {month}{tail}"))
            found.add(("en", f"{month} {day}"))
        found.add(("en", f"every {_ordinal(day)} of the month"))
        found.add(("en", f"on the {_ordinal(day)}"))

    for lang, (frm, until, between, to, and_, every, months, weekdays) in BOUND_WORDS.items():
        pairs = (months, weekdays, (f"3 {months[0]}", f"5 {months[0]}"))
        for first, last in pairs:
            bounds = (f"{frm} {first} {until} {last}", f"{frm} {first} {to} {last}",
                      f"{between} {first} {and_} {last}", f"{first} {to} {last}",
                      f"{until} {last}", f"{frm} {first}")
            for bound in bounds:
                found.add((lang, bound))
                for weekday in weekdays:
                    found.add((lang, f"{every} {weekday} {bound}"))
        for bound in (f"{frm} {months[0]} {to} {months[1]} {until} {UNTIL_MONTH[lang]}",
                      f"{frm} 2027 {until} 2030"):
            found.add((lang, bound))
            for weekday in weekdays:
                found.add((lang, f"{every} {weekday} {bound}"))

        every_day, (first_day, last_day) = ABBREVIATED_WEEKDAYS[lang]
        for connector in (to, until):
            bound = f"{frm} {first_day} {connector} {last_day}"
            found.add((lang, bound))
            found.add((lang, f"{every_day} {bound}"))
            for weekday in weekdays:
                found.add((lang, f"{every} {weekday} {bound}"))
        if lang in INNER_DE_RANGES:
            found.add((lang, INNER_DE_RANGES[lang]))
            for weekday in weekdays:
                found.add((lang, f"{every} {weekday} {INNER_DE_RANGES[lang]}"))
    return found


def span_text(span) -> str:
    return f"{span.start}/{span.end} {span.basis}"


def normalise(view: str, result) -> str:
    """One line per result; fields in PARTS order joined by ' | '."""
    if view == "candidates":
        return " ; ".join(f"{span_text(c.span)} | {c.remainder} | {c.construction} | {c.confidence:.4f}"
                          for c in result) or "[]"
    if result is None:
        return "none"
    if view == "timespan":
        return f"{span_text(result.span)} | {result.remainder}"
    if view == "recurrence":
        return f"{result.recurrence} | {result.remainder}"
    return " | ".join((result.summary, span_text(result.span), str(result.duration),
                       str(result.recurrence), f"{result.confidence:.4f}"))


def call(view: str, text: str, lang: str, anchor: datetime, mode: str) -> Tuple[str, int]:
    start = perf_counter_ns()
    try:
        out = normalise(view, VIEWS[view](text, lang, anchor, impossible=mode))
    except ImpossibleDateError as err:
        out = f"raise {err.reason} | {err.lang} | {err.text}"
    except Exception as err:
        out = f"error {type(err).__name__} {err}"
    return out.replace("\t", " ").replace("\n", " "), (perf_counter_ns() - start) // 1000


def run(inputs: Iterable[Tuple[str, str]], anchors=ANCHORS) -> List[Row]:
    rows = []
    warm = set()
    for lang, text in sorted(inputs):
        if lang not in warm:
            warm.add(lang)
            for view in VIEWS:
                call(view, "today", lang, anchors[0], "none")
        for anchor in anchors:
            for view in VIEWS:
                for mode in MODES:
                    out, micros = call(view, text, lang, anchor, mode)
                    rows.append((lang, text, view, mode, anchor.strftime("%Y-%m-%dT%H:%M"),
                                 out, str(micros)))
    return sorted(rows, key=lambda row: row[:5])


def read_rows(paths: List[str]) -> List[Row]:
    rows = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            next(f)
            rows += [tuple(line.rstrip("\n").split("\t")) for line in f]
    return sorted(rows, key=lambda row: row[:5])


def write_rows(path: str, rows: List[Row]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("\t".join(HEADER) + "\n")
        f.writelines("\t".join(row) + "\n" for row in rows)


def kind(result: str) -> str:
    if result in ("none", "[]"):
        return result
    return result.split(" ", 1)[0] if result.startswith(("raise ", "error ")) else "read"


def change_class(view: str, before: str, after: str) -> str:
    a, b = kind(before), kind(after)
    if a == "read" and b == "read":
        parts = (before.split(" | ") if view != "candidates" else [before],
                 after.split(" | ") if view != "candidates" else [after])
        names = [name for name, x, y in zip(PARTS[view], *parts) if x != y]
        return "read>read " + "+".join(names)
    return f"{a}>{b}"


def percentile(values: List[int], q: float) -> int:
    return sorted(values)[min(len(values) - 1, int(q * len(values)))]


def timing(rows: List[Row]) -> Dict[str, List[int]]:
    per_view = collections.defaultdict(list)
    for row in rows:
        per_view[row[2]].append(int(row[6]))
    return per_view


def diff(base: List[Row], head: List[Row], limit: int) -> int:
    """Print the comparison; return how many rows changed, are missing or are duplicated."""
    before = {row[:5]: row[5] for row in base}
    after = {row[:5]: row[5] for row in head}
    print(f"{len(base)} in, {len(head)} out")
    duplicates = (len(base) - len(before)) + (len(head) - len(after))
    if duplicates:
        print(f"{len(base) - len(before)} duplicate keys in base, {len(head) - len(after)} in head")
    only_base, only_head = sorted(before.keys() - after.keys()), sorted(after.keys() - before.keys())
    for name, keys in (("base", only_base), ("head", only_head)):
        if keys:
            print(f"{len(keys)} rows only in {name}")
            for key in keys[:limit or None]:
                print(f"  {key}")
    changed = collections.defaultdict(list)
    for key in sorted(before.keys() & after.keys()):
        if before[key] != after[key]:
            view = key[2]
            changed[(view, key[3], change_class(view, before[key], after[key]))].append(key)
    total = sum(map(len, changed.values()))
    print(f"{total} changed rows")
    for (view, mode, cls), keys in sorted(changed.items()):
        print(f"\n{view} {mode} {cls}: {len(keys)}")
        for key in keys[:limit or None]:
            print(f"  {key[0]}\t{key[1]}\t{key[4]}\n    base: {before[key]}\n    head: {after[key]}")
    print("\nmicroseconds per call: median / p95")
    base_times, head_times = timing(base), timing(head)
    for view in VIEWS:
        if view in base_times and view in head_times:
            print(f"  {view:<11} base {statistics.median(base_times[view]):.0f} / {percentile(base_times[view], .95)}"
                  f"   head {statistics.median(head_times[view]):.0f} / {percentile(head_times[view], .95)}")
    return total + len(only_base) + len(only_head) + duplicates


def words(text: str) -> Set[str]:
    return {word.strip(".,;:!?\"'()").lower() for word in text.split()} - {""}


def left_over(result: str) -> Set[str]:
    """Words a timespan or recurrence reading leaves unclaimed."""
    return words(result.split(" | ")[-1])


def disagreements(rows: List[Row]) -> Dict[str, List[Key]]:
    """Group phrases by the way their views contradict each other."""
    cells = collections.defaultdict(dict)
    for lang, text, view, mode, anchor, result, _ in rows:
        cells[(lang, text, anchor)][(view, mode)] = result
    found = collections.defaultdict(list)
    for (lang, text, anchor), cell in sorted(cells.items()):
        span, cands = cell.get(("timespan", "none"), "none"), cell.get(("candidates", "none"), "[]")
        rule, event = cell.get(("recurrence", "none"), "none"), cell.get(("event", "none"), "none")
        rule_raise = cell.get(("recurrence", "raise"), "none")
        reasons = {cell[(view, "raise")] for view in VIEWS
                   if kind(cell.get((view, "raise"), "")) == "raise"}
        classes = []
        if kind(span) == "read":
            if kind(rule_raise) == "raise":
                classes.append("timespan reads, recurrence refuses with a reason")
            if cands == "[]":
                classes.append("timespan reads, candidates empty")
            if kind(event) == "none":
                classes.append("timespan reads, event none")
        elif kind(cands) == "read":
            classes.append("candidates read, timespan none")
        if kind(span) == "read" and kind(rule) == "read":
            only_span, only_rule = left_over(span) - left_over(rule), left_over(rule) - left_over(span)
            if only_span and only_rule:
                classes.append("timespan and rule each leave words the other claims")
            elif len(only_span) >= 2:
                classes.append("timespan leaves 2+ words the rule claims")
            elif len(only_rule) >= 2:
                classes.append("rule leaves 2+ words the timespan claims")
        if kind(rule) == "read" and kind(span) == "none" and cands == "[]" and len(left_over(rule)) >= 2:
            classes.append("rule leaves 2+ words, timespan and candidates read nothing")
        if len(reasons) > 1:
            classes.append("views refuse with different reasons")
        for name in classes:
            found[name].append((lang, text, anchor))
    return found


def report(found: Dict[str, List[Key]], limit: int) -> None:
    for name, keys in sorted(found.items()):
        print(f"{name}: {len(keys)}")
        for lang, text, anchor in keys[:limit or None]:
            print(f"  {lang}\t{text}\t{anchor}")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run_cmd = sub.add_parser("run", help="write the TSV for this tree")
    run_cmd.add_argument("out")
    run_cmd.add_argument("--chunk", default="0/1", help="i/n: run every n-th input from i")
    run_cmd.add_argument("--lang", help="comma-separated languages to keep")
    diff_cmd = sub.add_parser("diff", help="compare two trees")
    diff_cmd.add_argument("--base", nargs="+", required=True)
    diff_cmd.add_argument("--head", nargs="+", required=True)
    diff_cmd.add_argument("--limit", type=int, default=5, help="examples per class, 0 for all")
    disagree_cmd = sub.add_parser("disagree", help="list cross-view contradictions")
    disagree_cmd.add_argument("tsv", nargs="+")
    disagree_cmd.add_argument("--limit", type=int, default=20, help="examples per class, 0 for all")
    args = parser.parse_args(argv)

    if args.command == "run":
        index, total = map(int, args.chunk.split("/"))
        inputs = sorted(corpus_inputs() | grid_inputs())
        if args.lang:
            langs = args.lang.split(",")
            inputs = [item for item in inputs if item[0] in langs]
        mine = inputs[index::total]
        write_rows(args.out, run(mine))
        print(f"{len(mine)} inputs, {len(mine) * len(ANCHORS) * len(VIEWS) * len(MODES)} rows -> {args.out}")
    elif args.command == "diff":
        sys.exit(1 if diff(read_rows(args.base), read_rows(args.head), args.limit) else 0)
    else:
        report(disagreements(read_rows(args.tsv)), args.limit)


if __name__ == "__main__":
    main()
