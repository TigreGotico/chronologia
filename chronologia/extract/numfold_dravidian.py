# -*- coding: utf-8 -*-
"""Spelled-number folding and the fraction clock, for Tamil.

Tamil numerals do not compose by concatenation.  A compound is built on a
distinct ADJECTIVAL stem -- ஒரு, இரு, மு, நால், ஐ, அறு, ஏழ், எண், பதின் --
and the join triggers sandhi at the seam, so 11 is பதினொன்று rather than
பத்து ஒன்று and 21 is இருபத்தொன்று rather than இருபது ஒன்று.  The hundreds are
suppletive in the same way: முந்நூறு is 300 and நானூறு is 400, neither of them
derivable from மூன்று or நான்கு by any rule this module could apply.  The table
below is therefore transcribed surface by surface from the source cited on it,
and NOTHING in it is generated.  A value with no transcribed surface simply does
not fold; the digits still read, and inventing the missing spelling would be a
guess dressed up as coverage.

The clock counts FORWARD
------------------------
The fraction attaches to the hour just named and adds to it.  ``ஒன்பதரை`` is
9:30 -- "nine-and-a-half", the fraction அரை fused onto the numeral -- and
``ஒன்பதே கால்`` is 9:15, the quarter கால் after the numeral carrying the
emphatic -ஏ.  A reader who takes the European "half nine" reading and subtracts
gets 8:30 for every one of them, so the direction is pinned in both senses by
the corpus.

Backward readings exist and are OVERTLY marked, which is what makes them safe
to read at all.  ``மூன்று மணிக்கு பத்து நிமிடம் மேல்`` is 3:10 -- மேல் is
"above, past" -- and ``ஆறு மணிக்கு பதினைந்து நிமிடம் குறைவு`` is 5:45, because
குறைவு is "less" and the hour it names is the UPCOMING one.  Both markers are
phrase-final and neither reading is recoverable without one, so a minute tail
carrying no marker is read forward, the direction the fused forms establish.

What the clock refuses
----------------------
``முக்கால்`` (three quarters) is a fraction word of the language, but no source
consulted worked it out as a clock reading.  Reading it as three quarters past
the named hour is an analogy from அரை and கால், and an analogy is not evidence,
so a numeral carrying it is WITHDRAWN as an opaque token: the phrase reaches no
construction and the extractor answers nothing rather than a plausible 9:45.

The fused அரை forms and the -ஏ கால் forms are shipped only for the hour the
sources actually work out.  Both fusions elide the numeral's final vowel before
the following one, and that elision applied to the other eleven hours would be
generated spelling, not attested spelling -- the same line the numeral table
draws.  The general shapes ``N மணி``, ``N மணி M நிமிடம்`` and the two marked
constructions carry every other reading and need no fused surface.

The locative is the direction
-----------------------------
"In N units" carries no preposition in Tamil: the direction is the locative
suffix -இல் on the counted noun itself, so ``மூன்று நாட்களில்`` is "in three
days" while ``மூன்று நாட்களுக்கு முன்`` is "three days ago" with the dative and
a trailing முன்.  The engine reads a direction from a marker TOKEN, and there
is no token here to read, so the locative pass below cuts the fused surface in
two -- the unit in its citation form, and the suffix as the separate forward
marker the locale ships as ``marker_future.voc``.  The pairs are transcribed
from CLDR's own in-N patterns one by one; the suffix is not stripped by rule,
because the oblique stem it attaches to differs per noun (மாதம் -> மாதத்தில்,
நாள் -> நாளில்) and a rule would have to invent those stems.

The day-period word picks the hour, from the CLDR band
------------------------------------------------------
A clock phrase carries its half-day in front: ``காலை ஒன்பதரை மணி`` is 9:30 in
the morning, ``மாலை ஆறு மணி`` is 18:00.  The reading is NOT a blanket "add
twelve for an afternoon word", because Tamil draws nine day-period bands and
one of them wraps midnight: ``இரவு இரண்டு மணி`` is 02:00, and a flat +12 would
answer 14:00 for a phrase naming the small hours.  The band a word names is
therefore consulted directly -- the CLDR boundaries in
:mod:`chronologia.dayparts`, never a second copy of them here -- and the spoken
hour is placed at whichever of its two twelve-hour readings falls inside that
band.  When neither does, or both do, the phrase is withdrawn: ``காலை ஒரு
மணி`` names an hour outside the morning band and nobody says it, so answering
either 01:00 or 13:00 would be a guess.

``மணி`` is read as the hour word only next to a numeral.  Its first dictionary
sense is "bell", and several further senses follow it, so the bare word binds
nothing on its own -- it is deliberately absent from the locale's unit
vocabulary, where the duration noun is மணிநேரம் instead.

Sources.  Weekday, month, relative-time and day-period data: Unicode CLDR
(``cldr-dates-full/main/ta/ca-gregorian.json``, ``dateFields.json``,
``cldr-cal-indian-full/main/ta/ca-indian.json``, and the supplemental
``dayPeriods`` ruleset for ``ta``).  Cardinals, the adjectival compounding
stems, the colloquial doublets and the fraction words: Wiktionary
``Module:number_list/data/ta``.  Clock direction and the two marked
constructions with their worked numbers: Preply "Telling the time in Tamil",
ling-app.com "How To Express Date And Time In Tamil" and Talkpal "Telling Time
in Tamil Language".  Nothing is delegated to an external number back-end.

Tamil digits ௦-௯ (U+0BE6..U+0BEF) need no pass here: they are Unicode decimal
digits, so the shared tokenizer already reads ``௨௦௨௬`` as 2026 and the clock
and ISO literals match them as readily as the ASCII ones.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex

# ---------------------------------------------------------------------------
# Cardinals.  Every surface below is transcribed from
# ``Module:number_list/data/ta`` on en.wiktionary.org; the compounds are the
# module's own spelled-out entries, never a join of two base stems.  The
# colloquial doublets (ஒண்ணு, ரெண்டு, ...) are carried in the same module and
# are a real spoken register, so they are read.
#
# The teens above thirteen and the unit-bearing compounds of thirty and above
# are ABSENT on purpose: their surfaces were not transcribed, and the seam
# sandhi that would generate them is exactly what the module's spelled-out
# entries show is not mechanical.  They fold as digits and not as words.
# ---------------------------------------------------------------------------
_CARDINALS: Dict[str, int] = {}


def _card(value: int, *surfaces: str) -> None:
    for s in surfaces:
        _CARDINALS[s] = value


# ஒரு is the ADJECTIVAL stem of one, which is the form that stands before a
# counted noun ("ஒரு வாரத்தில்" -- in one week); it is also the indefinite
# article, and the two senses are the same word doing the same work, so
# reading it as the count of one is right in both.
_card(1, "ஒன்று", "ஒண்ணு", "ஒரு")
_card(2, "இரண்டு", "ரெண்டு")
_card(3, "மூன்று", "மூணு")
_card(4, "நான்கு", "நாலு")
_card(5, "ஐந்து", "அஞ்சு")
_card(6, "ஆறு")
_card(7, "ஏழு")
_card(8, "எட்டு")
_card(9, "ஒன்பது")
_card(10, "பத்து")
_card(11, "பதினொன்று")
_card(12, "பன்னிரண்டு")
_card(13, "பதின்மூன்று")
_card(15, "பதினைந்து")
_card(20, "இருபது")
_card(21, "இருபத்தொன்று", "இருவத்தொண்ணு")
_card(30, "முப்பது")
_card(40, "நாற்பது")
_card(50, "ஐம்பது")
_card(60, "அறுபது")
_card(70, "எழுபது")
_card(80, "எண்பது")
_card(90, "தொண்ணூறு")
_card(100, "நூறு")
_card(101, "நூற்றொன்று")
_card(200, "இருநூறு")
_card(300, "முந்நூறு")
_card(400, "நானூறு")
_card(500, "ஐந்நூறு")
_card(600, "அறுநூறு")
_card(700, "எழுநூறு")
_card(800, "எண்ணூறு")
_card(900, "தொள்ளாயிரம்")
_card(1000, "ஆயிரம்")

#: ஆயிரம் multiplies the group before it and closes it into the running total,
#: which is how a year is spoken (இரண்டு ஆயிரம் இருபது == 2020).  ``நூறு`` is
#: NOT a multiplier here: the two-hundreds through nine-hundreds are suppletive
#: words in their own right above, so a numeral before நூறு is a separate
#: number, not its multiplicand.
_THOUSAND = "ஆயிரம்"


def read_run(text: str) -> Optional[int]:
    """The value of a space-separated run of Tamil number-word surfaces.

    Additive over the transcribed words, with ஆயிரம் multiplying the group
    accumulated so far.  Returns ``None`` when any word is not a number-word,
    so a partial reading is never committed.
    """
    total = 0
    group = 0
    seen = False
    for word in text.split():
        if word.isdigit():
            group += int(word)
            seen = True
            continue
        if word == _THOUSAND:
            group = (group or 1) * 1000
            total += group
            group = 0
            seen = True
            continue
        value = _CARDINALS.get(word)
        if value is None:
            return None
        group += value
        seen = True
    return total + group if seen else None


#: the magnitude class of a cardinal surface, which is what licenses one word
#: to continue a run another opened.  A composed numeral descends through the
#: classes, and two words of the SAME class never compose -- that is what keeps
#: two adjacent numerals two numbers rather than the single sum an
#: unconditioned scan would read.
_UNIT_CLASS, _HUNDRED_CLASS, _SCALE_CLASS = 1, 2, 3


def _magnitude(word: str) -> int:
    if word == _THOUSAND:
        return _SCALE_CLASS
    if _CARDINALS.get(word, 0) >= 100:
        return _HUNDRED_CLASS
    return _UNIT_CLASS


def _composes(previous: str, following: str) -> bool:
    prev, nxt = _magnitude(previous), _magnitude(following)
    if nxt > prev:
        return nxt == _SCALE_CLASS
    return nxt < prev


# ---------------------------------------------------------------------------
# The clock
# ---------------------------------------------------------------------------

#: the hour word, in the bare form and in the dative the "at N o'clock" and the
#: two marked constructions govern.
_HOUR_WORDS = ("மணி", "மணிக்கு")
#: the minute word, in the bare form and in the dative.
_MINUTE_WORDS = ("நிமிடம்", "நிமிடத்திற்கு")
#: மேல் "above, past" -- minutes counted forward from the named hour.
_DIR_PAST = "மேல்"
#: குறைவு "less" -- minutes counted back from the named hour, which is the
#: UPCOMING one, so ``ஆறு மணிக்கு பதினைந்து நிமிடம் குறைவு`` is 5:45.
_DIR_TO = "குறைவு"

#: the fused half-hour, and the emphatic-plus-quarter pair, for the one hour
#: the sources work out in full.  ``ஒன்பதரை`` is ஒன்பது with its final vowel
#: elided before அரை.
_FUSED_HALF: Dict[str, int] = {"ஒன்பதரை": 9}
#: the numeral carrying the emphatic -ஏ, which is what ``கால்`` follows.
_EMPHATIC: Dict[str, int] = {"ஒன்பதே": 9}
_QUARTER = "கால்"
#: the three-quarters fraction.  Recognised so the phrase carrying it can be
#: WITHDRAWN; never read, because no source works it out on a clock.
_THREE_QUARTERS = "முக்கால்"


# ---------------------------------------------------------------------------
# The locative "in N units" surfaces, each mapped to the citation form of the
# unit it inflects.  Every key is a CLDR ``dateFields.json`` future pattern for
# ``ta``, singular and plural; the value is the surface the locale's own
# ``unit_*.voc`` ships.
# ---------------------------------------------------------------------------
_LOCATIVE: Dict[str, str] = {
    "ஆண்டில்": "ஆண்டு", "ஆண்டுகளில்": "ஆண்டுகள்",
    "மாதத்தில்": "மாதம்", "மாதங்களில்": "மாதங்கள்",
    "வாரத்தில்": "வாரம்", "வாரங்களில்": "வாரங்கள்",
    "நாளில்": "நாள்", "நாட்களில்": "நாட்கள்",
    "மணிநேரத்தில்": "மணிநேரம்",
    "நிமிடத்தில்": "நிமிடம்", "நிமிடங்களில்": "நிமிடங்கள்",
    "விநாடியில்": "விநாடி", "விநாடிகளில்": "விநாடிகள்",
}
#: the suffix, emitted as its own token so the engine has a direction marker
#: to bind.  It is never written detached in Tamil, so the surface is
#: unreachable from ordinary text.
_LOCATIVE_MARKER = "இல்"


def _numeric(tok: Token, value: int, end: Token = None) -> Token:
    return Token(text=str(value), raw=str(value), index=tok.index,
                 is_number=True, value=value, char_start=tok.char_start,
                 char_end=(end or tok).char_end)


def _clock_literal(hour: int, minute: int, first: Token, last: Token) -> Token:
    text = f"{hour}:{minute:02d}"
    return Token(text=text, raw=text, index=first.index,
                 char_start=first.char_start, char_end=last.char_end)


def _opaque(first: Token, last: Token, text: str) -> Token:
    """A lexical token standing for a refused reading: it binds no slot, so the
    span it covers reaches no construction and the extractor answers nothing."""
    return Token(text=text, raw=text, index=first.index,
                 char_start=first.char_start, char_end=last.char_end)


def _locative_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Cut a locative-marked unit into the unit plus the forward marker."""
    out: List[Token] = []
    changed = False
    for t in tokens:
        base = None if t.is_number else _LOCATIVE.get(t.text)
        if base is None:
            out.append(t)
            continue
        out.append(Token(text=base, raw=t.raw, index=len(out),
                         char_start=t.char_start, char_end=t.char_end))
        out.append(Token(text=_LOCATIVE_MARKER, raw="", index=len(out),
                         char_start=t.char_end, char_end=t.char_end))
        changed = True
    return reindex(out) if changed else tokens


