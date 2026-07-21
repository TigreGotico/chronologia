# -*- coding: utf-8 -*-
"""The es<->en semantic-parity block.

Each pair is (``es`` phrase, English phrase) with the SAME meaning.  The
contract: both resolve to the SAME span.  Pure data -- imported both by the
corpus parity test and by the cross-language structural guard
(``test/test_language_parity.py``)."""

PARITY = [
    ('mañana', 'tomorrow'),
    ('ayer', 'yesterday'),
    ('hoy', 'today'),
    ('en 2 semanas', 'in 2 weeks'),
    ('hace 2 semanas', '2 weeks ago'),
    ('en 3 días', 'in 3 days'),
    ('hace 3 días', '3 days ago'),
    ('en 5 años', 'in 5 years'),
    ('hace 10 años', '10 years ago'),
    ('en 6 meses', 'in 6 months'),
    ('5 de junio de 2027', 'june 5 2027'),
    ('20 de julio de 1969', 'july 20 1969'),
    ('1 de enero de 2000', 'january 1 2000'),
    ('junio de 2027', 'june 2027'),
    ('enero de 2020', 'january 2020'),
    ('1999', '1999'),
    ('2020', '2020'),
    ('15:30', '15:30'),
    ('44 a.c.', '44 bc'),
    ('753 a.c.', '753 bc'),
    ('1492 d.c.', '1492 ad'),
    ('2000 ap', '2000 bp'),
    ('hace 66 millones de años', '66 million years ago'),
    ('verano de 1969', 'summer 1969'),
    ('invierno de 1970', 'winter 1970'),
    ('junio - agosto', 'from june to august'),
    ('enero - marzo', 'from january to march'),
    ('mediodía', 'noon'),
    ('medianoche', 'midnight'),
    ('las nueve y media', 'half past nine'),
]
