"""Convert OVOS-INTENT-2 ``.voc`` files into one ``vocab.json`` per language.

Development tool: it needs ``ovos-spec-tools`` (``uv pip install ovos-spec-tools``),
which chronologia itself does not.  Run it over a locale tree before deleting the
``.voc`` files:

    python scripts/voc_to_json.py chronologia/locale test/engine_locale

For every ``<root>/<lang>/`` holding ``.voc`` files it writes ``vocab.json``:
``{"format_version": 1, "words": {...}}`` where ``words`` maps the resource base
name (file name without ``.voc``) to the sorted, de-duplicated list of the
file's expanded surfaces.
"""
import json
import sys
from pathlib import Path

from ovos_spec_tools import LocaleResources, expand, read_resource_file


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
        (lang_dir / "vocab.json").write_text(
            json.dumps({"format_version": 1, "words": dict(sorted(words.items()))},
                       ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        written += len(paths)
    return written


if __name__ == "__main__":
    for root in sys.argv[1:]:
        print(f"{root}: {convert(Path(root))} vocabularies")
