"""The pipeline must never be able to see the answers.

A compliance engine that can read the truth file is not being evaluated, it is
being told. These tests are the guardrail: the file lives outside the package,
one write-only module produces it, and nothing else in `src/sentinelops/` may
import that module or name its path.
"""

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src" / "sentinelops"
TRUTH_MODULE = SRC / "synth" / "truth.py"

#: The only module allowed to know where the truth file lives.
ALLOWED = {TRUTH_MODULE}

#: The only module allowed to call the writer.
ALLOWED_IMPORTERS = {TRUTH_MODULE, SRC / "synth" / "generate.py"}

FORBIDDEN_TOKENS = ("truth_path", "TRUTH_DIR", "data/truth", "truth_2026")


def _modules():
    return sorted(SRC.rglob("*.py"))


def test_the_truth_file_lives_outside_the_package():
    from sentinelops.synth.truth import TRUTH_DIR, truth_path

    assert SRC not in TRUTH_DIR.parents and TRUTH_DIR != SRC
    assert TRUTH_DIR.name == "truth" and TRUTH_DIR.parent.name == "data"
    assert "src" not in truth_path(2026).parts


def test_no_module_names_the_truth_path():
    offenders = {}
    for path in _modules():
        if path in ALLOWED:
            continue
        text = path.read_text(encoding="utf-8")
        hits = [token for token in FORBIDDEN_TOKENS if token in text]
        if hits:
            offenders[str(path.relative_to(SRC))] = hits
    assert offenders == {}, f"truth path referenced outside truth.py: {offenders}"


def test_only_the_generator_imports_the_truth_module():
    importers = []
    for path in _modules():
        if path in ALLOWED_IMPORTERS:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            elif isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            if any(n.split(".")[-1] == "truth" for n in names):
                importers.append(str(path.relative_to(SRC)))
    assert importers == [], f"truth module imported by: {importers}"


def test_the_truth_module_cannot_read_anything_back():
    """Write-only by construction: no loader, no reader, no parse."""
    import sentinelops.synth.truth as truth

    public = {n for n in dir(truth) if not n.startswith("_")}
    assert public <= {"TRUTH_DIR", "truth_path", "write_truth_file", "Path", "json",
                      "annotations", "Any"}
    assert not any(n.startswith(("read", "load", "parse", "get_truth")) for n in public)

    source = TRUTH_MODULE.read_text(encoding="utf-8")
    for forbidden in ("read_text(", "json.load", "open("):
        assert forbidden not in source, f"truth.py performs a read: {forbidden}"


def test_the_pipeline_modules_are_clean():
    """Spot-check the modules that will actually decide verdicts."""
    for name in ("db.py", "repositories.py", "main.py", "entities.py"):
        text = (SRC / name).read_text(encoding="utf-8")
        assert "truth" not in text.lower()
    for path in (SRC / "llm").rglob("*.py"):
        assert "truth" not in path.read_text(encoding="utf-8").lower()


@pytest.mark.parametrize("token", FORBIDDEN_TOKENS)
def test_the_guard_would_actually_fire(tmp_path, token):
    """Negative control: the token scan must reject a planted reference."""
    planted = tmp_path / "leaky.py"
    planted.write_text(f"# reads {token} at assessment time\n", encoding="utf-8")
    assert token in planted.read_text(encoding="utf-8")
