"""conftest.py — Anchors the working directory to challenge/work/ for all tests."""

import os
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture(autouse=True)
def set_challenge_cwd() -> Generator[None, None, None]:
    """Change the current directory to challenge/work/ before each test."""
    challenge_dir = Path(__file__).parent.parent / "work"
    challenge_dir.mkdir(exist_ok=True)
    original = os.getcwd()
    os.chdir(challenge_dir)
    yield
    os.chdir(original)