#: the day-period surfaces that may lead a clock phrase, mapped to the
#: registry key of the band they name.  The keys are the locale's own
#: ``daypart_*_ta.voc`` file names, so a band can never be spellable in a clock
#: phrase but unknown to the registry.
_DAYPARTS: Dict[str, str] = {
    "அதிகாலை": "adhikaalai_ta",
    "காலை": "kaalai_ta",
    "மதியம்": "madhiyam_ta",
    "பிற்பகல்": "pirpakal_ta",
    "மாலை": "maalai_ta",
    "இரவு": "iravu_ta",
}
#: அந்தி மாலை is two words; the matcher glues multiword vocabulary but this
#: pass runs before that, so the pair is recognised here in its token form.
_DAYPART_PAIRS: Dict[Tuple[str, str], str] = {
    ("அந்தி", "மாலை"): "andhimaalai_ta",
}


def _band_hours(key: str) -> frozenset:
    """The whole hours the day-period band ``key`` covers, from the registry."""
    from chronologia.dayparts import DAY_PARTS
    part = DAY_PARTS[key]
    start, end = part.start.hour, part.end.hour
    span = (end - start) % 24 or 24
    # The CLDR band is half-open on INSTANTS, but an hour NAME sitting exactly
    # on a boundary belongs to neither half-open interval, and 18:00 is spoken
    # as மாலை ஆறு மணி as readily as it is with the band that opens there.  The
    # closing hour is therefore admitted as well.  It can never make a phrase
    # ambiguous: no band here is twelve hours wide, so at most one of an
    # hour's two twelve-hour readings ever lands inside one.
    return frozenset((start + k) % 24 for k in range(span + 1))


