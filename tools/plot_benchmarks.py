"""Compare chronologia with ovos-date-parser 0.29 on the date benches.

    python tools/plot_benchmarks.py <table.tsv>

The input is the per-bench summary TSV of the date bench scorer
(columns bench, side, lang, n, chronologia_correct, odp029_correct, ...).
The script writes docs/benchmarks/odp_vs_chronologia.json, the figure
docs/img/odp_vs_chronologia{.json,.svg,-dark.svg}, and the figure and the
table between the odp-table markers in docs/benchmarks.md.
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "img"))
from plot_style import save  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "benchmarks", "odp_vs_chronologia")
FIGURE = os.path.join(ROOT, "docs", "img", "odp_vs_chronologia")
PAGE = os.path.join(ROOT, "docs", "benchmarks.md")
START = "<!-- odp-table:start -->"
END = "<!-- odp-table:end -->"
#: (leader tag, bench locale or None, locale data code)
LEADERS = [
    ("pt-PT", "pt-PT", "pt"), ("pt-BR", "pt-BR", "pt"), ("es-CO", None, "es"),
    ("fr-FR", "fr", "fr"), ("it-IT", "it", "it"), ("de-DE", "de", "de"),
    ("nl-NL", "nl", "nl"), ("da-DK", "da", "da"), ("kab", "kab", "kab"),
    ("hi-IN", "hi", "hi"), ("bn-IN", None, None), ("mwr", None, None),
]
#: bench rows without a region tag, shown next to the leader they relate to
EXTRA = {"es-CO": ("es", "es")}


def rows():
    for tag, bench, code in LEADERS:
        yield tag, bench, code
        if tag in EXTRA:
            yield "", *EXTRA[tag]


def bench_label(tag, bench):
    if bench is None:
        return "none"
    return bench if bench == tag or "-" in bench else f"{bench} (rows with no region tag)"


def summarise(path):
    with open(path, encoding="utf-8") as f:
        first = f.readline()
        header = first.lstrip("# ").strip() if first.startswith("#") else None
        f.seek(0)
        rows = list(csv.DictReader((l for l in f if not l.startswith("#")), delimiter="\t"))
    langs = {}
    for r in rows:
        bench = langs.setdefault(r["lang"], {}).setdefault(
            r["bench"], {"n": 0, "chronologia": 0, "odp": 0})
        bench["n"] += int(r["n"])
        bench["chronologia"] += int(r["chronologia_correct"])
        bench["odp"] += int(r["odp029_correct"])
    out = {}
    for lang, benches in sorted(langs.items()):
        n = sum(b["n"] for b in benches.values())
        out[lang] = {
            "n": n,
            "chronologia": round(sum(b["chronologia"] for b in benches.values()) / n, 3),
            "odp": round(sum(b["odp"] for b in benches.values()) / n, 3),
            "ready": all(b["chronologia"] >= b["odp"] for b in benches.values()),
            "benches": benches,
        }
    print(f"{len(rows)} rows in, {len(out)} locales out", file=sys.stderr)
    return {"source": header, "locales": out}


def figure_data(data):
    return [{"label": f"{tag or bench} \u00b7 {bench}" if tag and tag != bench else bench,
             "n": data["locales"][bench]["n"],
             "chronologia": data["locales"][bench]["chronologia"],
             "odp": data["locales"][bench]["odp"]}
            for tag, bench, _ in rows() if bench in data["locales"]]


def alt(fig):
    gaps = sorted(fig, key=lambda r: r["chronologia"] - r["odp"])
    lo, hi = gaps[0], gaps[-1]
    wins = sum(r["chronologia"] > r["odp"] for r in fig)
    return (f"Strict correct rate per leader locale: chronologia is higher than "
            f"ovos-date-parser 0.29 in {wins} of {len(fig)} measured bench locales; "
            f"largest gap {hi['label']} {hi['chronologia']:.2f} against {hi['odp']:.2f}, "
            f"smallest gap {lo['label']} {lo['chronologia']:.2f} against {lo['odp']:.2f}.")


def table(data):
    lines = ["| Leader tag | Bench rows | Locale data | Rows | chronologia | ovos-date-parser 0.29 | Ready |",
             "|:---|:---|:---|---:|---:|---:|:---|"]
    for tag, bench, code in rows():
        v = data["locales"].get(bench)
        if v is None:
            lines.append(f"| {tag} | {bench_label(tag, bench)} | {code or 'none'} | 0 "
                         "| not measured | not measured | not measured |")
        else:
            ready = "yes" if v["ready"] else "no"
            lines.append(f"| {tag} | {bench_label(tag, bench)} | {code} | {v['n']} "
                         f"| {v['chronologia']:.3f} | {v['odp']:.3f} | {ready} |")
    return "\n".join(lines)


def block(data):
    picture = ("<picture>\n"
               '  <source media="(prefers-color-scheme: dark)" srcset="img/odp_vs_chronologia-dark.svg">\n'
               f'  <img alt="{alt(figure_data(data))}" src="img/odp_vs_chronologia.svg">\n'
               "</picture>")
    return f"{picture}\n\n{table(data)}"


def rendered_page(data):
    text = open(PAGE, encoding="utf-8").read()
    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)
    return f"{before}{START}\n{block(data)}\n{END}{after}"


def draw(fig, theme, rows):
    ax = fig.subplots()
    y = range(len(rows))
    h = 0.38
    for i, (key, label) in enumerate((("chronologia", "chronologia"),
                                      ("odp", "ovos-date-parser 0.29"))):
        vals = [r[key] for r in rows]
        bars = ax.barh([j + (i - 0.5) * h for j in y], vals, h, label=label,
                       color=theme["series"][i])
        ax.bar_label(bars, labels=[f"{v:.2f}" for v in vals], padding=3, fontsize=8,
                     color=theme["text"])
    ax.set_yticks(list(y), [f"{r['label']} (n={r['n']})" for r in rows])
    ax.invert_yaxis()
    ax.set_xlim(0, 1.1)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("strict correct rate")
    ax.legend(loc="lower right")


if __name__ == "__main__":
    data = summarise(sys.argv[1])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT + ".json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    page = rendered_page(data)
    with open(PAGE, "w", encoding="utf-8") as f:
        f.write(page)
    fig = figure_data(data)
    save(FIGURE, draw, fig, height=0.5 * len(fig) + 1.0)
