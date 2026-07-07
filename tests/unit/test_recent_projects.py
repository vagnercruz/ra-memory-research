"""Tests for the recent projects store."""

from pathlib import Path

from ramr.infrastructure.filesystem.recent_projects import RecentProjectsStore


def make_store(tmp_path: Path, limit: int = 10) -> RecentProjectsStore:
    return RecentProjectsStore(tmp_path / "recent_projects.json", limit=limit)


def test_empty_store_lists_nothing(tmp_path: Path) -> None:
    assert make_store(tmp_path).list() == []


def test_most_recent_entry_comes_first(tmp_path: Path) -> None:
    store = make_store(tmp_path)

    store.add(tmp_path / "first")
    store.add(tmp_path / "second")

    assert store.list() == [(tmp_path / "second").resolve(), (tmp_path / "first").resolve()]


def test_reopening_project_moves_it_to_front_without_duplicating(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.add(tmp_path / "first")
    store.add(tmp_path / "second")

    store.add(tmp_path / "first")

    assert store.list() == [(tmp_path / "first").resolve(), (tmp_path / "second").resolve()]


def test_limit_drops_oldest_entries(tmp_path: Path) -> None:
    store = make_store(tmp_path, limit=2)

    for name in ("one", "two", "three"):
        store.add(tmp_path / name)

    assert store.list() == [(tmp_path / "three").resolve(), (tmp_path / "two").resolve()]


def test_remove_forgets_entry(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.add(tmp_path / "gone")

    store.remove(tmp_path / "gone")

    assert store.list() == []


def test_entries_persist_across_instances(tmp_path: Path) -> None:
    make_store(tmp_path).add(tmp_path / "durable")

    assert make_store(tmp_path).list() == [(tmp_path / "durable").resolve()]


def test_corrupt_file_is_treated_as_empty(tmp_path: Path) -> None:
    file_path = tmp_path / "recent_projects.json"
    file_path.write_text("{ not json", encoding="utf-8")

    assert RecentProjectsStore(file_path).list() == []
