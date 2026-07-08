"""Tests for the emulator process locator."""

from ramr.infrastructure.memory.process_locator import EmulatorProcessLocator

_PROCESSES = [
    {"pid": 10, "name": "explorer.exe", "exe": "C:/Windows/explorer.exe"},
    {"pid": 20, "name": "PCSX2-QT.exe", "exe": "D:/emu/pcsx2-qt.exe"},
    {"pid": 30, "name": "chrome.exe", "exe": None},
]


def make_locator(processes: list[dict[str, object]]) -> EmulatorProcessLocator:
    return EmulatorProcessLocator(process_iterator=lambda: iter(processes))


def test_find_matches_case_insensitively() -> None:
    locator = make_locator(_PROCESSES)

    process = locator.find(["pcsx2-qt.exe"])

    assert process is not None
    assert process.pid == 20
    assert process.name == "PCSX2-QT.exe"
    assert process.executable_path == "D:/emu/pcsx2-qt.exe"


def test_find_returns_none_when_absent() -> None:
    assert make_locator(_PROCESSES).find(["duckstation.exe"]) is None


def test_find_returns_first_match_across_candidate_names() -> None:
    locator = make_locator(_PROCESSES)

    process = locator.find(["missing.exe", "chrome.exe"])

    assert process is not None
    assert process.pid == 30
    assert process.executable_path is None


def test_find_on_empty_process_list() -> None:
    assert make_locator([]).find(["pcsx2-qt.exe"]) is None
