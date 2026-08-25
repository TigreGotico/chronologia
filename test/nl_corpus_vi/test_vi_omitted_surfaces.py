"""What this locale deliberately does not read, pinned so it stays honest.

Every phrase below names a construction whose Vietnamese surface could not be
attested to a source, or whose surface is genuinely ambiguous, so no
vocabulary ships for it.  The contract is refusal: the extractor returns
nothing, or leaves the unread word in the remainder, rather than guessing.
Each pin turns into a failing test the day someone adds the vocabulary, which
is exactly when the behaviour should be revisited.
"""
import pytest

from ._corpus import parse


@pytest.mark.parametrize("text", [
    "năm", "vào năm", "một năm",
])
def test_bare_nam_is_the_noun_year_never_the_numeral_five(text):
    """năm is five and năm is year, one spelling and one tone.  Vietnamese
    itself avoids the collision by switching to lăm inside compounds, which
    is a statement that the bare word cannot be disambiguated.  Where no unit
    noun follows to be counted, the numeral reading is declined."""
    r = parse(text)
    assert r is None or r[1] != "" or r[0].start.month == 1


@pytest.mark.parametrize("text", ["kể từ hôm qua", "cho đến thứ sáu"])
def test_no_since_or_until_markers(text):
    """kể từ ("since") and cho đến ("until") surfaced only as aggregate
    mentions with no worked example, so neither ships and the range they
    would open does not resolve."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["từ thứ hai đến thứ sáu", "giữa hai và ba"])
def test_no_range_markers(text):
    """"from A to B" and "between A and B" have no attested Vietnamese marker
    in the sources consulted, so a range never binds and at most one endpoint
    resolves."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["hàng ngày", "hàng tuần", "hàng tháng"])
def test_no_recurrence_marker(text):
    """hàng ("every") appears only as a bound compounding prefix in the
    sources consulted, with no evidence that it stands free, so no recurrence
    vocabulary ships."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["tuần này", "tháng này", "năm nay"])
def test_no_this_deictic(text):
    """No source consulted gave a worked example of a "this <unit>" deictic,
    so none is invented; the unit noun alone names no span."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["một triệu năm trước", "một tỷ năm trước"])
def test_no_scales_above_the_thousand(text):
    """triệu (million) and tỷ (billion) are attested but sit far outside the
    range a civil date needs, so the fold stops at the thousand and the
    phrase is left unread rather than half-read."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["cn", "CN"])
def test_the_sunday_abbreviation_is_withheld(text):
    """CLDR abbreviates chủ nhật as CN, but bare cn is also the era
    abbreviation for Công Nguyên.  Admitting it would let an era marker
    resolve to a day of the week, so the abbreviation is not shipped."""
    assert parse(text) is None


@pytest.mark.parametrize("text", ["mốt", "hai mốt"])
def test_the_bare_southern_tomorrow_is_withheld(text):
    """mốt is the southern short form of ngày mốt (the day after tomorrow)
    and, in a tens compound, the numeral one (hai mươi mốt == 21).  Only the
    unambiguous ngày mốt ships."""
    assert parse(text) is None


@pytest.mark.parametrize("text", ["bốn giờ năm", "hai giờ mười"])
def test_the_minute_noun_is_required_on_the_additive_clock(text):
    """"bốn giờ năm" is four-oh-five with phút left off, but the same string
    also reads as four hours and five (of anything), and its first word is
    the year/five collision besides.  The additive minute is read only when
    phút closes it."""
    r = parse(text)
    assert r is None or r[1] != ""
