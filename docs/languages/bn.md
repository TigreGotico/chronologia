# Bengali (`bn`)

<!-- agent-hint
covers: where each word of the Bengali locale comes from, what it refuses and which questions a native speaker must settle
source: chronologia/locale/bn/lang.json, chronologia/locale/bn/*.voc, test/nl_corpus_bn/
generated: no
verify: .venv/bin/python -m doctest docs/languages/bn.md
see: docs/languages/index.md, docs/languages/hi.md
-->

This page records where each construction of the Bengali (`bn`) locale comes from and which words it refuses. numtag reads the number words and the Bengali digits ০-৯.

The locale refuses the bare words কাল and পরশু. Each one names a day in two directions: কাল is "tomorrow" or "yesterday", and পরশু is two days forward or back. Only the tense of the verb tells the direction, and chronologia does not read verbs. The one-direction forms আগামীকাল, গতকাল, আগামী পরশু and গত পরশু resolve.

## Try it

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('তিন দিন আগে', "bn", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-24T00:05:00', '')
    >>> span, rest = extract_timespan('আজ রাত নটায়', "bn", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat()
    '2017-06-27T21:00:00'
    >>> extract_timespan('কাল', "bn", datetime(2017, 6, 27, 0, 5)) is None
    True

## What ships

| Item | Source |
| :--- | :--- |
| Months, weekdays | Unicode CLDR 47, `common/main/bn.xml`, gregorian wide and abbreviated names |
| আজ, আগামীকাল, গতকাল, আগামী পরশু, গত পরশু | CLDR 47, day relative types 0, 1, -1, 2, -2 |
| আজকে, গতপরশু | H.-R. Thompson, *Bengali* (2012), time adverbials |
| Day periods ভোর, সকাল, দুপুর, বিকাল, সন্ধ্যা, রাত্রি and the -বেলায় forms | CLDR 47 dayPeriods and Day Period Rules |
| রাত, বিকালবেলা | Samsad Bengali-English Dictionary, p. 911 and p. 751 |
| পরে, আগে, থেকে, পর্যন্ত, আগামী, প্রতি | Thompson (2012) |
| পরের, গত, এই, পূর্বে | CLDR 47 relative-time names and patterns |
| The hour classifier -টা, -টায়, -টার, and বাজে | Thompson (2012): "tinta baje three oclock", "aj sokale noytay" |
| সাড়ে, সোয়া, পৌনে, দেড়, আড়াই | Thompson (2012), Appendix II |
| পয়লা, দোসরা, তেসরা, পাঁচই, বিশে, একুশে | Samsad, pp. 614, 522, 469, 632, 772, 183 |

The classifier -টা also counts things ("দুটো আম", two mangoes). So a bare number with -টা is a clock time only with a fraction word before it or বাজে after it. The locative -টায় ("পাঁচটায়", at five) is always a clock time.

The indefinite এক before a day part ("শীতের এক সকালে", one winter morning) names no day, and the phrase gets no reading.

## Open questions

Issue #1484 asks a native speaker these questions. Until the answers come, the locale does not read these forms:

- bare কাল and পরশু (refused);
- বিকেল and the clipped forms ন'টা and ছ'টা, which have no Bengali-script source yet;
- "N দিনের মধ্যে" ("within" or "after exactly");
- আগামী or পরের before a weekday: the coming one or the one of next week. The bare weekday rule reads the coming one;
- the range "X থেকে Y পর্যন্ত".

---
[← Belarusian](be.md) · [Home](../index.md) · [Bulgarian →](bg.md)
