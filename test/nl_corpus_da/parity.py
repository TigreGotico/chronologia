"""Semantic-parity block in the discovery convention (test_language_parity):
PARITY is the (english, local) translation-pair list whose spans must match
the English staples. Read as a literal from the test_*_parity.py module so
this file stays import-free (no engine import at discovery time).
"""
import ast as _ast
import glob as _glob
import os as _os

_dir = _os.path.dirname(__file__)
_src = open(_glob.glob(_os.path.join(_dir, "test_*_parity.py"))[0],
            encoding="utf-8").read()
PARITY = next(
    _ast.literal_eval(node.value)
    for node in _ast.walk(_ast.parse(_src))
    if isinstance(node, _ast.Assign)
    and any(getattr(t, "id", None) == "PAIRS" for t in node.targets))
