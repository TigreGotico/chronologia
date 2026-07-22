# -*- coding: utf-8 -*-
"""Relative offsets and named/weekday days in Malay."""
from datetime import timedelta
import pytest
from ._corpus import ANCHOR, start

A = ANCHOR


@pytest.mark.parametrize("text,days", [
    ("esok", 1), ("semalam", -1), ("hari ini", 0), ("lusa", 2)])
def test_named_days(text, days):
    exp = (A + timedelta(days=days)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,days", [
    ("3 hari lagi", 3), ("5 hari lepas", -5), ("1 hari lagi", 1),
    ("10 hari lagi", 10), ("2 hari lepas", -2), ("7 hari lagi", 7)])
def test_day_offsets(text, days):
    exp = (A + timedelta(days=days)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,weeks", [
    ("1 minggu lagi", 1), ("2 minggu lagi", 2), ("2 minggu lepas", -2),
    ("3 minggu lagi", 3), ("4 minggu lepas", -4)])
def test_week_offsets(text, weeks):
    exp = (A + timedelta(weeks=weeks)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,hours", [
    ("2 jam lagi", 2), ("3 jam lagi", 3), ("1 jam lagi", 1)])
def test_hour_offsets(text, hours):
    assert start(text).hour == (A + timedelta(hours=hours)).hour


@pytest.mark.parametrize("text,mins", [
    ("15 minit lagi", 15), ("30 minit lagi", 30), ("5 minit lagi", 5)])
def test_minute_offsets(text, mins):
    assert start(text).minute == (A + timedelta(minutes=mins)).minute


@pytest.mark.parametrize("text,wd", [
    ("selasa depan", 1), ("isnin depan", 0), ("jumaat depan", 4),
    ("jumaat lepas", 4), ("isnin lepas", 0), ("rabu depan", 2),
    ("sabtu depan", 5), ("ahad ini", 6)])
def test_weekdays(text, wd):
    assert start(text).weekday() == wd
