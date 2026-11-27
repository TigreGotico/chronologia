"""Post-match vetoes: each one rejects a false reading after the match.

The two vetoes that re-parse a fragment import ``extract_timespan`` inside the
function, because :mod:`chronologia.extract.timespan` imports this module.
"""
from __future__ import annotations

import re
import unicodedata
from contextvars import ContextVar

from chronologia.extract.anchored import marker_names_a_reference


# A reference governed by a negation or exclusion ("not tomorrow", "any day
# but Friday") is refused, not resolved (docs/design/errors-by-construction.md).
# A bound phrase ("not before Monday") is a constraint, not an exclusion.
def _exclusion_vetoes(governing_text: str, spec) -> bool:
    """True when ``governing_text`` holds an exclusion trigger and no bound
    preposition. The caller must bound the text to the residue right before the
    reference; :func:`_exclusion_governing_veto` derives that region from tokens."""
    triggers = spec.exclusion_triggers
    if not triggers:
        return False
    words = re.findall(r"[^\W\d_]+", governing_text.lower(), re.UNICODE)
    if not words:
        return False
    if any(w in spec.exclusion_bound_guards for w in words):
        return False
    return any(w in triggers for w in words)


# Sentence ends: the Latin ".!?;", the ellipsis, the Greek question mark
# (U+037E), the Armenian full stop (U+0589), the Arabic question mark and
# full stop (U+061F, U+06D4), the Devanagari danda and double danda (U+0964,
# U+0965), and the line breaks.
_SENTENCE_ENDS = frozenset(
    ".!?;\u2026\u037e\u0589\u061f\u06d4\u0964\u0965\n\r\u2028\u2029")


def _sentence_boundary_between(text, start, end) -> bool:
    """True when a sentence end (see ``_SENTENCE_ENDS``) sits in the raw gap
    ``text[start:end]`` separating two adjacent tokens."""
    if start is None or end is None or end <= start:
        return False
    return any(c in _SENTENCE_ENDS for c in text[start:end])


# Locales that write the hour-letter clock ("20h", "21h30"); see the folds in
# numfold_romance, numlayer_el and numlayer_sv.
_HOUR_LETTER_LOCALES = frozenset({
    "ast", "ca", "el", "es", "fr", "gl", "it", "oc", "pt", "ro", "sv"})
_HOUR_LITERAL = re.compile(r"\d{1,2}:\d{2}")


def _folded_clock(token, text):
    """Whether a clock token was built by a fold ("2h" read as 2:00) and not
    typed as the digits it shows."""
    return (token.char_start is None or text is None
            or unicodedata.normalize(
                "NFKC", text[token.char_start:token.char_end]
            ).lower() != token.raw)


def _bare_hour_in_sentence(tokens, consumed, spec, text=None):
    """Whether the whole reading is a bare hour inside a sentence with no clock
    marker ("un film de 2h"), in a locale that writes the hour-letter clock.
    A marker from ``marker_hour_statement.voc`` or ``marker_hour_approx.voc``
    before it, or a day period after a letter hour, keeps it a clock."""
    if spec.lang.split("-")[0] not in _HOUR_LETTER_LOCALES:
        return False
    if not any(t.index not in consumed and t.text.strip(".,;:!?")
               for t in tokens):
        return False
    oclock = set(spec.connectors.get("oclock", ()))
    glue = ((set(spec.connectors.get("of", ()))
             | set(spec.connectors.get("article", ())))
            - set(spec.connectors.get("at", ())))
    read = [t for t in tokens if t.index in consumed and t.text not in glue]
    tail = (len(read) >= 2 and read[-2].text in spec.clock_dirs
            and read[-1].text in spec.clock_fractions)
    if tail:
        read = read[:-2]
    literal = (len(read) == 1 and _folded_clock(read[0], text)
               and _HOUR_LITERAL.fullmatch(read[0].text))
    counted = ((len(read) == 2 and read[0].is_number
                and read[1].text in oclock)
               or (tail and len(read) == 1 and read[0].is_number
                   and _folded_clock(read[0], text)))
    if not (literal or counted):
        return False
    markers = (spec.connectors.get("hour_statement", frozenset())
               | spec.connectors.get("hour_approx", frozenset()))
    before = [t.text.lower() for t in tokens[:read[0].index]]
    if any(" ".join(before[-n:]) in markers
           for n in range(1, min(len(before), 4) + 1)):
        return False
    return not (literal
                and _day_period_follows(tokens[read[-1].index + 1:], spec))


