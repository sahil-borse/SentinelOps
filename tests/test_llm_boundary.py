"""No provider SDK type may cross out of `sentinelops.llm`."""

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "sentinelops"
LLM = SRC / "llm"

SDK_ROOTS = {
    "openai",
    "anthropic",
    "google",
    "cohere",
    "mistralai",
    "litellm",
    "langchain",
    "tiktoken",
    "boto3",
}


def _modules_outside_llm():
    return [p for p in SRC.rglob("*.py") if LLM not in p.parents and p != LLM]


def _imported_roots(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            roots.add(node.module.split(".")[0])
    return roots


def test_no_module_outside_llm_imports_a_provider_sdk():
    offenders = {
        str(p.relative_to(SRC)): sorted(_imported_roots(p) & SDK_ROOTS)
        for p in _modules_outside_llm()
        if _imported_roots(p) & SDK_ROOTS
    }
    assert offenders == {}, f"provider SDK imported outside llm/: {offenders}"


def test_no_module_outside_llm_imports_a_concrete_provider():
    offenders = []
    for path in _modules_outside_llm():
        text = path.read_text(encoding="utf-8")
        if "llm.providers" in text or "from .llm.providers" in text:
            offenders.append(str(path.relative_to(SRC)))
    assert offenders == [], f"concrete provider imported outside llm/: {offenders}"


def test_only_the_factory_reaches_for_a_provider():
    importers = [
        str(p.relative_to(LLM))
        for p in LLM.rglob("*.py")
        if "providers" not in p.parts and "providers" in p.read_text(encoding="utf-8")
    ]
    assert importers == ["factory.py"]
