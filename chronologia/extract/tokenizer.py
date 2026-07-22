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

_ISO = r"\d{4}-\d{2}-\d{2}"
_CLOCK = r"\d{1,2}:\d{2}(?::\d{2})?"
_NUM = r"\d+(?:\.\d+)?"
# a timezone acronym with an optional fixed signed offset kept as ONE token so
# the sign survives ("utc+2", "gmt-5", bare "utc"); language-neutral, like the
# ISO / clock literals above.  Named-city zones are deliberately out of scope.
_ZONE = r"(?:utc|gmt)(?:[+-]\d{1,2}(?::?\d{2})?)?"


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
        parts = [_ISO, _CLOCK, _ZONE]
        if modes.ordinal_dot:
            # a digit run followed by a dot that is not a decimal point
            parts.append(r"\d+\.(?!\d)")
        parts += [_NUM, word]
        self._re = re.compile("|".join(parts), re.UNICODE)

    def tokenize(self, text: str) -> Tuple[Token, ...]:
        if not text:
            return ()
        tokens = []
        for i, m in enumerate(self._re.finditer(text.lower())):
            raw = m.group(0)
            # match offsets are into ``text.lower()``; for the Latin-script
            # locales this engine serves, lower-casing is length-preserving, so
            # they are also the offsets into the original ``text``.
            cs, ce = m.start(), m.end()
            is_literal = (re.fullmatch(_ISO, raw) is not None
                          or re.fullmatch(_CLOCK, raw) is not None)
            if not is_literal and re.match(r"\d", raw):
                digits = raw.rstrip(".")
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
