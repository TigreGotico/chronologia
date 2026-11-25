# Adding a language

<!-- agent-hint
covers: the steps for teaching chronologia a new language with word lists and a test corpus
source: chronologia/locale/en/lang.json, chronologia/extract/schema.py, chronologia/extract/numlayer.py, test/test_language_parity.py
generated: no
verify: .venv/bin/python -c 'exec("import ast,io,re,sys,contextlib as c\np=sys.argv[1];t=open(p).read();ns={};n=bad=0\nfor b in re.findall(r\"\\x60\\x60\\x60python\\n(.*?)\\x60\\x60\\x60\",t,re.S):\n    if \"# doctest: skip\" in b: continue\n    L=b.split(\"\\n\")\n    for s in ast.parse(b).body:\n        o=io.StringIO()\n        with c.redirect_stdout(o): exec(compile(ast.Module([s],[]),p,\"exec\"),ns)\n        n+=isinstance(s,ast.Assert)\n        m=re.match(r\"^\\s*print\\(.*\\)\\s+# (.+)$\",L[s.end_lineno-1]) if isinstance(s,ast.Expr) and s.lineno==s.end_lineno else None\n        if m: n+=1; bad|=m[1].strip()!=o.getvalue().strip()\nsys.exit(bad or n==0)\n")' docs/adding-a-language.md
see: docs/extraction.md, docs/languages/index.md
-->

**Who this is for:** you speak a language chronologia does not yet read well, and you would like it to. You do **not** need to be a programmer. Adding a language is mostly *editing small lists of words in plain text files*. Each file holds one idea, such as "the words my language uses for January" or "the words that mean *next*". If you can use a text editor and you know your language, you can do this.

**What you will produce:** a folder, `chronologia/locale/<your-language-code>/`, holding those little word lists and one small settings file. When you are done, chronologia will understand phrases like *"next Friday"*, *"3 days ago"*, or *"5 June 2027"* written in your language.

**How long it takes:** a first, useful version, months, weekdays, and the common "next / last / in / ago" phrases, is an afternoon's work. You can stop there and it will be genuinely useful, then come back and add more later.

**The one rule that matters most:** every word you add must come from a *real source*. A source is a dictionary, a grammar book or your own knowledge as a native speaker. Note the source in the file. This is how the project stays trustworthy. We come back to it near the end, but keep it in mind from the start.

> Already a developer and just want the terse reference? The
> ["How a language works"](extraction.md) section of the extraction guide is the
> compact version. This page is the friendly, step-by-step one.

---

## What a "locale" is

A **locale** is one folder that holds everything chronologia needs to read dates in one language. It lives here:

```text
chronologia/
└── locale/
    ├── en/          ← English
    ├── ms/          ← Malay
    ├── de/          ← German
    └── <your code>/ ← the folder you will create
```

The folder name is your language's short **code**, the standard two-letter (or three-letter) ISO 639 code. English is `en`, Malay is `ms`, German is `de`, Kabyle is `kab`. If you are not sure of yours, search "ISO 639 code" plus your language's name.

Inside that folder is a **pile of small text files**. Almost all of them end in `.voc` (short for *vocabulary*). Each `.voc` file is a list of the words your language uses for **one single idea**. There is one more file, `lang.json`, which holds a few settings. That is the whole locale. Here is a real, small one, Kabyle:

```text
chronologia/locale/kab/
├── lang.json          ← the settings file (one per language)
├── month_1.voc        ← words for January
├── month_2.voc        ← words for February
│   … (through month_12.voc)
├── weekday_0.voc      ← words for Monday
│   … (through weekday_6.voc)
├── unit_day.voc       ← words meaning "day"
├── unit_week.voc      ← words meaning "week"
├── named_day_0.voc    ← words meaning "today"
├── named_day_1.voc    ← words meaning "tomorrow"
├── named_day_-1.voc   ← words meaning "yesterday"
└── marker_and.voc     ← the connecting word "and"
```

Nothing about *how dates work* lives in these files. The clever part, knowing that "3 days ago" means subtract three days, is shared code that every language reuses. Your files only supply **the words**. That is why no programming is needed: you are translating a vocabulary, not writing logic.

---

## The `.voc` file explained

A `.voc` file is the simplest thing imaginable: **one phrase per line**. Here is the real English file for January, `en/month_1.voc`:

```text
january
jan
ianuariis
```

These are three surfaces that all mean the first month. A **surface** is "a way of writing the word". The three are the full name, the common abbreviation and an old Latin form. When someone writes any of these, chronologia knows they mean month 1.

The rules for a `.voc` file are short:

