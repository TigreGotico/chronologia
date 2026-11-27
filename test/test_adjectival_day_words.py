"""An adjective made from a day word names that day: de "die gestrige Besprechung".

The adjective forms are surfaces in each language's ``named_day_<off>.voc``,
with the source in the comment above them (Wiktionary declension tables).
The expected day is the anchor, Tuesday 2017-06-27, plus the day offset.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

ROWS = [
    ("de", "Die gestrige Besprechung hat lange gedauert.", -1),
    ("de", "Bei der gestrigen Probe war der Chor gut.", -1),
    ("de", "Für das heutige Abendessen kaufe ich Spargel.", 0),
    ("de", "Hast du die Unterlagen für das morgige Treffen?", 1),
    ("ru", "Вчерашний дождь размыл дорогу.", -1),
    ("ru", "Мы спорим со вчерашнего вечера.", -1),
    ("ru", "Купи хлеба к сегодняшнему ужину.", 0),
    ("ru", "Завтрашняя прогулка может закончиться под дождём.", 1),
    ("cs", "Na včerejší schůzi jsme se dohodli.", -1),
    ("cs", "Dnešní schůzka se protáhla.", 0),
    ("cs", "Zítřejší výlet raději odložíme.", 1),
    ("fi", "Eilinen sadekuuro yllätti meidät.", -1),
    ("fi", "Eilisen kokouksen pöytäkirja on valmis.", -1),
    ("fi", "Tämänpäiväinen kokous siirrettiin.", 0),
    ("fi", "Huomiseksi on luvattu ukkoskuuroja.", 1),
    ("hu", "A tegnapi vihar után sáros a kert.", -1),
    ("hu", "A mai edzés után elfáradtam.", 0),
    ("hu", "A holnapi értekezletre hozd a jegyzeteket.", 1),
    ("tr", "Dünkü toplantıda karar verilmedi.", -1),
    ("tr", "Bugünkü toplantıda herkes konuştu.", 0),
    ("tr", "Yarınki konser için bilet aldık.", 1),
]


@pytest.mark.parametrize("lang,text,offset", ROWS)
def test_an_adjectival_day_word_names_the_day(lang, text, offset):
    found = extract_timespan(text, lang, ANCHOR)
    assert found is not None
    assert found.span.start.datetime() == datetime(2017, 6, 27) + timedelta(days=offset)


NO_DATE = [
    ("de", "Die Gestrigkeit seiner Ansichten stört mich."),
    ("hu", "Majdnem elkéstem a vonatról."),
    ("tr", "Dünya kupası finali heyecanlıydı."),
    ("fi", "Eilispäivän muisto on hämärä."),
]


@pytest.mark.parametrize("lang,text", NO_DATE)
def test_a_word_that_only_starts_like_a_day_adjective_gives_no_date(lang, text):
    assert extract_timespan(text, lang, ANCHOR) is None

