# -*- coding: utf-8 -*-
"""The pt<->en semantic-parity block.

Each pair is (``pt`` phrase, English phrase) with the SAME meaning.  The
contract: both resolve to the SAME span.  Pure data -- imported both by the
corpus parity test and by the cross-language structural guard
(``test/test_language_parity.py``)."""

PARITY = [
    ('amanhã', 'tomorrow'),
    ('ontem', 'yesterday'),
    ('hoje', 'today'),
    ('em 2 semanas', 'in 2 weeks'),
    ('há 2 semanas', '2 weeks ago'),
    ('em 3 dias', 'in 3 days'),
    ('há 3 dias', '3 days ago'),
    ('em 5 anos', 'in 5 years'),
    ('há 10 anos', '10 years ago'),
    ('em 6 meses', 'in 6 months'),
    ('5 de junho de 2027', 'june 5 2027'),
    ('20 de julho de 1969', 'july 20 1969'),
    ('1 de janeiro de 2000', 'january 1 2000'),
    ('junho de 2027', 'june 2027'),
    ('janeiro de 2020', 'january 2020'),
    ('1999', '1999'),
    ('2020', '2020'),
    ('15:30', '15:30'),
    ('44 a.c.', '44 bc'),
    ('753 a.c.', '753 bc'),
    ('1492 d.c.', '1492 ad'),
    ('2000 ap', '2000 bp'),
    ('há 66 milhões de anos', '66 million years ago'),
    ('verão de 1969', 'summer 1969'),
    ('inverno de 1970', 'winter 1970'),
    ('junho - agosto', 'from june to august'),
    ('janeiro - março', 'from january to march'),
    ('meio-dia', 'noon'),
    ('meia-noite', 'midnight'),
    ('às nove e meia', 'half past nine'),
]
