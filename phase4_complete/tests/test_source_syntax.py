import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_all_phase4_complete_python_sources_parse():
    files = list(ROOT.rglob("*.py"))
    assert files
    for path in files:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
