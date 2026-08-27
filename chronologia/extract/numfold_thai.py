# -*- coding: utf-8 -*-
"""Word segmentation, spelled-number folding and the six-hour clock, for Thai.

Thai is written in *scriptio continua*: there is no space between words, only
between phrases and sentences.  The shared tokenizer emits maximal letter runs,
so a whole Thai date phrase arrives as ONE token and no slot can bind any part
of it.  Everything here exists to turn that single run into the token stream the
rest of the engine already understands.

Segmentation -- exact cover, or nothing
---------------------------------------
A Thai run is split only when the *whole* run is covered, end to end, by
surfaces this locale actually knows: the vocabulary it ships plus the numeral
and clock words below.  Where a cover exists the run is cut into those words,
longest first; where none exists the token is handed on untouched.

That is a deliberate refusal rather than a limitation.  Maximal-match
segmentation would happily cut a temporal reading out of the middle of ordinary
prose, and Thai is full of temporal homographs that make the cut wrong:
``จันทร์`` is Monday and also the moon, ``อาทิตย์`` is Sunday and also the week,
``ตี`` is the small-hours word and also the everyday verb "to hit", ``ทุ่ม`` is
the evening hour word and also "to hurl".  Requiring the cover to consume the
entire run means a numeral syllable sitting inside an ordinary word can never
be mistaken for a count: prose is left alone, and a date phrase standing as its
own run -- which is how Thai's phrase spacing presents one -- reads exactly.

The dictionary is READ FROM THE LOCALE'S OWN ``.voc`` FILES rather than
restated here, so a surface can never be segmentable but unmatchable, or
matchable but unsegmentable.

Numerals
--------
Digit words 0-9 and the ascending place words ``สิบ`` 10, ``ร้อย`` 100, ``พัน``
1 000, ``หมื่น`` 10 000, ``แสน`` 100 000, ``ล้าน`` 1 000 000, joined by
positional concatenation with three irregularities:

* a units digit of 1 following a higher place is ``เอ็ด``, not ``หนึ่ง``
  (21 is ``ยี่สิบเอ็ด``);
* a tens digit of 1 drops its digit word, leaving bare ``สิบ`` (10 is ``สิบ``,
  15 is ``สิบห้า``);
* a tens digit of 2 is ``ยี่``, not ``สอง`` (20 is ``ยี่สิบ``).

Those three shapes are the ONLY licensed spellings of their values, so
``หนึ่งสิบ`` and ``สองสิบ`` are refused rather than read as 10 and 20: they are
arithmetically obvious and orthographically unattested, and accepting them
would invent a surface.  Two variants are read but never generated: a final 1
spelled ``หนึ่ง`` in place of ``เอ็ด`` (military register) and ``ซาว`` for
``ยี่สิบ`` (dialectal).

Thai digits ๐-๙ (U+0E50..) need no handling here: they are Unicode decimal
digits, so the shared tokenizer already reads ``๒๕๖๘`` as 2568.

The six-hour clock
------------------
Thai counts minutes FORWARD from the hour just named -- there is no subtractive
form -- but the hour's NAME runs on a six-hour cycle whose word changes with the
part of the day.  Minutes are the number plus ``นาที``, and ``นาที`` is
frequently dropped; ``ครึ่ง`` ("half") is the thirty-minute mark and follows the
hour word.  The shapes read here, and only these:

======================  ==============  =========================
shape                   reading         worked example
======================  ==============  =========================
``ตี`` N, N = 1..5      01:00..05:00    ``ตีสาม`` 03:00
N ``ทุ่ม``, N = 1..5    18 + N          ``หนึ่งทุ่ม`` 19:00
N ``โมงเช้า``, N = 6..11  N             ``แปดโมงครึ่ง`` 08:30
``บ่ายโมง``             13:00           ``บ่ายโมงสิบห้านาที`` 13:15
``บ่าย`` N ``โมง``, N = 2,3   12 + N    ``บ่ายสองโมง`` 14:00
``หกโมงเย็น``           18:00
======================  ==============  =========================

Everything outside that table is refused, for two separate reasons.

*The disputed late afternoon.*  The sources consulted disagree about which
label covers 16:00-18:59 -- one assigns ``โมงเย็น`` to 16:00-18:00 and starts
``ทุ่ม`` at 19:00, another runs ``บ่าย`` from 13:00 to 18:00, a third gives the
afternoon quarter as 13:00-18:59.  The disagreement is about the label, not the
arithmetic, but it means ``บ่ายสี่โมง`` and ``สี่โมงเย็น`` may or may not be the
same reading of 16:00 depending on whose table you take.  Only the band all
three agree on ships: ``บ่าย`` counts to 15:00 and ``โมงเย็น`` is read at the
single hour a source works out in full, ``หกโมงเย็น`` 18:00.  The 16:00-17:00
band is omitted rather than assigned to a winner.

*Bare* ``N โมง``.  ``หกโมงเช้า`` is 06:00 and ``หกโมงเย็น`` is 18:00, and one
source's own worked example glosses bare ``หกโมงห้านาที`` as an evening reading
while another's table puts bare ``หกโมง`` in the morning.  A ``โมง`` phrase
carrying no ``เช้า``/``เย็น``/``บ่าย`` is therefore genuinely ambiguous between
the two half-days and nothing inside the phrase separates them, so the run is
withdrawn as an opaque token and the extractor answers nothing rather than
picking a half-day.  ``ตี N`` and ``N ทุ่ม`` carry their half-day in the hour
word itself and are read.

``N โมงเช้า`` is read as N o'clock directly, for N = 6..11 only.  Every worked
morning example in the sources takes that reading -- 6, 7 and 8 with ``โมงเช้า``
are 06:00, 07:00 and 08:00 -- while the traditional cycle would number the same
hours 1..5.  The two numberings collide exactly on 1..5, so ``หนึ่งโมงเช้า``
through ``ห้าโมงเช้า`` are refused and 6..11, where no competing reading exists,
are read.

Sources.  Weekday, month, relative-time and day-period data: Unicode CLDR
(``cldr-dates-full/main/th/ca-gregorian.json``, ``dateFields.json``, and the
supplemental ``dayPeriods`` ruleset for ``th``).  Numerals, the three
irregularities and the ``หนึ่ง``/``ซาว`` variants: Wiktionary
``Module:number_list/data/th`` and ``Module:th-utilities``.  Clock direction,
minute forms and the per-quarter hour words: the "Telling time in Thai" A1
grammar point of Complete Thai, "Thai Time Expressions Explained" of The
Thaiger, and Wikipedia's "Thai six-hour clock".  Nothing is delegated to an
external number back-end.
"""
from __future__ import annotations

