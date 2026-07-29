# -*- coding: utf-8 -*-
"""Relative offsets and named/weekday days in Indonesian."""
from datetime import timedelta
import pytest
from ._corpus import ANCHOR, start

A = ANCHOR


@pytest.mark.parametrize("text,days", [
    ("besok", 1), ("kemarin", -1), ("hari ini", 0), ("lusa", 2),
    ("kemarin lusa", -2),
    # "kemarin dulu" / "kemarin dahulu" = the day before yesterday (-2), the
    # standard idiom alongside "kemarin lusa". Regression pin: bare "kemarin"
    # above must stay -1 and not be swallowed by the compound.
    ("kemarin dulu", -2), ("kemarin dahulu", -2)])
def test_named_days(text, days):
    exp = (A + timedelta(days=days)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,days", [
    ("3 hari lagi", 3), ("3 hari lalu", -3), ("3 hari yang lalu", -3),
    ("1 hari lagi", 1), ("10 hari lagi", 10), ("5 hari lalu", -5),
    ("7 hari lagi", 7)])
def test_day_offsets(text, days):
    exp = (A + timedelta(days=days)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,weeks", [
    ("1 minggu lagi", 1), ("2 minggu lagi", 2), ("2 minggu lalu", -2),
    ("3 pekan lagi", 3), ("4 minggu lalu", -4)])
def test_week_offsets(text, weeks):
    exp = (A + timedelta(weeks=weeks)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,hours", [
    ("2 jam lagi", 2), ("3 jam lagi", 3), ("1 jam lagi", 1)])
def test_hour_offsets(text, hours):
    assert start(text).hour == (A + timedelta(hours=hours)).hour


@pytest.mark.parametrize("text,mins", [
    ("15 menit lagi", 15), ("30 menit lagi", 30), ("5 menit lagi", 5)])
def test_minute_offsets(text, mins):
    assert start(text).minute == (A + timedelta(minutes=mins)).minute


@pytest.mark.parametrize("text,wd", [
    ("selasa depan", 1), ("senin depan", 0), ("jumat depan", 4),
    ("jumat lalu", 4), ("senin lalu", 0), ("rabu depan", 2),
    ("sabtu depan", 5), ("depan kamis", 3)])
def test_weekdays(text, wd):
    assert start(text).weekday() == wd
