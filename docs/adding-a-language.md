# Adding a language

**Who this is for:** you speak a language chronologia does not yet read well,
and you would like it to. You do **not** need to be a programmer. Adding a
language is mostly *editing small lists of words in plain text files* — one
file per idea ("the words my language uses for January", "the words that mean
*next*"). If you can use a text editor and you know your language, you can do
this.

**What you will produce:** a new folder,
`chronologia/locale/<your-language-code>/`, holding those little word lists and
one small settings file. When you are done, chronologia will understand phrases
like *"next Friday"*, *"3 days ago"*, or *"5 June 2027"* written in your
language.

**How long it takes:** a first, useful version — months, weekdays, and the
common "next / last / in / ago" phrases — is an afternoon's work. You can stop
there and it will be genuinely useful, then come back and add more later.

**The one rule that matters most:** every word you add should come from a
*real source* — a dictionary, a grammar book, or your own knowledge as a native
speaker — and you note that source in the file. This is how the project stays
trustworthy. We come back to it near the end, but keep it in mind from the
start.

> Already a developer and just want the terse reference? The
> ["How a language works"](extraction.md) section of the extraction guide is the
> compact version. This page is the friendly, step-by-step one.

---

## What a "locale" is

A **locale** is one folder that holds everything chronologia needs to read
dates in one language. It lives here:

```text
chronologia/
└── locale/
    ├── en/          ← English
    ├── ms/          ← Malay
    ├── de/          ← German
    └── <your code>/ ← the folder you will create
```

The folder name is your language's short **code** — the standard two-letter
(or three-letter) ISO 639 code. English is `en`, Malay is `ms`, German is `de`,
Kabyle is `kab`. If you are not sure of yours, search "ISO 639 code" plus your
language's name.

Inside that folder is a **pile of small text files**. Almost all of them end in
`.voc` (short for *vocabulary*). Each `.voc` file is a list of the words your
language uses for **one single idea**. There is one more file, `lang.json`,
which holds a few settings. That is the whole locale. Here is a real, small
one — Kabyle:

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

Nothing about *how dates work* lives in these files. The clever part — knowing
that "3 days ago" means subtract three days — is shared code that every
language reuses. Your files only supply **the words**. That is why no
programming is needed: you are translating a vocabulary, not writing logic.

---

## The `.voc` file explained

A `.voc` file is the simplest thing imaginable: **one phrase per line**. Here is
the real English file for January, `en/month_1.voc`:

```text
january
jan
ianuariis
```

Three surfaces (a **surface** is just "a way of writing the word") that all
mean the first month: the full name, the common abbreviation, and an old Latin
form. When someone writes any of these, chronologia knows they mean month 1.

The rules for a `.voc` file are short:

- **One surface per line.** If your language writes January two ways, put both,
  each on its own line.
- **Lowercase.** Write everything in lowercase. chronologia lowercases the
  text it reads before matching, so `January` and `january` are the same to it —
  writing lowercase keeps the files tidy and consistent.
- **Multi-word surfaces are fine.** A phrase like `hari ini` (Malay for
  "today") or `day after tomorrow` goes on one line, spaces and all.
- **Lines starting with `#` are comments.** They are notes for humans and are
  ignored by chronologia. This is where you write your **source** (more on that
  below). For example:

```text
# Month names from the Dewan Bahasa dan Pustaka standard dictionary.
# Confirmed by a native speaker (your name here), 2026.
januari
```

That is genuinely all there is to a `.voc` file. The *name* of the file tells
chronologia which idea the words belong to — `month_1.voc` for January,
`weekday_0.voc` for Monday, and so on. The next sections give you the exact list
of file names to create.

---

## Tier 1 — make it read dates at all

Start here. This tier gives you a language that can already read months,
weekdays, "today / tomorrow / yesterday", and "in N days / N days ago". It is a
real, shippable language on its own.

Create the folder `chronologia/locale/<your code>/` and, inside it, these files.
The **left column is the exact file name** — the name is not decoration, it is
how chronologia knows what the words mean, so copy it precisely.

### Months (12 files)

| File | Put in it |
|---|---|
| `month_1.voc` | your words for January |
| `month_2.voc` | February |
| … | … |
| `month_12.voc` | December |

One file per month, numbered 1 to 12. Each holds the month's name (and any
common short form) in your language, one per line.

