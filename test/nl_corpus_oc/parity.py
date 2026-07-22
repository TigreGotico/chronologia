"""Semantic-parity block in the discovery convention (test_language_parity):
PARITY = (lang, en) translation pairs whose spans must match the English
staples exactly. Pairs are read as a literal from test_nl_parity.py so this
file stays import-free.
"""
import ast as _ast
import os as _os

_src = open(_os.path.join(_os.path.dirname(__file__), "test_nl_parity.py"),
            encoding="utf-8").read()
PARITY = next(
    _ast.literal_eval(node.value)
    for node in _ast.walk(_ast.parse(_src))
    if isinstance(node, _ast.Assign)
    and any(getattr(t, "id", None) == "PAIRS" for t in node.targets))