def _day_period_follows(after, spec):
    """Whether ``after`` opens with a day period or a day word, alone or
    behind a relative marker ("20h ce soir", "15h amanhã")."""
    words = [t.text.lower() for t in after[:2]]
    if words and words[0] in spec.rel_markers:
        words = words[1:]
    return bool(words) and (words[0] in spec.dayparts
                            or words[0] in spec.daypart_today_words
                            or words[0] in spec.named_days)


def _exclusion_governing_veto(tokens, consumed, text, spec) -> bool:
    """True when an exclusion trigger governs the winning reference: it sits in the
    run of skippable unconsumed tokens right before the span, and no bound guard
    is in the run. A coordinating trigger (``spec.exclusion_coord``) vetoes only
    when a scope word is also in the run."""
    triggers = spec.exclusion_triggers
    if not triggers or not consumed:
        return False
    span_start = min(consumed)
    skippable = set(triggers) | set(spec.exclusion_bound_guards) \
        | set(spec.exclusion_scope) | set(spec.exclusion_coord) \
        | set(spec.exclusion_filler)
    for forms in spec.connectors.values():
        skippable |= set(forms)
    run = []
    next_start = tokens[span_start].char_start if span_start < len(tokens) else None
    i = span_start - 1
    while i >= 0:
        tok = tokens[i]
        if tok.index in consumed:
            i -= 1
            continue
        if _sentence_boundary_between(text, tok.char_end, next_start):
            break
        w = tok.text.lower()
        if w not in skippable:
            break
        run.append(w)
        next_start = tok.char_start
        i -= 1
    if not run:
        return False
    words = set(run)
    if words & set(spec.exclusion_bound_guards):
        return False
    hard = set(triggers) - set(spec.exclusion_coord)
    if words & hard:
        return True
    if (words & set(spec.exclusion_coord)) and (words & set(spec.exclusion_scope)):
        return True
    return False


_veto_active: ContextVar[bool] = ContextVar("veto_active", default=False)


_CLOCK_LITERAL = re.compile(r"\d{1,2}:\d{2}(:\d{2})?")


def _clock_half_read(tokens, consumed, spec):
    """Whether a bound clock literal is followed by an unread "past" direction and
    a minute count ("ás 20h e 45"): no order adds minutes after a literal, so the
    phrase is refused. The number is a minute count only when it ends the phrase
    or carries a minute unit ("às 10:00 e 2 amigos" keeps its clock)."""
    for i, (here, after, count) in enumerate(
            zip(tokens, tokens[1:], tokens[2:])):
        if (here.index in consumed
                and _CLOCK_LITERAL.fullmatch(here.text)
                and after.index not in consumed
                and spec.clock_dirs.get(after.text, 0) > 0
                and count.index not in consumed and count.is_number
                and _minute_count(count, tokens[i + 3:i + 4], spec)):
            return True
    return False


def _minute_count(count, rest, spec):
    """Whether ``count`` ends the phrase or is followed by a minute unit,
    either as a word or as a letter written on the number."""
    if not rest:
        return True
    nxt = rest[0]
    glued = (count.char_end is not None and nxt.char_start is not None
             and count.char_end == nxt.char_start)
    return glued or spec.units.get(nxt.text) == "minute"


