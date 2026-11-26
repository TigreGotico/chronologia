"""Build the language support table in docs/languages/index.md.

The table comes from two sources: the locale data in chronologia/locale/ and
the test results in docs/languages/support.json.

    python tools/language_support.py measure   # run the test rows, write support.json
    python tools/language_support.py write     # write the table into the index
    python tools/language_support.py check     # exit 1 when the index differs
"""
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALE = os.path.join(ROOT, "chronologia", "locale")
RESULTS = os.path.join(ROOT, "docs", "languages", "support.json")
INDEX = os.path.join(ROOT, "docs", "languages", "index.md")
sys.path.insert(0, ROOT)
START = "<!-- support-table:start -->"
END = "<!-- support-table:end -->"

#: feature -> pattern on the test file name in test/nl_corpus_<code>/
FEATURES = {
    "dates": r"calendar|date|month_day|day_of_month",
    "clock": r"clock|meridiem",
    "durations": r"duration",
    "relative days": r"relative|named_?day|day_word",
    "ranges": r"range",
    "recurrence": r"recurr",
    "holidays": r"holiday|feast",
}
SPOKEN = "spoken"
COLUMNS = list(FEATURES) + [SPOKEN]

#: the language-leader tags, in leader order
LEADERS = [
    ("pt-PT", "Portuguese (Portugal)"), ("pt-BR", "Portuguese (Brazil)"),
    ("es-CO", "Spanish (Colombia)"), ("fr-FR", "French (France)"),
    ("it-IT", "Italian (Italy)"), ("de-DE", "German (Germany)"),
    ("nl-NL", "Dutch (Netherlands)"), ("da-DK", "Danish (Denmark)"),
    ("kab", "Kabyle"), ("hi-IN", "Hindi (India)"),
    ("bn-IN", "Bengali (India)"), ("mwr", "Marwari"),
]
NO_LOCALE_ISSUE = "https://github.com/TigreGotico/chronologia/issues/1484"

NAMES = {
    "sq": "Albanian", "ar": "Arabic", "an": "Aragonese", "hy": "Armenian",
    "ast": "Asturian", "az": "Azerbaijani", "eu": "Basque",
    "be": "Belarusian", "bg": "Bulgarian", "ca": "Catalan", "hr": "Croatian",
    "cs": "Czech", "da": "Danish", "nl": "Dutch", "en": "English",
    "eo": "Esperanto", "et": "Estonian", "fil": "Filipino", "fi": "Finnish",
    "fr": "French", "gl": "Galician", "ka": "Georgian", "de": "German",
    "el": "Greek", "ha": "Hausa", "he": "Hebrew", "hi": "Hindi",
    "hu": "Hungarian", "is": "Icelandic", "id": "Indonesian", "ga": "Irish",
    "it": "Italian", "kab": "Kabyle", "ko": "Korean", "lv": "Latvian",
    "lt": "Lithuanian", "mk": "Macedonian", "ms": "Malay", "mt": "Maltese",
    "mwl": "Mirandese", "nb": "Norwegian Bokmål", "nn": "Norwegian Nynorsk",
    "oc": "Occitan", "fa": "Persian", "pl": "Polish", "pt": "Portuguese",
    "ro": "Romanian", "ru": "Russian", "sr": "Serbian", "sk": "Slovak",
    "sl": "Slovenian", "es": "Spanish", "sw": "Swahili", "sv": "Swedish",
    "ta": "Tamil", "th": "Thai", "tr": "Turkish", "uk": "Ukrainian",
    "vi": "Vietnamese", "cy": "Welsh", "fy": "West Frisian",
}


def locales():
    return sorted(os.path.basename(os.path.dirname(f))
                  for f in glob.glob(os.path.join(LOCALE, "*", "lang.json")))


def test_files(code):
    """{feature: [test file paths]} for one locale."""
    out = {}
    corpus = os.path.join(ROOT, "test", f"nl_corpus_{code}")
    names = sorted(os.listdir(corpus)) if os.path.isdir(corpus) else []
    for feature, pattern in FEATURES.items():
        out[feature] = [os.path.join(corpus, n) for n in names
                        if n.startswith("test_") and n.endswith(".py")
                        and re.search(pattern, n)]
    out[SPOKEN] = sorted(glob.glob(os.path.join(ROOT, "test", f"test_spoken*_{code}.py")))
    return out


