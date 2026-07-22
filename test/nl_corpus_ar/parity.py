# -*- coding: utf-8 -*-
"""The ar<->en semantic-parity block.

Each pair is (``ar`` phrase, English phrase) with the SAME meaning.  The
contract: both resolve to the SAME span.  Pure data -- imported both by the
corpus parity test and by the cross-language structural guard
(``test/test_language_parity.py``)."""

PARITY = [
    ('غدا', 'tomorrow'),
    ('أمس', 'yesterday'),
    ('اليوم', 'today'),
    ('بعد غد', 'the day after tomorrow'),
    ('بعد 2 أسابيع', 'in 2 weeks'),
    ('قبل 2 أسابيع', '2 weeks ago'),
    ('بعد 3 أيام', 'in 3 days'),
    ('قبل 3 أيام', '3 days ago'),
    ('بعد 5 سنوات', 'in 5 years'),
    ('قبل 10 سنوات', '10 years ago'),
    ('بعد 6 أشهر', 'in 6 months'),
    ('15 يناير 2020', 'january 15 2020'),
    ('20 يوليو 1969', 'july 20 1969'),
    ('1 يناير 2000', 'january 1 2000'),
    ('يونيو 2027', 'june 2027'),
    ('يناير 2020', 'january 2020'),
    ('1999', '1999'),
    ('2020', '2020'),
    ('15:30', '15:30'),
    ('44 ق.م', '44 bc'),
    ('753 ق.م', '753 bc'),
    ('1492 م', '1492 ad'),
    ('2000 ق.ح', '2000 bp'),
    ('قبل 66 مليون سنة', '66 million years ago'),
    ('صيف 1969', 'summer 1969'),
    ('شتاء 1970', 'winter 1970'),
    ('يناير - مارس', 'from january to march'),
    ('يونيو - أغسطس', 'from june to august'),
    ('الظهر', 'noon'),
    ('منتصف الليل', 'midnight'),
]
