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
    # Slovak names the clock half toward the coming hour the same direction
    # as Czech ("pol deviatej" == half toward nine, parallel to "půl deváté"),
    # attested by en.wiktionary.org/wiki/half_past's translation table (sk:
    # "pol druhej" under the headword "half past one" == 1:30).  It is NOT
    # wired here despite that: the hour is a genitive/locative ORDINAL
    # ("deviatej", "druhej"), not Croatian's bare cardinal, so the hr wiring
    # (bare_half_to + a bare "FRACTION HOUR" order) does not transfer as-is --
    # it would need an ordinal-aware toward-hour construction of its own, the
    # same shape Czech already has via _HOUR_SK-style ordinal folding.  Also,
    # unlike Croatian's "pola", "pol" here stays a genuine cardinal number
    # word ("pol hodiny" == half an hour) and cannot simply be dropped from
    # this fold set the way hr's "pola" was -- see the hr entry below for the
    # duration breakage that caused.  Left unimplemented rather than shipped
    # half-built.
    "sk": {"dva", "dve", "dvoch", "tri", "štyri", "pol"},
    "pl": {"dwa", "dwie", "dwóch", "trzy", "cztery", "pół"},
    # "one" agrees in gender/case with its noun; the model pronounces only the
    # masculine nominative "один"/"один", so the feminine forms (required before
    # feminine unit nouns like минута/секунда/хвилина) never enter the run set
    # and every compound ending in 1 folded to N-1.  Add the feminine
    # nominative/accusative/oblique, mirroring the "два"/"две"/"двух" trio.
    "ru": {"два", "две", "двух", "три", "пол", "одна", "одну", "одной"},
    # NB "пів" is deliberately NOT folded here, mirroring cs's "půl": folding
    # it to 0.5 would erase the toward-hour clock's FRACTION surface
    # ("пів на другу") before the grammar ever sees the word.  Standalone
    # "пів <unit>" durations already resolve through the QUANT slot
    # (lang.json quantifiers), not this cardinal fold.
    "uk": {"два", "дві", "двох", "три", "одна", "одну", "одної"},
    # NB "pola" is deliberately NOT folded here, mirroring cs's "půl":
    # folding it to 0.5 would erase the toward-hour clock's FRACTION surface
    # ("pola devet") before the grammar ever sees the word.  "pol" stays IN
    # the fold set -- it is the plain cardinal-duration half ("pol sata",
    # "sat i pol", "dva i pol sata"), not the clock word, and dropping it
    # alongside "pola" broke all ten of those readings for no reason.  The
    # accepted cost of excluding "pola" alone is that the timespan-composing
    # "za pola sata" (in half an hour) no longer resolves through this fold
    # either; the standalone "pola sata" duration still resolves through the
    # QUANT slot (lang.json quantifiers), unaffected by this table.
    "hr": {"dva", "dvije", "tri", "pol"},
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
    # Pronounce through 999, not just 100: the hundred-words 200..900
    # ("двести", "триста", "dwieście", ...) only ever appear when a number
    # >= 200 is spoken, so a run set built from 0..100 alone silently dropped
    # every spelled hundred and returned None for "двести дней" (two hundred
    # days) across all eight Slavic locales.  The 100..999 sweep adds only those
    # hundred-words (the tens/units are already covered by 0..99), so the set
    # stays a closed class of genuine number-words -- no over-folding risk.
    for n in range(0, 1000):
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


def _make_fold_bg() -> Callable[[Tuple[Token, ...]], Tuple[Token, ...]]:
    """Bulgarian names a compound cardinal with an internal "и" ("двадесет и
    три" == 23), so ``pronounce_number_bg``'s sweep puts "и" itself in the
    model-derived word set -- unlike its Slavic siblings, none of which
    spell a compound this way.  Read as bare ``is_number`` membership (the
    ``_make_fold`` shape above) that swallows ANY "и" adjacent to a number,
    including the clock's additive "осем и половина" ("eight and a half"),
    folding "осем и" to the bare hour and stranding "половина" for the
    FRACTION slot to never see -- the same fold trap that already forced cs's
    "půl", uk's "пів" and hr's "pola" out of their bare-cardinal sets.  "и"
    is pulled out of the membership set here and reinstated only as a
    ``joiner``, which the shared engine (numfold_engine.fold) admits into a
    run solely when the *following* token is itself a number word -- exactly
    the compound case -- so "двадесет и три" still folds to 23 while "осем и
    половина" leaves "и" standing for the clock's CLOCKDIR slot."""
    words = _numwords("bg") - {"и"}
    return make_fold(NumberGrammar(
        is_number=lambda tok: tok.is_number or tok.text in words,
        extract=lambda text: _extract("bg", text),
        joiner=lambda tok: tok.text == "и"))


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
# sk mirrors pl's feminine-locative toward-hour class: "o druhej (hodine)" (at
# two o'clock) names the coming hour with a feminine locative ordinal agreeing
# with the elided "hodine".  Citation: Jazykovedný ústav Ľ. Štúra SAV,
# Morfológia slovenského jazyka, skloňovanie radových čísloviek, ženský rod
# lokál jednotného čísla "jednej ... dvanástej".
# https://slovnik.juls.savba.sk/
_HOUR_SK = {  # locative feminine, elided "hodine"
    "jednej": 1, "druhej": 2, "tretej": 3, "štvrtej": 4, "piatej": 5,
    "šiestej": 6, "siedmej": 7, "ôsmej": 8, "deviatej": 9, "desiatej": 10,
    "jedenástej": 11, "dvanástej": 12}

