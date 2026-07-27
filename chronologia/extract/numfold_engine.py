"""The single spelled-number fold engine shared by every language family.

Every family's fold does the *same* thing: scan a maximal run of
number-word tokens, read its value with the language's
``extract_number_<lang>`` back-end, and synthesise one digit
:class:`~chronologia.extract.model.Token` that preserves the run's character
extent (``char_start`` of the first token, ``char_end`` of the last).  The
only genuine variation is *data* -- which tokens count as number-words, which
back-end reads the value, and a few real per-family quirks:

* an internal connector inside a run (English "one hundred **and** five",
  Arabic "خمسة **و**عشرون", the Romance ``JOIN_WORD``);
* whether that connector survives into the text handed to the back-end
  (English strips "and"; the Romance/Semitic back-ends read theirs);
* a single-token surface the back-end rejects but a curated map resolves
  (Romance feminine ordinals, the Finnish/Estonian genitive and Greek/Basque
  hour forms);
* a token-stream pre-pass a family runs first (the Germanic word-map and
  ordinal-suffix merge, the Romance a.c./d.c. glue, the Basque case-suffix
  merge, the French elision split ...).

Those are the fields of :class:`NumberGrammar`; :func:`make_fold` turns a
grammar into the ``tuple[Token] -> tuple[Token]`` fold.  This module owns the
*only* copy of the run-scan algorithm and the *only* ``_reindex``.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable, Optional, Tuple

import re

from chronologia.extract.model import Token
from chronologia.extract import tokenizer as _tok

# The whole-literal shapes the tokenizer keeps as one non-number token: an ISO
# week designator, an ISO calendar literal, a numeric/dotted civil date and a
# clock.  A spelled-number fold must never re-read a number out of one of
# these -- its back-end will happily pull "15" out of the dotted date
# "15. 6. 2020" (the spaced civil form) or "2024" out of "2024/03", handing the
# caller a number the tokenizer deliberately declined to expose and stranding
# the rest of the literal.  Bare digit runs are already refused below; this
# covers the separator-bearing literals, which are not ``.isdigit()``.
_LITERAL = re.compile(
    "|".join(f"(?:{p})" for p in (_tok._ISOWEEK, _tok._ISO,
                                  _tok._NUMDATE_ANY, _tok._CLOCK)))


def reindex(tokens) -> Tuple[Token, ...]:
    """Renumber ``Token.index`` so the stream stays contiguous from 0."""
    return tuple(replace(t, index=i) for i, t in enumerate(tokens))


def _never(_tok: Token) -> bool:
    return False


@dataclass(frozen=True)
class NumberGrammar:
    """The per-language data the shared fold varies on.

    ``is_number``  -- run membership: is this token a number-word?
    ``extract``    -- read the numeric value of a run's joined text
                      (``False``/``None`` == not a number).
    ``joiner``     -- optional predicate for an internal connector token
                      ("and"/"و"/JOIN_WORD) that continues a run when a
                      number-word follows it.
    ``joiner_in_text`` -- keep joiner tokens in the text handed to
                      ``extract`` (Romance/Semitic) or drop them (English).
    ``single_fallback`` -- for a one-token run the back-end rejects, a
                      surface->value lookup (returns ``None`` when absent).
    ``pre``        -- an optional token-stream pre-pass run before the scan.
    """
    is_number: Callable[[Token], bool]
    extract: Callable[[str], Any]
    joiner: Callable[[Token], bool] = _never
    joiner_in_text: bool = True
    single_fallback: Optional[Callable[[str], Any]] = None
    pre: Optional[Callable[[Tuple[Token, ...]], Tuple[Token, ...]]] = None


def make_fold(grammar: NumberGrammar
              ) -> Callable[[Tuple[Token, ...]], Tuple[Token, ...]]:
    """Build the spelled-number fold for ``grammar`` -- the one implementation."""
    spelled = grammar.is_number

    def is_number(tok: Token) -> bool:
        """Run membership, with the tokenizer's refusals honoured.

        A digit surface that reaches this pass *without* a number reading was
        refused one on purpose -- it is the year of a date-shaped run that
        bound no date ("2024/03", "15.06.20201"), and reading it alone is the
        silent wrong the tokenizer just declined to commit.  Several languages
        decide run membership by asking their number back-end what a surface is
        worth, and the back-ends happily read "2024" out of any digits, which
        would hand the refused numeral straight back.  This pass exists for
        *spelled* numbers; digits are the tokenizer's business, so its verdict
        stands.
        """
        if not tok.is_number and tok.text.isdigit():
            return False
        # a whole date/clock literal the tokenizer bound (the spaced dotted
        # civil date "15. 6. 2020", an ISO literal, a clock): the back-end can
        # read a number out of its first component, but the tokenizer chose to
        # keep it whole, and that verdict stands here too.
        if not tok.is_number and _LITERAL.fullmatch(tok.text):
            return False
        return spelled(tok)

    joiner = grammar.joiner
    extract = grammar.extract
    fallback = grammar.single_fallback
    keep_joiner = grammar.joiner_in_text
    pre = grammar.pre

    def fold(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        if pre is not None:
            tokens = pre(tokens)
        out = []
        i = 0
        n = len(tokens)
        while i < n:
            if not is_number(tokens[i]):
                out.append(tokens[i])
                i += 1
                continue
            j = i
            run = []
            while j < n:
                if is_number(tokens[j]):
                    run.append(tokens[j])
                    j += 1
                elif (joiner(tokens[j]) and run and j + 1 < n
                      and is_number(tokens[j + 1])):
                    run.append(tokens[j])   # internal connector: keeps the run
                    j += 1
                else:
                    break
            # a run with no spelled number-word needs no folding: its members
            # are already complete digit numbers, and merging two of them
            # ("2019 2020", "2 and 4") would fabricate a single wrong value out
            # of a list of distinct dates.  The joiner ("and"/"e") is not a
            # spelled number-word, so a pure-digit run bridged by one still
            # folds nothing -- each digit stays its own token for the matcher.
            spelled = [t for t in run if not t.is_number and not joiner(t)]
            if not spelled:
                out.extend(run)
                i = j
                continue
            if keep_joiner:
                text = " ".join(t.text for t in run)
            else:
                text = " ".join(t.text for t in run if not joiner(t))
            value = extract(text)
            if ((value is False or value is None) and fallback is not None
                    and len(run) == 1):
                fb = fallback(run[0].text)
                if fb is not None:
                    value = fb
            if value is False or value is None:
                out.extend(run)
                i = j
                continue
            num = int(value) if float(value).is_integer() else float(value)
            out.append(Token(text=str(num), raw=str(num), index=0,
                             is_number=True, value=num,
                             char_start=run[0].char_start,
                             char_end=run[-1].char_end))
            i = j
        return reindex(out)

    return fold
