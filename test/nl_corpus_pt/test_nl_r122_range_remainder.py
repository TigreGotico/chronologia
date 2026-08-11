# -*- coding: utf-8 -*-
"""R122: a bound "do dia A ... até ao dia B" range must consume its own
marker words -- the compound "até ao"/"até à" terminator and the "dia"
day-of-month label noun on both endpoints.

Two independent leaks composed in this construction:

* "até ao"/"até à" is "até" (until) stacked with the contracted article
  "ao"/"à".  The connector scanner only had the bare terminators "até" and
  "ao" registered separately, so it split on the first ("até") and left the
  trailing "ao"/"à" unclaimed in front of the right endpoint.
* "dia" heads the everyday "dia N de <mês>" idiom ("day 3 of March" == the
  3rd of March) on EITHER endpoint, but is not itself part of the date
  construction's own grammar, so it was left stranded even when the date it
  labels bound correctly.

Both cases share the same signature: the span comes out correct, but a
temporal function word leaks into ``.remainder``.

The "dia" leak is not range-specific: the SAME defect signature shows up on
ANY bound date, range or not -- a bare "dia 3 de março" and one embedded in
a sentence ("a reunião é dia 3 de março") both stranded "dia" too.  The fix
(:func:`chronologia.extract.timespan._fold_day_label`) is wired into both
the range-endpoint resolver and the single-span resolver.
"""
from ._corpus import parse, AstroDate


def test_full_range_consumes_both_marker_classes():
    text = ("do dia 3 de março às 9 da manhã até ao dia 5 de abril "
            "às 5 da tarde")
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r[0].start == AstroDate(2018, 3, 3, 9, 0)
    assert r[0].end == AstroDate(2018, 4, 5, 17, 1)
    assert r[1] == "", f"marker words leaked into remainder: {r[1]!r}"


def test_ate_a_range_without_day_labels_consumes_the_compound_marker():
    text = "do dia 3 de março até ao dia 5 de abril"
    r = parse(text)
    assert r is not None
    assert r[0].start == AstroDate(2018, 3, 3)
    assert r[0].end == AstroDate(2018, 4, 6)
    assert r[1] == "", f"marker words leaked into remainder: {r[1]!r}"


def test_ate_a_with_a_accent_variant_also_consumes():
    text = "do dia 3 de março até à conferência de 5 de abril"
    r = parse(text)
    assert r is not None
    assert r[0].start == AstroDate(2018, 3, 3)
    assert r[0].end == AstroDate(2018, 4, 6)
    # "conferência de" (the conference of) is real non-temporal content on
    # the right endpoint's own clause -- only the "à" marker glue is
    # swallowed, never the noun it introduces.
    assert r[1] == "conferência de", f"unexpected remainder: {r[1]!r}"


def test_range_embedded_in_a_sentence_keeps_the_surrounding_words():
    text = ("Do dia 3 de março até ao dia 5 de abril, o museu estará "
            "fechado.")
    r = parse(text)
    assert r is not None
    assert r[0].start == AstroDate(2018, 3, 3)
    assert r[0].end == AstroDate(2018, 4, 6)
    # "o museu estará fechado" (the museum will be closed) is real content
    # after the range -- the fix must only swallow the range's own markers.
    assert r[1] == "o museu estará fechado", f"remainder: {r[1]!r}"


def test_bare_ate_with_no_contracted_article_is_untouched():
    # Control: "até o dia" (no contraction) has no "ao"/"à" to fold in --
    # only the bare "até" terminator is consumed, exactly as before.
    text = "do dia 3 de março até o dia 5 de abril"
    r = parse(text)
    assert r is not None
    assert r[0].start == AstroDate(2018, 3, 3)
    assert r[0].end == AstroDate(2018, 4, 6)
    assert r[1] == "o", f"unexpected remainder: {r[1]!r}"


def test_dia_outside_a_range_is_left_alone():
    # Control: "dia" (day) is an everyday noun used all over the language
    # outside the "dia N de <mês>" date idiom; when no range binds around it
    # it must not be touched by this fix.
    text = "Vou passar o dia com a minha família."
    r = parse(text)
    assert r is None, f"{text!r} unexpectedly parsed to {r!r}"


# -- standalone / embedded "dia N de <mês>" (no range at all) -------------
#
# The "dia" leak is the same defect signature whether or not the date it
# labels sits inside a range: a bare "dia 3 de março" and one embedded in a
# sentence ("a reunião é dia 3 de março") both left "dia" stranded even
# though the date bound correctly.


def test_standalone_dia_date_consumes_the_label():
    text = "dia 3 de março"
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r[0].start == AstroDate(2018, 3, 3)
    assert r[0].end == AstroDate(2018, 3, 4)
    assert r[1] == "", f"'dia' leaked into remainder: {r[1]!r}"


def test_dia_date_embedded_in_a_sentence_consumes_the_label():
    text = "a reunião é dia 3 de março"
    r = parse(text)
    assert r is not None
    assert r[0].start == AstroDate(2018, 3, 3)
    assert r[0].end == AstroDate(2018, 3, 4)
    # "a reunião é" (the meeting is) is real non-temporal content -- only the
    # "dia" label directly abutting the bound date is swallowed.
    assert r[1] == "a reunião é", f"unexpected remainder: {r[1]!r}"


def test_dia_not_adjacent_to_the_consumed_date_stays_in_remainder():
    # Control: "dia" here is the subject of "estava bonito" (was beautiful),
    # not a label on "ontem" (yesterday) -- "bonito" sits between "dia" and
    # the consumed date token, so the fold must NOT bridge across it.
    text = "o dia estava bonito ontem"
    r = parse(text)
    assert r is not None
    assert r[0].start == AstroDate(2017, 6, 26)
    assert "dia" in r[1], f"'dia' should have stayed in remainder: {r[1]!r}"


def test_dia_todo_still_refuses():
    # Control (probed first): "o dia todo" ("the whole day") has no date to
    # bind at all -- it must keep refusing exactly as before this fix, never
    # fabricate a span out of a bare "dia".
    text = "o dia todo"
    r = parse(text)
    assert r is None, f"{text!r} unexpectedly parsed to {r!r}"
