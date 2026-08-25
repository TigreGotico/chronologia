"""Sun-letter assimilation: the definite article is spelled nine ways.

The Maltese article is il- before a moon letter and l- before a vowel, but
when the following word begins with one of the nine sun letters (ċ, d, n, r,
s, t, x, z, ż) the l assimilates to that consonant and the article surfaces as
iċ-, id-, in-, ir-, is-, it-, ix-, iz- or iż-.  Every date-bearing word is met
in whichever form its own initial consonant forces, so a vocabulary holding
only "il-" recognises barely half the weekdays.

The weekday names carry their article in the citation form (It-Tnejn,
L-Erbgħa, Is-Sibt), and the relative period phrases carry theirs on the noun
(is-sena, ix-xahar, id-dieħla).  Gold is the calendar: the anchor is Wednesday
2027-05-12, and each weekday resolves to the next occurrence of that day.
"""
import pytest

from ._corpus import ANCHOR, day, parse, remainder, span, start_end


# -- the seven weekdays, each with the article its initial forces -----------

@pytest.mark.parametrize("text,y,m,d", [
    ("it-Tnejn", 2027, 5, 17),
    ("it-Tlieta", 2027, 5, 18),
    ("l-Erbgħa", 2027, 5, 19),
    ("il-Ħamis", 2027, 5, 13),
    ("il-Ġimgħa", 2027, 5, 14),
    ("is-Sibt", 2027, 5, 15),
    ("il-Ħadd", 2027, 5, 16),
])
def test_each_weekday_is_read_through_its_own_article(text, y, m, d):
    assert start_end(text) == day(y, m, d)


def test_the_anchor_is_a_wednesday():
    assert ANCHOR.weekday() == 2


@pytest.mark.parametrize("text", [
    "it-Tnejn", "l-Erbgħa", "is-Sibt", "il-Ħadd",
])
def test_a_weekday_consumes_its_article(text):
    assert remainder(text) == ""


# -- the article on the relative period phrases -----------------------------

@pytest.mark.parametrize("text,start_iso,end_iso", [
    ("din is-sena", "2027-01-01", "2028-01-01"),
    ("is-sena d-dieħla", "2028-01-01", "2029-01-01"),
    ("is-sena l-oħra", "2026-01-01", "2027-01-01"),
    ("dan ix-xahar", "2027-05-01", "2027-06-01"),
    ("ix-xahar id-dieħel", "2027-06-01", "2027-07-01"),
    ("ix-xahar li għadda", "2027-04-01", "2027-05-01"),
])
def test_the_period_phrases_carry_the_assimilated_article(text, start_iso, end_iso):
    s = span(text)
    assert s.start.date().isoformat() == start_iso
    assert s.end.date().isoformat() == end_iso


# -- the article contracts with the "at" preposition the same nine ways -----

@pytest.mark.parametrize("text,hour", [
    ("fis-sitta", 6),
    ("fis-sebgħa", 7),
    ("fit-tmienja", 8),
    ("fid-disgħa", 9),
    ("fl-għaxra", 10),
    ("fil-ħdax", 11),
    ("fit-tnax", 12),
])
def test_the_preposition_carries_the_same_assimilation(text, hour):
    assert span(text).start.hour == hour


# -- a bare stem without its article is not the weekday ---------------------

def test_the_bare_numeral_stem_is_not_a_weekday():
    # tnejn, tlieta and erbgħa without an article are the cardinals two,
    # three and four, and must not read as Monday, Tuesday or Wednesday.
    for text in ("tnejn", "tlieta", "erbgħa"):
        assert parse(text) is None


def test_the_bare_week_noun_is_not_friday():
    # "ġimgħa" without an article is the week; "il-Ġimgħa" is Friday.
    assert span("ġimgħa ilu").start.date().isoformat() == "2027-05-05"
    assert span("il-Ġimgħa").start.weekday() == 4


def test_the_demonstrative_frame_names_the_week_not_friday():
    # "din il-ġimgħa" is the week: it is what CLDR gives as the week field's
    # relative-type-0, and it is the only sense running Maltese uses for it.
    # Gender is what separates the two readings -- ġimgħa is feminine and
    # takes din, so the feminine demonstrative carries the article away from
    # the weekday surface, while the masculine weekdays keep their own frame.
    s = span("din il-ġimgħa")
    assert (s.start.date().isoformat(), s.end.date().isoformat()) == (
        "2027-05-10", "2027-05-17")
    assert (s.end_datetime - s.start_datetime).days == 7


def test_the_postposed_articled_week_frames_still_read_as_friday():
    # The mirror frames cannot be separated the same way: there the article
    # sits on the noun, where the Friday surface claims it, and no marker
    # stands to its left to carry it off.  The bare noun keeps the week
    # reading, which is the route that stays available for these two.
    assert span("il-ġimgħa d-dieħla").start.weekday() == 4
    assert span("ġimgħa d-dieħla").start.date().isoformat() == "2027-05-17"
    assert span("il-ġimgħa li għaddiet").start.weekday() == 4
    assert span("ġimgħa li għaddiet").start.date().isoformat() == "2027-05-03"


@pytest.mark.parametrize("text,y,m,d", [
    ("dan it-Tnejn", 2027, 5, 10),
    ("din it-Tlieta", 2027, 5, 11),
    ("din l-Erbgħa", 2027, 5, 12),
    ("dan il-Ħamis", 2027, 5, 13),
    ("dan is-Sibt", 2027, 5, 15),
    ("dan il-Ħadd", 2027, 5, 16),
])
def test_the_demonstrative_still_reaches_every_other_weekday(text, y, m, d):
    # Only the feminine din + il- run is claimed by the week; every other
    # weekday keeps its demonstrative frame, masculine or feminine.
    assert start_end(text) == day(y, m, d)


# -- the weekday relative phrases -------------------------------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("il-Ħadd li ġej", 2027, 5, 16),
    ("il-Ħadd ta' wara", 2027, 5, 16),
    ("il-Ħadd li għadda", 2027, 5, 9),
    ("it-Tnejn li ġej", 2027, 5, 17),
    ("it-Tnejn li għadda", 2027, 5, 10),
    ("is-Sibt li għadda", 2027, 5, 8),
    ("il-Ħamis li ġej", 2027, 5, 13),
])
def test_the_weekday_relative_phrases(text, y, m, d):
    assert start_end(text) == day(y, m, d)
