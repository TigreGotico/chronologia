"""The day after tomorrow in Azerbaijani.

az.wiktionary glosses it under "gün": "Biri gün (o birisi gün) -- sabahdan
sonrakı gün".  The fused spelling is what runs in literary prose, on
az.wikisource: "sabah-birigün ərə gedərsən" (Şamdan bəy) and "sabah yox,
birigün züvvarlar çıxırlar" (Danabaş kəndinin əhvalatları).

Anchor 2017-06-27, a Tuesday; two days later is Thursday 29 June.
"""
import pytest

from ._corpus import AstroDate, nomatch, parse, start


@pytest.mark.parametrize("text", ["birigün", "o biri gün", "o birisi gün"])
def test_day_after_tomorrow(text):
    assert start(text) == AstroDate(2017, 6, 29)
    assert parse(text).remainder == ""


def test_tomorrow_is_unchanged():
    assert start("sabah") == AstroDate(2017, 6, 28)


def test_bare_biri_before_a_gun_word_is_not_a_day():
    """"biri" plus a gün- word is the ordinary "one of them", not a date.

    az.wikisource and az.wikipedia both carry the collision --
    "başçılardan biri günah işlədərək", "heç biri günümüzə" -- which is why
    the bare spaced "biri gün" is not a surface here.
    """
    nomatch("başçılardan biri günah işlədi")
    nomatch("heç biri günümüzə gəlib çatmamışdır")
