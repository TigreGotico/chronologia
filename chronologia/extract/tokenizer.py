"""Text -> tuple[Token] with per-language mode flags.

Two invented-word-friendly modes matter for the synthetic locale and the
first migration wave:

* ``split_contractions`` -- an apostrophe acts as a token separator
  (``d'aujourd'hui`` -> ``d aujourd hui``) rather than an in-word letter.
* ``ordinal_dot`` -- a digit run followed by a dot (``5.``) is one numeric
  token, the trailing dot stripped (German-style ordinals).

Numbers are detected as digit runs (optionally decimal); spelled-number
normalisation is a separate binding applied by the normaliser, so the
tokenizer stays language-neutral.  ISO date literals (``2017-06-30``) are
kept as a single token for the ``iso_date`` pre-pass.
"""
from __future__ import annotations

import re
from typing import Tuple

from chronologia.extract.model import Token, TokenizerModes

# Typography a real user pastes in -- from a word processor, a CJK keyboard,
# a Romance-language document -- that is the same character as an ASCII one to
# the eye but a different codepoint to the matcher.  Left unmapped each is a
# silent wrong: a curly "o’clock" fails the straight-apostrophe vocab lookup,
# a fullwidth "5：30" strands its minutes, a no-break space splits a date in
# two.  A TARGETED table (never blanket NFKC) is used on purpose: every entry
# below is a strict 1:1 codepoint substitution, so the pass is
# length-preserving and the character offsets the tokenizer hands downstream
# (used to slice the remainder out of the ORIGINAL text) stay valid.  NFKC is
# neither length-preserving (½ -> "1⁄2", ² -> "2", ﷺ -> a long expansion) nor
# safe for the scripts this engine serves -- it would recompose combining
# marks on month names and could disturb RTL text -- so it is rejected.
# Arabic-Indic digits (٠-٩) are deliberately absent: they are NOT fullwidth,
# the numeric tokenizer already reads them, and mapping them would be a
# regression, not a fix.
_UNICODE_FOLD = {
    # curly single quotes / apostrophe / prime -> straight apostrophe
    "\u2018": "'", "\u2019": "'", "\u02bc": "'", "\u2032": "'",
    # curly / low double quotes -> straight quote
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u201f": '"',
    # fullwidth digits U+FF10..FF19 -> ASCII 0..9
    **{chr(0xFF10 + d): str(d) for d in range(10)},
    # fullwidth punctuation used to glue date/clock components -> ASCII
    "\uff1a": ":", "\uff0c": ",", "\uff0e": ".", "\uff0f": "/",
    "\uff0d": "-", "\uff01": "!", "\uff1b": ";",
    # no-break, narrow-no-break, figure, thin spaces, ideographic space
    # -> ordinary space
    "\u00a0": " ", "\u202f": " ", "\u2007": " ", "\u2009": " ",
    "\u3000": " ",
    # Turkish/Azeri/Crimean-Tatar capital dotted I (U+0130) -> ASCII 'i'.
    # Its str.lower() expands to 'i' + COMBINING DOT ABOVE (two codepoints),
    # which would break the length-preserving invariant the tokenizer relies on
    # (offsets into the lower-cased text must index the original one-for-one, or
    # every remainder slice after an \u0130 is off by one).  Folding it here keeps the
    # later .lower() length-preserving.
    "\u0130": "i",
}
_UNICODE_TABLE = str.maketrans(_UNICODE_FOLD)
# The zero-width non-joiner (U+200C) and joiner (U+200D) are *intra-word*
# formatting marks: Persian orthography writes a compound word's parts with a
# ZWNJ to suppress the cursive join ("پنج‌شنبه" Thursday, "سه‌شنبه" Tuesday),
# yet the very same word is routinely typed without it ("پنجشنبه").  Both
# spellings are the same word, so the ZWNJ/ZWJ is dropped from the token's
# MATCHING key while the raw surface (and therefore the character offsets the
# tokenizer hands downstream) keeps it verbatim -- offsets are taken from
# ``char_start``/``char_end`` into the original text, never from ``text``, so
# folding the key is offset-safe.  The loader tokenises its vocab surfaces
# through this same class, so a voc entry written WITH a ZWNJ is registered in
# its folded (ZWNJ-free) form as well; a user's either spelling then matches.
_INTRAWORD_ZW = dict.fromkeys((0x200C, 0x200D))
# the º / ª ordinal indicators (Spanish/Portuguese/Italian "1º de abril" = the
# 1st) glued to a digit, with the optional RAE dot ("1.º"): read as the day
# number by dropping the indicator.  Only after a digit, so a bare "Nº" or a
# lone ª is untouched.  The replacement pads with spaces of equal length,
# keeping the pass length-preserving like the table above.
_ORDINAL_IND = re.compile(r"(\d)(\.?[ºª])")


