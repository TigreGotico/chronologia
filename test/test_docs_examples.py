"""Every ``python`` code block in the docs and the README must run.

This is the executable guarantee behind the guides: each fenced ``` ```python ```
block in ``README.md`` and ``docs/*.md`` is extracted and executed, so no
example can silently rot.  Blocks of one document share a namespace and run in
document order, exactly as a reader meets them (a later block may use a name an
earlier block imported or defined).  A block whose text contains the marker
``# doctest: skip`` is illustrative-only and is not executed.
"""
import io
import re
from contextlib import redirect_stdout
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_FENCE = re.compile(r"```python\n(.*?)```", re.DOTALL)
_SKIP_MARKER = "# doctest: skip"


def _markdown_files():
    files = [_REPO_ROOT / "README.md"]
    files += sorted((_REPO_ROOT / "docs").glob("*.md"))
    return [f for f in files if f.exists()]


def _blocks(path):
    """Yield ``(index, code)`` for each runnable python block in ``path``."""
    text = path.read_text(encoding="utf-8")
    for i, match in enumerate(_FENCE.finditer(text)):
        code = match.group(1)
        if _SKIP_MARKER in code:
            continue
        yield i, code


def _doc_ids():
    ids = []
    for path in _markdown_files():
        if any(True for _ in _blocks(path)):
            ids.append(path)
    return ids


@pytest.mark.parametrize("path", _doc_ids(), ids=lambda p: p.name)
def test_doc_examples_execute(path):
    """Run every python block in ``path`` in one shared namespace, in order."""
    namespace = {}
    ran = 0
    for index, code in _blocks(path):
        try:
            with redirect_stdout(io.StringIO()):
                exec(compile(code, f"{path.name}#block{index}", "exec"),
                     namespace)
        except Exception as exc:  # pragma: no cover - failure path
            pytest.fail(
                f"{path.name} block #{index} raised "
                f"{type(exc).__name__}: {exc}\n---\n{code}")
        ran += 1
    assert ran > 0, f"{path.name} declared runnable blocks but ran none"
