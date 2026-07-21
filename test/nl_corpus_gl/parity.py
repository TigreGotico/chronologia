# -*- coding: utf-8 -*-
"""The gl<->en semantic-parity block.

Each pair is (``gl`` phrase, English phrase) with the SAME meaning.  The
contract: both resolve to the SAME span.  Pure data -- imported both by the
corpus parity test and by the cross-language structural guard
(``test/test_language_parity.py``)."""

PARITY = [
    ('mañá', 'tomorrow'),
    ('onte', 'yesterday'),
    ('hoxe', 'today'),
    ('en 2 semanas', 'in 2 weeks'),
    ('hai 2 semanas', '2 weeks ago'),
    ('en 3 días', 'in 3 days'),
    ('hai 3 días', '3 days ago'),
    ('en 5 anos', 'in 5 years'),
    ('hai 10 anos', '10 years ago'),
    ('en 6 meses', 'in 6 months'),
    ('5 de xuño de 2027', 'june 5 2027'),
    ('20 de xullo de 1969', 'july 20 1969'),
    ('1 de xaneiro de 2000', 'january 1 2000'),
    ('xuño de 2027', 'june 2027'),
    ('xaneiro de 2020', 'january 2020'),
    ('1999', '1999'),
    ('2020', '2020'),
    ('15:30', '15:30'),
    ('44 a.c.', '44 bc'),
    ('753 a.c.', '753 bc'),
    ('1492 d.c.', '1492 ad'),
    ('2000 ap', '2000 bp'),
    ('hai 66 millóns de anos', '66 million years ago'),
    ('verán de 1969', 'summer 1969'),
    ('inverno de 1970', 'winter 1970'),
    ('xuño - agosto', 'from june to august'),
    ('xaneiro - marzo', 'from january to march'),
    ('mediodía', 'noon'),
    ('medianoite', 'midnight'),
    ('ás nove e media', 'half past nine'),
]
