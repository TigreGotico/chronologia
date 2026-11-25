"""Convert OVOS-INTENT-2 ``.voc`` files into one ``vocab.json`` per language.

Development tool: it needs ``ovos-spec-tools`` (``uv pip install ovos-spec-tools``),
which chronologia itself does not.  Run it over a locale tree before deleting the
``.voc`` files:

    python scripts/voc_to_json.py chronologia/locale test/engine_locale

For every ``<root>/<lang>/`` holding ``.voc`` files it writes ``vocab.json``:
``{"format_version": 1, "words": {...}, "sources": {...}}`` where ``words`` maps
the resource base name (file name without ``.voc``) to the sorted, de-duplicated
list of the file's expanded surfaces, and ``sources`` maps a base name to the
comment lines of its file, in file order, without the ``#`` and one following
space.  A file without comment lines has no entry in ``sources``.
"""
import json
import sys
from pathlib import Path

from ovos_spec_tools import LocaleResources, expand, read_resource_file


def comment_lines(path: Path) -> list:
    """The comment lines of a ``.voc`` file, without ``#`` and one space."""
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    comments = [line.lstrip()[1:] for line in lines
                if line.lstrip().startswith("#")]
    return [c[1:] if c.startswith(" ") else c for c in comments]


def convert(root: Path) -> int:
    resources = LocaleResources(str(root))
    written = 0
    for lang_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        paths = sorted(lang_dir.glob("*.voc"))
        if not paths:
            continue
        vocab_map = resources.vocabularies(lang_dir.name)
        words = {path.stem: sorted({s for template in read_resource_file(path)
                                    for s in expand(template, vocab_map)})
                 for path in paths}
        sources = {path.stem: comment_lines(path) for path in paths}
        document = {"format_version": 1, "words": dict(sorted(words.items()))}
        if any(sources.values()):
            document["sources"] = {k: v for k, v in sorted(sources.items()) if v}
        (lang_dir / "vocab.json").write_text(
            json.dumps(document, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        written += len(paths)
    return written


if __name__ == "__main__":
    for root in sys.argv[1:]:
        print(f"{root}: {convert(Path(root))} vocabularies")