- **One surface per line**. If your language writes January two ways, put both, each on its own line.
- **Lowercase**. Write everything in lowercase. chronologia lowercases the text it reads before matching. So `January` and `january` are the same to it. Writing lowercase keeps the files tidy and consistent.
- **Multi-word surfaces are fine**. A phrase like `hari ini` (Malay for "today") or `day after tomorrow` goes on one line, spaces and all.
- **Lines starting with `#` are comments**. They are notes for humans and are ignored by chronologia. This is where you write your **source** (more on that below). For example:

```text
# Month names from the Dewan Bahasa dan Pustaka standard dictionary.
# Confirmed by a native speaker (your name here), 2026.
januari
```

That is genuinely all there is to a `.voc` file. The *name* of the file tells chronologia which idea the words belong to, `month_1.voc` for January, `weekday_0.voc` for Monday, and so on. The next sections give you the exact list of file names to create.

---

## Tier 1, make it read dates at all

Start here. This tier gives you a language that can already read months, weekdays, "today / tomorrow / yesterday", and "in N days / N days ago". It is a real, shippable language on its own.

Create the folder `chronologia/locale/<your code>/` and, inside it, these files. The **left column is the exact file name**. The name is not decoration. It is how chronologia knows what the words mean, so copy it exactly.

### Months (12 files)

| File | Put in it |
|---|---|
| `month_1.voc` | your words for January |
| `month_2.voc` | February |
| … | … |
| `month_12.voc` | December |

One file per month, numbered 1 to 12. Each holds the month's name (and any common short form) in your language, one per line.

### Weekdays (7 files)

| File | Put in it |
|---|---|
| `weekday_0.voc` | Monday |
| `weekday_1.voc` | Tuesday |
| … | … |
| `weekday_6.voc` | Sunday |

Note the numbering: **Monday is 0**, Sunday is 6. (This matches the way most of the world's calendars count, and chronologia's shared code. If your culture starts the week on Sunday, do not worry. That is a *setting* that you flip in `lang.json`, not a change to these file names.)

### The unit words (the "day / week / month / year" nouns)

| File | Put in it |
|---|---|
| `unit_day.voc` | your word(s) for "day" |
| `unit_week.voc` | "week" |
| `unit_month.voc` | "month" (the noun, e.g. in "3 months ago") |
| `unit_year.voc` | "year" |
| `unit_hour.voc` | "hour" |
| `unit_minute.voc` | "minute" |

These are the nouns that appear in phrases like "3 **days** ago" or "in 2 **weeks**".

### The direction markers (this is what makes "ago" vs "in" work)

| File | Put in it |
|---|---|
| `marker_past.voc` | the word that points **backwards** in time, English "ago" |
| `marker_future.voc` | the word that points **forwards**, English "in" / "hence" |

These two are important and subtle, so here is why they matter. chronologia never guesses direction. In "3 days ago", the word *ago* is what tells it to subtract. You list here whatever word your language uses for that, and the shared code does the rest. Malay uses `lepas` for the past and `lagi` for the future. You do not write any "subtract" logic. You just name the word.

### The "next / last / this" markers

| File | Put in it |
|---|---|
| `marker_next.voc` | "next" (as in "next Friday", "next week") |
| `marker_last.voc` | "last" (as in "last Tuesday") |
| `marker_this.voc` | "this" (as in "this week") |

### The named days (today / tomorrow / yesterday)

These are single words that name a day by how far it is from *today*. The number in the file name is that offset in days: `0` is today, `1` is tomorrow, `-1` is yesterday.

| File | Put in it |
|---|---|
| `named_day_0.voc` | "today" |
| `named_day_1.voc` | "tomorrow" |
| `named_day_-1.voc` | "yesterday" |
| `named_day_2.voc` | (optional) "the day after tomorrow", if your language has one word for it |

### The settings file `lang.json`

Finally, one small settings file. The gentlest way to make it is to **copy an existing one and edit it**. A good starting point is Malay (`ms/lang.json`). It is compact and covers the common cases. `lang.json` is explained in its own section below. For Tier 1 you can copy Malay's and change very little.

That's Tier 1. With those files in place, chronologia can already read months, weekdays, "today/tomorrow/yesterday", relative offsets, and simple calendar dates in your language.

