# -*- coding: utf-8 -*-
"""Adversarial Aragonese."""
import pytest
from ._corpus import nomatch, start


@pytest.mark.parametrize("text", [
    "", "   ", "buen diya", "cinco", "diya", "mes",
    "25:00", "32:99",
    "besok", "yarın", "onte", "besok"])
def test_nomatch(text):
    nomatch(text)


def test_es_article_is_token_only():
    # 'es' (plural article) must match only as a standalone token: it must
    # never bite inside 'martes' or 'meses'
    assert start("o martes que viene") is not None
    nomatch("meses")


@pytest.mark.parametrize("text", ["... hue ...", "!!! demán !!!"])
def test_junk_around(text):
    assert start(text) is not None
