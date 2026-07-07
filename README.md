# RA Memory Research

A desktop assistant that helps RetroAchievements developers research
emulator memory: capture RAM snapshots, compare them, track addresses, and
organize findings — while achievements themselves are always created
manually in RAIntegration.

This tool is **not** a cheat engine and never creates achievements
automatically.

## Planned features

- Emulator connection through pluggable memory providers (PCSX2, BizHawk, DuckStation, RPCS3)
- Full-RAM snapshots with timestamps, events, and notes
- Snapshot comparison (changed / increased / decreased, bit, word, float, BCD)
- Real-time watch list with labels, history, and charts
- Timeline of gameplay events linked to snapshots
- Address inspector with statistics and confidence scores
- Structure finder
- Code notes with enums, flags, and bitfields
- Export to CSV, JSON, and Markdown
- Portable per-game project directories

## Requirements

- Windows 10 or 11
- Python 3.13+

## Development setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Run the application:

```powershell
python main.py
```

Run quality checks:

```powershell
black .
ruff check .
pytest
```

## Documentation

See [docs/architecture.md](docs/architecture.md) for the architecture
overview, layering rules, and module roadmap.

## Status

Early development — Sprint 2 complete: portable per-game projects can be
created, opened, and reopened from a recent-projects list, each with its
own SQLite research database.