def normalise_unicode(text: str) -> str:
    """Length-preserving typographic fold applied before tokenizing.

    Every substitution is one codepoint for one codepoint (or an equal-length
    run for the ordinal indicator), so character offsets into the result line
    up exactly with the original text the remainder is later sliced from.
    """
    text = text.translate(_UNICODE_TABLE)
    return _ORDINAL_IND.sub(lambda m: m.group(1) + " " * len(m.group(2)), text)

# ISO-8601 year-first calendar literals, kept whole: a full date -- dash
# ("2017-06-30"), slash ("2024/03/06", 1-2 digit month/day) or dot
# ("2020.06.15", the form Hungarian mandates) -- and the
# day-less year-month ("2024-03", dash only, as ISO-8601 writes it).  A
# 4-digit-leading, year-first surface is unambiguously Y-M-D in EVERY
# locale, so -- unlike the day/month-ambiguous _NUMDATE below -- no
# per-locale dmy swap ever applies here.  The four-digit lead and required
# separator keep a bare year, fraction or decimal from ever matching.
#
# Every alternative ends in a ``(?!\d)`` boundary guard, and this is what keeps
# the literal honest rather than merely tidy.  Without it a digit run that is
# NOT an ISO literal still matches a prefix of one and the tail is stranded in
# the remainder: "1914-1918", an ordinary written year range, matched the
# year-month alternative as "1914-19" (month 19, so the whole reading was
# refused) and "2026-071" read as July 2026 with a stray "1" left over.  The
# guard makes the literal all-or-nothing, so a digit run that continues past
# the shape falls through to the plain-number rule where it belongs.
# The year-month alternative additionally refuses a following "-<digit>": that
# is the head of a longer dashed run ("2026-07-244"), and reading a month out
# of its first seven characters is the same stranded-tail wrong.
# The dotted alternative is the Hungarian civil form: the Academy's
# orthography (AkH. 297) and MSZ ISO 8601 both write the date year-first with
# dots, "2020.06.15".  It needs no per-locale switch for the same reason the
# dashed and slashed forms do not -- a four-digit lead is year-first
# everywhere -- and it cannot collide with a decimal number or a thousands
# group, because both of those are refused by the two required dots and by the
# "(?!\.\d)" guard, which keeps the literal from reading the head of a longer
# dotted run ("1990.12.31.5" is not a date with a spare fraction).
_ISO = (r"\d{4}-\d{2}-\d{2}(?!\d)|\d{4}/\d{1,2}/\d{1,2}(?!\d)"
        r"|\d{4}\.\d{1,2}\.\d{1,2}(?!\d)(?!\.\d)"
        r"|\d{4}-\d{2}(?!\d)(?!-\d)")
