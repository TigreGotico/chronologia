"""Temporal-lemma normalisation: pure ``Token -> Token``.

Closed-class morphology only.  Two data-driven passes, in order:

1. **Lemma map** -- irregular inflected forms mapped to their canonical
   surface form (``tygodni -> tydzien``).  Exact-match wins outright.
2. **Suffix strip** -- rule-based regular inflection removal
   (``ostiralean -> ostiral`` via ``["-ean", ""]``).  A leading ``-`` in
   the pattern marks it as a suffix; the first matching rule applies.

Numbers pass through untouched -- morphology never rewrites a numeral.
Only ``Token.text`` changes; ``Token.raw`` is preserved for remainder
reconstruction.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Tuple

from chronologia.extract.model import LangSpec, Token


class TemporalNormaliser:
    """Configured once from a :class:`LangSpec`."""

    def __init__(self, spec: LangSpec):
        self.lemmas = spec.lemmas
        self.suffix_strip = spec.suffix_strip

    def normalise_token(self, token: Token) -> Token:
        if token.is_number:
            return token
        if token.text in self.lemmas:
            return replace(token, text=self.lemmas[token.text])
        for pattern, repl in self.suffix_strip:
            suffix = pattern.lstrip("-")
            if suffix and token.text.endswith(suffix) and token.text != suffix:
                return replace(token, text=token.text[:-len(suffix)] + repl)
        return token

    def normalise(self, tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        return tuple(self.normalise_token(t) for t in tokens)