# -- Ukrainian "at <hour>": locative feminine, elided "годині" -----------------
# "о другій (годині)" == at two o'clock (02:00, the literal named hour, not a
# toward-hour reading -- "о"/"about" + locative just names the hour).
# Citation: worked examples "о сьомій годині" (at seven o'clock) and "о
# шостій" (at six) -- slovopedia.org.ua, "Смолич. То як передати..."
# (http://slovopedia.org.ua/34/53415/33359.html) and dimostovyk.blogspot.com,
# "Квіти і час" (https://dimostovyk.blogspot.com/p/6_9.html).
_HOUR_UK = {
    "першій": 1, "другій": 2, "третій": 3, "четвертій": 4, "п'ятій": 5,
    "шостій": 6, "сьомій": 7, "восьмій": 8, "дев'ятій": 9, "десятій": 10,
    "одинадцятій": 11, "дванадцятій": 12}
for _apo in ("'", "’"):
    _HOUR_UK.update({f"п{_apo}ятій": 5, f"дев{_apo}ятій": 9})

# -- Ukrainian toward-hour "пів на <hour>"/"чверть на <hour>": accusative -----
# feminine, elided "годину".  "пів на другу" == half onto the second == 01:30
# (the NAMED hour is the coming one); "чверть на одинадцяту" == a quarter
# onto the eleventh == 10:15.  Citations: promovu.in.ua, "Час англійською"
# (https://promovu.in.ua/time/) and miyklas.com.ua, 6th-grade lesson
# (https://www.miyklas.com.ua/p/ukrainska-mova/6-klas/chislivnik-14257/vikoristannia-chislivnikiv-na-poznachennia-dat-i-chasu-37756/).
_HOUR_UK_ACC = {
    "першу": 1, "другу": 2, "третю": 3, "четверту": 4, "п'яту": 5,
    "шосту": 6, "сьому": 7, "восьму": 8, "дев'яту": 9, "десяту": 10,
    "одинадцяту": 11, "дванадцяту": 12}
for _apo in ("'", "’"):
    _HOUR_UK_ACC.update({f"п{_apo}яту": 5, f"дев{_apo}яту": 9})


# -- feminine nominative ordinals that agree with a feminine temporal noun ------
# Several date-relevant period nouns are FEMININE across the family, and the
# ordinal that selects one of them carries the feminine nominative ending, which
# ``pronounce_ordinal_<lang>`` never emits (it gives only the MASCULINE
# nominative pierwszy/drugi..., and ru/bg carry no ordinal pronouncer at all).
# So the feminine surface is supplied here as a closed table -- the same shape
# and reason as the day/hour ordinal tables above.  It feeds every feminine
# period noun the extractor reads: the "half" (половина / połowa / polovina /
# половина), the ru/bg feminine "week" (неделя / седмица, "третья неделя
# апреля" = the third week of April), the feminine "quarter"/"decade"/"tenth"
# (четверть / декада ...), etc.  The two-entry version shipped in #264 folded
# only 1st/2nd, so "третья неделя апреля" (3rd week) stranded and the whole
# month was returned -- a silent wrong answer.  The table now spans the full
# date-relevant range 1..12 (weeks 1-5, decades/thirds 1-3, and higher to be
# safe), so every feminine period ordinal folds to its digit.  Owning these
# surfaces locally is also what keeps ovos-number-parser from misreading the
# ordinal as a fraction (вторая -> 0.5, третья -> 0.333): the fold turns the
# word into an integer token BEFORE the cardinal back-end ever sees it.
# Citations, per language (feminine ordinal числительные / liczebniki):
#   ru -- Розенталь, *Справочник по правописанию*, склонение порядковых
#         числительных: женский род, ед. ч., им. п. "первая ... двенадцатая".
#   pl -- PWN, *Słownik języka polskiego*: liczebnik porządkowy, rodzaj żeński
#         "pierwsza ... dwunasta".  https://sjp.pwn.pl/
#   uk -- *Український правопис* (2019): порядкові числівники, жіночий рід
#         "перша ... дванадцята".
#   cs -- Internetová jazyková příručka (ÚJČ AV ČR): řadové číslovky, rod ženský
#         "první ... dvanáctá".  https://prirucka.ujc.cas.cz/
#   sk -- Jazykovedný ústav Ľ. Štúra SAV, Morfológia slovenského jazyka: radové
#         číslovky, ženský rod "prvá ... dvanásta".  https://slovnik.juls.savba.sk/
#   sl -- Fran (ZRC SAZU), SSKJ2: vrstilni števniki, ženski spol
#         "prva ... dvanajsta".  https://fran.si/
#   hr -- Institut za hrvatski jezik / Hrvatski jezični portal: redni brojevi,
#         ženski rod "prva ... dvanaesta".  https://hjp.znanje.hr/
#   bg -- Институт за български език (БАН): редни числителни, женски род
#         "първа ... дванадесета" и членувано "първата ... дванадесетата".
#         https://ibl.bas.bg/
_FEM_ORD_RU = {
    "первая": 1, "вторая": 2, "третья": 3, "четвёртая": 4, "четвертая": 4,
    "пятая": 5, "шестая": 6, "седьмая": 7, "восьмая": 8, "девятая": 9,
    "десятая": 10, "одиннадцатая": 11, "двенадцатая": 12}
