# -*- coding: utf-8 -*-
"""Era references in Persian."""
import pytest
from ._corpus import start


@pytest.mark.parametrize("text,y", [
    ("44 پیش از میلاد", -43), ("753 پیش از میلاد", -752),
    ("330 پیش از میلاد", -329)])
def test_bc(text, y):
    assert start(text).year == y


@pytest.mark.parametrize("text,y", [
    ("1492 میلادی", 1492), ("476 میلادی", 476)])
def test_ad(text, y):
    assert start(text).year == y