# the ISO-8601 week designator (ISO 8601 §4.4.4.2): ``YYYY-Www`` for the week
# itself and ``YYYY-Www-D`` for one weekday inside it (D = 1..7, Monday..Sunday).
# The literal ``W`` is what makes this shape unmistakable -- it can never be
# confused with the all-digit _ISO calendar literal or with _NUMDATE, so the
# three stay mutually exclusive by construction.  The standard writes ``W``
# uppercase; lowercase ``w`` is accepted as permissive input (the tokenizer
# lower-cases before matching anyway) and collides with nothing, since no other
# literal shape allows a letter between two digit runs.  Matched AHEAD of _ISO
# and _NUMDATE so the week designator is never split into a bare year plus
# leftovers -- the silent-wrong reading this literal exists to prevent.
# The standard pads the week number to two digits, but ``2026-W1`` is written
# often enough that refusing it re-opened exactly that silent wrong: the ``W1``
# was stranded and the bare year 2026 came back as a confident answer.  One or
# two digits are therefore accepted, and the closing ``(?!\d)`` keeps the
# padded form from matching only a prefix of a longer run ("2026-W123" names no
# week and must not read as week 12).
_ISOWEEK = r"\d{4}-[wW]\d{1,2}(?:-\d)?(?!\d)"
# a numeric slash/dash separated date ("12/11/2024", "5-6-24"): two 1-2 digit
# components and a 2-4 digit year, kept whole so the matcher binds it as one
# ``NUMDATE`` slot.  Requiring the third (year) component and two separators
# keeps a bare fraction/score ("1/2") from ever reading as a date.  The
# component->day/month order is a resolve-time, per-locale (dmy) decision; the
# tokenizer stays language-neutral.
# same all-or-nothing boundary guard as _ISO: "12/11/20244" is not a date with
# a spare digit, it is not a date at all.
_NUMDATE = r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}(?!\d)"
# the same date written with dots, "15.06.2020" -- the official civil form of
# German (DIN 5008), Russian and Ukrainian (GOST R 6.30-2003), Polish, Czech
# and Slovak (CSN 01 6910), Finnish and Estonian (SFS 4175, which drops the
# leading zeros: "15.6.2020"), Turkish (TDK), Dutch, Danish, Norwegian,
# Slovene, Croatian and Romanian.  It is enabled by the per-language
# ``dotted_date`` tokenizer mode rather than always, because a locale that has
# no dotted convention must keep reading "06.15.2020" as the two numbers it is;
# English in particular writes the dot in neither order.
#
# The dot was excluded here for a long time, on the grounds that it collides
# with the decimal-number and ordinal-dot shapes.  The collision is real but
# the exclusion did not produce the refusal it was meant to: "15.06.2020" fell
# through to the bare-number rule, the year matched alone, and the caller got a
# confident whole-year span with "15.06" stranded in the remainder -- silently
# wrong for the most ordinary way most of Europe writes a date.  Three
# components with two dots is what keeps the shape apart from both colliders: a
# decimal ("2.5") and a thousands group ("1.000", "1.000.000" in German) never
# carry two dots with a 1-2 digit head and a 2-4 digit tail, and an ordinal dot
# ("15. Juni") is followed by a space and a word, never by a digit.  The literal
# is matched ahead of the ordinal-dot and bare-number rules so the whole date
# binds as one token instead of being eaten piecewise.
#
# Both boundary guards are load-bearing, exactly as in _ISO.  "(?!\d)" refuses
# a longer digit run ("15.06.20201"), and "(?!\.\d)" refuses the head of a
# longer dotted run, so "1.2.3.4" and "1.15.06.2020" name no date at all
# instead of yielding a date plus a stranded tail.
# The same national standards that write "15.06.2020" write it in running
# prose with a single space after each dot -- "15. 6. 2020" is the everyday
# German (DIN 5008), Czech/Slovak (CSN/STN 01 6910), Finnish, Russian etc.
# form.  Without the optional space the three dotted-with-space pieces fall
# apart on the whitespace split into "15.", "6." and "2020"; the ordinal-dot
# rule ate the first two, the year matched alone, and the caller got a
# confident whole-year span with "15. 6." stranded -- the very silent wrong the
# space-less literal exists to end.  A single optional space after each interior
# dot keeps the shape one token.  The 2-4 digit year still anchors the pattern,
# so a bare "15. 6." (two ordinals, no year) matches nothing and fabricates no
# date, and the trailing boundary guards are unchanged.
# The leading "(?<!\d\.)" refuses a date whose head is glued to a preceding
# "digit." -- so "1.15.06.2020" stays a malformed run (its "15.06.2020" tail
# does not bind).  It is deliberately NOT extended to a spaced "digit. " form:
# a numbered-list item before a real date -- "1. 15.06.2020", "5. 5.6.2020" --
# is a genuine date the guard must let through, not shred.
_DOTDATE = r"(?<!\d\.)\d{1,2}\. ?\d{1,2}\. ?\d{2,4}(?!\d)(?!\.\d)"
# what the ``NUMDATE`` slot accepts: either separator style.  The matcher and
# the resolver read this one name, so there is a single source of truth for the
# shape and the day/month order stays the locale's ``dmy`` decision.
_NUMDATE_ANY = f"(?:{_NUMDATE})|(?:{_DOTDATE})"
# a written fraction, "1/2", "3/4" -- two 1-2 digit components and exactly one
# separator, matched AFTER ``_NUMDATE`` so a real date ("3/4/2025") still wins
# the alternation at the same start position (``_NUMDATE`` requires the third,
# year, component; a bare two-part slash run never satisfies it and falls
# through to this literal instead).  Without a dedicated literal the '/' matches
# nothing in the token regex, so "1/2 hour" tokenized as the two bare numbers
# "1" and "2" with nothing to say they were EVER joined; the unit-count fold
# then bound the *second* number to the unit ("2 hours") and stranded the
# first as an unexplained remainder ("1") -- a silent misread, not a refusal.
# The value is read as an ordinary decimal (``num/den``) by the same numeric
# branch below, so it composes with a following unit exactly like "0.5 hour"
# already does. No denominator allow-list is enforced: an oddball fraction
# ("5/7 hour") is arithmetically well-defined and is read the same as any other
# decimal count would be -- the fold's job is to stop the slash from being
# silently DROPPED, not to police which fractions are sensible durations.
# The trailing "(?!/\d)" keeps this from swallowing the HEAD of a broken
# three-component date whose year overflowed ("12/11/20244" -- _NUMDATE's
# year component is capped at 4 digits and its own "(?!\d)" guard refuses
# the 5th, so it falls through here).  Reading "12/11" as a fraction in that
# wreckage would strand "20244" as an unrelated number instead of the
# all-or-nothing refusal the broken-date literal is designed to produce
# (see ``_year_inside_a_broken_date``): the whole run must split into its
# three bare numerals, not two of them plus a stray "fraction".
_SLASHFRAC = r"\d{1,2}/\d{1,2}(?!\d)(?!/\d)"
_CLOCK = r"\d{1,2}:\d{2}(?::\d{2})?(?!\d)"
_NUM = r"\d+(?:\.\d+)?"
# a timezone acronym with an optional fixed signed offset kept as ONE token so
# the sign survives ("utc+2", "gmt-5", bare "utc"); language-neutral, like the
# ISO / clock literals above.  Named-city zones are deliberately out of scope.
_ZONE = r"(?:utc|gmt)(?:[+-]\d{1,2}(?::?\d{2})?)?"
# a bare RFC/ISO signed numeric offset kept as ONE token ("-0500", "+05:30",
# "-08:00") so the sign survives to resolve time.  The hour is bound 00..14 and
# the minute 00..59 -- the real range of a UTC offset -- so a signed year or a
# hyphenated year ("-1918", "mid-2017") is NOT mistaken for an offset.  The
# negative lookbehind additionally keeps a tight numeric range ("1400-1000")
# from being read as an offset (the sign must not follow a digit); the trailing
# guard forbids a fifth digit.
_NUMOFFSET = r"(?<!\d)[+-](?:0\d|1[0-4]):?[0-5]\d(?!\d)"
#: the characters that glue the components of a written date together.
_DATE_SEPS = "./-"