def _impossible_date_veto(tokens, consumed, text, engine, anchor):
    """Whether the winning reading strands an impossible day-of-month numeral
    ("the 32nd of February", "32 aprile"); a stranded valid date does not veto.
    ``_veto_active`` stops the fragment re-parse from re-entering this veto,
    which would otherwise recurse ``2**n`` times."""
    from chronologia.extract.timespan import extract_timespan
    if _veto_active.get():
        return False
    token = _veto_active.set(True)
    try:
        of_surfaces = set(engine.spec.connectors.get("of", ()))
        # A numeral+unit+"of" run right before ANY recognised match start, not only
        # the winner, is the same stranding one composition layer further out.
        veto_cb = lambda m: _candidate_veto(tokens, m, engine.spec)  # noqa: E731
        match_starts = {m.span[0] for m in engine.matcher.match(tokens, veto_cb)}
        for i in range(len(tokens) - 1):
            if not (tokens[i].index not in consumed and tokens[i].is_number):
                continue
            j = i + 1
            skipped_unit = False
            # Skip one unit/scope noun between the numeral and "of" ("the 0th WEEK of
            # may"). An ordinal that never bound is detected only here.
            if j < len(tokens) and _ordish_scope_word(tokens[j].text, engine.spec):
                j += 1
                skipped_unit = True
            if not (j < len(tokens) and tokens[j].index not in consumed
                    and tokens[j].text in of_surfaces):
                continue
            if j + 1 < len(tokens) and (tokens[j + 1].index in consumed
                                        or tokens[j + 1].index in match_starts):
                return True                              # qualifier abuts winner
            if skipped_unit:
                # The unresolved-fragment check does not apply after a skipped unit: its
                # scan can run across unrelated clauses and refuse a valid sentence.
                continue
            cs = tokens[i].char_start
            ce = None
            for t in tokens[i:]:
                if t.index in consumed or t.char_start is None:
                    break
                ce = t.char_end
            if cs is not None and ce is not None:
                frag = text[cs:ce]
                if extract_timespan(frag, engine.spec.lang, anchor) is None:
                    return True                          # impossible stranded date
        for i, t in enumerate(tokens):
            if t.index in consumed or not t.is_number or t.value is None \
                    or t.value != int(t.value) or t.value <= 31:
                continue
            # a number immediately followed by a unit word ("48 hours", "90
            # seconds") is a duration/count, not an attempted day-of-month --
            # its own trailing unit disambiguates it, so it never reaches the
            # "does this look like an impossible date" fallback below.
            if (i + 1 < len(tokens) and tokens[i + 1].index not in consumed
                    and tokens[i + 1].text in (set(engine.spec.units)
                                               | set(engine.spec.singular_units))):
                continue
            abuts = ((i > 0 and tokens[i - 1].index in consumed)
                     or (i + 1 < len(tokens) and tokens[i + 1].index in consumed))
            if abuts and extract_timespan(t.text, engine.spec.lang, anchor) is None:
                return True                              # impossible day-of-month
        return False
    finally:
        _veto_active.reset(token)


def _ordish_scope_word(text, spec):
    """Whether ``text`` is a singular unit or scope noun of the "Nth <unit> of
    <scope>" construction. A plural names a count, so it is excluded."""
    if text in spec.plural_units or text in ("weekends", "quarters"):
        return False
    return (text in spec.units or text in spec.scope_units
            or text in spec.weekend_words
            or text in spec.connectors.get("quarter_word", frozenset())
            or text in spec.weekdays)


def _is_scope_noun(text, spec):
    """Whether ``text`` is a scope noun that the ``SCOPE_UNIT`` slot accepts: a
    decade/century/millennium word or a calendar unit coarser than an hour."""
    if text in spec.scope_units:
        return True
    kind = spec.units.get(text)
    return kind is not None and kind not in ("hour", "minute", "second")


def _trailing_scope_veto(tokens, consumed, spec):
    """Whether the winning reading strands, right after the span, one unbound
    scope noun with an optional "of" and article ("os últimos dias do ano"):
    the unsupported "last <plural-unit> of <period>" compound."""
    if not consumed:
        return False
    last = max(consumed)
    trailing = [t for t in tokens if t.index > last and t.index not in consumed]
    # the trailing run must abut the winning span (no consumed gap): the scope
    # was trying to bind to the reading that just won.
    if not trailing or trailing[0].index != last + 1:
        return False
    of_surfaces = spec.connectors.get("of", frozenset())
    article_surfaces = spec.connectors.get("article", frozenset())
    i = 0
    while i < len(trailing) and (trailing[i].text in of_surfaces
                                 or trailing[i].text in article_surfaces):
        i += 1
    rest = trailing[i:]
    # exactly one residual scope noun, optionally introduced by a connector
    # ("do ano"/"do mês") or standing on its own genitive ("roku"/"miesiąca").
    return len(rest) == 1 and _is_scope_noun(rest[0].text, spec)