def has_data(code, feature, tag):
    """Whether the locale ships the data that the feature reads."""
    folder = os.path.join(LOCALE, code)
    spec = json.load(open(os.path.join(folder, "lang.json"), encoding="utf-8"))
    constructions = spec.get("constructions", {})
    voc = {os.path.basename(f)[:-4] for f in glob.glob(os.path.join(folder, "*.voc"))}
    if feature == "dates":
        return "calendar_date" in constructions and all(
            f"month_{m}" in voc for m in range(1, 13))
    if feature == "clock":
        return "clock_time" in constructions
    if feature == "durations":
        return any(v.startswith("unit_") for v in voc)
    if feature == "relative days":
        return any(v.startswith("named_day_") for v in voc)
    if feature == "ranges":
        return bool(voc & {"marker_from", "marker_to", "marker_between", "marker_until"})
    if feature == "recurrence":
        return "marker_every" in voc or any(v.startswith("marker_freq_") for v in voc)
    if feature == "holidays":
        return "holiday_ref" in constructions
    from chronologia.spoken import writes
    return writes(tag)


def number_reader(code, tag):
    from chronologia.extract.numlayer import NUMTAG_LANGS
    from chronologia.extract.timespan import _REGION_NUMBER_LANG
    if code not in NUMTAG_LANGS:
        hook = json.load(open(os.path.join(LOCALE, code, "lang.json"))).get("hook", "")
        return hook.split(":")[0].rsplit(".", 1)[-1]
    lexicon = _REGION_NUMBER_LANG.get(tag.lower())
    return f"numtag ({lexicon} lexicon)" if lexicon else "numtag"


def measure():
    """Run every mapped test file and write the pass counts to support.json."""
    results = {}
    for code in locales():
        files = test_files(code)
        paths = sorted({p for ps in files.values() for p in ps})
        outcome = {}
        if paths:
            with tempfile.TemporaryDirectory() as tmp:
                xml = os.path.join(tmp, "junit.xml")
                subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                                f"--junitxml={xml}", *paths],
                               cwd=ROOT, stdout=subprocess.DEVNULL, check=False)
                for case in ET.parse(xml).iter("testcase"):
                    module = case.get("classname", "").split(".")
                    name = next(m for m in module if m.startswith("test_")) + ".py"
                    passed = not any(c.tag in ("failure", "error", "skipped") for c in case)
                    p, n = outcome.get(name, (0, 0))
                    outcome[name] = (p + passed, n + 1)
        results[code] = {}
        for feature, ps in files.items():
            counts = [outcome.get(os.path.basename(p), (0, 0)) for p in ps]
            results[code][feature] = [sum(c[0] for c in counts), sum(c[1] for c in counts)]
        print(code, results[code], file=sys.stderr)
    with open(RESULTS, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"{len(results)} locales in, {len(results)} locales written to {RESULTS}")


def cell(code, feature, tag, results):
    passed, rows = results[code][feature]
    data = has_data(code, feature, tag)
    if feature == SPOKEN and not data:
        return "no"
    if data and passed:
        word = "yes"
    elif data or passed:
        word = "partial"
    else:
        word = "no"
    return f"{word} {passed}/{rows}"


def row(name, tag, code, results):
    link = f"[{name}]({code}.md)"
    cells = [cell(code, f, tag, results) for f in COLUMNS]
    return f"| {link} | {tag} | {code} | {number_reader(code, tag)} | " + " | ".join(cells) + " |"


def table():
    results = json.load(open(RESULTS, encoding="utf-8"))
    codes = locales()
    head = "| Language | Tag | Data | Numbers | " + " | ".join(c.capitalize() for c in COLUMNS) + " |"
    lines = [head, "|" + ":---|" * (4 + len(COLUMNS))]
    for tag, name in LEADERS:
        code = tag.split("-")[0]
        if code in codes:
            lines.append(row(name, tag, code, results))
        else:
            gap = " | ".join(["no"] * len(COLUMNS))
            lines.append(f"| {name} | {tag} | none | not supported, see "
                         f"[#1484]({NO_LOCALE_ISSUE}) | {gap} |")
    leader_codes = {t.split("-")[0] for t, _ in LEADERS}
    for code in sorted((c for c in codes if c not in leader_codes), key=NAMES.__getitem__):
        lines.append(row(NAMES[code], code, code, results))
    return "\n".join(lines)


def rendered_index():
    text = open(INDEX, encoding="utf-8").read()
    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)
    return f"{before}{START}\n{table()}\n{END}{after}"


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "check"
    if command == "measure":
        measure()
    elif command == "write":
        text = rendered_index()
        with open(INDEX, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.exit(0 if rendered_index() == open(INDEX, encoding="utf-8").read() else 1)
