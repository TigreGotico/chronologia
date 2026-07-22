# -*- coding: utf-8 -*-
"""Relative offsets and named/weekday days in Azerbaijani."""
from datetime import timedelta
import pytest
from ._corpus import ANCHOR, start

A = ANCHOR


@pytest.mark.parametrize("text,days", [
    ("sabah", 1), ("dünən", -1), ("bugün", 0), ("bu gün", 0),
    ("o biri gün", 2), ("srağagün", -2)])
def test_named_days(text, days):
    exp = (A + timedelta(days=days)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,days", [
    ("3 gün sonra", 3), ("3 gün əvvəl", -3), ("2 gün qabaq", -2),
    ("1 gün sonra", 1), ("10 gün sonra", 10), ("5 gün əvvəl", -5),
    ("7 gün sonra", 7)])
def test_day_offsets(text, days):
    exp = (A + timedelta(days=days)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,weeks", [
    ("1 həftə sonra", 1), ("2 həftə sonra", 2), ("2 həftə əvvəl", -2),
    ("3 həftə sonra", 3), ("4 həftə əvvəl", -4)])
def test_week_offsets(text, weeks):
    exp = (A + timedelta(weeks=weeks)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,hours", [
    ("2 saat sonra", 2), ("3 saat sonra", 3), ("5 saat əvvəl", -5),
    ("1 saat sonra", 1)])
def test_hour_offsets(text, hours):
    assert start(text).hour == (A + timedelta(hours=hours)).hour


@pytest.mark.parametrize("text,mins", [
    ("15 dəqiqə sonra", 15), ("30 dəqiqə sonra", 30), ("45 dəqiqə əvvəl", -45),
    ("5 dəqiqə sonra", 5)])
def test_minute_offsets(text, mins):
    assert start(text).minute == (A + timedelta(minutes=mins)).minute


@pytest.mark.parametrize("text,wd", [
    ("gələn çərşənbə axşamı", 1), ("gələn bazar ertəsi", 0),
    ("gələn cümə", 4), ("keçən cümə", 4), ("keçən bazar ertəsi", 0),
    ("gələn çərşənbə", 2), ("gələn şənbə", 5), ("ötən bazar", 6)])
def test_weekdays(text, wd):
    assert start(text).weekday() == wd