def _stranded_ordinal_scope_veto(tokens, consumed, spec):
    """Whether the winning reading strands a trailing ``of? article? ORD
    SCOPE_UNIT`` tail ("the weekend of the 5th month"). ``weekend_of_month``
    binds only a named month. Text after the two tokens is allowed."""
    if not consumed:
        return False
    last = max(consumed)
    trailing = [t for t in tokens if t.index > last and t.index not in consumed]
    if not trailing or trailing[0].index != last + 1:
        return False
    of_surfaces = spec.connectors.get("of", frozenset())
    article_surfaces = spec.connectors.get("article", frozenset())
    i = 0
    while i < len(trailing) and (trailing[i].text in of_surfaces
                                 or trailing[i].text in article_surfaces):
        i += 1
    rest = trailing[i:]
    return (len(rest) >= 2 and rest[0].is_number and (rest[0].value or 0) >= 1
            and _is_scope_noun(rest[1].text, spec))


def _stranded_compound_ordinal_veto(tokens, match, spec) -> bool:
    """Whether a century/millennium ``scoped_ordinal`` reading leaves an unconsumed
    token on either side of its ``ORD``/``SORD`` slot ("abad kedua puluh"): the
    fold read one piece of a multi-word spelled ordinal, so the century is wrong."""
    ord_tok = match.slots.get("ORD") or match.slots.get("SORD")
    scope_tok = match.slots.get("SCOPE_UNIT") or match.slots.get("CMUNIT")
    if ord_tok is None or scope_tok is None:
        return False
    if spec.scope_units.get(scope_tok.text) not in ("century", "millennium"):
        return False
    consumed_idx = set(range(*match.span))
    by_index = {t.index: t for t in tokens}
    for neighbor_idx in (ord_tok.index - 1, ord_tok.index + 1):
        neighbor = by_index.get(neighbor_idx)
        if neighbor is not None and neighbor_idx not in consumed_idx:
            return True
    return False


def _stranded_explicit_anchor_veto(tokens, consumed, text, spec, anchor):
    """Whether the winning reading strands a trailing ``from <date>`` that
    resolves on its own ("the next 2 quarters from 500 BC"). The ``rel_span``
    family has no order for an explicit anchor, so the span would be wrong."""
    from chronologia.extract.timespan import extract_timespan
    if not consumed:
        return False
    last = max(consumed)
    trailing = [t for t in tokens if t.index > last and t.index not in consumed]
    if not trailing or trailing[0].index != last + 1:
        return False
    of_surfaces = spec.connectors.get("of", frozenset())
    article_surfaces = spec.connectors.get("article", frozenset())
    from_surfaces = spec.connectors.get("from", frozenset())
    i = 0
    while i < len(trailing) and (trailing[i].text in of_surfaces
                                 or trailing[i].text in article_surfaces):
        i += 1
    if i >= len(trailing) or trailing[i].text not in from_surfaces:
        return False
    i += 1
    rest = trailing[i:]
    if not rest:
        return False
    cs, ce = rest[0].char_start, rest[-1].char_end
    if cs is None or ce is None:
        return False
    frag = text[cs:ce]
    return extract_timespan(frag, spec.lang, anchor) is not None


def _stranded_fraction_prefix_veto(tokens, consumed, spec):
    """Whether the winning reading strands a leading ``article? NUM FRACTION_WORD
    of?`` prefix ("first half of leap february 2028"). ``half_period`` and
    ``quarter_of_month`` need the month right after "of". Filler words after the
    prefix are allowed."""
    if not consumed:
        return False
    first = min(consumed)
    if first == 0:
        return False
    i = first - 1
    while i >= 0 and tokens[i].index not in consumed:
        i -= 1
    lead = [t for t in tokens[i + 1:first]]
    if not lead:
        return False
    article_surfaces = spec.connectors.get("article", frozenset())
    j = 0
    while j < len(lead) and lead[j].text in article_surfaces:
        j += 1
    if j >= len(lead) or not (lead[j].is_number and (lead[j].value or 0) >= 1):
        return False
    j += 1
    fraction_words = (set(spec.connectors.get("half", ()))
                      | set(spec.connectors.get("quarter_word", ())))
    if j >= len(lead) or lead[j].text not in fraction_words:
        return False
    j += 1
    # a trailing "of?" is optional -- some locales' month-fraction surface is
    # connector-less ("erste Hälfte Februar") -- but any presence of it here
    # is consumed as part of the recognised prefix, not counted as filler.
    of_surfaces = spec.connectors.get("of", frozenset())
    if j < len(lead) and lead[j].text in of_surfaces:
        j += 1
    return True


