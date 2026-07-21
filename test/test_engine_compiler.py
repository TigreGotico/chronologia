"""Compiler stage: order parsing, precedence ordering, per-lang caching."""
from dataclasses import replace

from engine_helpers import load_zz

from chronologia.extract import ConstructionCompiler
from chronologia.extract.compiler import parse_order


def test_parse_order_optional_and_slots():
    order = parse_order("calendar_date", "MONTH DAY? YEAR?")
    names = [(e.name, e.optional, e.is_slot) for e in order.elements]
    assert names == [("MONTH", False, True), ("DAY", True, True),
                     ("YEAR", True, True)]


def test_parse_order_connector_is_not_slot():
    order = parse_order("calendar_date", "DAY of MONTH YEAR?")
    of = order.elements[1]
    assert of.name == "of" and not of.is_slot and not of.optional


def test_cache_returns_same_object():
    comp = ConstructionCompiler()
    spec = load_zz()
    first = comp.compile(spec)
    assert comp.compile(spec) is first


def test_cache_is_per_language():
    comp = ConstructionCompiler()
    spec = load_zz()
    other = replace(spec, lang="yy")
    assert comp.compile(spec) is not comp.compile(other)


def test_table_sorted_by_precedence():
    table = ConstructionCompiler().compile(load_zz()).table
    ranks = [prec for prec, _, _ in table]
    assert ranks == sorted(ranks)
    # iso_date (3) must precede calendar_date (4) which precedes named_day (8)
    names_by_rank = [name for _, name, _ in table]
    assert names_by_rank.index("iso_date") < names_by_rank.index("calendar_date")
    assert (names_by_rank.index("calendar_date")
            < names_by_rank.index("named_day"))