import glob
import os
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

_LOCALE_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "locale", "th")

#: 0..9 in their citation form.
DIGITS: Dict[str, int] = {
    "ศูนย์": 0, "หนึ่ง": 1, "สอง": 2, "สาม": 3, "สี่": 4,
    "ห้า": 5, "หก": 6, "เจ็ด": 7, "แปด": 8, "เก้า": 9,
}

#: ascending place words below the million.
PLACES: Dict[str, int] = {
    "สิบ": 10, "ร้อย": 100, "พัน": 1000, "หมื่น": 10000, "แสน": 100000,
}
MILLION = "ล้าน"
TEN = "สิบ"
#: the tens-place form of two: ยี่ takes สิบ after it, while the dialectal ซาว
#: is the whole of twenty on its own.
TENS_TWO = "ยี่"
TWENTY_DIALECTAL = "ซาว"
#: the units-place form of one after a higher place.
UNIT_ONE = "เอ็ด"

#: the hour words of the six-hour cycle, and the day-part words that pin a
#: ``โมง`` hour to a half-day.
HOUR_TI = "ตี"          # the small hours
HOUR_THUM = "ทุ่ม"       # the evening
HOUR_MONG = "โมง"        # the ambiguous hour word
BAI = "บ่าย"             # the early afternoon
CHAO = "เช้า"            # the morning
YEN = "เย็น"             # the late afternoon / early evening
HALF = "ครึ่ง"
MINUTE_WORD = "นาที"

#: every word this module contributes to the segmentation dictionary in its own
#: right -- the numeral and clock vocabulary, which is deliberately NOT shipped
#: as locale ``.voc`` (``โมง``/``ตี``/``ทุ่ม`` must never bind a slot on their
#: own; they are only ever read next to a numeral).
_OWN_WORDS = (frozenset(DIGITS) | frozenset(PLACES)
              | {TENS_TWO, TWENTY_DIALECTAL, MILLION, UNIT_ONE,
                 HOUR_TI, HOUR_THUM, HOUR_MONG, BAI, CHAO, YEN,
                 HALF, MINUTE_WORD})


def _is_thai(text: str) -> bool:
    return bool(text) and all("ก" <= ch <= "๛" for ch in text)


_DICT: Optional[frozenset] = None


