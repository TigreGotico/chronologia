# -*- coding: utf-8 -*-
"""A part-of-day word set off by a comma still decides the half of a lone clock.

Ruling 27: a locale's own morning or evening word beside a digit clock decides
the half, even when the reader does not join the word to the clock.  A comma
between the word and the clock does not end that reading in any locale.  Said at 23:00 on 22 November, each
row reads as the next such clock, and the evening or afternoon word picks the
pm half.  The es, pt
and gl adverb "tarde" ("late") is covered in ``test_tarde_late_adverb``.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2026, 11, 22, 23, 0)

ROWS = [
    ('es', 'el sábado por la tarde, a las 5', datetime(2026, 11, 28, 17, 0)),
    ('es', 'esta tarde, a las 5', datetime(2026, 11, 22, 17, 0)),
    ('es', 'mañana, a las 5 de la tarde', datetime(2026, 11, 23, 17, 0)),
    ('es', 'a las 5, por la tarde', datetime(2026, 11, 23, 17, 0)),
    ('es', 'a las 5. Tarde libre', datetime(2026, 11, 23, 17, 0)),
    ('es', 'por la mañana, a las 6', datetime(2026, 11, 23, 6, 0)),
    ('es', 'a las 6:30, que no llegue tarde', datetime(2026, 11, 23, 6, 30)),
    ('es', 'madrugada, a las 4:30', datetime(2026, 11, 23, 4, 30)),
    ('es', 'a las 7, de la tarde', datetime(2026, 11, 23, 19, 0)),
    ('pt', 'sábado à tarde, às 5', datetime(2026, 11, 28, 17, 0)),
    ('pt', 'às 5, da tarde', datetime(2026, 11, 23, 17, 0)),
    ('pt', 'de manhã, às 6', datetime(2026, 11, 23, 6, 0)),
    ('en', 'in the evening, at 8', datetime(2026, 11, 23, 20, 0)),
    ('en', 'at 8, in the evening', datetime(2026, 11, 23, 20, 0)),
    ('en', 'tomorrow evening, at 8', datetime(2026, 11, 23, 20, 0)),
    ('nl', "'s avonds, om 8", datetime(2026, 11, 23, 20, 0)),
    ('nl', "om 8, 's avonds", datetime(2026, 11, 23, 20, 0)),
    ('de', 'abends, um 8', datetime(2026, 11, 23, 20, 0)),
    ('de', 'um 8, abends', datetime(2026, 11, 23, 20, 0)),
    ('nl', "'s middags, om 3", datetime(2026, 11, 23, 15, 0)),
    ('nl', 'vanavond, om 8', datetime(2026, 11, 22, 20, 0)),
    ('nl', 'morgenavond, om 8', datetime(2026, 11, 23, 20, 0)),
    ('nl', "'s avonds, om 8 uur, gaan we eten", datetime(2026, 11, 23, 20, 0)),
    ('nl', "'s avonds om 8", datetime(2026, 11, 23, 20, 0)),
    ('de', 'nachmittags, um 3', datetime(2026, 11, 23, 15, 0)),
    ('de', 'abends, um 8 Uhr', datetime(2026, 11, 23, 20, 0)),
    ('de', 'heute Abend, um 8', datetime(2026, 11, 22, 20, 0)),
    ('en', 'tonight, at 8', datetime(2026, 11, 22, 20, 0)),
    ('en', 'evening, at 8', datetime(2026, 11, 23, 20, 0)),
    ('en', 'pm, at 8', datetime(2026, 11, 23, 20, 0)),
    ('fr', 'le soir, à 8 heures', datetime(2026, 11, 23, 20, 0)),
    ('fr', 'ce soir, à 8 heures', datetime(2026, 11, 22, 20, 0)),
    ('fr', "l'après-midi, à 3 heures", datetime(2026, 11, 23, 15, 0)),
    ('it', 'di sera, alle 8', datetime(2026, 11, 23, 20, 0)),
    ('it', 'stasera, alle 8', datetime(2026, 11, 22, 20, 0)),
    ('it', 'pomeriggio, alle 3', datetime(2026, 11, 23, 15, 0)),
    ('ca', 'a la tarda, a les 5', datetime(2026, 11, 23, 17, 0)),
    ('ca', 'aquest vespre, a les 8', datetime(2026, 11, 22, 20, 0)),
    ('gl', 'pola tarde, ás 5', datetime(2026, 11, 23, 17, 0)),
    ('es', 'tarde, a las 5', datetime(2026, 11, 23, 17, 0)),
    ('es', 'noche, a las 9', datetime(2026, 11, 23, 9, 0)),
    ('es', 'por la noche, a las 9', datetime(2026, 11, 23, 21, 0)),
    ('pt', 'à noite, às 9', datetime(2026, 11, 23, 21, 0)),
    ('pt', 'tarde, às 5', datetime(2026, 11, 23, 17, 0)),
    ('es', 'reunión, tarde, a las 5', datetime(2026, 11, 23, 17, 0)),
]


@pytest.mark.parametrize("lang,text,expected", ROWS)
def test_a_comma_keeps_the_part_of_day_beside_the_clock(lang, text, expected):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == expected
