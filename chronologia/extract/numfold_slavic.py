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

from functools import lru_cache
from importlib import import_module
from typing import Callable, FrozenSet, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import NumberGrammar, make_fold, reindex

# Oblique/declined number forms the number model does not emit from its
# nominative pronunciation but that the corpora attest.  Closed class,
# facts of the language -- kept tiny and explicit.
_EXTRA: dict = {
    # NB "půl" is deliberately NOT a cardinal number-word: extract_number_cs
    # reads it as 0.5, which would fold the toward-hour half word out of the
    # clock's FRACTION slot ("půl deváté").  The half-hour duration ("půl
    # hodiny") resolves through the marker_half path, not the cardinal fold.
    "cs": {"dva", "dvě", "dvou", "tři", "čtyři"},
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


def _make_fold(lang: str) -> Callable[[Tuple[Token, ...]], Tuple[Token, ...]]:
    """A bare cardinal fold: run membership from the model-derived word set,
    value read back through ``extract_number_<lang>``.  No connector, no
    fallback -- just the shared engine over this family's data."""
    return make_fold(NumberGrammar(
        is_number=lambda tok: tok.is_number or tok.text in _numwords(lang),
        extract=lambda text: _extract(lang, text)))


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

# -- toward-hour clock: the ordinal/genitive form that NAMES the coming hour --
# The Slavic spoken clock counts toward the coming hour and names it with a
# declined ordinal agreeing with an elided hour noun -- Russian genitive
# masculine ("девятого" of-the-ninth, agreeing with elided "часа"), Czech and
# Polish genitive/locative feminine ("deváté"/"dziewiątej", agreeing with
# "hodiny"/"godziny"), Slovenian genitive plural ("devetih").  Those surfaces
# are their own closed morphological class the cardinal back-end does not read,
# and -- unlike the nominative quarter ordinal -- they sit *adjacent* to the
# fraction word ("pol devetih"), whose own half-word is a number-word in some
# models; folding them BEFORE the cardinal pass would let the fraction and the
# hour merge into one run.  So this map is applied as a POST-pass, after the
# cardinal fold has run, turning the lone hour-ordinal surface into the digit
# its HOUR slot binds.  Citations (per language) live in the locale voc files.
_HOUR_RU = {  # genitive masculine, elided "часа"
    "первого": 1, "второго": 2, "третьего": 3, "четвёртого": 4,
    "четвертого": 4, "пятого": 5, "шестого": 6, "седьмого": 7,
    "восьмого": 8, "девятого": 9, "десятого": 10, "одиннадцатого": 11,
    "двенадцатого": 12}
_HOUR_CS = {  # genitive feminine, elided "hodiny"
    "první": 1, "druhé": 2, "třetí": 3, "čtvrté": 4, "páté": 5, "šesté": 6,
    "sedmé": 7, "osmé": 8, "deváté": 9, "desáté": 10, "jedenácté": 11,
    "dvanácté": 12}
_HOUR_SL = {  # genitive plural, elided "ure"
    "enih": 1, "dveh": 2, "treh": 3, "štirih": 4, "petih": 5, "šestih": 6,
    "sedmih": 7, "osmih": 8, "devetih": 9, "desetih": 10, "enajstih": 11,
    "dvanajstih": 12}
_HOUR_PL = {  # genitive/locative feminine ("do/po ...") + nominative ("za ...")
    "pierwszej": 1, "drugiej": 2, "trzeciej": 3, "czwartej": 4, "piątej": 5,
    "szóstej": 6, "siódmej": 7, "ósmej": 8, "dziewiątej": 9, "dziesiątej": 10,
    "jedenastej": 11, "dwunastej": 12,
    "pierwsza": 1, "druga": 2, "trzecia": 3, "czwarta": 4, "piąta": 5,
    "szósta": 6, "siódma": 7, "ósma": 8, "dziewiąta": 9, "dziesiąta": 10,
    "jedenasta": 11, "dwunasta": 12}


def _hour_rewrite(hourmap: dict) -> Callable:
    """A post-fold pass folding a lone toward-hour ordinal surface to its
    digit.  Runs after the cardinal fold so the (number-word) fraction and the
    hour never merge into a single run."""
    frozen = dict(hourmap)

    def rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        out, changed = [], False
        for t in tokens:
            if not t.is_number and t.text in frozen:
                v = frozen[t.text]
                out.append(Token(text=str(v), raw=str(v), index=t.index,
                                 is_number=True, value=v,
                                 char_start=t.char_start, char_end=t.char_end))
                changed = True
            else:
                out.append(t)
        return reindex(out) if changed else tokens

    return rewrite


def _split_ru_pol(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Russian contracts "пол" + genitive-ordinal hour into one word
    ("полдевятого" == half toward the ninth == 08:30).  Split it back into the
    half-word "половина" and the bare ordinal so the FRACTION+HOUR clock reads
    it; only fires when the tail is a known hour ordinal, so "полдень"/"полночь"
    are left whole."""
    out, changed = [], False
    for t in tokens:
        tail = t.text[3:] if t.text.startswith("пол") else ""
        if not t.is_number and tail in _HOUR_RU:
            cs, ce = t.char_start, t.char_end
            mid = (cs + 3) if cs is not None else None
            out.append(Token(text="половина", raw="половина", index=t.index,
                             is_number=False, char_start=cs, char_end=mid))
            out.append(Token(text=tail, raw=tail, index=t.index,
                             is_number=False, char_start=mid, char_end=ce))
            changed = True
        else:
            out.append(t)
    return reindex(out) if changed else tokens


def _compose(*passes: Callable) -> Callable:
    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        for p in passes:
            tokens = p(tokens)
        return tokens
    return run


fold_cs = _compose(with_ordinals(_make_fold("cs"), "cs"), _hour_rewrite(_HOUR_CS))
fold_sk = with_ordinals(_make_fold("sk"), "sk")
fold_pl = _compose(with_ordinals(_make_fold("pl"), "pl"), _hour_rewrite(_HOUR_PL))
fold_ru = _compose(_split_ru_pol, with_ordinals(_make_fold("ru"), "ru", _ORD_RU),
                   _hour_rewrite(_HOUR_RU))
fold_uk = with_ordinals(_make_fold("uk"), "uk")
fold_hr = with_ordinals(_make_fold("hr"), "hr")
fold_sl = _compose(with_ordinals(_make_fold("sl"), "sl", _ORD_SL),
                   _hour_rewrite(_HOUR_SL))
fold_bg = with_ordinals(_make_fold("bg"), "bg", _ORD_BG)
