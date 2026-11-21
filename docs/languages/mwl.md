# Mirandese (`mwl`)

<!-- agent-hint
covers: where each construction of the Mirandese locale comes from, what it refuses and which questions a native speaker would settle
source: `chronologia/locale/mwl/lang.json`, `chronologia/locale/mwl/*.voc`, `chronologia/extract/numlayer.py:NUMTAG_LANGS`
generated: no
verify: python -m doctest docs/languages/mwl.md && python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set()\nfor m in re.finditer(r\"`([^`]+)`[^.`\\n]{0,25}?\\b(?:is|are|reads|gives|=)\\s+(\\d\\d):(\\d\\d)\",pr):\n    ph=m[1]\n    if ph[0]==\"-\" or not re.search(r\"[^\\W\\d_]\",ph): continue\n    r=extract_timespan(ph,c,A)\n    if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2],m[3])\npm=re.sub(r\"`[^`]*`\",lambda m:m[0].replace(\". \",\".\\x01\"),pr)\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(r\"((?:`[^`]+`(?:,| and| or|, and)? ?)+)\\s*(?:both |each |all )?(?:returns?|gives?) (?:nothing|`None`)\",s): cl|=set(x.replace(\"\\x01\",\" \") for x in re.findall(r\"`([^`]+)`\",m[1]))\nex={ast.literal_eval(x) for x in re.findall(r\">>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\",t)}\nif cl!=ex: bad=1;print(\"refusals differ\",cl^ex)\nsys.exit(bad)\n")' docs/languages/mwl.md
see: `docs/languages/index.md`, `docs/extraction.md`
-->

