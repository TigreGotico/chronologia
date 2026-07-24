"""Tokenizer stage: mode flags and number/iso detection."""
import pytest

from chronologia.extract import Tokenizer, TokenizerModes


def _texts(tokens):
    return [t.text for t in tokens]


def test_basic_split_and_lowercase():
    toks = Tokenizer(TokenizerModes()).tokenize("Foo BAR baz")
    assert _texts(toks) == ["foo", "bar", "baz"]
    assert [t.index for t in toks] == [0, 1, 2]


def test_number_detection():
    tok = Tokenizer(TokenizerModes()).tokenize("3")[0]
    assert tok.is_number and tok.value == 3 and tok.text == "3"


def test_decimal_number():
    tok = Tokenizer(TokenizerModes()).tokenize("3.5")[0]
    assert tok.is_number and tok.value == 3.5


def test_ordinal_dot_on():
    tok = Tokenizer(TokenizerModes(ordinal_dot=True)).tokenize("5.")[0]
    assert tok.is_number and tok.value == 5 and tok.text == "5" and tok.raw == "5."


def test_ordinal_dot_off_keeps_bare_number():
    tok = Tokenizer(TokenizerModes(ordinal_dot=False)).tokenize("5.")[0]
    assert tok.is_number and tok.value == 5 and tok.raw == "5"


def test_split_contractions_on():
    toks = Tokenizer(TokenizerModes(split_contractions=True)).tokenize("z'day")
    assert _texts(toks) == ["z", "day"]


def test_split_contractions_off():
    toks = Tokenizer(TokenizerModes(split_contractions=False)).tokenize("z'day")
    assert _texts(toks) == ["z'day"]


def test_iso_token_kept_whole():
    toks = Tokenizer(TokenizerModes()).tokenize("2017-06-30")
    assert _texts(toks) == ["2017-06-30"] and not toks[0].is_number


def test_empty_text():
    assert Tokenizer(TokenizerModes()).tokenize("") == ()


def test_garbage_never_raises():
    toks = Tokenizer(TokenizerModes(split_contractions=True, ordinal_dot=True)
                     ).tokenize("!!! ??? --- ...")
    assert toks == ()


def test_iso_week_token_kept_whole_padded_or_not():
    tok = Tokenizer(TokenizerModes())
    assert _texts(tok.tokenize("2026-W01")) == ["2026-w01"]
    assert _texts(tok.tokenize("2026-W1")) == ["2026-w1"]
    assert _texts(tok.tokenize("2026-W1-3")) == ["2026-w1-3"]


# A digit run that continues past a literal's shape is not that literal with a
# spare digit -- it is not that literal at all.  Without the trailing boundary
# guard each of these bound a prefix and stranded the tail, which is how the
# ordinary written year range "1914-1918" came to be read as month 19 of 1914.
@pytest.mark.parametrize("text,expected", [
    ("1914-1918", ["1914", "1918"]),
    ("2026-071", ["2026", "071"]),
    ("2026-07-244", ["2026", "07", "244"]),
    ("12/11/20244", ["12", "11", "20244"]),
    ("15:305", ["15", "305"]),
    ("2026-W123", ["2026", "w", "123"]),
])
def test_digits_past_a_literal_break_it_up(text, expected):
    assert _texts(Tokenizer(TokenizerModes()).tokenize(text)) == expected


@pytest.mark.parametrize("text", ["2017-06-30", "2024/03/06", "2024-03",
                                  "12/11/2024", "15:30", "2026-w01"])
def test_literals_at_their_exact_length_still_bind(text):
    assert _texts(Tokenizer(TokenizerModes()).tokenize(text)) == [text]


# A four-digit numeral glued by a dot, slash or dash to a digit group of some
# other length is a component of a date somebody wrote, not a year standing on
# its own.  When the run around it binds no date literal, the numeral keeps its
# surface but gives up its number reading, so no year slot can pick it out of
# the wreckage and answer with a whole-year span the writer never asked for.
@pytest.mark.parametrize("text,year", [
    ("15.06.2020", "2020"),      # a dotted date in a language without them
    ("15.06.20201", "20201"),    # a digit run past the shape
    ("12/11/20244", "20244"),
    ("2024/03", "2024"),         # a slashed year-month is not an ISO one
    ("2026-071", "2026"),
])
def test_a_year_glued_into_a_broken_date_is_not_a_number(text, year):
    toks = Tokenizer(TokenizerModes()).tokenize(text)
    glued = [t for t in toks if t.text == year]   # the surface is kept whole
    assert glued and not any(t.is_number for t in glued)
    assert all(t.value is None for t in glued)


@pytest.mark.parametrize("text", ["1914-1918", "2020-2021"])
def test_a_four_digit_neighbour_leaves_the_year_a_number(text):
    """The written year range is the one glued shape that is not wreckage:
    no calendar component but a year is written with four digits, so two
    four-digit numbers around a tight hyphen are two years."""
    toks = Tokenizer(TokenizerModes()).tokenize(text)
    assert all(t.is_number for t in toks)


@pytest.mark.parametrize("text", ["2.5", "1.000", "1914-", "-1918", "covid-19"])
def test_ordinary_numerals_keep_their_number_reading(text):
    """A decimal, a thousands group, a dangling hyphen and a hyphenated word
    glue nothing to a year, so none of them lose anything."""
    toks = Tokenizer(TokenizerModes()).tokenize(text)
    assert any(t.is_number for t in toks)