_FEM_ORD_PL = {
    "pierwsza": 1, "druga": 2, "trzecia": 3, "czwarta": 4, "piąta": 5,
    "szósta": 6, "siódma": 7, "ósma": 8, "dziewiąta": 9, "dziesiąta": 10,
    "jedenasta": 11, "dwunasta": 12}
_FEM_ORD_UK = {
    "перша": 1, "друга": 2, "третя": 3, "четверта": 4, "шоста": 6,
    "сьома": 7, "восьма": 8, "десята": 10, "одинадцята": 11, "дванадцята": 12}
# Ukrainian spells 5 and 9 with an apostrophe (straight or typographic).
for _apo in ("'", "’"):
    _FEM_ORD_UK.update({f"п{_apo}ята": 5, f"дев{_apo}ята": 9})
_FEM_ORD_CS = {
    "první": 1, "druhá": 2, "třetí": 3, "čtvrtá": 4, "pátá": 5, "šestá": 6,
    "sedmá": 7, "osmá": 8, "devátá": 9, "desátá": 10, "jedenáctá": 11,
    "dvanáctá": 12}
_FEM_ORD_SK = {
    "prvá": 1, "druhá": 2, "tretia": 3, "štvrtá": 4, "piata": 5, "šiesta": 6,
    "siedma": 7, "ôsma": 8, "deviata": 9, "desiata": 10, "jedenásta": 11,
    "dvanásta": 12}
_FEM_ORD_SL = {
    "prva": 1, "druga": 2, "tretja": 3, "četrta": 4, "peta": 5, "šesta": 6,
    "sedma": 7, "osma": 8, "deveta": 9, "deseta": 10, "enajsta": 11,
    "dvanajsta": 12}
_FEM_ORD_HR = {
    "prva": 1, "druga": 2, "treća": 3, "četvrta": 4, "peta": 5, "šesta": 6,
    "sedma": 7, "osma": 8, "deveta": 9, "deseta": 10, "jedanaesta": 11,
    "dvanaesta": 12}
_FEM_ORD_BG = {
    "първа": 1, "втора": 2, "трета": 3, "четвърта": 4, "пета": 5, "шеста": 6,
    "седма": 7, "осма": 8, "девета": 9, "десета": 10, "единадесета": 11,
    "единайсета": 11, "дванадесета": 12, "дванайсета": 12}
# Bulgarian selects a period noun with the *definite* article (-ата): "третата
# седмица" = the third week.  Fold those definite feminine surfaces too.
_FEM_ORD_BG.update({w + "та": v for w, v in dict(_FEM_ORD_BG).items()})


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


# Genitive-singular duration-unit surfaces "пол" ("half") contracts onto in
# the ordinary compound-noun spelling ("полчаса" == half an hour, "полминуты"
# == half a minute, "полдня" == half a day, "полнедели" == half a week) --
# citation forms taken from unit_hour.voc/unit_minute.voc/unit_day.voc/
# unit_week.voc.  Split so the leading "пол" reads as the standalone 0.5
# quantifier and the tail reads as the ordinary UNIT surface, exactly as the
# already-supported space-separated spelling ("пол часа") does; without the
# split the fused spelling is one unknown word and the whole phrase strands.
_UNIT_GEN_RU = {"часа": "hour", "минуты": "minute", "дня": "day",
                "недели": "week"}


