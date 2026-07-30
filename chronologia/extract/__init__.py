"""Natural-language date extraction: text -> :class:`~chronologia.DateSpan`.

The declarative construction engine that turns a date written the way a
human writes it ("the 15th of Ramadan 1446", "next winter", "66 million
years ago") into the *referential width* of the phrase -- a half-open
:class:`~chronologia.astrodate.DateSpan`, not a single collapsed instant.

The public edge is :func:`extract_timespan`; :func:`explain` opens a debug
window over the same pipeline.  Every language is data only -- a
``chronologia/locale/<code>/`` directory of ``.voc`` vocabulary files plus
one ``lang.json`` stanza; the engine core (tokenizer, normaliser,
compiler, matcher, resolver, loader) is shared and language-agnostic.

This package ``__init__`` is a thin facade: the single-span implementation
(``extract_timespan`` / ``extract_candidates``, the range and open-range
families, the scale-mode policy, the vetoes, and the :class:`DateTimeEngine`
facade with its lazy engine cache) lives in :mod:`chronologia.extract.timespan`,
and the n-series edges (durations, multi-mention, recurrence) in
:mod:`chronologia.extract.nseries`; both are re-exported here so
``chronologia.extract`` stays the single public edge.
"""
from __future__ import annotations

# engine core, re-exported so ``chronologia.extract`` is the single public edge
from chronologia.extract.compiler import ConstructionCompiler
from chronologia.extract.explain import ExplainTrace, explain
from chronologia.extract.loader import load_lang_spec
from chronologia.extract.matcher import ConstructionMatcher
from chronologia.extract.model import (Conventions, Direction, LangSpec,
                                           Match, Resolution, SlotElement,
                                           SlotOrder, Token, TokenizerModes)
from chronologia.extract.normaliser import TemporalNormaliser
from chronologia.extract.resolver import Resolver
from chronologia.extract.tokenizer import Tokenizer

# single-span implementation: public edges, the DateTimeEngine facade and its
# lazy engine cache, the range/open-range families, the scale-mode policy and
# the vetoes.  Living in a leaf module that never imports this package, the
# names the other edge modules reach for (``_timespan_engine``,
# ``_resolve_scale_mode``, ``_extract_range``, the range connector defaults,
# ``_exclusion_vetoes``, ...) are importable at module scope, so ``nseries`` no
# longer needs function-local imports and there is no import cycle.
from chronologia.extract.timespan import (  # noqa: F401
    Candidate, DateSpanResult, DateTimeEngine, TimeSpanResult,
    extract_candidates, extract_timespan,
    _timespan_engine, _resolve_scale_mode, _exclusion_vetoes,
    _extract_range, _conn_surfaces, _RANGE_BETWEEN, _RANGE_FROM,
    _TIMESPAN_ENGINES, _ENGINE_LOCK)

# N-series edges (durations, multi-mention, recurrence) live in their own
# module; imported here so ``chronologia.extract`` is the single public edge.
from chronologia.extract.nseries import (
    DurationResult, RecurrenceResult, TimeMention, extract_duration,
    extract_recurrence, extract_timespans)

__all__ = [
    "Conventions", "Direction", "LangSpec", "Match", "Resolution",
    "SlotElement", "SlotOrder", "Token", "TokenizerModes",
    "Tokenizer", "TemporalNormaliser", "ConstructionCompiler",
    "ConstructionMatcher", "Resolver", "load_lang_spec",
    "ExplainTrace", "explain",
    "extract_timespan", "extract_candidates", "Candidate",
    "extract_duration", "extract_timespans", "extract_recurrence",
    "TimeMention", "DateSpanResult", "TimeSpanResult", "DurationResult",
    "RecurrenceResult",
]
