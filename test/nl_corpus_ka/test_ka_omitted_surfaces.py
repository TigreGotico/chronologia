"""What this locale deliberately does not read, pinned so it stays honest.

Every phrase below names a construction whose Georgian surface could not be
attested to a source, or whose surface is genuinely ambiguous, so no
vocabulary ships for it.  The contract is refusal: the extractor returns
nothing, or leaves the unread word in the remainder, rather than guessing.
Each pin turns into a failing test the day someone adds the vocabulary, which
is exactly when the behaviour should be revisited.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, nomatch, parse


@pytest.mark.parametrize("text", [
    "ორი კვირის წინ", "სამი კვირის შემდეგ", "კვირის წინ",
])
def test_no_week_duration_unit(text):
    """კვირა names BOTH Sunday and the week, under one dictionary entry whose
    seven-case declension is identical for the two senses -- there is no
    morphological cue to tell them apart, and no source consulted establishes
    one reading as dominant in a counted phrase.  The ambiguity is resolved by
    CONSTRUCTION: კვირა binds the weekday slot alone, and every duration
    reading refuses instead of picking a sense."""
    assert parse(text) is None


@pytest.mark.parametrize("text", [
    "ორი კვირა", "სამი კვირა", "ხუთი კვირა", "ერთი კვირა", "ოცდაათი კვირა",
    "2 კვირა", "10 კვირა",
])
def test_counted_kvira_refuses_rather_than_answering_sunday(text):
    """A count before კვირა can only be a span of weeks, and this locale has
    no week unit to express it -- so the weekday reading is vetoed too.
    Answering "Sunday" here and stranding the numeral would hand a caller who
    asked for a duration one specific day, which is a wrong span rather than
    an incomplete one.  Declining the false weekday reading is not the same as
    asserting the unsourced week reading, which stays unavailable."""
    assert parse(text) is None


@pytest.mark.parametrize("text,expected_day", [
    ("კვირა", 2), ("მომავალი კვირა", 2), ("გასული კვირა", 25),
])
def test_kvira_reads_as_sunday_where_position_disambiguates(text, expected_day):
    """The refusals above cost nothing on the weekday side.  A weekday-slot
    position -- bare, or after the relative markers that select an occurrence
    of a weekday -- admits only the Sunday sense, and those readings resolve."""
    from ._corpus import start
    s = start(text)
    assert s.weekday() == 6
    assert s.day == expected_day


@pytest.mark.parametrize("text", ["ორი დღე", "ორი თვე", "ათი წელი", "სამი წუთი"])
def test_counted_veto_does_not_reach_unambiguous_units(text):
    """The veto is keyed to the one ambiguous surface.  Every other counted
    unit still refuses for its own reason -- a bare quantity is not a point in
    time -- and must keep doing so through its own path, not this one."""
    assert parse(text) is None


@pytest.mark.parametrize("text,expected", [
    ("ორი დღის წინ", ANCHOR - timedelta(days=2)),
    ("სამი თვის წინ", ANCHOR - relativedelta(months=3)),
])
def test_counted_veto_does_not_reach_working_offsets(text, expected):
    """Control: a count before a normal unit still drives its offset."""
    from ._corpus import ad, start
    assert start(text) == ad(expected)


def test_counted_veto_does_not_reach_other_weekdays():
    """Control: the veto is scoped to the ambiguous surface, so an
    unambiguous weekday keeps the shared behaviour every locale has -- it
    still resolves, with the unread count left in the remainder."""
    r = parse("ორი ორშაბათი")
    assert r is not None and r[0].start.weekday() == 0 and r[1] != ""


@pytest.mark.parametrize("text", [
    "სამი საუკუნის წინ", "საუკუნე", "მეოცე საუკუნე", "ორი საუკუნის შემდეგ",
])
def test_no_century_unit(text):
    """საუკუნე is the century, but its Wiktionary entry carries no declension
    table at all -- a genuine gap, confirmed through both the rendered page
    and the parse API -- so the genitive the postpositions govern would have
    to be inferred from other -ე stems.  It is omitted instead."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "ყოველდღე", "ყოველ დღე", "ყოველ თვე", "ყოველ წელს",
])
def test_no_recurrence(text):
    """"Every" is attested only as the fused compound adverb ყოველდღე
    ("daily"), never as a quantifier heading a free noun phrase, so it is not
    generalised to other units and the compound itself names no single span."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "მას შემდეგ რაც ორშაბათი", "ორშაბათიდან", "გუშინდან",
])
def test_no_since_marker(text):
    """"Since" has no dedicated postposition: it is either the periphrastic
    clause-level მას შემდეგ რაც or an extension of the plain "from" suffix
    -დან, and neither was confirmed with a temporal worked example that
    distinguishes it from "after"/"from"."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "8 საათიდან 5 საათამდე", "ორშაბათსა და პარასკევს შორის",
    "ივნისსა და ივლისს შორის",
])
def test_no_between_range(text):
    """Georgian has two unrelated between-forms -- the paired suffixes
    -დან...-მდე for a time range and the separate word შორის for two
    entities -- and the sources consulted disagree on which case შორის
    governs.  Neither ships while that conflict is open."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "ორი ათასწლეულის წინ", "ერთი ათასწლეულის შემდეგ",
])
def test_millennium_reads(text):
    """The counterpart of the century gap: ათასწლეული's declension table IS
    rendered, so the unit ships and this must NOT refuse."""
    r = parse(text)
    assert r is not None and r[1] == ""


@pytest.mark.parametrize("text", [
    "ორი საათი", "სამი საათი", "რვა საათი",
])
def test_no_bare_oclock(text):
    """No source consulted gives a plain "it is N o'clock" surface for
    Georgian -- only the four minute-band idioms, of which just the half is
    modelled -- so a bare count of hours stays a duration and names no time
    of day."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "სამის ათი წუთი", "სამს რომ აკლია ოცდახუთი წუთი",
    "ორის თხუთმეტი წუთი",
])
def test_no_minute_bands(text):
    """The first half-hour marks its relation by the genitive alone, with no
    direction word at all, and the second half-hour switches to a whole
    subordinate clause ("three that lacks twenty-five minutes").  Neither
    shape fits the slot model, so both refuse rather than being approximated
    by the half construction."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "ზაფხული", "ზამთარი", "გაზაფხული", "შემოდგომა",
])
def test_no_seasons(text):
    """No season vocabulary is attested for this locale, so the season names
    stay unread rather than being taken from a bilingual word list."""
    nomatch(text)


@pytest.mark.parametrize("text", ["AM", "PM", "დილის 9", "საღამოს 9"])
def test_no_meridiem(text):
    """CLDR ka gives no native am/pm surfaces -- the fields hold the literal
    Latin "AM"/"PM" -- so no meridiem vocabulary ships."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "ორი კვირა წინ", "სამი კვირა წინ", "ერთი კვირა წინ", "2 კვირა წინ",
])
def test_counted_kvira_with_postposed_marker_refuses(text):
    """წინ is a POSTPOSITION, so a counted კვირა phrase carries its relative
    marker after the noun.  The count still forbids the weekday reading --
    a trailing marker disambiguates direction, never sense -- so these refuse
    exactly like the bare counted forms rather than naming N Sundays back."""
    assert parse(text) is None


@pytest.mark.parametrize("text,expected_day", [
    ("ორი ორშაბათი წინ", 19), ("სამი ორშაბათი წინ", 12),
])
def test_counted_unambiguous_weekday_with_postposed_marker(text, expected_day):
    """ორშაბათი (Monday) shares no surface with a duration, so the counted
    reading survives behind the same postposition: N Mondays before the
    Tuesday anchor."""
    from ._corpus import start
    s = start(text)
    assert s.weekday() == 0
    assert s.day == expected_day
