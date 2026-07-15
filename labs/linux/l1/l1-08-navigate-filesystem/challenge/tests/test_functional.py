"""test_functional.py — l1-08-navigate-filesystem
Validates: challenge/work/projet/ matches the target directory tree exactly.
Total: 100 points (9 tests).
"""
import pathlib
import pytest

WORK = pathlib.Path(".")
BASE = WORK / "projet"

# ── Required directories ──────────────────────────────────────────────────────
REQUIRED_DIRS = [
    BASE / "src",
    BASE / "tests",
    BASE / "docs",
    BASE / "config",
]

# ── Required files ────────────────────────────────────────────────────────────
REQUIRED_FILES = [
    BASE / "src" / "app.py",
    BASE / "src" / "utils.py",
    BASE / "tests" / "test_app.py",
    BASE / "docs" / "README.txt",
    BASE / "config" / "settings.conf",
]


# ── T1 — projet/ exists (10 pts) ─────────────────────────────────────────────
@pytest.mark.points(10)
def test_projet_dir_exists():
    """challenge/work/projet/ must exist"""
    assert BASE.is_dir(), "projet/ directory not found — run: mkdir -p projet/src ..."


# ── T2-T5 — Required directories (30 pts total, 7-8 pts each) ────────────────
@pytest.mark.points(8)
@pytest.mark.parametrize("dirpath", REQUIRED_DIRS, ids=[d.name for d in REQUIRED_DIRS])
def test_required_directory(dirpath):
    """Each required subdirectory must exist"""
    assert dirpath.is_dir(), f"Directory missing: {dirpath.relative_to(WORK)}"


# ── T6-T10 — Required files (60 pts total, 12 pts each) ──────────────────────
@pytest.mark.points(12)
@pytest.mark.parametrize(
    "filepath",
    REQUIRED_FILES,
    ids=[str(f.relative_to(BASE)) for f in REQUIRED_FILES],
)
def test_required_file(filepath):
    """Each required file must exist"""
    assert filepath.exists(), f"File missing: {filepath.relative_to(WORK)}"
