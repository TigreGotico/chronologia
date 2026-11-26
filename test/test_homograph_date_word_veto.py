# -*- coding: utf-8 -*-
"""A date word that is a homograph of a more frequent word names no time alone.

pt "verão" is also "they will see", sv/nb/nn "vår" is also "our", ro "mai" is
also "more".  Each language lists these words in ``marker_homograph.voc``,
with the dictionary source in the file header.  A preposition, a
demonstrative, an article, a number or a year beside the word keeps the date
sense.

Anchor: Tuesday 2026-03-10 13:00.  A season or a month names its current or
next occurrence (ruling C of ``docs/rulings.md``): summer is 1 June to
1 September, autumn 1 September to 1 December, spring 1 March to 1 June.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2026, 3, 10, 13)

NO_DATE = [
    ("pt-PT", "Os vizinhos verão que a horta ficou linda."),
    ("pt-BR", "Quando provarem o bolo, as crianças verão que a receita é boa."),
    ("pt-BR", "Eles verão o filme."),
    ("sv", "Har du träffat vår nya granne som flyttade in i huset bredvid?"),
    ("nb", "Vår nabo har malt gjerdet sitt knallgrønt."),
    ("nn", "Vår nabo har måla gjerdet sitt knallgrønt, og no lurer heile gata på kvifor."),
    ("uk", "Сусідський пес такий лютий, що листоноша обходить наше подвір'я."),
    ("uk", "Він глянув на мене лютим поглядом."),
    ("hu", "Nagyapám ősz szakállát gondosan fésülgeti a tükör előtt."),
    ("fa", "کارمند بانک مهر شرکت را پای برگه زد."),
    ("fa", "شکارچی تیر را در کمان گذاشت."),
    ("ro", "Vecinul meu mai are o bicicletă ruginită în pivniță."),
    ("ro", "Vara mea Ioana a deschis o mică brutărie lângă gară."),
    ("ro", "Mai e timp."),
    ("sq", "Gjyshi im bën verë të kuqe shumë të shijshme."),
]

DATED = [
    ("pt-PT", "vamos à praia no verão", datetime(2026, 6, 1)),
    ("pt-PT", "este verão vamos à praia", datetime(2026, 6, 1)),
    ("pt-PT", "o verão de 2027", datetime(2027, 6, 1)),
    ("pt-BR", "o verão chegou", datetime(2026, 6, 1)),
    ("sv", "vi reser i vår", datetime(2026, 3, 1)),
    ("nb", "vi reiser i vår", datetime(2026, 3, 1)),
    ("ro", "plecăm în mai", datetime(2026, 5, 1)),
    ("ro", "plecăm pe 1 mai", datetime(2026, 5, 1)),
    ("ro", "vara aceasta plecăm la mare", datetime(2026, 6, 1)),
    ("hu", "az ősz szép volt", datetime(2026, 9, 1)),
    ("hu", "ősz van", datetime(2026, 9, 1)),
    ("hu", "ősz jön", datetime(2026, 9, 1)),
    ("uk", "лютий був холодним", datetime(2027, 2, 1)),
    ("ro", "vara asta mergem la mare", datetime(2026, 6, 1)),
    ("ro", "mergem la mare vara asta", datetime(2026, 6, 1)),
    ("ro", "mai anul acesta", datetime(2026, 5, 1)),
    # Solar Hijri: 1 Tir 1405 is 2026-06-22 and 1 Mehr 1405 is 2026-09-23
    # (Iranian calendar, 1 Farvardin 1405 = 2026-03-21, months 1-6 have 31 days).
    ("fa", "تیر ماه", datetime(2026, 6, 22)),
    ("fa", "تیر ماه به سفر می‌رویم", datetime(2026, 6, 22)),
    ("fa", "مهر ماه مدرسه‌ها باز می‌شوند", datetime(2026, 9, 23)),
]


@pytest.mark.parametrize("lang,text", NO_DATE)
def test_homograph_alone_names_no_time(lang, text):
    assert extract_timespan(text, lang, ANCHOR) is None


@pytest.mark.parametrize("lang,text,start", DATED)
def test_time_cue_keeps_the_date(lang, text, start):
    found = extract_timespan(text, lang, ANCHOR)
    assert found is not None
    assert found.span.start.datetime() == start


@pytest.mark.xfail(raises=AssertionError, strict=True,
                   reason="ro '<season> anului <year>' drops the year, also for "
                          "non-homograph seasons")
@pytest.mark.parametrize("text", ["vara anului 2027", "primăvara anului 2027"])
def test_season_of_the_year_keeps_the_year(text):
    found = extract_timespan(text, "ro", ANCHOR)
    assert found is not None
    assert found.span.start.datetime().year == 2027


@pytest.mark.xfail(raises=AssertionError, strict=True,
                   reason="ro copula after a homograph season is no cue: 'e' "
                          "would also keep 'mai e timp' as May")
def test_ro_season_subject_before_copula():
    found = extract_timespan("vara e caldă", "ro", ANCHOR)
    assert found is not None
    assert found.span.start.datetime() == datetime(2026, 6, 1)
