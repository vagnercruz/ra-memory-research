"""Registry of the available memory providers."""

from collections.abc import Iterable

from ramr.domain.exceptions import MemoryProviderError
from ramr.domain.memory_provider import MemoryProvider
from ramr.infrastructure.memory.pcsx2_provider import Pcsx2Provider


class MemoryProviderRegistry:
    """Keeps the providers the application knows about, keyed by emulator name."""

    def __init__(self, providers: Iterable[MemoryProvider] = ()) -> None:
        self._providers: dict[str, MemoryProvider] = {}
        for provider in providers:
            self.register(provider)

    def register(self, provider: MemoryProvider) -> None:
        self._providers[provider.emulator_name] = provider

    def names(self) -> list[str]:
        """Registered emulator names in alphabetical order."""
        return sorted(self._providers)

    def all(self) -> list[MemoryProvider]:
        return [self._providers[name] for name in self.names()]

    def get(self, emulator_name: str) -> MemoryProvider:
        """Return the provider for ``emulator_name``.

        Raises:
            MemoryProviderError: if no provider is registered under that name.
        """
        try:
            return self._providers[emulator_name]
        except KeyError:
            raise MemoryProviderError(
                f"No memory provider registered for '{emulator_name}'."
            ) from None


def build_default_registry() -> MemoryProviderRegistry:
    """Registry with every provider shipped by default."""
    return MemoryProviderRegistry([Pcsx2Provider()])