def _adjacent_group(text: str, sep: int, step: int) -> int:
    """How many digits sit on the far side of the separator at ``sep``.

    Zero when there is no separator there or nothing but non-digits beyond it,
    which is how a trailing "1914-" or an ordinary hyphenated word tells itself
    apart from a date component.
    """
    if not 0 <= sep < len(text) or text[sep] not in _DATE_SEPS:
        return 0
    i, n = sep + step, 0
    while 0 <= i < len(text) and text[i].isdigit():
        n += 1
        i += step
    return n


def _year_inside_a_broken_date(text: str, start: int, end: int,
                               digits: str) -> bool:
    """Is this four-digit-or-longer numeral visibly part of a date-shaped run?

    A numeral that is glued by a dot, slash or dash to a digit group of some
    other length is a component of a date somebody wrote, not a year standing
    on its own.  When the run around it failed to bind as a date literal --
    because the language has no dotted convention ("15.06.2020" in French),
    because a component names nothing real ("31.02.2020"), or because the digit
    run continues past the literal's shape ("15.06.20201", "2026-071") -- the
    honest answer is that nothing was read.  Reading the year alone out of the
    wreckage is the same silent wrong the dotted literal exists to end: the
    caller gets a confident whole-year span and no sign that the day and the
    month were dropped on the floor.  So the numeral gives up its number
    reading entirely and binds no slot, and the phrase resolves to nothing.

    The one glued shape that is not wreckage is the written year range: a tight
    hyphen between two four-digit numbers, "1914-1918", where both sides are
    years and neither is a day or a month.  No calendar component but a year is
    written with four digits, so an equal-length four-digit neighbour is the
    exact and only exemption.
    """
    if len(digits) < 4 or not digits.isdigit():
        return False
    left = _adjacent_group(text, start - 1, -1)
    # ``end`` is the surface's char_end, not ``start + len(digits)`` -- a
    # thousands-grouped surface ("12,000") is longer than its digit string
    # ("12000"), so the right-neighbour must be probed just past the SURFACE.
    right = _adjacent_group(text, end, 1)
    return bool((left and left != 4) or (right and right != 4))