def dictionary() -> frozenset:
    """Every Thai-script surface the segmenter may cut a run into.

    The locale's own ``.voc`` surfaces, read once straight off disk, plus this
    module's numeral and clock words.  Reading the shipped files rather than
    restating them is what keeps the segmenter and the matcher from disagreeing
    about what Thai words exist.
    """
    global _DICT
    if _DICT is None:
        words = set(_OWN_WORDS)
        for path in glob.glob(os.path.join(_LOCALE_DIR, "*.voc")):
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#") and _is_thai(line):
                        words.add(line)
        _DICT = frozenset(words)
    return _DICT


_MAX_WORD_LEN: Optional[int] = None


def _max_word_len() -> int:
    """The longest surface in the dictionary: the cover search never scans
    further back than it could possibly match."""
    global _MAX_WORD_LEN
    if _MAX_WORD_LEN is None:
        _MAX_WORD_LEN = max(len(w) for w in dictionary())
    return _MAX_WORD_LEN


#: a run longer than this is prose, not a date phrase; covering it is not worth
#: the quadratic scan and a cover that long would be an accident anyway.
MAX_RUN = 64


def segment(run: str) -> Optional[List[str]]:
    """Cut ``run`` into dictionary words covering it exactly, or ``None``.

    Longest-word-first among the exact covers, so ``วันจันทร์`` reads as the
    weekday and never as ``วัน`` + ``จันทร์`` ("day" + "moon").
    """
    if not run or len(run) > MAX_RUN or not _is_thai(run):
        return None
    words = dictionary()
    n, longest = len(run), _max_word_len()
    # reach[j] is True when run[:j] is exactly covered.
    reach = [False] * (n + 1)
    reach[0] = True
    for j in range(1, n + 1):
        for k in range(max(0, j - longest), j):
            if reach[k] and run[k:j] in words:
                reach[j] = True
                break
    if not reach[n]:
        return None
    out: List[str] = []
    j = n
    while j:
        for k in range(max(0, j - longest), j):
            if reach[k] and run[k:j] in words:
                out.append(run[k:j])
                j = k
                break
    out.reverse()
    return out


def read(words: Sequence[str]) -> Tuple[Optional[int], int]:
    """Read the longest well-formed numeral at the head of ``words``.

    Returns the value and how many words it consumed, or ``(None, 0)``.  A
    partial reading is never committed.
    """
    value, i = _below_million(words, 0)
    if value is None:
        return None, 0
    if i < len(words) and words[i] == MILLION:
        rest, j = _below_million(words, i + 1)
        return value * 1000000 + (rest or 0), (j if rest is not None else i + 1)
    return value, i


def _below_million(words: Sequence[str], i: int) -> Tuple[Optional[int], int]:
    start, total, seen, last = i, 0, False, None
    n = len(words)
    while i < n:
        w = words[i]
        if w == TEN:                              # bare tens: สิบห้า == 15
            if last is not None and last <= 10:
                break
            total, last, i, seen = total + 10, 10, i + 1, True
            continue
        if w == TENS_TWO and i + 1 < n and words[i + 1] == TEN:
            if last is not None and last <= 10:
                break
            total, last, i, seen = total + 20, 10, i + 2, True
            continue
        if w == TWENTY_DIALECTAL:
            if last is not None and last <= 10:
                break
            total, last, i, seen = total + 20, 10, i + 1, True
            continue
        if w == UNIT_ONE:                         # ยี่สิบเอ็ด == 21
            if not seen or (last is not None and last <= 1):
                break
            return total + 1, i + 1
        if w in DIGITS:
            d = DIGITS[w]
            if i + 1 < n and words[i + 1] in PLACES:
                place = PLACES[words[i + 1]]
                # the tens place spells 1 as bare สิบ and 2 as ยี่สิบ, so a
                # digit word there is not a tens compound at all; the digit is
                # read on its own and the place word left to open the next
                # numeral, which is how the unspaced สอง + สิบ of "ตีสองสิบ
                # นาที" reads as 2 and 10 rather than as nothing.
                licensed = not (place == 10 and d in (1, 2)) and (
                    last is None or place < last)
                if licensed:
                    total, last, i, seen = total + d * place, place, i + 2, True
                    continue
            if last is not None and last <= 1:
                break
            return (total + d, i + 1) if seen else (d, i + 1)
        break
    return (total, i) if seen else (None, start)


def read_run(text: str) -> Optional[int]:
    """The value of a Thai numeral written as one unspaced run, or ``None``."""
    words = segment(text)
    if words is None:
        return None
    value, used = read(words)
    return value if value is not None and used == len(words) else None


