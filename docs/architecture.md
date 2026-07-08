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

**Memory providers (Sprint 3).** Emulator access goes through the
`MemoryProvider` port, defined in `ramr.domain.memory_provider`. The
service layer depends only on that abstraction; every concrete adapter
lives in `ramr.infrastructure.memory`, so a new emulator is one new
provider class, not a change rippling across the app.

The infrastructure splits the work into small, swappable collaborators
behind the `MemoryReader` and `ProcessLocator` ports:

- `ProcessMemoryReader` — reads host process memory through the Win32
  `OpenProcess`/`ReadProcessMemory` API (ctypes). Loaded lazily so the
  module stays importable off Windows.
- `EmulatorProcessLocator` — finds a process by executable name via
  psutil; the process iterator is injectable for tests.
- `BufferMemoryReader` and `FakeMemoryProvider` — in-memory
  implementations for offline development and deterministic tests.
- `ProcessMemoryProvider` — base class that wires a locator and reader
  together, translating console-relative *guest* addresses to *host*
  addresses via a subclass-provided base.

`EmulatorService` owns at most one connection at a time and exposes a
three-state lifecycle (`DISCONNECTED`, `CONNECTED`, `LOST`); the window
polls `refresh_connection()` on a timer to notice an emulator that was
closed underneath it.

**Guest RAM base calibration (honest limitation).** RetroAchievements
addresses are console-relative, but emulators allocate guest RAM on the
host heap, so the base address is not a fixed constant. `Pcsx2Provider`
therefore exposes a `guest_base_override` and, without it, raises a clear
"not calibrated" error rather than reading from a guessed address that
would return garbage. Automatic base resolution (signature scan or the
emulator's memory-exposure API) is planned for a later sprint. Everything
around this point — reader, locator, address translation, service, and
UI — is real and fully tested; only the emulator-specific base offset
awaits calibration against a live process.

**Project storage (Sprint 2).** Each game is an independent, portable
project directory: `project.json` for small human-readable metadata,
`research.db` (SQLite) for large datasets, plus `snapshots/`, `exports/`,
`notes/`, and `cache/` subdirectories. The project's root directory is
derived from where it was opened and never stored in the file, so
directories can be moved or shared freely. Database schema changes use
append-only migrations tracked with SQLite's `user_version` pragma.
`ProjectService` owns the open project and its database connection; the
recent-projects list lives in a JSON file in the per-user data directory.

**PySide6 wrapper lifetime.** Menu objects reached through temporary
`actions()` traversals get invalidated when Python garbage-collects the
intermediate wrappers. `MenuBarBuilder.build()` therefore returns a
`MainMenus` container of direct references that `MainWindow` keeps alive;
menus are always accessed through it, never by traversal.

## Module roadmap

| Module | Status |
| --- | --- |
| Application shell (window, docks, menus, logging) | Done (Sprint 1) |
| Project system (create/open/save portable projects) | Done (Sprint 2) |
| Memory providers and emulator connection | Done (Sprint 3); PCSX2 base awaits calibration |
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
