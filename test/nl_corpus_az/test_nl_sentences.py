# -*- coding: utf-8 -*-
"""Natural az sentences a user actually writes -- the date embedded in real
context, asserting the exact resolved day."""
from datetime import timedelta
import pytest
from ._corpus import ANCHOR, AstroDate, start

A = ANCHOR


@pytest.mark.parametrize("text,kind,arg", [('İclas sabah olacaq.', 'off', 1), ('Dünən yağış yağdı.', 'off', -1), ('Bugün işə getmədim.', 'off', 0), ('O biri gün bayramdır.', 'off', 2), ('Üç gün əvvəl gəldi.', 'off', -3), ('Bir həftə sonra imtahan var.', 'off', 7), ('Biz iki həftə əvvəl köçdük.', 'off', -14), ('On gün sonra qayıdarıq.', 'off', 10), ('Beş gün əvvəl başladı.', 'off', -5), ('Srağagün zəng etmişdi.', 'off', -2), ('Ad günüm 28 may.', 'md', (5, 28)), ('Bayram 18 oktyabr.', 'md', (10, 18)), ('İmtahan 12 aprel olacaq.', 'md', (4, 12)), ('Tətil 20 iyun başlayır.', 'md', (6, 20)), ('Yeni il 1 yanvar.', 'md', (1, 1)), ('Müstəqillik 28 may 1918 elan olundu.', 'ymd', (1918, 5, 28)), ('Müharibə 6 avqust 1945 bitdi.', 'ymd', (1945, 8, 6)), ('Ay 20 iyul 1969 gəzildi.', 'ymd', (1969, 7, 20)), ('Zəlzələ 18 oktyabr 1991 oldu.', 'ymd', (1991, 10, 18)), ('Hadisə 12 aprel 1961 baş verdi.', 'ymd', (1961, 4, 12)), ('Gələn çərşənbə axşamı görüşərik.', 'wd', 1), ('Keçən cümə orada idim.', 'wd', 4), ('Gələn bazar ertəsi başlayır.', 'wd', 0), ('Ötən bazar yağış yağdı.', 'wd', 6), ('Gələn şənbə səfərə çıxırıq.', 'wd', 5)])
def test_sentence(text, kind, arg):
    s = start(text)
    if kind == "off":
        exp = (A + timedelta(days=arg)).date()
        assert (s.year, s.month, s.day) == (exp.year, exp.month, exp.day)
    elif kind == "md":
        assert (s.month, s.day) == arg
    elif kind == "ymd":
        assert (s.year, s.month, s.day) == arg
    elif kind == "wd":
        assert s.weekday() == arg
