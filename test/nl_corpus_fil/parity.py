# -*- coding: utf-8 -*-
"""The fil<->en semantic-parity block: each pair resolves to the SAME span."""

PARITY = [
    # named days
    ('bukas', 'tomorrow'),
    ('kahapon', 'yesterday'),
    ('ngayon', 'today'),
    ('kamakalawa', 'day before yesterday'),
    # weekdays, all Spanish loans
    ('lunes', 'monday'),
    ('martes', 'tuesday'),
    ('miyerkules', 'wednesday'),
    ('huwebes', 'thursday'),
    ('biyernes', 'friday'),
    ('sabado', 'saturday'),
    ('linggo', 'sunday'),
    ('noong lunes', 'last monday'),
    ('noong biyernes', 'last friday'),
    # offsets, native numerals under both ligature shapes
    ('sa dalawang araw', 'in 2 days'),
    ('sa tatlong araw', 'in 3 days'),
    ('sa apat na araw', 'in 4 days'),
    ('sa limang taon', 'in 5 years'),
    ('sa anim na buwan', 'in 6 months'),
    ('sa dalawang oras', 'in 2 hours'),
    ('sa labinlimang minuto', 'in 15 minutes'),
    ('sa dalawang semana', 'in 2 weeks'),
    # dates: native ordinal day, Spanish month name
    ('ika-17 ng hulyo 2026', 'july 17 2026'),
    ('ika-20 ng hulyo 1969', 'july 20 1969'),
    ('ika-isa ng enero 2000', 'january 1 2000'),
    ('ika-24 ng agosto 2026', 'august 24 2026'),
    ('hunyo 2027', 'june 2027'),
    ('enero 2020', 'january 2020'),
    ('1999', '1999'),
    ('2020', '2020'),
    # clock, both systems
    ('15:30', '15:30'),
    ('09:05', '09:05'),
    ('23:59', '23:59'),
    ('alas otso ng umaga', '8 am'),
    ('alas otso ng gabi', '8 pm'),
    ('alas dose ng tanghali', '12 pm'),
    ('tanghali', 'noon'),
    ('hatinggabi', 'midnight'),
    ('alas kuwatro y medya ng hapon', '4:30 pm'),
    ('labinlimang minuto bago ang ika-apat ng hapon', '3:45 pm'),
    ('limang minuto makalipas ang ika-anim ng umaga', '6:05 am'),
]
