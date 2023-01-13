from time import monotonic
from typing import Callable, Optional,  Protocol, TypeVar


T = TypeVar('T')


class SingleObjectCache(Protocol[T]):
    def get(self) -> Optional[T]:
        pass

    def get_or_load(self, load_fn: Callable[[], T]) -> T:
        pass


class DummySingleObjectCache(SingleObjectCache[T]):
    def get(self) -> Optional[T]:
        return None

    def get_or_load(self, load_fn: Callable[[], T]) -> T:
        return load_fn()


class SingleObjectInMemoryCache(SingleObjectCache[T]):

    def __init__(
        self,
        initial_value: Optional[T] = None,
        max_age_in_seconds: Optional[float] = None
    ) -> None:
        self._value = initial_value
        self.max_age_in_seconds = max_age_in_seconds
        self._last_updated_time: Optional[float] = None

    def _is_max_age_reached(self, now: float) -> bool:
        return bool(
            self.max_age_in_seconds
            and self._last_updated_time is not None
            and (now - self._last_updated_time > self.max_age_in_seconds)
        )

    def get(self) -> Optional[T]:
        return self._value

    def get_or_load(self, load_fn: Callable[[], T]) -> T:
        now = monotonic()
        result = self._value
        if result is not None and not self._is_max_age_reached(now):
            return result
        result = load_fn()
        assert result is not None
        self._value = result
        self._last_updated_time = now
        return result
