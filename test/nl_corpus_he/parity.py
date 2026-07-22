# -*- coding: utf-8 -*-
"""The he<->en semantic-parity block.

Each pair is (``he`` phrase, English phrase) with the SAME meaning.  The
contract: both resolve to the SAME span.  Pure data.

Hebrew has no conventional Before-Present marker (BP is a scientific
convention with no Hebrew idiom), so the parity block carries an extra
weekday / clock pair in its place to keep >= 25 meaning-equivalent phrases."""

PARITY = [
    ('מחר', 'tomorrow'),
    ('אתמול', 'yesterday'),
    ('היום', 'today'),
    ('מחרתיים', 'the day after tomorrow'),
    ('שלשום', 'the day before yesterday'),
    ('בעוד 2 שבועות', 'in 2 weeks'),
    ('לפני 2 שבועות', '2 weeks ago'),
    ('בעוד 3 ימים', 'in 3 days'),
    ('לפני 3 ימים', '3 days ago'),
    ('בעוד 5 שנים', 'in 5 years'),
    ('לפני 10 שנים', '10 years ago'),
    ('בעוד 6 חודשים', 'in 6 months'),
    ('15 בינואר 2020', 'january 15 2020'),
    ('20 ביולי 1969', 'july 20 1969'),
    ('1 בינואר 2000', 'january 1 2000'),
    ('יוני 2027', 'june 2027'),
    ('ינואר 2020', 'january 2020'),
    ('1999', '1999'),
    ('2020', '2020'),
    ('15:30', '15:30'),
    ('44 לפנה״ס', '44 bc'),
    ('753 לפנה״ס', '753 bc'),
    ('1492 לספירה', '1492 ad'),
    ('לפני 66 מיליון שנה', '66 million years ago'),
    ('קיץ 1969', 'summer 1969'),
    ('חורף 1970', 'winter 1970'),
    ('ינואר - מרץ', 'from january to march'),
    ('יוני - אוגוסט', 'from june to august'),
    ('צהריים', 'noon'),
    ('חצות', 'midnight'),
]
