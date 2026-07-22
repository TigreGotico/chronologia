# -*- coding: utf-8 -*-
"""Relative offsets, named days and weekdays in Aragonese.

Directional markers: fa = ago (past), en / dentro (de) = in (future); these
resolve BACKWARD and FORWARD respectively from the anchor."""
from datetime import timedelta
import pytest
from ._corpus import ANCHOR, start

A = ANCHOR


@pytest.mark.parametrize("text,days", [
    ("hue", 0), ("huei", 0), ("demán", 1), ("manyana", 1),
    ("ayere", -1), ("ahiere", -1), ("pasadoman", 2), ("antiyer", -2)])
def test_named_days(text, days):
    exp = (A + timedelta(days=days)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,days", [
    ("en 3 diyas", 3), ("fa 3 diyas", -3), ("en 1 diya", 1),
    ("dentro de 10 diyas", 10), ("fa 5 diyas", -5), ("en 7 días", 7)])
def test_day_offsets(text, days):
    exp = (A + timedelta(days=days)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,weeks", [
    ("en 1 semana", 1), ("en 2 semanas", 2), ("fa 2 semanas", -2),
    ("dentro de 3 semanas", 3), ("fa 4 semanas", -4)])
def test_week_offsets(text, weeks):
    exp = (A + timedelta(weeks=weeks)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,wd", [
    ("o martes que viene", 1), ("o luns que viene", 0),
    ("o viernes que viene", 4), ("o viernes pasau", 4),
    ("o luns pasau", 0), ("o miercres que viene", 2),
    ("que viene chueves", 3)])
def test_weekdays(text, wd):
    assert start(text).weekday() == wd