def surface(n: int) -> str:
    """The spelled surface of ``n``, 0..999999999999 -- the three
    irregularities applied, so it and :func:`read` can never disagree."""
    n = int(n)
    if not 0 <= n <= 999999999999:
        raise ValueError(f"no attested Thai surface for {n}")
    if n >= 1000000:
        millions, rest = divmod(n, 1000000)
        head = surface(millions) + MILLION
        return head if rest == 0 else head + surface(rest)
    out = ""
    for word, place in (("แสน", 100000), ("หมื่น", 10000),
                        ("พัน", 1000), ("ร้อย", 100)):
        d, n = divmod(n, place)
        if d:
            out += _digit(d) + word
    tens, unit = divmod(n, 10)
    if tens == 1:
        out += TEN
    elif tens == 2:
        out += TENS_TWO + TEN
    elif tens:
        out += _digit(tens) + TEN
    if unit:
        out += UNIT_ONE if (unit == 1 and out) else _digit(unit)
    return out or _digit(0)


def _digit(d: int) -> str:
    return next(w for w, v in DIGITS.items() if v == d)


def _numeric(first: Token, value: int, last: Token) -> Token:
    return Token(text=str(value), raw=str(value), index=first.index,
                 is_number=True, value=value, char_start=first.char_start,
                 char_end=last.char_end)


def _opaque(first: Token, last: Token, text: str) -> Token:
    """A lexical token standing for a refused reading: it binds no slot, so the
    span it covers reaches no construction and the extractor answers nothing."""
    return Token(text=text, raw=text, index=first.index,
                 char_start=first.char_start, char_end=last.char_end)


def _segment_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Cut every exactly-coverable Thai run into its dictionary words."""
    out: List[Token] = []
    changed = False
    for tok in tokens:
        pieces = None if tok.is_number else segment(tok.text)
        if pieces is None or len(pieces) == 1:
            out.append(tok)
            continue
        changed = True
        offset = tok.char_start
        for word in pieces:
            start = None if offset is None else offset
            end = None if offset is None else offset + len(word)
            out.append(Token(text=word, raw=word, index=len(out),
                             char_start=start, char_end=end))
            if offset is not None:
                offset = end
    return reindex(out) if changed else tokens


def _cardinal_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    out: List[Token] = []
    i, n, changed = 0, len(tokens), False
    while i < n:
        tok = tokens[i]
        if tok.is_number:
            out.append(tok)
            i += 1
            continue
        j = i
        while j < n and not tokens[j].is_number:
            j += 1
        value, used = read([t.text for t in tokens[i:j]])
        if value is None:
            out.append(tok)
            i += 1
            continue
        out.append(_numeric(tok, value, tokens[i + used - 1]))
        i, changed = i + used, True
    return reindex(out) if changed else tokens


def _clock_literal(hour: int, minute: int, first: Token, last: Token) -> Token:
    text = f"{hour}:{minute:02d}"
    return Token(text=text, raw=text, index=first.index,
                 char_start=first.char_start, char_end=last.char_end)


def _minutes_at(tokens: Tuple[Token, ...], i: int) -> Tuple[int, int]:
    """The forward minute tail at ``i``: ``(minutes, tokens consumed)``.

    ``ครึ่ง`` is the half hour; a bare count is minutes with ``นาที`` optional.
    """
    n = len(tokens)
    if i < n and tokens[i].text == HALF:
        return 30, 1
    if i < n and tokens[i].is_number and tokens[i].value is not None:
        value = tokens[i].value
        if float(value).is_integer() and 0 <= value <= 59:
            if i + 1 < n and tokens[i + 1].text == MINUTE_WORD:
                return int(value), 2
            return int(value), 1
    return 0, 0


def _hour_at(tokens: Tuple[Token, ...], i: int):
    """The hour phrase at ``i``.

    ``(hour, consumed)`` for a reading, ``(None, consumed)`` for a phrase that
    is recognisably an hour but whose value the sources do not agree on, and
    ``None`` when there is no hour phrase here at all.  The middle case matters
    as much as the first: withdrawing the whole phrase -- period word included
    -- is what stops ``บ่ายสี่โมง`` from decaying into the bare ``บ่าย``
    day-part and answering the whole afternoon for a phrase that named one
    minute of it.
    """
    n = len(tokens)

    def num(k):
        t = tokens[k] if k < n else None
        if (t is not None and t.is_number and t.value is not None
                and float(t.value).is_integer()):
            return int(t.value)
        return None

    # ตี N -- the small hours, 01:00..05:00.  ตี alone is the everyday verb
    # "to hit", so the numeral is what makes it an hour word at all.
    if tokens[i].text == HOUR_TI:
        v = num(i + 1)
        if v is None:
            return None
        return (v, 2) if 1 <= v <= 5 else (None, 2)

    # บ่ายโมง == 13:00; บ่าย N โมง == 12 + N, for the hours all three sources
    # agree on.  A bare บ่าย with no โมง is the day-part word and is left to it.
    if tokens[i].text == BAI:
        if i + 1 < n and tokens[i + 1].text == HOUR_MONG:
            return 13, 2
        v = num(i + 1)
        if v is not None and i + 2 < n and tokens[i + 2].text == HOUR_MONG:
            return (12 + v, 3) if v in (2, 3) else (None, 3)
        return None

    v = num(i)
    if v is None:
        return None
    # N ทุ่ม -- the evening, 18 + N
    if i + 1 < n and tokens[i + 1].text == HOUR_THUM:
        return (18 + v, 2) if 1 <= v <= 5 else (None, 2)
    if i + 1 < n and tokens[i + 1].text == HOUR_MONG:
        period = tokens[i + 2].text if i + 2 < n else None
        if period == CHAO:
            return (v, 3) if 6 <= v <= 11 else (None, 3)
        if period == YEN:
            return (18, 3) if v == 6 else (None, 3)
        # bare N โมง: morning and evening are both live and nothing in the
        # phrase chooses.  Refuse, consuming both tokens so the numeral cannot
        # go on to be read as a day or a year on its own.
        return None, 2
    return None


def _clock_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fuse a six-hour-clock phrase into one clock literal, or withdraw it."""
    out: List[Token] = []
    i, n, changed = 0, len(tokens), False
    while i < n:
        found = _hour_at(tokens, i)
        if found is None:
            out.append(tokens[i])
            i += 1
            continue
        hour, used = found
        minute, extra = _minutes_at(tokens, i + used)
        if hour is None:
            used += extra
            raw = "".join(t.raw for t in tokens[i:i + used])
            out.append(_opaque(tokens[i], tokens[i + used - 1], raw))
            i, changed = i + used, True
            continue
        last = tokens[i + used + extra - 1]
        out.append(_clock_literal(hour % 24, minute, tokens[i], last))
        i, changed = i + used + extra, True
    return reindex(out) if changed else tokens