### Weekdays (7 files)

| File | Put in it |
|---|---|
| `weekday_0.voc` | Monday |
| `weekday_1.voc` | Tuesday |
| … | … |
| `weekday_6.voc` | Sunday |

Note the numbering: **Monday is 0**, Sunday is 6. (This matches the way most of
the world's calendars count, and chronologia's shared code. If your culture
starts the week on Sunday, don't worry — that is a *setting* you'll flip in
`lang.json`, not a change to these file names.)

### The unit words (the "day / week / month / year" nouns)

| File | Put in it |
|---|---|
| `unit_day.voc` | your word(s) for "day" |
| `unit_week.voc` | "week" |
| `unit_month.voc` | "month" (the noun, e.g. in "3 months ago") |
| `unit_year.voc` | "year" |
| `unit_hour.voc` | "hour" |
| `unit_minute.voc` | "minute" |

These are the nouns that appear in phrases like "3 **days** ago" or "in 2
**weeks**".

### The direction markers (this is what makes "ago" vs "in" work)

| File | Put in it |
|---|---|
| `marker_past.voc` | the word that points **backwards** in time — English "ago" |
| `marker_future.voc` | the word that points **forwards** — English "in" / "from now" / "hence" |

These two are important and subtle, so here is why they matter. chronologia
never guesses direction. In "3 days ago", the word *ago* is what tells it to
subtract. Whatever word your language uses for that — Malay uses `lepas` for the
past and `lagi` for the future — you list it here, and the shared code does the
rest. You do not write any "subtract" logic; you just name the word.

### The "next / last / this" markers

| File | Put in it |
|---|---|
| `marker_next.voc` | "next" (as in "next Friday", "next week") |
| `marker_last.voc` | "last" (as in "last Tuesday") |
| `marker_this.voc` | "this" (as in "this week") |

### The named days (today / tomorrow / yesterday)

These are single words that name a day by how far it is from *today*. The number
in the file name is that offset in days — `0` is today, `1` is tomorrow, `-1` is
yesterday.

| File | Put in it |
|---|---|
| `named_day_0.voc` | "today" |
| `named_day_1.voc` | "tomorrow" |
| `named_day_-1.voc` | "yesterday" |
| `named_day_2.voc` | (optional) "the day after tomorrow", if your language has one word for it |

### The settings file `lang.json`

Finally, one small settings file. The gentlest way to make it is to **copy an
existing one and edit it**. A good starting point is Malay (`ms/lang.json`) — it
is compact and covers the common cases. `lang.json` is explained in its own
section below; for Tier 1 you can copy Malay's and change very little.

That's Tier 1. With those files in place, chronologia can already read months,
weekdays, "today/tomorrow/yesterday", relative offsets, and simple calendar
dates in your language.

