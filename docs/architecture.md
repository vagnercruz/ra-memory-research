# Architecture

RA Memory Research is a desktop assistant that helps RetroAchievements
developers research emulator memory. It is **not** a cheat engine, an
achievement editor, or a memory scanner for gameplay modification — and it
never creates achievements automatically. Developers always create
achievements manually in RAIntegration; this tool only accelerates the
research that precedes that work.

## Layers

The codebase follows Clean Architecture with a strict downward dependency
rule. A layer may depend on the layers below it, never above.

```
Presentation (ramr.ui)
        ↓
Services (ramr.services)
        ↓
Domain (ramr.domain)
        ↓
Infrastructure (ramr.infrastructure)
```

| Layer | Package | Responsibility | Rules |
| --- | --- | --- | --- |
| Presentation | `ramr.ui` | Qt widgets, windows, docks | No business logic; delegates to services |
| Services | `ramr.services` | Use cases (capture snapshot, compare, export) | Orchestrates domain + infrastructure |
| Domain | `ramr.domain` | Comparison rules, statistics, structure discovery | Pure Python; no Qt, no I/O |
| Infrastructure | `ramr.infrastructure` | Database, filesystem, logging, memory providers | Concrete adapters behind abstractions |

Cross-cutting packages:

- `ramr.core` — application bootstrap, settings, shared constants.
- `ramr.models` — data models shared across layers (projects, snapshots, notes).
- `ramr.utils` — small dependency-free helpers.

## Source layout

```
src/ramr/
    core/                   Bootstrap, settings, constants
    ui/                     Main window, docks, menu bar, status bar
        docks/
    services/               Use-case orchestration
    domain/                 Pure business rules
    models/                 Shared data models
    infrastructure/
        database/           SQLite persistence for large datasets
        filesystem/         Portable project directories, JSON metadata
        logging/            Root logging configuration
        memory/             Emulator memory providers
    utils/
tests/
    unit/                   Pure Python tests
    ui/                     pytest-qt widget tests (offscreen platform)
docs/
resources/
```

The `src` layout plus an editable install (`pip install -e ".[dev]"`) keeps
imports honest (`from ramr...`, never `from src...`) and makes PyInstaller
packaging straightforward later.

## Key design decisions

**Package restructure (Sprint 1).** The original flat `src/core`, `src/ui`,
`src/memory` modules imported `src` itself as a package, which breaks as
soon as the application is installed or frozen. Everything moved into a
proper `ramr` package before more code accumulated on the broken layout.

**Settings vs. constants.** `ramr.core.constants` holds fixed application
identity and layout values; `ApplicationSettings` carries the runtime
configuration handed to windows and services. User-editable preferences
(theme, recent projects, window state) will be persisted through an
infrastructure-backed store in a later sprint.

**Logging.** `configure_logging()` installs console plus rotating-file
handlers under the per-user application data directory. It replaces
handlers instead of stacking them, so reconfiguration (and tests) stay
safe. The path comes from Qt's `QStandardPaths` in the bootstrap layer, so
the logging module itself stays Qt-free.

**Memory providers.** Emulator access will go through a `MemoryProvider`
abstraction in `ramr.infrastructure.memory` (PCSX2, BizHawk, DuckStation,
RPCS3, ...). Upper layers depend only on the abstraction, so new emulators
mean one new provider class, not changes across the app.

**Project storage.** Each game is an independent, portable project
directory: JSON for metadata (`project.json`, notes), SQLite for large
datasets (snapshots, value histories).

## Module roadmap

| Module | Status |
| --- | --- |
| Application shell (window, docks, menus, logging) | Done (Sprint 1) |
| Project system (create/open/save portable projects) | Planned |
| Memory providers (PCSX2, BizHawk, DuckStation, RPCS3) | Planned |
| Snapshot manager (full-RAM captures with events and notes) | Planned |
| Comparison engine (changed/increased/decreased, bit/word/float/BCD) | Planned |
| Watch list (real-time values, labels, history, charts) | Planned |
| Timeline (events linked to snapshots) | Planned |
| Address inspector (value, history, statistics, confidence) | Planned |
| Structure finder | Planned |
| Code notes (descriptions, enums, flags, bitfields, export) | Planned |
| Statistics and graphs (pyqtgraph) | Planned |
| Export (CSV, JSON, Markdown) | Planned |

## Conventions

- Python 3.13+, type hints everywhere, docstrings on public classes and functions.
- Formatting with Black, linting with Ruff (both configured in `pyproject.toml`).
- Tests with pytest; UI tests use pytest-qt on the offscreen platform.
- Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`).
- Everything — code, comments, commits, docs — in English.
