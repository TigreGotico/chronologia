# -*- coding: utf-8 -*-
"""Recurrence in Portuguese: ``extract_recurrence(text, "pt")`` -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "pt"

_CASES = [
    ("cada sexta-feira", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("cada segunda-feira", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("cada dia", "FREQ=DAILY", ""),
    ("cada mês", "FREQ=MONTHLY", ""),
    ("cada ano", "FREQ=YEARLY", ""),
    ("cada duas semanas", "FREQ=WEEKLY;INTERVAL=2", ""),
    ("semanalmente", "FREQ=WEEKLY", ""),
    ("mensalmente", "FREQ=MONTHLY", ""),
    ("anualmente", "FREQ=YEARLY", ""),
    ("diariamente", "FREQ=DAILY", ""),
    ("a primeira segunda-feira de cada mês", "FREQ=MONTHLY;BYDAY=1MO", ""),
    # Elliptical nth-weekday: the "do mês" tail is dropped in speech, exactly
    # as English drops "of the month".  The reading is engine-side and
    # language-agnostic -- it needs no pt vocabulary beyond the "último"
    # relative marker and the ordinal fold the locale already ships.
    ("toda última sexta-feira", "FREQ=MONTHLY;BYDAY=-1FR", ""),
    ("toda última sexta-feira do mês", "FREQ=MONTHLY;BYDAY=-1FR", ""),
    ("cada última sexta-feira", "FREQ=MONTHLY;BYDAY=-1FR", ""),
    ("toda última segunda-feira", "FREQ=MONTHLY;BYDAY=-1MO", ""),
    ("toda primeira segunda-feira", "FREQ=MONTHLY;BYDAY=1MO", ""),
    ("cada primeira sexta-feira", "FREQ=MONTHLY;BYDAY=1FR", ""),
    # as in English, an ordinal of two or upwards leaves the two readings
    # competing, so the month-of reading waits for the explicit tail.
    ("toda terceira quinta-feira do mês", "FREQ=MONTHLY;BYDAY=3TH", ""),
]


# adversarial: without the "todo/toda/cada" framing these are single past
# dates, not rules -- "última sexta-feira" is the friday just gone.
@pytest.mark.parametrize("text", [
    "última sexta-feira", "a última sexta-feira", "primeira sexta-feira",
])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None


# a cardinal before a unit stays an INTERVAL, never a day-of-month.
def test_cardinal_plus_unit_stays_an_interval():
    got = extract_recurrence("cada duas semanas", LANG)
    assert got is not None
    assert got[0].to_string() == "FREQ=WEEKLY;INTERVAL=2"


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ["sexta-feira", "a segunda-feira"])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None


# Date-anchored recurrence + clock pin (BYHOUR/BYMINUTE) + fixed-holiday rule.
_ANCHORED_CASES = [
    ("todo 10 de maio", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10", ""),
    ("todos os anos em 10 de maio", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10", ""),
    ("todo 25 de dezembro", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25", ""),
    ("todos os meses no dia 10", "FREQ=MONTHLY;BYMONTHDAY=10", ""),
    ("todos os dias às 9", "FREQ=DAILY;BYHOUR=9", ""),
    ("diariamente às 9", "FREQ=DAILY;BYHOUR=9", ""),
    ("toda quarta às 9:30", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9;BYMINUTE=30", ""),
    ("todo domingo às 9", "FREQ=WEEKLY;BYDAY=SU;BYHOUR=9", ""),
    ("toda quinta-feira às 15", "FREQ=WEEKLY;BYDAY=TH;BYHOUR=15", ""),
    ("todos os dias ao meio-dia", "FREQ=DAILY;BYHOUR=12", ""),
    ("todo dia à meia-noite", "FREQ=DAILY;BYHOUR=0", ""),
    ("todo natal", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _ANCHORED_CASES)
def test_anchored_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


from chronologia.recurrence import HolidayRecurrence   # noqa: E402


@pytest.mark.parametrize("text,key", [
    ("toda páscoa", "easter"),
    ("toda sexta-feira santa", "good_friday"),
])
def test_movable_holiday_recurrence(text, key):
    got = extract_recurrence(text, LANG)
    assert got is not None
    assert got[0] == HolidayRecurrence(key)
    assert got[1] == ""
    with pytest.raises(ValueError):
        got[0].to_string()


# --------------------------------------------------------------------------
# "uma vez ..." framing and the plural day-of-month form.
#
# Every surface below was confirmed natural by a native European Portuguese
# speaker; nothing here is a translation-by-analogy of the English forms.
# --------------------------------------------------------------------------
_ONCE_CASES = [
    # "uma vez por <unidade>" -- one occurrence per period *is* that period's
    # plain frequency, so the count word adds no RRULE part of its own.
    ("uma vez por dia", "FREQ=DAILY", ""),
    ("uma vez por semana", "FREQ=WEEKLY", ""),
    ("uma vez por mês", "FREQ=MONTHLY", ""),
    ("uma vez por ano", "FREQ=YEARLY", ""),
    # European Portuguese also contracts the preposition with the article:
    # "à semana", "ao mês".
    ("uma vez à semana", "FREQ=WEEKLY", ""),
    ("uma vez ao mês", "FREQ=MONTHLY", ""),
    ("uma vez ao dia", "FREQ=DAILY", ""),
    ("uma vez ao ano", "FREQ=YEARLY", ""),
    # a weekday pins the day, exactly as English "once a week on monday".
    ("uma vez por semana à segunda", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("uma vez por semana à segunda-feira", "FREQ=WEEKLY;BYDAY=MO", ""),
    # ... and the clock pin still folds on top of it.
    ("uma vez por semana à segunda às 9", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
]


_DAY_OF_MONTH_CASES = [
    # The plural is what a speaker uses here: the rule is not about one
    # specific day, so "todos os dias 1" reads as "the 1st of every month".
    ("todos os dias 1", "FREQ=MONTHLY;BYMONTHDAY=1", ""),
    ("todos os dias 15", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    ("todos os dias 1 do mês", "FREQ=MONTHLY;BYMONTHDAY=1", ""),
    ("todos os dias 15 do mês", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    ("no dia 1 de cada mês", "FREQ=MONTHLY;BYMONTHDAY=1", ""),
    ("no dia 15 de cada mês", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
]


@pytest.mark.parametrize("text,rrule,remainder",
                         _ONCE_CASES + _DAY_OF_MONTH_CASES)
def test_once_and_day_of_month(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


def test_todos_os_dias_still_means_daily():
    """The collision guard: "todos os dias" on its own is DAILY.

    Only a *trailing day number* diverts it to a day-of-month rule, so the
    bare phrase must keep the reading it has always had."""
    got = extract_recurrence("todos os dias", LANG)
    assert got is not None
    assert got[0].to_string() == "FREQ=DAILY"
    assert got[1] == ""


def test_singular_day_number_is_not_a_day_of_month_rule():
    """"todo dia 1" is not the natural surface for this sense (a native
    speaker uses the plural), so the day number is *not* read as a
    BYMONTHDAY: the phrase keeps its plain DAILY reading and the stray
    number is left in the remainder."""
    got = extract_recurrence("todo dia 1", LANG)
    assert got is not None
    assert got[0].to_string() == "FREQ=DAILY"
    assert got[1] == "1"


@pytest.mark.parametrize("text", [
    # a per-period *count* above one needs a different RRULE shape
    # (BYSETPOS / per-period COUNT) than the plain frequency, so it is left
    # unread rather than forced into a wrong interval.
    "duas vezes por semana",
    "três vezes por mês",
    # the count phrase alone names no period at all
    "uma vez",
    "uma vez por",
    # a bare day number is a date, not a rule
    "dia 1",
    "no dia 1",
])
def test_once_adversarial_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None


# --------------------------------------------------------------------------
# Plural nth-weekday: the canonical pt surface for a recurring set.
#
# Native-speaker ruling from the repo owner: Portuguese marks the recurring
# set with the PLURAL throughout -- plural article, plural ordinal, plural
# weekday, plus the "do mês" tail.  The singular names one particular
# occasion.  This is the same correction the owner applied to "todo dia 1".
#
# It also composes cleanly with the conservative rule from #217: the natural
# pt form already carries the explicit "do mês" tail, so the ordinal-vs-
# interval ambiguity that forced English to wait for positive evidence simply
# does not arise here -- every ordinal from two upwards is already unambiguous.
# --------------------------------------------------------------------------
_PLURAL_NTH_WEEKDAY_CASES = [
    ("todas as terceiras quintas-feiras do mês", "FREQ=MONTHLY;BYDAY=3TH"),
    ("todas as primeiras segundas-feiras do mês", "FREQ=MONTHLY;BYDAY=1MO"),
    ("todas as últimas sextas-feiras do mês", "FREQ=MONTHLY;BYDAY=-1FR"),
    ("todas as últimas quartas-feiras do mês", "FREQ=MONTHLY;BYDAY=-1WE"),
    ("todas as primeiras sextas-feiras do mês", "FREQ=MONTHLY;BYDAY=1FR"),
    ("todas as terceiras terças-feiras do mês", "FREQ=MONTHLY;BYDAY=3TU"),
    ("todas as terceiras quartas-feiras do mês", "FREQ=MONTHLY;BYDAY=3WE"),
    ("todas as primeiras terças-feiras do mês", "FREQ=MONTHLY;BYDAY=1TU"),
    ("todas as últimas segundas-feiras do mês", "FREQ=MONTHLY;BYDAY=-1MO"),
]


@pytest.mark.parametrize("text,rrule", _PLURAL_NTH_WEEKDAY_CASES)
def test_plural_nth_weekday(text, rrule):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == ""


# --------------------------------------------------------------------------
# The same plural nth-weekday frame for "sábado"/"domingo", which are not
# "-feira" compounds and so have no plural surface in the weekday vocabulary.
#
# The plural is licensed POSITIONALLY, not globally: it is read only when an
# "every" determiner ("todos os") plus an ordinal or a "último" marker sits
# directly before it.  A surname cannot occupy that slot, so "domingos" the
# name is untouched -- see the guards below.
#
# European Portuguese takes the article throughout ("todos os ..."); the
# article-less Brazilian forms remain accepted input but are not canonical.
# Source: Ciberduvidas, «Todo dia e todos os dias» --
# https://ciberduvidas.iscte-iul.pt/consultorio/perguntas/todo-dia-e-todos-os-dias/23627
# --------------------------------------------------------------------------
_NON_FEIRA_PLURAL_CASES = [
    ("todos os últimos domingos do mês", "FREQ=MONTHLY;BYDAY=-1SU"),
    ("todos os primeiros sábados do mês", "FREQ=MONTHLY;BYDAY=1SA"),
    ("todos os últimos sábados do mês", "FREQ=MONTHLY;BYDAY=-1SA"),
    ("todos os primeiros domingos do mês", "FREQ=MONTHLY;BYDAY=1SU"),
    ("todos os terceiros domingos do mês", "FREQ=MONTHLY;BYDAY=3SU"),
    ("todos os terceiros sábados do mês", "FREQ=MONTHLY;BYDAY=3SA"),
    # "first"/"last" need no tail (the #217 rule), exactly as the -feira days
    ("todos os últimos domingos", "FREQ=MONTHLY;BYDAY=-1SU"),
    ("todos os primeiros sábados", "FREQ=MONTHLY;BYDAY=1SA"),
    ("cada último domingo", "FREQ=MONTHLY;BYDAY=-1SU"),
    # the dropped "-feira" plural in the same frame
    ("todas as últimas segundas do mês", "FREQ=MONTHLY;BYDAY=-1MO"),
]


@pytest.mark.parametrize("text,rrule", _NON_FEIRA_PLURAL_CASES)
def test_non_feira_plural_nth_weekday(text, rrule):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == ""


@pytest.mark.parametrize("text", [
    # #217's rule is engine-wide and is NOT weakened here: from two upwards
    # the bare (tail-less) ordinal stays ambiguous and is left unread.
    "todos os terceiros domingos", "todos os terceiros sábados",
    # without the "every" determiner the plural is not licensed at all
    "os últimos domingos do mês", "últimos domingos do mês",
    "primeiros sábados do mês",
    # bare plurals: "Domingos" is a common pt surname / given name
    "domingos", "sábados", "o senhor domingos chegou",
    # and the ordinal-count corpus is untouched
    "3 sextas",
])
def test_plural_weekday_licensing_guards(text):
    assert extract_recurrence(text, LANG) is None


def test_plural_weekday_is_never_folded_to_a_number():
    """"segundas"/"quintas" are weekday names in the plural exactly as they
    are in the singular, so the plural-ordinal fold must not eat them."""
    got = extract_recurrence("todas as segundas-feiras", LANG)
    assert got is not None
    assert got[0].to_string() == "FREQ=WEEKLY;BYDAY=MO"


@pytest.mark.parametrize("text", [
    # plural ordinals are folded, but the surfaces that are ordinary nouns
    # this engine reads ("segundos" seconds, "quartos" the clock quarter)
    # are held back and so name no recurrence on their own.
    "segundos", "dois quartos",
    # the ordinals that ARE weekday names ("segundas" 2nd/Mondays, "quartas"
    # 4th/Wednesdays, "quintas" 5th/Thursdays) stay weekdays, so the plural
    # nth-weekday reading is not available for those counts -- the phrase
    # reads as the weekday it names rather than being guessed either way.
    "todas as quintas quintas-feiras do mês",
])
def test_plural_ordinal_noun_homographs_are_not_recurrences(text):
    got = extract_recurrence(text, LANG)
    assert got is None or got[1] != ""


# --------------------------------------------------------------------------
# The European Portuguese habitual weekday, marked by the PREPOSITION.
#
# Source: Ciberdúvidas da Língua Portuguesa, «À(s) segunda(s)-feira(s)»,
# Eunice Marta, 1 June 2012 --
# https://ciberduvidas.iscte-iul.pt/consultorio/perguntas/as-segundas-feiras/31385
#
# Asked which of «"As segundas-feiras faço ginástica" ou "a segunda-feira faço
# ginástica"» expresses "all Mondays", the consultant answers that BOTH the
# singular and the plural convey it -- «À segunda-feira faço ginástica», «Às
# segundas-feiras faço ginástica» -- and that the construction requires the
# preposition: the bare article does not give the habitual reading.  This is
# the ordinary EP way to say "every monday", so it must parse as one.
# --------------------------------------------------------------------------
_HABITUAL_CASES = [
    # -feira compounds, singular then plural
    ("à segunda-feira", "FREQ=WEEKLY;BYDAY=MO"),
    ("às segundas-feiras", "FREQ=WEEKLY;BYDAY=MO"),
    ("à terça-feira", "FREQ=WEEKLY;BYDAY=TU"),
    ("às terças-feiras", "FREQ=WEEKLY;BYDAY=TU"),
    ("à quarta-feira", "FREQ=WEEKLY;BYDAY=WE"),
    ("às quartas-feiras", "FREQ=WEEKLY;BYDAY=WE"),
    ("à quinta-feira", "FREQ=WEEKLY;BYDAY=TH"),
    ("às quintas-feiras", "FREQ=WEEKLY;BYDAY=TH"),
    ("à sexta-feira", "FREQ=WEEKLY;BYDAY=FR"),
    ("às sextas-feiras", "FREQ=WEEKLY;BYDAY=FR"),
    # sábado / domingo are not -feira days and take the masculine ao/aos
    ("ao sábado", "FREQ=WEEKLY;BYDAY=SA"),
    ("aos sábados", "FREQ=WEEKLY;BYDAY=SA"),
    ("ao domingo", "FREQ=WEEKLY;BYDAY=SU"),
    ("aos domingos", "FREQ=WEEKLY;BYDAY=SU"),
    # the -feira noun is routinely dropped in speech
    ("à segunda", "FREQ=WEEKLY;BYDAY=MO"),
    ("às segundas", "FREQ=WEEKLY;BYDAY=MO"),
    ("às sextas", "FREQ=WEEKLY;BYDAY=FR"),
]


@pytest.mark.parametrize("text,rrule", _HABITUAL_CASES)
def test_habitual_weekday(text, rrule):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == ""


@pytest.mark.parametrize("text", [
    # "em + article" is a single date -- "na segunda-feira" is *on Monday*,
    # the monday coming, not a rule.  The a-vs-em contrast is exactly the
    # distinction the Ciberduvidas answer draws, so the two prepositions live
    # in separate vocabularies and this reading is structurally unreachable.
    "na segunda-feira", "no domingo", "no sábado", "nas segundas-feiras",
    # a bare article carries no habitual sense either (per the same source)
    "a segunda-feira",
])
def test_em_preposition_is_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None


def test_habitual_preposition_does_not_swallow_the_clock():
    """"às" is also the clock marker ("às 9" = at nine).  The habitual rule
    fires only before a WEEKDAY, so one sentence can carry both uses."""
    got = extract_recurrence("às segundas-feiras às 9", LANG)
    assert got is not None
    assert got[0].to_string() == "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9"
    assert got[1] == ""
    # a lone clock time is no recurrence at all
    assert extract_recurrence("às 9", LANG) is None


def test_bare_plural_weekday_is_still_a_surname():
    """The plural weekday surface is accepted ONLY under the habitual
    preposition, so "domingos" on its own stays the surname it also is."""
    assert extract_recurrence("o senhor domingos chegou", LANG) is None
    assert extract_recurrence("domingos", LANG) is None


# --------------------------------------------------------------------------
# "cada/todos os feriados em/de <jurisdição>" -- a whole calendar's holiday
# set, R108.  No RFC 5545 rule either -- to_string() refuses the same way
# HolidayRecurrence above does.
# --------------------------------------------------------------------------
from chronologia.recurrence import JurisdictionHolidays   # noqa: E402


@pytest.mark.parametrize("text,jurisdiction", [
    ("todos os feriados em Portugal", "PT"),
    ("cada feriado de Portugal", "PT"),
    ("todos os feriados em Espanha", "ES"),
    ("cada feriado da França", "FR"),
    ("todos os feriados na Alemanha", "DE"),
    ("cada feriado do Brasil", "BR"),
])
def test_jurisdiction_holidays_recurrence(text, jurisdiction):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0] == JurisdictionHolidays(jurisdiction)
    assert got[1] == ""
    with pytest.raises(ValueError):
        got[0].to_string()


def test_jurisdiction_holidays_unknown_country_declines():
    assert extract_recurrence("todos os feriados na Atlântida", LANG) is None


def test_bare_todos_os_feriados_is_unchanged():
    """Pinning the pre-R108 behaviour of the bare phrase (no jurisdiction)."""
    assert extract_recurrence("todos os feriados", LANG) is None


# --------------------------------------------------------------------------
# R111a: "todos os feriados em Portugal E Espanha" -- a second recognised
# jurisdiction joined by the natural pt connector "e" names more than one
# jurisdiction; refuse rather than silently keep only the first (Spain
# dropped).
# --------------------------------------------------------------------------
@pytest.mark.parametrize("text", [
    "todos os feriados em Portugal e Espanha",
    "cada feriado da França e da Alemanha",
])
def test_jurisdiction_holidays_multi_country_declines(text):
    assert extract_recurrence(text, LANG) is None


# --------------------------------------------------------------------------
# R111b: a trailing whole-year scope binds as UNTIL rather than stranding.
# Anchored at 2026-08-11 so "no próximo ano" is unambiguously 2027.
# --------------------------------------------------------------------------
from datetime import datetime as _datetime  # noqa: E402

_ANCHOR = _datetime(2026, 8, 11, 12, 0)


def test_every_monday_next_year_binds_until_pt():
    got = extract_recurrence(
        "toda segunda-feira próximo ano", LANG, anchor=_ANCHOR)
    assert got is not None
    rec, remainder = got
    assert remainder == ""
    assert rec.until.year == 2028 and rec.until.month == 1 and rec.until.day == 1


def test_every_holiday_in_portugal_next_year_declines_pt():
    """JurisdictionHolidays has no bound field to attach a year scope to;
    refuse outright, mirroring the English test."""
    got = extract_recurrence(
        "todos os feriados em Portugal próximo ano", LANG, anchor=_ANCHOR)
    assert got is None