> **A note on numbers.** In "3 days ago", the `3` is a *digit* — chronologia
> reads digits directly in every language, no setup needed. If you also want it
> to read the *spelled-out* number ("three days ago"), that needs one extra
> piece, the number backend, covered in [its own section](#numbers-digits-vs-spelled-out-words).
> You can skip it for now; digits work regardless.

---

## Tier 2 — times of day and clocks

Once dates work, you can teach clock times and parts of the day. These are
optional; add them when you're ready.

### Clock landmarks and dayparts

| File | Put in it |
|---|---|
| `clock_landmark_0.voc` | "midnight" (0 minutes past midnight) |
| `clock_landmark_720.voc` | "noon" / "midday" (720 minutes = 12:00) |
| `daypart_morning.voc` | words for the morning band |
| `daypart_evening.voc` | words for the evening band |
| `daypart_night.voc` | words for the night band |

A **landmark** is a named clock instant; the number in the file name is the
minutes past midnight. A **daypart** names a stretch of the day.

Here is the part that surprises people: **the hours are not the same in every
language, and you must not assume English's.** Spanish runs one *tarde* from
noon until eight in the evening, across what English splits into afternoon and
evening. German has six bands, and *Nachmittag* does not start at noon. Swedish
and Norwegian have a *förmiddag* / *formiddag* — a late-morning band English
cannot name in one word at all. So the bands are **data**, listed per language
in `chronologia/dayparts.py`, and your job is to say what your language's bands
actually are.

Two steps, then:

1. **Find your language's bands.** The `chronologia/dayparts.py` file holds the
   ones already known, each transcribed from the [Unicode CLDR day-period
   chart](https://www.unicode.org/cldr/charts/47/supplemental/day_periods.html),
   which lists them for a great many languages. If yours is there, add its rows
   the same way, citing the chart. If it is not, use your national dictionary or
   language academy and cite that instead — and if you cannot find a source,
   leave the band out. An honest gap is much better than invented hours.
2. **Name the `.voc` file after the band.** A band that belongs to one language
   is registered under a key like `tarde_es` or `kveld_nb`, and the file is
   `daypart_tarde_es.voc`. Only a band shared by every language — English's
   plain `morning`, `afternoon`, `evening`, `night` — uses the bare name.

Two traps worth knowing before you write the files:

- **One word per surface.** A day-part surface has to be a single token, so a
  hyphenated or two-word name (French *après-midi*, Romanian *după-amiază*)
  cannot be listed; the tokenizer splits it. Those bands stay registered
  without vocabulary rather than being faked.
- **Watch for a word that already means something else.** If your day-part word
  is also your word for *tomorrow* (Spanish *mañana*, German *morgen*) or for
  *noon* (Dutch *middag*), listing it plainly would quietly break the reading
  people actually mean. See the licensing note below.

### When a daypart word is also another word

Spanish *mañana* is both "morning" and "tomorrow". If you simply list it, then
"mañana" on its own stops meaning tomorrow — a silent, wrong answer, which is
the one thing this library will not ship.

The fix is to **license the day-part reading positionally**: leave the bare
`DAYPART` order out of your `daypart_ref` construction, so the word is read as
a day-part only in a position where the other meaning cannot occur. Spanish
says *esta mañana*, *por la mañana*, *de mañana* — always with a demonstrative,
an article or a preposition — so those orders are listed and the bare one is
not:

```text
"daypart_ref": {
  "orders": [
    "REL_MARKER DAYPART",   ← "esta mañana"
    "article DAYPART",      ← "por la mañana"
    "of DAYPART"            ← "de mañana"
  ]
}
```

Bare "mañana" then keeps its tomorrow reading, and "mañana por la tarde" still
reads as tomorrow afternoon.

If your language has no such position — German says *heute Morgen* with nothing
in front of the word — then there is no honest way to list it, and the band
ships with no vocabulary. German keeps *Vormittag*, *Nachmittag*, *Abend* and
*Nacht*, and gives up *Morgen*. Losing one phrase is a fair price for never
turning "morgen" into the wrong day.

### The clock-fraction words and the convention flags

Here is the interesting part. Many languages say things like "half nine" or
"quarter to ten". But **different languages mean different things by the same
shape**, and chronologia will not guess — you *tell* it, with a setting called a
**convention flag** in `lang.json`.

First, the fraction words:

| File | Put in it |
|---|---|
| `clock_fraction_30.voc` | your word for the "half" fraction |
| `clock_fraction_15.voc` | your word for the "quarter" fraction |
| `clock_dir_past.voc` | the word meaning "past" (e.g. "half **past** nine") |
| `clock_dir_to.voc` | the word meaning "to" / "before" (e.g. "quarter **to** ten") |

When the direction word is *spoken* ("half **past** nine"), there is no
ambiguity. The flags below only decide what a **bare** fraction — one with *no*
direction word — means in your language:

| Flag in `lang.json` | Set it to `true` if, in your language… |
|---|---|
| `bare_half_past` | "half nine" means **9:30** (English colloquial: half *past* nine) |
| `bare_half_to` | "half nine" means **8:30** (German/Dutch/Scandinavian: the half *before* nine — "halb neun") |
| `bare_quarter_to` | a bare quarter counts *toward* the coming hour (Hungarian/Estonian: "quarter nine" = 8:15) |
| `toward_hour_12h` | in a toward-the-hour system, the hour before one is spoken as *twelve*, so "half toward one" is **12:30**, not 00:30 (Slovenian, Russian, Polish, Czech) |

Pick the one that matches how *your* language actually speaks. If none applies —
your language always says the direction word out loud — leave them all off (the
default). The plain-language question to ask yourself is: *"In my language, does
'half nine' mean 8:30 or 9:30?"* — and set the flag accordingly.

### Counting quarters toward the hour ("dos quarts de deu")

Some languages don't just shift the hour — they *count* how many quarters of the
coming hour have already struck. Catalan's traditional **sistema de campanar**
is the clearest case, and Catalan speaks it alongside the ordinary additive
clock, so both have to work at once:

| Catalan | Time | Same time, ordinary clock |
|---|---|---|
| `un quart de deu` | 09:15 | `les nou i quart` |
| `dos quarts de deu` | 09:30 | `les nou i mitja` |
| `tres quarts de deu` | 09:45 | `les deu menys quart` |

The named hour is the one being *approached*, so the reading is
`(hour − 1) + N×15` minutes — `un quart de deu` is quarter past **nine**. The
hour before one is spoken as twelve, so `un quart d'una` is 12:15.

This is a different *shape*, not a flag: it needs its own word list and its own
construction order.

| File | Put in it |
|---|---|
| `marker_quarters.voc` | your word for "quarter(s)" in this counting sense, all inflections (Catalan: `quart`, `quarts`) |

Then add the order to `clock_time` in `lang.json`, before the other clock
orders:

```json
"at? QUARTS quarters of HOUR of? article? MERIDIEM? ZONE?"
```

`QUARTS` binds the count. Only one, two and three quarters exist — a fourth
quarter is just the whole hour, so counts outside 1–3 are refused rather than
guessed.

---

## Tier 3 — the rich stuff

When the basics are solid, chronologia can read much more, each backed by its
own `.voc` files and construction orders. You don't need any of this to
contribute something useful, but here's where to look:

- **Seasons** — `season_spring.voc`, `season_summer.voc`, … (plus a
  `hemisphere` setting in `lang.json` for southern-hemisphere languages).
- **Eras** — "44 BC", "1492 AD": `marker_bc.voc`, `marker_ad.voc`.
- **Weekends** — `special_weekend.voc` (and the `weekend_start` setting for
  languages whose weekend is Friday–Saturday).
- **Quarters, ISO weeks, decades, fuzzy periods** ("early 90s") — see the
  constructions in an existing full language like `en/lang.json`.
- **Holidays** — you do **not** list these by hand. Holiday names come
  automatically from the shared holidays engine once your language code is
  known to it. See [civil-holidays.md](civil-holidays.md).
- **Non-Gregorian calendars** (Islamic, Hebrew, …) — use
  `month_<calendar>_<n>.voc`, e.g. `month_islamic_civil_9.voc` for Ramadan.
  See [calendars.md](calendars.md) for the calendar names.

The best way to learn Tier 3 is to open a mature language (`en`, `de`, `pt`)
and copy the pattern for the one feature you want.

---

## Tier 4 — recurrence ("every Friday", "the third Tuesday of every month")

A locale that stops at Tier 3 can read a single date, but not a *repeating*
one — "every Friday", "daily at 9", "the third Tuesday of every month" all
name a rule, not a single day, and that rule is the RFC 5545 `RRULE` grammar
covered in [recurrence.md](recurrence.md). This tier is what teaches your
language the words that name a recurrence; the RRULE machinery itself is
shared engine code, so — same as everywhere else in this guide — you are
only supplying vocabulary.

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
| `marker_freq_biweekly.voc` | "biweekly" / "fortnightly" — read as *every two weeks*, the more common sense (Merriam-Webster's usage note), not "twice a week" |
| `marker_freq_quarterly.voc` | "quarterly" — every three months |

### The recurrence-specific markers

| File | Put in it |
|---|---|
| `marker_recur_once.voc` | "once" (as in "once a week") |
| `marker_recur_per.voc` | "per" (as in "twice per month") |
| `marker_recur_for.voc` | "for" (as in "every Monday **for** 6 weeks" — bounds the rule with a `COUNT`) |
| `marker_until.voc` | "until" / "till" (as in "every Friday **until** June" — bounds the rule with an `UNTIL`) |
| `marker_weekday.voc` | the class noun "weekday(s)" (as in "every weekday", distinct from any one named weekday) |
| `marker_recur_habitual.voc` | (optional) a habitual preposition some languages use instead of "every" before a weekday — Portuguese marks it with `à` / `às` / `ao` / `aos` ("**à** segunda" = "on Mondays, habitually") |

`special_weekend.voc` (Tier 3) and the weekday/month files (Tier 1) do double
duty here — "every weekend", "every Friday", and "the third Tuesday of
November" all resolve through the same weekday and month vocabulary you
already wrote; there is nothing new to add for those.

With these files in place, chronologia reads "every Friday", "every other
week", "daily", "once a week on Monday", "the last Monday of May", and the
bounded forms "every Monday for 6 weeks" / "every Friday until June" in your
language, resolving to the same `Recurrence` object [recurrence.md](recurrence.md)
describes — worth reading if you want to see what the rule looks like once
your words are folded onto it.

---

## `lang.json` explained gently

`lang.json` is the one non-`.voc` file. It is a small **settings** file that
tells chronologia which sentence shapes your language uses and a few calendar
conventions. You will almost always start by copying an existing one.

It has four parts worth understanding:

**1. `tokenizer`** — three on/off switches for how text is chopped into
words. Most languages leave them all `false`. (`split_contractions` splits
words like French *l'année*; `ordinal_dot` treats "3." as an ordinal, used in
German; `dotted_date` reads the continental numeric date "15.06.2020" as one
date, and belongs to every language whose everyday written date has that
shape — German, Russian, Polish, Czech, Finnish, Turkish, Dutch and their
neighbours — but not to a language that writes the numeric date only with
slashes.)

**2. `constructions`** — this is the heart of it. A **construction** is a
*recipe* for one kind of date phrase, and each recipe lists the **word order**
your language uses. An order is written as a short sequence of **slots**
(uppercase names for "a thing that goes here") and **connector words**
(lowercase, matched against a `.voc` file). Read the uppercase names as
placeholders. For example, from Malay:

```text
"calendar_date": {
  "orders": [
    "DAY MONTH YEAR?",     ← "17 July 2026"  (day, then month, then optional year)
    "MONTH DAY? YEAR?"     ← "July 2026" or "July 17 2026"
  ]
}
```

- `DAY`, `MONTH`, `YEAR` are **slots** — chronologia fills them from the
  numbers and month words in the sentence.
- A trailing `?` means "**optional**" — `YEAR?` reads a year if one is present,
  but the phrase still works without it.
- A relative offset like Malay "3 days ago" uses the order
  `"NUM UNIT MARKER"` — a number, then a unit word, then a direction marker
  (`ago`). English says the marker differently ("in 3 days"), so English lists
  a different order. **This is the main thing you adjust for your language: the
  word order.** If your language puts the month before the day, list
  `MONTH DAY`; if after, list `DAY MONTH`. You are describing your grammar, not
  inventing it.

The safest approach: copy the `constructions` block from the language closest
to yours, then reorder the slots inside each order to match how *your* language
actually arranges the words. If a construction uses words your language doesn't
have, just remove that construction — chronologia checks on load that every
recipe has the words it needs, and will tell you clearly if one is missing its
vocabulary.

**3. `conventions`** — a handful of calendar facts:

- `week_start` — `"monday"` or `"sunday"`.
- `dmy` — `true` if your language writes day-before-month (15/06), `false` for
  month-before-day (06/15).
- `weekend_start` — first day of the two-day weekend as a Monday=0 number
  (`5` = Saturday for most of the world; `4` = Friday for Israel and much of the
  Arab world).
- the clock flags from Tier 2 (`bare_half_past`, `bare_half_to`, …).
- `hemisphere` — `"south"` if seasons should be flipped, else leave it out.

**4. `hook`** — this is the only line that names a bit of code, and most
languages that need it are already covered. The hook is the **number-folding
function**: it turns spelled-out numbers ("three", "twenty-five") into digits
before matching. If your language is in the supported list (next section), you
point `hook` at the ready-made function for it, exactly like Malay does:

```text
"hook": "chronologia.extract.numfold:fold_ms"
```

If your language has no number backend yet, leave `hook` out entirely —
chronologia will still read digits perfectly, just not spelled-out number
words. Nothing else in `lang.json` depends on the hook.

---

## Numbers: digits vs spelled-out words

chronologia reads **digits** (`3`, `2027`, `15:30`) in every language with no
setup at all. The only thing that needs help is **spelled-out** numbers —
"three days ago" instead of "3 days ago".

Turning "three" into `3` is a separate, specialised job done by a companion
library called **ovos-number-parser**. chronologia leans on it so it doesn't
have to re-learn every language's number words. A language is covered if
ovos-number-parser ships a `extract_number_<your code>` function for it.

**Languages with a number backend today** (spelled-out numbers work):

> ar, az, bg, ca, cs, da, de, el, en, es, et, eu, fa, fi, fr, fy, gl, he, hr,
> hu, id, it, kab, ms, nb, nl, nn, pl, ru, sk, sl, sv, tr, uk

**If your language is on that list:** set `hook` in `lang.json` to the matching
`fold_<code>` function (see the existing languages for the exact name — most
reuse a shared folder).

**If your language is *not* on that list:** that is completely fine. Leave
`hook` out, ship your language with digit reading only, and it still passes all
its tests. Adding spelled-out number support is a separate contribution to
ovos-number-parser — a good follow-up, not a blocker. If you'd like to add it,
ask the maintainers where to start.

---

## Testing — how you prove it works

This is the most important section, and it is friendlier than it sounds.

chronologia follows a simple discipline: **you don't get to claim your language
works — you show it, with examples.** For every language there is a folder of
tests at `test/nl_corpus_<your code>/` full of *real sentences a person would
say*, each paired with the exact date it should mean. The test runner checks
that chronologia agrees. This is the project's guarantee of quality, and it is
required: **a new language must ship these examples.**

Two things make it approachable:

**1. The examples are just phrases and expected answers.** Here is a real one
from the Malay corpus — you can see it's readable even if you don't code:

```text
("esok",           1)   # "esok" (tomorrow) should be 1 day after today
("semalam",       -1)   # "semalam" (yesterday) should be 1 day before today
("hari ini",       0)   # "hari ini" (today) should be today
```

You write the phrase in your language and the answer you *know* is right as a
native speaker. That's the whole idea.

**2. The parity block — proving the *meaning* matches English.** Alongside the
examples, each language ships a small list called the **parity block**
(`parity.py`), which pairs a phrase in your language with the English phrase
that means the same thing:

```text
('minggu depan', 'next week'),
('esok',         'tomorrow'),
('17 julai 2026','july 17 2026'),
('44 sm',        '44 bc'),
```

The test runner reads *both*, resolves them, and insists they land on the
**exact same span**. This is a powerful, honest check: it proves your Malay
"next week" means the same instant of time as English "next week", with no
hand-tuning. Every language needs **at least 25** such pairs, and the corpus as
a whole needs **at least 100 example cases** total (across all the little
`test_nl_*.py` files). The easiest path is to copy the structure of an existing
corpus folder (Malay's `nl_corpus_ms/` is a good, compact model) and translate
the phrases.

**3. The confusables file — words that only *look* like dates.** A mature corpus
also includes a `test_nl_confusables.py` listing sentences with words that
resemble dates but aren't meant that way — a month name used as a person's
name, a "second" that means "a moment", not the time unit. These assert that
chronologia does *not* wrongly grab them. This one is worth adding once the
happy path works, because it catches over-eager matching.

### Running your language's tests

From the top of the repository, run just your language's tests like this:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest test/nl_corpus_<your code>/ -q
```

(The `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` part keeps unrelated plugins from
interfering. In this project's shared environment the interpreter is
`~/.venvs/ovos/bin/python`; use whichever Python has chronologia installed.)

A green run — no failures — means your language works. That's the moment you're
aiming for.

---

## The citation rule — and why it matters

Here is the rule the project cares about most, and the reason for it.

Every word you add — a month name, a marker, a season word — should be traceable
to a **real source**: a dictionary, a published grammar, a language authority,
or your own confirmation as a native speaker. And you *write that source down*,
as a `#` comment at the top of the `.voc` file.

**Why.** chronologia is used to read dates people wrote, in dozens of languages
its maintainers cannot all speak. The only thing that makes a Kabyle or Tagalog
month list trustworthy to someone who doesn't speak it is a **source they can
check**. A citation turns "someone typed this in" into "this is documented."
That is the whole difference between data people can rely on and data they
can't.

**How.** Put one or two comment lines at the top of the file:

```text
# Month names from the Dewan Bahasa dan Pustaka standard dictionary (2015 ed.).
# https://prpm.dbp.gov.my/
januari
```

**A native speaker's confirmation counts** — you are a valid source for your own
language. Just say so plainly:

```text
# Colloquial forms confirmed by a native speaker, 2026.
# Standard forms cross-checked against Wiktionary.
esok
```

The goal is not bureaucracy. It's that the next person — maintainer or
contributor — can see *where this came from* and trust it.

---

## Submitting your work

You don't need to be a git expert. The gentle version:

1. **Fork** the repository on GitHub (a "fork" is your own copy) using the Fork
   button.
2. **Create a branch** with a clear name like `add-language-<your code>`.
3. **Add your files** — the new `chronologia/locale/<your code>/` folder and the
   new `test/nl_corpus_<your code>/` folder.
4. **Run the tests** for your language (the command above) and make sure they're
   green.
5. **Open a pull request** back to the project, describing the language you
   added and citing your sources.

If any of that is unfamiliar, say so in an issue first — the maintainers would
much rather help you land a good language than have you struggle with git alone.
Check for a `CONTRIBUTING` guide in the repository for the project's exact
preferences on branches and commits.

---

## A worked mini-example: adding one month spelling

Let's walk the smallest possible change end to end, so you can see the whole
loop. Suppose Malay already works, but you notice that April is missing a common
spelling your region uses, and you want to add it.

**Step 1 — find the file.** April is month 4, so the file is
`chronologia/locale/ms/month_4.voc`. Open it in a text editor.

**Step 2 — add the surface and its source.** Add your spelling on its own line,
lowercase, and note where it comes from:

```text
# Standard month name from Dewan Bahasa dan Pustaka.
# Regional spelling confirmed by a native speaker, 2026.
april
```

**Step 3 — add a test that proves it reads.** Open (or find) the Malay calendar
test, `test/nl_corpus_ms/test_nl_calendar.py`, and add a case using your new
spelling in a full date, with the date you know it means.

**Step 4 — run it.** From the top of the repo:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest test/nl_corpus_ms/ -q
```

**Step 5 — see green.** No failures means chronologia now reads your spelling
and still reads everything it read before. You're done — commit and open a pull
request.

That five-step loop — *find the file, add the word with a source, add a test,
run it, see green* — is the entire rhythm of contributing a language, whether
you're fixing one spelling or adding a whole new locale from scratch.

---

## Seeing it work in code

Once your locale is in place, this is what reading a date looks like — the same
call works for every language, yours included:

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

Swap `"en"` for your language code and `"next friday"` for the equivalent phrase
in your language, and — once your locale ships those words — it resolves to the
very same Friday. That is the whole promise of adding a language: the shared
engine already knows what dates *mean*; you are simply teaching it the words
your language uses to say them.

---

*Ready for the technical reference? The
["How a language works — and how to add one"](extraction.md) section of the
extraction guide is the compact, developer-facing companion to this page.*
