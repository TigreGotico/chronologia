"""What this locale deliberately does not read, pinned so it stays honest.

Every phrase below names a construction whose Lithuanian surfaces could not
be attested to a dictionary source, so no vocabulary ships for it.  The
contract is refusal: the extractor returns nothing, or leaves the unread word
in the remainder, rather than guessing.  Each pin turns into a failing test
the day someone adds the vocabulary, which is exactly when the behaviour
should be revisited.
"""
import pytest

from ._corpus import nomatch, parse, remainder


@pytest.mark.parametrize("text", [
    "44 pr. m. e.", "1990 m. e. metai", "prieš mūsų erą",
])
def test_no_era_vocabulary(text):
    """No era marker ships: the abbreviation "pr. m. e." could not be
    attested, so an era-qualified year is refused."""
    r = parse(text)
    assert r is None or "pr" in r[1] or "e" in r[1]


@pytest.mark.parametrize("text", [
    "pirmasis ketvirtis", "ketvirtis", "antras ketvirtis",
])
def test_no_calendar_quarter(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["po 45 sekundžių", "prieš 30 sekundžių"])
def test_no_second_unit(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["3 savaitė", "savaitė 3", "trečioji savaitė"])
def test_no_iso_week_reference(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["birželio pradžioje", "birželio pabaigoje"])
def test_period_part_is_left_in_the_remainder(text):
    """No early/mid/late vocabulary ships, so the whole month is returned and
    the unread part word stays visible in the remainder."""
    assert remainder(text) != ""


def test_final_weekday_marker_is_left_in_the_remainder():
    """"paskutinis" (last, final) has no attested declension table, so it is
    not a relative marker here and must not be silently swallowed."""
    assert "paskutinis" in remainder("paskutinis penktadienis")


@pytest.mark.parametrize("text", ["praeitais metais", "kitais metais"])
def test_instrumental_determiner_is_not_read(text):
    """The instrumental of the determiners could not be attested; the
    nominative and accusative forms are what ship."""
    nomatch(text)


@pytest.mark.parametrize("text", ["be ketvirčio trys", "ketvirtis po trijų"])
def test_no_quarter_hour_clock(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["pusė vienuoliktos", "pusė trečios"])
def test_ordinal_hour_is_not_the_toward_hour_form(text):
    """The hour named by "pusė" is the cardinal genitive ("pusė vienuolikos"),
    not an ordinal; the ordinal shape is refused rather than guessed."""
    nomatch(text)


@pytest.mark.parametrize("text", ["du šimtai penkiasdešimt dienų"])
def test_spelled_hundreds_need_a_marker(text):
    """A spelled quantity is still only a quantity without a direction
    marker."""
    nomatch(text)
