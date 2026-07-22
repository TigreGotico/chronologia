# -*- coding: utf-8 -*-
"""Natural tr sentences a user actually writes -- the date embedded in real
context, asserting the exact resolved day."""
from datetime import timedelta
import pytest
from ._corpus import ANCHOR, AstroDate, start

A = ANCHOR


@pytest.mark.parametrize("text,kind,arg", [('Toplantı yarın.', 'off', 1), ('Dün akşam geldim.', 'off', -1), ('Bugün işe gitmedim.', 'off', 0), ('Öbür gün tatil var.', 'off', 2), ('Önceki gün aramıştı.', 'off', -2), ('Üç gün önce geldi.', 'off', -3), ('Bir hafta sonra sınav var.', 'off', 7), ('Biz iki hafta önce taşındık.', 'off', -14), ('On gün sonra döneriz.', 'off', 10), ('Beş gün önce başladı.', 'off', -5), ('Doğum günüm 26 temmuz.', 'md', (7, 26)), ('Bayram 30 ağustos.', 'md', (8, 30)), ('Sınav 23 nisan olacak.', 'md', (4, 23)), ('Tatil 15 haziran başlıyor.', 'md', (6, 15)), ('Yılbaşı 1 ocak.', 'md', (1, 1)), ('Cumhuriyet 29 ekim 1923 kuruldu.', 'ymd', (1923, 10, 29)), ('Savaş 6 ağustos 1945 bitti.', 'ymd', (1945, 8, 6)), ('Ay 20 temmuz 1969 gezildi.', 'ymd', (1969, 7, 20)), ('Duvar 9 kasım 1989 yıkıldı.', 'ymd', (1989, 11, 9)), ('Deprem 17 ağustos 1999 oldu.', 'ymd', (1999, 8, 17)), ('Gelecek salı görüşürüz.', 'wd', 1), ('Geçen cuma oradaydım.', 'wd', 4), ('Gelecek pazartesi başlıyor.', 'wd', 0), ('Geçen çarşamba yağmur yağdı.', 'wd', 2), ('Gelecek cumartesi pikniğe gidiyoruz.', 'wd', 5)])
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