def _in_band(key: str, hour: int) -> bool:
    return hour in _band_hours(key)


def _pin_to_band(key: str, hour: int) -> Optional[int]:
    """``hour`` placed at whichever twelve-hour reading the band admits."""
    if hour > 12:
        return hour if _in_band(key, hour) else None
    candidates = {hour % 12, (hour % 12) + 12}
    inside = [h for h in sorted(candidates) if _in_band(key, h)]
    return inside[0] if len(inside) == 1 else None


def _daypart_at(tokens: Tuple[Token, ...], i: int) -> Tuple[Optional[str], int]:
    """The day-period band named at ``i``, and how many tokens it spans."""
    if i + 1 < len(tokens):
        key = _DAYPART_PAIRS.get((tokens[i].text, tokens[i + 1].text))
        if key is not None:
            return key, 2
    return _DAYPARTS.get(tokens[i].text), 1


def _cardinal_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold a well-formed run of spelled cardinals into one digit token."""
    out: List[Token] = []
    i, n, changed = 0, len(tokens), False
    while i < n:
        t = tokens[i]
        if t.is_number or t.text not in _CARDINALS:
            out.append(t)
            i += 1
            continue
        j = i + 1
        while (j < n and not tokens[j].is_number
               and tokens[j].text in _CARDINALS
               and _composes(tokens[j - 1].text, tokens[j].text)):
            j += 1
        value = read_run(" ".join(tok.text for tok in tokens[i:j]))
        if value is None:
            out.append(t)
            i += 1
            continue
        out.append(_numeric(t, value, tokens[j - 1]))
        i, changed = j, True
    return reindex(out) if changed else tokens


def _int_at(tokens: Tuple[Token, ...], k: int) -> Optional[int]:
    t = tokens[k] if 0 <= k < len(tokens) else None
    if (t is not None and t.is_number and t.value is not None
            and float(t.value).is_integer()):
        return int(t.value)
    return None


def _minute_tail(tokens: Tuple[Token, ...], i: int) -> Tuple[int, int, int]:
    """The minute tail at ``i``: ``(minutes, direction, tokens consumed)``.

    A count plus the minute word, optionally closed by மேல் (forward) or
    குறைவு (backward, off the UPCOMING hour).  Direction is ``+1`` when
    unmarked, the direction the fused fractions establish.  ``(0, 0, 0)`` when
    there is no minute tail here.
    """
    value = _int_at(tokens, i)
    if value is None or not 0 <= value <= 59:
        return 0, 0, 0
    if i + 1 >= len(tokens) or tokens[i + 1].text not in _MINUTE_WORDS:
        return 0, 0, 0
    used = 2
    direction = 1
    if i + 2 < len(tokens):
        if tokens[i + 2].text == _DIR_PAST:
            used = 3
        elif tokens[i + 2].text == _DIR_TO:
            used, direction = 3, -1
    return value, direction, used


def _hour_at(tokens: Tuple[Token, ...], i: int):
    """The hour phrase at ``i``.

    ``(hour, minute, consumed)`` for a reading, ``(None, None, consumed)`` for
    a phrase recognisably naming an hour whose value no source settles, and
    ``None`` when there is no hour phrase here at all.  Withdrawing the whole
    phrase in the middle case is what stops a refused fraction from decaying
    into the bare numeral behind it and answering a day of the month.
    """
    n = len(tokens)
    if i >= n:
        return None
    text = tokens[i].text

    if text in _FUSED_HALF:
        used = 1
        if i + 1 < n and tokens[i + 1].text in _HOUR_WORDS:
            used = 2
        return _FUSED_HALF[text], 30, used

    if text in _EMPHATIC:
        following = tokens[i + 1].text if i + 1 < n else None
        if following == _QUARTER:
            used = 2
            if i + 2 < n and tokens[i + 2].text in _HOUR_WORDS:
                used = 3
            return _EMPHATIC[text], 15, used
        if following == _THREE_QUARTERS:
            used = 2
            if i + 2 < n and tokens[i + 2].text in _HOUR_WORDS:
                used = 3
            return None, None, used
        return None

    hour = _int_at(tokens, i)
    if hour is None or not 0 <= hour <= 23:
        return None
    if i + 1 >= n or tokens[i + 1].text not in _HOUR_WORDS:
        return None
    if i + 2 < n and tokens[i + 2].text == _THREE_QUARTERS:
        return None, None, 3
    minute, direction, extra = _minute_tail(tokens, i + 2)
    if extra and direction < 0:
        # குறைவு counts back off the UPCOMING hour: "fifteen minutes less than
        # six" is 5:45, an hour earlier than the hour the phrase names.
        if minute == 0:
            return None, None, 2 + extra
        return (hour - 1) % 24, 60 - minute, 2 + extra
    return hour, minute, 2 + extra


def _clock_rewrite(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fuse a clock phrase into one clock literal, or withdraw it."""
    out: List[Token] = []
    i, n, changed = 0, len(tokens), False
    while i < n:
        band, lead = _daypart_at(tokens, i)
        found = _hour_at(tokens, i + lead) if band is not None else None
        if found is None:
            band, lead = None, 0
            found = _hour_at(tokens, i)
        if found is None:
            out.append(tokens[i])
            i += 1
            continue
        hour, minute, used = found
        used += lead
        last = tokens[i + used - 1]
        if hour is not None and band is not None:
            hour = _pin_to_band(band, hour)
            minute = minute if hour is not None else None
        if hour is None:
            raw = " ".join(t.raw for t in tokens[i:i + used])
            out.append(_opaque(tokens[i], last, raw))
        else:
            out.append(_clock_literal(hour % 24, minute, tokens[i], last))
        i, changed = i + used, True
    return reindex(out) if changed else tokens


def _compose(*passes: Callable) -> Callable:
    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        for p in passes:
            tokens = p(tokens)
        return tokens
    return run


fold_ta = _compose(_locative_rewrite, _cardinal_rewrite,
                   _clock_rewrite)