This page records where each construction of the Mirandese (`mwl`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Mirandese is an Asturleonese language spoken in north-eastern Portugal, and it
is surrounded on every side by Portuguese. Many of its time words are spelled
exactly as Portuguese spells them — `janeiro`, `abril`, `maio`, `agosto`,
`sábado` — and many others differ by one letter, which is precisely how a
Portuguese surface slips into a Mirandese locale unnoticed. Every group below
was therefore confirmed in Mirandese text: the Mirandese Wikipedia
(Biquipédia), or the Mirandese sections of the English Wiktionary, which cite
Moisés Pires' *Pequeno vocabulário Mirandês-Português*.

The words that mark the language are the ones to check first. The week is
`sumana`, not *semana*. The day is `die`, not *dia*. The year is `anho`, not
*ano*. The century is `seclo`. Yesterday is `onte` and today is `hoije`.

## What ships

**Months.** Twelve are confirmed in Biquipédia running text in date phrases:
`janeiro`, `febreiro`, `márcio`, `abril`, `maio`, `júnio`, `júlio`, `agosto`,
`setembre`, `outubre`, `nobembre`, `dezembre`. `márcio` needed care, since it
is also a common Portuguese given name; the check used the date frame `de
Márcio` rather than the bare word, and that frame is well represented.

**Weekdays.** `segunda-feira` through `sesta-feira` and `demingo` all occur in
Biquipédia. The locale ships them unhyphenated because the tokenizer shears the
hyphen, so both writings reach the same surface. `sesta-feira` with an *s* is
the Mirandese form and the one that occurs; the Portuguese *sexta* is not the
spelling here.

**The date line** is `15 de janeiro de 2020`, day-first, with an optional
leading article. The article file lists `l`, `la`, `ls`, `las` and `lo` — the
Asturleonese *l*-articles, not the Portuguese *o*/`a` ones.

**Named days.** `hoije`, `onte`, `manhana` and `trasdonte` each have a
Mirandese Wiktionary entry. `hoije` is sourced there to Pires' vocabulary;
`trasdonte` is derived as *trás* + *de* + *onte*, literally "behind yesterday".

**Relative offsets.** The past takes `hai`, `fai` or the trailing `atrás`; the
future takes `an`, `déntro` or `dentro`. Both directions work with a digit or a
spelled count: `hai trés dies`, `déntro de trés dies`, `trés sumanas atrás`.

**The clock.** Minutes are added with `e` and subtracted with `menos`: `a las
trés e meia` is 03:30, `a las trés menos quarto` is 02:45. The half is `meia`
or `meio` and the quarter is `quarto`.

**Century and decade.** `seclo` is taken from Biquipédia running text — the
article titled *Seclo XX*, and the sentence in *Lhéngua mirandesa* that reads
"nun eirie para alhá de ls anhos 80 de l seclo XX". It has no Mirandese
Wiktionary entry; the English Wiktionary page for `seclo` carries a Latin
section only. `década` and `decada` come from Biquipédia category titles
(*Catadorie:Década de 1850*, *Catadorie:Década de 2000*); both the accented and
unaccented spellings ship, because Mirandese writing does not mark this accent
consistently. All four page titles exist.

**The decade frame** is `ls anhos 80`. Only the plural `anhos` reaches the
decade slot, so a singular `anho` cannot be misread as a decade. `anho` has a
Mirandese Wiktionary entry, from Old Leonese, from Latin *annus*.

**Markers.** `apuis` and its variants for "after", `antes` for "before", `zde`
and `desde` for "since", `até` and `ata` for "until", `cada` and `todos` for
"every", `agora` for the present, `que ben` for the coming period and
`passado` or `redadeiro` for the past one.

## Weaker provenance

**`sumana`** occurs freely in Biquipédia but has no Mirandese Wiktionary entry,
so the week rests on corpus attestation alone.

**`onte`** was found only a handful of times in Biquipédia. Its Wiktionary
entry is solid — from Old Galician-Portuguese, ultimately Latin *ad noctem* —
so the word is not in doubt, but the corpus support for it is thin.

**`manhana` for tomorrow.** The locale ships it as the named day one ahead. The
Mirandese Wiktionary entry gives it only as the feminine noun "morning", from
Vulgar Latin \**maneana*, and Biquipédia's occurrences are dominated by the
newspaper name *Correio de la Manhana*, which is the morning sense. Both
readings are ordinary in the neighbouring Romance languages; the locale commits
to one of them without a source that separates the two.

## What refuses

**Noon and midnight.** The locale ships no clock landmark at all, so `meidie`
and `meia-nuite` return nothing. Both are attested in Biquipédia text, so this
is a gap in coverage rather than a decision about the language.

**Dayparts and the twelve-hour clock.** There is no morning, afternoon, evening
or night meridiem in this locale either, so an hour cannot be pushed into the
afternoon by naming the part of day.

**Roman-numeral centuries.** `l seclo XX` returns nothing, although that is how
Biquipédia writes it.

**A trailing "before" or "after" on an offset.** `trés dies antes` and `trés
dies apuis` both return nothing.

**A bare duration.** `trés horas` and `meia hora` return nothing.

## Known defects

These are wrong or lossy outputs, not refusals, and each is reproducible with
`extract_timespan(text, "mwl", anchor=datetime(2017, 6, 27, 13, 4))`.

The most consequential one is the conjunction. Mirandese writes "and" as `i`,
and the locale's own marker file lists `i` first, ahead of `e`. But the clock's
forward-direction file lists `e` alone. So `a las trés i meia` returns 03:00
with `i meia` stranded, and `a las trés i quarto` returns 03:00 with `i quarto`
stranded, while the `e` spellings of the same phrases return the correct 03:30
and 03:15. The locale answers its own primary conjunction with the wrong time
instead of refusing it.

`a las siete de la nuite` returns 07:00 and strands `nuite`, because there is
no night meridiem to consume it. Where an English or Portuguese speaker would
expect 19:00, the result is a morning hour with the disambiguating word thrown
away — the same shape for `a las dieç de la nuite`, which gives 10:00.

`na sumana que ben` returns the correct week but strands `na`. `l die 15 de
márcio` returns the correct day but strands `l die`. `l trimestre que ben`
returns the correct quarter but strands `l`.

## Open questions for a native speaker

1. Does `manhana` mean tomorrow in ordinary Mirandese, or only the morning? If
   both, is anything else used for tomorrow?
2. Are `meidie` and `meia-nuite` the everyday words for noon and midnight?
3. Which conjunction is used when telling the time — `i` or `e`?
4. Is there a word for the day after tomorrow? The locale has `trasdonte` for
   the day before yesterday and nothing on the other side.
5. Is `sumana` the only spelling, or is *semana* also written?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("mwl")
    True
    >>> span, rest = extract_timespan('a las trés e meia', "mwl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T03:30:00', '')
    >>> span, rest = extract_timespan('a las trés menos quarto', "mwl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:45:00', '')
    >>> span, rest = extract_timespan('15 de janeiro de 2020', "mwl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2020-01-15T00:00:00', '')
    >>> span, rest = extract_timespan('hai trés dies', "mwl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-24T00:05:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('meidie', "mwl", anchor) is None
    True
    >>> extract_timespan('meia-nuite', "mwl", anchor) is None
    True
    >>> extract_timespan('l seclo XX', "mwl", anchor) is None
    True
    >>> extract_timespan('trés dies antes', "mwl", anchor) is None
    True
    >>> extract_timespan('trés dies apuis', "mwl", anchor) is None
    True
    >>> extract_timespan('trés horas', "mwl", anchor) is None
    True
    >>> extract_timespan('meia hora', "mwl", anchor) is None
    True

---
[← Maltese](mt.md) · [Home](../index.md) · [Norwegian Bokmål →](nb.md)
