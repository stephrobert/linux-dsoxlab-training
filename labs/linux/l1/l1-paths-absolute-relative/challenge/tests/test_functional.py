"""test_functional.py — l1-paths-absolute-relative
Validates: both copies exist + 5 path puzzles solved correctly.
Total: 100 points (8 tests).
"""
import pathlib
import re
import pytest

WORK = pathlib.Path(".")
PLACEHOLDER = "VOTRE_RÉPONSE_ICI"

ABSOLUTE_COPY = WORK / "backup" / "absolute" / "source.txt"
RELATIVE_COPY = WORK / "backup" / "relative" / "source.txt"
PUZZLES_FILE = WORK / "puzzles.txt"

# Expected answers for the 5 puzzles
EXPECTED_ANSWERS = [
    r"\.\./docs/index\.html",        # puzzle 1
    r"\.\./syslog",                   # puzzle 2
    r"\.\./data/2024/report\.csv",    # puzzle 3
    r"\.\./\.\./nginx/nginx\.conf",   # puzzle 4
    r"projects/web/index\.html",      # puzzle 5
]


def read_puzzles():
    return PUZZLES_FILE.read_text(encoding="utf-8")


def get_answers(text: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"^ANSWER:\s*(.+)$", text, re.MULTILINE)]


# ── T1 — Absolute copy exists (15 pts) ───────────────────────────────────────
@pytest.mark.points(15)
def test_absolute_copy_exists():
    """backup/absolute/source.txt must exist"""
    assert ABSOLUTE_COPY.exists(), (
        f"{ABSOLUTE_COPY} not found — copy source.txt using an absolute path"
    )


# ── T2 — Relative copy exists (15 pts) ───────────────────────────────────────
@pytest.mark.points(15)
def test_relative_copy_exists():
    """backup/relative/source.txt must exist"""
    assert RELATIVE_COPY.exists(), (
        f"{RELATIVE_COPY} not found — copy source.txt using a relative path"
    )


# ── T3 — puzzles.txt exists (5 pts) ──────────────────────────────────────────
@pytest.mark.points(5)
def test_puzzles_file_exists():
    assert PUZZLES_FILE.exists(), "puzzles.txt not found — run: dsoxlab run l1-paths-absolute-relative"


# ── T4 — No placeholder (5 pts) ──────────────────────────────────────────────
@pytest.mark.points(5)
def test_no_placeholder():
    assert PLACEHOLDER not in read_puzzles(), "puzzles.txt still contains VOTRE_RÉPONSE_ICI"


# ── T5-T9 — Puzzle answers correct (12 pts each = 60 pts) ────────────────────
@pytest.mark.points(12)
@pytest.mark.parametrize(
    "idx,pattern",
    list(enumerate(EXPECTED_ANSWERS, start=1)),
    ids=[f"puzzle_{i}" for i in range(1, 6)],
)
def test_puzzle_answer(idx: int, pattern: str):
    """Each puzzle answer must match the expected relative path"""
    answers = get_answers(read_puzzles())
    assert len(answers) >= idx, f"Puzzle {idx} answer not found"
    answer = answers[idx - 1]
    assert re.fullmatch(pattern, answer, re.IGNORECASE), (
        f"Puzzle {idx}: expected pattern '{pattern}', got '{answer}'"
    )