def _new_year_definite_article_veto(tokens, match, spec) -> bool:
    """True when a ``new_year_ref`` match with no ``YEARANY`` slot follows a
    definite article ("the new year"): that names the coming year, not
    1 January."""
    if match.construction != "new_year_ref":
        return False
    if "YEARANY" in match.slots:
        return False
    start = match.span[0]
    if start == 0:
        return False
    articles = spec.connectors.get("article", frozenset())
    return tokens[start - 1].text.lower() in articles


def _bare_be_trailing_veto(tokens, match, spec) -> bool:
    """True when a bare-"BE" Buddhist-Era match has tokens after it and no year
    word in it: "in 2020 be ready" holds the verb, and the era abbreviation is
    clause-final ("2560 BE")."""
    if match.construction != "era_buddhist_be":
        return False
    year_words = spec.connectors.get("year_word", frozenset())
    start, end = match.span
    if any(tok.text in year_words for tok in tokens[start:end]):
        return False
    return end < len(tokens)


def _stray_capitalized_be_veto(tokens, match, spec) -> bool:
    """True for a ``year_ref`` match followed by a capitalized "BE" (the ``cap``
    flag): the era reading was declined, so a plain year would be 543 years off.
    A lower-case verb "be" keeps the year."""
    if match.construction != "year_ref":
        return False
    end = match.span[1]
    return end < len(tokens) and tokens[end].text == "be" and tokens[end].cap


def _stray_capitalized_am_veto(tokens, match, spec) -> bool:
    """True for a ``SMALLYEAR`` ``year_ref`` match followed by a capitalized "AM"
    (Anno Mundi, "in the year 1 AM"). A ``GYEAR`` match and a lower-case
    meridiem "am" are not vetoed."""
    if match.construction != "year_ref" or "SMALLYEAR" not in match.slots:
        return False
    end = match.span[1]
    return end < len(tokens) and tokens[end].text == "am" and tokens[end].cap


def _stranded_year_veto(tokens, match, spec) -> bool:
    """True for a yearless 29 February followed by a year the match did not bind
    ("the 29th of February this year"): the leap-year roll would cross it. Only
    a four-digit year behind at most one glue word, or a rel-marked year word,
    right after the match counts."""
    if match.construction != "calendar_date":
        return False
    day = match.slots.get("DAY")
    month = match.slots.get("MONTH")
    if day is None or month is None or "YEAR" in match.slots:
        return False
    if (spec.months.get(month.text), int(day.value)) != (2, 29):
        return False
    tail = tokens[match.span[1]:match.span[1] + 3]
    for skipped, tok in enumerate(tail[:2]):
        if tok.is_number:
            return (skipped == 0 or not tail[0].is_number) \
                and len(tok.raw.strip(".")) == 4 and tok.raw.strip(".").isdigit()
    if len(tail) >= 2:
        first, second = tail[0].text, tail[1].text
        if (first in spec.rel_markers and spec.units.get(second) == "year") \
                or (spec.units.get(first) == "year"
                    and second in spec.rel_markers):
            return True
    return False


def _stray_year_zero_veto(tokens, match, spec) -> bool:
    """True for a ``relative_offset`` "year" match followed by a bare "0" ("in
    year 0"). ``SMALLYEAR`` refuses "0", so the "in a year" reading would strand
    it."""
    if match.construction != "relative_offset":
        return False
    unit = match.slots.get("UNIT")
    if unit is None or spec.units.get(unit.text) != "year":
        return False
    end = match.span[1]
    return (end < len(tokens) and tokens[end].is_number
            and tokens[end].raw.rstrip(".") == "0")


