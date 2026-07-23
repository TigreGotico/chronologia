"""Spelled-number folding pre-pass for the Slavic family.

The tokenizer only recognises *digit* runs as numbers; Slavic speech spells
them, and every number carries heavy case morphology ("dvadsaťpäť minút",
"через тридцать минут").  This pass folds a maximal run of spelled
number-words into a single digit :class:`~chronologia.extract.model.Token`
so a ``NUM`` slot binds the same whether the writer typed ``25`` or the
words.

Unlike the English fold (a hand-listed closed class), the Slavic fold
derives its number-word set *from the language's own number model*: the
cardinals ``ovos_number_parser`` can pronounce for ``0..99`` (nominative
forms) plus a small per-language table of the oblique/declined forms the
corpora actually use.  Run membership is gated by that closed set; the
numeric value is read back from ``extract_number_<lang>`` so declension the
extractor understands is honoured.  This keeps over-folding (a stray word
the extractor happens to read as a number) from firing.

Each ``fold_<lang>`` is wired as the language ``hook`` in
``locale/<lang>/lang.json`` and is a pure ``tuple[Token] -> tuple[Token]``.
"""
from __future__ import annotations

from dataclasses import replace
from functools import lru_cache
from importlib import import_module
from typing import Callable, FrozenSet, Tuple

from chronologia.extract.model import Token

# Oblique/declined number forms the number model does not emit from its
# nominative pronunciation but that the corpora attest.  Closed class,
# facts of the language -- kept tiny and explicit.
_EXTRA: dict = {
    "cs": {"dva", "dvě", "dvou", "tři", "čtyři", "půl"},
    "sk": {"dva", "dve", "dvoch", "tri", "štyri", "pol"},
    "pl": {"dwa", "dwie", "dwóch", "trzy", "cztery", "pół"},
    "ru": {"два", "две", "двух", "три", "пол"},
    "uk": {"два", "дві", "двох", "три", "пів"},
    "hr": {"dva", "dvije", "tri", "pola", "pol"},
    "sl": {"dva", "dve", "tri", "pol"},
    "bg": {"два", "две", "три", "половин"},
}


@lru_cache(maxsize=None)
def _model(lang: str):
    return import_module(f"ovos_number_parser.numbers_{lang}")


@lru_cache(maxsize=None)
def _numwords(lang: str) -> FrozenSet[str]:
    mod = _model(lang)
    pron = getattr(mod, f"pronounce_number_{lang}")
    words = set()
    for n in range(0, 100):
        try:
            for w in str(pron(n)).lower().replace("-", " ").split():
                words.add(w)
        except Exception:
            pass
    words |= _EXTRA.get(lang, set())
    return frozenset(words)


def _extract(lang: str, text: str):
    fn = getattr(_model(lang), f"extract_number_{lang}")
    try:
        return fn(text)
    except Exception:
        return False


def _reindex(tokens) -> Tuple[Token, ...]:
    return tuple(replace(t, index=i) for i, t in enumerate(tokens))


def _make_fold(lang: str) -> Callable[[Tuple[Token, ...]], Tuple[Token, ...]]:
    def _is_numword(tok: Token) -> bool:
        return tok.is_number or tok.text in _numwords(lang)

    def fold(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        out = []
        i = 0
        n = len(tokens)
        while i < n:
            if not _is_numword(tokens[i]):
                out.append(tokens[i])
                i += 1
                continue
            j = i
            run = []
            while j < n and _is_numword(tokens[j]):
                run.append(tokens[j])
                j += 1
            spelled = [t for t in run if not t.is_number]
            if not spelled:
                out.extend(run)
                i = j
                continue
            text = " ".join(t.text for t in run)
            value = _extract(lang, text)
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
        return _reindex(out)

    return fold


from chronologia.extract.numfold_ordinals import with_ordinals

# Spelled ordinals the *quarter* (and scoped-ordinal) construction reads in its
# ``ORD`` slot.  cs/sk/pl/uk/hr expose ``pronounce_ordinal_<lang>`` (masculine
# nominative, the form the masculine quarter word "kvartál"/"kwartał"/"квартал"
# agrees with), so ``with_ordinals`` derives them from the model.  ru/sl carry
# no ordinal pronouncer, and bg agrees with the *neuter* "тримесечие", so those
# three supply an explicit closed table (a fact of the language).
_ORD_RU = {"первый": 1, "второй": 2, "третий": 3, "четвёртый": 4,
           "четвертый": 4, "пятый": 5, "шестой": 6, "седьмой": 7,
           "восьмой": 8, "девятый": 9, "десятый": 10}
_ORD_SL = {"prvi": 1, "drugi": 2, "tretji": 3, "četrti": 4, "peti": 5,
           "šesti": 6, "sedmi": 7, "osmi": 8, "deveti": 9, "deseti": 10}
_ORD_BG = {"първо": 1, "второ": 2, "трето": 3, "четвърто": 4, "пето": 5,
           "шесто": 6, "седмо": 7, "осмо": 8, "девето": 9, "десето": 10}

fold_cs = with_ordinals(_make_fold("cs"), "cs")
fold_sk = with_ordinals(_make_fold("sk"), "sk")
fold_pl = with_ordinals(_make_fold("pl"), "pl")
fold_ru = with_ordinals(_make_fold("ru"), "ru", _ORD_RU)
fold_uk = with_ordinals(_make_fold("uk"), "uk")
fold_hr = with_ordinals(_make_fold("hr"), "hr")
fold_sl = with_ordinals(_make_fold("sl"), "sl", _ORD_SL)
fold_bg = with_ordinals(_make_fold("bg"), "bg", _ORD_BG)
