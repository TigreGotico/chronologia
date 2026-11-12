"""The ordinal fold builds its surface map without a deprecated
ovos-number-parser entry point.

ovos-number-parser deprecates ``pronounce_ordinal_pt``, ``_gl`` and
``_mwl`` with the message "migrate to use RomanceNumberExtractor and
NumberVocabulary directly instead"; each one only forwards to the
module's ``RomanceNumberExtractor.pronounce_ordinal``.
"""
import warnings

import pytest

from chronologia.extract.numfold_ordinals import _pron_ordinal_map


@pytest.mark.parametrize("lang", ["pt", "gl", "mwl"])
def test_map_is_built_without_a_deprecation_warning(lang):
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        surfaces = _pron_ordinal_map.__wrapped__(lang)
    assert surfaces

