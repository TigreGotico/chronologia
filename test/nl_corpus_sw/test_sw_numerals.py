"""Numerals, and the noun class that chooses their shape.

Swahili counts with two sets of words at once.  Six inherited Bantu stems take
a concord prefix from the class of the noun they count, and four Arabic loans
never change at all.  The units this locale ships fall into two classes, so
every agreeing stem has two correct surfaces -- "siku tano" beside "miaka
mitano" -- and a reader that knew only one of them would return nothing for
half the sentences a speaker writes.
"""
import pytest

from ._corpus import ANCHOR, day, nomatch, parse, span, start, start_end


def _days_ago(n):
    from datetime import timedelta
    return ANCHOR - timedelta(days=n)


# -- the class 9/10 units: the stem surfaces bare ---------------------------
# sekunde, dakika, saa, siku and wiki are N-class nouns.  The class prefix is
# absorbed to nothing, so the numeral stands in its bare stem shape and the
# noun itself never changes for number: the whole count lives in the numeral.

@pytest.mark.parametrize("word,n", [
    ("moja", 1), ("mbili", 2), ("tatu", 3), ("nne", 4), ("tano", 5),
    ("sita", 6), ("saba", 7), ("nane", 8), ("tisa", 9), ("kumi", 10),
])
def test_the_bare_stem_counts_days(word, n):
    assert start(f"siku {word} zilizopita") == _days_ago(n)


def test_the_noun_does_not_change_for_number():
    """One day and ten days stand beside the same word siku."""
    assert start("siku moja iliyopita") == _days_ago(1)
    assert start("siku kumi zilizopita") == _days_ago(10)


# -- the class 3/4 units: the mi- concord ------------------------------------
# mwaka/miaka and mwezi/miezi prefix mi- in the plural, and the agreeing
# numeral prefixes it too.  The invariant loans do not.

@pytest.mark.parametrize("word,n", [
    ("miwili", 2), ("mitatu", 3), ("minne", 4), ("mitano", 5),
    ("minane", 8),
])
def test_the_mi_concord_counts_years(word, n):
    assert start(f"miaka {word} iliyopita").year == ANCHOR.year - n


@pytest.mark.parametrize("word,n", [
    ("sita", 6), ("saba", 7), ("tisa", 9), ("kumi", 10),
])
def test_the_arabic_loans_take_no_concord(word, n):
    """The loans stand in one shape whichever class counts with them."""
    assert start(f"miaka {word} iliyopita").year == ANCHOR.year - n
    assert start(f"siku {word} zilizopita") == _days_ago(n)


def test_the_two_concords_read_the_same_value():
    assert start("miezi mitano iliyopita").month == 12
    assert start("siku tano zilizopita") == _days_ago(5)


# -- composition -------------------------------------------------------------
# Components run largest first -- the scale word LEADS its multiplier, "elfu
# mbili" being two thousand -- and descend, optionally linked by na.

@pytest.mark.parametrize("phrase,n", [
    ("kumi na moja", 11), ("kumi na tano", 15), ("kumi na tisa", 19),
    ("ishirini", 20), ("ishirini na tano", 25),
    ("thelathini", 30), ("arobaini na tano", 45), ("hamsini", 50),
    ("sitini", 60), ("sabini na mbili", 72), ("themanini", 80),
    ("tisini na tisa", 99),
])
def test_composed_numerals_count_minutes(phrase, n):
    from datetime import timedelta
    assert start(f"dakika {phrase} zilizopita") == ANCHOR - timedelta(minutes=n)


@pytest.mark.parametrize("phrase,n", [
    ("mia", 100), ("mia moja", 100), ("mia mbili", 200), ("mia tisa", 900),
    ("mia moja na ishirini na tano", 125),
])
def test_the_hundred_word_leads_its_multiplier(phrase, n):
    assert start(f"miaka {phrase} iliyopita").year == ANCHOR.year - n


def test_the_thousand_word_leads_its_multiplier():
    assert start("miaka elfu mbili iliyopita").year == ANCHOR.year - 2000


# -- na is the ordinary "and" as well ---------------------------------------
# The connector bridges only where one number genuinely continues: the
# component it introduces must be strictly smaller than the one before it.

def test_the_connector_does_not_bridge_two_dates():
    assert start_end("kati ya 5 Juni na 8 Juni") == (day(2027, 6, 5)[0],
                                                     day(2027, 6, 9)[0])


@pytest.mark.parametrize("text", ["tano na tatu", "ishirini na ishirini"])
def test_a_run_that_cannot_be_one_number_reads_as_none(text):
    nomatch(text)


@pytest.mark.parametrize("words", [
    ("tano", "na", "tatu"),          # two units: neither is smaller
    ("ishirini", "na", "thelathini"),  # two tens words
    ("mia", "na", "elfu"),           # the scales run the wrong way round
    ("na", "tano"),                  # the connector never opens a number
    ("tano", "na"),                  # nor closes one
])
def test_the_reader_refuses_a_run_that_is_not_one_number(words):
    """The connector bridges only a genuine descent of components.

    Without this gate "siku tatu na Jumatano" and every other sentence whose
    na is the ordinary "and" would collapse into a single wrong numeral.
    """
    from chronologia.extract.numfold_bantu import read_run
    assert read_run(words) is None


@pytest.mark.parametrize("words,value", [
    (("kumi", "na", "moja"), 11),
    (("ishirini", "na", "tano"), 25),
    (("mia", "tatu", "ishirini", "na", "tano"), 325),
    (("elfu", "mbili", "mia", "tatu", "ishirini", "na", "tano"), 2325),
])
def test_the_reader_composes_a_descending_run(words, value):
    from chronologia.extract.numfold_bantu import read_run
    assert read_run(words) == value