> **A note on numbers**. In "3 days ago", the `3` is a *digit*. Chronologia
> reads digits directly in every language, no setup needed. If you also want it
> to read the *spelled-out* number ("three days ago"), that needs one extra
> piece, the number backend, covered in [its own section](#numbers-digits-vs-spelled-out-words).
> You can skip it. Digits work regardless.

---

## Tier 2, times of day and clocks

Once dates work, you can teach clock times and parts of the day. These are optional. Add them when you're ready.

### Clock landmarks and dayparts

| File | Put in it |
|---|---|
| `clock_landmark_0.voc` | "midnight" (0 minutes past midnight) |
| `clock_landmark_720.voc` | "noon" / "midday" (720 minutes = 12:00) |
| `daypart_morning.voc` | words for the morning band |
| `daypart_evening.voc` | words for the evening band |
| `daypart_night.voc` | words for the night band |

A **landmark** is a named clock instant. The number in the file name is the minutes past midnight. A **daypart** names a stretch of the day.

Here is the part that surprises people: **the hours are not the same in every language. You must not assume English's**. Spanish runs one *tarde* from noon until eight in the evening, across what English splits into afternoon and evening. German has six bands, and *Nachmittag* does not start at noon. Swedish and Norwegian have a *förmiddag* / *formiddag*, a late-morning band English cannot name in one word at all. So the bands are **data**, listed per language in `chronologia/dayparts.py`, and your job is to say what your language's bands actually are.

Two steps, then:

1. **Find your language's bands**. The `chronologia/dayparts.py` file holds the known bands. Each comes from the [Unicode CLDR day-period chart](https://www.unicode.org/cldr/charts/47/supplemental/day_periods.html), which lists them for many languages. If yours is there, add its rows the same way, citing the chart. If it is not, use your national dictionary or language academy and cite that instead. If you cannot find a source, leave the band out. An honest gap is much better than invented hours.
2. **Name the `.voc` file after the band**. A band that belongs to one language is registered under a key like `tarde_es` or `kveld_nb`, and the file is `daypart_tarde_es.voc`. Only a band shared by every language, English's plain `morning`, `afternoon`, `evening`, `night`, uses the bare name.

Two traps worth knowing before you write the files:

- **One word per surface**. A day-part surface has to be a single token. So a hyphenated or two-word name (French *après-midi*, Romanian *după-amiază*) cannot be listed. The tokenizer splits it. Those bands stay registered without vocabulary rather than being faked.
- **Watch for a word that already means something else**. Your day-part word may also be your word for *tomorrow* (Spanish *mañana*, German *morgen*) or for *noon* (Dutch *middag*). If you list it plainly, you break the reading that people mean. See the licensing note below.

### When a daypart word is also another word

Spanish *mañana* is both "morning" and "tomorrow". If you list it plainly, "mañana" on its own stops meaning tomorrow. That is a silent, wrong answer, and this library does not ship wrong answers.

The fix is to **license the day-part reading positionally**: leave the bare `DAYPART` order out of your `daypart_ref` construction. So the word is read as a day-part only in a position where the other meaning cannot occur. Spanish says *esta mañana*, *por la mañana*, *de mañana*, always with a demonstrative, an article or a preposition. So those orders are listed and the bare one is not:

```text
"daypart_ref": {
  "orders": [
    "REL_MARKER DAYPART",   ← "esta mañana"
    "article DAYPART",      ← "por la mañana"
    "of DAYPART"            ← "de mañana"
  ]
}
```

Bare "mañana" then keeps its tomorrow reading, and "mañana por la tarde" still reads as tomorrow afternoon.

Your language may have no such position. German says *heute Morgen* with nothing in front of the word. Then no correct way to list it exists, and the band ships with no vocabulary. German keeps *Vormittag*, *Nachmittag*, *Abend* and *Nacht*, and gives up *Morgen*. Losing one phrase is a fair price for never turning "morgen" into the wrong day.

### The clock-fraction words and the convention flags

Here is the interesting part. Many languages say things like "half nine" or "quarter to ten". But **different languages mean different things by the same shape**, and chronologia will not guess. You *tell* it, with a setting called a **convention flag** in `lang.json`.

First, the fraction words:

| File | Put in it |
|---|---|
| `clock_fraction_30.voc` | your word for the "half" fraction |
| `clock_fraction_15.voc` | your word for the "quarter" fraction |
| `clock_dir_past.voc` | the word meaning "past" (e.g. "half **past** nine") |
| `clock_dir_to.voc` | the word meaning "to" / "before" (e.g. "quarter **to** ten") |

When the direction word is *spoken* ("half **past** nine"), there is no ambiguity. The flags below only decide what a **bare** fraction, one with *no* direction word, means in your language:

| Flag in `lang.json` | Set it to `true` if, in your language… |
|---|---|
| `bare_half_past` | "half nine" means **9:30** (English colloquial: half *past* nine) |
| `bare_half_to` | "half nine" means **8:30** (German/Dutch/Scandinavian: the half *before* nine, "halb neun") |
| `bare_quarter_to` | a bare quarter counts *toward* the coming hour (Hungarian/Estonian: "quarter nine" = 8:15) |
| `toward_hour_12h` | in a toward-the-hour system, renames the hour before one as *twelve* on the toward-hour path. A bare "half toward one" still resolves to the next of 00:30 and 12:30, whichever comes first after the anchor (ruling 17). The locales Slovenian, Russian, Polish and Czech set it |

Pick the one that matches how *your* language actually speaks. If none applies, because your language always says the direction word out loud, leave them all off (the default). The plain-language question to ask yourself is: *"In my language, does 'half nine' mean 8:30 or 9:30?"*, and set the flag accordingly.

### When the clock preposition also counts ("a las 3 vecinas")

In some languages the word before a clock hour also introduces a counted group: English "wave at 5 people", Spanish "a las 3 vecinas" (to the three neighbours), Dutch "om 3 mensen" (about three people). Two optional files let chronologia tell the two apart. Leave them out if your language has no such clash.

| File | Put in it |
|---|---|
| `marker_at_counts.voc` | the clock prepositions that also introduce a counted group ("at", "a", "om") |
| `marker_counted_noun.voc` | nouns that count people or things a clock never takes ("people", "vecinas", "mensen"), singular and plural, each gender |
| `marker_participle_aux.voc` | forms of the auxiliary that a word with a season reading follows as a past participle (fr "avoir" before "été") |

A bare hour behind one of those prepositions and directly before one of those nouns is read as a count. Any other word after the hour, a verb included, leaves the clock as it is ("a las 8 llegamos" is 08:00). Cite a dictionary entry that shows the class of each noun in the file header, and keep the fetched page with your audit.

### Counting quarters toward the hour ("dos quarts de deu")

Some languages don't just shift the hour. They *count* how many quarters of the coming hour have already struck. Catalan's traditional **sistema de campanar** is the clearest case, and Catalan speaks it alongside the ordinary additive clock, so both have to work at once:

| Catalan | Time | Same time, ordinary clock |
|---|---|---|
| `un quart de deu` | 09:15 | `les nou i quart` |
| `dos quarts de deu` | 09:30 | `les nou i mitja` |
| `tres quarts de deu` | 09:45 | `les deu menys quart` |

The named hour is the one being *approached*, so the reading is `(hour − 1) + N×15` minutes, `un quart de deu` is quarter past **nine**. The hour before one is spoken as twelve, so `un quart d'una` is 12:15.

This is a different *shape*, not a flag: it needs its own word list and its own construction order.

| File | Put in it |
|---|---|
| `marker_quarters.voc` | your word for "quarter(s)" in this counting sense, all inflections (Catalan: `quart`, `quarts`) |

Then add the order to `clock_time` in `lang.json`, before the other clock orders:

```json
"at? QUARTS quarters of HOUR of? article? MERIDIEM? ZONE?"
```

`QUARTS` binds the count. Only one, two and three quarters exist. A fourth quarter is the whole hour, so the library refuses counts outside 1-3 and does not guess.

---

## Tier 3, the rich stuff

When the basics are solid, chronologia can read much more, each backed by its own `.voc` files and construction orders. You don't need any of this to contribute something useful, but here's where to look:

- **Seasons**: `season_spring.voc`, `season_summer.voc`, … (plus a `hemisphere` setting in `lang.json` for southern-hemisphere languages).
- **Eras**: "44 BC", "1492 AD": `marker_bc.voc`, `marker_ad.voc`.
- **Weekends**: `special_weekend.voc` (and the `weekend_start` setting for languages whose weekend is Friday-Saturday).
- **Quarters, ISO weeks, decades, fuzzy periods** ("early 90s"), see the constructions in an existing full language like `en/lang.json`.
- **Holidays**: you do **not** list these by hand. Holiday names come automatically from the shared holidays engine once your language code is known to it. See [civil-holidays.md](civil-holidays.md).
- **Non-Gregorian calendars** (Islamic, Hebrew, …), use `month_<calendar>_<n>.voc`, e.g. `month_islamic_civil_9.voc` for Ramadan. See [calendars.md](calendars.md) for the calendar names.

The best way to learn Tier 3 is to open a mature language (`en`, `de`, `pt`) and copy the pattern for the one feature you want.

---

## Tier 4, recurrence ("every Friday", "the third Tuesday of every month")

A locale that stops at Tier 3 can read a single date. But it does not read a *repeating* one. "Every Friday", "daily at 9" and "the third Tuesday of every month" each name a rule, not a single day. That rule is the RFC 5545 `RRULE` grammar that [recurrence.md](recurrence.md) covers. This tier is what teaches your language the words that name a recurrence. The RRULE machinery itself is shared engine code, so, same as everywhere else in this guide, you are only supplying vocabulary.

### The `every` / `other` markers

| File | Put in it |
|---|---|
| `marker_every.voc` | "every" / "each" (as in "every Friday", "every 2 weeks") |
| `marker_recur_other.voc` | "other" / "alternate" (as in "every **other** week") |

### The frequency adverbs

Some recurrences are said as a single adverb rather than "every + unit":

| File | Put in it |
|---|---|
| `marker_freq_daily.voc` | "daily" |
| `marker_freq_weekly.voc` | "weekly" |
| `marker_freq_monthly.voc` | "monthly" |
| `marker_freq_yearly.voc` | "yearly" / "annually" |
| `marker_freq_biweekly.voc` | "biweekly" / "fortnightly", read as *every two weeks*, the more common sense (Merriam-Webster's usage note), not "twice a week" |
| `marker_freq_quarterly.voc` | "quarterly". Every three months |

### The recurrence-specific markers

| File | Put in it |
|---|---|
| `marker_recur_once.voc` | "once" (as in "once a week") |
| `marker_recur_per.voc` | "per" (as in "twice per month") |
| `marker_recur_for.voc` | "for" (as in "every Monday **for** 6 weeks", bounds the rule with a `COUNT`) |
| `marker_until.voc` | "until" / "till" (as in "every Friday **until** June", bounds the rule with an `UNTIL`) |
| `marker_weekday.voc` | the class noun "weekday(s)" (as in "every weekday", distinct from any one named weekday) |
| `marker_weekday_count.voc` | the plural forms of the class noun that name a count ("5 weekdays of the month"), never an ordinal |
| `marker_recur_habitual.voc` | (optional) a habitual preposition some languages use instead of "every" before a weekday, Portuguese marks it with `à` / `às` / `ao` / `aos` ("**à** segunda" = "on Mondays, habitually") |

`special_weekend.voc` (Tier 3) and the weekday and month files (Tier 1) do double duty here. "Every weekend", "every Friday" and "the third Tuesday of November" all resolve through the weekday and month vocabulary that you already wrote. There is nothing to add for those.

With these files in place, chronologia reads these phrases in your language: "every Friday", "every other week", "daily", "once a week on Monday" and "the last Monday of May". It also reads the bounded forms "every Monday for 6 weeks" and "every Friday until June". Each resolves to the `Recurrence` object that [recurrence.md](recurrence.md) describes. Read that page to see what the rule looks like once your words are folded onto it.

---

## `lang.json` explained gently

`lang.json` is the one non-`.voc` file. It is a small **settings** file that tells chronologia which sentence shapes your language uses and a few calendar conventions. You will almost always start by copying an existing one.

It has four parts worth understanding:

**1. `tokenizer`**: three on/off switches for how text is chopped into words. Most languages leave them all `false`. The flag `split_contractions` splits words like French *l'année*. The flag `ordinal_dot` treats "3." as an ordinal, as German does.

The flag `dotted_date` reads the continental numeric date "15.06.2020" as one date. It belongs to every language whose everyday written date has that shape: German, Russian, Polish, Czech, Finnish, Turkish, Dutch and their neighbours. It does not belong to a language that writes the numeric date only with slashes.

**2. `constructions`**: this is the heart of it. A **construction** is a *recipe* for one kind of date phrase, and each recipe lists the **word order** your language uses. An order is a short sequence of **slots** and **connector words**. A slot is an uppercase name for "a thing that goes here".

A connector word is lowercase and matches a `.voc` file. Read the uppercase names as placeholders. For example, from Malay:

```text
"calendar_date": {
  "orders": [
    "DAY MONTH YEAR?",     ← "17 July 2026"  (day, then month, then optional year)
    "MONTH DAY? YEAR?"     ← "July 2026" or "July 17 2026"
  ]
}
```

- `DAY`, `MONTH`, `YEAR` are **slots**. Chronologia fills them from the numbers and month words in the sentence.
- A trailing `?` means "**optional**", `YEAR?` reads a year if one is present, but the phrase still works without it.
- A relative offset like Malay "3 days ago" uses the order `"NUM UNIT MARKER"`, a number, then a unit word, then a direction marker (`ago`). English says the marker differently ("in 3 days"). So English lists a different order. **The word order is the main thing you adjust for your language**. If your language puts the month before the day, list `MONTH DAY`. If after, list `DAY MONTH`. You are describing your grammar, not inventing it.

The safest approach is to copy the `constructions` block from the language closest to yours. Then reorder the slots inside each order to match how *your* language arranges the words. If a construction uses words your language doesn't have, just remove that construction. Chronologia checks on load that every recipe has the words it needs, and will tell you clearly if one is missing its vocabulary.

**3. `conventions`**: a handful of calendar facts:

- `week_start`: `"monday"` or `"sunday"`.
- `dmy`: `true` if your language writes day-before-month (15/06), `false` for month-before-day (06/15).
- `weekend_start`: first day of the two-day weekend, as a number with Monday=0. The value `5` is Saturday, for most of the world. The value `4` is Friday, for Israel and much of the Arab world.
- the clock flags from Tier 2 (`bare_half_past`, `bare_half_to`, …).
- `hemisphere`: `"south"` if seasons should be flipped, else leave it out.

**4. `number_fold`**: the number-folding settings. They turn spelled-out numbers ("three", "twenty-five") into digits before matching. A language that numtag reads (next section) needs only the object, and it can be empty:

```json
"number_fold": {}
```

The object lists what the `.voc` files cannot say. Every key is optional:

- `word_numbers`: words numtag does not read. Each word maps to `[value, is_ordinal]`, as in `"annen": [2, true]`.
- `ordinal_suffixes`: the lone suffixes of a digit ordinal. The tokenizer reads "21e" as "21" and "e", and a suffix in this list merges back into an ordinal.
- `phrase_numbers`: two words that name one number: `"een paar": 2`.
- `compounds`: rows of `{"heads": {head: reading}, "tails": [...]}`. A word that is exactly a head and a tail splits into two tokens before range detection, so "morgenochtend" reads as "morgen" and "ochtend".
- `fraction_counts`: rows that fold the count 1 and a fraction word into the fraction. A row names `word` and `value`. A row with `unit` makes the fraction word name that unit ("en kvart" is a quarter of an hour), unless the next word is in `not_before`.
- `h_clock_markers`: the words before which "21h30" is a clock time. Without a marker "21h30" is a duration.

The fold also reads the `clock_fraction_*.voc`, `scale_*.voc`, `marker_since.voc`, `marker_until.voc`, `unit_*.voc`, `month_*.voc` and `currency*.voc` files of the locale. They tell a count from a year and keep the half of a clock hour a word.

If your language has no number fold, leave `number_fold` out. chronologia still reads digits, but not spelled-out number words. Nothing else in `lang.json` depends on it.

A few languages still name code with three other keys. `hook` points at a fold function, and a locale that sets it leaves `number_fold` out. `pre_hook` runs once on the whole token stream before range detection and number folding. `post_hook` runs once on the whole stream after the number fold, with the tokens and the language spec. French uses it to read "dans 2 heures moins 10 secondes" as one length:

```json
"post_hook": "chronologia.extract.numlayer_fr:fold_fr_hour_length"
```

---

## Numbers: digits vs spelled-out words

chronologia reads **digits** (`3`, `2027`, `15:30`) in every language with no setup at all. The only thing that needs help is **spelled-out** numbers, "three days ago" instead of "3 days ago".

Turning "three" into `3` is a separate, specialised job. Two kinds of number fold exist.

Most languages read their numbers through [numtag](https://github.com/TigreGotico/numtag). numtag keeps one lexicon file per language, with the source of every rule inside the file. A language reads through numtag when it has an entry in `NUMTAG_LANGS` in `chronologia/extract/numlayer.py`. A numtag lexicon alone is not enough.

The other languages (for example `be`, `mk`, `sr`, `cy`, `ga` and `ko`) read spelled numbers with a `numfold_*.py` module of chronologia's own, which owns its number words as closed tables.

**To read your language through numtag:** first make sure numtag ships a lexicon for it. Adding one is described in numtag's [adding-a-language guide](https://github.com/TigreGotico/numtag/blob/dev/docs/adding-a-language.md). Then add the language to `NUMTAG_LANGS` and add a `number_fold` object to its `lang.json` (compare `locale/ms/lang.json`).

**If your language has no number fold:** that is completely fine. Leave `number_fold` out, ship your language with digit reading only, and it still passes all its tests. Spelled-out number support is a good follow-up, not a blocker.

---

## Testing, how you prove it works

This is the most important section, and it is friendlier than it sounds.

chronologia follows a simple discipline: **you do not claim that your language works. You show it, with examples**. Every language has a folder of tests at `test/nl_corpus_<your code>/`. It holds *real sentences a person would say*, each paired with the exact date it should mean. The test runner checks that chronologia agrees. It is required: **a language must ship these examples.**

### What a green corpus does and does not tell you

A passing corpus means the engine returns the value the example says it should. It does not mean a speaker of that language has read the example.

Most locales are **unverified but internally consistent**: their expected values are derived by arithmetic independent of the parser. That arithmetic has been re-derived against implementations sharing no code with it, but the *phrases* have had no native reader. An unidiomatic sentence with a correct date attached passes every check the project can run alone.

A locale becomes verified when a speaker of it signs the corpus off. The reviewer is named where that has happened, with something a reader can go and check. Danish has one: @andlo, whose native review of the open questions in `docs/languages/da.md` is issues #887 and #888. Every other locale waits for a reader. Until a reader checks it, its corpus shows that the engine is self-consistent. It does not show that the engine understands the language.

Being a reviewer for a locale elsewhere in the organisation is not a record here. The name goes on this page when the person has read these files and said so where it can be cited.

This is why the vocabulary comment convention above asks for a name and not a verdict: "confirmed by a native speaker" is a claim about a person, and only a person can make it. No automated check, corpus frequency count or model reading may be written up as a native review. A speaker outranks every signal the project owns, which is precisely what makes the word worth protecting.

Two things make it approachable:

**1. The examples are just phrases and expected answers**. Here is a real one from the Malay corpus. You can see it's readable even if you don't code:

```text
("esok",           1)   # "esok" (tomorrow) should be 1 day after today
("semalam",       -1)   # "semalam" (yesterday) should be 1 day before today
("hari ini",       0)   # "hari ini" (today) should be today
```

You write the phrase in your language and the answer you *know* is right as a native speaker. That's the whole idea.

**2. The parity block proves the *meaning* matches English**. Alongside the examples, each language ships a small list called the **parity block** (`parity.py`). It pairs a phrase in your language with the English phrase that means the same thing:

```text
('minggu depan', 'next week'),
('esok',         'tomorrow'),
('17 julai 2026','july 17 2026'),
('44 sm',        '44 bc'),
```

The test runner reads *both*, resolves them, and insists they land on the **exact same span**. This check proves your Malay "next week" means the same instant of time as English "next week", with no hand-tuning. Every language needs **at least 25** such pairs. The corpus as a whole needs **at least 100 example cases** total (across all the little `test_nl_*.py` files). The easiest path is to copy the structure of an existing corpus folder (Malay's `nl_corpus_ms/` is a good, compact model) and translate the phrases.

**3. The confusables file holds words that only *look* like dates**. A mature corpus also includes a `test_nl_confusables.py`. It lists sentences with words that resemble dates but do not mean one.

Two examples are a month name used as a person's name and a "second" that means "a moment", not the time unit. These assert that chronologia does *not* wrongly grab them. This one is worth adding once the happy path works, because it catches over-eager matching.

### Running your language's tests

From the top of the repository, run just your language's tests like this:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest test/nl_corpus_<your code>/ -q
```

(The `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` part keeps unrelated plugins from interfering. Use the Python that has chronologia installed.)

A green run, no failures, means your language works. That's the moment you're aiming for.

---

## The citation rule, and why it matters

Here is the rule the project cares about most, and the reason for it.

Every word you add must trace to a **real source**. This holds for a month name, a marker and a season word. A real source is a dictionary, a published grammar, a language authority or your own confirmation as a native speaker. And you *write that source down*, as a `#` comment at the top of the `.voc` file.

**Why.** chronologia is used to read dates people wrote, in dozens of languages its maintainers cannot all speak. The only thing that makes a Kabyle or Tagalog month list trustworthy to someone who doesn't speak it is a **source they can check**. A citation turns "someone typed this in" into "this is documented." That is the difference between data people can rely on and data they cannot.

**How**. Put one or two comment lines at the top of the file:

```text
# Month names from the Dewan Bahasa dan Pustaka standard dictionary (2015 ed.).
# https://prpm.dbp.gov.my/
januari
```

**A native speaker's confirmation counts**: you are a valid source for your own language. Just say so plainly:

```text
# Colloquial forms confirmed by a native speaker, 2026.
# Standard forms cross-checked against Wiktionary.
esok
```

The goal is not bureaucracy. It's that the next person, maintainer or contributor, can see *where this came from* and trust it.

---

## When the right answer is to leave it out

Sooner or later you will reach a construction your language does not have, or has in a way your sources cannot agree on. Leaving it out is a correct outcome. A locale that ships fewer constructions honestly is worth more than one that ships them all by guessing. Nobody will ask you to fill every file.

The three shapes this takes are all normal. Your language may simply lack the concept. Maltese has no word for the day before yesterday, so it ships no `named_day_-2.voc` and that phrase returns nothing. A word may have a form about which your sources contradict each other. Serbian *nedelja* is Sunday in one dictionary and the week in another, in the very case that "last" and "next" use.

So that word answers neither, and the unambiguous *sedmica* carries the week reading. Or the reference data may define no boundaries for something that another language pins down. Several locales ship no day-period bands at all, and invent no clock times for "morning".

The one thing that is never acceptable is a form you made up because the neighbouring language has one. That produces a confident wrong answer, which the caller cannot detect and cannot argue with.

**Pin the refusal, don't just omit it**. An empty gap looks identical to an oversight, and the next contributor will helpfully fill it. Two habits prevent that. Write the reason as a `#` header comment in the nearest related file, the file that *does* ship. Name the source you consulted and what it failed to establish:

```text
# pitgħada, "the day after tomorrow", with its attested variant bitgħada.
# There is no named_day_-2 file: Maltese has no sourced word for the day
# before yesterday, CLDR carries no relative-type--2 field for mt, and none
# is invented here.  en.wiktionary.org, pitgħada.
pitgħada
```

Then assert the refusal in your corpus, the same way you assert the readings that work. Some locales keep a dedicated `test_<code>_refusals.py` module for exactly this:

```python
# doctest: skip
@pytest.mark.parametrize("text", ["qabel ilbieraħ", "ilbieraħ l-ieħor"])
def test_the_day_before_yesterday_is_not_guessed(text):
    r = parse(text)
    assert r is None or r[0].start.date().isoformat() != "2027-05-10"
```

Note the shape of that assertion. The refusal being pinned is not "this returns `None`", it is "this never returns the *wrong day*". A phrase whose construction does not exist may still parse partially. The parser consumes the words it knows and leaves the rest in the remainder. That is a fair outcome. What must never happen is the confident wrong date.

A pinned refusal is a decision with evidence behind it. An unpinned one is indistinguishable from a to-do, and it will quietly become a wrong answer the first time someone tidies up.

---

## Submitting your work

You don't need to be a git expert. The gentle version:

1. **Fork** the repository on GitHub (a "fork" is your own copy) using the Fork button.
2. **Create a branch** with a clear name like `add-language-<your code>`.
3. **Add your files**: the `chronologia/locale/<your code>/` folder and the `test/nl_corpus_<your code>/` folder.
4. **Run the tests** for your language (the command above) and make sure they're green.
5. **Open a pull request** back to the project, describing the language you added and citing your sources.

If any of that is unfamiliar, say so in an issue first. The maintainers prefer to help you land a good language over leaving you alone with git. Check for a `CONTRIBUTING` guide in the repository for the project's exact preferences on branches and commits.

---

## A worked mini-example: adding one month spelling

Let's walk the smallest possible change end to end, so you can see the whole loop. Suppose Malay already works, but you notice that April is missing a common spelling your region uses, and you want to add it.

**Step 1, find the file**. April is month 4, so the file is `chronologia/locale/ms/month_4.voc`. Open it in a text editor.

**Step 2, add the surface and its source**. Add your spelling on its own line, lowercase, and note where it comes from:

```text
# Standard month name from Dewan Bahasa dan Pustaka.
# Regional spelling confirmed by a native speaker, 2026.
april
```

**Step 3, add a test that proves it reads**. Open the Malay calendar test, `test/nl_corpus_ms/test_nl_calendar.py`. Add a case that uses the spelling you add in a full date, with the date you know it means.

**Step 4, run it**. From the top of the repo:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest test/nl_corpus_ms/ -q
```

**Step 5, see green**. No failures means chronologia reads your spelling and still reads everything it read before. You're done: commit and open a pull request.

That five-step loop is the whole rhythm of contributing a language. The steps are *find the file, add the word with a source, add a test, run it, see green*. It is the same loop for one spelling and for a whole locale.

---

## Seeing it work in code

Once your locale is in place, this is what reading a date looks like. The same call works for every language, yours included:

```python
from datetime import datetime

from chronologia import extract_timespan

# Pretend "now" is noon on Wednesday, 15 July 2026.
anchor = datetime(2026, 7, 15, 12, 0)

result = extract_timespan("next friday", "en", anchor)
# result.span is the stretch of time it found; result.remainder is the
# leftover text that was not part of the date.
assert result.span.start.year == 2026
assert result.span.start.month == 7
assert result.span.start.day == 17
```

Swap `"en"` for your language code and `"next friday"` for the equivalent phrase in your language. Once your locale ships those words, the phrase resolves to the same Friday. That is the whole promise of adding a language: the shared engine already knows what dates *mean*. You are simply teaching it the words your language uses to say them.

---

*Ready for the technical reference? The ["How a language works, and how to add one"](extraction.md) section of the extraction guide is the compact, developer-facing companion to this page.*

---
[← Reading dates written by humans](extraction.md) · [Home](index.md) · [Events and iCalendar →](events.md)
