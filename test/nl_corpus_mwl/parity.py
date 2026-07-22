# -*- coding: utf-8 -*-
"""The mwl<->en semantic-parity block: each pair resolves to the SAME span."""

PARITY = [
    # rel_period / weekend / bare-weekday rollout
    ('sesta feira', 'friday'),
    ('segunda feira', 'monday'),
    ('manhana', 'tomorrow'),
    ('onte', 'yesterday'),
    ('hoije', 'today'),
    ('trasdonte', 'day before yesterday'),
    ('hai 2 sumanas', '2 weeks ago'),
    ('hai 4 sumanas', '4 weeks ago'),
    ('hai 3 dies', '3 days ago'),
    ('hai 2 dies', '2 days ago'),
    ('hai 5 anhos', '5 years ago'),
    ('hai 10 anhos', '10 years ago'),
    ('hai 6 meses', '6 months ago'),
    ('5 de júnio de 2027', 'june 5 2027'),
    ('20 de júlio de 1969', 'july 20 1969'),
    ('1 de janeiro de 2000', 'january 1 2000'),
    ('25 de dezembre de 2025', 'december 25 2025'),
    ('júnio de 2027', 'june 2027'),
    ('janeiro de 2020', 'january 2020'),
    ('júnio', 'june'),
    ('janeiro', 'january'),
    ('márcio', 'march'),
    ('agosto', 'august'),
    ('1999', '1999'),
    ('2020', '2020'),
    ('1969', '1969'),
    ('15:30', '15:30'),
]
