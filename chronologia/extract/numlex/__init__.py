"""Native number lexicon + compositional reader.

Replaces ``ovos-number-parser``'s ``extract_number_<lang>``/pronounce-sweep
round trip with an in-tree ``word -> (value, role)`` table plus a generic
additive-multiplicative reader.  See ``docs/design/native-number-lexicon.md``
for the phased rollout; this package is phase P0 (English only) -- the
``lexicon``/``reader`` shape is language-agnostic, but only the English table
is populated so far.
"""
from chronologia.extract.numlex.lexicon import Entry, NumberLexicon
from chronologia.extract.numlex.reader import read_run
from chronologia.extract.numlex.roles import Role

__all__ = ["Entry", "NumberLexicon", "read_run", "Role"]
