"""Compare chronologia with ovos-date-parser 0.29 on the date benches.

    python tools/plot_benchmarks.py <table.tsv>

The input is the per-bench summary TSV of the date bench scorer
(columns bench, side, lang, n, chronologia_correct, odp029_correct, ...).
The script writes docs/benchmarks/odp_vs_chronologia.json,
docs/benchmarks/odp_vs_chronologia.png and the table in docs/benchmarks.md.
"""
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "benchmarks", "odp_vs_chronologia")
PAGE = os.path.join(ROOT, "docs", "benchmarks.md")
START = "<!-- odp-table:start -->"
END = "<!-- odp-table:end -->"
LEADERS = ["pt-PT", "pt-BR", "es", "es-CO", "fr", "it", "de", "nl", "da",
           "kab", "hi", "bn", "mwr"]


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


def table(data):
    lines = ["| Locale | Rows | chronologia | ovos-date-parser 0.29 | Ready |",
             "|:---|---:|---:|---:|:---|"]
    for lang in LEADERS:
        v = data["locales"].get(lang)
        if v is None:
            lines.append(f"| {lang} | 0 | not measured | not measured | not measured |")
        else:
            ready = "yes" if v["ready"] else "no"
            lines.append(f"| {lang} | {v['n']} | {v['chronologia']:.3f} | {v['odp']:.3f} | {ready} |")
    return "\n".join(lines)


def rendered_page(data):
    text = open(PAGE, encoding="utf-8").read()
    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)
    return f"{before}{START}\n{table(data)}\n{END}{after}"


def plot(data, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    shown = [l for l in LEADERS if l in data["locales"]]
    missing = [l for l in LEADERS if l not in data["locales"]]
    fig, ax = plt.subplots(figsize=(8, 0.55 * len(shown) + 1.6), dpi=120)
    y = range(len(shown))
    h = 0.38
    for off, key, label, color in ((-h / 2, "chronologia", "chronologia", "#2a6fdb"),
                                   (h / 2, "odp", "ovos-date-parser 0.29", "#e08a1e")):
        vals = [data["locales"][l][key] for l in shown]
        bars = ax.barh([i + off for i in y], vals, h, label=label, color=color)
        ax.bar_label(bars, labels=[f"{v:.2f}" for v in vals], padding=3, fontsize=8)
    ax.set_yticks(list(y), [f"{l} (n={data['locales'][l]['n']})" for l in shown])
    ax.invert_yaxis()
    ax.set_xlim(0, 1.08)
    ax.set_xlabel("strict correct rate")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="lower right", frameon=False)
    if missing:
        fig.text(0.01, 0.01, "No bench rows: " + ", ".join(missing), fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, metadata={"Software": None})


if __name__ == "__main__":
    data = summarise(sys.argv[1])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT + ".json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    page = rendered_page(data)
    with open(PAGE, "w", encoding="utf-8") as f:
        f.write(page)
    if os.environ.get("DOCS_FIGURES_DATA_ONLY") != "1":
        plot(data, OUT + ".png")
