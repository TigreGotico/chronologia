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
}
_UNICODE_TABLE = str.maketrans(_UNICODE_FOLD)
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
# date, and the two boundary guards are unchanged.
_DOTDATE = r"\d{1,2}\. ?\d{1,2}\. ?\d{2,4}(?!\d)(?!\.\d)"
# what the ``NUMDATE`` slot accepts: either separator style.  The matcher and
# the resolver read this one name, so there is a single source of truth for the
# shape and the day/month order stays the locale's ``dmy`` decision.
_NUMDATE_ANY = f"(?:{_NUMDATE})|(?:{_DOTDATE})"
_CLOCK = r"\d{1,2}:\d{2}(?::\d{2})?(?!\d)"
_NUM = r"\d+(?:\.\d+)?"
# a timezone acronym with an optional fixed signed offset kept as ONE token so
# the sign survives ("utc+2", "gmt-5", bare "utc"); language-neutral, like the
# ISO / clock literals above.  Named-city zones are deliberately out of scope.
_ZONE = r"(?:utc|gmt)(?:[+-]\d{1,2}(?::?\d{2})?)?"
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


def _year_inside_a_broken_date(text: str, start: int, digits: str) -> bool:
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
    right = _adjacent_group(text, start + len(digits), 1)
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
        zwj = r"(?:[‌‍][^\W\d]+)*"
        word = (r"[^\W\d]+" + zwj if modes.split_contractions
                else r"[^\W\d]+(?:['’‌‍][^\W\d]+)*")
        # ISO and clock literals (2017-06-30, 15:30, 5:07:30) are kept whole,
        # ahead of the bare-number rule, so the matcher can bind them as one
        # slot; both are language-neutral, always-on lexical shapes.
        parts = [_ISOWEEK, _ISO, _NUMDATE, _CLOCK, _ZONE]
        if modes.dotted_date:
            # ahead of the ordinal-dot and bare-number rules below, so a
            # dotted date binds whole rather than being read as a number
            parts.insert(3, _DOTDATE)
        if modes.ordinal_dot:
            # a digit run followed by a dot that is not a decimal point
            parts.append(r"\d+\.(?!\d)")
        parts += [_NUM, word]
        self._re = re.compile("|".join(parts), re.UNICODE)

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
        for i, m in enumerate(self._re.finditer(low)):
            raw = m.group(0)
            # match offsets are into ``text.lower()``; for the Latin-script
            # locales this engine serves, lower-casing is length-preserving, so
            # they are also the offsets into the original ``text``.
            cs, ce = m.start(), m.end()
            is_literal = (re.fullmatch(_ISOWEEK, raw) is not None
                          or re.fullmatch(_ISO, raw) is not None
                          or re.fullmatch(_NUMDATE_ANY, raw) is not None
                          or re.fullmatch(_CLOCK, raw) is not None)
            if not is_literal and re.match(r"\d", raw):
                digits = raw.rstrip(".")
                if _year_inside_a_broken_date(low, cs, digits):
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
                value = float(digits) if "." in digits else int(digits)
                tokens.append(Token(text=raw.rstrip("."), raw=raw, index=i,
                                    is_number=True, value=value,
                                    char_start=cs, char_end=ce))
            else:
                tokens.append(Token(text=raw, raw=raw, index=i,
                                    char_start=cs, char_end=ce))
        # re-index sequentially (finditer index already sequential, but be
        # explicit so callers can trust index == position)
        return tuple(Token(t.text, t.raw, i, t.is_number, t.value,
                           t.char_start, t.char_end)
                     for i, t in enumerate(tokens))
