"""02 — The same question in many languages.

Run it with::

    python examples/02_languages.py

The extractor is not English-only. Each language ships its own small
**vocabulary** file (the words for "tomorrow", the month names, how ordinals
are written), and the same engine reads them all. The date logic underneath is
shared, so "tomorrow" in French and "tomorrow" in Arabic land on the very same
day.

A **locale** is that pairing of a language with its regional conventions; you
pass it as a short code — ``"en"``, ``"es"``, ``"ar"``. **RTL** means a
right-to-left script (Arabic, Hebrew); it is handled exactly like any other —
the words differ, the answer does not.
"""
from datetime import datetime

from chronologia import extract_timespan

anchor = datetime(2024, 1, 1)  # a fixed "now" so "tomorrow" is reproducible

# "tomorrow" written in eight languages, two of them right-to-left.
tomorrow_in = [
    ("en", "tomorrow"),
    ("es", "mañana"),
    ("fr", "demain"),
    ("de", "morgen"),
    ("pt", "amanhã"),
    ("ru", "завтра"),   # Cyrillic
    ("ar", "غدا"),      # Arabic — right-to-left
    ("he", "מחר"),      # Hebrew — right-to-left
]

print("'tomorrow', anchored at 2024-01-01:\n")
for lang, phrase in tomorrow_in:
    span, _ = extract_timespan(phrase, lang, anchor)
    got = span.start_datetime.date().isoformat()
    print(f"  {lang:3} {phrase:10} -> {got}")
    # Every language must agree: tomorrow is 2024-01-02.
    assert got == "2024-01-02", (lang, got)

# Month names are localised too — Spanish "marzo" is the same month as
# English "March".
es, _ = extract_timespan("marzo de 2024", "es", anchor)
en, _ = extract_timespan("March 2024", "en", anchor)
assert es.start_datetime.date() == en.start_datetime.date() == datetime(2024, 3, 1).date()
print("\n'marzo de 2024' == 'March 2024' ->", es.start_datetime.date())

print("\nOK — one engine, many vocabularies, one shared answer.")
