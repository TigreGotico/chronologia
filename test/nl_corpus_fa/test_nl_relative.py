# -*- coding: utf-8 -*-
"""Relative offsets, named days and weekdays in Persian.

پیش/قبل mark the past (ago); بعد/دیگر the future (in)."""
from datetime import timedelta
import pytest
from ._corpus import ANCHOR, start

A = ANCHOR


@pytest.mark.parametrize("text,days", [
    ("امروز", 0), ("فردا", 1), ("دیروز", -1), ("پس‌فردا", 2), ("پریروز", -2)])
def test_named_days(text, days):
    exp = (A + timedelta(days=days)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,days", [
    ("3 روز بعد", 3), ("3 روز پیش", -3), ("1 روز بعد", 1),
    ("10 روز بعد", 10), ("5 روز پیش", -5), ("7 روز دیگر", 7)])
def test_day_offsets(text, days):
    exp = (A + timedelta(days=days)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,weeks", [
    ("1 هفته بعد", 1), ("2 هفته بعد", 2), ("2 هفته پیش", -2),
    ("3 هفته بعد", 3), ("4 هفته پیش", -4)])
def test_week_offsets(text, weeks):
    exp = (A + timedelta(weeks=weeks)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,hours", [
    ("2 ساعت بعد", 2), ("3 ساعت بعد", 3), ("5 ساعت پیش", -5)])
def test_hour_offsets(text, hours):
    assert start(text).hour == (A + timedelta(hours=hours)).hour


@pytest.mark.parametrize("text,wd", [
    ("سه‌شنبه آینده", 1), ("دوشنبه آینده", 0), ("جمعه آینده", 4),
    ("جمعه گذشته", 4), ("دوشنبه گذشته", 0), ("چهارشنبه آینده", 2)])
def test_weekdays(text, wd):
    assert start(text).weekday() == wd
