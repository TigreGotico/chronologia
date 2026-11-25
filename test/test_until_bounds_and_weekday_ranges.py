"""An "until" bound keeps its value and a weekday range keeps its weekday set.

Expected values are the readings of the current tree, each checked by hand
against the anchor 2026-11-22 (a Sunday): "until december" is 2026-12-01,
"until june" 2027-06-01, "until 2030" 2030-01-01, "until friday" 2026-11-27,
"5 de agosto" 2027-08-05 and "until before christmas" 2026-12-25.  Rows marked
xfail pin the value an open issue asks for.
"""
from datetime import datetime

import pytest

from chronologia import extract_recurrence

ANCHOR = datetime(2026, 11, 22, 9, 0)
ISSUE_1291 = pytest.mark.xfail(
    strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1291")

WEEKDAYS = "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR"
DECEMBER = "FREQ=DAILY;UNTIL=20261201T000000"
YEAR_PAIR = "FREQ=WEEKLY;UNTIL=20300101T000000;BYDAY=MO"


def read(lang, text):
    got = extract_recurrence(text, lang, ANCHOR)
    return str(got.recurrence), got.remainder


@pytest.mark.parametrize("lang, text, rule, remainder", [
    # "from A to B until C": C is a third month and keeps its value
    ("en", "every day from june to august until december", DECEMBER, "from june to august"),
    ("pt", "todos os dias de junho a agosto até dezembro", DECEMBER, "de junho a agosto"),
    ("es", "cada día de junio a agosto hasta diciembre", DECEMBER, "de junio a agosto"),
    ("fr", "chaque jour de juin à août jusqu'à décembre", DECEMBER, "de juin à août"),
    ("it", "ogni giorno da giugno a agosto fino a dicembre", DECEMBER, "da giugno a agosto"),
    ("ca", "cada dia de juny a agost fins a desembre", DECEMBER, "de juny a agost"),
    ("gl", "cada día de xuño a agosto ata decembro", DECEMBER, "de xuño a agosto"),
    # a year pair
    ("en", "every monday from 2027 until 2030", YEAR_PAIR, ""),
    ("de", "jeden Montag von 2027 bis 2030", YEAR_PAIR, ""),
    ("pt", "todas as segundas de 2027 até 2030", YEAR_PAIR, ""),
    ("es", "cada lunes de 2027 hasta 2030", YEAR_PAIR, ""),
    ("fr", "chaque lundi de 2027 jusqu'à 2030", YEAR_PAIR, ""),
    ("nl", "elke maandag van 2027 tot 2030", YEAR_PAIR, ""),
    ("it", "ogni lunedì da 2027 fino a 2030", YEAR_PAIR, ""),
    ("ca", "cada dilluns de 2027 fins a 2030", YEAR_PAIR, ""),
    ("gl", "cada luns de 2027 ata 2030", YEAR_PAIR, ""),
    # a date range with an inner "de"
    ("pt", "todas as segundas de 3 de junho até 5 de agosto",
     "FREQ=WEEKLY;UNTIL=20270805T000000;BYDAY=MO", ""),
    ("es", "cada lunes del 3 de junio hasta el 5 de agosto",
     "FREQ=WEEKLY;UNTIL=20270805T000000;BYDAY=MO", ""),
    # an until word before a holiday, and a plain until bound
    ("en", "every day from monday until before christmas",
     "FREQ=DAILY;UNTIL=20261225T000000", "from monday"),
    ("de", "jeden Montag bis August", "FREQ=WEEKLY;UNTIL=20270801T000000;BYDAY=MO", ""),
    ("en", "every friday until june", "FREQ=WEEKLY;UNTIL=20270601T000000;BYDAY=FR", ""),
    ("nl", "elke dag van maandag tot en met vrijdag", WEEKDAYS, ""),
])
def test_an_until_bound_keeps_its_value(lang, text, rule, remainder):
    assert read(lang, text) == (rule, remainder)


@pytest.mark.parametrize("lang, text, rule", [
    ("de", "jeden Tag von Mo bis Fr", WEEKDAYS),
    ("de", "jeden Tag von Mo. bis Fr.", WEEKDAYS),
    ("de", "jeden Werktag von Mo bis Mi", "FREQ=WEEKLY;BYDAY=MO,TU,WE"),
    ("nl", "elke dag van ma tot vr", WEEKDAYS),
    ("nl", "elke dag van ma t/m vr", WEEKDAYS),
    ("pt", "todos os dias de seg até sex", WEEKDAYS),
    ("pt", "todos os dias de seg a sex", WEEKDAYS),
    ("es", "todos los días de lun hasta vie", WEEKDAYS),
    ("es", "todos los días de lun a vie", WEEKDAYS),
    ("fr", "tous les jours du lun jusqu'au ven", WEEKDAYS),
    ("fr", "tous les jours de lun à ven", WEEKDAYS),
    ("it", "ogni giorno da lun fino a ven", WEEKDAYS),
    ("it", "ogni giorno da lun a ven", WEEKDAYS),
    ("ca", "cada dia de dl fins a dv", WEEKDAYS),
    ("ca", "cada dia de dl a dv", WEEKDAYS),
    ("gl", "cada día de lun ata ven", WEEKDAYS),
    ("gl", "cada día de lun a ven", WEEKDAYS),
    ("en", "every day from mon until fri", WEEKDAYS),
    ("en", "every day from mon to fri", WEEKDAYS),
    ("en", "every day from monday to friday", WEEKDAYS),
])
def test_an_abbreviated_weekday_range_keeps_its_weekday_set(lang, text, rule):
    assert read(lang, text) == (rule, "")


# "every day from monday until friday" is a weekday set, as with "to".
def test_an_until_word_between_two_weekdays_gives_a_weekday_set():
    assert read("en", "every day from monday until friday") == (WEEKDAYS, "")


# A weekday rule from one month until another consumes both bounds, and its
# UNTIL ends with August, as extract_timespan reads "from june to august".  The
# tree leaves "from june" in the remainder and stops UNTIL at 1 August.
@ISSUE_1291
@pytest.mark.parametrize("lang, text", [
    ("de", "jeden Montag von Juni bis August"),
    ("en", "every monday from june until august"),
    ("nl", "elke maandag van juni tot augustus"),
    ("pt", "toda segunda-feira de junho até agosto"),
    ("es", "cada lunes de junio hasta agosto"),
    ("fr", "chaque lundi de juin jusqu'à août"),
    ("it", "ogni lunedì da giugno fino a agosto"),
    ("ca", "cada dilluns de juny fins a agost"),
    ("gl", "cada luns de xuño ata agosto"),
])
def test_a_month_range_with_an_until_word_runs_to_the_end_of_the_range(lang, text):
    assert read(lang, text) == ("FREQ=WEEKLY;UNTIL=20270901T000000;BYDAY=MO", "")


# An until word after a range keeps its own date, as en "every day from june
# to august until december" reads.
@pytest.mark.parametrize("lang, text, remainder", [
    ("de", "jeden Tag von Juni bis August bis Dezember", "von Juni bis August"),
    ("nl", "elke dag van juni tot augustus tot december", "van juni tot augustus"),
])
def test_an_until_word_after_a_range_keeps_its_date(lang, text, remainder):
    assert read(lang, text) == (DECEMBER, remainder)