#: Month surfaces that are also the bare word for Christmas;
#: see :func:`_month_holiday_collision_veto`.
_MONTH_HOLIDAY_COLLISIONS = {
    "da": frozenset({"jul"}),
    "sv": frozenset({"jul"}),
    "nb": frozenset({"jul"}),
    "nn": frozenset({"jul"}),
}


def _month_holiday_collision_veto(tokens, match, spec) -> bool:
    """True for a bare one-token ``calendar_date`` month in
    :data:`_MONTH_HOLIDAY_COLLISIONS` (Scandinavian "jul") with no day or year.
    The equal-length ``holiday_ref`` reading (Christmas) then wins."""
    if match.construction != "calendar_date":
        return False
    if match.length != 1:
        return False
    if "DAY" in match.slots or "YEAR" in match.slots:
        return False
    collisions = _MONTH_HOLIDAY_COLLISIONS.get(spec.lang)
    if not collisions:
        return False
    return tokens[match.span[0]].text in collisions


def _relday_daypart_homograph_veto(tokens, match, spec) -> bool:
    """True for a ``daypart_ref`` match whose ``DAYPART`` is also a day word
    (es/gl "mañana") right after a "before"/"after" marker: "antes de mañana" is
    "before tomorrow", never "before the morning"."""
    if match.construction != "daypart_ref":
        return False
    dp_tok = match.slots.get("DAYPART")
    if dp_tok is None or dp_tok.text not in spec.named_days:
        return False
    b = match.span[0]
    if b == 0:
        return False
    dir_markers = (spec.connectors.get("before", frozenset())
                   | spec.connectors.get("after", frozenset())
                   | spec.connectors.get("offset_after", frozenset()))
    return tokens[b - 1].text in dir_markers


def _participle_season_veto(tokens, match, spec) -> bool:
    """True for a match that opens on a season word right after a form of the
    auxiliary in ``marker_participle_aux.voc`` (French "a été")."""
    start = match.span[0]
    if start == 0 or tokens[start].text not in spec.seasons:
        return False
    return tokens[start - 1].text in spec.connectors.get("participle_aux",
                                                         frozenset())


def _num_preamble_named_day_idiom_veto(tokens, match, spec) -> bool:
    """True for a ``named_day_after``/``named_day_before`` match right after a
    number ("two days after tomorrow"). The idiom is a fixed one-day shift with no
    ``NUM`` slot, so the numeral goes to the generic anchored-offset composition."""
    if match.construction not in ("named_day_after", "named_day_before"):
        return False
    b = match.span[0]
    if b == 0:
        return False
    return tokens[b - 1].is_number


def _subday_named_day_idiom_veto(match, spec) -> bool:
    """True for a ``named_day_span_idiom`` match with a sub-day unit ("an hour
    today"). Its resolver declines that unit, so the offset and the day are read
    as two references that :func:`_compose` joins."""
    if match.construction != "named_day_span_idiom":
        return False
    return spec.units.get(match.slots["UNIT"].text) in _SUBDAY_OFFSET_UNITS


def _skip_one_idiom_veto(tokens, match, spec) -> bool:
    """True for an "after next" / "before last" idiom whose marker modifies
    the word after it: in "the day after next summer" the idiom would read
    "the day after next" and strand "summer".  Without it, "next summer"
    reads as the reference and "the day after" as the offset."""
    return (match.construction in ("after_next", "before_last")
            and marker_names_a_reference(tokens, match.span[1] - 1, spec))


def _homograph_veto(tokens, match, spec) -> bool:
    """True for a match made only of ``marker_homograph.voc`` surfaces (pt
    "verão", sv "vår") with no time cue beside it: a connector before, a relative
    marker or daypart after, a ``marker_homograph_cue.voc`` word or a number on
    either side. A word that is the whole input keeps the date sense."""
    words = spec.connectors.get("homograph")
    if not words:
        return False
    b, e = match.span
    if e - b == len(tokens) or any(t.text not in words for t in tokens[b:e]):
        return False
    if b > 0:
        prev = tokens[b - 1]
        if prev.is_number or any(prev.text in v for k, v in spec.connectors.items()
                                 if k != "homograph"):
            return False
    if e < len(tokens):
        nxt = tokens[e]
        if (nxt.is_number or nxt.text in spec.rel_markers
                or nxt.text in spec.dayparts
                or nxt.text in spec.connectors.get("homograph_cue", ())):
            return False
    return True