class Tokenizer:
    """Configured once from a language's :class:`TokenizerModes`."""

    def __init__(self, modes: TokenizerModes):
        self.modes = modes
        # letters only; apostrophes separate words when contractions split,
        # otherwise they stay inside the word
        # letters; when contractions are NOT split, an apostrophe glues
        # letter runs into one word (d'aujourd'hui stays whole)
        # a zero-width non-joiner / joiner (‌ / ‍) is an *intra-word*
        # formatting mark in Persian and other scripts (سه‌شنبه "Tuesday" is one
        # word), so it always glues letter runs -- never a token boundary.
        # the Hebrew geresh ׳ (U+05F3) and gershayim ״ (U+05F4) are the numeral
        # marks of gematria (תשפ״ה, ה׳תשפ״ה): they sit BETWEEN letters of a
        # single number-word, so -- like the apostrophe / ZWNJ above -- they
        # glue the letter runs into one token rather than splitting it.  They
        # occur only in Hebrew, so listing them is inert for every other locale.
        # Devanagari writes a syllable as a base consonant plus COMBINING vowel
        # signs, the nukta and the virama -- मार्च is म + ा + र + ् + च, and
        # फ़रवरी is फ + ़ + रवरी.  Those marks are Unicode categories Mn and Mc,
        # which ``\w`` (and therefore ``[^\W\d]``) does not match, so without
        # them in the letter class every Devanagari word ends at its first
        # matra and the token stream is a run of bare consonants.  They are
        # part of the word, not a glue character, so they join the letter class
        # itself.  Ranges are the Devanagari block's sign/matra subranges
        # (Unicode 16.0 chart U+0900): U+0900-0903 candrabindu/anusvara/
        # visarga, U+093A-094F matras + nukta + virama, U+0951-0957 accents and
        # additional marks, U+0962-0963 vocalic-l matras.  The digits
        # U+0966-096F are deliberately excluded -- they are numbers, and the
        # numeric rule below already reads them.  Inert for every script that
        # writes no combining mark.
        # Thai writes a syllable as a base consonant plus COMBINING vowel
        # signs and tone marks -- วันจันทร์ is ว + ◌ั + น + จ + ◌ั + น + ท + ร +
        # ◌์ -- and those marks are Mn, so without them in the letter class
        # every Thai word ends at its first vowel sign and "วันจันทร์" arrives
        # as five bare-consonant fragments.  Ranges are the Thai block's mark
        # subranges (Unicode 16.0 chart U+0E00): U+0E31 mai han-akat,
        # U+0E34-0E3A the sara/nikhahit vowel signs plus phinthu, and
        # U+0E47-0E4E maitaikhu, the four tone marks, thanthakhat, nikhahit
        # and yamakkan.  The baht sign U+0E3F, the fongman U+0E4F and the
        # Thai digits U+0E50-0E59 are deliberately excluded: a currency
        # symbol and a bullet are not letters, and the numeric rule below
        # already reads the digits.
        letter = r"(?:[^\W\d]|[ऀ-ःऺ-ॏ॑-ॗॢॣ]|[\u0e31\u0e34-\u0e3a\u0e47-\u0e4e])"
        zwj = r"(?:[‌‍׳״]" + letter + r"+)*"
        # a geresh can also be the mark on its OWN, trailing the letters
        # instead of sitting between two of them: that is how a SINGLE-LETTER
        # gematria numeral is written (א׳ = 1, ה׳ = 5), as opposed to a
        # multi-letter one where the (gershayim) mark sits before the last
        # letter (ט״ו = 15, כ״ט = 29) and so is already kept by ``zwj`` above.
        # Without this, a trailing geresh has nothing after it to glue to and
        # is dropped as a stray char, so ``is_gematria_numeral`` never sees
        # the mark and the single-letter numeral silently fails to fold.
        # Restricted to the real geresh/gershayim (not their ASCII '/"
        # fallbacks, which double as ordinary quote marks) so this stays
        # inert outside Hebrew -- an English/French trailing apostrophe or
        # closing quote is untouched.
        trailing_mark = r"[׳״]?"
        word = (letter + r"+" + zwj + trailing_mark
                if modes.split_contractions
                else letter + r"+(?:['’‌‍׳״]" + letter + r"+)*" + trailing_mark)
        # ISO and clock literals (2017-06-30, 15:30, 5:07:30) are kept whole,
        # ahead of the bare-number rule, so the matcher can bind them as one
        # slot; both are language-neutral, always-on lexical shapes.
        parts = [_ISOWEEK, _ISO, _NUMDATE, _SLASHFRAC, _CLOCK, _ZONE, _NUMOFFSET]
        if modes.dotted_date:
            # ahead of the ordinal-dot and bare-number rules below, so a
            # dotted date binds whole rather than being read as a number
            parts.insert(4, _DOTDATE)
        if modes.ordinal_dot:
            # a digit run followed by a dot that is not a decimal point.
            # ``ordinal_dot_max_digits`` (a per-locale fact) optionally caps
            # how wide that digit run may be -- see its docstring in
            # ``model.TokenizerModes``. Unbounded by default, matching every
            # ordinal_dot locale's original behaviour (a year-first dotted
            # date like Hungarian's "2026. június 20." needs the full
            # 4-digit run to keep its dot).
            cap = modes.ordinal_dot_max_digits
            parts.append(r"\d{1,%d}\.(?!\d)" % cap if cap else r"\d+\.(?!\d)")
        # The number rule is locale-aware: the SAME two characters group
        # thousands or mark the decimal in OPPOSITE roles per locale, so the
        # grouped surface binds as ONE token instead of being split into a
        # confident-but-wrong fragment.  A grouping run is one-or-more
        # exactly-three-digit groups after a 1-3 digit head; the decimal tail
        # is optional.  The plain "\d+" alternative (with only the decimal
        # tail) still matches an ungrouped run, so nothing that parsed before
        # stops parsing.  Both forms keep the whole surface in ``raw``; only
        # the VALUE string is transformed downstream, so char offsets are
        # untouched.
        # The whole alternation is wrapped in a non-capturing group with a
        # trailing ``(?!\d)`` so the guard binds to EITHER alternative once
        # this fragment is spliced into the bigger "|"-joined ``parts``
        # alternation below -- without the group, a bare trailing lookahead
        # would bind only to the last alternative here (the plain-number
        # one), leaving the grouped alternative free to match a truncated
        # prefix of a longer digit run.  With no lookahead, the grouped alternative is only required
        # to find ONE exactly-three-digit group and is free to stop there
        # even when more digits (with no separator) immediately follow --
        # so "5,2025" (a comma glued straight onto a 4-digit run, e.g. a
        # month/day date typed without a space, "march5,2025") greedily
        # matches as "5,202", folds to the number 5202, and stealthily
        # strands a bare "5" as its own token right after -- a US-style date
        # misread as the year 5202.  Requiring nothing to follow the whole
        # matched number keeps the grouped form working for real groupings
        # ("1,000 days") while forcing this glued-onto-more-digits shape to
        # fall through to the plain alternative instead, which stops at the
        # comma and leaves the ",2025" tail for the comma-glue guard below.
        if modes.decimal_comma:
            # Continental European: '.' groups thousands, ',' is the decimal.
            num = r"(?:\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)(?!\d)"
        else:
            # English (and he/ms): ',' groups thousands, '.' is the decimal.
            num = r"(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?!\d)"
        self._decimal_comma = modes.decimal_comma
        parts += [num, word]
        self._re = re.compile("|".join(parts), re.UNICODE)
        # Arabic-script native decimal/thousands separators (U+066B/U+066C)
        # map to this locale's Latin decimal/grouping char respectively --
        # opposite of each other, matching the decimal_comma convention.
        decimal_char = "," if modes.decimal_comma else "."
        grouping_char = "." if modes.decimal_comma else ","
        self._native_sep_table = str.maketrans({
            "٫": decimal_char,
            "٬": grouping_char,
        })
        # kept for the comma-glue guard in ``tokenize`` below: this locale's
        # grouping separator, the character whose presence right at a digit
        # run's edge -- with no space and no valid group either side -- marks
        # a glued-together numeral rather than two independent numbers.
        self._grouping_char = grouping_char

    def tokenize(self, text: str) -> Tuple[Token, ...]:
        if not text:
            return ()
        tokens = []
        # typographic fold first: curly quotes, fullwidth forms, no-break
        # spaces and digit+º/ª ordinal indicators become their ASCII twin
        # BEFORE matching.  It is strictly length-preserving (see
        # ``normalise_unicode``), so the offsets below still index the caller's
        # original text one-for-one and the remainder slices out verbatim.
        low = normalise_unicode(text).lower()
        if self._native_sep_table:
            # Arabic-script native separators (U+066B decimal, U+066C
            # thousands) are unambiguous by Unicode definition and only
            # occur in Arabic-script input, so a length-preserving 1-char
            # translation to this locale's Latin separator role is safe for
            # every locale -- it lets the Latin-only number regex above
            # recognise them without touching char offsets.
            low = low.translate(self._native_sep_table)
        # Set for one iteration when the PREVIOUS digit run was withdrawn
        # because it was glued straight onto this one by an invalid grouping
        # separator (see the comma-glue guard below) -- so this run, the
        # other half of the same glued mess, gets its number reading
        # withdrawn too instead of being read as a lone, unrelated number.
        suppress_glued_number = False
        for i, m in enumerate(self._re.finditer(low)):
            raw = m.group(0)
            # match offsets are into ``text.lower()``; for the Latin-script
            # locales this engine serves, lower-casing is length-preserving, so
            # they are also the offsets into the original ``text``.
            cs, ce = m.start(), m.end()
            # lower-casing is length-preserving for the Latin-script locales
            # here, so the same offsets index the ORIGINAL text: record whether
            # the surface opened with a capital (proper-noun positional guard).
            cap = cs < len(text) and text[cs] != low[cs]
            if re.fullmatch(_SLASHFRAC, raw) is not None:
                # "1/2", "3/4": read the two components as a single decimal
                # count (see ``_SLASHFRAC`` above for why the slash must not
                # be allowed to vanish between two bare-number tokens). A
                # zero denominator ("1/0") names no fraction -- withdraw the
                # number reading entirely rather than raise, same treatment
                # as any other unreadable numeral.
                num_s, den_s = raw.split("/")
                den = int(den_s)
                if den == 0:
                    tokens.append(Token(text=raw, raw=raw, index=i,
                                        char_start=cs, char_end=ce, cap=cap))
                else:
                    tokens.append(Token(text=raw, raw=raw, index=i,
                                        is_number=True, value=int(num_s) / den,
                                        char_start=cs, char_end=ce))
                continue
            is_literal = (re.fullmatch(_ISOWEEK, raw) is not None
                          or re.fullmatch(_ISO, raw) is not None
                          or re.fullmatch(_NUMDATE_ANY, raw) is not None
                          or re.fullmatch(_CLOCK, raw) is not None)
            if not is_literal and re.match(r"\d", raw):
                # Map the surface to a plain numeric string: strip the grouping
                # separator, map the decimal separator to '.'.  Which char is
                # which is the locale's convention -- comma-decimal locales
                # group with '.' and decimal with ',', dot-decimal locales the
                # reverse.  ``digits`` is therefore separator-free with '.' the
                # only (decimal) dot, so ``isdigit()`` is True exactly for an
                # integer surface and the year/overflow guards read it cleanly.
                surface = raw.rstrip(".")
                if self._decimal_comma:
                    digits = surface.replace(".", "").replace(",", ".")
                else:
                    digits = surface.replace(",", "")
                # A grouping separator glued directly onto this run's edge,
                # with a digit immediately on its far side and no space
                # anywhere, is either the tail of an invalid grouping this
                # run's own match already rejected (the ``(?!\d)`` guard
                # above stops the greedy grouped alternative from eating
                # into it) or, symmetrically, this run IS that tail.  Either
                # way, two adjacent digit runs separated only by a bare
                # grouping char is not a shape either locale's number rules
                # define -- en "5,2025" and "2,5" are not a valid thousands
                # grouping (wrong group width) and not a decimal (wrong
                # locale), so both sides give up their number reading rather
                # than have the matcher silently pick whichever side happens
                # to sit next to a unit/date word ("2,5 hours" -> 5h with the
                # 2 dropped; "march5,2025" -> a stray day-shaped 5 and an
                # unrelated year).  ``was_glued`` propagates the withdrawal
                # to this run when the PREVIOUS run set it; ``glue_ahead``
                # detects the same shape looking forward and arms it for the
                # next run.
                was_glued = suppress_glued_number
                suppress_glued_number = False
                glue_ahead = (ce < len(low) and low[ce] == self._grouping_char
                              and ce + 1 < len(low) and low[ce + 1].isdigit())
                if was_glued or glue_ahead:
                    if glue_ahead:
                        suppress_glued_number = True
                    tokens.append(Token(text=raw, raw=raw, index=i,
                                        char_start=cs, char_end=ce))
                    continue
                if _year_inside_a_broken_date(low, cs, ce, digits):
                    # the surface stays exactly as written -- only its number
                    # reading is withdrawn, so no year slot can bind it
                    tokens.append(Token(text=raw, raw=raw, index=i,
                                        char_start=cs, char_end=ce))
                    continue
                # A digit run longer than any real date/duration value
                # (year, day, count) carries no temporal meaning; withdraw its
                # number reading rather than let int()/float() choke on it
                # (CPython caps int(str) at 4300 digits -> ValueError).
                if len(digits.replace(".", "")) > 18:
                    tokens.append(Token(text=raw, raw=raw, index=i,
                                        char_start=cs, char_end=ce))
                    continue
                # A '-' glued directly to the digit run, with whitespace (not
                # string-start) before it, is a freestanding mid-sentence
                # signed number ("..., -3 times", "in -3 days") -- the number
                # regex only matches the digit run, so the sign falls between
                # tokens and would otherwise vanish, turning a negative into a
                # confident positive.  Three guards, all required:
                #  - the '-' must be glued to the digits (not a digit before
                #    it -- date ranges "1914-1918", ISO "2026-08-05"; not a
                #    letter before it -- zone offsets "utc-3"; not spaced --
                #    markdown bullets "- 3 days" keep their number reading);
                #  - whitespace, specifically, must precede the '-' -- a
                #    string-start '-3' ("-1918" typed bare) is bullet-like,
                #    the same as a spaced '- 3', and keeps its number reading;
                #  - the token appended just before this one must not itself
                #    be a number -- otherwise a spaced range typo ("1914
                #    -1918") would have its second year wrongly declined
                #    instead of read as the range's end.
                if (cs >= 2 and low[cs - 1] == "-" and low[cs - 2].isspace()
                        and not (tokens and tokens[-1].is_number)):
                    # fold the glued '-' into the token's own extent (not just
                    # a recorded flag, unlike the apostrophe case above) so
                    # ``render_remainder`` slices it back out of the original
                    # text instead of losing it in the gap between tokens.
                    signed_raw = text[cs - 1:ce]
                    tokens.append(Token(text=signed_raw, raw=signed_raw, index=i,
                                        char_start=cs - 1, char_end=ce))
                    continue
                value = float(digits) if "." in digits else int(digits)
                # an apostrophe immediately before the digit run is the strong
                # two-digit-year cue ("'42", "the '90s").  The apostrophe folds
                # to ASCII in ``low`` and is not part of the number match, so
                # record it here -- it is the only surviving trace.
                apos = cs > 0 and low[cs - 1] == "'"
                tokens.append(Token(text=raw.rstrip("."), raw=raw, index=i,
                                    is_number=True, value=value,
                                    char_start=cs, char_end=ce,
                                    apostrophe=apos))
            else:
                tokens.append(Token(text=raw.translate(_INTRAWORD_ZW), raw=raw,
                                    index=i, char_start=cs, char_end=ce, cap=cap))
        # re-index sequentially (finditer index already sequential, but be
        # explicit so callers can trust index == position)
        return tuple(Token(t.text, t.raw, i, t.is_number, t.value,
                           t.char_start, t.char_end, t.cap,
                           prev_cap=(tokens[i - 1].cap if i > 0 else False),
                           apostrophe=t.apostrophe)
                     for i, t in enumerate(tokens))
