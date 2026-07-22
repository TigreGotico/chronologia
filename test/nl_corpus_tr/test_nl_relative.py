# -*- coding: utf-8 -*-
"""Relative offsets and named/weekday days in Turkish."""
from datetime import timedelta
import pytest
from ._corpus import ANCHOR, start, span

A = ANCHOR


@pytest.mark.parametrize("text,days", [
    ("yarın", 1), ("dün", -1), ("bugün", 0), ("öbür gün", 2),
    ("ertesi gün", 2), ("önceki gün", -2), ("evvelki gün", -2)])
def test_named_days(text, days):
    assert start(text).day == (A + timedelta(days=days)).day


@pytest.mark.parametrize("text,days", [
    ("3 gün sonra", 3), ("3 gün önce", -3), ("1 gün sonra", 1),
    ("10 gün sonra", 10), ("5 gün önce", -5), ("7 gün sonra", 7),
    ("2 gün önce", -2)])
def test_day_offsets(text, days):
    assert start(text) == start("bugün") if days == 0 else True
    exp = (A + timedelta(days=days)).date()
    assert (start(text).year, start(text).month, start(text).day) ==         (exp.year, exp.month, exp.day)


@pytest.mark.parametrize("text,weeks", [
    ("1 hafta sonra", 1), ("2 hafta sonra", 2), ("2 hafta önce", -2),
    ("3 hafta sonra", 3), ("4 hafta önce", -4)])
def test_week_offsets(text, weeks):
    exp = (A + timedelta(weeks=weeks)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,hours", [
    ("2 saat sonra", 2), ("3 saat sonra", 3), ("5 saat önce", -5),
    ("1 saat sonra", 1)])
def test_hour_offsets(text, hours):
    exp = A + timedelta(hours=hours)
    assert (start(text).hour) == exp.hour


@pytest.mark.parametrize("text,mins", [
    ("15 dakika sonra", 15), ("30 dakika sonra", 30), ("45 dakika önce", -45),
    ("5 dakika sonra", 5)])
def test_minute_offsets(text, mins):
    exp = A + timedelta(minutes=mins)
    assert start(text).minute == exp.minute


@pytest.mark.parametrize("text,wd", [
    ("gelecek salı", 1), ("gelecek pazartesi", 0), ("gelecek cuma", 4),
    ("geçen cuma", 4), ("geçen pazartesi", 0), ("gelecek çarşamba", 2),
    ("gelecek cumartesi", 5), ("geçen pazar", 6), ("gelecek perşembe", 3)])
def test_weekdays(text, wd):
    assert start(text).weekday() == wd
