"""Emulator memory providers.

Each supported emulator (PCSX2, BizHawk, DuckStation, RPCS3, ...) gets a
provider implementing a common ``MemoryProvider`` abstraction so upper
layers never depend on emulator-specific details.
"""