#: the era markers, written with internal dots so the tokenizer already splits
#: them into two letters plus the year.  Kept here rather than as locale
#: connector vocabulary because the era is applied as arithmetic on the year --
#: the Buddhist calendar shares the Gregorian months and days exactly, and
#: differs only in the year number -- so there is nothing left for a slot to
#: bind once the fold has read it.
_ERA_PREFIXES = {("พ", "ศ"): "buddhist",     # พ.ศ. -- Buddhist Era
                 ("ค", "ศ"): "common_era"}   # ค.ศ. -- Common Era


def _era_year(key: str, n: int) -> int:
    """``n`` in era ``key`` as a Common-Era year, through the shared registry
    (BE 2568 == 2025 CE), never a constant restated here."""
    from chronologia.eras import ERAS
    return ERAS[key].epoch.year + n - 1


def _era_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Read ``พ.ศ. 2568`` as the Common-Era year it names.

    Thai's civil year is normally the Buddhist Era, and the marker is the only
    thing that says so: CLDR's own long and full date patterns for ``th`` carry
    the era field precisely because a bare four-digit Thai year does not
    identify its own era.  A year carrying the marker is therefore converted
    here; a bare one is read as Common Era like every other locale's, because
    nothing in it chooses and guessing wrong is a 543-year error.
    """
    out: List[Token] = []
    i, n, changed = 0, len(tokens), False
    while i < n:
        key = _ERA_PREFIXES.get((tokens[i].text,
                                 tokens[i + 1].text if i + 1 < n else None))
        year = None
        if key is not None and i + 2 < n and tokens[i + 2].is_number:
            value = tokens[i + 2].value
            if value is not None and float(value).is_integer() and value > 0:
                year = _era_year(key, int(value))
        if year is None:
            out.append(tokens[i])
            i += 1
            continue
        out.append(_numeric(tokens[i], year, tokens[i + 2]))
        i, changed = i + 3, True
    return reindex(out) if changed else tokens


def _compose(*passes: Callable) -> Callable:
    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        for p in passes:
            tokens = p(tokens)
        return tokens
    return run


fold_th = _compose(_segment_rewrite, _cardinal_rewrite, _era_rewrite,
                   _clock_rewrite)