def _split_ru_pol_unit(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Split the fused "пол<unit-genitive>" compound into "пол" + the
    genitive unit word, mirroring :func:`_split_ru_pol` for the toward-hour
    contraction.  Runs before that pass; the unit-genitive set and the
    toward-hour ordinal set do not overlap, so order between the two does
    not matter."""
    out, changed = [], False
    for t in tokens:
        tail = t.text[3:] if t.text.startswith("пол") else ""
        if not t.is_number and tail in _UNIT_GEN_RU:
            cs, ce = t.char_start, t.char_end
            mid = (cs + 3) if cs is not None else None
            out.append(Token(text="пол", raw="пол", index=t.index,
                             is_number=False, char_start=cs, char_end=mid))
            out.append(Token(text=tail, raw=tail, index=t.index,
                             is_number=False, char_start=mid, char_end=ce))
            changed = True
        else:
            out.append(t)
    return reindex(out) if changed else tokens


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


# -- calendar day: the declined ordinal that names the day of the month -------
# Slavic says a date with an ordinal agreeing with an elided day noun, in the
# case the sentence puts it in: the citation form is the genitive masculine
# ("trzeciego maja", "třetího prosince", "третьего декабря"), and the month name
# stands in the genitive beside it.  Bulgarian, having lost its cases, uses the
# bare masculine ("трети декември").  These surfaces are a closed morphological
# class the cardinal back-end does not read, so each language supplies its own
# table -- the same shape as the toward-hour tables above, and the same reason.
#
# Days 21..31 are compound.  Which element carries the ordinal is a fact of the
# individual language, not of the family: Polish, Czech and Slovak decline both
# elements ("dwudziestego trzeciego"), Russian, Ukrainian, Croatian and
# Bulgarian leave the tens a plain cardinal and inflect only the unit ("двадцать
# третьего", "dvadeset trećeg", "двадесет и трети"), and Slovene writes the
# whole numeral as one word with the unit first ("triindvajsetega").  So a
# language declares its ordinal surfaces in ``ords`` and, where the tens element
# is a bare cardinal, in ``tens_prefix``; the rewrite below adds the two.
# Folding only the unit and dropping the tens would answer the third of the
# month when the speaker said the twenty-third, which is the whole failure this
# table exists to prevent.
#
# Citations, per language:
#   pl -- PWN, *Poradnia językowa*, "Zapis daty": the day is read as a genitive
#         ordinal and the month name is always genitive.
#         https://sjp.pwn.pl/poradnia/haslo/Zapis-daty;16535.html
#   cs -- Internetová jazyková příručka, ÚJČ AV ČR: skloňování řadových
#         číslovek, vzor "mladý"/"jarní".  https://prirucka.ujc.cas.cz/?id=310
#   sk -- Jazykovedný ústav Ľ. Štúra SAV, Morfológia slovenského jazyka:
#         skloňovanie radových čísloviek.  https://slovnik.juls.savba.sk/
#   hr -- Institut za hrvatski jezik / Hrvatski jezični portal: sklonidba
#         rednih brojeva, with the attested -og/-oga variants.
#         https://hjp.znanje.hr/
#   sl -- Fran (ZRC SAZU), SSKJ2: vrstilni števniki, one-word 21..31.
#         https://fran.si/
#   bg -- Институт за български език, БАН, *Официален правописен речник*:
#         редни числителни имена.  https://ibl.bas.bg/rechnik/
#   ru -- Грамота.ру, "Как правильно употреблять числительные": the day stands
#         in the genitive and only the last element of a compound inflects.
#         https://gramota.ru/biblioteka/spravochniki/pismovnik/kak-pravilno-upotreblyat-chislitelnye
#   uk -- *Український правопис* (2019), відмінювання порядкових числівників.
#         https://nus.org.ua/wp-content/uploads/2019/05/Ukr.-pravopys-2019-1.pdf
_DAY_PL = {
    "pierwszego": 1, "drugiego": 2, "trzeciego": 3, "czwartego": 4,
    "piątego": 5, "szóstego": 6, "siódmego": 7, "ósmego": 8,
    "dziewiątego": 9, "dziesiątego": 10, "jedenastego": 11, "dwunastego": 12,
    "trzynastego": 13, "czternastego": 14, "piętnastego": 15,
    "szesnastego": 16, "siedemnastego": 17, "osiemnastego": 18,
    "dziewiętnastego": 19, "dwudziestego": 20, "trzydziestego": 30}
_DAY_CS = {
    "prvního": 1, "prvého": 1, "druhého": 2, "třetího": 3, "čtvrtého": 4,
    "pátého": 5, "šestého": 6, "sedmého": 7, "osmého": 8, "devátého": 9,
    "desátého": 10, "jedenáctého": 11, "dvanáctého": 12, "třináctého": 13,
    "čtrnáctého": 14, "patnáctého": 15, "šestnáctého": 16, "sedmnáctého": 17,
    "osmnáctého": 18, "devatenáctého": 19, "dvacátého": 20, "třicátého": 30}
_DAY_SK = {
    "prvého": 1, "druhého": 2, "tretieho": 3, "štvrtého": 4,
    "piateho": 5, "šiesteho": 6, "siedmeho": 7, "ôsmeho": 8, "deviateho": 9,
    "desiateho": 10, "jedenásteho": 11, "dvanásteho": 12, "trinásteho": 13,
    "štrnásteho": 14, "pätnásteho": 15, "šestnásteho": 16,
    "sedemnásteho": 17, "osemnásteho": 18, "devätnásteho": 19,
    "dvadsiateho": 20, "tridsiateho": 30}
_DAY_HR = {}
for _stem, _v in (("prv", 1), ("drug", 2), ("treć", 3), ("četvrt", 4),
                  ("pet", 5), ("šest", 6), ("sedm", 7), ("osm", 8),
                  ("devet", 9), ("deset", 10), ("jedanaest", 11),
                  ("dvanaest", 12), ("trinaest", 13), ("četrnaest", 14),
                  ("petnaest", 15), ("šesnaest", 16), ("sedamnaest", 17),
                  ("osamnaest", 18), ("devetnaest", 19), ("dvadeset", 20),
                  ("trideset", 30)):
    # Croatian admits the short and the long genitive ending alike.
    _DAY_HR[_stem + ("eg" if _stem == "treć" else "og")] = _v
    _DAY_HR[_stem + ("ega" if _stem == "treć" else "oga")] = _v
_DAY_SL = {
    "prvega": 1, "drugega": 2, "tretjega": 3, "četrtega": 4, "petega": 5,
    "šestega": 6, "sedmega": 7, "osmega": 8, "devetega": 9, "desetega": 10,
    "enajstega": 11, "dvanajstega": 12, "trinajstega": 13,
    "štirinajstega": 14, "petnajstega": 15, "šestnajstega": 16,
    "sedemnajstega": 17, "osemnajstega": 18, "devetnajstega": 19,
    "dvajsetega": 20, "enaindvajsetega": 21, "dvaindvajsetega": 22,
    "triindvajsetega": 23, "štiriindvajsetega": 24, "petindvajsetega": 25,
    "šestindvajsetega": 26, "sedemindvajsetega": 27, "osemindvajsetega": 28,
    "devetindvajsetega": 29, "tridesetega": 30, "enaintridesetega": 31}
_DAY_BG = {
    "първи": 1, "втори": 2, "трети": 3, "четвърти": 4, "пети": 5,
    "шести": 6, "седми": 7, "осми": 8, "девети": 9, "десети": 10,
    "единадесети": 11, "единайсети": 11, "дванадесети": 12, "дванайсети": 12,
    "тринадесети": 13, "тринайсети": 13, "четиринадесети": 14,
    "четиринайсети": 14, "петнадесети": 15, "петнайсети": 15,
    "шестнадесети": 16, "шестнайсети": 16, "седемнадесети": 17,
    "седемнайсети": 17, "осемнадесети": 18, "осемнайсети": 18,
    "деветнадесети": 19, "деветнайсети": 19, "двадесети": 20,
    "двайсети": 20, "тридесети": 30, "трийсети": 30}
# Bulgarian carries the DEFINITE article on the masculine ordinal when it
# selects a masculine noun -- "първият понеделник" (the first Monday),
# "третият вторник".  The full article is -ият and the short/colloquial
# variant -ия; both are current, and both attach to the bare -и ordinal
# (първи -> първият / първия).  Without them the definite ordinal stranded
# and the weekday+month were silently dropped.  Fold every definite surface
# to the same digit as its bare -и form.  (Официален правопис на българския
# език, БАН 2012: членуване на редните числителни имена, мъжки род ед. ч. --
# пълен член -ият, кратък член -ия.)
_BG_DEF_BASE = {w: v for w, v in _DAY_BG.items() if w.endswith("и")}
_DAY_BG.update({w + "ят": v for w, v in _BG_DEF_BASE.items()})
_DAY_BG.update({w + "я": v for w, v in _BG_DEF_BASE.items()})
_DAY_RU = {
    "первого": 1, "второго": 2, "третьего": 3, "четвёртого": 4,
    "четвертого": 4, "пятого": 5, "шестого": 6, "седьмого": 7,
    "восьмого": 8, "девятого": 9, "десятого": 10, "одиннадцатого": 11,
    "двенадцатого": 12, "тринадцатого": 13, "четырнадцатого": 14,
    "пятнадцатого": 15, "шестнадцатого": 16, "семнадцатого": 17,
    "восемнадцатого": 18, "девятнадцатого": 19, "двадцатого": 20,
    "тридцатого": 30}
_DAY_UK = {
    "першого": 1, "другого": 2, "третього": 3, "четвертого": 4,
    "шостого": 6, "сьомого": 7, "восьмого": 8, "десятого": 10,
    "одинадцятого": 11, "дванадцятого": 12, "тринадцятого": 13,
    "чотирнадцятого": 14, "шістнадцятого": 16, "сімнадцятого": 17,
    "вісімнадцятого": 18, "двадцятого": 20, "тридцятого": 30}
# Ukrainian spells 5, 9, 15 and 19 with an apostrophe, which is typed as either
# the straight or the typographic character; both surfaces reach the fold.
for _apo in ("'", "’"):
    _DAY_UK.update({f"п{_apo}ятого": 5, f"дев{_apo}ятого": 9,
                    f"п{_apo}ятнадцятого": 15, f"дев{_apo}ятнадцятого": 19})


# -- calendar day, NEUTER NOMINATIVE ------------------------------------------
# East Slavic also names the day of the month in the bare NOMINATIVE, where the
# ordinal is NEUTER, agreeing with the elided neuter noun число ("сегодня
# пятнадцатое апреля" = today is the fifteenth of April; "п'ятнадцяте квітня").
# ``pronounce_ordinal_<lang>`` carries no such form (ru/uk expose no ordinal
# pronouncer at all) and the genitive #273 tables above hold only the -ого/-ого
# forms, so the neuter nominative stranded and the whole month was returned --
# a silent wrong answer.  These closed tables own the neuter nominative for the
# date-relevant range 1..31 (tens 20/30 fold on their own; the compound 21..29,
# 31 compose through the bare-cardinal tens прefix _TENS_RU/_TENS_UK, exactly as
# the genitive day fold does).
#   ru -- Розенталь, Справочник по правописанию: порядковые числительные,
#         средний род, ед. ч., им. п. "первое ... тридцать первое".
#   uk -- Український правопис (2019): порядкові числівники, середній рід
#         "перше ... тридцять перше".
_DAY_RU_NEUTER = {
    "первое": 1, "второе": 2, "третье": 3, "четвёртое": 4, "четвертое": 4,
    "пятое": 5, "шестое": 6, "седьмое": 7, "восьмое": 8, "девятое": 9,
    "десятое": 10, "одиннадцатое": 11, "двенадцатое": 12, "тринадцатое": 13,
    "четырнадцатое": 14, "пятнадцатое": 15, "шестнадцатое": 16,
    "семнадцатое": 17, "восемнадцатое": 18, "девятнадцатое": 19,
    "двадцатое": 20, "тридцатое": 30}
_DAY_UK_NEUTER = {
    "перше": 1, "друге": 2, "третє": 3, "четверте": 4, "шосте": 6,
    "сьоме": 7, "восьме": 8, "десяте": 10, "одинадцяте": 11, "дванадцяте": 12,
    "тринадцяте": 13, "чотирнадцяте": 14, "шістнадцяте": 16, "сімнадцяте": 17,
    "вісімнадцяте": 18, "двадцяте": 20, "тридцяте": 30}
for _apo in ("'", "’"):
    _DAY_UK_NEUTER.update({f"п{_apo}яте": 5, f"дев{_apo}яте": 9,
                           f"п{_apo}ятнадцяте": 15, f"дев{_apo}ятнадцяте": 19})


def _day_rewrite(ords: dict, tens_prefix: dict = None,
                 joiner: tuple = ()) -> Callable:
    """A pre-fold pass turning the declined day-of-month ordinal into the digit
    its ``DAY`` slot binds, adding a compound ``tens + unit`` pair into the one
    number it names.  Runs before the cardinal fold so a cardinal tens element
    is claimed by the compound rather than folded on its own."""
    ords = dict(ords)
    tens = dict(tens_prefix or {})
    tens.update({w: v for w, v in ords.items() if v in (20, 30)})

    def _num(t: Token, value: int, end: Token = None) -> Token:
        return Token(text=str(value), raw=str(value), index=t.index,
                     is_number=True, value=value, char_start=t.char_start,
                     char_end=(end or t).char_end)

    def rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        out, i, n, changed = [], 0, len(tokens), False
        while i < n:
            t = tokens[i]
            if t.is_number:
                out.append(t)
                i += 1
                continue
            if t.text in tens:
                j = i + 1
                if j < n and tokens[j].text in joiner:
                    j += 1
                if j < n and ords.get(tokens[j].text, 0) in range(1, 10):
                    out.append(_num(t, tens[t.text] + ords[tokens[j].text],
                                    tokens[j]))
                    i, changed = j + 1, True
                    continue
            if t.text in ords:
                out.append(_num(t, ords[t.text]))
                i, changed = i + 1, True
                continue
            out.append(t)
            i += 1
        return reindex(out) if changed else tokens

    return rewrite


# The tens element that stays a bare cardinal, per language.  It is folded only
# as part of a compound day; on its own it is an ordinary cardinal and belongs
# to the cardinal fold ("двадцать пять минут" must still read twenty-five).
_TENS_RU = {"двадцать": 20, "тридцать": 30}
_TENS_UK = {"двадцять": 20, "тридцять": 30}
_TENS_HR = {"dvadeset": 20, "trideset": 30}
_TENS_BG = {"двадесет": 20, "двайсет": 20, "тридесет": 30, "трийсет": 30}


def _compose(*passes: Callable) -> Callable:
    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        for p in passes:
            tokens = p(tokens)
        return tokens
    return run


# The day-ordinal pass leads, so a compound day claims its cardinal tens before
# the cardinal fold can take that tens for a bare number; the toward-hour pass
# still trails, because its surfaces must not merge with the fraction word.
fold_cs = _compose(_day_rewrite(_DAY_CS),
                   with_ordinals(_make_fold("cs"), "cs", _FEM_ORD_CS),
                   _hour_rewrite(_HOUR_CS))
fold_sk = _compose(_day_rewrite(_DAY_SK),
                   with_ordinals(_make_fold("sk"), "sk", _FEM_ORD_SK),
                   _hour_rewrite(_HOUR_SK))
fold_pl = _compose(_day_rewrite(_DAY_PL),
                   with_ordinals(_make_fold("pl"), "pl", _FEM_ORD_PL),
                   _hour_rewrite(_HOUR_PL))
fold_ru = _compose(_split_ru_pol_unit,
                   _split_ru_pol,
                   _day_rewrite({**_DAY_RU, **_DAY_RU_NEUTER}, _TENS_RU),
                   with_ordinals(_make_fold("ru"), "ru",
                                 {**_ORD_RU, **_FEM_ORD_RU}),
                   _hour_rewrite(_HOUR_RU))
fold_uk = _compose(_day_rewrite({**_DAY_UK, **_DAY_UK_NEUTER}, _TENS_UK),
                   with_ordinals(_make_fold("uk"), "uk", _FEM_ORD_UK),
                   _hour_rewrite({**_HOUR_UK, **_HOUR_UK_ACC}))
fold_hr = _compose(_day_rewrite(_DAY_HR, _TENS_HR, ("i",)),
                   with_ordinals(_make_fold("hr"), "hr", _FEM_ORD_HR))
fold_sl = _compose(_day_rewrite(_DAY_SL),
                   with_ordinals(_make_fold("sl"), "sl",
                                 {**_ORD_SL, **_FEM_ORD_SL}),
                   _hour_rewrite(_HOUR_SL))
fold_bg = _compose(_day_rewrite(_DAY_BG, _TENS_BG, ("и",)),
                   with_ordinals(_make_fold_bg(), "bg",
                                 {**_ORD_BG, **_FEM_ORD_BG}))


# -- Serbian: dual-script cardinal/ordinal fold -------------------------------
# ovos_number_parser ships no numbers_sr module, so the model-backed cardinal
# fold above (``_model``/``_numwords``/``_extract``) does not apply to sr.
# Below 100, Serbian cardinals form exactly like their Croatian cognates
# ("jedan, dva, tri ... dvadeset, trideset ..."), Wiktionary Appendix:
# Serbo-Croatian/Numbers (https://en.wiktionary.org/wiki/Appendix:Serbo-Croatian/Numbers),
# so this closed Latin-script table stands in for the model.  Every entry is
# doubled onto Cyrillic by the deterministic, digraph-aware transliteration
# (Gajica -> Vukovica) that every sr .voc surface in this locale also goes
# through -- the same "one closed list, both scripts" mechanism, rather than
# new engine machinery for script handling.  V1 covers 0-99 plus the bare
# hundred: the day/duration range the sr NL corpus exercises.
_SR_DIGRAPHS = (("lj", "љ"), ("nj", "њ"), ("dž", "џ"))
_SR_SINGLE = {
    "a": "а", "b": "б", "c": "ц", "č": "ч", "ć": "ћ", "d": "д", "đ": "ђ",
    "e": "е", "f": "ф", "g": "г", "h": "х", "i": "и", "j": "ј", "k": "к",
    "l": "л", "m": "м", "n": "н", "o": "о", "p": "п", "r": "р", "s": "с",
    "š": "ш", "t": "т", "u": "у", "v": "в", "z": "з", "ž": "ж"}


def sr_lat2cyr(word: str) -> str:
    """Deterministic Latin -> Cyrillic transliteration, digraphs first so
    lj/nj/dž fold to љ/њ/џ rather than their letters transliterated apart."""
    for lat, cyr in _SR_DIGRAPHS:
        word = word.replace(lat, cyr)
    return "".join(_SR_SINGLE.get(ch, ch) for ch in word)


_SR_ONES = {"jedan": 1, "jedna": 1, "jedno": 1, "dva": 2, "dve": 2, "tri": 3,
            "četiri": 4, "pet": 5, "šest": 6, "sedam": 7, "osam": 8,
            "devet": 9}
# "petnaest" (15) is deliberately absent: it is the clock's literal FRACTION
# terminal (clock_fraction_15.voc, alongside "četvrt") in "petnaest do sedam"
# == 6:45, and folding it to a digit here would strand that reading -- a
# spelled "petnaest <unit>" duration is out of scope for v1 (write the digit
# "15" instead).
_SR_TEENS = {"deset": 10, "jedanaest": 11, "dvanaest": 12, "trinaest": 13,
             "četrnaest": 14, "šesnaest": 16,
             "sedamnaest": 17, "osamnaest": 18, "devetnaest": 19}
_SR_TENS = {"dvadeset": 20, "trideset": 30, "četrdeset": 40, "pedeset": 50,
            "šezdeset": 60, "sedamdeset": 70, "osamdeset": 80,
            "devedeset": 90}
_SR_HUNDRED = {"sto": 100}
# "pola"/"četvrt" are deliberately NOT in this run set: they are the clock's
# literal FRACTION terminal (clock_fraction_15.voc/clock_fraction_30.voc),
# and folding them into a cardinal run here would fuse an adjacent HOUR
# ("pola četiri") into one wrong NUM instead of leaving FRACTION and HOUR as
# two slots -- mirroring the cs "půl" note above, not hr's "pola" inclusion
# (hr never binds a clock FRACTION slot, so it has no such collision).


def _sr_double(table: dict) -> dict:
    out = dict(table)
    out.update({sr_lat2cyr(w): v for w, v in table.items()})
    return out


_SR_WORDS = {**_sr_double(_SR_ONES), **_sr_double(_SR_TEENS),
             **_sr_double(_SR_TENS), **_sr_double(_SR_HUNDRED)}


def _extract_sr(text: str):
    """Compose a spelled sr cardinal from its parts (an optional hundred, an
    optional ten-or-teen, an optional one): "sto dvadeset pet" == 125,
    "dvadeset pet" == 25, "pet" == 5.  Any unknown word fails the whole run,
    mirroring the shared model-backed ``_extract``."""
    words = text.split()
    if not words or any(w not in _SR_WORDS for w in words):
        return False
    return float(sum(_SR_WORDS[w] for w in words))


def _make_fold_sr() -> Callable[[Tuple[Token, ...]], Tuple[Token, ...]]:
    return make_fold(NumberGrammar(
        is_number=lambda tok: tok.is_number or tok.text in _SR_WORDS,
        extract=_extract_sr))


# -- calendar day: genitive-masculine ordinal, elided "dana" -----------------
# Serbian names the day of the month with a genitive-masculine ordinal
# agreeing with an elided "dana" ("petog maja" = the fifth of May), the same
# shape as the other Slavic genitive-day tables above.  Citation: Fond
# projekta Rastko / Правопис српскога језика (Матица српска), писање датума;
# spot-checked against Wiktionary's individual ordinal entries (prvi, drugi,
# treći, ...).  Compound days 21-31 leave the tens a bare cardinal and
# decline only the unit ("dvadeset petog" = 25th), mirroring hr's tens_prefix
# composition; both scripts via ``sr_lat2cyr``.
_DAY_SR = {}
for _stem, _v in (("prvog", 1), ("drugog", 2), ("trećeg", 3),
                  ("četvrtog", 4), ("petog", 5), ("šestog", 6),
                  ("sedmog", 7), ("osmog", 8), ("devetog", 9),
                  ("desetog", 10), ("jedanaestog", 11), ("dvanaestog", 12),
                  ("trinaestog", 13), ("četrnaestog", 14), ("petnaestog", 15),
                  ("šesnaestog", 16), ("sedamnaestog", 17),
                  ("osamnaestog", 18), ("devetnaestog", 19),
                  ("dvadesetog", 20), ("tridesetog", 30)):
    _DAY_SR[_stem] = _v
    _DAY_SR[sr_lat2cyr(_stem)] = _v
_TENS_SR = {"dvadeset": 20, "trideset": 30}
_TENS_SR.update({sr_lat2cyr(w): v for w, v in dict(_TENS_SR).items()})

fold_sr = _compose(_day_rewrite(_DAY_SR, _TENS_SR), _make_fold_sr())
