"""conftest.py — l1-env-profiles"""
import os
import pathlib

import pytest


@pytest.fixture(autouse=True)
def set_workdir():
    work_dir = pathlib.Path(__file__).parent.parent / "work"
    work_dir.mkdir(parents=True, exist_ok=True)
    original = os.getcwd()
    os.chdir(work_dir)
    yield
    os.chdir(original)