def _candidate_veto(tokens, match, spec) -> bool:
    """Whether a context veto drops ``match`` before the overlap contest, so a
    shorter correct reading survives."""
    return (_new_year_definite_article_veto(tokens, match, spec)
            or _bare_be_trailing_veto(tokens, match, spec)
            or _stray_capitalized_be_veto(tokens, match, spec)
            or _stray_capitalized_am_veto(tokens, match, spec)
            or _stray_year_zero_veto(tokens, match, spec)
            or _month_holiday_collision_veto(tokens, match, spec)
            or _relday_daypart_homograph_veto(tokens, match, spec)
            or _participle_season_veto(tokens, match, spec)
            or _homograph_veto(tokens, match, spec)
            or _num_preamble_named_day_idiom_veto(tokens, match, spec)
            or _subday_named_day_idiom_veto(match, spec)
            or _stranded_year_veto(tokens, match, spec)
            or _skip_one_idiom_veto(tokens, match, spec))


#: sub-day offset units -- a ``relative_offset`` bound to one of these is
#: already a clock-level point ("2 saat əvvəl" == an hour-wide span, not a
#: day), so :func:`_compose` never treats it as a composable date; only a
#: day-or-coarser offset ("3 gün əvvəl") is a whole day a trailing clock can pin a minute on.
_SUBDAY_OFFSET_UNITS = frozenset({"second", "minute", "hour"})


def _indefinite_daypart_veto(tokens, consumed, text, spec) -> bool:
    """True for a season or daypart reading next to an indefinite marker from
    ``marker_indef_daypart.voc`` (Hindi "एक सुबह", one morning). It reads the
    written surface, because the number fold turns एक into 1."""
    indef = spec.connectors.get("indef_daypart")
    if not indef or not consumed:
        return False
    if not any(tokens[i].text in spec.seasons or tokens[i].text in spec.dayparts
               for i in consumed):
        return False
    n = len(tokens)
    for k in range(min(consumed), min(n, max(consumed) + 4)):
        t = tokens[k]
        if (t.char_start is not None
                and text[t.char_start:t.char_end] in indef
                and any(tokens[j].text in spec.dayparts
                        for j in range(k + 1, min(n, k + 3)))):
            return True
    return False


def _core_veto(tokens, consumed, rep, engine, anchor, text):
    """Whether the composed winner strands a tail that shows it is the wrong
    reading of an unsupported compound."""
    if text is not None and _indefinite_daypart_veto(tokens, consumed, text,
                                                     engine.spec):
        return True
    # An unbound "of? <SCOPE_UNIT>" tail after a bare relative period (see
    # _trailing_scope_veto).
    if (rep.construction == "rel_period"
            and _trailing_scope_veto(tokens, consumed, engine.spec)):
        return True
    # A bare weekend reading ("weekend"/"the last N weekends") that strands an
    # unbound "of the Nth month" scope tail is the unsupported ordinal-month
    # weekend compound (see _stranded_ordinal_scope_veto) -- refuse rather
    # than surface the anchor-relative weekend with the scope phrase dropped.
    if (rep.construction in ("weekend_ref", "rel_span_weekend")
            and _stranded_ordinal_scope_veto(tokens, consumed, engine.spec)):
        return True
    # An unbound "from <date>" tail after a present-anchored span (see
    # _stranded_explicit_anchor_veto).
    if (text is not None
            and rep.construction in ("rel_span", "rel_period", "rel_span_quarter")
            and _stranded_explicit_anchor_veto(tokens, consumed, text,
                                               engine.spec, anchor)):
        return True
    # An unbound leading "ORD half/quarter of?" prefix before a bare month (see
    # _stranded_fraction_prefix_veto).
    if (rep.construction == "calendar_date"
            and _stranded_fraction_prefix_veto(tokens, consumed, engine.spec)):
        return True
    # A token beside the ORD slot of a century/millennium ordinal (see
    # _stranded_compound_ordinal_veto).
    if (rep.construction == "scoped_ordinal"
            and _stranded_compound_ordinal_veto(tokens, rep, engine.spec)):
        return True
    return False
