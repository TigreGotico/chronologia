# -*- coding: utf-8 -*-
"""Natural id sentences a user actually writes -- the date embedded in real
context, asserting the exact resolved day."""
from datetime import timedelta
import pytest
from ._corpus import ANCHOR, AstroDate, start

A = ANCHOR


@pytest.mark.parametrize("text,kind,arg", [('Meeting besok pagi.', 'off', 1), ('Kemarin hujan deras.', 'off', -1), ('Hari ini saya libur.', 'off', 0), ('Lusa ada ujian.', 'off', 2), ('Kemarin lusa dia datang.', 'off', -2), ('Tiga hari lalu dia pergi.', 'off', -3), ('Satu minggu lagi ada acara.', 'off', 7), ('Dua minggu lalu kami pindah.', 'off', -14), ('Sepuluh hari lagi kita kembali.', 'off', 10), ('Lima hari lalu mulai.', 'off', -5), ('Ulang tahun 17 agustus.', 'md', (8, 17)), ('Acara 28 oktober.', 'md', (10, 28)), ('Ujian 21 april nanti.', 'md', (4, 21)), ('Libur 25 desember.', 'md', (12, 25)), ('Tahun baru 1 januari.', 'md', (1, 1)), ('Kemerdekaan 17 agustus 1945 diproklamasikan.', 'ymd', (1945, 8, 17)), ('Sumpah 28 oktober 1928 diikrarkan.', 'ymd', (1928, 10, 28)), ('Bulan 20 juli 1969 dijejaki.', 'ymd', (1969, 7, 20)), ('Reformasi 21 mei 1998 terjadi.', 'ymd', (1998, 5, 21)), ('Peristiwa 30 september 1965 terjadi.', 'ymd', (1965, 9, 30)), ('Selasa depan kita bertemu.', 'wd', 1), ('Jumat lalu kami berkumpul.', 'wd', 4), ('Senin depan mulai kerja.', 'wd', 0), ('Rabu depan ada rapat.', 'wd', 2), ('Sabtu depan kita jalan-jalan.', 'wd', 5)])
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
