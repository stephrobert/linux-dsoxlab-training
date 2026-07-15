"""conftest.py — l1-03-prepare-vm
Sets the working directory to challenge/work/ for all tests.
"""
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
