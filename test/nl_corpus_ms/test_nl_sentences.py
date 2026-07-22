# -*- coding: utf-8 -*-
"""Natural ms sentences a user actually writes -- the date embedded in real
context, asserting the exact resolved day."""
from datetime import timedelta
import pytest
from ._corpus import ANCHOR, AstroDate, start

A = ANCHOR


@pytest.mark.parametrize("text,kind,arg", [('Jumpa esok pagi.', 'off', 1), ('Semalam hujan lebat.', 'off', -1), ('Hari ini saya cuti.', 'off', 0), ('Lusa ada peperiksaan.', 'off', 2), ('Lima hari lepas dia pergi.', 'off', -5), ('Satu minggu lagi ada majlis.', 'off', 7), ('Dua minggu lepas kami berpindah.', 'off', -14), ('Sepuluh hari lagi kita kembali.', 'off', 10), ('Tiga hari lepas mula.', 'off', -3), ('Dua hari lepas tiba.', 'off', -2), ('Hari lahir 31 ogos.', 'md', (8, 31)), ('Acara 16 september.', 'md', (9, 16)), ('Peperiksaan 21 april nanti.', 'md', (4, 21)), ('Cuti 25 disember.', 'md', (12, 25)), ('Tahun baru 1 januari.', 'md', (1, 1)), ('Merdeka 31 ogos 1957 diisytiharkan.', 'ymd', (1957, 8, 31)), ('Malaysia 16 september 1963 dibentuk.', 'ymd', (1963, 9, 16)), ('Bulan 20 julai 1969 dijejaki.', 'ymd', (1969, 7, 20)), ('Peristiwa 13 mei 1969 berlaku.', 'ymd', (1969, 5, 13)), ('Sambutan 3 mac 2027 diadakan.', 'ymd', (2027, 3, 3)), ('Selasa depan kita berjumpa.', 'wd', 1), ('Jumaat lepas kami berkumpul.', 'wd', 4), ('Isnin depan mula kerja.', 'wd', 0), ('Rabu depan ada mesyuarat.', 'wd', 2), ('Sabtu depan kita bersiar-siar.', 'wd', 5)])
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
