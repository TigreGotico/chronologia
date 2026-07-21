# -*- coding: utf-8 -*-
"""The ca<->en semantic-parity block.

Each pair is (``ca`` phrase, English phrase) with the SAME meaning.  The
contract: both resolve to the SAME span.  Pure data -- imported both by the
corpus parity test and by the cross-language structural guard
(``test/test_language_parity.py``)."""

PARITY = [
    ('demà', 'tomorrow'),
    ('ahir', 'yesterday'),
    ('avui', 'today'),
    ('en 2 setmanes', 'in 2 weeks'),
    ('fa 2 setmanes', '2 weeks ago'),
    ('en 3 dies', 'in 3 days'),
    ('fa 3 dies', '3 days ago'),
    ('en 5 anys', 'in 5 years'),
    ('fa 10 anys', '10 years ago'),
    ('en 6 mesos', 'in 6 months'),
    ('5 de juny de 2027', 'june 5 2027'),
    ('20 de juliol de 1969', 'july 20 1969'),
    ('1 de gener de 2000', 'january 1 2000'),
    ('juny de 2027', 'june 2027'),
    ('gener de 2020', 'january 2020'),
    ('1999', '1999'),
    ('2020', '2020'),
    ('15:30', '15:30'),
    ('44 a.c.', '44 bc'),
    ('753 a.c.', '753 bc'),
    ('1492 d.c.', '1492 ad'),
    ('2000 ap', '2000 bp'),
    ("fa 66 milions d'anys", '66 million years ago'),
    ('estiu de 1969', 'summer 1969'),
    ('hivern de 1970', 'winter 1970'),
    ('juny - agost', 'from june to august'),
    ('gener - març', 'from january to march'),
    ('migdia', 'noon'),
    ('mitjanit', 'midnight'),
    ('les nou i mitja', 'half past nine'),
]
