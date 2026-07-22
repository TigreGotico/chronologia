# -*- coding: utf-8 -*-
"""Natural fa sentences a user actually writes -- the date embedded in real
context, asserting the exact resolved day."""
from datetime import timedelta
import pytest
from ._corpus import ANCHOR, AstroDate, start

A = ANCHOR


@pytest.mark.parametrize("text,kind,arg", [('جلسه فردا است.', 'off', 1), ('دیروز باران بارید.', 'off', -1), ('امروز کار نکردم.', 'off', 0), ('پس\u200cفردا امتحان است.', 'off', 2), ('پریروز زنگ زد.', 'off', -2), ('سه روز پیش آمد.', 'off', -3), ('یک هفته بعد امتحان است.', 'off', 7), ('دو هفته پیش نقل مکان کردیم.', 'off', -14), ('ده روز بعد برمی\u200cگردیم.', 'off', 10), ('پنج روز پیش شروع شد.', 'off', -5), ('تولدم 5 ژوئن است.', 'md', (6, 5)), ('مراسم 25 دسامبر است.', 'md', (12, 25)), ('امتحان 14 فوریه است.', 'md', (2, 14)), ('تعطیلات 30 ژوئن شروع می\u200cشود.', 'md', (6, 30)), ('سال نو 1 ژانویه است.', 'md', (1, 1)), ('ماه 20 ژوئیه 1969 پیموده شد.', 'ymd', (1969, 7, 20)), ('جنگ 6 اوت 1945 پایان یافت.', 'ymd', (1945, 8, 6)), ('رویداد 11 سپتامبر 2001 رخ داد.', 'ymd', (2001, 9, 11)), ('مراسم 25 دسامبر 2025 برگزار شد.', 'ymd', (2025, 12, 25)), ('حادثه 3 مارس 2010 رخ داد.', 'ymd', (2010, 3, 3)), ('سه\u200cشنبه آینده می\u200cبینمت.', 'wd', 1), ('جمعه گذشته آنجا بودم.', 'wd', 4), ('دوشنبه آینده شروع می\u200cشود.', 'wd', 0), ('چهارشنبه آینده جلسه داریم.', 'wd', 2), ('قرار ما 15 خرداد 1403 است.', 'ymd', (2024, 6, 4))])
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
